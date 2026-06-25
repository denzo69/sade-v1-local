from __future__ import annotations

from pathlib import Path


def test_coverage_omits_legacy_helper_scripts() -> None:
    coveragerc = Path(".coveragerc").read_text(encoding="utf-8")
    required_patterns = [
        "app/add_*.py",
        "app/patch_*.py",
        "app/fix_*.py",
        "app/*backup*.py",
        "app/mainOLD*.py",
    ]

    for pattern in required_patterns:
        assert pattern in coveragerc


def test_coverage_reports_are_written_to_reports_directory() -> None:
    coveragerc = Path(".coveragerc").read_text(encoding="utf-8")

    assert "directory = reports/htmlcov" in coveragerc
    assert "output = reports/coverage.xml" in coveragerc
