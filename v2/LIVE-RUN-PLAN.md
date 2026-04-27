# Substrate Agent v2.8 Live Run Observation Plan

Status: Draft
Date: 2026-04-27

## Goal

Observe short real runtime behavior on this machine.

## What to watch

- startup behavior
- background loop stability
- growth log writes
- bridge artifacts
- CPU-only fallback behavior
- belief creation under live context

## Short observation window

1. start substrate agent
2. let it run briefly
3. inject a realistic absorb event
4. inspect:
   - belief files
   - growth logs
   - bridge state
   - status output

## Success criteria

- process starts and stops cleanly
- at least one growth log entry exists
- at least one belief can be created during live run
- no crash in short run
- output paths are sane

## Likely risk areas

- CPU inference delay
- prewarm causing long startup
- too little context polled by default
- no live events unless explicitly injected

## Output

- live-run result summary
- observed bottlenecks
- v2.8 recommendations
