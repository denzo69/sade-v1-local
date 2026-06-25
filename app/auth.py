from __future__ import annotations

"""Säde v1:n paikallinen käyttäjä- ja istuntosuojaus."""

import argparse
import getpass
import hashlib
import hmac
import json
import re
import secrets
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


AUTH_FILENAME = "auth.json"
SESSIONS_FILENAME = "auth_sessions.json"
SESSION_COOKIE = "sade_session"
SESSION_TTL_SECONDS = 12 * 60 * 60
MAX_FAILED_ATTEMPTS = 5
FAILED_ATTEMPT_WINDOW_SECONDS = 15 * 60
SCRYPT_N = 2**15
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_MAXMEM = 64 * 1024 * 1024
MIN_PASSWORD_LENGTH = 12

_LOCK = threading.RLock()
_FAILURES: Dict[str, list[float]] = {}


def resolve_project_root(project_root: Optional[Path] = None) -> Path:
    root = Path(project_root or Path(__file__).resolve().parent.parent).resolve()
    return root.parent if root.name.lower() == "app" else root


def auth_path(project_root: Optional[Path] = None) -> Path:
    return resolve_project_root(project_root) / "app" / "memory" / AUTH_FILENAME


def sessions_path(project_root: Optional[Path] = None) -> Path:
    return resolve_project_root(project_root) / "app" / "memory" / SESSIONS_FILENAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_private_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def validate_username(username: str) -> str:
    value = str(username or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", value):
        raise ValueError("Käyttäjänimessä saa olla 3–32 kirjainta, numeroa tai merkkiä _ . -")
    return value


def validate_password(password: str) -> None:
    if len(password or "") < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Salasanassa pitää olla vähintään {MIN_PASSWORD_LENGTH} merkkiä.")
    if len(password) > 256:
        raise ValueError("Salasana on liian pitkä.")


def _derive(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        maxmem=SCRYPT_MAXMEM,
        dklen=32,
    )


def create_user(project_root: Optional[Path], username: str, password: str, *, replace: bool = False) -> Dict[str, Any]:
    username = validate_username(username)
    validate_password(password)
    path = auth_path(project_root)
    with _LOCK:
        if path.exists() and not replace:
            return {"ok": False, "message": "Käyttäjä on jo määritetty. Käytä --replace vain paikallisessa palautustilanteessa."}
        salt = secrets.token_bytes(16)
        digest = _derive(password, salt)
        payload = {
            "version": 1,
            "username": username,
            "password_hash": digest.hex(),
            "salt": salt.hex(),
            "algorithm": "scrypt",
            "parameters": {"n": SCRYPT_N, "r": SCRYPT_R, "p": SCRYPT_P, "dklen": 32},
            "created_at": _now_iso(),
        }
        _write_private_json(path, payload)
        _write_private_json(sessions_path(project_root), {"version": 1, "sessions": []})
    return {"ok": True, "username": username, "path": str(path)}


def auth_configured(project_root: Optional[Path] = None) -> bool:
    data = _read_json(auth_path(project_root), {})
    return bool(data.get("username") and data.get("password_hash") and data.get("salt"))


def _failure_key(client_ip: str, username: str) -> str:
    return f"{client_ip}|{username.lower()}"


def login_retry_after(client_ip: str, username: str) -> int:
    key = _failure_key(client_ip, username)
    now = time.time()
    with _LOCK:
        recent = [stamp for stamp in _FAILURES.get(key, []) if now - stamp < FAILED_ATTEMPT_WINDOW_SECONDS]
        _FAILURES[key] = recent
    if len(recent) < MAX_FAILED_ATTEMPTS:
        return 0
    return max(1, int(FAILED_ATTEMPT_WINDOW_SECONDS - (now - recent[0])))


def verify_credentials(project_root: Optional[Path], username: str, password: str, client_ip: str = "unknown") -> Dict[str, Any]:
    retry_after = login_retry_after(client_ip, username)
    if retry_after:
        return {"ok": False, "rate_limited": True, "retry_after": retry_after}
    data = _read_json(auth_path(project_root), {})
    valid = False
    try:
        salt = bytes.fromhex(str(data.get("salt", "")))
        expected = bytes.fromhex(str(data.get("password_hash", "")))
        supplied = _derive(password, salt)
        valid = hmac.compare_digest(str(username), str(data.get("username", ""))) and hmac.compare_digest(supplied, expected)
    except Exception:
        valid = False
    key = _failure_key(client_ip, username)
    with _LOCK:
        if valid:
            _FAILURES.pop(key, None)
        else:
            _FAILURES.setdefault(key, []).append(time.time())
    return {"ok": valid, "rate_limited": False}


def _load_sessions(project_root: Optional[Path]) -> Dict[str, Any]:
    data = _read_json(sessions_path(project_root), {"version": 1, "sessions": []})
    if not isinstance(data.get("sessions"), list):
        data["sessions"] = []
    return data


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def create_session(project_root: Optional[Path], username: str, client_ip: str, user_agent: str) -> Dict[str, Any]:
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(24)
    now = int(time.time())
    entry = {
        "token_hash": _token_hash(token),
        "csrf": csrf,
        "username": username,
        "created_at": now,
        "expires_at": now + SESSION_TTL_SECONDS,
        "client_ip_hash": hashlib.sha256(client_ip.encode("utf-8")).hexdigest()[:16],
        "user_agent_hash": hashlib.sha256(user_agent.encode("utf-8")).hexdigest()[:16],
    }
    with _LOCK:
        data = _load_sessions(project_root)
        data["sessions"] = [item for item in data["sessions"] if int(item.get("expires_at", 0)) > now]
        data["sessions"].append(entry)
        _write_private_json(sessions_path(project_root), data)
    return {"token": token, "csrf": csrf, "username": username, "expires_at": entry["expires_at"]}


def get_session(project_root: Optional[Path], token: str) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    wanted = _token_hash(token)
    now = int(time.time())
    changed = False
    found = None
    with _LOCK:
        data = _load_sessions(project_root)
        active = []
        for item in data["sessions"]:
            if int(item.get("expires_at", 0)) <= now:
                changed = True
                continue
            active.append(item)
            if hmac.compare_digest(str(item.get("token_hash", "")), wanted):
                found = dict(item)
        if changed:
            data["sessions"] = active
            _write_private_json(sessions_path(project_root), data)
    return found


def revoke_session(project_root: Optional[Path], token: str) -> bool:
    if not token:
        return False
    wanted = _token_hash(token)
    with _LOCK:
        data = _load_sessions(project_root)
        before = len(data["sessions"])
        data["sessions"] = [item for item in data["sessions"] if not hmac.compare_digest(str(item.get("token_hash", "")), wanted)]
        changed = len(data["sessions"]) != before
        if changed:
            _write_private_json(sessions_path(project_root), data)
    return changed


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Luo Säde v1:n paikallinen kirjautumiskäyttäjä.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create-user")
    create.add_argument("username")
    create.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    password = getpass.getpass("Uusi salasana (vähintään 12 merkkiä): ")
    confirmation = getpass.getpass("Salasana uudelleen: ")
    if password != confirmation:
        print("Salasanat eivät täsmää.")
        return 1
    try:
        result = create_user(None, args.username, password, replace=args.replace)
    except ValueError as error:
        print(error)
        return 1
    print(result.get("message") or f"Käyttäjä {result['username']} luotu turvallisesti.")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
