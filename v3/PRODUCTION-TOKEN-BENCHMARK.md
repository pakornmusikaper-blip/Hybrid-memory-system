# Production-Style Token Benchmark

Status: Draft
Date: 2026-04-27

## Goal

Estimate prompt-size and token-shape differences between:

1. baseline direct-context mode
2. substrate prepared bundle mode
3. runtime/bridge response mode

## Why this benchmark matters

v2 showed architectural savings in prompt bulk.
v3 now has queue/runtime/bridge/operator layers.
This benchmark asks whether the operational flow still preserves token efficiency.

## Scenarios

### Scenario A: initial system question
Large direct context vs prepared substrate summary.

### Scenario B: follow-up question
Repeated direct memory load vs compact response path.

### Scenario C: runtime bridge response
Compare what a bridge-style processed response looks like against direct source injection.

## Metrics

- chars
- approx tokens
- reduction ratio
- follow-up reduction ratio
- runtime-response reduction ratio

## Caveat

This is still approximate unless measured against exact model provider accounting.
It is still useful for architecture decisions because prompt bulk strongly correlates with token usage.
