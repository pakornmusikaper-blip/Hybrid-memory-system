#!/usr/bin/env python3
"""
Substrate v3.8 operator surface.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


class OperatorSurface:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.runtime_dir = self.root / "runtime"
        self.queues_dir = self.runtime_dir / "queues"

    def status(self) -> dict:
        state = self._read_json(self.runtime_dir / "state.json")
        health = self._read_json(self.runtime_dir / "health.json")
        return {"state": state, "health": health}

    def queue_stats(self) -> dict:
        return {
            "inbox": self._count("inbox"),
            "outbox": self._count("outbox"),
            "processed": self._count("processed"),
            "failed": self._count("failed"),
            "duplicates": self._count("duplicates"),
            "poison": self._count("poison"),
        }

    def list_poison(self) -> list[dict]:
        items = []
        for path in sorted((self.queues_dir / "poison").glob("*.json")):
            payload = self._read_json(path)
            items.append({"file": path.name, "payload": payload})
        return items

    def retry_poison(self, filename: str) -> dict:
        src = self.queues_dir / "poison" / filename
        if not src.exists():
            return {"ok": False, "reason": "not-found", "file": filename}

        payload = self._read_json(src)
        payload["attempts"] = 0
        payload.pop("last_error", None)
        payload.pop("not_before", None)

        dst = self.queues_dir / "inbox" / filename
        with open(dst, "w") as f:
            json.dump(payload, f, indent=2)
        src.unlink()
        return {"ok": True, "retried": filename}

    def drain_outbox(self) -> list[dict]:
        drained = []
        outbox = self.queues_dir / "outbox"
        for path in sorted(outbox.glob("*.json")):
            drained.append(self._read_json(path))
        return drained

    def _count(self, name: str) -> int:
        return len(list((self.queues_dir / name).glob("*.json")))

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        with open(path) as f:
            return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Substrate v3.8 operator surface")
    parser.add_argument("root", help="runtime root path")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("queue-stats")
    sub.add_parser("poison-list")
    retry = sub.add_parser("poison-retry")
    retry.add_argument("filename")
    sub.add_parser("outbox-drain")

    args = parser.parse_args()
    ops = OperatorSurface(Path(args.root))

    if args.command == "status":
        print(json.dumps(ops.status(), indent=2))
    elif args.command == "queue-stats":
        print(json.dumps(ops.queue_stats(), indent=2))
    elif args.command == "poison-list":
        print(json.dumps(ops.list_poison(), indent=2))
    elif args.command == "poison-retry":
        print(json.dumps(ops.retry_poison(args.filename), indent=2))
    elif args.command == "outbox-drain":
        print(json.dumps(ops.drain_outbox(), indent=2))


if __name__ == "__main__":
    main()
