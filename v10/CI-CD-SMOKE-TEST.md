# v10.x CI/CD Smoke Test Integration

Status: Draft
Date: 2026-04-27

## Goal

Run smoke test automatically on every push to guard against regressions.

## Workflow

- trigger on push to main / PR
- install dependencies
- run `python v10/smoke_test.py`
- fail the build if smoke test fails
