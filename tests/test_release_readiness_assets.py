from pathlib import Path

from app.live_evals import LIVE_EVAL_CASES
from app.main import load_config


ROOT = Path(__file__).resolve().parent.parent


def test_release_readiness_files_exist() -> None:
    required = [
        "README.md",
        "QUICKSTART.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        ".env.example",
        ".github/workflows/tests.yml",
        "scripts/release_readiness.py",
    ]

    for relative in required:
        assert (ROOT / relative).exists(), relative


def test_readme_is_utf8_and_mentions_core_workflows() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Local AI Workspace" in text
    assert "pytest" in text
    assert "/evals/static" in text
    assert "/backup/archive" in text
    assert "authentication" in text.lower()


def test_env_overrides_config(monkeypatch) -> None:
    monkeypatch.setenv("SADE_OLLAMA_MODEL", "unit-test-model")
    monkeypatch.setenv("SADE_NUM_CTX", "4096")
    monkeypatch.setenv("SADE_UI_LANGUAGE", "en")

    config = load_config()

    assert config["ollama_model"] == "unit-test-model"
    assert config["num_ctx"] == 4096
    assert config["ui_language"] == "en"


def test_live_eval_cases_are_defined_without_running_model() -> None:
    assert len(LIVE_EVAL_CASES) >= 3
    assert all("prompt" in case for case in LIVE_EVAL_CASES)
    assert all("must_include_any" in case for case in LIVE_EVAL_CASES)
