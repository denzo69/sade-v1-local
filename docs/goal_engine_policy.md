# Goal Engine Policy

The goal engine is a read-only planning helper. It recommends the next development step from project state, tests, and documented gaps.

## Boundaries

- It must not execute file changes directly.
- It must not claim that planned features are already complete.
- It should prefer verifiable next steps over speculative roadmap items.

## Good output

A useful recommendation includes the reason, affected module, risk level, and a testable completion condition.
