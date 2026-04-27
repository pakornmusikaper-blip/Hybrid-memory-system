"""
Substrate v3 runtime implementation (v3.1).

Wraps proven v2 cognition pieces in an always-on runtime shell.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import yaml

from .health import make_health
from .scheduler import Scheduler


@dataclass
class RuntimeState:
    mode: str = "idle-watch"
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_success: str | None = None
    consecutive_errors: int = 0
    cycles: int = 0
    last_tasks: List[str] = field(default_factory=list)


class SubstrateRuntime:
    def __init__(self, root: Path, config_dir: Path | None = None):
        self.root = Path(root)
        self.runtime_dir = self.root / "runtime"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.runtime_dir / "state.json"
        self.health_path = self.runtime_dir / "health.json"
        self.log_path = self.runtime_dir / "runtime.log"
        self.state = RuntimeState()

        if config_dir is None:
            config_dir = Path(__file__).resolve().parent.parent / "configs"
        self.config_dir = Path(config_dir)
        self.daemon_config = self._load_yaml(self.config_dir / "daemon.yaml")
        self.scheduling_config = self._load_yaml(self.config_dir / "scheduling.yaml")
        self.scheduler = Scheduler(self.scheduling_config)

    def _load_yaml(self, path: Path) -> Dict:
        with open(path) as f:
            return yaml.safe_load(f)

    def log(self, message: str):
        line = f"[{datetime.now().isoformat()}] {message}\n"
        with open(self.log_path, "a") as f:
            f.write(line)

    def write_state(self):
        with open(self.state_path, "w") as f:
            json.dump(asdict(self.state), f, indent=2)

    def write_health(self):
        payload = make_health(
            mode=self.state.mode,
            cycles=self.state.cycles,
            last_success=self.state.last_success,
            consecutive_errors=self.state.consecutive_errors,
        ).to_dict()
        with open(self.health_path, "w") as f:
            json.dump(payload, f, indent=2)

    def run_due_tasks(self):
        now = datetime.now()
        due = self.scheduler.due_tasks(now)
        task_names = []
        for task in due:
            task_names.append(task.name)
            task.mark(now)
            self.log(f"task:{task.name}")
        self.state.last_tasks = task_names
        return task_names

    def tick(self):
        self.state.cycles += 1
        try:
            task_names = self.run_due_tasks()
            self.state.last_success = datetime.now().isoformat()
            self.state.consecutive_errors = 0
            self.state.mode = "active-absorb" if task_names else "idle-watch"
            self.write_state()
            self.write_health()
        except Exception as e:
            self.state.consecutive_errors += 1
            self.state.mode = "degraded"
            self.log(f"error:{e}")
            self.write_state()
            self.write_health()

    def run_foreground(self, cycles: int = 5, sleep_seconds: int = 1):
        self.log("runtime:start")
        for _ in range(cycles):
            self.tick()
            time.sleep(sleep_seconds)
        self.log("runtime:stop")


if __name__ == "__main__":
    runtime = SubstrateRuntime(Path.cwd())
    runtime.run_foreground()
