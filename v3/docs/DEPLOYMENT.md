# Substrate v3 Deployment

## Target shapes
- laptop or workstation daemon
- server-side daemon
- OpenClaw-adjacent always-on background service

## Recommended progression
1. local foreground runtime
2. local supervised daemon
3. optional systemd service
4. optional OpenClaw integration wrapper

## Requirements
- Python runtime
- writable runtime state directory
- access to memory layers
- optional GPU for higher throughput

## Deployment concerns
- restart policy
- log rotation
- queue persistence
- runtime lockfile
- health file updates

## Important warning
Do not make v3 depend on live model success for survival.
The daemon must keep running in degraded mode when inference fails.
