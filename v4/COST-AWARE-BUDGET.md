# v4.3 Cost-Aware Cognition Budget

Status: Draft
Date: 2026-04-27

## Goal

Make Substrate choose cognition depth based on real cost tradeoffs.

## Cost model

### Cheap operations
- belief reuse
- anticipation cache hit
- heuristic response
- quiet-watch monitoring

### Moderate cost
- light-prepare
- active-absorb standard depth
- structured record lookup

### Expensive
- reflective deep cognition
- model generation
- pattern recognition over large corpus

## Budget bands

### tight
Minimal spend. Only critical events trigger expensive ops.

### normal
Balanced. Moderate spend on high-value work.

### generous
Full depth. Invest in rich cognition for complex cases.

## Decision inputs

- current token/spend budget
- event urgency and value
- fallback rate
- recent spend trend
- conscious layer urgency signal

## Policy

- tight budget: escalate only, use heuristic for non-critical
- normal budget: balanced depth for high-priority
- generous budget: reflective depth for moderate signals too

## Why this matters

Token budget is finite. A truly intelligent substrate should know when to invest and when to conserve.
