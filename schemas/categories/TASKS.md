# Tasks Schema

Status: Draft
Date: 2026-04-26

## Purpose

Use task records only for durable or high-value tasks that should persist beyond ephemeral chat flow.

This category should answer questions like:
- what remains to be done
- what is blocked
- what next action matters

## Minimum fields

```yaml
id: task-id
title: Task Title
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: >
  Short summary.
tags:
  - task
sources:
  - path/to/source
related: []
```

## Recommended fields

```yaml
priority: low | medium | high | critical
state: pending | in_progress | blocked | completed
assignee: best
next_action: >
  Immediate next action.
blockers: []
```

## Use when
- a task spans sessions
- missing it would be costly
- it belongs in durable operational memory

## Avoid when
- the task is short-lived and already handled by lightweight todo flow
