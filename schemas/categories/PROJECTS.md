# Projects Schema

Status: Draft
Date: 2026-04-26

## Purpose

Use project records for active or important workstreams with durable identity.

This category should answer questions like:
- what is the project
- what is its current state
- what are the main paths, goals, and dependencies

## Minimum fields

```yaml
id: project-id
title: Project Title
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: >
  Short summary.
tags:
  - project
sources:
  - path/to/source
related: []
```

## Recommended fields

```yaml
goal: >
  Primary goal.
state: active | paused | completed | archived
owners: []
key_paths: []
dependencies: []
next_focus: >
  Most important next area.
```

## Use when
- the work has continuity across sessions
- location and state matter
- future agents should understand what is ongoing

## Avoid when
- the work is a trivial one-shot task
