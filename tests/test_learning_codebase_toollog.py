from __future__ import annotations

from pathlib import Path
import textwrap

import pytest

from app import codebase_map, learning_review, tool_log


def test_tool_log_preview_read_parse_error_and_clear(tmp_path: Path) -> None:
    long_text = "x" * 1500
    preview = tool_log._safe_preview(
        {
            "content": long_text,
            "items": [{"reply": long_text}],
            "plain": long_text,
        }
    )

    assert "katkaistu" in preview["content"]
    assert "katkaistu" in preview["items"][0]["reply"]
    assert "katkaistu" in preview["plain"]

    first = tool_log.log_tool_event(
        tmp_path,
        tool="read_file",
        action="api",
        request={"relative_path": "docs/readme.md"},
        result={"ok": True, "content": long_text},
    )
    second = tool_log.log_tool_event(
        tmp_path,
        tool="write_file",
        action="api",
        ok=False,
        error="denied",
    )
    path = Path(first["path"])
    with path.open("a", encoding="utf-8") as file:
        file.write("not-json\n")

    read = tool_log.read_tool_log(tmp_path, limit=10)
    cleared = tool_log.clear_tool_log(tmp_path)
    empty = tool_log.read_tool_log(tmp_path)

    assert first["ok"] is True
    assert second["ok"] is True
    assert read["count"] == 3
    assert read["items"][0]["tool"] == "read_file"
    assert read["items"][1]["ok"] is False
    assert read["items"][2]["action"] == "parse_error"
    assert cleared["ok"] is True
    assert empty["count"] == 0


def test_learning_review_helpers_extract_terms_relevance_and_tasks(tmp_path: Path) -> None:
    text = textwrap.dedent("""
    # FastAPI RAG Notes

    - RAG improves retrieval for semantic memory.
    - Tool router requires guardrails and approval flow.

    FastAPI and Python are used in this project. FastAPI creates API routes.
    Semantic memory, embeddings and ChromaDB help source-aware answers.
    """)

    headings = learning_review._headings(text)
    bullets = learning_review._bullet_points(text)
    terms = learning_review._extract_terms(text)
    points = learning_review._main_learning_points(text)
    relevance = learning_review._project_relevance(terms, "uploads/fastapi_rag.md")
    tasks = learning_review._future_tasks(terms, "uploads/fastapi_rag.md")
    remember = learning_review._remember_later(points, terms)

    assert headings == ["FastAPI RAG Notes"]
    assert len(bullets) == 2
    assert "rag" in terms
    assert "fastapi" in terms
    assert points
    assert any("backend" in item.lower() or "api" in item.lower() for item in relevance)
    assert any("rag" in item.lower() for item in tasks)
    assert remember
    assert learning_review._sha256("abc") == learning_review._sha256("abc")


def test_learning_review_create_read_status_and_duplicate_detection(tmp_path: Path) -> None:
    upload = tmp_path / "uploads" / "fastapi_rag.md"
    upload.parent.mkdir(parents=True)
    upload.write_text(
        "# FastAPI RAG\n\n"
        "- RAG improves retrieval.\n"
        "- Semantic memory stores embeddings.\n\n"
        "FastAPI and Python are important for the API layer. "
        "Guardrails and approval flow keep tool use safe.",
        encoding="utf-8",
    )

    created = learning_review.create_learning_review_for_file(tmp_path, "uploads/fastapi_rag.md")
    duplicate = learning_review.create_learning_review_for_file(tmp_path, "uploads/fastapi_rag.md")
    forced = learning_review.create_learning_review_for_file(tmp_path, "uploads/fastapi_rag.md", force=True)
    reviews = learning_review.read_learning_reviews(tmp_path)
    status = learning_review.get_learning_review_status(tmp_path)

    assert created["ok"] is True
    assert created["already_exists"] is False
    assert duplicate["already_exists"] is True
    assert forced["already_exists"] is False
    assert reviews["total"] == 2
    assert status["reviews_count"] == 2
    assert "RAG" in created["review"]["markdown"]


def test_learning_review_recent_candidates_from_log_and_uploads(tmp_path: Path) -> None:
    first = tmp_path / "uploads" / "first.md"
    second = tmp_path / "uploads" / "second.md"
    blocked = tmp_path / "uploads" / "old_backup_file.md"
    first.parent.mkdir(parents=True)
    first.write_text("# First\n\nFastAPI API memory.", encoding="utf-8")
    second.write_text("# Second\n\nRAG semantic memory.", encoding="utf-8")
    blocked.write_text("skip", encoding="utf-8")

    log_path = tmp_path / "memory" / "autonomous_learning_log.jsonl"
    log_path.parent.mkdir(parents=True)
    log_path.write_text(
        '{"event": "file_learned", "relative_path": "uploads/second.md"}\n'
        'not-json\n'
        '{"event": "ignored", "relative_path": "uploads/first.md"}\n',
        encoding="utf-8",
    )

    from_log = learning_review._candidate_paths_from_learning_log(tmp_path)
    recent = learning_review.create_reviews_for_recent_learning(tmp_path, max_files=5)

    log_path.unlink()
    from_uploads = learning_review._candidate_paths_from_learning_log(tmp_path)

    assert from_log == ["uploads/second.md"]
    assert recent["created_count"] == 1
    assert from_uploads == ["uploads/first.md", "uploads/second.md"]


