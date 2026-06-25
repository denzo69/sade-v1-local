from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json
import math
import re


SAFE_EXTENSIONS = {
    ".md", ".txt", ".json", ".py", ".html", ".htm", ".css", ".js",
    ".yml", ".yaml", ".toml", ".ini", ".ps1", ".bat"
}

BLOCKED_DIR_NAMES = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "vector_db"
}

MAX_FILE_SCAN_BYTES = 350_000

SOURCE_PRIORITIES = {
    "learning_review": 110,
    "atlas": 100,
    "sade_memory": 95,
    "operating_manual": 98,
    "project_doc": 75,
    "uploaded_file": 65,
    "chat_log": 15,
    "unknown": 40,
}

CHAT_LOG_MAX_RESULTS = 1
DEFAULT_N_RESULTS = 8
DEFAULT_MAX_CONTEXT_CHARS = 4500
DEFAULT_MIN_SCORE = 55.0
MAX_RESULTS_PER_PATH = 3


@dataclass
class RagCandidate:
    source_type: str
    source: str
    path: str
    title: str
    text: str
    distance: Optional[float] = None
    base_rank: Optional[int] = None
    origin: str = "unknown"
    metadata: Optional[Dict[str, Any]] = None
    score: float = 0.0
    reasons: Optional[List[str]] = None
    term_coverage: float = 0.0
    matched_terms: Optional[List[str]] = None
    filename_matched_terms: Optional[List[str]] = None
    exact_phrase: bool = False

    def to_dict(self, rank: int) -> Dict[str, Any]:
        return {
            "rank": rank,
            "score": round(float(self.score), 3),
            "source_type": self.source_type,
            "source": self.source,
            "path": self.path,
            "title": self.title,
            "distance": self.distance,
            "origin": self.origin,
            "term_coverage": round(float(self.term_coverage), 3),
            "matched_terms": self.matched_terms or [],
            "filename_matched_terms": self.filename_matched_terms or [],
            "exact_phrase": self.exact_phrase,
            "reasons": self.reasons or [],
            "metadata": self.metadata or {},
            "text": self.text,
        }


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _safe_relative(project_path: Path, path: Path) -> Optional[str]:
    try:
        return str(path.resolve().relative_to(project_path.resolve())).replace("\\", "/")
    except Exception:
        return None


def _is_blocked_path(path: Path, project_path: Path) -> bool:
    relative = _safe_relative(project_path, path)

    if relative is None:
        return True

    for part in Path(relative).parts:
        if part in BLOCKED_DIR_NAMES:
            return True

    name = path.name.lower()

    if name.startswith(("add_", "fix_", "install_", "patch_")) and name.endswith((".py", ".ps1", ".bat")):
        return True

    if "rag_engine_v1_1" in name or "rag_engine_v1_2" in name:
        return True

    if name.endswith(".pyc") or "_backup_" in name:
        return True

    if name in {
        "tool_log.jsonl",
        "task_history.jsonl",
        "autonomous_learning_log.jsonl",
        "ingested_files.jsonl",
        "memory_log.jsonl",
    }:
        return True

    return False


def _read_text_safely(path: Path, max_chars: int = MAX_FILE_SCAN_BYTES) -> str:
    try:
        if path.stat().st_size > max_chars * 4:
            return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def _normalize_text(text: str) -> str:
    text = str(text).lower()
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _query_terms(query: str) -> List[str]:
    normalized = _normalize_text(query)
    words = re.findall(r"[a-zåäö0-9+]{3,}", normalized, flags=re.IGNORECASE)

    stopwords = {
        "miten", "mikä", "mita", "mitä", "missä", "missa", "kuka", "että",
        "joka", "tämä", "tama", "nämä", "nama", "sitä", "sita", "minun",
        "sinun", "pitää", "pitaa", "toimia", "kertoa", "näytä", "nayta",
        "hae", "etsi", "muistista", "ragista", "search", "about", "what",
        "how", "the", "and", "for", "with", "from", "this", "that",
        "säde", "sade", "säteelle", "sateelle", "säteessä", "sateessa",
        "saa", "voi", "voiko", "pystyy", "pitäisi", "pitaisi",
        "tiedosto", "tiedostosta", "asia", "asiat",
    }

    clean = []

    for word in words:
        word = word.lower()

        if word not in stopwords and word not in clean:
            clean.append(word)

    return clean[:20]


