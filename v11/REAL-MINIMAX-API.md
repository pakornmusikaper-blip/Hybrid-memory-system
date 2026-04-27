# v11.x Real MiniMax API Transport

Status: Draft
Date: 2026-04-27

## Goal

Replace the mock scaffold with real HTTP API transport.

## API Details

- Endpoint: `POST https://api.minimax.io/api/v1/text/chatcompletion_v2`
- Auth: `Bearer $MINIMAX_API_KEY`
- Model: `MiniMax-M2.7`
- Timeout: 30s
- Errors: timeout, rate-limit, auth-fail → fallback to heuristic
