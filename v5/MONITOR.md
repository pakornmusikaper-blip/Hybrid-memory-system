# Consciousness Monitor

Status: Draft
Date: 2026-04-27

## Goal

Provide real-time visibility into the "vital signs" of the Substrate consciousness system.

## What to monitor

### Runtime vitality
- Is daemon running?
- Are cycles incrementing?
- Is state.json being updated?
- Last successful tick timestamp

### Queue pressure
- inbox depth (pending events)
- outbox depth (pending deliveries)
- processed count
- poison queue (failed items)

### Belief health
- Total beliefs / active / retired
- Stages distribution
- Average confidence
- Weakening beliefs count

### Concept coherence
- Total concepts / coherent / mature
- Average coherence score
- Dissolved concepts

### Cognitive patterns
- Dominant mode (last N ticks)
- Wake distribution (wake/accumulate/silent)
- Budget spend trend
- Recent spend level

### Self-reflection health
- Last reflection timestamp
- Is system healthy?
- Recommendations count

## Output format

Human-readable status panel:
- Overall status (alive/degraded/critical)
- Key metrics
- Alerts (if any)
- Latest self-reflection summary

## Alert conditions

- consecutive_errors >= 3
- fallback_rate >= 0.3
- inbox depth >= 10
- health = "degraded"
- no cycles for 60s
- beliefs stuck in embryonic > 24h