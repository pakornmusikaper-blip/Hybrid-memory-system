# Decisions Schema

Status: Draft
Date: 2026-04-26

## Purpose

Use decision records for architectural, policy, and workflow decisions worth preserving canonically.

This category should answer questions like:
- what was decided
- why was it decided
- what does it affect
- what did it replace

## Minimum fields

```yaml
id: decision-id
title: Decision Title
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: >
  Short summary.
tags:
  - decision
sources:
  - path/to/source
related: []
```

## Recommended fields

```yaml
decision: >
  What was decided.
rationale: >
  Why it was decided.
impact: []
supersedes: []
tradeoffs: []
```

## Use when
- the decision will likely be referenced again
- ambiguity would be costly
- later work depends on the decision

## Avoid when
- the conclusion is still too unstable to preserve canonically
