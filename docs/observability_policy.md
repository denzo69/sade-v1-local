# Observability Policy

Observability explains why the system made a decision.

## Useful trace fields

- User request category.
- Selected module or tool.
- Policy decision.
- Source documents used.
- Error state and safe fallback.

## Privacy rule

Debug traces must be useful without leaking secrets, passwords, session IDs, or full private memory contents.
