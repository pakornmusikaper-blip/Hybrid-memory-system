"""
Substrate v3 health helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict


@dataclass
class HealthSnapshot:
    status: str
    mode: str
    cycles: int
    last_success: str | None
    consecutive_errors: int
    updated_at: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def classify_health(consecutive_errors: int, last_success: str | None) -> str:
    if consecutive_errors >= 5:
        return "failed"
    if consecutive_errors >= 3:
        return "degraded"
    if last_success is None:
        return "warm"
    return "healthy"


def make_health(mode: str, cycles: int, last_success: str | None, consecutive_errors: int) -> HealthSnapshot:
    return HealthSnapshot(
        status=classify_health(consecutive_errors, last_success),
        mode=mode,
        cycles=cycles,
        last_success=last_success,
        consecutive_errors=consecutive_errors,
        updated_at=datetime.now().isoformat(),
    )
