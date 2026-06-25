from __future__ import annotations

"""Semanttisen muistin turvallinen huolto: esikatselu ensin, poisto vain vahvistettuna."""

import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.audit_log import write_audit_event
from app.semantic_memory import _get_collection, _import_chromadb, _vector_db_path


CONFIRMATION_PHRASE = "HYVÄKSYN MUISTIHUOLLON"
PROTECTED_SOURCES = {"sade_memory.md", "learning_reviews.md", "manual", "learning_feedback"}


def _open_collection(project_root: Path):
    chromadb, embedding_functions, error = _import_chromadb()
    if error:
        raise RuntimeError(str(error))
    client = chromadb.PersistentClient(path=str(_vector_db_path(project_root)))
    return _get_collection(client, embedding_functions)


def _protected(metadata: Dict[str, Any]) -> bool:
    joined = " ".join(str(metadata.get(key, "")).lower() for key in ("source", "title", "path"))
    return any(source in joined for source in PROTECTED_SOURCES)


def plan_memory_cleanup(project_root: Path, *, older_than_days: int = 180) -> Dict[str, Any]:
    root = Path(project_root).resolve()
    try:
        collection = _open_collection(root)
        raw = collection.get(include=["documents", "metadatas"])
    except Exception as exc:
        return {"ok": False, "dry_run": True, "error": str(exc), "candidates": []}
    ids = raw.get("ids") or []
    documents = raw.get("documents") or []
    metadatas = raw.get("metadatas") or []
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(30, int(older_than_days)))
    seen: Dict[str, str] = {}
    candidates: List[Dict[str, Any]] = []
    for index, item_id in enumerate(ids):
        document = str(documents[index] if index < len(documents) else "")
        metadata = metadatas[index] if index < len(metadatas) and metadatas[index] else {}
        if _protected(metadata):
            continue
        digest = hashlib.sha256(" ".join(document.lower().split()).encode("utf-8")).hexdigest()
        reason = "duplicate" if digest in seen else ""
        seen.setdefault(digest, item_id)
        saved_at = metadata.get("saved_at") or metadata.get("indexed_at")
        if not reason and metadata.get("source") == "chat_log.md" and saved_at:
            try:
                parsed = datetime.fromisoformat(str(saved_at).replace("Z", "+00:00"))
                if parsed.astimezone(timezone.utc) < cutoff:
                    reason = "old_chat_log"
            except ValueError:
                pass
        if reason:
            candidates.append({"id": item_id, "reason": reason, "source": metadata.get("source", "unknown"), "preview": document[:160]})
    return {"ok": True, "dry_run": True, "count": collection.count(), "candidate_count": len(candidates), "candidates": candidates, "protected_sources": sorted(PROTECTED_SOURCES)}


def apply_memory_cleanup(project_root: Path, candidate_ids: List[str], *, confirmation: str) -> Dict[str, Any]:
    root = Path(project_root).resolve()
    if confirmation != CONFIRMATION_PHRASE:
        return {"ok": False, "deleted": 0, "message": "Muistihuolto vaatii täsmällisen vahvistuslauseen."}
    plan = plan_memory_cleanup(root)
    allowed = {item["id"] for item in plan.get("candidates") or []}
    selected = [item_id for item_id in candidate_ids if item_id in allowed]
    if not selected:
        return {"ok": False, "deleted": 0, "message": "Hyväksyttyjä poistoehdokkaita ei annettu."}
    write_audit_event(root, category="memory", action="memory_cleanup", outcome="attempt", risk_level="high", reason="Hyväksytty muistihuolto aloitetaan.", target="memory/vector_db", details={"count": len(selected)})
    collection = _open_collection(root)
    collection.delete(ids=selected)
    write_audit_event(root, category="memory", action="memory_cleanup", outcome="success", risk_level="high", reason="Hyväksytyt muistimerkinnät poistettiin.", target="memory/vector_db", details={"count": len(selected)})
    return {"ok": True, "deleted": len(selected), "remaining": collection.count()}

