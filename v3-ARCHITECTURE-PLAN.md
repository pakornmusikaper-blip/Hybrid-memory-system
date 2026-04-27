# Substrate Agent v3 Architecture Plan

Status: Draft
Date: 2026-04-27

## Vision

Turn Substrate from a tested prototype into an always-on background daemon.

v2 proved:
- architecture works
- beliefs can be formed
- growth logs work
- bridge works
- short live run works

v3 should make Substrate feel alive continuously.

---

## Core Shift in v3

### v2
- script-driven
- manually started
- observation-oriented
- prototype runtime

### v3
- daemonized
- always-on lifecycle
- supervised runtime
- event-driven background cognition
- persistent operational state

---

## v3 Runtime Model

```text
┌──────────────────────────────────────────┐
│        Substrate Daemon Supervisor       │
│  start / stop / restart / health checks  │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│          Substrate Runtime Core          │
│  loop scheduler + event router + state   │
└────────────────────┬─────────────────────┘
                     │
     ┌───────────────┼────────────────┐
     │               │                │
┌────▼────┐   ┌──────▼──────┐   ┌─────▼─────┐
│ Ingest  │   │ Cognition    │   │ Outputs   │
│ Pollers │   │ Engine       │   │ & Bridge  │
└────┬────┘   └──────┬──────┘   └─────┬─────┘
     │               │                │
┌────▼────────────────▼────────────────▼────┐
│          Persistent State Store           │
│ beliefs / patterns / queues / runtime     │
└───────────────────────────────────────────┘
```

---

## v3 Components

### 1. Daemon Supervisor
Responsibility:
- start the daemon
- monitor health
- restart on crash
- expose pid/status/uptime

Possible forms:
- systemd service on Linux
- simple Python supervisor for portability
- OpenClaw cron or heartbeat companion mode

### 2. Runtime Core
Responsibility:
- maintain loop timing
- separate fast/slow tasks
- track runtime state
- control ingest, cognition, outputs

State examples:
- last successful cycle
- current mode
- backlog depth
- consecutive failures
- active model mode

### 3. Ingest Pollers
Responsibility:
- observe relevant memory changes
- watch structured/wiki/sources changes
- ingest queued conscious requests
- optionally watch external system outputs later

Poller types:
- file-change poller
- bridge queue poller
- scheduled review poller
- maintenance poller

### 4. Cognition Engine
Responsibility:
- weave context
- form beliefs
- validate beliefs
- refresh anticipations
- generate intuitions
- detect contradictions

Should support modes:
- fast heuristic mode
- local model mode
- deferred heavy mode

### 5. Outputs & Bridge
Responsibility:
- write bridge messages
- emit intuitions
- update growth logs
- record health warnings
- optionally notify conscious layer on important events

### 6. Persistent Runtime State
Responsibility:
- store daemon health
- store last checkpoints
- store queue offsets
- support safe restarts

Suggested files:
```text
substrate/runtime/
├── state.json
├── health.json
├── queues/
├── checkpoints/
└── locks/
```

---

## Scheduling Model

Use multiple cadences instead of one loop doing everything.

### Fast loop (every 10-30s)
- bridge queue polling
- light file checks
- health state update

### Medium loop (every 2-5 min)
- context weaving
- anticipation refresh
- recent change ingestion

### Slow loop (every 15-60 min)
- contradiction scans
- confidence decay checks
- pattern recognition
- cleanup / pruning

### Deep loop (every few hours)
- structural review
- heavy synthesis
- memory hygiene
- compaction / archival suggestions

---

## Runtime Modes

### Mode A: idle-watch
No urgent work. Keep polling lightly.

### Mode B: active-absorb
Recent changes detected. Ingest and weave.

### Mode C: reflective
Run deeper growth and pattern analysis.

### Mode D: degraded
Model unavailable or repeated failures. Use heuristic fallback and minimize load.

### Mode E: maintenance
Cleanup, decay checks, queue repair, log compaction.

---

## Health Model

Substrate should know whether it is healthy.

Metrics:
- uptime
- last successful cycle
- queue backlog size
- average cycle duration
- consecutive errors
- last belief formed time
- last intuition emitted time
- current device mode (cpu/cuda)
- fallback usage frequency

Health states:
- healthy
- warm
- degraded
- stalled
- failed

Example:
```json
{
  "status": "degraded",
  "uptime_seconds": 18342,
  "last_success": "2026-04-27T08:30:00",
  "consecutive_errors": 3,
  "device": "cpu",
  "fallback_rate": 0.72
}
```

---

## Queue Model

### Input queues
- conscious queries
- corrections
- ingest tasks
- scheduled reviews

### Output queues
- responses
- intuitions
- health warnings
- growth events

Need:
- queue persistence
- retry rules
- poison-item handling
- deduplication

---

## Safety / Stability Requirements

### 1. Never block forever on model generation
Use:
- watchdog timeout
- degraded fallback mode
- token caps

### 2. Avoid bridge spam
Use:
- intuition throttling
- priority thresholds
- collapse repeated events

### 3. Prevent belief explosion
Use:
- max beliefs per cycle
- merge similar beliefs
- confidence thresholds
- archive low-value beliefs

### 4. Survive restart cleanly
Use:
- runtime checkpoints
- file-based locks
- recoverable queues

---

## Suggested v3 File Layout

```text
v3/
├── daemon/
│   ├── supervisor.py
│   ├── service.py
│   ├── runtime.py
│   ├── scheduler.py
│   └── health.py
├── pollers/
│   ├── files.py
│   ├── bridge.py
│   └── reviews.py
├── cognition/
│   ├── engine.py
│   ├── beliefs.py
│   ├── patterns.py
│   ├── validation.py
│   └── intuitions.py
├── runtime/
│   ├── state.json
│   ├── health.json
│   ├── queues/
│   └── checkpoints/
├── configs/
│   ├── daemon.yaml
│   └── scheduling.yaml
└── docs/
    ├── OPERATIONS.md
    ├── HEALTH-MODEL.md
    └── DEPLOYMENT.md
```

---

## Migration Path from v2 to v3

### Phase 1
- keep v2 logic
- wrap it in runtime core
- add scheduler + state store

### Phase 2
- split loops by cadence
- add daemon supervisor
- add runtime health model

### Phase 3
- add robust queues
- add throttled intuitions
- add degraded mode automation

### Phase 4
- package deployment patterns
- optional systemd service
- optional OpenClaw integration layer

---

## First Concrete v3 Deliverables

1. `v3/daemon/runtime.py`
2. `v3/daemon/scheduler.py`
3. `v3/configs/daemon.yaml`
4. `v3/configs/scheduling.yaml`
5. `v3/docs/OPERATIONS.md`
6. `v3/docs/DEPLOYMENT.md`

---

## Recommendation

Build v3 as an operational runtime shell around the proven v2 cognition pieces.

Do not rewrite cognition first.
Wrap, schedule, supervise, and health-check it.
That is the shortest path to a truly alive substrate.
