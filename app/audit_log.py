from __future__ import annotations

"""Append-only audit log for security-relevant Säde v1 actions."""

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional
import json


AUDIT_LOG_FILENAME = "audit_log.jsonl"
GENESIS_HASH = "0" * 64
MAX_VALUE_CHARS = 800
SENSITIVE_KEYS = {
    "api_key", "apikey", "authorization", "cookie", "password", "secret",
    "token", "access_token", "refresh_token", "content", "text", "reply",
}
_WRITE_LOCK = Lock()


class AuditLogError(RuntimeError):
    pass


def resolve_project_root(project_root: Path) -> Path:
    root = Path(project_root).resolve()
    return root.parent if root.name.lower() == "app" else root


def audit_log_path(project_root: Path, create_parent: bool = False) -> Path:
    root = resolve_project_root(project_root)
    path = root / "app" / "memory" / AUDIT_LOG_FILENAME
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _sanitize(value: Any, key: str = "") -> Any:
    if key.lower() in SENSITIVE_KEYS:
        if value is None or value == "":
            return value
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): _sanitize(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value[:50]]
    if isinstance(value, str):
        return value if len(value) <= MAX_VALUE_CHARS else value[:MAX_VALUE_CHARS] + "…[truncated]"
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return str(value)[:MAX_VALUE_CHARS]


def _canonical(entry: Dict[str, Any]) -> str:
    payload = {key: value for key, value in entry.items() if key != "event_hash"}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _event_hash(entry: Dict[str, Any]) -> str:
    return sha256(_canonical(entry).encode("utf-8")).hexdigest()


def _load_entries(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    entries: List[Dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            raise AuditLogError(f"Audit-lokin rivi {line_number} ei ole kelvollista JSON-dataa.") from error
        if not isinstance(item, dict):
            raise AuditLogError(f"Audit-lokin rivi {line_number} ei ole objekti.")
        entries.append(item)
    return entries


def verify_audit_log(project_root: Path) -> Dict[str, Any]:
    path = audit_log_path(project_root)
    try:
        entries = _load_entries(path)
    except AuditLogError as error:
        return {"ok": False, "valid": False, "path": str(path), "count": 0, "error": str(error)}

    previous = GENESIS_HASH
    for index, entry in enumerate(entries, start=1):
        expected_sequence = index
        if entry.get("sequence") != expected_sequence:
            return {"ok": False, "valid": False, "path": str(path), "count": len(entries), "error": f"Virheellinen sequence rivillä {index}."}
        if entry.get("previous_hash") != previous:
            return {"ok": False, "valid": False, "path": str(path), "count": len(entries), "error": f"Hash-ketju katkesi rivillä {index}."}
        calculated = _event_hash(entry)
        if entry.get("event_hash") != calculated:
            return {"ok": False, "valid": False, "path": str(path), "count": len(entries), "error": f"Rivin {index} sisältöä on muutettu."}
        previous = calculated

    return {
        "ok": True,
        "valid": True,
        "path": str(path),
        "count": len(entries),
        "last_hash": previous,
        "last_event_at": entries[-1].get("time") if entries else None,
    }


def write_audit_event(
    project_root: Path,
    *,
    category: str,
    action: str,
    actor: str = "sade",
    outcome: str = "success",
    risk_level: str = "low",
    reason: str = "",
    target: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if outcome not in {"attempt", "success", "failure", "denied"}:
        raise ValueError("Tuntematon audit outcome.")
    if risk_level not in {"low", "medium", "high"}:
        raise ValueError("Tuntematon audit risk_level.")

    path = audit_log_path(project_root, create_parent=True)
    with _WRITE_LOCK:
        verification = verify_audit_log(project_root)
        if not verification["valid"]:
            raise AuditLogError(f"Audit-loki ei läpäissyt eheystarkistusta: {verification.get('error')}")

        sequence = int(verification["count"]) + 1
        entry: Dict[str, Any] = {
            "version": 1,
            "sequence": sequence,
            "time": _now(),
            "actor": str(actor),
            "category": str(category),
            "action": str(action),
            "outcome": outcome,
            "risk_level": risk_level,
            "reason": str(reason)[:MAX_VALUE_CHARS],
            "target": str(target)[:MAX_VALUE_CHARS] if target else None,
            "details": _sanitize(details or {}),
            "previous_hash": verification["last_hash"],
        }
        entry["event_hash"] = _event_hash(entry)
        with path.open("a", encoding="utf-8", newline="\n") as file:
            file.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")

    return {"ok": True, "path": str(path), "sequence": sequence, "event_hash": entry["event_hash"]}


def read_audit_log(project_root: Path, limit: int = 50) -> Dict[str, Any]:
    path = audit_log_path(project_root)
    verification = verify_audit_log(project_root)
    if not verification["valid"]:
        return {**verification, "items": []}
    entries = _load_entries(path)
    safe_limit = max(1, min(int(limit), 500))
    return {**verification, "items": entries[-safe_limit:]}


def audit_status(project_root: Path) -> Dict[str, Any]:
    return verify_audit_log(project_root)