def test_learning_review_rejects_unsafe_files(tmp_path: Path) -> None:
    (tmp_path / "uploads").mkdir()
    (tmp_path / "uploads" / "binary.exe").write_text("no", encoding="utf-8")
    (tmp_path / "uploads" / "folder").mkdir()

    with pytest.raises(FileNotFoundError):
        learning_review.create_learning_review_for_file(tmp_path, "uploads/missing.md")
    with pytest.raises(ValueError):
        learning_review.create_learning_review_for_file(tmp_path, "../escape.md")
    with pytest.raises(ValueError):
        learning_review.create_learning_review_for_file(tmp_path, "uploads/folder")
    with pytest.raises(ValueError):
        learning_review.create_learning_review_for_file(tmp_path, "uploads/binary.exe")


def test_codebase_map_analyzers_and_find(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "main.py").write_text(
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "class Service:\n"
        "    def run(self):\n"
        "        return 'ok'\n"
        "@app.get('/health')\n"
        "def health():\n"
        "    return {'ok': True}\n",
        encoding="utf-8",
    )
    (app_dir / "ui.html").write_text(
        "<div id='app'></div><script>function loadData(){ fetch('/health') }</script>",
        encoding="utf-8",
    )
    (app_dir / "config.json").write_text('{"model": "test"}', encoding="utf-8")
    (app_dir / "README.md").write_text("# Title\n\n[Link](https://example.com)", encoding="utf-8")
    (app_dir / "broken.py").write_text("def nope(:\n", encoding="utf-8")
    (app_dir / "memory").mkdir()
    (app_dir / "memory" / "chat_log.md").write_text("skip", encoding="utf-8")

    py_analysis = codebase_map._analyze_python((app_dir / "main.py").read_text(encoding="utf-8"))
    html_analysis = codebase_map._analyze_html((app_dir / "ui.html").read_text(encoding="utf-8"))
    json_analysis = codebase_map._analyze_json((app_dir / "config.json").read_text(encoding="utf-8"))
    md_analysis = codebase_map._analyze_markdown((app_dir / "README.md").read_text(encoding="utf-8"))
    broken = codebase_map.analyze_file(app_dir, app_dir / "broken.py")
    built = codebase_map.build_codebase_map(tmp_path, include_snippets=True)
    read = codebase_map.read_codebase_map(tmp_path)
    found = codebase_map.find_in_codebase_map(tmp_path, "health")
    empty = codebase_map.find_in_codebase_map(tmp_path, "   ")

    assert py_analysis["routes"][0]["path"] == "/health"
    assert "loadData" in html_analysis["functions"]
    assert json_analysis["top_level_keys"] == ["model"]
    assert md_analysis["headings"][0]["text"] == "Title"
    assert "syntax_error" in broken["analysis"]
    assert built["ok"] is True
    assert built["route_count"] >= 1
    assert read["ok"] is True
    assert found["count"] >= 1
    assert empty["ok"] is False


def test_codebase_map_read_errors_and_safe_mapping(tmp_path: Path) -> None:
    missing = codebase_map.read_codebase_map(tmp_path)
    item_from_string = codebase_map._safe_mapping_item("hello", "file.py")
    item_from_dict = codebase_map._safe_mapping_item({"name": "fn"}, "file.py")

    app_dir = tmp_path / "app"
    memory = app_dir / "memory"
    memory.mkdir(parents=True)
    (memory / "codebase_map.json").write_text("not-json", encoding="utf-8")
    invalid = codebase_map.read_codebase_map(tmp_path)

    assert missing["ok"] is False
    assert item_from_string["name"] == "hello"
    assert item_from_string["file"] == "file.py"
    assert item_from_dict["file"] == "file.py"
    assert invalid["ok"] is False


def test_codebase_map_skip_and_large_file_helpers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    hidden = app_dir / ".cache" / "x.py"
    hidden.parent.mkdir()
    hidden.write_text("print('skip')", encoding="utf-8")
    backup = app_dir / "main_backup_2026.py"
    backup.write_text("print('backup')", encoding="utf-8")
    pyc = app_dir / "module.pyc"
    pyc.write_text("compiled", encoding="utf-8")
    memory_file = app_dir / "memory" / "chat_log.md"
    memory_file.parent.mkdir()
    memory_file.write_text("private chat", encoding="utf-8")
    outside = tmp_path / "outside.py"
    outside.write_text("print('outside')", encoding="utf-8")

    monkeypatch.setattr(codebase_map, "MAX_READ_CHARS", 10)
    large = app_dir / "large.txt"
    large.write_text("x" * 50, encoding="utf-8")

    assert codebase_map._should_skip(hidden, app_dir) is True
    assert codebase_map._should_skip(backup, app_dir) is True
    assert codebase_map._should_skip(pyc, app_dir) is True
    assert codebase_map._should_skip(memory_file, app_dir) is True
    assert codebase_map._should_skip(outside, app_dir) is True
    assert codebase_map._read_text(large) == "x" * 10


def test_codebase_map_build_limits_and_error_items(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "a.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    (app_dir / "b.py").write_text("def b():\n    return 2\n", encoding="utf-8")

    original_analyze = codebase_map.analyze_file
    def flaky_analyze(project_path: Path, path: Path, include_snippet: bool = False):
        if path.name == "b.py":
            raise RuntimeError("cannot read")
        return original_analyze(project_path, path, include_snippet=include_snippet)

    monkeypatch.setattr(codebase_map, "MAX_FILES", 5)
    monkeypatch.setattr(codebase_map, "analyze_file", flaky_analyze)

    built = codebase_map.build_codebase_map(tmp_path)

    assert built["ok"] is True
    assert built["file_count"] == 2
    assert any(item.get("error") == "cannot read" for item in built["files"])
