from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json
import re
import uuid


SAFE_EXTENSIONS = {
    ".py", ".html", ".htm", ".md", ".txt", ".json", ".css", ".js",
    ".yml", ".yaml", ".toml", ".ini", ".ps1", ".bat"
}

BLOCKED_DIR_NAMES = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "vector_db"
}

MAX_REVIEW_CHARS = 250_000
DEFAULT_MAX_REVIEWS = 10

IMPORTANT_TERMS = [
    "rag", "retrieval-augmented generation", "semantic memory", "embeddings",
    "vector database", "chromadb", "ollama", "fastapi", "pydantic",
    "tool router", "tool use", "function calling", "task queue",
    "autonomous learning loop", "file ingestion", "dev mode", "codebase map",
    "guardrails", "human-in-the-loop", "approval flow", "patch proposal",
    "diff", "sandbox", "read-only", "write permission", "system prompt",
    "context window", "local ai", "agent", "autonomous agent",
    "python", "api", "upload", "memory", "learning review",
]

FINNISH_STOPWORDS = {
    "että", "joka", "jossa", "ovat", "tämä", "nämä", "sitä", "sillä",
    "myös", "kuin", "sekä", "mutta", "koska", "joten", "jonka", "tähän",
    "tätä", "sitten", "voidaan", "käyttää", "käytetään", "projektin",
    "projekti", "säde", "jani", "tiedosto", "tiedostot", "kansio",
    "tarkoittaa", "esimerkiksi", "hyvä", "tärkeä", "tärkeää",
}

ENGLISH_STOPWORDS = {
    "this", "that", "with", "from", "into", "when", "then", "than",
    "also", "have", "has", "are", "for", "and", "the", "you", "your",
    "project", "file", "files", "system", "means", "used", "using",
    "example", "important", "should", "could", "would", "local",
}


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _memory_path(project_path: Path) -> Path:
    path = project_path / "memory"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _uploads_path(project_path: Path) -> Path:
    path = project_path / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _reviews_md_path(project_path: Path) -> Path:
    return _memory_path(project_path) / "learning_reviews.md"


def _reviews_log_path(project_path: Path) -> Path:
    return _memory_path(project_path) / "learning_reviews.jsonl"


def _learning_log_path(project_path: Path) -> Path:
    return _memory_path(project_path) / "autonomous_learning_log.jsonl"


def _relative(project_path: Path, path: Path) -> str:
    return str(path.resolve().relative_to(project_path.resolve())).replace("\\", "/")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def _append_jsonl(path: Path, item: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(item, ensure_ascii=False) + "\n")


