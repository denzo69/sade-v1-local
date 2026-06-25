from pathlib import Path

from app.language_pack import (
    build_language_context,
    inspect_text,
    language_status,
    preferred_term,
    requested_language,
)
from app import main


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_finnish_is_default_and_english_requires_explicit_request() -> None:
    assert requested_language("Miten audit log toimii?") == "fi"
    assert requested_language("Vastaa englanniksi, kiitos") == "en"
    assert "suomella" in build_language_context("Kerro tilasi")
    assert build_language_context("Answer in English").startswith("LANGUAGE: English")


def test_project_terminology_and_technical_forms_are_protected() -> None:
    context = build_language_context("Miten tool router toimii?")

    assert preferred_term("audit log") == "audit-loki"
    assert "tool_router" in context
    assert "tiedostopolut" in context
    assert "keksi" in context.lower()


def test_text_inspection_detects_mojibake() -> None:
    assert inspect_text("Säde käyttää FastAPIa ja JSONL-lokia.")["ok"] is True
    assert inspect_text("S\uFFFDde")["ok"] is False


def test_language_pack_is_integrated_into_main_prompt(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_system_prompt", lambda: "SYSTEM")
    monkeypatch.setattr(main, "get_rag_context", lambda _query: "RAG")
    monkeypatch.setattr(main, "get_memory_context", lambda: "MEMORY")
    monkeypatch.setattr(main, "get_chat_context", lambda: "CHAT")

    prompt = main.build_sade_prompt("Kerro lyhyesti nykytilasi")

    assert "Suomen kielen vastausohje" in prompt
    assert "suomella" in prompt
    assert language_status(PROJECT_ROOT)["policy_exists"] is True


def test_ui_is_finnish_and_has_no_encoding_damage() -> None:
    ui = (Path(__file__).parents[1] / "app" / "templates" / "ui.html").read_text(encoding="utf-8")
    nav = ui.split('<nav class="nav-tabs"', 1)[1].split("</nav>", 1)[0]

    assert '<html lang="fi">' in ui
    assert all(label in ui for label in ("Keskustelu", "Muisti", "Aineistot", "Asetukset", "kehittäjätyökalut"))
    assert "Tehtävät" not in nav
    assert "Kehittäjä" not in nav
    assert inspect_text(ui)["ok"] is True
