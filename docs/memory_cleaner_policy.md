# Memory Cleaner Policy

The memory cleaner keeps local memory useful without silently deleting important information.

## Rules

- Cleaning should be explicit and reviewable.
- Destructive cleanup must be audit logged.
- Private memory should not be included in the public repository.
- Expired or low-value entries may be flagged before deletion.

## Safer default

Prefer review and export over automatic deletion.
