# v6.0 Model Adapter Layer

Status: Draft
Date: 2026-04-27

## Goal

Decouple Substrate cognition from any single model backend.

## Why

Substrate should keep its memory, prioritization, wake policy, budget policy, and reflection logic even if the model changes.

## Design

```text
Substrate pipeline
  -> ModelAdapter interface
      -> QwenAdapter
      -> LlamaAdapter
      -> OpenAIAdapter
      -> HeuristicAdapter
```

## Interface

Core methods:
- `generate(prompt, mode)`
- `summarize(text)`
- `reflect(context)`
- `health()`

## Requirements

- consistent return shape
- explicit model name/provider
- timeout-safe failure handling
- heuristic fallback remains available

## Benefit

This makes model swap a configuration change, not an architectural rewrite.
