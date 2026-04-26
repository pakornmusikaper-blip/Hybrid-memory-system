# Hybrid Memory System

> **v2 is here!** The Substrate Agent brings autonomous learning to the memory system. [Learn more →](v2/README.md)

A documentation-first hybrid memory architecture for long-running AI agents.

Most agent memory systems either keep too much chat history or depend too heavily on retrieval alone. Hybrid Memory System gives long-running agents a more durable knowledge model by separating evidence, facts, synthesis, and search into distinct layers.

The result is a memory system that is easier to maintain, easier to review, and more reliable to use across repeated real work.

![Architecture Overview](ARCHITECTURE-DIAGRAM.svg)

## Architecture at a glance

```
sources/       →  Raw evidence (immutable)
structured/    →  Canonical facts & state
wiki/          →  Synthesis & reusable knowledge
search/        →  Retrieval support (rebuildable)
```

Each layer has a clear purpose and its own promotion discipline.

## Who this is for

- Personal AI assistants that need to remember facts reliably
- Research agents that compound knowledge over time
- Operational agents that handle recurring real-world work
- Long-running project assistants that need lower noise memory

## What is inside

- **Architecture docs** — layer design and reasoning
- **Schema packs** — structured records, wiki pages, promotion rules
- **Category schemas** — people, preferences, projects, decisions, systems, tasks, timelines
- **Templates** — copy-ready record and page templates for every category
- **Lint & quality standards** — rules to keep the system clean as it grows
- **Onboarding guides** — quick start, 30-minute guide, common mistakes
- **Public-safe examples** — minimal memory stack, category examples, lint findings

## Best starting path

1. Read this README
2. Read `PACKAGE-INDEX.md` for the full map
3. Read `QUICKSTART.md` to get started in minutes
4. Read `FIRST-30-MINUTES.md` for the full onboarding experience

## Core design principle

> Promote carefully. Not everything should become canonical memory. Only keep what will remain useful and trustworthy over time.

The system protects itself from becoming a noisy archive by enforcing clear boundaries between layers and a review discipline that catches degradation early.

## Why this is different from transcript-only or retrieval-only memory

Most AI agents today rely on one of two memory approaches:

### Transcript-only memory
Stores every conversation, every document, every note in one place.

**Problems as it scales:**
- Facts, synthesis, evidence, and noise all live together
- Retrieval returns whatever semantically matches, not what is canonically correct
- No distinction between raw evidence and synthesized knowledge
- Memory grows noisy and trust degrades
- Agents repeat the same mistakes because old context and new context look the same

### Retrieval-only memory (RAG)
Uses vector search to find relevant documents from a large corpus.

**Problems as it scales:**
- Retrieval quality depends on embedding and chunking quality
- No canonical source of truth for facts
- Facts and synthesis are mixed in retrieved documents
- No lifecycle management — old documents stay forever even when wrong
- Search alone cannot fix a system that stores the wrong things

### Hybrid Memory System approach

Separates four distinct layers with clear boundaries and promotion discipline:

| Approach | Evidence | Facts | Synthesis | Retrieval |
|---|---|---|---|---|
| Transcript-only | mixed | mixed | mixed | hard to find |
| RAG-only | mixed | mixed | mixed | only search |
| **Hybrid Memory System** | `sources/` | `structured/` | `wiki/` | `search/` |

The key difference: **facts are canonical, synthesis is reusable, evidence is preserved, and retrieval supports — not replaces — a real knowledge model.**

Over time, this means:
- Agents answer fact questions more reliably
- Knowledge compounds correctly instead of accumulating noise
- Review and maintenance stay manageable because degradation is caught early
- External systems like Apollo WorkOS stay canonical while global knowledge stays shared

## Architecture diagram

![Architecture Overview](ARCHITECTURE-DIAGRAM.svg)

The diagram shows:
- **Four memory layers** from evidence to retrieval
- **Promotion discipline** connecting maintenance to canonical layers
- **External systems** (Apollo/Hermes, OpenClaw) feeding source evidence selectively
- **Boundary** between the public package and live knowledge-system adoption

## Quick reference

| Layer | Format | Purpose |
|---|---|---|
| `sources/` | Any raw file | Immutable evidence |
| `structured/` | YAML | Canonical facts, state, decisions |
| `wiki/` | Markdown + frontmatter | Reusable synthesis |
| `search/` | Manifests, catalogs | Retrieval support |

## Related resources

- `ARCHITECTURE.md` — detailed layer design
- `SCHEMA-PACK-V1.md` — structured record and wiki schema guidance
- `CATEGORY-SCHEMA-PACK-V1.1.md` — category-specific schema extensions
- `LINT-PACK-V1.md` — quality rules and maintenance workflow
- `QUICKSTART.md` — fastest path to a working system
- `repo/PUBLISHING-SEQUENCE.md` — how this package was released

## License

MIT — see `LICENSE`