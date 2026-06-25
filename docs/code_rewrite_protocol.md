# Säde Code Rewrite Protocol

## Purpose

This protocol defines how Säde v1 code may be changed while preserving truth boundaries, testability, rollback safety, and auditability.

## Core rule

Do not claim a change is complete until:

1. the change exists in files,
2. relevant tests have been run,
3. the result has been documented,
4. a rollback path exists when the change is risky.

## When a rewrite is allowed

A rewrite is allowed when at least one condition is true:

- a bug or contradiction is reproducible,
- documentation and implementation disagree,
- a critical route lacks tests,
- a refactor removes real complexity or risk,
- a safety boundary is unclear or unenforced.

## Before changing code

Record:

- the goal in one sentence,
- affected modules,
- expected behavior before and after,
- risk level,
- test plan,
- rollback plan.

Choose one change type:

- `patch`: small targeted fix,
- `refactor`: behavior-preserving structure change,
- `rewrite`: larger replacement with tests,
- `revert`: restore a known safer state.

## During the change

- Prefer small, reviewable changes.
- Do not mix unrelated features into a bug fix.
- Do not weaken guardrails without replacing them.
- Preserve user data and local memory files.
- Treat external input, uploaded files, and retrieved web content as untrusted.

## Required checks

Run the smallest useful test set first, then the full suite when the change is broad.

Required for high-risk areas:

- memory writes,
- file writes,
- authentication,
- audit logging,
- RAG/source handling,
- web search,
- tool routing,
- system prompt changes,
- backup/restore.

## Merge criteria

A change can be accepted when:

- tests are green,
- documentation impact has been checked,
- safety or permission changes are audited,
- user-facing terminology remains clear,
- planned, implemented, and tested states are not confused.

## Forbidden

- Do not claim an integration is complete without a test or demo path.
- Do not commit secrets, sessions, personal memory, vector DBs, backups, or uploads.
- Do not silently delete memory or user data.
- Do not hide test failures in documentation.
- Do not present a prototype route as production-ready.

## Rollback

Every risky rewrite should state:

- previous commit or backup point,
- files affected,
- data migration risk,
- rollback command or manual rollback steps.

## Audit entry

For meaningful rewrites, record:

- date,
- reason,
- affected modules,
- tests run,
- outcome,
- open risks.
