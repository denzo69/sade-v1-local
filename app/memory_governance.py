from __future__ import annotations

"""Käyttäjän muistin elinkaaren hallinta: näytä, vie ja poista hallitusti."""

import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.audit_log import write_audit_event


DELETE_CONFIRMATION = "HYVÄKSYN MUISTIMERKINNÄN POISTON"


def _memory_file(project_root: Path) -> Path:
    return Path(project_root).resolve() / "memory" / "sade_memory.md"


def _entry_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def list_memory_entries(project_root: Path, *, limit: int = 100) -> Dict[str, Any]:
    path = _memory_file(project_root)
    if not path.exists():
        return {"ok": True, "entries": [], "count": 0, "path": str(path)}
    content = path.read_text(encoding="utf-8", errors="ignore")
    chunks = [chunk.strip() for chunk in re.split(r"\n---\n", content) if chunk.strip()]
    entries: List[Dict[str, Any]] = []
    for chunk in chunks:
        title_match = re.search(r"^##\s+(.+)$", chunk, flags=re.MULTILINE)
        time_match = re.search(r"\*\*Aika:\*\*\s*(.+)", chunk)
        entries.append({
            "id": _entry_id(chunk),
            "title": title_match.group(1).strip() if title_match else "Säde-muisti",
            "time": time_match.group(1).strip() if time_match else None,
            "preview": chunk[:500],
            "characters": len(chunk),
        })
    return {"ok": True, "path": str(path), "count": len(entries), "entries": entries[-max(1, min(limit, 500)):]}


def export_memory_json(project_root: Path) -> Dict[str, Any]:
    root = Path(project_root).resolve()
    export_dir = root / "memory" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    payload = list_memory_entries(root, limit=500)
    payload["exported_at"] = datetime.now().isoformat(timespec="seconds")
    target = export_dir / f"sade_memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_audit_event(root, category="data", action="export_memory_json", outcome="success", risk_level="medium", reason="Käyttäjän muisti vietiin JSON-muotoon.", target=str(target))
    return {"ok": True, "path": str(target), "count": payload.get("count", 0)}


def delete_memory_entry(project_root: Path, entry_id: str, *, confirmation: str) -> Dict[str, Any]:
    root = Path(project_root).resolve()
    path = _memory_file(root)
    if confirmation != DELETE_CONFIRMATION:
        return {"ok": False, "deleted": False, "message": "Poisto vaatii täsmällisen vahvistuslauseen."}
    if not path.exists():
        return {"ok": False, "deleted": False, "message": "Säde-muistia ei löytynyt."}

    content = path.read_text(encoding="utf-8", errors="ignore")
    chunks = [chunk for chunk in re.split(r"(\n---\n)", content)]
    rebuilt: List[str] = []
    removed: Optional[str] = None
    index = 0
    while index < len(chunks):
        part = chunks[index]
        if part == "\n---\n" and index + 1 < len(chunks):
            candidate = chunks[index + 1]
            candidate_id = _entry_id(candidate.strip())
            if candidate_id == entry_id:
                removed = candidate
                index += 2
                continue
        elif part.strip() and _entry_id(part.strip()) == entry_id:
            removed = part
            index += 1
            continue
        rebuilt.append(part)
        index += 1

    if removed is None:
        return {"ok": False, "deleted": False, "message": "Muistimerkintää ei löytynyt annetulla id:llä."}

    backup = path.with_name(f"{path.stem}_before_delete_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}")
    shutil.copy2(path, backup)
    write_audit_event(root, category="memory", action="delete_memory_entry", outcome="attempt", risk_level="high", reason="Käyttäjä hyväksyi yksittäisen muistimerkinnän poiston.", target=entry_id, details={"backup": str(backup)},)
    path.write_text("".join(rebuilt).strip() + "\n", encoding="utf-8")
    write_audit_event(root, category="memory", action="delete_memory_entry", outcome="success", risk_level="high", reason="Yksittäinen muistimerkintä poistettiin.", target=entry_id, details={"backup": str(backup)},)
    return {"ok": True, "deleted": True, "entry_id": entry_id, "backup": str(backup)}

