from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


REQUIRED_FILES = [
    "README.md",
    "QUICKSTART.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".env.example",
    ".gitignore",
    "requirements.txt",
    "pytest.ini",
    ".github/workflows/tests.yml",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    "docs/repo_cleanup_plan.md",
    "docs/architecture.md",
    "docs/code_rewrite_protocol.md",
    ".coveragerc",
    "VERSION",
    "CHANGELOG.md",
    "LICENSE",
    "docs/ai_evaluation_policy.md",
    "docs/tool_risk_policy.md",
    "docs/backup_restore_policy.md",
    "docs/memory_governance_policy.md",
    "docs/model_provider_policy.md",
]


SENSITIVE_PATTERNS = [
    "app/memory/auth.json",
    "app/memory/auth_sessions.json",
    "app/memory/vector_db",
    "app/memory/backups",
    "app/memory/exports",
]


def run(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return completed.returncode, (completed.stdout + completed.stderr).strip()


def main() -> int:
    files = {path: (ROOT / path).exists() for path in REQUIRED_FILES}
    git_code, git_output = run(["git", "status", "--short"])
    tracked_code, tracked_output = run(["git", "ls-files"])
    sensitive_seen = [
        pattern for pattern in SENSITIVE_PATTERNS
        if pattern.replace("/", "\\") in tracked_output or pattern in tracked_output
    ]
    pytest_code, pytest_output = run([str(ROOT / ".venv" / "Scripts" / "python.exe"), "-m", "pytest", "-q"])
    report = {
        "ok": all(files.values()) and pytest_code == 0 and not sensitive_seen,
        "required_files": files,
        "pytest_ok": pytest_code == 0,
        "pytest_tail": pytest_output.splitlines()[-5:],
        "git_status_is_clean": git_output == "",
        "sensitive_paths_still_tracked": sensitive_seen,
        "notes": [
            "Git-statuksen ei tarvitse olla puhdas kehityksen aikana, mutta julkaisua varten sen pitäisi olla hallittu.",
            "Jos sensitive_paths_still_tracked ei ole tyhjä, älä julkaise ennen siivousta.",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
