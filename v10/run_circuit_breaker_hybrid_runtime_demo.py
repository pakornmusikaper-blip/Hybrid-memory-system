#!/usr/bin/env python3
"""
Demo: circuit breaker standalone validation.
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
    root = Path('/tmp/v10_cb_runtime_demo')
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    cb = CircuitBreaker(root / 'cb.json', CircuitBreakerConfig(
        failures_to_open=3,
        cooldown_seconds=0.5,
        half_open_successes=2,
    ))

    print("=== CLOSED -> OPEN after 3 failures ===")
    for i in range(3):
        cb.record_failure()
        print(f"  failure {i+1}: state={cb.snapshot().state}, failures={cb._consecutive_failures}")

    print(f"\n=== OPEN: requests blocked ===")
    print(f"  allow_request={cb.allow_request()}")
    print(f"  state={cb.snapshot().state}")

    print("\n=== OPEN -> HALF-OPEN after cooldown ===")
    sleep(0.6)
    print(f"  allow_request={cb.allow_request()}")
    print(f"  state={cb.snapshot().state}")

    print("\n=== HALF-OPEN -> CLOSED after 2 successes ===")
    cb.record_success()
    print(f"  state={cb.snapshot().state}")
    cb.record_success()
    print(f"  state={cb.snapshot().state}")

    print("\n=== CLOSED again ===")
    print(f"  allow_request={cb.allow_request()}")


if __name__ == '__main__':
    main()
