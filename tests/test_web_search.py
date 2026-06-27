from __future__ import annotations

from pathlib import Path

from app.tool_router import route_tool_preview, route_tool_request
from app.web_search import format_web_search_reply, web_search_status


def _fake_search(_root: Path, query: str, max_results: int = 6):
    return {
        "ok": True,
        "query": query,
        "provider": "test",
        "results": [{"rank": 1, "title": "Testilähde", "url": "https://example.test", "source": "example.test", "snippet": ""}],
    }


def test_web_search_status_question_reports_real_capability(tmp_path: Path) -> None:
    result = route_tool_request(tmp_path, "Entä toimiiko haku netistä?")

    assert result["handled"] is True
    assert result["tool"] == "web_search_status"
    assert result["result"]["enabled"] is True
    assert result["result"]["direct_chat_integration"] is True
    assert result["result"]["rag_integration"] is False
    assert "Kyllä, verkkohaku on käytössä" in result["reply"]
    assert route_tool_preview("Voitko hakea verkosta?")["tool"] == "web_search_status"


def test_guided_web_search_consumes_next_message_as_query(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("app.web_search.web_search", _fake_search)

    start = route_tool_request(tmp_path, "Joo haluan kokeilla yksinkertaista hakua.")
    result = route_tool_request(tmp_path, "viimeisimmät tutkimustulokset tekoälyn etiikasta")

    assert start["tool"] == "web_search_pending"
    assert result["tool"] == "web_search"
    assert result["result"]["query"] == "viimeisimmät tutkimustulokset tekoälyn etiikasta"
    assert "https://example.test" in result["reply"]
    assert not (tmp_path / "app" / "memory" / "web_search_state.json").exists()


def test_plain_message_is_not_web_search_without_pending_state(tmp_path: Path) -> None:
    result = route_tool_request(tmp_path, "viimeisimmät tutkimustulokset tekoälyn etiikasta")

    assert result["handled"] is False


def test_explicit_web_search_still_works(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("app.web_search.web_search", _fake_search)
    result = route_tool_request(tmp_path, "hae verkosta tekoälyn etiikka 2026")

    assert result["tool"] == "web_search"
    assert result["result"]["query"] == "tekoälyn etiikka 2026"
    assert [item["label"] for item in result["actions"]] == ["Tarkista lähteet", "Syvennä hakua"]


def test_source_review_uses_latest_successful_search(tmp_path: Path, monkeypatch) -> None:
    cache = tmp_path / "memory" / "web_search_cache"
    cache.mkdir(parents=True)
    (cache / "20260621_test.json").write_text(
        '{"ok": true, "query": "etiikka", "results": [{"title": "Lähde", "url": "https://example.test"}]}',
        encoding="utf-8",
    )
    monkeypatch.setattr("app.web_search.inspect_source", lambda url: {"ok": True, "url": url, "preview": "Tarkistettu ote"})

    result = route_tool_request(tmp_path, "Tarkista lähteet")

    assert result["tool"] == "web_source_review"
    assert result["result"]["verified_count"] == 1
    assert "Tarkistettu ote" in result["reply"]
    assert "Semanttiseen muistiin tallennusta ei tarjota" in result["reply"]


def test_search_reply_recommends_review_before_memory() -> None:
    reply = format_web_search_reply(_fake_search(Path("."), "etiikka"))

    assert "Tarkista lähteet" in reply
    assert "ei tallenneta faktatietona semanttiseen muistiin" in reply


def test_failed_search_never_claims_success() -> None:
    reply = format_web_search_reply({"ok": False, "query": "test", "provider": "test", "error": "offline"})

    assert "Verkkohaku ei onnistunut" in reply
    assert "En väitä tietoa haetuksi" in reply


def test_status_does_not_claim_unimplemented_integrations(tmp_path: Path) -> None:
    status = web_search_status(tmp_path)

    assert status["automatic_search"] is False
    assert status["rag_integration"] is False
    assert status["semantic_memory_integration"] is False
    assert status["goal_engine_integration"] is False


def test_page_check_request_routes_to_web_search(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("app.web_search.web_search", _fake_search)

    message = "Tarkasta Veikkauksen sivulta edellinen loton oikea numero"
    result = route_tool_request(tmp_path, message)

    assert result["handled"] is True
    assert result["tool"] == "web_search"
    assert result["result"]["query"] == "Veikkauksen sivulta edellinen loton oikea numero"
    assert route_tool_preview(message)["tool"] == "web_search"
