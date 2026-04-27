# v6.3 Runtime Adapter Integration

Status: Draft
Date: 2026-04-27

## Goal

Integrate model routing and adapters into the intelligent runtime so execution backend is chosen dynamically.

## Flow

```text
event
  -> prioritizer
  -> mode_policy
  -> wake_policy
  -> cost_budget_policy
  -> model_routing_policy
  -> chosen adapter.generate()/summarize()/reflect()
```

## Inputs to routing

- privacy tag on event
- budget band from cost budget policy
- mode/depth from cognition decision
- urgency from wake decision

## Outputs

- chosen backend
- model result
- fallback status
- backend trace in runtime logs
