from __future__ import annotations

"""Rakenteinen oppimispalaute Janin tekemille korjauksille."""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.audit_log import write_audit_event


FEEDBACK_FILE = "learning_feedback.jsonl"
MAX_TEXT_CHARS = 4000


def _root(project_root: Optional[Path] = None) -> Path:
    return Path(project_root or Path(__file__).resolve().parent.parent).resolve()


def feedback_path(project_root: Optional[Path] = None) -> Path:
    path = _root(project_root) / "memory" / FEEDBACK_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _clean(value: str) -> str:
    value = " ".join(str(value or "").split()).strip()
    patterns = [
        r"(?i)(api[_ -]?key|token|password|salasana)\s*[:=]\s*\S+",
        r"\bsk-[A-Za-z0-9_-]{12,}\b",
    ]
    for pattern in patterns:
        value = re.sub(pattern, "[SENSUROITU]", value)
    return value[:MAX_TEXT_CHARS]


def record_feedback(
    project_root: Optional[Path],
    *,
    correction: str,
    original: str = "",
    category: str = "general",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    correction = _clean(correction)
    original = _clean(original)
    if not correction:
        return {"ok": False, "message": "Korjaus puuttuu."}
    root = _root(project_root)
    created_at = _now()
    feedback_id = hashlib.sha256(f"{created_at}|{original}|{correction}".encode("utf-8")).hexdigest()[:16]
    entry = {
        "id": feedback_id,
        "created_at": created_at,
        "original": original,
        "correction": correction,
        "category": _clean(category) or "general",
        "tags": [_clean(tag) for tag in (tags or []) if _clean(tag)],
        "status": "active",
        "semantic_memory_written": False,
    }
    write_audit_event(root, category="learning", action="record_feedback", outcome="attempt", risk_level="medium", reason="Käyttäjän korjaus tallennetaan oppimispalautteeksi.", target=FEEDBACK_FILE, details={"feedback_id": feedback_id})
    with feedback_path(root).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    write_audit_event(root, category="learning", action="record_feedback", outcome="success", risk_level="medium", reason="Oppimispalaute tallennettiin.", target=FEEDBACK_FILE, details={"feedback_id": feedback_id})
    return {"ok": True, "entry": entry, "path": str(feedback_path(root))}


def read_feedback(project_root: Optional[Path] = None, limit: int = 50) -> Dict[str, Any]:
    path = feedback_path(project_root)
    items: List[Dict[str, Any]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
            except Exception:
                continue
            if item.get("status") == "active":
                items.append(item)
    return {"ok": True, "count": len(items), "items": items[-max(1, min(limit, 200)):], "path": str(path)}


def build_feedback_context(project_root: Optional[Path] = None, limit: int = 8) -> str:
    items = read_feedback(project_root, limit=limit).get("items") or []
    if not items:
        return ""
    lines = ["Käyttäjän aiemmat korjaukset (noudata vain, kun ne sopivat nykyiseen tilanteeseen):"]
    for item in items:
        original = item.get("original") or "aiempi vastaus"
        lines.append(f"- {original} → {item.get('correction')}")
    return "\n".join(lines)


def parse_feedback_message(message: str) -> Optional[Dict[str, str]]:
    text = str(message or "").strip()
    match = re.match(r"(?is)^(?:korjaus|oppimispalaute)\s*:\s*(.+?)\s*(?:->|→)\s*(.+)$", text)
    if match:
        return {"original": match.group(1).strip(), "correction": match.group(2).strip()}
    return None

