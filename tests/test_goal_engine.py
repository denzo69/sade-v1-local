from pathlib import Path
from app.goal_engine import build_goal_status, collect_components


def _touch(root: Path, relative: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("test", encoding="utf-8")


def test_goal_engine_is_read_only_and_prioritizes_missing_feedback(tmp_path: Path) -> None:
    _touch(tmp_path, "app/web_search.py")
    before = sorted(str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*"))
    status = build_goal_status(tmp_path)
    after = sorted(str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*"))
    assert status["mode"] == "read_only_goal_status"
    assert status["recommendation"]["id"] == "learning_feedback_memory_v1"
    assert before == after


def test_goal_engine_detects_new_modules(tmp_path: Path) -> None:
    _touch(tmp_path, "app/learning_feedback.py")
    _touch(tmp_path, "app/memory_cleaner.py")
    components = {item.id: item for item in collect_components(tmp_path)}
    assert components["learning_feedback"].status == "implemented_candidate"
    assert components["memory_cleaner"].status == "implemented_candidate"


def test_goal_engine_reports_dedicated_tests(tmp_path: Path) -> None:
    _touch(tmp_path, "app/goal_engine.py")
    _touch(tmp_path, "tests/test_goal_engine.py")
    components = {item.id: item for item in collect_components(tmp_path)}
    assert components["goal_engine"].status == "tested_candidate"
