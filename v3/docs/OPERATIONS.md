# Substrate v3 Operations

## Operator goals
- keep daemon alive
- know when it is degraded
- recover cleanly after crashes
- avoid silent stalls

## Basic operations
- start daemon
- stop daemon
- restart daemon
- inspect health.json
- inspect runtime logs
- inspect queue backlog

## Health checks
- last successful cycle timestamp
- consecutive errors
- fallback rate
- queue size
- last belief formed
- last intuition emitted

## Common degraded states
- model load failure
- repeated generation fallback
- stuck queue backlog
- no successful cycles for too long

## Recovery actions
1. check health.json
2. inspect logs
3. switch to degraded mode if needed
4. restart daemon
5. clear poison queue items if necessary
