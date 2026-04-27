#!/usr/bin/env python3
"""
OpenClaw wrapper mode for Substrate v3.4.

Workspace-aware launcher that discovers the OpenClaw workspace layout
and starts the runtime/supervisor against the knowledge-system root.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from daemon.runtime import SubstrateRuntime
from daemon.supervisor import Supervisor


def detect_workspace() -> dict:
    workspace = Path.home() / ".openclaw" / "workspace"
    knowledge_root = workspace / "knowledge-system"
    hybrid_root = workspace / "hybrid-memory-system"
    v3_root = hybrid_root / "v3"
    return {
        "workspace": workspace,
        "knowledge_root": knowledge_root,
        "hybrid_root": hybrid_root,
        "v3_root": v3_root,
        "config_dir": v3_root / "configs",
    }


def cmd_info() -> None:
    info = detect_workspace()
    print(
        json.dumps(
            {k: str(v) for k, v in info.items()},
            indent=2,
        )
    )


def cmd_runtime_demo(cycles: int, sleep_seconds: int) -> None:
    info = detect_workspace()
    runtime = SubstrateRuntime(info["knowledge_root"], info["config_dir"])
    runtime.run_foreground(cycles=cycles, sleep_seconds=sleep_seconds)
    print(json.dumps({"mode": "runtime-demo", "cycles": cycles, "root": str(info["knowledge_root"])}))


def cmd_supervisor_status() -> None:
    info = detect_workspace()
    supervisor = Supervisor(info["knowledge_root"], info["config_dir"])
    print(json.dumps(supervisor.status(), indent=2))


def cmd_supervisor_start(cycles: int, sleep_seconds: int) -> None:
    info = detect_workspace()
    supervisor = Supervisor(info["knowledge_root"], info["config_dir"])
    print(json.dumps(supervisor.start(cycles=cycles, sleep_seconds=sleep_seconds), indent=2))


def cmd_supervisor_stop() -> None:
    info = detect_workspace()
    supervisor = Supervisor(info["knowledge_root"], info["config_dir"])
    print(json.dumps(supervisor.stop(), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Substrate v3.4 OpenClaw wrapper")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("info", help="Show detected OpenClaw workspace paths")

    p_demo = sub.add_parser("runtime-demo", help="Run foreground runtime demo against OpenClaw workspace")
    p_demo.add_argument("--cycles", type=int, default=2)
    p_demo.add_argument("--sleep", type=int, default=1)

    p_status = sub.add_parser("status", help="Show supervisor status against OpenClaw workspace")

    p_start = sub.add_parser("start", help="Start supervised runtime against OpenClaw workspace")
    p_start.add_argument("--cycles", type=int, default=20)
    p_start.add_argument("--sleep", type=int, default=1)

    sub.add_parser("stop", help="Stop supervised runtime against OpenClaw workspace")

    args = parser.parse_args()

    if args.command == "info":
        cmd_info()
    elif args.command == "runtime-demo":
        cmd_runtime_demo(args.cycles, args.sleep)
    elif args.command == "status":
        cmd_supervisor_status()
    elif args.command == "start":
        cmd_supervisor_start(args.cycles, args.sleep)
    elif args.command == "stop":
        cmd_supervisor_stop()


if __name__ == "__main__":
    main()
