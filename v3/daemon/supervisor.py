"""
Substrate v3 supervisor (v3.2).
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict


class Supervisor:
    def __init__(self, root: Path, config_dir: Path):
        self.root = Path(root)
        self.config_dir = Path(config_dir)
        self.runtime_dir = self.root / "runtime"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.pid_path = self.runtime_dir / "substrate.pid"
        self.lock_path = self.runtime_dir / "substrate.lock"
        self.stdout_path = self.runtime_dir / "supervisor.out.log"

    def _read_pid(self) -> int | None:
        if not self.pid_path.exists():
            return None
        try:
            return int(self.pid_path.read_text().strip())
        except Exception:
            return None

    def _is_running(self, pid: int | None) -> bool:
        if pid is None:
            return False
        proc_path = Path(f"/proc/{pid}")
        if not proc_path.exists():
            return False
        stat_path = proc_path / "stat"
        try:
            if stat_path.exists():
                parts = stat_path.read_text().split()
                if len(parts) > 2 and parts[2] == "Z":
                    return False
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def start(self, cycles: int = 20, sleep_seconds: int = 1) -> Dict[str, object]:
        pid = self._read_pid()
        if self._is_running(pid):
            return {"started": False, "reason": "already-running", "pid": pid}

        self.lock_path.write_text("locked\n")
        script = Path(__file__).resolve().parent.parent / "run_runtime_daemon.py"
        with open(self.stdout_path, "ab") as out:
            proc = subprocess.Popen(
                [sys.executable, str(script), str(self.root), str(self.config_dir), str(cycles), str(sleep_seconds)],
                stdout=out,
                stderr=out,
                start_new_session=True,
            )
        self.pid_path.write_text(str(proc.pid))
        return {"started": True, "pid": proc.pid}

    def stop(self) -> Dict[str, object]:
        pid = self._read_pid()
        if not self._is_running(pid):
            self._cleanup_stale()
            return {"stopped": False, "reason": "not-running"}

        os.kill(pid, signal.SIGTERM)
        for _ in range(10):
            time.sleep(0.2)
            if not self._is_running(pid):
                break
        if self._is_running(pid):
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.2)
        self._cleanup_stale()
        return {"stopped": not self._is_running(pid), "pid": pid}

    def status(self) -> Dict[str, object]:
        pid = self._read_pid()
        running = self._is_running(pid)
        if not running:
            self._cleanup_stale()
            pid = self._read_pid()
        return {
            "running": running,
            "pid": pid,
            "pidFile": str(self.pid_path),
            "lockFile": str(self.lock_path),
            "stdoutLog": str(self.stdout_path),
        }

    def _cleanup_stale(self):
        pid = self._read_pid()
        if pid is None or not self._is_running(pid):
            if self.pid_path.exists():
                self.pid_path.unlink()
            if self.lock_path.exists():
                self.lock_path.unlink()
