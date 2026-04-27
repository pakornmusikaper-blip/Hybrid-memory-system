"""
Growth System — Belief Validation and Confidence Tracking

v2.1: Automatic belief validation, pattern recognition, and reality checking.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import uuid


class GrowthSystem:
    """
    Manages belief lifecycle and growth tracking.

    Responsibilities:
    - Validate beliefs against facts
    - Decay confidence over time
    - Detect belief contradictions
    - Track growth patterns
    """

    def __init__(self, memory_root: Path):
        self.memory_root = Path(memory_root)
        self.beliefs_dir = self.memory_root / "v2" / "substrate" / "own_memory" / "beliefs"
        self.patterns_dir = self.memory_root / "v2" / "substrate" / "own_memory" / "patterns"
        self.growth_dir = self.memory_root / "v2" / "substrate" / "own_memory" / "growth_log"

        for d in [self.beliefs_dir, self.patterns_dir, self.growth_dir]:
            d.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────────
    # BELIEF VALIDATION
    # ─────────────────────────────────────────────────────────────

    def validate_belief(self, belief: Dict, facts: List[Dict]) -> Dict:
        """
        Validate a belief against known facts.
        Returns updated belief with validation result.
        """
        result = {
            "status": "confirmed",
            "confidence_delta": 0.0,
            "contradictions": [],
            "supports": [],
        }

        belief_text = belief.get("statement", "").lower()

        for fact in facts:
            fact_text = fact.get("statement", "").lower()

            # Check for contradiction
            if self._is_contradiction(belief_text, fact_text):
                result["status"] = "contradicted"
                result["contradictions"].append(fact)
                result["confidence_delta"] -= 0.3

            # Check for support
            elif self._is_support(belief_text, fact_text):
                result["supports"].append(fact)
                result["confidence_delta"] += 0.1

        # Update belief confidence
        new_confidence = belief.get("confidence", 0.5) + result["confidence_delta"]
        new_confidence = max(0.0, min(1.0, new_confidence))  # Clamp to [0, 1]

        belief["confidence"] = new_confidence
        belief["last_validated"] = datetime.now().isoformat()
        belief["validation_result"] = result["status"]

        return belief

    def _is_contradiction(self, text1: str, text2: str) -> bool:
        """Check if two texts are contradictory."""
        # Simple negation detection
        negations = ["not", "no", "never", "neither", "nor", "none"]

        words1 = set(text1.split())
        words2 = set(text2.split())

        # If they share significant content but one has negation
        common = words1 & words2
        if len(common) > 3:  # Significant overlap
            for neg in negations:
                if neg in text1 and neg not in text2:
                    return True
                if neg in text2 and neg not in text1:
                    return True

        return False

    def _is_support(self, text1: str, text2: str) -> bool:
        """Check if text2 supports text1."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        # Significant word overlap suggests support
        common = words1 & words2
        return len(common) > max(5, len(words1) * 0.3)

    def validate_all_stale(self, days: int = 30) -> List[Dict]:
        """Validate all beliefs older than N days."""
        stale_beliefs = []
        cutoff = datetime.now() - timedelta(days=days)

        for path in self.beliefs_dir.glob("*.json"):
            with open(path) as f:
                belief = json.load(f)

            last_validated = belief.get("last_validated", belief.get("created", ""))
            if last_validated:
                last_date = datetime.fromisoformat(last_validated)
                if last_date < cutoff:
                    stale_beliefs.append(belief)

        # Validate each
        facts = self._gather_facts()
        validated = []

        for belief in stale_beliefs:
            updated = self.validate_belief(belief, facts)
            self._save_belief(updated)
            validated.append(updated)

        return validated

    def _gather_facts(self) -> List[Dict]:
        """Gather facts from sources and structured records."""
        facts = []

        # From structured records
        structured_dir = self.memory_root / "structured"
        if structured_dir.exists():
            for path in structured_dir.rglob("*.yaml"):
                try:
                    with open(path) as f:
                        data = yaml.safe_load(f)
                    if data.get("type") == "fact" or data.get("category") == "decisions":
                        facts.append(
                            {"statement": data.get("summary", str(data)), "source": str(path)}
                        )
                except:
                    pass

        return facts

    # ─────────────────────────────────────────────────────────────
    # CONFIDENCE DECAY
    # ─────────────────────────────────────────────────────────────

    def apply_decay(self, decay_factor: float = 0.9, age_threshold_days: int = 30) -> int:
        """
        Apply confidence decay to old beliefs.
        Returns number of beliefs decayed.
        """
        decayed = 0
        cutoff = datetime.now() - timedelta(days=age_threshold_days)

        for path in self.beliefs_dir.glob("*.json"):
            with open(path) as f:
                belief = json.load(f)

            last_validated = belief.get("last_validated", belief.get("created", ""))
            if last_validated:
                last_date = datetime.fromisoformat(last_validated)
                if last_date < cutoff:
                    # Apply decay
                    old_confidence = belief.get("confidence", 0.5)
                    new_confidence = old_confidence * decay_factor

                    belief["confidence"] = new_confidence
                    belief["status"] = (
                        "decaying" if new_confidence < 0.3 else belief.get("status", "active")
                    )
                    belief["decayed_at"] = datetime.now().isoformat()

                    self._save_belief(belief)
                    decayed += 1

        return decayed

    # ─────────────────────────────────────────────────────────────
    # CONTRADICTION DETECTION
    # ─────────────────────────────────────────────────────────────

    def detect_contradictions(self) -> List[Dict]:
        """
        Find pairs of beliefs that contradict each other.
        Returns list of contradiction pairs.
        """
        beliefs = self._get_all_beliefs()
        contradictions = []

        for i, b1 in enumerate(beliefs):
            for b2 in beliefs[i + 1 :]:
                if self._is_contradiction(
                    b1.get("statement", "").lower(), b2.get("statement", "").lower()
                ):
                    contradictions.append(
                        {
                            "belief1": b1["id"],
                            "belief2": b2["id"],
                            "statement1": b1.get("statement", "")[:100],
                            "statement2": b2.get("statement", "")[:100],
                        }
                    )

        return contradictions

    # ─────────────────────────────────────────────────────────────
    # PATTERN RECOGNITION
    # ─────────────────────────────────────────────────────────────

    def recognize_patterns(self, min_occurrences: int = 3) -> List[Dict]:
        """
        Scan beliefs and identify recurring patterns.
        Returns list of recognized patterns.
        """
        beliefs = self._get_all_beliefs()

        # Group by subject
        subject_groups = {}
        for belief in beliefs:
            subject = belief.get("subject", "unknown")
            if subject not in subject_groups:
                subject_groups[subject] = []
            subject_groups[subject].append(belief)

        # Find patterns
        patterns = []

        for subject, group in subject_groups.items():
            if len(group) >= min_occurrences:
                # Pattern: same subject, multiple beliefs
                avg_confidence = sum(b.get("confidence", 0) for b in group) / len(group)

                pattern = {
                    "id": str(uuid.uuid4())[:8],
                    "type": "subject_frequency",
                    "subject": subject,
                    "belief_count": len(group),
                    "avg_confidence": avg_confidence,
                    "created": datetime.now().isoformat(),
                }
                patterns.append(pattern)

        # Save patterns
        self._save_patterns(patterns)

        return patterns

    def _save_patterns(self, patterns: List[Dict]) -> None:
        """Save patterns to file."""
        if not patterns:
            return

        date = datetime.now().strftime("%Y-%m")
        path = self.patterns_dir / f"{date}.json"

        existing = []
        if path.exists():
            with open(path) as f:
                existing = json.load(f)

        # Merge, avoiding duplicates
        existing_ids = {p["id"] for p in existing}
        for p in patterns:
            if p["id"] not in existing_ids:
                existing.append(p)

        with open(path, "w") as f:
            json.dump(existing, f, indent=2)

    # ─────────────────────────────────────────────────────────────
    # GROWTH TRACKING
    # ─────────────────────────────────────────────────────────────

    def get_growth_summary(self) -> Dict:
        """Get summary of growth metrics."""
        beliefs = self._get_all_beliefs()

        active = [b for b in beliefs if b.get("status") == "active"]
        decaying = [b for b in beliefs if b.get("status") == "decaying"]
        contradicted = [b for b in beliefs if b.get("status") == "contradicted"]

        avg_confidence = sum(b.get("confidence", 0) for b in beliefs) / max(1, len(beliefs))

        # Load growth log
        growth_entries = []
        for path in sorted(self.growth_dir.glob("*.jsonl")):
            with open(path) as f:
                for line in f:
                    if line.strip():
                        growth_entries.append(json.loads(line))

        return {
            "total_beliefs": len(beliefs),
            "active_beliefs": len(active),
            "decaying_beliefs": len(decaying),
            "contradicted_beliefs": len(contradicted),
            "avg_confidence": round(avg_confidence, 3),
            "total_growth_entries": len(growth_entries),
            "patterns_identified": len(list(self.patterns_dir.glob("*.json"))),
        }

    def log_growth(self, operation: str, **kwargs) -> None:
        """Log a growth event."""
        entry = {"timestamp": datetime.now().isoformat(), "operation": operation, **kwargs}

        date = datetime.now().strftime("%Y-%m-%d")
        path = self.growth_dir / f"{date}.jsonl"

        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # ─────────────────────────────────────────────────────────────
    # UTILITIES
    # ─────────────────────────────────────────────────────────────

    def _get_all_beliefs(self) -> List[Dict]:
        """Get all beliefs."""
        beliefs = []
        for path in self.beliefs_dir.glob("*.json"):
            with open(path) as f:
                beliefs.append(json.load(f))
        return beliefs

    def _save_belief(self, belief: Dict) -> None:
        """Save a belief."""
        path = self.beliefs_dir / f"{belief['id']}.json"
        with open(path, "w") as f:
            json.dump(belief, f, indent=2)
