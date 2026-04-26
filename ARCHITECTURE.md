# Hybrid Memory System, Architecture

Status: Draft
Date: 2026-04-26

## Core Model

The system has four layers.

### Layer 1. Sources
Immutable raw inputs.

Examples:
- documents
- pasted notes
- exported chats
- screenshots
- logs
- transcripts

Purpose:
- preserve evidence
- support auditability
- avoid knowledge distortion

### Layer 2. Structured Memory
Stable fact records.

Examples:
- people
- preferences
- projects
- decisions
- tasks
- systems
- timelines

Purpose:
- answer factual questions reliably
- store state explicitly
- reduce ambiguity

### Layer 3. Wiki
Synthesized and cross-linked knowledge.

Examples:
- concepts
- troubleshooting guides
- workflows
- comparisons
- project pages
- reusable answers

Purpose:
- preserve analysis and synthesis
- accumulate insight over time
- reduce repeated re-derivation

### Layer 4. Search
Retrieval support artifacts.

Examples:
- catalogs
- manifests
- caches
- optional indexes

Purpose:
- accelerate lookup
- support larger corpora
- avoid treating search indexes as primary knowledge

## Canonical Layout

```text
hybrid-memory-root/
├── sources/
├── structured/
├── wiki/
├── search/
├── maintenance/
├── templates/
└── references/
```

## Promotion Rules

- raw evidence stays in `sources/`
- facts move into `structured/`
- synthesis moves into `wiki/`
- search artifacts are rebuildable and live in `search/`

## Query Strategy

### Fact lookup
1. structured
2. curated memory
3. recent notes
4. sources

### Synthesis lookup
1. wiki
2. structured
3. sources

### Troubleshooting lookup
1. wiki workflows and systems
2. structured systems and decisions
3. sources and logs

## Recommended Rollout

### Phase 1
- backbone folders
- schema docs
- templates

### Phase 2
- first fact records
- first wiki pages
- minimal real usage

### Phase 3
- catalogs and search manifests
- maintenance workflows

### Phase 4
- optional automation
- optional agent integration wrappers

## Public-package design constraint

Keep this package generic enough that it can be published without leaking:
- private identities
- local tokens
- machine-specific secrets
- one-off operational noise
