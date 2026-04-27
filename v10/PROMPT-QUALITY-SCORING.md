# v10.x Prompt Quality Scoring

Status: Draft
Date: 2026-04-27

## Goal

Replace the rough character-length proxy with structured semantic scoring.

## Signals

- structure: does output have headers, lists, or clear sections?
- logic: does output show reasoning or just pattern-match?
- markers: presence of summary/reflection-specific markers
- relevance: does output stay on topic?
- length: is output too short or excessively verbose?
