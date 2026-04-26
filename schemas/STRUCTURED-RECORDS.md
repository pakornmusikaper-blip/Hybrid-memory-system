# Structured Records Schema Pack v1

Status: Draft
Date: 2026-04-26

## Purpose

Structured records are the fact backbone of the hybrid memory system.

They exist to answer questions that require:
- stable facts
- explicit state
- canonical decisions
- durable references
- low ambiguity

Use structured records for information that should not live only in chat history or only in freeform wiki prose.

## Core Design Goals

1. Make important facts easy to retrieve
2. Keep records human-readable
3. Preserve source references
4. Support incremental updates
5. Avoid forcing premature complexity

## Canonical Categories

The base package supports these categories:

- people
- preferences
- projects
- decisions
- systems
- tasks
- timelines

Additional categories may be added later, but these should cover most early use cases.

## Universal Minimum Schema

Every structured record should contain at least:

```yaml
id: unique-record-id
title: Human Title
status: active | draft | archived
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: >
  One paragraph summary.
tags:
  - tag-a
sources:
  - path/to/source
related: []
```

## Recommended Extended Fields

```yaml
owner: best
scope:
  - personal
  - technical
canonical: true
confidence: high | medium | low
review_after: YYYY-MM-DD
```

Use these only where they add value.

## Category-specific Recommendations

### People
Use for stable identity and relationship context.

Recommended extra fields:
```yaml
aliases: []
roles: []
preferences: []
contact_points: []
```

### Preferences
Use for durable user, team, or agent preferences.

Recommended extra fields:
```yaml
subject: user | agent | team
preference_type: communication | tooling | workflow | style
value: >
  The preference itself.
```

### Projects
Use for active or important workstreams.

Recommended extra fields:
```yaml
goal: >
  Primary goal.
state: active | paused | completed | archived
owners: []
key_paths: []
dependencies: []
```

### Decisions
Use for architecture, policy, and workflow decisions.

Recommended extra fields:
```yaml
decision: >
  What was decided.
rationale: >
  Why it was decided.
impact:
  - area-a
supersedes: []
```

### Systems
Use for system-level state or architecture facts.

Recommended extra fields:
```yaml
system_type: software | workflow | infrastructure | process
key_paths: []
components: []
```

### Tasks
Use only for durable tasks worth persisting outside ephemeral todo flow.

Recommended extra fields:
```yaml
priority: low | medium | high | critical
assignee: best
next_action: >
  Immediate next action.
```

### Timelines
Use for historical sequences worth preserving.

Recommended extra fields:
```yaml
period: YYYY-MM | YYYY-MM-DD
events: []
```

## Canonicality Rule

A structured record should be the canonical home for a fact when:
- the fact is likely to be queried repeatedly
- ambiguity would be costly
- it has operational or architectural importance

Do not create structured records for every trivial note.

## Good Use Cases

- who the user is
- important preferences
- current project state
- technical architecture decisions
- canonical paths
- repeated troubleshooting conclusions

## Bad Use Cases

- rough brainstorming
- freeform analysis better suited to wiki pages
- raw source copies
- noisy short-lived execution notes

## Update Discipline

When updating a record:
1. preserve the existing `id`
2. update `updated`
3. keep `summary` concise
4. add or update sources when evidence changes
5. do not silently change important facts without updating rationale in related records when needed

## Efficiency Guidance

To keep retrieval efficient:
- prefer one canonical record over many duplicates
- keep summaries short
- use category-specific folders
- keep tags stable
- add `related` links only when genuinely useful

## Public-package guidance

The package should include generic sample records, not private real-user records.
