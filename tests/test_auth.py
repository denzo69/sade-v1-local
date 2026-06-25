from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main
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
