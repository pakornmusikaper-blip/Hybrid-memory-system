# Hybrid Memory System, Package Vision

Status: Draft
Date: 2026-04-26

## Purpose

This package is a reusable memory architecture for long-running AI agents.

It is designed to help an agent move beyond short-lived chat memory and basic transcript recall by separating four concerns:

1. raw evidence
2. structured facts and state
3. synthesized knowledge
4. retrieval support

The package is intentionally generic.

It is not tied to Hermes.
It is not tied to OpenClaw.
It is not tied to one user.

It should work for:
- personal assistants
- research agents
- operational agents
- support agents
- multi-session coding agents

## First adopter

The first adopter is `best`, running in Pakorn's OpenClaw workspace.

The first implementation should optimize for:
- clarity
- low risk
- incremental rollout
- human-readable files
- future public release

## Package Goal

Provide a practical 9.5/10 memory architecture built on:
- Structured Memory
- LLM-Wiki
- Search layer

## Philosophy

### Why not transcript-only memory
Transcript-only memory is noisy, expensive to search repeatedly, and weak at cumulative synthesis.

### Why not RAG-only memory
RAG is useful for retrieval but weak at persistent compiled understanding.

### Why not wiki-only memory
Wiki-only memory is powerful but needs a fact backbone and retrieval support.

### Why hybrid
A high-quality agent needs:
- immutable evidence
- stable facts
- compounding synthesis
- efficient lookup

## Non-goals for v1

- not a vector database product
- not a hosted SaaS
- not a complex UI
- not an automatic ingestion engine from day one
- not tied to a specific model provider

## v1 shape

This package should first exist as a file-based architecture kit with:
- schema documentation
- directory conventions
- templates
- promotion rules
- example records and pages
- maintenance guidance

Later it can evolve into:
- a public GitHub repository
- an OpenClaw skill
- a Hermes-compatible integration layer
- optional search/indexing scripts

## Product Principles

1. Keep files human-readable
2. Keep the architecture modular
3. Separate source-of-truth layers clearly
4. Prefer conventions over heavy tooling early
5. Support both human and agent inspection
6. Make migration incremental and reversible
7. Design for open publication from the start
