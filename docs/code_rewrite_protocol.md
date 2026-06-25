# Code Rewrite Protocol

This protocol defines how Local AI Workspace code may be changed while preserving truth boundaries, testability, rollback safety, and auditability.

## Rule

Do not claim a change is complete until it has been written, reviewed, tested, and documented.

## Before a change

- Define the goal in one sentence.
- Identify affected modules.
- Identify risks.
- Decide whether the work is a patch, refactor, rewrite, or rollback.

## During a change

- Keep changes small and reversible.
- Avoid mixing unrelated feature work into bug fixes.
- Preserve authentication, audit logging, and memory safeguards.

## Required checks

- Unit tests for local behavior.
- Integration tests for memory, tools, web search, or audit flows.
- Regression tests for fixed bugs.
- Secret redaction checks when logs or traces are involved.

## Merge criteria

A change is ready when tests pass, documentation is updated when needed, and the rollback path is clear.
