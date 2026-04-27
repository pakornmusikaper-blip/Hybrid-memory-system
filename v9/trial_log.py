#!/usr/bin/env python3
"""
v9.2 Persistent trial logs.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class TrialLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, report_summary: Dict, source_path: str | None = None):
        entries = self.read_all()
        entries.append({
            "ts": datetime.now().isoformat(),
            "source_path": source_path,
            "summary": report_summary,
        })
        self._write(entries)

    def read_all(self) -> List[Dict]:
        if not self.path.exists():
            return []
        with open(self.path) as f:
            return json.load(f)

    def latest(self) -> Dict | None:
        entries = self.read_all()
        return entries[-1] if entries else None

    def _write(self, entries: List[Dict]):
        with open(self.path, "w") as f:
            json.dump(entries[-200:], f, indent=2)
