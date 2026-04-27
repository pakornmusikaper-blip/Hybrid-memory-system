# v6.7 Persisted Usage Ledger

Status: Draft
Date: 2026-04-27

## Goal

Persist external model usage across runtime restarts so daily limits are trustworthy.

## Stores

- date key
- request count
- estimated cost
- per-provider breakdown
- optional event log

## Why

In-memory counters reset on restart. A persisted ledger makes budget enforcement reliable.
