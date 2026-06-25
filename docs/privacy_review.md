# Privacy review

Date: 2026-06-25

This project is intended to be published as a portfolio repository. Before publishing, verify that local personal data is not committed.

## Protected by `.gitignore`

- `.env`
- `app/memory/*.jsonl`
- `app/memory/*.json`
- `app/memory/chat_log.md`
- `app/memory/sade_memory.md`
- `app/memory/auth.json`
- `app/memory/auth_sessions.json`
- `app/uploads/`
- `reports/htmlcov/`
- `reports/coverage.xml`

## Manual release checklist

1. Run `python scripts/privacy_scan.py`.
2. Run `python scripts/release_readiness.py`.
3. Review `git status` before pushing.
4. Do not publish personal memory, sessions, uploads, local backups, or API keys.
5. Replace screenshots if they reveal private browser tabs or personal information.

## Current note

Legacy development files were moved under `archive/legacy-app-files/2026-06-25/` to keep active runtime modules easier to review.
