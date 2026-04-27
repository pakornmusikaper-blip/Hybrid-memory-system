# v4.1 Adaptive Cognition Modes

Status: Draft
Date: 2026-04-27

## Goal

Make Substrate change its cognition style depending on event pressure and priority.

## Modes

### quiet-watch
Minimal work. Observe only.

### light-prepare
Prepare a small context bundle. No deep cognition.

### active-absorb
Ingest and process incoming events normally.

### reflective
Spend more cognition on pattern linkage and interpretation.

### alert
Escalate, wake conscious layer, and prioritize immediacy.

## Inputs

Mode policy should consider:
- prioritization decision
- current runtime health
- fallback rate / degraded condition
- queue pressure

## Desired behavior

- high pressure + healthy runtime -> alert / active-absorb
- high pressure + degraded runtime -> alert with compact handling
- low pressure + healthy runtime -> light-prepare or reflective
- low pressure + degraded runtime -> quiet-watch