def _term_matches(term: str, haystack: str) -> bool:
    haystack = _normalize_text(haystack)
    term = _normalize_text(term)

    if not term:
        return False

    if term in haystack:
        return True

    endings = [
        "ssa", "ssä", "sta", "stä", "lla", "llä", "lle", "ksi", "nen",
        "minen", "ista", "istä", "ihin", "issa", "issä", "ing", "ed", "es", "s",
    ]

    for ending in endings:
        if term.endswith(ending) and len(term) > len(ending) + 3:
            stem = term[:-len(ending)]

            if stem and stem in haystack:
                return True

    return False


def _keyword_overlap(query: str, text: str) -> Tuple[int, List[str]]:
    terms = _query_terms(query)
    matched = [term for term in terms if _term_matches(term, text)]
    return len(matched), matched


def _filename_overlap(query: str, source: str, path: str, title: str) -> Tuple[int, List[str]]:
    terms = _query_terms(query)
    haystack = " ".join([source, path, title])
    matched = [term for term in terms if _term_matches(term, haystack)]
    return len(matched), matched


def _query_exact_phrase_in(query: str, text: str) -> bool:
    phrase = _normalize_text(query)

    if not phrase:
        return False

    return phrase in _normalize_text(text)


def _classify_source(source: str, path: str, title: str, text: str = "") -> str:
    joined = f"{source} {path} {title}".lower()

    if "learning_reviews" in joined or "learning review" in joined:
        return "learning_review"

    if "sade_operating_manual" in joined or "operating manual" in joined:
        return "operating_manual"

    if "memory_policy" in joined or "guardrails" in joined or "knowledge_mapping" in joined:
        return "atlas"

    if "atlas" in joined or "sade_atlas_pack" in joined:
        return "atlas"

    if "sade_memory.md" in joined or source == "sade_memory.md":
        return "sade_memory"

    if "chat_log.md" in joined or source == "chat_log.md":
        return "chat_log"

    if joined.startswith("file:uploads/") or "uploads/" in joined:
        return "uploaded_file"

    if "system_prompt" in joined or "tools_layer_notes" in joined or "readme" in joined:
        return "project_doc"

    return "unknown"


def _semantic_similarity_from_distance(distance: Optional[float]) -> float:
    if distance is None:
        return 0.0

    try:
        distance = float(distance)
    except Exception:
        return 0.0

    if math.isnan(distance):
        return 0.0

    return max(0.0, 35.0 / (1.0 + distance))


def _required_coverage(query: str) -> float:
    terms = _query_terms(query)

    if len(terms) <= 1:
        return 1.0

    if len(terms) == 2:
        return 1.0

    return 0.67


