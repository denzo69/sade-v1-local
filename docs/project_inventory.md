# Project Inventory

Local AI Workspace is a FastAPI-based local assistant workspace with a browser UI and safety-focused AI engineering features.

## Main components

- `app/main.py` — FastAPI routes and application wiring.
- `app/templates/ui.html` — browser UI.
- `app/auth.py` — local authentication and sessions.
- `app/audit_log.py` — audit event writing.
- `app/rag_engine.py` — retrieval over local sources.
- `app/semantic_memory.py` — semantic memory helper layer.
- `app/tool_router.py` — tool command routing.
- `app/language_pack.py` — UI localization support.
- `tests/` — unit, integration, security, and release-readiness tests.

## Public boundary

The repository should include code, tests, and documentation, not private local memory data.
