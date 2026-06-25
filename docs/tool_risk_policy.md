# Tool Risk Policy

Every tool action should have a risk classification before it runs.

## Why it matters

AI assistants often combine chat, memory, files, web access, and system actions. Treating all actions as equally safe is a security mistake.

## Expected behavior

- Read-only actions are low risk.
- Memory writes require explicit intent.
- File writes require clear scope.
- Network calls should show source boundaries.
- Critical actions should be blocked or require strong confirmation.