def _score_candidate(candidate: RagCandidate, query: str) -> RagCandidate:
    terms = _query_terms(query)

    all_text = " ".join([
        candidate.source,
        candidate.path,
        candidate.title,
        candidate.text,
    ])

    metadata_text = " ".join([
        candidate.source,
        candidate.path,
        candidate.title,
    ])

    overlap_count, matched_terms = _keyword_overlap(query, all_text)
    filename_count, filename_terms = _filename_overlap(query, candidate.source, candidate.path, candidate.title)
    exact_phrase = _query_exact_phrase_in(query, metadata_text) or _query_exact_phrase_in(query, candidate.text[:2500])

    coverage = 1.0

    if terms:
        coverage = overlap_count / len(terms)

    filename_coverage = 0.0

    if terms:
        filename_coverage = filename_count / len(terms)

    priority = SOURCE_PRIORITIES.get(candidate.source_type, SOURCE_PRIORITIES["unknown"])

    if overlap_count == 0 and filename_count == 0 and not exact_phrase:
        effective_priority = min(priority * 0.18, 22)
    else:
        effective_priority = priority

    reasons = [
        f"source_priority:{priority}",
        f"effective_priority:{round(effective_priority, 1)}",
        f"term_coverage:{round(coverage, 2)}",
    ]

    if matched_terms:
        reasons.append("matched_terms:" + ", ".join(matched_terms[:8]))

    if filename_terms:
        reasons.append("filename_terms:" + ", ".join(filename_terms[:8]))

    if exact_phrase:
        reasons.append("exact_phrase")

    score = float(effective_priority)
    score += _semantic_similarity_from_distance(candidate.distance)
    score += overlap_count * 10
    score += filename_count * 18

    if exact_phrase:
        score += 35

    if terms and filename_count == len(terms):
        score += 80
        reasons.append("all_terms_in_filename_or_path")

    if terms and overlap_count == len(terms):
        score += 35
        reasons.append("all_terms_matched")

    if terms and len(terms) >= 2:
        required = _required_coverage(query)

        if coverage < required and filename_coverage < required and not exact_phrase:
            penalty = 85 if coverage == 0 else 55
            score -= penalty
            reasons.append(f"coverage_penalty:-{penalty}")

    if candidate.source_type == "chat_log":
        score -= 45

        if overlap_count == 0 and filename_count == 0 and not exact_phrase:
            score -= 60

        reasons.append("chat_log_demoted")

    if candidate.source_type in {"learning_review", "atlas", "operating_manual", "sade_memory"}:
        if overlap_count > 0 or filename_count > 0 or exact_phrase:
            score += 10
            reasons.append("trusted_source_with_match")
        else:
            reasons.append("trusted_source_without_match_no_bonus")

    candidate.score = score
    candidate.reasons = reasons
    candidate.term_coverage = coverage
    candidate.matched_terms = matched_terms
    candidate.filename_matched_terms = filename_terms
    candidate.exact_phrase = exact_phrase

    return candidate


def _passes_relevance_gate(candidate: RagCandidate, query: str) -> bool:
    terms = _query_terms(query)

    if not terms:
        return True

    all_text = " ".join([
        candidate.source,
        candidate.path,
        candidate.title,
        candidate.text,
    ])

    overlap_count, _ = _keyword_overlap(query, all_text)
    filename_count, _ = _filename_overlap(query, candidate.source, candidate.path, candidate.title)
    exact_phrase = _query_exact_phrase_in(query, all_text[:3500])

    if exact_phrase:
        return True

    if filename_count == len(terms):
        return True

    if len(terms) == 1:
        return overlap_count >= 1 or filename_count >= 1

    required = _required_coverage(query)
    coverage = overlap_count / len(terms)
    filename_coverage = filename_count / len(terms)

    return coverage >= required or filename_coverage >= required


def _content_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8", errors="ignore")).hexdigest()


def _dedupe_candidates(candidates: List[RagCandidate]) -> List[RagCandidate]:
    seen = set()
    result = []

    for item in candidates:
        metadata = item.metadata or {}
        sha = metadata.get("sha256") or metadata.get("source_sha256")
        text_key = _content_hash(item.text[:3000]) if item.text else ""

        if sha:
            key = f"sha:{sha}|text:{text_key[:16]}"
        else:
            key = f"text:{text_key[:24]}|title:{_normalize_text(item.title)[:80]}"

        if key in seen:
            continue

        seen.add(key)
        result.append(item)

    return result


def _limit_per_path(candidates: List[RagCandidate], max_per_path: int = MAX_RESULTS_PER_PATH) -> List[RagCandidate]:
    counts: Dict[str, int] = {}
    result: List[RagCandidate] = []

    for item in candidates:
        key = item.path or item.source or "unknown"
        counts[key] = counts.get(key, 0) + 1

        if counts[key] <= max_per_path:
            result.append(item)

    return result


