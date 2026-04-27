# v8.5 Deployable Runtime Config Loader

Status: Draft
Date: 2026-04-27

## Goal

Load runtime model-routing configuration from a real file instead of defaults embedded in code.

## Scope

- read JSON config file
- hydrate RuntimeConfig / ExternalBudget
- support missing fields with defaults
- make operator deployment repeatable
