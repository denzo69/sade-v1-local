from pathlib import Path


def test_high_risk_mutations_have_attempt_and_outcome_audits() -> None:
    source = (Path(__file__).parents[1] / "app" / "main.py").read_text(encoding="utf-8")
    for action in ("write_file", "append_file", "rebuild_semantic_index", "update_system_prompt", "create_export", "create_backup", "run_next", "cancel"):
        assert f'action="{action}", outcome="attempt"' in source
        assert f'action="{action}", outcome="success"' in source or f'action="{action}", outcome="success" if' in source
