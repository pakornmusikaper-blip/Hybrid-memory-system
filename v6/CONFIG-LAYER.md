# v6.5 Config Layer + External Budget Controls

Status: Draft
Date: 2026-04-27

## Goal

Make local/external model execution configurable and safe.

## Controls

- enable/disable local model
- enable/disable external model
- choose preferred local/external models
- API key env names
- daily external request limit
- daily external cost limit
- privacy mode defaults

## Safety

External models must be disabled by default.
All API keys come from environment variables, never hardcoded.
Budget limits should block routing before API calls are attempted.
