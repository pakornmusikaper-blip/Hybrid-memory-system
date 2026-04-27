# v4.0 Event Prioritization Engine

Status: Draft
Date: 2026-04-27

## Goal

Make Substrate decide what deserves attention before spending cognition.

## Core idea

Not every event should be treated equally.
Substrate should classify events into priority bands and choose a cognition mode.

## Priority bands

- **critical** — immediate escalation or processing
- **high** — process soon, likely wake conscious layer
- **normal** — process in ordinary loop
- **low** — defer or batch
- **silent** — ignore or archive quietly

## Event examples

### critical
- contradiction on high-confidence belief
- repeated queue poison item on important domain
- urgent correction from conscious layer

### high
- new query from bridge
- strong intuition candidate
- significant confidence shift

### normal
- routine absorb event
- standard follow-up context prep
- scheduled review

### low
- repetitive low-value refresh
- stale weak belief cleanup

### silent
- exact duplicate low-value events
- already handled repetitive noise

## Decision outputs

Each prioritization returns:
- priority band
- recommended mode
- whether to wake conscious layer
- whether to process immediately
- optional defer seconds

## Modes

- `alert`
- `active-absorb`
- `light-prepare`
- `reflective`
- `quiet-watch`
- `silent-drop`

## Why this matters

This is the first real layer of pre-conscious intelligence.
It decides what is worth thought before thought happens.