def _trim_text(text: str, max_chars: int = 1400) -> str:
    clean = re.sub(r"\n{3,}", "\n\n", text.strip())

    if len(clean) <= max_chars:
        return clean

    return clean[:max_chars].rstrip() + "\n...[katkaistu]"


def _chunk_markdownish(text: str, max_chars: int = 1200) -> List[str]:
    parts = []
    blocks = re.split(r"\n(?=#{1,6}\s+)", text)

    for block in blocks:
        block = block.strip()

        if not block:
            continue

        if len(block) <= max_chars:
            parts.append(block)
            continue

        paragraphs = [p.strip() for p in block.split("\n\n") if p.strip()]
        current = ""

        for paragraph in paragraphs:
            candidate = (current + "\n\n" + paragraph).strip() if current else paragraph

            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    parts.append(current)

                current = paragraph[:max_chars]

        if current:
            parts.append(current)

    return parts


def _lexical_candidates_from_file(
    project_path: Path,
    file_path: Path,
    query: str,
    source_type: str,
    origin: str,
    max_candidates: int = 4,
) -> List[RagCandidate]:
    if not file_path.exists() or not file_path.is_file():
        return []

    if file_path.suffix.lower() not in SAFE_EXTENSIONS:
        return []

    if _is_blocked_path(file_path, project_path):
        return []

    text = _read_text_safely(file_path)

    if not text.strip():
        return []

    relative = _safe_relative(project_path, file_path) or str(file_path)
    chunks = _chunk_markdownish(text, max_chars=1400)
    scored = []

    for chunk in chunks:
        overlap, matched = _keyword_overlap(query, f"{relative} {chunk}")
        filename_count, filename_terms = _filename_overlap(query, file_path.name, relative, file_path.stem)
        exact = _query_exact_phrase_in(query, f"{relative} {chunk}")

        if overlap <= 0 and filename_count <= 0 and not exact:
            continue

        candidate = RagCandidate(
            source_type=source_type,
            source=file_path.name,
            path=relative,
            title=file_path.stem.replace("_", " ").replace("-", " ").title(),
            text=chunk,
            origin=origin,
            metadata={"matched_terms": matched, "filename_terms": filename_terms},
        )

        if not _passes_relevance_gate(candidate, query):
            continue

        scored.append(_score_candidate(candidate, query))

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:max_candidates]


def _learning_review_candidates(project_path: Path, query: str) -> List[RagCandidate]:
    results: List[RagCandidate] = []
    log_path = project_path / "memory" / "learning_reviews.jsonl"

    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                item = json.loads(line)
            except Exception:
                continue

            if not isinstance(item, dict):
                continue

            fields = [
                str(item.get("title", "")),
                str(item.get("relative_path", "")),
                " ".join(item.get("terms") or []),
                " ".join(item.get("learning_points") or []),
                " ".join(item.get("project_relevance") or []),
                " ".join(item.get("remember_later") or []),
                " ".join(item.get("future_tasks") or []),
            ]

            haystack = "\n".join(fields)
            overlap, matched = _keyword_overlap(query, haystack)
            filename_count, filename_terms = _filename_overlap(
                query,
                "learning_reviews.jsonl",
                str(item.get("relative_path", "")),
                str(item.get("title", "")),
            )
            exact = _query_exact_phrase_in(query, haystack)

            if overlap <= 0 and filename_count <= 0 and not exact:
                continue

            text = item.get("markdown") or haystack
            candidate = RagCandidate(
                source_type="learning_review",
                source="learning_reviews.jsonl",
                path=str(item.get("relative_path", "")),
                title=str(item.get("title", "")),
                text=_trim_text(text, max_chars=1600),
                origin="learning_review_log",
                metadata={
                    "review_id": item.get("review_id"),
                    "matched_terms": matched,
                    "filename_terms": filename_terms,
                    "created_at": item.get("created_at"),
                    "sha256": item.get("sha256"),
                },
            )

            if not _passes_relevance_gate(candidate, query):
                continue

            results.append(_score_candidate(candidate, query))

    md_path = project_path / "memory" / "learning_reviews.md"
    results.extend(
        _lexical_candidates_from_file(
            project_path,
            md_path,
            query,
            source_type="learning_review",
            origin="learning_reviews_md",
            max_candidates=5,
        )
    )

    return results


