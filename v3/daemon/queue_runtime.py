"""
Substrate v3.5 queue/inbox runtime helpers.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class QueueRuntime:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.runtime_dir = self.root / "runtime"
        self.queues_dir = self.runtime_dir / "queues"
        self.inbox_dir = self.queues_dir / "inbox"
        self.outbox_dir = self.queues_dir / "outbox"
        self.processed_dir = self.queues_dir / "processed"
        self.failed_dir = self.queues_dir / "failed"
        self.duplicate_dir = self.queues_dir / "duplicates"
        for d in [
            self.inbox_dir,
            self.outbox_dir,
            self.processed_dir,
            self.failed_dir,
            self.duplicate_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def enqueue_inbox(self, payload: Dict) -> Path:
        name = payload.get("id") or datetime.now().strftime("%Y%m%d%H%M%S%f")
        path = self.inbox_dir / f"{name}.json"
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        return path

    def list_inbox(self) -> List[Path]:
        return sorted(self.inbox_dir.glob("*.json"))

    def process_next(self) -> Dict[str, object] | None:
        items = self.list_inbox()
        if not items:
            return None
        path = items[0]
        with open(path) as f:
            payload = json.load(f)

        payload_id = payload.get("id", path.stem)

        if self._already_processed(payload_id):
            duplicate_path = self.duplicate_dir / path.name
            path.rename(duplicate_path)
            return {
                "id": payload_id,
                "type": payload.get("type", "unknown"),
                "status": "duplicate",
                "processed_at": datetime.now().isoformat(),
                "summary": f"Skipped duplicate payload {payload_id}",
            }

        try:
            result = {
                "id": payload_id,
                "type": payload.get("type", "unknown"),
                "status": "processed",
                "processed_at": datetime.now().isoformat(),
                "summary": self._summarize(payload),
                "attempts": int(payload.get("attempts", 0)) + 1,
            }

            out_path = self.outbox_dir / f"{result['id']}.json"
            with open(out_path, "w") as f:
                json.dump(result, f, indent=2)

            processed_path = self.processed_dir / path.name
            path.rename(processed_path)
            return result
        except Exception as e:
            return self._handle_failure(path, payload, str(e))

    def _handle_failure(self, path: Path, payload: Dict, error: str) -> Dict[str, object]:
        attempts = int(payload.get("attempts", 0)) + 1
        payload["attempts"] = attempts
        payload["last_error"] = error
        payload["updated_at"] = datetime.now().isoformat()

        if attempts >= 3:
            fail_path = self.failed_dir / path.name
            with open(fail_path, "w") as f:
                json.dump(payload, f, indent=2)
            path.unlink(missing_ok=True)
            return {
                "id": payload.get("id", path.stem),
                "type": payload.get("type", "unknown"),
                "status": "failed",
                "processed_at": datetime.now().isoformat(),
                "summary": f"Failed after {attempts} attempts: {error}",
                "attempts": attempts,
            }

        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        return {
            "id": payload.get("id", path.stem),
            "type": payload.get("type", "unknown"),
            "status": "retry",
            "processed_at": datetime.now().isoformat(),
            "summary": f"Retry scheduled after error: {error}",
            "attempts": attempts,
        }

    def _already_processed(self, payload_id: str) -> bool:
        return (self.outbox_dir / f"{payload_id}.json").exists() or any(
            p.stem == payload_id for p in self.processed_dir.glob("*.json")
        )

    def _summarize(self, payload: Dict) -> str:
        if payload.get("type") == "query":
            return f"Handled query: {payload.get('query', '')[:120]}"
        if payload.get("type") == "correction":
            return f"Handled correction for belief {payload.get('belief_id', 'unknown')}"
        return f"Handled payload type {payload.get('type', 'unknown')}"

    def stats(self) -> Dict[str, int]:
        return {
            "inbox": len(list(self.inbox_dir.glob("*.json"))),
            "outbox": len(list(self.outbox_dir.glob("*.json"))),
            "processed": len(list(self.processed_dir.glob("*.json"))),
            "failed": len(list(self.failed_dir.glob("*.json"))),
            "duplicates": len(list(self.duplicate_dir.glob("*.json"))),
        }