def _append_markdown(path: Path, markdown: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("# Learning Reviews\n\n", encoding="utf-8")

    with path.open("a", encoding="utf-8") as file:
        file.write("\n---\n\n")
        file.write(markdown.rstrip())
        file.write("\n")


def _should_skip(path: Path, project_path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(project_path.resolve())
    except ValueError:
        return True

    for part in relative.parts:
        if part in BLOCKED_DIR_NAMES:
            return True

    name = path.name.lower()

    if "_backup_" in name or name.endswith(".pyc"):
        return True

    if name in {
        "learning_reviews.md",
        "learning_reviews.jsonl",
        "autonomous_learning_log.jsonl",
        "tool_log.jsonl",
        "tasks.json",
        "task_history.jsonl",
        "ingested_files.jsonl",
    }:
        return True

    return False


def _safe_file_path(project_path: Path, relative_path: str) -> Path:
    cleaned = relative_path.strip().replace("\\", "/").lstrip("/")
    path = (project_path / cleaned).resolve()

    try:
        path.relative_to(project_path.resolve())
    except ValueError:
        raise ValueError("Tiedostopolku menee projektikansion ulkopuolelle.")

    if not path.exists():
        raise FileNotFoundError(f"Tiedostoa ei löytynyt: {cleaned}")

    if not path.is_file():
        raise ValueError("Polku ei ole tiedosto.")

    if _should_skip(path, project_path):
        raise ValueError("Tiedosto on estetyssä polussa tai estetty tiedosto.")

    if path.suffix.lower() not in SAFE_EXTENSIONS:
        raise ValueError(f"Tiedostotyyppi ei ole tuettu: {path.suffix}")

    return path


def _read_text(path: Path) -> Dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    truncated = False

    if len(content) > MAX_REVIEW_CHARS:
        content = content[:MAX_REVIEW_CHARS]
        truncated = True

    return {
        "content": content,
        "truncated": truncated,
        "sha256": _sha256(content),
    }


def _sentence_candidates(text: str) -> List[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    candidates = []

    for sentence in sentences:
        sentence = sentence.strip(" -•\t")
        if 45 <= len(sentence) <= 260:
            candidates.append(sentence)

    return candidates


def _headings(text: str) -> List[str]:
    results = []
    for match in re.finditer(r"^(#{1,6})\s+(.+)$", text, flags=re.MULTILINE):
        title = match.group(2).strip()
        if title and title.lower() not in {"tarkoitus", "purpose"}:
            results.append(title)
    return results[:20]


def _bullet_points(text: str) -> List[str]:
    results = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ", "• ")):
            item = stripped[2:].strip()
            if 8 <= len(item) <= 180:
                results.append(item)
    return results[:40]


def _extract_terms(text: str) -> List[str]:
    lower = text.lower()
    found = []

    for term in IMPORTANT_TERMS:
        if term in lower:
            found.append(term)

    words = re.findall(r"[A-Za-zÅÄÖåäö][A-Za-zÅÄÖåäö0-9_-]{3,}", lower)
    counts: Dict[str, int] = {}

    for word in words:
        if word in FINNISH_STOPWORDS or word in ENGLISH_STOPWORDS:
            continue
        if len(word) < 4:
            continue
        counts[word] = counts.get(word, 0) + 1

    frequent = [
        word for word, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        if count >= 2
    ][:15]

    combined = []

    for term in found + frequent:
        normalized = term.strip()
        if normalized and normalized not in combined:
            combined.append(normalized)

    return combined[:25]


def _main_learning_points(text: str) -> List[str]:
    bullets = _bullet_points(text)
    headings = _headings(text)
    sentences = _sentence_candidates(text)

    points: List[str] = []

    for heading in headings[:6]:
        points.append(f"Tiedostossa käsitellään aihetta: {heading}.")

    for bullet in bullets[:8]:
        if bullet not in points:
            points.append(bullet)

    if len(points) < 5:
        for sentence in sentences[:8]:
            if sentence not in points:
                points.append(sentence)

    return points[:10]


def _project_relevance(terms: List[str], relative_path: str) -> List[str]:
    joined = " ".join(terms).lower() + " " + relative_path.lower()
    relevance = []

    if any(term in joined for term in ["fastapi", "api", "pydantic", "python"]):
        relevance.append("Tämä vahvistaa Säde v1:n backend-, API- ja Python-rakenteen ymmärrystä.")

    if any(term in joined for term in ["rag", "semantic memory", "embeddings", "chromadb", "vector"]):
        relevance.append("Tämä liittyy Säde v1:n RAG-, semanttisen muistin ja vektorihaun kehittämiseen.")

    if any(term in joined for term in ["tool", "router", "function calling", "task queue"]):
        relevance.append("Tämä auttaa Sädeä ymmärtämään työkalukerrosta, tool routeria ja tehtäväjonoa.")

    if any(term in joined for term in ["guardrails", "approval", "sandbox", "read-only", "write permission"]):
        relevance.append("Tämä tukee turvallista agenttiarkkitehtuuria, jossa muutokset ovat rajattuja ja hyväksyttäviä.")

    if any(term in joined for term in ["job", "work", "linkedin", "hakemus", "työnhaku"]):
        relevance.append("Tämä auttaa Jania työnhaussa, osaamisen sanoittamisessa ja portfolio-projektin esittämisessä.")

    if any(term in joined for term in ["autonomous learning", "learning loop", "file ingestion", "upload"]):
        relevance.append("Tämä liittyy tiedostojen oppimiseen, upload-työnkulkuun ja Autonomous Learning Loopiin.")

    if not relevance:
        relevance.append("Tämä täydentää Säde v1:n muistia ja voi toimia myöhemmin RAG-kontekstina.")

    return relevance[:8]


def _future_tasks(terms: List[str], relative_path: str) -> List[str]:
    joined = " ".join(terms).lower() + " " + relative_path.lower()
    tasks = []

    if "guardrails" in joined:
        tasks.append("Suunnittele myöhemmin keskitetty guardrails.py-moduuli.")

    if "patch proposal" in joined or "diff" in joined or "approval" in joined:
        tasks.append("Rakenna myöhemmin Patch Proposal v1, jossa Säde ehdottaa diff-muutoksia ennen hyväksyntää.")

    if "rag" in joined or "semantic memory" in joined:
        tasks.append("Rakenna myöhemmin selkeä RAG Engine v1, joka hakee muistista kontekstin ennen vastausta.")

    if "fastapi" in joined or "python" in joined:
        tasks.append("Pidä FastAPI-rakenne modulaarisena ja siirrä kasvavaa logiikkaa omiin tiedostoihin.")

    if "job" in joined or "work" in joined or "linkedin" in joined or "työnhaku" in joined:
        tasks.append("Hyödynnä tätä tietoa CV:ssä, LinkedInissä ja hakemusteksteissä.")

    if "autonomous learning" in joined or "file ingestion" in joined:
        tasks.append("Paranna oppimissilmukkaa siten, että se tekee aina oppimiskatsauksen opituista tiedostoista.")

    if not tasks:
        tasks.append("Käytä tätä tiedostoa myöhemmin muistihakujen ja vastausten kontekstina.")

    return tasks[:8]


def _remember_later(points: List[str], terms: List[str]) -> List[str]:
    reminders = []

    if terms:
        reminders.append("Tärkeimmät käsitteet kannattaa tunnistaa ja käyttää myöhemmin hakusanoina.")

    if points:
        reminders.append("Tiedoston ydinasiat kannattaa hakea muistista ennen kuin aiheesta vastataan käyttäjälle.")

    if any("guardrails" in term for term in terms):
        reminders.append("Turvarajat pitää toteuttaa sekä prompt-ohjeina että kovina koodirajoina.")

    if any(term in {"rag", "semantic memory", "embeddings"} for term in terms):
        reminders.append("RAG parantaa vastauksia tuomalla oikean kontekstin mallille, mutta ei kouluta mallia uudelleen.")

    if any(term in {"task queue", "tool router", "tool use"} for term in terms):
        reminders.append("Agenttimaisuus kannattaa rakentaa vaiheittain: ensin työkalut, sitten jono, sitten hyväksyntä.")

    if not reminders:
        reminders.append("Tämä tiedosto on osa Säteen atlas-tietopohjaa ja täydentää myöhempää muistihakua.")

    return reminders[:6]


def _read_review_log(project_path: Path) -> List[Dict[str, Any]]:
    path = _reviews_log_path(project_path)

    if not path.exists():
        return []

    items = []

    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                items.append(item)
        except Exception:
            continue

    return items


def _already_reviewed(project_path: Path, relative_path: str, sha256: str) -> Optional[Dict[str, Any]]:
    for item in _read_review_log(project_path):
        if item.get("relative_path") == relative_path and item.get("sha256") == sha256:
            return item
    return None


def create_learning_review_for_file(
    project_path: Path,
    relative_path: str,
    force: bool = False,
) -> Dict[str, Any]:
    path = _safe_file_path(project_path, relative_path)
    read = _read_text(path)

    relative = _relative(project_path, path)
    sha = read["sha256"]

    existing = _already_reviewed(project_path, relative, sha)

    if existing and not force:
        return {
            "ok": True,
            "message": "Tästä tiedostoversiosta on jo oppimiskatsaus.",
            "already_exists": True,
            "review": existing,
        }

    content = read["content"]
    title = path.stem.replace("_", " ").replace("-", " ").strip().title()
    review_id = uuid.uuid4().hex[:12]

    headings = _headings(content)
    points = _main_learning_points(content)
    terms = _extract_terms(content)
    relevance = _project_relevance(terms, relative)
    remember = _remember_later(points, terms)
    future_tasks = _future_tasks(terms, relative)

    markdown_lines = [
        f"# Learning Review: {title}",
        "",
        f"- Review ID: `{review_id}`",
        f"- Source: `{relative}`",
        f"- Created: { _now() }",
        f"- SHA256: `{sha[:16]}...`",
        f"- Truncated: {read['truncated']}",
        "",
        "## Mitä opin",
        "",
    ]

    for point in points:
        markdown_lines.append(f"- {point}")

    markdown_lines.extend([
        "",
        "## Tärkeät käsitteet",
        "",
    ])

    for term in terms:
        markdown_lines.append(f"- {term}")

    markdown_lines.extend([
        "",
        "## Miten tämä liittyy Säde v1 -projektiin",
        "",
    ])

    for item in relevance:
        markdown_lines.append(f"- {item}")

    markdown_lines.extend([
        "",
        "## Mitä kannattaa muistaa myöhemmin",
        "",
    ])

    for item in remember:
        markdown_lines.append(f"- {item}")

    markdown_lines.extend([
        "",
        "## Mahdolliset jatkotehtävät",
        "",
    ])

    for task in future_tasks:
        markdown_lines.append(f"- {task}")

    markdown = "\n".join(markdown_lines)

    review_item = {
        "ok": True,
        "review_id": review_id,
        "created_at": _now(),
        "title": title,
        "relative_path": relative,
        "filename": path.name,
        "sha256": sha,
        "truncated": read["truncated"],
        "headings": headings,
        "learning_points": points,
        "terms": terms,
        "project_relevance": relevance,
        "remember_later": remember,
        "future_tasks": future_tasks,
        "markdown": markdown,
    }

    _append_markdown(_reviews_md_path(project_path), markdown)
    _append_jsonl(_reviews_log_path(project_path), review_item)

    return {
        "ok": True,
        "message": "Oppimiskatsaus luotu.",
        "already_exists": False,
        "review": review_item,
        "reviews_md": str(_reviews_md_path(project_path)),
        "reviews_log": str(_reviews_log_path(project_path)),
    }


def _candidate_paths_from_learning_log(project_path: Path, limit: int = 50) -> List[str]:
    path = _learning_log_path(project_path)
    results: List[str] = []

    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()

        for line in reversed(lines):
            try:
                item = json.loads(line)
            except Exception:
                continue

            if item.get("event") == "file_learned":
                relative = item.get("relative_path")
                if relative and relative not in results:
                    results.append(relative)

            if len(results) >= limit:
                break

    if results:
        return list(reversed(results))

    uploads = _uploads_path(project_path)

    for file in sorted(uploads.rglob("*"), key=lambda item: str(item).lower()):
        if len(results) >= limit:
            break

        if file.is_file() and file.suffix.lower() in SAFE_EXTENSIONS and not _should_skip(file, project_path):
            results.append(_relative(project_path, file))

    return results


def create_reviews_for_recent_learning(
    project_path: Path,
    max_files: int = DEFAULT_MAX_REVIEWS,
    force: bool = False,
) -> Dict[str, Any]:
    max_files = max(1, min(int(max_files), 100))
    candidates = _candidate_paths_from_learning_log(project_path, limit=max_files * 3)

    created = []
    skipped = []
    failed = []

    for relative in candidates:
        if len(created) >= max_files:
            break

        try:
            result = create_learning_review_for_file(project_path, relative, force=force)

            if result.get("already_exists"):
                skipped.append({
                    "relative_path": relative,
                    "reason": "already_reviewed",
                    "review_id": (result.get("review") or {}).get("review_id"),
                })
            else:
                review = result.get("review") or {}
                created.append({
                    "relative_path": relative,
                    "review_id": review.get("review_id"),
                    "title": review.get("title"),
                    "terms": review.get("terms", [])[:10],
                })

        except Exception as error:
            failed.append({
                "relative_path": relative,
                "error": str(error),
            })

    return {
        "ok": True,
        "message": "Oppimiskatsausajo suoritettu.",
        "created_count": len(created),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "created": created,
        "skipped": skipped[:50],
        "failed": failed,
        "reviews_md": str(_reviews_md_path(project_path)),
        "reviews_log": str(_reviews_log_path(project_path)),
    }


def read_learning_reviews(project_path: Path, limit: int = 50) -> Dict[str, Any]:
    items = _read_review_log(project_path)
    selected = items[-max(1, min(int(limit), 500)):]

    return {
        "ok": True,
        "count": len(selected),
        "total": len(items),
        "reviews_md": str(_reviews_md_path(project_path)),
        "reviews_log": str(_reviews_log_path(project_path)),
        "items": selected,
    }


def get_learning_review_status(project_path: Path) -> Dict[str, Any]:
    items = _read_review_log(project_path)
    md_path = _reviews_md_path(project_path)
    log_path = _reviews_log_path(project_path)

    return {
        "ok": True,
        "message": "Learning Review v1 on käytettävissä.",
        "reviews_count": len(items),
        "reviews_md": str(md_path),
        "reviews_log": str(log_path),
        "reviews_md_exists": md_path.exists(),
        "reviews_log_exists": log_path.exists(),
    }
