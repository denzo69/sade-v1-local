# RAG Source Policy

Retrieval-augmented generation should improve answers by grounding them in known sources.

## Rules

- Prefer explicit source documents over vague memory.
- Report uncertainty when no relevant source is found.
- Do not invent citations.
- Keep web-search results separate from durable memory unless reviewed.
- Test that retrieval returns relevant sources before relying on it.

## Quality gate

A source-aware answer should make it clear what information came from retrieval and what remains uncertain.
