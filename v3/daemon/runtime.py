"""
Substrate v3 runtime skeleton.

Wraps proven v2 cognition pieces in an always-on runtime shell.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict


@dataclass
class RuntimeState:
    mode: str = "idle-watch"
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_success: str | None = None
    consecutive_errors: int = 0
    cycles: int = 0


class SubstrateRuntime:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.runtime_dir = self.root / "runtime"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.runtime_dir / "state.json"
        self.health_path = self.runtime_dir / "health.json"
        self.state = RuntimeState()

    def write_state(self):
        with open(self.state_path, "w") as f:
            json.dump(self.state.__dict__, f, indent=2)

    def write_health(self, status: str = "healthy"):
        payload: Dict[str, object] = {
            "status": status,
            "mode": self.state.mode,
            "cycles": self.state.cycles,
            "last_success": self.state.last_success,
            "consecutive_errors": self.state.consecutive_errors,
            "updated_at": datetime.now().isoformat(),
        }
        with open(self.health_path, "w") as f:
            json.dump(payload, f, indent=2)

    def tick(self):
        self.state.cycles += 1
        self.state.last_success = datetime.now().isoformat()
        self.write_state()
        self.write_health("healthy")

    def run_foreground(self, cycles: int = 3, sleep_seconds: int = 1):
        for _ in range(cycles):
            self.tick()
            time.sleep(sleep_seconds)


if __name__ == "__main__":
    runtime = SubstrateRuntime(Path.cwd())
    runtime.run_foreground()
