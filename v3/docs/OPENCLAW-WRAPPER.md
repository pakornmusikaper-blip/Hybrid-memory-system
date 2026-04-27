# OpenClaw Wrapper Mode (v3.4)

## Goal

Let Substrate v3 run as a workspace-aware companion around the OpenClaw layout.

## What it detects

- `~/.openclaw/workspace`
- `~/.openclaw/workspace/knowledge-system`
- `~/.openclaw/workspace/hybrid-memory-system`
- `hybrid-memory-system/v3/configs`

## Commands

```bash
python v3/openclaw_wrapper.py info
python v3/openclaw_wrapper.py runtime-demo --cycles 2
python v3/openclaw_wrapper.py status
python v3/openclaw_wrapper.py start --cycles 20
python v3/openclaw_wrapper.py stop
```

## Why this matters

Before wrapper mode, v3 runtime existed mostly as a standalone daemon prototype.

With wrapper mode:
- the runtime understands the OpenClaw workspace shape
- it can target the real `knowledge-system` root directly
- daemon lifecycle commands become workspace aware

## Next likely step

Connect wrapper mode to queue/bridge artifacts under the real OpenClaw workspace and add a small operator command surface.