def _sade_memory_candidates(project_path: Path, query: str) -> List[RagCandidate]:
    return _lexical_candidates_from_file(
        project_path,
        project_path / "memory" / "sade_memory.md",
        query,
        source_type="sade_memory",
        origin="sade_memory_lexical",
        max_candidates=5,
    )


def _important_upload_candidates(project_path: Path, query: str) -> List[RagCandidate]:
    uploads = project_path / "uploads"
    results: List[RagCandidate] = []

    if not uploads.exists():
        return results

    curated_tokens = [
        "atlas", "manual", "notes", "roadmap", "policy", "guardrails", "rag",
        "sade_project", "knowledge", "memory", "operating"
    ]

    files = []

    for file_path in uploads.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SAFE_EXTENSIONS:
            continue

        if _is_blocked_path(file_path, project_path):
            continue

        relative = _safe_relative(project_path, file_path) or ""

        if not any(token in relative.lower() for token in curated_tokens):
            continue

        files.append(file_path)

    for file_path in sorted(files, key=lambda item: str(item).lower())[:120]:
        relative = _safe_relative(project_path, file_path) or str(file_path)
        source_type = _classify_source(file_path.name, relative, file_path.stem)

        results.extend(
            _lexical_candidates_from_file(
                project_path,
                file_path,
                query,
                source_type=source_type,
                origin="curated_upload_lexical",
                max_candidates=3,
            )
        )

    return results


def _semantic_candidates(project_path: Path, query: str, n_results: int = 12) -> List[RagCandidate]:
    try:
        from app.semantic_memory import search_semantic_memory
    except Exception:
        return []

    try:
        search_result = search_semantic_memory(
            project_path,
            query,
            n_results=max(1, min(int(n_results), 24))
        )
    except Exception:
        return []

    if not search_result.get("ok"):
        return []

    results = []

    for item in search_result.get("results") or []:
        metadata = item.get("metadata") or {}
        source = str(metadata.get("source", "tuntematon"))
        path = str(metadata.get("path", ""))
        title = str(metadata.get("title", ""))

        if source.startswith("file:") and not path:
            path = source.replace("file:", "", 1)

        text = str(item.get("text", "")).strip()
        source_type = _classify_source(source, path, title, text)

        candidate = RagCandidate(
            source_type=source_type,
            source=source,
            path=path,
            title=title,
            text=text,
            distance=item.get("distance"),
            base_rank=item.get("rank"),
            origin="semantic_memory",
            metadata=metadata,
        )

        if not _passes_relevance_gate(candidate, query):
            continue

        results.append(_score_candidate(candidate, query))

    return results



def _metadata_text(candidate: RagCandidate) -> str:
    return " ".join([
        candidate.source or "",
        candidate.path or "",
        candidate.title or "",
        str((candidate.metadata or {}).get("source", "")),
        str((candidate.metadata or {}).get("relative_path", "")),
    ])


def _metadata_matches_all_terms(candidate: RagCandidate, query: str) -> bool:
    terms = _query_terms(query)

    if not terms:
        return True

    metadata = _metadata_text(candidate)
    return all(_term_matches(term, metadata) for term in terms)


def _is_strict_document_query(query: str) -> bool:
    terms = set(_query_terms(query))

    strict_pairs = [
        {"operating", "manual"},
        {"memory", "policy"},
        {"knowledge", "mapping"},
    ]

    return any(pair.issubset(terms) for pair in strict_pairs)


