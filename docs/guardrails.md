# Guardrails

Local AI Workspace uses guardrails to keep model behavior, memory use, and tool execution inside clear boundaries.

## Main rules

- Do not claim unsupported facts.
- Do not invent sources.
- Do not store sensitive information without explicit intent.
- Do not execute high-risk tools without policy checks.
- Do not expose local secrets in logs, screenshots, or documentation.

## Truth boundary

If the system cannot verify something from local state, source documents, or an explicit web-search result, it should say so.
