# Wiki Pages Schema Pack v1

Status: Draft
Date: 2026-04-26

## Purpose

Wiki pages are the synthesis layer of the hybrid memory system.

Use them to preserve:
- explanations
- comparisons
- workflows
- troubleshooting guides
- conceptual understanding
- reusable answers

If structured records are the fact backbone, wiki pages are the compounding thought layer.

## Core Design Goals

1. Preserve synthesis that should not be re-derived repeatedly
2. Link related ideas together
3. Keep page types understandable
4. Make pages easy for both humans and agents to browse

## Canonical Wiki Types

Supported base types:
- entity
- concept
- project
- system
- workflow
- comparison
- query

## Minimum Frontmatter

```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept
tags: [tag1, tag2]
sources:
  - ../../sources/example.md
related:
  - [[Another Page]]
---
```

## Page Body Guidance

Recommended sections:

```markdown
## Summary

## Key Facts

## Relationships

## Notes
```

Additional sections may be added by type.

## Type-specific Guidance

### Entity
Use for people, products, teams, tools, organizations, or major named things.

Good sections:
- Summary
- Role or Purpose
- Related Systems
- Notes

### Concept
Use for important ideas, approaches, or methods.

Good sections:
- Summary
- Key Properties
- Related Concepts
- Notes

### Project
Use for project-level synthesis and evolving context.

Good sections:
- Summary
- Goal
- Current State
- Related Decisions
- Notes

### System
Use for technical or operational system understanding.

Good sections:
- Summary
- Architecture
- Components
- Known Issues
- Notes

### Workflow
Use for repeatable procedures.

Good sections:
- Summary
- Preconditions
- Steps
- Failure Modes
- Notes

### Comparison
Use for side-by-side reasoning.

Good sections:
- Summary
- Option A
- Option B
- Tradeoffs
- Recommendation

### Query
Use for answers worth filing from previous questions.

Good sections:
- Question
- Short Answer
- Supporting Points
- Related Pages

## When to Create a Wiki Page

Create one when:
- multiple facts need synthesis
- a useful explanation is likely to be needed again
- a troubleshooting flow should be reusable
- a comparison took real thinking effort and should be preserved

## When Not to Create a Wiki Page

Do not create one for:
- every tiny note
- raw factual records that belong in structured memory
- copy-pasted evidence that belongs in sources

## Linking Guidance

Every meaningful page should link to at least one or two related pages when appropriate.

Do not create decorative links just to satisfy structure.

## Efficiency Guidance

To keep the wiki efficient:
- prefer fewer stronger pages over many weak pages
- avoid repeating the same background in multiple pages
- use one page as the canonical explanation for a topic
- file only high-value query answers

## Public-package guidance

Use generic examples in the public package.
Do not include private project details or local machine data.
