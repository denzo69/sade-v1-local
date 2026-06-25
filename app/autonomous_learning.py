from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json

from app.file_ingestion import ingest_file

try:
    from app.file_ingestion import TEXT_EXTENSIONS, MAX_INGEST_CHARS
except Exception:
    TEXT_EXTENSIONS = {
        ".py", ".html", ".htm", ".md", ".txt", ".json", ".css", ".js",
        ".yml", ".yaml", ".toml", ".ini", ".ps1", ".bat"
    }
    MAX_INGEST_CHARS = 250_000


BLOCKED_DIR_NAMES = {
    ".git", ".venv", "venv", "env", "__pycache__", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "vector_db"
}

DEFAULT_MAX_FILES = 10


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


def _ingestion_log_path(project_path: Path) -> Path:
    return _memory_path(project_path) / "ingested_files.jsonl"


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

    return False


def _read_ingestion_log(project_path: Path) -> Dict[str, Any]:
    path = _ingestion_log_path(project_path)
    hashes = set()
    path_hashes = set()
    paths = set()
    items: List[Dict[str, Any]] = []

    if not path.exists():
        return {
            "path": str(path),
            "hashes": hashes,
            "path_hashes": path_hashes,
            "paths": paths,
            "items": items,
        }

    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue

        if not isinstance(item, dict):
            continue

        items.append(item)

        sha = item.get("sha256")
        relative_path = item.get("relative_path")

        if sha:
            hashes.add(sha)

        if relative_path:
            paths.add(relative_path)

        if sha and relative_path:
            path_hashes.add(f"{relative_path}|{sha}")

    return {
        "path": str(path),
        "hashes": hashes,
        "path_hashes": path_hashes,
        "paths": paths,
        "items": items,
    }


def _read_text_for_hash(path: Path) -> Dict[str, Any]:
    content = path.read_text(encoding="utf-8")

    truncated = False

    if len(content) > MAX_INGEST_CHARS:
        content = content[:MAX_INGEST_CHARS]
        truncated = True

    return {
        "content": content,
        "sha256": _sha256(content),
        "truncated": truncated,
    }


def scan_uploads_for_learning(
    project_path: Path,
    include_already_ingested: bool = False,
    limit: int = 100,
) -> Dict[str, Any]:
    uploads = _uploads_path(project_path)
    ingestion_log = _read_ingestion_log(project_path)

    candidates: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    for path in sorted(uploads.rglob("*"), key=lambda item: str(item).lower()):
        if len(candidates) >= max(1, min(int(limit), 1000)):
            break

        if not path.is_file():
            continue

        relative_path = _relative(project_path, path)

        if _should_skip(path, project_path):
            skipped.append({
                "relative_path": relative_path,
                "reason": "blocked_path",
            })
            continue

        suffix = path.suffix.lower()

        if suffix not in TEXT_EXTENSIONS:
            skipped.append({
                "relative_path": relative_path,
                "reason": f"unsupported_extension:{suffix}",
            })
            continue

        try:
            hash_data = _read_text_for_hash(path)
        except UnicodeDecodeError:
            skipped.append({
                "relative_path": relative_path,
                "reason": "not_utf8_text",
            })
            continue
        except Exception as error:
            skipped.append({
                "relative_path": relative_path,
                "reason": str(error),
            })
            continue

        sha = hash_data["sha256"]
        path_hash = f"{relative_path}|{sha}"

        already_ingested = (
            sha in ingestion_log["hashes"]
            or path_hash in ingestion_log["path_hashes"]
        )

        if already_ingested and not include_already_ingested:
            skipped.append({
                "relative_path": relative_path,
                "reason": "already_ingested",
                "sha256": sha,
            })
            continue

        candidates.append({
            "relative_path": relative_path,
            "filename": path.name,
            "suffix": suffix,
            "size_bytes": path.stat().st_size,
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
            "sha256": sha,
            "truncated": hash_data["truncated"],
            "already_ingested": already_ingested,
        })

    return {
        "ok": True,
        "message": "Uploads-kansio skannattu oppimista varten.",
        "uploads_path": str(uploads),
        "ingestion_log": ingestion_log["path"],
        "candidate_count": len(candidates),
        "skipped_count": len(skipped),
        "candidates": candidates,
        "skipped": skipped[:100],
    }


