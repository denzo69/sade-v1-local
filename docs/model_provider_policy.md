# Model Provider Policy

The application should isolate model-provider calls behind a provider layer so local and remote models can be swapped without rewriting the rest of the app.

## Goals

- Keep prompt construction separate from transport details.
- Make provider configuration explicit.
- Avoid hard-coding one model backend into unrelated modules.
- Keep error messages clear when the provider is unavailable.

## Portfolio value

This demonstrates maintainable AI application architecture rather than a one-off model integration.
