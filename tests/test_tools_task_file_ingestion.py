from __future__ import annotations

from pathlib import Path

import pytest

from app import file_ingestion, task_queue, tools


def test_tools_file_lifecycle_and_safety_boundaries(tmp_path: Path) -> None:
    project = tmp_path

    status = tools.get_tools_status(project)
    available = tools.list_available_tools()

    assert status["ok"] is True
    assert "read_file" in status["tools"]
    assert available["ok"] is True

    written = tools.write_file(project, "docs/note.md", "# Otsikko\n\nHei Säde")
    assert written["relative_path"] == "docs/note.md"

    listed = tools.list_files(project, "docs")
    assert listed["count"] == 1
    assert listed["items"][0]["name"] == "note.md"

    read = tools.read_file(project, "docs/note.md", max_chars=8)
    assert read["truncated"] is True
    assert read["content"] == "# Otsikk"

    appended = tools.append_file(project, "docs/note.md", "\nLisärivi")
    assert appended["ok"] is True
    assert "Lisärivi" in tools.read_file(project, "docs/note.md")["content"]

    overwritten = tools.write_file(project, "docs/note.md", "uusi", overwrite=True)
    assert overwritten["ok"] is True
    assert tools.read_file(project, "docs/note.md")["content"] == "uusi"

    with pytest.raises(tools.ToolError):
        tools.write_file(project, "../escape.md", "ei")
    with pytest.raises(tools.ToolError):
        tools.write_file(project, ".git/config", "ei")
    with pytest.raises(tools.ToolError):
        tools.write_file(project, "image.exe", "ei")
    with pytest.raises(tools.ToolError):
        tools.write_file(project, "docs/note.md", "ei", overwrite=False)


def test_tools_project_status_and_file_listing_filters_hidden_and_blocked(tmp_path: Path) -> None:
    project = tmp_path
    (project / "memory").mkdir()
    (project / "memory" / "sade_memory.md").write_text("muisti", encoding="utf-8")
    (project / ".hidden").write_text("hidden", encoding="utf-8")
    (project / "node_modules").mkdir()
    (project / "visible.txt").write_text("visible", encoding="utf-8")

    listed = tools.list_files(project)
    names = {item["name"] for item in listed["items"]}
    project_status = tools.project_status(project)

    assert "visible.txt" in names
    assert ".hidden" not in names
    assert "node_modules" not in names
    assert project_status["paths"]["memory"]["type"] == "directory"
    assert project_status["paths"]["sade_memory"]["exists"] is True


def test_task_queue_lifecycle_success_failure_cancel_and_history(tmp_path: Path) -> None:
    project = tmp_path

    empty = task_queue.add_task(project, "   ")
    first = task_queue.add_task(project, "onnistuva tehtävä", title="Onnistuu", priority=5)
    second = task_queue.add_task(project, "epäonnistuva tehtävä", title="Epäonnistuu", priority=1)
    third = task_queue.add_task(project, "peruttava tehtävä", title="Peru", priority=3)

    assert empty["ok"] is False
    assert first["ok"] is True
    assert task_queue.get_task_queue_status(project)["counts"]["queued"] == 3

    cancelled = task_queue.cancel_task(project, third["task"]["id"])
    assert cancelled["ok"] is True
    assert cancelled["task"]["status"] == "cancelled"

    run_first = task_queue.run_next_task(project, lambda prompt: {"ok": True, "reply": prompt})
    run_second = task_queue.run_task_by_id(
        project,
        second["task"]["id"],
        lambda prompt: {"ok": False, "error": "boom", "text": "x" * 1200},
    )
    missing = task_queue.run_task_by_id(project, "missing", lambda prompt: {"ok": True})
    cannot_cancel_done = task_queue.cancel_task(project, first["task"]["id"])

    assert run_first["ok"] is True
    assert run_first["task"]["status"] == "done"
    assert run_second["ok"] is False
    assert run_second["task"]["status"] == "failed"
    assert "boom" in run_second["task"]["error"]
    assert missing["ok"] is False
    assert cannot_cancel_done["ok"] is False

    done = task_queue.list_tasks(project, status="done")
    all_tasks = task_queue.list_tasks(project, limit=10)
    history = task_queue.read_task_history(project, limit=20)

    assert done["count"] == 1
    assert all_tasks["count"] == 3
    assert history["count"] >= 6
    assert any(item["event"] == "task_failed" for item in history["items"])


def test_task_queue_executor_exception_is_captured(tmp_path: Path) -> None:
    task = task_queue.add_task(tmp_path, "räjähtävä tehtävä")

    def explode(prompt: str) -> dict:
        raise RuntimeError(f"virhe: {prompt}")

    result = task_queue.run_task_by_id(tmp_path, task["task"]["id"], explode)

    assert result["ok"] is False
    assert result["task"]["status"] == "failed"
    assert "virhe" in result["error"]


def test_file_ingestion_summary_ingest_and_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path
    source = project / "uploads" / "notes.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "# Säde notes\n\n"
        "Ensimmäinen kappale kertoo projektista.\n\n"
        "- muisti\n"
        "- audit\n\n"
        "def example():\n"
        "    return 'ok'\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        file_ingestion,
        "add_text_to_semantic_memory",
        lambda *args, **kwargs: {"ok": True, "indexed": True, "chunks": 2},
    )

    summary = file_ingestion.summarize_file(project, "uploads/notes.md")
    ingested = file_ingestion.ingest_file(
        project,
        "uploads/notes.md",
        add_to_memory=True,
        add_to_semantic=True,
        title="Notes",
        tags=["portfolio"],
    )
    log = file_ingestion.read_ingestion_log(project)

    assert summary["ok"] is True
    assert summary["summary"]["stats"]["headings"] == 1
    assert summary["summary"]["stats"]["bullets"] == 2
    assert summary["summary"]["stats"]["code_like_lines"] >= 1
    assert ingested["ok"] is True
    assert ingested["memory"]["ok"] is True
    assert ingested["semantic_memory"]["chunks"] == 2
    assert log["count"] == 1
    assert log["items"][0]["relative_path"] == "uploads/notes.md"
    assert "Notes" in (project / "memory" / "sade_memory.md").read_text(encoding="utf-8")


def test_file_ingestion_rejects_unsafe_or_missing_files(tmp_path: Path) -> None:
    project = tmp_path
    (project / "uploads").mkdir()
    (project / "uploads" / "binary.exe").write_text("nope", encoding="utf-8")

    with pytest.raises(tools.ToolError):
        file_ingestion.summarize_file(project, "uploads/missing.md")
    with pytest.raises(tools.ToolError):
        file_ingestion.summarize_file(project, "uploads/binary.exe")
    with pytest.raises(tools.ToolError):
        file_ingestion.summarize_file(project, "../outside.md")


def test_file_ingestion_truncates_and_handles_parse_errors(tmp_path: Path) -> None:
    project = tmp_path
    path = project / "big.txt"
    path.write_text("abcdef", encoding="utf-8")

    summarized = file_ingestion.summarize_file(project, "big.txt", max_chars=3)
    log_path = project / "memory" / "ingested_files.jsonl"
    log_path.parent.mkdir(parents=True)
    log_path.write_text('{"ok": true}\nnot-json\n', encoding="utf-8")
    log = file_ingestion.read_ingestion_log(project, limit=5)

    assert summarized["file"]["truncated"] is True
    assert summarized["summary"]["stats"]["chars"] == 3
    assert log["items"][0]["ok"] is True
    assert log["items"][1]["ok"] is False
