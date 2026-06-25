from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent.parent

SENSITIVE_PATTERNS = [
    ("env_file", re.compile(r"(^|/)\.env$", re.I)),
    ("auth_file", re.compile(r"app/memory/auth(_sessions)?\.json$", re.I)),
    ("memory_jsonl", re.compile(r"app/memory/.*\.jsonl$", re.I)),
    ("chat_log", re.compile(r"app/memory/chat_log\.md$", re.I)),
    ("sade_memory", re.compile(r"app/memory/sade_memory\.md$", re.I)),
    ("api_key_literal", re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}", re.I)),
]

SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "reports",
    "archive",
    "app/memory",
    "app/uploads",
}

SKIP_DIR_PREFIXES = (
    ".venv_broken_",
)


def iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        parts = path.relative_to(ROOT).parts
        if any(part in SKIP_DIRS for part in parts):
            continue
        if any(part.startswith(SKIP_DIR_PREFIXES) for part in parts):
            continue
        if rel.startswith(("app/memory/", "app/uploads/")):
            continue
        yield path, rel


def main() -> int:
    findings = []
    for path, rel in iter_files():
        for name, pattern in SENSITIVE_PATTERNS[:5]:
            if pattern.search(rel):
                findings.append({"type": name, "path": rel})
        if path.suffix.lower() in {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".ini"}:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if SENSITIVE_PATTERNS[-1][1].search(text):
                findings.append({"type": "api_key_literal", "path": rel})

    if findings:
        print({"ok": False, "findings": findings})
        return 1
    print({"ok": True, "findings": []})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
