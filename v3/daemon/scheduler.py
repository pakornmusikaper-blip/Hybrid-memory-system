"""
Substrate v3 scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List


@dataclass
class LoopTask:
    name: str
    interval_seconds: int
    last_run: datetime | None = None

    def due(self, now: datetime) -> bool:
        if self.last_run is None:
            return True
        return now - self.last_run >= timedelta(seconds=self.interval_seconds)

    def mark(self, now: datetime):
        self.last_run = now


class Scheduler:
    def __init__(self, config: Dict):
        scheduling = config.get("scheduling", {})
        self.tasks: List[LoopTask] = [
            LoopTask("fast", int(scheduling.get("fastLoopSeconds", 15))),
            LoopTask("medium", int(scheduling.get("mediumLoopSeconds", 180))),
            LoopTask("slow", int(scheduling.get("slowLoopSeconds", 1800))),
            LoopTask("deep", int(scheduling.get("deepLoopSeconds", 14400))),
        ]

    def due_tasks(self, now: datetime) -> List[LoopTask]:
        return [task for task in self.tasks if task.due(now)]
