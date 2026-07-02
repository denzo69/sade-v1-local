from __future__ import annotations

from pathlib import Path

from app.persona_layer import _clean_next_steps, _status_emoji, build_persona_frame, render_introspection_reply
from app.introspection import build_introspection_report
from app.tool_router import _format_omatila_reply, route_tool_request


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_tested_candidate_has_distinct_status_icon() -> None:
    assert _status_emoji("tested_candidate") == "🧪"


def test_next_steps_remove_stale_and_duplicate_recommendations() -> None:
    steps = _clean_next_steps([
        "Lisää tai päivitä automaattiset testit omatila-ketjulle ja aja pytest.",
        "Pidä memory_cleaner.py puuttuvana, kunnes se testataan.",
        "Pidä memory_cleaner.py suunniteltuna, kunnes se testataan.",
        "Seuraava suositeltu turvakerros on audit_log v1 ennen automaatioita.",
        "Lisää Learning Feedback Memory v1.",
    ])

    assert steps == [
        "Pidä memory_cleaner.py puuttuvana, kunnes se testataan.",
        "Lisää Learning Feedback Memory v1.",
    ]


def test_omatila_reply_matches_current_project_state() -> None:
    report = build_introspection_report(PROJECT_ROOT)
    reply = render_introspection_reply(report, build_persona_frame(PROJECT_ROOT))

    assert "🧪 **audit_log** — `tested_candidate`" in reply
    assert "Seuraava suositeltu turvakerros on audit_log v1" not in reply
    assert "Lisää tai päivitä automaattiset testit omatila-ketjulle" not in reply
    assert "🧪 **memory_cleaner** — `tested_candidate`" in reply
    assert "🧪 **learning_feedback** — `tested_candidate`" in reply
    assert reply.count("**persona_layer**") == 1


def test_tool_router_omatila_uses_clean_persona_report() -> None:
    result = route_tool_request(PROJECT_ROOT / "app", "omatila")

    assert result["handled"] is True
    assert result["tool"] == "introspection"
    assert "# Self-State" in result["reply"]
    assert "Truth boundary" in result["reply"]
    assert "Seuraava suositeltu turvakerros on audit_log v1" not in result["reply"]


def test_tool_router_self_state_fallback_formats_missing_items() -> None:
    reply = _format_omatila_reply({
        "project_root": "masked-root",
        "documents": [
            {"id": "project_inventory", "status": "active", "active_path": "docs/project_inventory.md"},
            {"id": "missing_policy", "status": "missing", "note": "not found"},
        ],
        "modules": [
            {"id": "main", "status": "implemented_candidate", "note": "available", "referenced_by": ["README"]},
            {"id": "source_reader", "status": "missing", "note": "planned"},
        ],
        "verified_capabilities": ["read_only_project_status_report"],
        "limitations": ["No writes are performed."],
        "next_steps": ["Add health dashboard."],
    })

    assert "# Self-State — Local AI Workspace" in reply
    assert "Active or fallback-discovered documents: 1 / 2" in reply
    assert "Missing documents:" in reply
    assert "`source_reader` — missing" in reply
    assert "References: README." in reply
    assert "Missing modules are not presented as implemented" in reply
