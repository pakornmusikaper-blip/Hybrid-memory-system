# Timelines Schema

Status: Draft
Date: 2026-04-26

## Purpose

Use timeline records for historical sequences or period summaries worth preserving.

This category should answer questions like:
- what happened during a given period
- what sequence led to the current state
- what milestones matter

## Minimum fields

```yaml
id: timeline-id
title: Timeline Title
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: >
  Short summary.
tags:
  - timeline
sources:
  - path/to/source
related: []
```

## Recommended fields

```yaml
period: YYYY-MM | YYYY-MM-DD
events: []
conclusion: >
  Optional summary of what the sequence means.
```

## Use when
- a sequence matters more than isolated facts
- future reasoning benefits from chronology

## Avoid when
- daily memory already captures enough and there is no reuse value