def _document_intent_passes(candidate: RagCandidate, query: str) -> bool:
    if not _is_strict_document_query(query):
        return True

    if _metadata_matches_all_terms(candidate, query):
        return True

    query_terms = set(_query_terms(query))

    if {"operating", "manual"}.issubset(query_terms) and candidate.source_type == "operating_manual":
        return True

    return False


def rag_search(
    project_path: Path,
    query: str,
    n_results: int = DEFAULT_N_RESULTS,
    include_chat_log: bool = False,
    min_score: float = DEFAULT_MIN_SCORE,
) -> Dict[str, Any]:
    clean_query = query.strip()

    if not clean_query:
        return {
            "ok": False,
            "message": "Hakusana ei saa olla tyhjä.",
            "query": query,
            "results": [],
        }

    n_results = max(1, min(int(n_results), 20))

    candidates: List[RagCandidate] = []
    candidates.extend(_learning_review_candidates(project_path, clean_query))
    candidates.extend(_sade_memory_candidates(project_path, clean_query))
    candidates.extend(_important_upload_candidates(project_path, clean_query))
    candidates.extend(_semantic_candidates(project_path, clean_query, n_results=max(12, n_results * 2)))

    total_before_dedupe = len(candidates)
    candidates = _dedupe_candidates(candidates)

    filtered = []
    chat_count = 0

    for candidate in candidates:
        candidate = _score_candidate(candidate, clean_query)

        if not _passes_relevance_gate(candidate, clean_query):
            continue

        if not _document_intent_passes(candidate, clean_query):
            continue

        if candidate.score < min_score:
            continue

        if candidate.source_type == "chat_log":
            if not include_chat_log:
                continue

            chat_count += 1

            if chat_count > CHAT_LOG_MAX_RESULTS:
                continue

        filtered.append(candidate)

    filtered.sort(key=lambda item: item.score, reverse=True)
    filtered = _limit_per_path(filtered, max_per_path=MAX_RESULTS_PER_PATH)
    selected = filtered[:n_results]

    return {
        "ok": True,
        "message": "RAG-haku valmis.",
        "version": "1.2-document-intent",
        "query": clean_query,
        "query_terms": _query_terms(clean_query),
        "count": len(selected),
        "total_candidates": len(candidates),
        "total_before_dedupe": total_before_dedupe,
        "include_chat_log": include_chat_log,
        "min_score": min_score,
        "created_at": _now(),
        "ranking_rules": [
            "term_coverage_gate",
            "filename_path_title_boost",
            "source_priority_requires_match",
            "chat_log_demoted_or_excluded",
            "content_hash_dedupe",
            "per_path_result_limit",
            "strict_document_intent_gate",
            "exclude_patch_scripts_from_rag",
        ],
        "results": [item.to_dict(index + 1) for index, item in enumerate(selected)],
    }


def format_rag_results(search_result: Dict[str, Any], max_chars: int = DEFAULT_MAX_CONTEXT_CHARS) -> str:
    if not search_result.get("ok"):
        return ""

    results = search_result.get("results") or []

    if not results:
        return ""

    parts = []

    for item in results:
        header = (
            f"[{item.get('rank')}] "
            f"type={item.get('source_type')} "
            f"score={item.get('score')} "
            f"coverage={item.get('term_coverage')} "
            f"source={item.get('source')}"
        )

        if item.get("path"):
            header += f" path={item.get('path')}"

        if item.get("title"):
            header += f" title={item.get('title')}"

        text = _trim_text(str(item.get("text", "")), max_chars=1200)
        parts.append(header + "\n" + text)

    context = "\n\n---\n\n".join(parts).strip()

    if len(context) <= max_chars:
        return context

    return context[:max_chars].rstrip() + "\n\n[RAG-konteksti katkaistu pituuden vuoksi.]"


