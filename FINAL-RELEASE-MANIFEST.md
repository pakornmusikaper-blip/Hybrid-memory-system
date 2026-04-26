# Final Release Manifest

Status: Draft
Date: 2026-04-26
Target release: v0.1 documentation-first

## Release intent

This release should publish the Hybrid Memory System as a documentation-first architecture kit for long-running AI agents.

The goal is not to ship every possible extension.
The goal is to ship a coherent, useful, public-safe first version.

## Include

### Root documents
- `README.md`
- `PACKAGE-INDEX.md`
- `PACKAGE-VISION.md`
- `QUICKSTART.md`
- `FIRST-30-MINUTES.md`
- `COMMON-MISTAKES.md`
- `ADOPTION-CHECKLIST.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `SCHEMA-PACK-V1.md`
- `CATEGORY-SCHEMA-PACK-V1.1.md`
- `CATEGORY-TEMPLATES-PACK-V1.md`
- `LINT-PACK-V1.md`

### Directories
- `references/`
- `schemas/`
- `templates/`
- `lint/`
- `onboarding/`
- `examples/`
- `repo/`

## Intentionally not required for v0.1

- automation scripts
- platform-specific integration code
- private operational corpora
- local-only overlays
- complex search/index tooling

## Core public message

Hybrid Memory System helps agents preserve evidence, store canonical facts, build reusable synthesis, and improve retrieval quality over time.

## Release rule

If a file does not improve adoption, clarity, or maintainability for a public user, it should not be required in v0.1.
