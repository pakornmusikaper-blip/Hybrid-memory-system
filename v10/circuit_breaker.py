#!/usr/bin/env python3
"""
v10.x Circuit breaker for external provider protection.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    failures_to_open: int = 3
    cooldown_seconds: float = 60.0
    half_open_successes: int = 2


@dataclass
class CircuitBreakerSnapshot:
    state: str
    consecutive_failures: int
    consecutive_successes: int
    last_failure_ts: float | None
    opened_at: float | None
    half_open_successes: int

    def to_dict(self) -> Dict:
        return asdict(self)


class CircuitBreaker:
    def __init__(self, path: Path | None = None, config: CircuitBreakerConfig | None = None):
        self.path = Path(path) if path else None
        self.config = config or CircuitBreakerConfig()
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._last_failure_ts: float | None = None
        self._opened_at: float | None = None
        self._half_open_successes = 0
        self._half_open = False
        if self.path and self.path.exists():
            self._load()

    def record_success(self):
        if self._half_open:
            self._half_open_successes += 1
            if self._half_open_successes >= self.config.half_open_successes:
                self._closed()
        else:
            self._consecutive_failures = 0
            self._consecutive_successes += 1
        self._save()

    def record_failure(self):
        self._consecutive_failures += 1
        self._last_failure_ts = time.time()
        if self._half_open:
            self._open()
            return
        if self._consecutive_failures >= self.config.failures_to_open:
            self._open()
        self._save()

    def allow_request(self) -> bool:
        if self._opened_at is None and not self._half_open:
            return True
        if self._opened_at is not None and self._cooldown_elapsed():
            self._transition_to_half_open()
            return True
        if self._half_open:
            return True
        return False

    def snapshot(self) -> CircuitBreakerSnapshot:
        return CircuitBreakerSnapshot(
            state=self._current_state().value,
            consecutive_failures=self._consecutive_failures,
            consecutive_successes=self._consecutive_successes,
            last_failure_ts=self._last_failure_ts,
            opened_at=self._opened_at,
            half_open_successes=self._half_open_successes,
        )

    def _current_state(self) -> CircuitState:
        if self._half_open:
            return CircuitState.HALF_OPEN
        if self._opened_at is None:
            return CircuitState.CLOSED
        if self._cooldown_elapsed():
            return CircuitState.HALF_OPEN
        return CircuitState.OPEN

    def _open(self):
        self._opened_at = time.time()
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._half_open_successes = 0
        self._half_open = False

    def _transition_to_half_open(self):
        self._opened_at = None
        self._half_open = True
        self._half_open_successes = 0
        self._consecutive_successes = 0

    def _closed(self):
        self._opened_at = None
        self._half_open = False
        self._half_open_successes = 0
        self._consecutive_successes = 0
        self._consecutive_failures = 0

    def _cooldown_elapsed(self) -> bool:
        return (time.time() - self._opened_at) >= self.config.cooldown_seconds

    def _save(self):
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "consecutive_failures": self._consecutive_failures,
            "consecutive_successes": self._consecutive_successes,
            "last_failure_ts": self._last_failure_ts,
            "opened_at": self._opened_at,
            "half_open_successes": self._half_open_successes,
            "half_open": self._half_open,
        }
        with open(self.path, "w") as f:
            json.dump(data, f)

    def _load(self):
        data = json.loads(self.path.read_text())
        self._consecutive_failures = data.get("consecutive_failures", 0)
        self._consecutive_successes = data.get("consecutive_successes", 0)
        self._last_failure_ts = data.get("last_failure_ts")
        self._opened_at = data.get("opened_at")
        self._half_open_successes = data.get("half_open_successes", 0)
        self._half_open = data.get("half_open", False)
