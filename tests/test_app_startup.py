from app.main import UI_TEMPLATE_PATH, app, health


def test_health_function_starts() -> None:
    payload = health()

    assert payload["ok"] is True
    assert payload["status"] == "running"


def test_ui_and_core_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/ui" in paths
    assert "/chat" in paths
    assert "/files/upload" in paths
    assert "/tools/router/run" in paths
    assert "/audit/status" in paths
    assert "/audit/log" in paths
    assert "/language/status" in paths
    assert "/web-search/status" in paths
    assert "/login" in paths
    assert "/auth/login" in paths
    assert "/auth/logout" in paths
    assert "/auth/status" in paths
    assert "/tools/policies" in paths
    assert "/rag/quality" in paths
    assert "/debug/trace" in paths
    assert "/evals/static" in paths
    assert "/evals/live" in paths
    assert "/security/prompt-injection/analyze" in paths
    assert "/memory/entries" in paths
    assert "/memory/export" in paths
    assert "/memory/delete-entry" in paths
    assert "/backup/list" in paths
    assert "/backup/archive" in paths
    assert "/backup/restore" in paths
    assert "/model/status" in paths


def test_ui_uses_simplified_user_navigation() -> None:
    html = UI_TEMPLATE_PATH.read_text(encoding="utf-8")
    nav = html.split('<nav class="nav-tabs"', 1)[1].split("</nav>", 1)[0]

    assert 'class="tab-panel active" id="panel-chat"' in html
    assert 'data-tab="memory"' in html
    assert 'data-tab="files"' in html
    assert 'data-tab="settings"' in html
    assert 'data-tab="development"' not in html
    assert 'data-tab="tasks"' not in html
    assert 'id="panel-tasks"' not in html
    assert "Aineistot" in nav
    assert "Asetukset" in nav
    assert "Kehittäjä" not in nav
    assert "Edistynyt: tarkistus- ja kehittäjätyökalut" in html
    assert "Lisää muistettava asia" in html
    assert "Näytä mitä Säde muistaa" in html
    assert "Opeta Sädeä tiedostolla" in html
    assert "Lähteistä haku" in html
    assert "const I18N" in html
    assert "Interface language" in html
    assert 'id="configLanguage"' in html
    assert "Muisti ladataan pyynnöstä." in html
    assert "Enter lähettää · Shift+Enter vaihtaa riviä" in html
    assert "sade-task-section" in html
    assert '"sade-task-section", "sade-dev-section"' in html


def test_ui_has_mobile_viewport_and_compact_chat_layout() -> None:
    html = UI_TEMPLATE_PATH.read_text(encoding="utf-8")

    assert 'name="viewport"' in html
    assert "width=device-width, initial-scale=1" in html
    assert "max-width: 1480px" in html
    assert "height: calc(100dvh - 178px)" in html
    assert "#panel-chat" in html
    assert "height: clamp(250px, 44dvh, 430px)" in html
    assert ".chat-composer .actions #sendChatButton" in html
    assert "__SADE_CSRF_TOKEN__" in html
    assert "Kirjaudu ulos" in html
    assert "loadMemoryEntries()" in html
    assert "exportMemoryJson()" in html
    assert "createBackupArchive()" in html
    assert "runStaticEvals()" in html
    assert "runLiveEvals()" in html
    assert "Edistynyt: Säteen ydinprompti" in html
    assert "Kielipaketin tekninen tila" in html
