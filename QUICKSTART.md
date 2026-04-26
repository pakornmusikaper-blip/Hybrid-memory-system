# Quick Start

Status: Draft
Date: 2026-04-26

This quick start is for users who want the fastest path to a useful hybrid memory system.

## Goal

In one short setup pass, create:
- a sources layer
- a structured memory layer
- a wiki layer
- a tiny example corpus

## 1. Create the folder tree

Create:

```text
memory-root/
├── sources/
├── structured/
├── wiki/
└── search/
```

If you want the full package layout, use the architecture docs. For a fast start, the four core directories are enough.

## 2. Add one raw source

Create a simple source note in `sources/`.

Examples:
- a copied article
- a note from a conversation
- a short technical finding

## 3. Add three structured records

Recommended first three:
- one person record
- one decision record
- one system or project record

## 4. Add two wiki pages

Recommended first two:
- one system or concept page
- one workflow or comparison page

## 5. Ask real questions

Test with:
- a fact question
- a synthesis question
- a troubleshooting question

## 6. Review quality

Before scaling, check:
- records have sources
- summaries are clear
- wiki pages are worth keeping
- facts and synthesis are not mixed together

Then review:
- `LINT-PACK-V1.md`
- `lint/LINT-RULES.md`
- `ADOPTION-CHECKLIST.md`

## Success condition

If your agent can answer a few real questions better than transcript-only memory, the system is working.