def run_autonomous_learning_loop(
    project_path: Path,
    max_files: int = DEFAULT_MAX_FILES,
    add_to_memory: bool = True,
    add_to_semantic: bool = True,
) -> Dict[str, Any]:
    max_files = max(1, min(int(max_files), 100))

    scan = scan_uploads_for_learning(
        project_path,
        include_already_ingested=False,
        limit=max_files,
    )

    candidates = scan.get("candidates", [])[:max_files]
    learned: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []

    session = {
        "time": _now(),
        "event": "learning_loop_started",
        "max_files": max_files,
        "candidate_count": len(candidates),
        "add_to_memory": add_to_memory,
        "add_to_semantic": add_to_semantic,
    }
    _append_jsonl(_learning_log_path(project_path), session)

    for candidate in candidates:
        relative_path = candidate["relative_path"]

        try:
            result = ingest_file(
                project_path,
                relative_path,
                add_to_memory=add_to_memory,
                add_to_semantic=add_to_semantic,
                title=f"Autonomous learning: {candidate['filename']}",
                tags=["auto-learning", "file", "ingested"],
            )

            learned_item = {
                "relative_path": relative_path,
                "filename": candidate["filename"],
                "sha256": candidate["sha256"],
                "summary": (result.get("summary") or {}).get("summary"),
                "semantic_chunks": (result.get("semantic_memory") or {}).get("chunks"),
                "ok": result.get("ok"),
            }

            learned.append(learned_item)

            _append_jsonl(_learning_log_path(project_path), {
                "time": _now(),
                "event": "file_learned",
                **learned_item,
            })

        except Exception as error:
            failed_item = {
                "relative_path": relative_path,
                "filename": candidate.get("filename"),
                "error": str(error),
            }

            failed.append(failed_item)

            _append_jsonl(_learning_log_path(project_path), {
                "time": _now(),
                "event": "file_learning_failed",
                **failed_item,
            })

    final = {
        "time": _now(),
        "event": "learning_loop_finished",
        "learned_count": len(learned),
        "failed_count": len(failed),
    }
    _append_jsonl(_learning_log_path(project_path), final)

    return {
        "ok": True,
        "message": "Autonomous Learning Loop suoritettu.",
        "learning_log": str(_learning_log_path(project_path)),
        "scan": {
            "candidate_count": scan.get("candidate_count"),
            "skipped_count": scan.get("skipped_count"),
        },
        "learned_count": len(learned),
        "failed_count": len(failed),
        "learned": learned,
        "failed": failed,
    }


def get_learning_status(project_path: Path) -> Dict[str, Any]:
    scan = scan_uploads_for_learning(
        project_path,
        include_already_ingested=False,
        limit=100,
    )

    learning_log = _learning_log_path(project_path)
    learning_events = 0

    if learning_log.exists():
        learning_events = len(learning_log.read_text(encoding="utf-8").splitlines())

    return {
        "ok": True,
        "message": "Autonomous Learning Loop on käytettävissä.",
        "uploads_path": str(_uploads_path(project_path)),
        "ingestion_log": str(_ingestion_log_path(project_path)),
        "learning_log": str(learning_log),
        "pending_files": scan.get("candidate_count", 0),
        "learning_events": learning_events,
        "supported_extensions": sorted(TEXT_EXTENSIONS),
    }


def read_learning_log(project_path: Path, limit: int = 50) -> Dict[str, Any]:
    path = _learning_log_path(project_path)

    if not path.exists():
        return {
            "ok": True,
            "path": str(path),
            "count": 0,
            "items": [],
        }

    lines = path.read_text(encoding="utf-8").splitlines()
    selected = lines[-max(1, min(int(limit), 500)):]

    items: List[Dict[str, Any]] = []

    for line in selected:
        try:
            items.append(json.loads(line))
        except Exception:
            items.append({
                "event": "parse_error",
                "raw": line,
            })

    return {
        "ok": True,
        "path": str(path),
        "count": len(items),
        "items": items,
    }
