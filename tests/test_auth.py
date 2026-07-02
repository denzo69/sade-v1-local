from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main
from app import auth
from app.auth import (
    SESSION_COOKIE,
    auth_configured,
    create_user,
    get_session,
    verify_credentials,
)


pytestmark = pytest.mark.filterwarnings("ignore:Using `httpx` with `starlette.testclient` is deprecated:DeprecationWarning")


def test_password_is_hashed_and_credentials_are_verified(tmp_path: Path) -> None:
    result = create_user(tmp_path, "jani", "pitka-turvallinen-salasana")
    stored = (tmp_path / "app" / "memory" / "auth.json").read_text(encoding="utf-8")

    assert result["ok"] is True
    assert auth_configured(tmp_path) is True
    assert "pitka-turvallinen-salasana" not in stored
    assert verify_credentials(tmp_path, "jani", "pitka-turvallinen-salasana", "test-ip")["ok"] is True
    assert verify_credentials(tmp_path, "jani", "väärä-salasana", "other-ip")["ok"] is False


def test_routes_require_login_and_csrf(tmp_path: Path, monkeypatch) -> None:
    app_path = tmp_path / "app"
    app_path.mkdir(parents=True)
    monkeypatch.setattr(main, "PROJECT_PATH", app_path)
    create_user(tmp_path, "jani", "pitka-turvallinen-salasana")

    with TestClient(main.app) as client:
        denied = client.post("/chat", json={"message": "tee koodikartta"})
        login = client.post("/auth/login", json={"username": "jani", "password": "pitka-turvallinen-salasana"})
        status = client.get("/auth/status")
        ui = client.get("/ui")
        csrf_denied = client.post("/auth/logout")
        csrf = status.json()["csrf_token"]
        logout = client.post("/auth/logout", headers={"X-CSRF-Token": csrf})

    assert denied.status_code == 401
    assert login.status_code == 200
    assert SESSION_COOKIE in login.cookies
    assert status.json()["authenticated"] is True
    assert "__SADE_CSRF_TOKEN__" not in ui.text
    assert csrf in ui.text
    assert csrf_denied.status_code == 403
    assert logout.status_code == 200
    assert get_session(tmp_path, login.cookies.get(SESSION_COOKIE, "")) is None


def test_unconfigured_instance_exposes_only_setup_status(tmp_path: Path, monkeypatch) -> None:
    app_path = tmp_path / "app"
    app_path.mkdir(parents=True)
    monkeypatch.setattr(main, "PROJECT_PATH", app_path)

    with TestClient(main.app) as client:
        status = client.get("/auth/status")
        protected = client.get("/health")
        login_page = client.get("/login")

    assert status.status_code == 200
    assert status.json()["configured"] is False
    assert protected.status_code == 503
    assert login_page.status_code == 200


def test_auth_validation_invalid_json_and_replace(tmp_path: Path) -> None:
    auth_file = tmp_path / "app" / "memory" / "auth.json"
    auth_file.parent.mkdir(parents=True)
    auth_file.write_text("{not-json", encoding="utf-8")

    assert auth_configured(tmp_path) is False

    with pytest.raises(ValueError):
        auth.validate_username("no")
    with pytest.raises(ValueError):
        auth.validate_username("bad user!")
    with pytest.raises(ValueError):
        auth.validate_password("short")
    with pytest.raises(ValueError):
        auth.validate_password("x" * 300)

    created = create_user(tmp_path, "jani", "pitka-turvallinen-salasana", replace=True)
    duplicate = create_user(tmp_path, "jani", "pitka-turvallinen-salasana")

    assert created["ok"] is True
    assert duplicate["ok"] is False


def test_auth_rate_limit_session_expiry_and_revoke_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    auth._FAILURES.clear()
    create_user(tmp_path, "jani", "pitka-turvallinen-salasana")

    for _ in range(auth.MAX_FAILED_ATTEMPTS):
        assert verify_credentials(tmp_path, "jani", "wrong-password", "rate-ip")["ok"] is False

    limited = verify_credentials(tmp_path, "jani", "pitka-turvallinen-salasana", "rate-ip")
    assert limited["rate_limited"] is True
    assert limited["retry_after"] >= 1
    assert auth.revoke_session(tmp_path, "") is False

    session = auth.create_session(tmp_path, "jani", "127.0.0.1", "pytest")
    assert get_session(tmp_path, session["token"])["username"] == "jani"

    sessions = auth._load_sessions(tmp_path)
    sessions["sessions"][0]["expires_at"] = 1
    auth._write_private_json(auth.sessions_path(tmp_path), sessions)

    assert get_session(tmp_path, session["token"]) is None


def test_auth_cli_success_password_mismatch_and_validation_error(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(auth, "create_user", lambda project_root, username, password, replace=False: {"ok": True, "username": username})
    monkeypatch.setattr(auth.getpass, "getpass", lambda prompt: "pitka-turvallinen-salasana")
    monkeypatch.setattr("sys.argv", ["auth.py", "create-user", "jani"])
    assert auth._cli() == 0
    assert "jani" in capsys.readouterr().out

    prompts = iter(["pitka-turvallinen-salasana", "eri-salasana"])
    monkeypatch.setattr(auth.getpass, "getpass", lambda prompt: next(prompts))
    monkeypatch.setattr("sys.argv", ["auth.py", "create-user", "jani"])
    assert auth._cli() == 1
    assert "Salasanat" in capsys.readouterr().out

    def raise_validation(project_root, username, password, replace=False):
        raise ValueError("bad username")

    monkeypatch.setattr(auth, "create_user", raise_validation)
    monkeypatch.setattr(auth.getpass, "getpass", lambda prompt: "pitka-turvallinen-salasana")
    monkeypatch.setattr("sys.argv", ["auth.py", "create-user", "bad"])
    assert auth._cli() == 1
    assert "bad username" in capsys.readouterr().out
