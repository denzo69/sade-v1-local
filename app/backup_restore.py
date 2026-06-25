from __future__ import annotations

"""Varmuuskopiointi ja palautus Säde v1:n arvokkaalle datalle."""

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from app.audit_log import write_audit_event


RESTORE_CONFIRMATION = "HYVÄKSYN VARMUUSKOPION PALAUTUKSEN"
BACKUP_DIRNAME = "backups"


def _backup_dir(project_root: Path) -> Path:
    path = Path(project_root).resolve() / "memory" / BACKUP_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def _backup_candidates(project_root: Path) -> List[Path]:
    root = Path(project_root).resolve()
    candidates: List[Path] = []
    for relative in ["memory", "docs"]:
        base = root / relative
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            name = path.name.lower()
            if name in {"auth.json", "auth_sessions.json"}:
                continue
            if "vector_db" in [part.lower() for part in path.parts]:
                continue
            if path.suffix.lower() in {".md", ".json", ".jsonl", ".txt"}:
                candidates.append(path)
    for path in [root / "config.json", root / "app" / "config.json"]:
        if path.exists() and path.is_file():
            candidates.append(path)
    return sorted(set(candidates), key=lambda item: str(item).lower())


def create_backup_archive(project_root: Path) -> Dict[str, Any]:
    root = Path(project_root).resolve()
    target = _backup_dir(root) / f"sade_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    files = _backup_candidates(root)
    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(root),
        "files": [],
        "excluded": ["auth.json", "auth_sessions.json", "vector_db"],
    }
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = str(path.relative_to(root)).replace("\\", "/")
            archive.write(path, relative)
            manifest["files"].append(relative)
        archive.writestr("backup_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write_audit_event(root, category="data", action="create_backup_archive", outcome="success", risk_level="medium", reason="Säde-datasta luotiin zip-varmuuskopio.", target=str(target), details={"file_count": len(files)})
    return {"ok": True, "path": str(target), "file_count": len(files), "manifest": manifest}


def list_backup_archives(project_root: Path) -> Dict[str, Any]:
    backups = []
    for path in _backup_dir(project_root).glob("sade_backup_*.zip"):
        backups.append({
            "name": path.name,
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        })
    return {"ok": True, "count": len(backups), "backups": sorted(backups, key=lambda item: item["name"], reverse=True)}


def restore_backup_archive(project_root: Path, backup_name: str, *, confirmation: str) -> Dict[str, Any]:
    root = Path(project_root).resolve()
    if confirmation != RESTORE_CONFIRMATION:
        return {"ok": False, "restored": False, "message": "Palautus vaatii täsmällisen vahvistuslauseen."}
    backup_path = (_backup_dir(root) / Path(backup_name).name).resolve()
    try:
        backup_path.relative_to(_backup_dir(root).resolve())
    except ValueError:
        return {"ok": False, "restored": False, "message": "Varmuuskopion polku ei ole sallittu."}
    if not backup_path.exists():
        return {"ok": False, "restored": False, "message": "Varmuuskopiota ei löytynyt."}
    write_audit_event(root, category="data", action="restore_backup_archive", outcome="attempt", risk_level="high", reason="Käyttäjä hyväksyi varmuuskopion palautuksen.", target=str(backup_path))
    restored: List[str] = []
    with zipfile.ZipFile(backup_path, "r") as archive:
        for member in archive.namelist():
            if member == "backup_manifest.json" or member.endswith("/"):
                continue
            target = (root / member).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(member))
            restored.append(member)
    write_audit_event(root, category="data", action="restore_backup_archive", outcome="success", risk_level="high", reason="Varmuuskopio palautettiin.", target=str(backup_path), details={"restored": restored})
    return {"ok": True, "restored": True, "backup": str(backup_path), "files": restored}
