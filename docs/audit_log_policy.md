# Audit Log Policy

Audit logging records security-relevant actions in a way that is useful for debugging and review without exposing secrets.

## Logged events

- Authentication events.
- Tool execution decisions.
- Memory writes, deletes, exports, backups, and restores.
- High-risk or denied actions.
- Debug-trace events relevant to developer review.

## Redaction rule

Audit logs must not store passwords, session IDs, CSRF tokens, raw secrets, or full private memory contents.

## Integrity rule

Each important action should be explainable after the fact: what was requested, what policy was applied, and whether the action was allowed or denied.
