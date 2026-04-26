# Lint Rules Pack v1

Status: Draft
Date: 2026-04-26

## Purpose

Lint rules keep the memory system healthy as it grows.

The goal is not to maximize rule count. The goal is to catch the failures that most damage retrieval quality, trust, and maintainability.

## Rule Design Principles

1. Prefer a small number of high-value rules
2. Flag issues that materially harm future use
3. Avoid turning maintenance into busywork
4. Separate hard failures from advisory warnings

## Severity Levels

### Error
A problem that likely damages correctness, retrievability, or canonicality.

### Warning
A problem that weakens quality but may be acceptable temporarily.

### Info
An improvement suggestion or low-risk inconsistency.

## Core Rule Set

### R001. Missing minimum structured fields
Severity: Error

A structured record is invalid if it lacks one or more required minimum fields.

Required minimum:
- `id`
- `title`
- `status`
- `created`
- `updated`
- `summary`
- `tags`
- `sources`

### R002. Missing wiki frontmatter essentials
Severity: Error

A wiki page is invalid if it lacks required frontmatter fields:
- `title`
- `created`
- `updated`
- `type`
- `tags`
- `sources`

### R003. Missing source references
Severity: Error

A structured record or wiki page must cite at least one source unless it is explicitly a placeholder draft.

### R004. Duplicate canonical record for the same fact
Severity: Error

Two records should not both act as canonical homes for the same durable fact.

### R005. Raw source content copied into canonical layers without reason
Severity: Warning

Structured records and wiki pages should not become large dumps of copied source text.

### R006. Wiki page has no meaningful summary
Severity: Warning

A wiki page should explain why it exists, not only list fragments.

### R007. Structured summary is too vague
Severity: Warning

A structured record summary should identify the record's durable meaning, not generic filler.

### R008. Orphan wiki page
Severity: Warning

A page with no useful inbound or outbound relationships may be hard to discover and maintain.

### R009. Stale active decision
Severity: Warning

An active decision record that has not been reviewed for a long period may still be valid, but should be reconsidered.

### R010. Category mismatch
Severity: Warning

A record placed in the wrong category weakens retrieval and mental model clarity.

### R011. Weak or unstable tags
Severity: Info

Tags that are overly generic, inconsistent, or one-off reduce classification value.

### R012. Over-promotion
Severity: Info

Not every observation should be promoted into canonical memory. Low-value promotions create noise.

## Rule Application Notes

These rules may be checked manually at first.
They do not require automation in v1.

The most important rules early on are:
- R001
- R002
- R003
- R004
- R006
