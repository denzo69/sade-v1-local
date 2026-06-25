# Repo Cleanup Plan

This project contains development history files that are useful locally but noisy in a public GitHub portfolio repo.

## Keep in public repo

- `app/` source modules
- `tests/`
- `docs/` policy and architecture docs
- `.github/` workflows and templates
- `README.md`, `QUICKSTART.md`, `SECURITY.md`, `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md`
- `requirements.txt`, `pytest.ini`, `.env.example`

## Do not publish

- `app/memory/`
- `memory/`
- `uploads/`
- `app/uploads/`
- `logs/`
- local backups
- vector databases
- auth/session files
- personal autobiographical data unless explicitly anonymized

## Archive or remove before public release

Candidate patterns:

- `patch_*.py`
- `add_*.py`
- `fix_*.py`
- `*_backup_*`
- one-off installation scripts that are no longer part of the supported workflow
- old zip packages

Recommended approach:

1. Keep them locally until the first clean public release is cut.
2. Move useful historical scripts to `_archive/development-scripts/` only if they help tell the project story.
3. Otherwise exclude them from the public branch.
4. Run `python scripts/release_readiness.py` before publishing.

## Cleanup applied on 2026-06-25

- Moved 49 legacy app backup/patch/generator files from `app/` to `archive/legacy-app-files/2026-06-25/`.
- Kept active runtime modules in `app/`.
- Added privacy scan script: `scripts/privacy_scan.py`.
- Updated README screenshots and portfolio positioning.

