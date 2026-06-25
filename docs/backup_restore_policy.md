# Backup and Restore Policy

Local AI Workspace includes backup and restore support for local memory and documentation data.

## Backup scope

Backups may include:

- local memory files,
- project documentation,
- selected configuration files,
- audit metadata required for recovery review.

Backups must not be committed to Git.

## Restore rule

Restore is a high-risk operation. It should require explicit user intent, be audit logged, and preserve a clear rollback path when possible.
