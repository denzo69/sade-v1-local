# Tool Permission Policy

Tool permissions separate safe read actions from actions that can change local state.

## Risk levels

- `read`: inspect local project state.
- `memory_write`: write durable memory.
- `file_write`: modify project files.
- `network`: fetch external information.
- `critical`: actions that affect secrets, authentication, restore, or system execution.

## Rule

The router should classify a tool action before execution and deny or require confirmation for risky operations.
