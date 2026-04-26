# Preferences Schema

Status: Draft
Date: 2026-04-26

## Purpose

Use preference records for durable behavioral, communication, workflow, or tooling preferences.

This category should answer questions like:
- how should the agent communicate
- what style does the user prefer
- what workflow choices should be remembered

## Minimum fields

```yaml
id: preference-id
title: Preference Title
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: >
  Short summary.
tags:
  - preference
sources:
  - path/to/source
related: []
```

## Recommended fields

```yaml
subject: user | agent | team
preference_type: communication | workflow | tooling | style
value: >
  The preference itself.
strength: strong | medium | weak
notes: []
```

## Use when
- the preference changes future behavior materially
- it is likely to be repeated or relied on

## Avoid when
- it is a one-off mood or temporary suggestion
