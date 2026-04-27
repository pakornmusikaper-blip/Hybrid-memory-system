#!/usr/bin/env python3
"""
Demo for circuit breaker.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from time import sleep

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v10.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState


def main():
    root = Path('/tmp/v10_circuit_breaker_demo')
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    cb = CircuitBreaker(root / 'circuit-breaker.json', CircuitBreakerConfig(
        failures_to_open=3,
        cooldown_seconds=0.5,
        half_open_successes=2,
    ))

    print("=== CLOSED: record 2 failures (below threshold) ===")
    cb.record_failure()
    cb.record_failure()
    print(f"  state={cb.snapshot().state}")

    print("=== CLOSED -> OPEN: 3rd failure hits threshold ===")
    cb.record_failure()
    snap = cb.snapshot()
    print(f"  state={snap.state}, opened_at={snap.opened_at}")

    print("=== OPEN: request blocked while open ===")
    print(f"  allow_request={cb.allow_request()}")

    print("=== OPEN -> HALF-OPEN: after cooldown ===")
    sleep(0.6)
    print(f"  allow_request={cb.allow_request()}")
    print(f"  state={cb.snapshot().state}")

    print("=== HALF-OPEN: 1st success ===")
    cb.record_success()
    print(f"  state={cb.snapshot().state}")

    print("=== HALF-OPEN -> CLOSED: 2nd success ===")
    cb.record_success()
    print(f"  state={cb.snapshot().state}")

    print("=== CLOSED -> OPEN: 3 failures in new window ===")
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    print(f"  state={cb.snapshot().state}")


if __name__ == '__main__':
    main()
