# v4.4 Integrate v4 into v3 Runtime

Status: Draft
Date: 2026-04-27

## Goal

Wire v4 intelligence layers (prioritization, modes, wake, budget) into the v3 runtime tick loop.

## Architecture

```
runtime tick:
  1. receive event from queue/inbox
  2. prioritizer.decide(event)           -> priority band
  3. mode_policy.decide(priority)       -> cognition mode
  4. wake_policy.decide(mode, event)     -> wake/accumulate/silent
  5. cost_budget_policy.decide(wake, health, spend_trend) -> budget band
  6. execute cognition at appropriate depth
  7. write result to outbox or accumulate
```

## Integration points

- v4/prioritizer.py -> runtime tick entry
- v4/mode_policy.py -> runtime cognition depth
- v4/wake_policy.py -> runtime wake/escalate path
- v4/cost_budget_policy.py -> runtime resource management

## Behavior changes

- runtime becomes "intelligent" not just mechanical
- queue events trigger cognitive pipeline
- output routing respects wake decision
- budget tracking affects future ticks
