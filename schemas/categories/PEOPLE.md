# People Schema

Status: Draft
Date: 2026-04-26

## Purpose

Use people records for durable identity and relationship context.

This category should answer questions like:
- who is this person
- how should the agent refer to them
- what roles or identities matter
- what stable preferences or associations are already known

## Minimum fields

```yaml
id: person-id
title: Person Name
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: >
  Short summary.
tags:
  - person
sources:
  - path/to/source
related: []
```

## Recommended fields

```yaml
aliases: []
roles: []
labels: []
preferences: []
contact_points: []
notes: []
```

## Use when
- the person is queried repeatedly
- naming matters
- role context matters
- stable relationship context helps future work

## Avoid when
- the person is a passing mention only
- there is no durable value in preserving the record
