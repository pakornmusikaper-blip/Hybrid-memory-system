# Promotion Rules, Schema Pack v1

Status: Draft
Date: 2026-04-26

## Purpose

Promotion rules determine where information should live.

Without clear promotion rules, a memory system becomes noisy, duplicative, and expensive to query.

## Four Destinations

### 1. Sources
Put information in `sources/` when it is raw evidence.

Examples:
- exported transcript
- copied article
- screenshot
- raw log

### 2. Structured records
Put information in `structured/` when it is a stable fact, decision, or explicit state.

Examples:
- user preference
- project state
- key path
- architectural decision

### 3. Wiki pages
Put information in `wiki/` when it is synthesis, explanation, or reusable reasoning.

Examples:
- comparison of architectures
- troubleshooting guide
- conceptual explanation
- preserved query answer

### 4. Leave it ephemeral
Leave information in temporary notes or daily memory when it is not yet important enough to promote.

Examples:
- rough ideas
- uncertain observations
- low-value working notes

## Promotion Decision Questions

Ask:
1. Is this raw evidence
2. Is this a stable fact
3. Is this synthesis or explanation
4. Is this important enough to preserve canonically
5. Is this local-only or globally reusable

## Promotion Table

| Information kind | Destination |
|---|---|
| document, transcript, log | sources |
| preference, canonical path, key fact | structured |
| explanation, comparison, workflow | wiki |
| rough scratch note | ephemeral |

## Local vs Global Promotion

### Keep local when
- the note is task-specific
- the knowledge is unlikely to be reused elsewhere
- the conclusion is still unstable

### Promote global when
- the knowledge is reusable
- the decision affects multiple tasks or systems
- it represents a durable preference or policy
- it improves future answers materially

## Anti-patterns

Do not:
- copy raw source text into structured records unnecessarily
- use wiki pages as dumping grounds for every fact
- create multiple canonical records for the same thing
- promote uncertain notes too early

## Efficiency Rule

Promote only what increases future retrieval quality enough to justify maintenance cost.
