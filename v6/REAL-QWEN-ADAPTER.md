# v6.1 Real Qwen Adapter

Status: Draft
Date: 2026-04-27

## Goal

Replace the mock Qwen adapter with a real local-transformers adapter shape that can plug into actual model loading later.

## Scope

- config-driven model name
- generation mode mapping
- unified prompt entrypoint
- safe fallback if transformers unavailable
- lightweight CPU-friendly defaults

## Modes

- `light` -> short generation
- `standard` -> normal generation
- `focused` -> more tokens, lower temperature
- `reflect` -> compact structured reflection

## Why

This is the bridge from architecture to actual runtime model execution.
