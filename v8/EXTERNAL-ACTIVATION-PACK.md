# v8.2 External Activation Pack

Status: Draft
Date: 2026-04-27

## Goal

Prepare a safe, operator-friendly path to enable external models for real.

## Includes

- environment validation
- config validation
- budget guard validation
- ledger path validation
- dry-run activation check
- smoke test path

## Safety

No API call should happen until:
- external is enabled
- API key exists
- budget limits exist
- ledger path is writable
