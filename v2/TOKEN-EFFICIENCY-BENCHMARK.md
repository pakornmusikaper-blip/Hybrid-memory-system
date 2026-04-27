# Token Efficiency Benchmark Plan

Status: Draft
Date: 2026-04-27

## Goal

Measure whether Substrate-style preparation reduces token usage and repeated context load.

## Compare

### A. Baseline mode
Conscious layer reads large raw context directly.

### B. Substrate mode
Conscious layer receives compact prepared bundle / belief summary.

## Metrics

- approximate input token count
- prompt size reduction ratio
- context reuse rate
- number of repeated source chunks
- latency proxy (character count / prompt size)

## Test scenarios

1. repeated question about the same project
2. repeated question about the same person
3. repeated system diagnosis flow
4. cross-linked follow-up question

## Expected outcome

Substrate mode should:
- reduce repeated prompt bulk
- reduce duplicated context injection
- improve reuse of summaries/beliefs

## Caveat

This benchmark is an approximation unless connected to a real token-counting API/model runtime.
