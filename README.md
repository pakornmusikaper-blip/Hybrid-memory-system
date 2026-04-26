# Hybrid Memory System

Status: Internal incubation, release-ready draft
Date: 2026-04-26

Hybrid Memory System is a reusable file-based memory architecture for long-running AI agents.

It is designed to help agents move beyond transcript-only memory by separating:
- raw evidence
- structured facts and state
- synthesized knowledge
- retrieval support

This package is intentionally documentation-first.
It is designed to be useful before any heavy automation exists.

## Who this is for

Use this package if you want an agent that:
- keeps stable facts separately from explanations
- compounds knowledge over time
- answers repeated questions more consistently
- preserves evidence without treating every transcript as canonical memory

It is a strong fit for:
- personal assistants
- research agents
- operational agents
- long-running project assistants

## What is inside

- vision and architecture docs
- schema packs
- category-specific templates
- lint and quality guidance
- onboarding and quick-start guides
- public-safe example corpora
- repository-release guidance

## Best starting path

If you are new to the package, read in this order:
1. `PACKAGE-INDEX.md`
2. `PACKAGE-VISION.md`
3. `QUICKSTART.md`
4. `FIRST-30-MINUTES.md`

If you are evaluating it for publication, continue with:
5. `FINAL-RELEASE-MANIFEST.md`
6. `repo/FIRST-GITHUB-RELEASE-SET.md`
7. `repo/PUBLISHING-SEQUENCE.md`

## Core idea

Use four layers:
1. `sources/` for raw evidence
2. `structured/` for canonical facts and state
3. `wiki/` for synthesis and reusable explanations
4. `search/` for retrieval support artifacts

## Release posture

This package is already strong enough for a careful documentation-first public release.

## Important constraint

Do not assume every local experiment belongs in the public package.
Only keep what generalizes well.
