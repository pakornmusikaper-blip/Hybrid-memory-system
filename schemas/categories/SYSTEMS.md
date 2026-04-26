# Systems Schema

Status: Draft
Date: 2026-04-26

## Purpose

Use system records for technical or operational systems with stable structure or important state.

This category should answer questions like:
- what system is this
- what components matter
- what paths are canonical
- what known issues or states matter

## Minimum fields

```yaml
id: system-id
title: System Title
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: >
  Short summary.
tags:
  - system
sources:
  - path/to/source
related: []
```

## Recommended fields

```yaml
system_type: software | infrastructure | workflow | process
key_paths: []
components: []
known_issues: []
notes: []
```

## Use when
- the system has recurring operational relevance
- canonical paths or components matter
- troubleshooting context is likely to recur

## Avoid when
- the information is purely temporary runtime noise
