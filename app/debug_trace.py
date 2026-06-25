from __future__ import annotations

"""Kehittäjän jäljitettävyys: mitä reittiä pyyntö kulki ja miksi."""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


TRACE_FILE = "debug_trace.jsonl"


def _trace_path(project_root: Path) -> Path:
    path = Path(project_root).resolve() / "memory" / TRACE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _redact(item) for key, item in value.items() if str(key).lower() not in {"password", "token", "cookie"}}
    if isinstance(value, list):
        return [_redact(item) for item in value[:30]]
    text = str(value)
    text = re.sub(r"(?i)(password|salasana|token|api[_ -]?key)\s*[:=]\s*\S+", r"\1=[SENSUROITU]", text)
    text = re.sub(r"\bsk-[A-Za-z0-9_-]{12,}\b", "[SENSUROITU]", text)
    return text[:2000]


def write_trace(
    project_root: Path,
    *,
    event: str,
    user_message: str = "",
    route: str = "",
    decision: str = "",
    tool: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    created_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    message_hash = hashlib.sha256(str(user_message or "").encode("utf-8", errors="ignore")).hexdigest()[:16]
    entry = {
        "created_at": created_at,
        "event": event,
        "message_hash": message_hash,
        "message_preview": _redact(user_message)[:240],
        "route": route,
        "decision": decision,
        "tool": tool,
        "details": _redact(details or {}),
    }
    with _trace_path(project_root).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return {"ok": True, "entry": entry}


def read_traces(project_root: Path, limit: int = 50) -> Dict[str, Any]:
    path = _trace_path(project_root)
    items: List[Dict[str, Any]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return {
        "ok": True,
        "path": str(path),
        "count": len(items),
        "items": items[-max(1, min(int(limit), 200)):],
    }

