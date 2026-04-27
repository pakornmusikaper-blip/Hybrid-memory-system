# SUBSTRATE OPERATOR PLAYBOOK

Status: Ready
Date: 2026-04-27

## Overview

SUBSTRATE is an autonomous conscious-subconscious AI agent platform. It runs a cognitive pipeline (priority → mode → wake → budget → route → adapter) and can use local, external, or hybrid execution paths.

## Quick Start

```bash
# Full operator workspace
python v10/operator_workspace.py --root /path/to/state --ledger /path/to/ledger.json status
python v10/operator_workspace.py --root /path/to/state --ledger /path/to/ledger.json dashboard

# Run all checks
python v11/run_all_checks.py

# Smoke test
python v10/operator_workspace.py smoke

# Trial registry
python v10/operator_workspace.py trials --path /path/to/registry.json

# Circuit breaker status
python v10/operator_workspace.py circuit --path /path/to/cb.json
```

## Operator Commands

### Status
```bash
python v10/operator_workspace.py status --root /path/to/state
```
Shows runtime status, queue health, belief state, concept coherence, cognitive pattern, and reflection state.

### Dashboard
```bash
python v10/operator_workspace.py dashboard \
  --root /path/to/state \
  --ledger /path/to/ledger.json \
  --benchmark /path/to/benchmark.json \
  --trial-log /path/to/trial-log.json
```
Full decision dashboard with status, beliefs, concepts, cognition, reflections, usage, benchmark, trial history, quality, recommendations, and policy tuning suggestions.

### Smoke Test
```bash
python v10/operator_workspace.py smoke
```
Verifies all core components are importable and functional. Runs in CI on every push.

### Usage
```bash
python v10/operator_workspace.py usage --ledger /path/to/ledger.json
```
Shows daily request/cost totals, per-provider breakdown, and ratio metrics.

### Trials
```bash
python v10/operator_workspace.py trials --path /path/to/registry.json
```
Lists all indexed trials with assessment, cost, and tags.

### Registry Search
```bash
python v10/operator_workspace.py registry-search \
  --path /path/to/registry.json \
  --tag hybrid \
  --assessment "healthy"
```
Search trials by tag or assessment.

### Circuit Breaker
```bash
python v10/operator_workspace.py circuit --path /path/to/cb.json
```
Shows circuit breaker state (closed/open/half_open), consecutive failures, and last failure timestamp.

## Core Architecture

```
Event
  → EventPrioritizer (priority)
  → AdaptiveModePolicy (mode)
  → ConsciousWakePolicy (wake action)
  → CostBudgetPolicy (budget band)
  → ModelRoutingPolicy (route decision)
  → Adapter (local/external/heuristic)
  → CircuitBreaker (external protection)
```

## Routing Policy

| Privacy | Budget | Mode | Urgency | Route |
|---|---|---|---|---|
| restricted | any | any | any | local |
| tight | tight | light | any | heuristic |
| normal | generous | focused/reflect | high | external |
| normal | normal | standard | normal | local |

## Circuit Breaker States

```
CLOSED (normal operation)
  → 3 consecutive failures → OPEN (external blocked)

OPEN (external blocked)
  → 60s cooldown → HALF-OPEN (probe allowed)

HALF-OPEN (probing)
  → 2 successes → CLOSED
  → 1 failure → OPEN
```

## Budget Bands

| Band | Spend Level | Max Depth |
|---|---|---|
| tight | minimum | heuristic |
| normal | moderate | standard |
| generous | maximum | focused/deep |

## Memory Budget

- Max total: 5 MB across beliefs, concepts, cognition, reflections
- Old beliefs (>7 days) auto-archived
- Dissolved concepts auto-compacted

## Quality Scoring

Output quality scored on 5 signals:
- **structure** (headers, bullets, sections)
- **logic** (reasoning words)
- **markers** (operation-specific keywords)
- **relevance** (off-topic detection)
- **length** (right-sized output)

## Alert Triggers

| Alert | Condition | Level |
|---|---|---|
| Circuit OPEN | 3 consecutive external failures | 🚨 alert |
| Budget exceeded | cost or requests > 80% of limit | 🚨 alert |
| Poison queue | items in poison queue | ⚠️ warning |
| Reflection needed | beliefs formed but no reflection | ℹ️ info |
| Trial complete | benchmark run finished | ✅ success |

## Common Issues

### "minimax unavailable: missing env MINIMAX_API_KEY"
External is disabled or API key not set. Set `MINIMAX_API_KEY` in environment or enable in config.

### "qwen unavailable: model loading disabled"
Local model loading disabled by config. System falls back to heuristic adapter automatically.

### Circuit OPEN
External provider is failing. Check provider status. After 60s cooldown, system will probe automatically.

### High memory usage
Run `MemoryBudgetEnforcer.archive_beliefs()` or `compact_concepts()` to reclaim space.