def build_rag_context(
    project_path: Path,
    query: str,
    n_results: int = DEFAULT_N_RESULTS,
    max_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
    include_chat_log: bool = False,
    min_score: float = DEFAULT_MIN_SCORE,
) -> str:
    result = rag_search(
        project_path,
        query,
        n_results=n_results,
        include_chat_log=include_chat_log,
        min_score=min_score,
    )

    context = format_rag_results(result, max_chars=max_chars)

    if not context:
        return (
            "RAG-haku ei löytänyt riittävän laadukasta kontekstia. "
            "Älä keksi muistista löytyneitä tietoja, jos niitä ei ole annettu tässä."
        )

    return context


def format_rag_search_reply(search_result: Dict[str, Any], max_item_chars: int = 1200) -> str:
    if not search_result.get("ok"):
        return search_result.get("message", "RAG-haku epäonnistui.")

    results = search_result.get("results") or []
    query = search_result.get("query", "")

    if not results:
        terms = ", ".join(search_result.get("query_terms") or [])

        return (
            f"En löytänyt riittävän laadukkaita RAG-osumia haulle `{query}`.\n\n"
            f"Hakutermit: `{terms}`\n\n"
            "Tämä on parempi kuin väärän lähteen näyttäminen. "
            "Kannattaa tarkistaa, onko aiheesta tehty atlas, Learning Review tai onko tiedosto opittu muistiin."
        )

    lines = [
        f"Löysin RAG-haulla {len(results)} laadukasta osumaa haulle `{query}`:",
        f"Versio: {search_result.get('version', '1.x')}",
        f"Hakutermit: `{', '.join(search_result.get('query_terms') or [])}`",
        "",
    ]

    for item in results:
        lines.append(
            f"### {item.get('rank')}. {item.get('source_type')} — score {item.get('score')} — coverage {item.get('term_coverage')}"
        )

        if item.get("title"):
            lines.append(f"**Otsikko:** {item.get('title')}")

        if item.get("source"):
            lines.append(f"**Lähde:** `{item.get('source')}`")

        if item.get("path"):
            lines.append(f"**Polku:** `{item.get('path')}`")

        reasons = item.get("reasons") or []

        if reasons:
            lines.append(f"**Miksi valittu:** {', '.join(reasons[:6])}")

        lines.append("")
        lines.append(_trim_text(str(item.get("text", "")), max_chars=max_item_chars))
        lines.append("")

    return "\n".join(lines).strip()


def rag_status(project_path: Path) -> Dict[str, Any]:
    files = {
        "sade_memory": project_path / "memory" / "sade_memory.md",
        "learning_reviews_md": project_path / "memory" / "learning_reviews.md",
        "learning_reviews_log": project_path / "memory" / "learning_reviews.jsonl",
        "chat_log": project_path / "memory" / "chat_log.md",
        "uploads": project_path / "uploads",
    }

    status = {}

    for name, path in files.items():
        status[name] = {
            "path": str(path),
            "exists": path.exists(),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
        }

        if path.exists() and path.is_file():
            try:
                status[name]["size_bytes"] = path.stat().st_size
            except Exception:
                pass

    semantic = {}

    try:
        from app.semantic_memory import semantic_memory_status
        semantic = semantic_memory_status(project_path)
    except Exception as error:
        semantic = {
            "ok": False,
            "error": str(error),
        }

    return {
        "ok": True,
        "message": "RAG Engine v1.2 document intent fix on käytettävissä.",
        "version": "1.2-document-intent",
        "source_priorities": SOURCE_PRIORITIES,
        "chat_log_default": "demoted/excluded",
        "default_n_results": DEFAULT_N_RESULTS,
        "default_max_context_chars": DEFAULT_MAX_CONTEXT_CHARS,
        "default_min_score": DEFAULT_MIN_SCORE,
        "max_results_per_path": MAX_RESULTS_PER_PATH,
        "ranking_rules": [
            "term_coverage_gate",
            "filename_path_title_boost",
            "source_priority_requires_match",
            "chat_log_demoted_or_excluded",
            "content_hash_dedupe",
            "per_path_result_limit",
            "strict_document_intent_gate",
            "exclude_patch_scripts_from_rag",
        ],
        "files": status,
        "semantic_memory": semantic,
    }
