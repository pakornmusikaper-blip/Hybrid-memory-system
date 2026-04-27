"""
Consciousness Bridge — Bidirectional Communication Protocol

v2.2: Enables structured dialogue between conscious and subconscious layers.

The bridge allows:
- Conscious to query substrate for prepared context
- Substrate to surface "intuitions" to conscious
- Belief synchronization between layers
- Emergent understanding to flow both ways
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class MessageType(Enum):
    """Types of messages in the bridge protocol."""

    QUERY = "query"  # Conscious asks substrate
    RESPONSE = "response"  # Substrate responds
    INTUITION = "intuition"  # Substrate surfaces unexpected insight
    BELIEF_UPDATE = "belief_update"  # Belief was formed/updated
    VALIDATION_RESULT = "validation"  # Validation completed
    CORRECTION = "correction"  # Correction needed
    ANTICIPATION = "anticipation"  # Substrate prepared something


class ConsciousnessBridge:
    """
    Bridge for bidirectional communication between conscious and subconscious.

    Protocol:
    1. Conscious sends QUERY → Substrate responds with RESPONSE
    2. Substrate can proactively send INTUITION to conscious
    3. Belief updates flow both directions
    4. Validations and corrections maintain integrity
    """

    def __init__(self, memory_root: Path):
        self.memory_root = Path(memory_root)
        self.bridge_dir = (
            self.memory_root / "v2" / "substrate" / "own_memory" / "consciousness_bridge"
        )
        self.bridge_dir.mkdir(parents=True, exist_ok=True)

        # Message queues
        self.inbox_dir = self.bridge_dir / "inbox"
        self.outbox_dir = self.bridge_dir / "outbox"
        self.intuitions_dir = self.bridge_dir / "intuitions"

        for d in [self.inbox_dir, self.outbox_dir, self.intuitions_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────────
    # SENDING MESSAGES
    # ─────────────────────────────────────────────────────────────

    def send_query(self, query: str, context: Optional[Dict] = None) -> str:
        """
        Send a query from conscious to substrate.
        Returns message ID for tracking.
        """
        message = {
            "id": str(uuid.uuid4())[:8],
            "type": MessageType.QUERY.value,
            "query": query,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
        }

        self._save_message(message, self.outbox_dir / f"{message['id']}.json")
        return message["id"]

    def send_response(self, query_id: str, response: Dict, confidence: float) -> str:
        """
        Send response from substrate to conscious.
        """
        message = {
            "id": str(uuid.uuid4())[:8],
            "type": MessageType.RESPONSE.value,
            "query_id": query_id,
            "response": response,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "status": "delivered",
        }

        self._save_message(message, self.inbox_dir / f"{message['id']}.json")
        return message["id"]

    def surface_intuition(self, intuition: Dict) -> str:
        """
        Surface an intuition from substrate to conscious.
        An intuition is an unexpected insight that deserves attention.
        """
        message = {
            "id": str(uuid.uuid4())[:8],
            "type": MessageType.INTUITION.value,
            "intuition": intuition,
            "timestamp": datetime.now().isoformat(),
            "status": "pending_attention",
            "priority": intuition.get("priority", "normal"),
        }

        self._save_message(message, self.intuitions_dir / f"{message['id']}.json")
        return message["id"]

    def notify_belief_update(self, belief_id: str, update_type: str, details: Dict) -> str:
        """
        Notify about a belief update.
        """
        message = {
            "id": str(uuid.uuid4())[:8],
            "type": MessageType.BELIEF_UPDATE.value,
            "belief_id": belief_id,
            "update_type": update_type,  # formed, updated, contradicted, decayed
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "status": "logged",
        }

        self._save_message(message, self.bridge_dir / "belief_updates" / f"{message['id']}.json")
        return message["id"]

    def send_correction(self, belief_id: str, correction: Dict) -> str:
        """
        Send a correction from conscious to substrate.
        Used when conscious detects substrate belief is wrong.
        """
        message = {
            "id": str(uuid.uuid4())[:8],
            "type": MessageType.CORRECTION.value,
            "belief_id": belief_id,
            "correction": correction,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
        }

        self._save_message(message, self.outbox_dir / f"correction_{message['id']}.json")
        return message["id"]

    # ─────────────────────────────────────────────────────────────
    # RECEIVING MESSAGES
    # ─────────────────────────────────────────────────────────────

    def get_pending_intuitions(self, priority: Optional[str] = None) -> List[Dict]:
        """
        Get intuitions waiting for conscious attention.
        Optionally filter by priority.
        """
        intuitions = []

        for path in self.intuitions_dir.glob("*.json"):
            with open(path) as f:
                msg = json.load(f)

            if msg.get("status") == "pending_attention":
                if priority is None or msg.get("priority") == priority:
                    intuitions.append(msg)

        # Sort by priority and timestamp
        priority_order = {"high": 0, "normal": 1, "low": 2}
        intuitions.sort(
            key=lambda x: (priority_order.get(x.get("priority", "normal"), 1), x["timestamp"])
        )

        return intuitions

    def get_inbox(self, limit: int = 10) -> List[Dict]:
        """Get recent messages in inbox."""
        messages = []

        for path in sorted(
            self.inbox_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
        )[:limit]:
            with open(path) as f:
                messages.append(json.load(f))

        return messages

    def get_pending_queries(self) -> List[Dict]:
        """Get queries that haven't been responded to yet."""
        queries = []

        for path in self.outbox_dir.glob("*.json"):
            with open(path) as f:
                msg = json.load(f)

            if msg.get("type") == MessageType.QUERY.value and msg.get("status") == "pending":
                queries.append(msg)

        return queries

    def get_pending_corrections(self) -> List[Dict]:
        """Get corrections waiting to be processed."""
        corrections = []

        for path in self.outbox_dir.glob("correction_*.json"):
            with open(path) as f:
                corrections.append(json.load(f))

        return corrections

    # ─────────────────────────────────────────────────────────────
    # MESSAGE HANDLING
    # ─────────────────────────────────────────────────────────────

    def mark_delivered(self, message_id: str, direction: str = "inbox") -> None:
        """Mark a message as delivered."""
        if direction == "inbox":
            path = self.inbox_dir / f"{message_id}.json"
        else:
            path = self.outbox_dir / f"{message_id}.json"

        if path.exists():
            with open(path) as f:
                msg = json.load(f)
            msg["status"] = "delivered"
            with open(path, "w") as f:
                json.dump(msg, f, indent=2)

    def acknowledge_intuition(self, intuition_id: str) -> None:
        """Mark an intuition as acknowledged by conscious."""
        path = self.intuitions_dir / f"{intuition_id}.json"

        if path.exists():
            with open(path) as f:
                msg = json.load(f)
            msg["status"] = "acknowledged"
            msg["acknowledged_at"] = datetime.now().isoformat()
            with open(path, "w") as f:
                json.dump(msg, f, indent=2)

    def process_correction(self, correction_id: str, applied: bool) -> None:
        """Process a correction and mark it as applied or rejected."""
        path = self.outbox_dir / f"correction_{correction_id}.json"

        if path.exists():
            with open(path) as f:
                msg = json.load(f)
            msg["status"] = "applied" if applied else "rejected"
            msg["processed_at"] = datetime.now().isoformat()
            with open(path, "w") as f:
                json.dump(msg, f, indent=2)

    # ─────────────────────────────────────────────────────────────
    # UTILITIES
    # ─────────────────────────────────────────────────────────────

    def _save_message(self, message: Dict, path: Path) -> None:
        """Save a message to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(message, f, indent=2)

    def get_bridge_stats(self) -> Dict:
        """Get statistics about the bridge."""
        inbox_count = len(list(self.inbox_dir.glob("*.json")))
        outbox_count = len(list(self.outbox_dir.glob("*.json")))
        intuitions_count = len(list(self.intuitions_dir.glob("*.json")))

        pending_intuitions = len(self.get_pending_intuitions())
        pending_queries = len(self.get_pending_queries())

        return {
            "inbox_count": inbox_count,
            "outbox_count": outbox_count,
            "total_intuitions": intuitions_count,
            "pending_intuitions": pending_intuitions,
            "pending_queries": pending_queries,
        }

    def clear_old_messages(self, days: int = 7) -> int:
        """Clear messages older than N days. Returns count cleared."""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        cleared = 0

        for dir_path in [self.inbox_dir, self.outbox_dir]:
            for path in dir_path.glob("*.json"):
                with open(path) as f:
                    msg = json.load(f)

                msg_time = datetime.fromisoformat(msg["timestamp"])
                if msg_time < cutoff:
                    path.unlink()
                    cleared += 1

        return cleared


class IntuitionGenerator:
    """
    Generates intuitions from substrate observations.

    An intuition is generated when:
    - Substrate notices something unexpected
    - A pattern breaks expected behavior
    - Two unrelated concepts seem connected
    - Belief confidence changes significantly
    """

    def __init__(self, bridge: ConsciousnessBridge):
        self.bridge = bridge

    def generate(self, observation: Dict) -> Optional[Dict]:
        """
        Generate an intuition from an observation.
        Returns None if nothing worth surfacing.
        """
        intuition_type = observation.get("type")

        if intuition_type == "unexpected_pattern":
            return self._unexpected_pattern(observation)
        elif intuition_type == "belief_confidence_shift":
            return self._confidence_shift(observation)
        elif intuition_type == "connection_found":
            return self._connection_found(observation)
        elif intuition_type == "contradiction_detected":
            return self._contradiction(observation)

        return None

    def _unexpected_pattern(self, obs: Dict) -> Optional[Dict]:
        """Surface when an unexpected pattern is found."""
        pattern = obs.get("pattern", {})

        # Only surface high-confidence unexpected patterns
        if pattern.get("confidence", 0) < 0.7:
            return None

        return {
            "type": "intuition",
            "category": "unexpected_pattern",
            "title": f"Unexpected pattern in {pattern.get('subject', 'unknown')}",
            "description": f"Found {pattern.get('count', 0)} occurrences with avg confidence {pattern.get('avg_confidence', 0):.2f}",
            "data": pattern,
            "priority": "normal",
        }

    def _confidence_shift(self, obs: Dict) -> Optional[Dict]:
        """Surface when belief confidence changes significantly."""
        shift = obs.get("shift", 0)

        # Only surface large shifts
        if abs(shift) < 0.2:
            return None

        direction = "increased" if shift > 0 else "decreased"

        return {
            "type": "intuition",
            "category": "confidence_shift",
            "title": f"Belief confidence {direction}",
            "description": f"Belief about '{obs.get('subject', 'unknown')}' changed by {shift:+.2f}",
            "data": obs,
            "priority": "high" if abs(shift) > 0.4 else "normal",
        }

    def _connection_found(self, obs: Dict) -> Optional[Dict]:
        """Surface when an unexpected connection is found."""
        return {
            "type": "intuition",
            "category": "connection",
            "title": "Unexpected connection found",
            "description": f"Found link between '{obs.get('concept1', '')}' and '{obs.get('concept2', '')}'",
            "data": obs,
            "priority": "normal",
        }

    def _contradiction(self, obs: Dict) -> Optional[Dict]:
        """Surface contradictions immediately."""
        return {
            "type": "intuition",
            "category": "contradiction",
            "title": "Belief contradiction detected",
            "description": f"Beliefs '{obs.get('belief1', '')}' and '{obs.get('belief2', '')}' contradict each other",
            "data": obs,
            "priority": "high",
        }
