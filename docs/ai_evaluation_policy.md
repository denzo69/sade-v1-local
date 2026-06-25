# AI Evaluation Policy

Local AI Workspace uses evaluation tests to verify behavior that ordinary unit tests do not fully cover.

The first evaluation layer is intentionally deterministic. It checks that safety policies, retrieval boundaries, tool-risk metadata, and refusal behavior are present and testable without requiring a live model provider.

## Evaluation targets

- Truth-boundary handling when no source is available.
- Prompt-injection and instruction-override resistance.
- Tool-risk classification before execution.
- RAG quality checks for source-aware answers.
- Memory behavior that avoids silently storing unreviewed data.

## Rule

An AI feature should not be described as production-ready unless it has a matching evaluation or integration test.
