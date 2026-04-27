# Circuit Breaker

Status: Draft
Date: 2026-04-27

## Goal

Protect the runtime from cascading failures when the external provider is unstable.

## States

```
CLOSED (normal) -> failure threshold -> OPEN (blocking external)
OPEN -> cooldown elapses -> HALF-OPEN (probe)
HALF-OPEN -> success -> CLOSED
HALF-OPEN -> failure -> OPEN
```

## Thresholds

- failures to open: 3
- cooldown seconds: 60
- half-open success threshold: 2
