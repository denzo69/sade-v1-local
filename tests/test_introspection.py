from __future__ import annotations

from pathlib import Path

from app.introspection import build_introspection_report


def write(path: Path, content: str = "test") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_introspection_separates_existing_and_missing_files(tmp_path: Path) -> None:
    project = tmp_path / "Sade-v1"

    write(project / "docs" / "project_inventory.md", "# Project Inventory")
    write(project / "uploads" / "memory_policy.md", "# Memory Policy fallback")
    write(project / "app" / "main.py", "from app.introspection import build_introspection_report\n")
    write(project / "app" / "introspection.py", "# placeholder")

    report = build_introspection_report(project)

    docs = {item["id"]: item for item in report["documents"]}
    modules = {item["id"]: item for item in report["modules"]}

    assert docs["project_inventory"]["status"] == "active"
    assert docs["memory_policy"]["status"] == "fallback_active"
    assert docs["self_model_policy"]["status"] == "missing"

    assert modules["introspection"]["status"] in {"created", "implemented_candidate"}
    assert modules["memory_cleaner"]["status"] == "missing"


def test_introspection_does_not_mark_created_module_as_tested(tmp_path: Path) -> None:
    project = tmp_path / "Sade-v1"

    write(project / "app" / "introspection.py", "# exists but not tested")
    write(project / "app" / "main.py", "# no integration")

    report = build_introspection_report(project)
    modules = {item["id"]: item for item in report["modules"]}

    assert modules["introspection"]["status"] == "created"
    assert modules["introspection"]["status"] != "tested"


def test_introspection_reports_real_test_inventory_and_current_ui(tmp_path: Path) -> None:
    project = tmp_path / "Sade-v1"
    write(project / "app" / "audit_log.py", "def write_audit_event():\n    pass\n")
    write(
        project / "tests" / "test_audit_log.py",
        "from app.audit_log import write_audit_event\n\ndef test_audit_chain():\n    assert write_audit_event\n",
    )
    write(
        project / "app" / "templates" / "ui.html",
        '<html lang="fi"><button data-tab="chat"></button><button data-tab="memory"></button>'
        '<section class="tab-panel active" id="panel-chat"></section>Muisti ladataan pyynnöstä.</html>',
    )

    report = build_introspection_report(project)
    modules = {item["id"]: item for item in report["modules"]}

    assert report["test_status"]["discovered_test_count"] == 1
    assert report["test_status"]["last_run_status"] == "not_executed_by_introspection"
    assert report["ui_status"]["language"] == "fi"
    assert report["ui_status"]["chat_first"] is True
    assert report["ui_status"]["lazy_memory"] is True
    assert modules["audit_log"]["status"] == "tested_candidate"
    assert not (project / "app" / "memory").exists()
