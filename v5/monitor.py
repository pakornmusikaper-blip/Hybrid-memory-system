#!/usr/bin/env python3
"""
Consciousness Monitor CLI — ดูสุขภาพจิตของ Substrate ง่ายๆ

ใช้: python monitor.py <runtime_root>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def status_panel(root: Path) -> str:
    runtime_dir = root
    queue_dir = runtime_dir / "queue"

    state = read_json(runtime_dir / "state.json")
    health = read_json(runtime_dir / "health.json")

    # queue counts
    def count(name: str) -> int:
        p = queue_dir / name
        if not p.exists():
            return 0
        return len(list(p.glob("*.json")))

    inbox = count("inbox")
    outbox = count("outbox")
    processed = count("processed")
    poison = count("poison")

    # status
    errors = health.get("consecutive_errors", 0)
    mode = state.get("mode", "unknown")
    cycles = state.get("cycles", 0)
    last = state.get("last_success", "never")

    if errors >= 3:
        status = "🔴 CRITICAL"
    elif errors >= 1:
        status = "🟡 DEGRADED"
    else:
        status = "🟢 ALIVE"

    lines = [
        f"{'='*50}",
        f"  SUBSTRATE CONSCIOUSNESS MONITOR",
        f"{'='*50}",
        f"",
        f"Status  : {status}",
        f"Mode    : {mode}",
        f"Cycles  : {cycles}",
        f"Last OK : {last or 'unknown'}",
        f"",
        f"── Queue ──────────────────────────────────",
        f"  inbox     : {inbox}",
        f"  outbox    : {outbox}",
        f"  processed : {processed}",
        f"  poison    : {poison}",
        f"",
    ]

    # alerts
    if errors >= 3:
        lines.append(f"  ⚠️  {errors} consecutive errors — CRITICAL")
    elif errors >= 1:
        lines.append(f"  ⚠️  {errors} consecutive errors")

    if inbox >= 10:
        lines.append(f"  ⚠️  inbox pressure high ({inbox} items)")
    if poison >= 1:
        lines.append(f"  ⚠️  {poison} poison items need attention")

    if errors == 0 and inbox < 10 and poison == 0:
        lines.append(f"  ✅ all clear")

    lines.append(f"")
    return "\n".join(lines)


def beliefs_panel(root: Path) -> str:
    """Read belief health from runtime/memory/beliefs.json if it exists."""
    belief_path = root / "memory" / "beliefs.json"
    if not belief_path.exists():
        return "  (no belief file found)\n"

    beliefs = read_json(belief_path)
    if isinstance(beliefs, list):
        total = len(beliefs)
        stages = {}
        for b in beliefs:
            s = b.get("stage", "unknown")
            stages[s] = stages.get(s, 0) + 1
        confs = [b.get("confidence", 0) for b in beliefs if "confidence" in b]
        avg_conf = sum(confs) / max(1, len(confs))
    else:
        total = beliefs.get("total", 0)
        stages = beliefs.get("by_stage", {})
        avg_conf = beliefs.get("avg_confidence", 0)

    lines = [
        f"── Belief Health ──────────────────────────",
        f"  total    : {total}",
        f"  stages   : {stages}",
        f"  avg conf : {avg_conf:.3f}",
        f"",
    ]
    return "\n".join(lines)


def concepts_panel(root: Path) -> str:
    """Read concept health from runtime/memory/concepts.json if it exists."""
    concepts_path = root / "memory" / "concepts.json"
    if not concepts_path.exists():
        return "  (no concepts file found)\n"

    concepts = read_json(concepts_path)
    if isinstance(concepts, list):
        total = len(concepts)
        stages = {}
        for c in concepts:
            s = c.get("stage", "unknown")
            stages[s] = stages.get(s, 0) + 1
    else:
        total = concepts.get("total", 0)
        stages = concepts.get("by_stage", {})

    lines = [
        f"── Concept Coherence ───────────────────────",
        f"  total  : {total}",
        f"  stages : {stages}",
        f"",
    ]
    return "\n".join(lines)


def cognition_panel(root: Path) -> str:
    """Read cognition history from runtime/cognition.json if it exists."""
    cog_path = root / "runtime" / "cognition.json"
    if not cog_path.exists():
        return "  (no cognition history found)\n"

    cog = read_json(cog_path)
    modes = cog.get("mode_distribution", {})
    wakes = cog.get("wake_history", [])
    dominant = max(modes, key=modes.get) if modes else "unknown"
    recent = wakes[-20:] if len(wakes) > 20 else wakes
    wake_ratio = sum(1 for w in recent if w == "wake") / max(1, len(recent))

    lines = [
        f"── Cognitive Pattern ───────────────────────",
        f"  dominant mode : {dominant}",
        f"  modes used    : {len(modes)}",
        f"  wake ratio    : {wake_ratio:.2f} ({sum(1 for w in recent if w=='wake')}/{len(recent)})",
        f"",
    ]
    return "\n".join(lines)


def reflections_panel(root: Path) -> str:
    reflections_path = root / "memory" / "reflections.json"
    if not reflections_path.exists():
        return "  (no reflections file found)\n"

    reflections = read_json(reflections_path)
    total = len(reflections) if isinstance(reflections, list) else 0
    latest = reflections[-1] if total else {}
    summary = latest.get("summary", "") if isinstance(latest, dict) else ""
    trigger = latest.get("trigger", "unknown") if isinstance(latest, dict) else "unknown"
    lines = [
        f"── Reflection State ───────────────────────",
        f"  total reflections : {total}",
        f"  latest trigger    : {trigger}",
        f"  latest summary    : {summary[:120]}",
        f"",
    ]
    return "\n".join(lines)


def full_report(root: Path) -> str:
    lines = [
        status_panel(root),
        beliefs_panel(root),
        concepts_panel(root),
        cognition_panel(root),
        reflections_panel(root),
        f"{'='*50}",
        f"  Generated: {datetime.now().isoformat()}",
        f"{'='*50}",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Substrate Consciousness Monitor")
    parser.add_argument("root", help="runtime root path (เช่น /tmp/runtime)")
    parser.add_argument("--json", action="store_true", help="output as JSON")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"❌ path not found: {root}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        output = {
            "status": status_panel(root),
            "beliefs": beliefs_panel(root),
            "concepts": concepts_panel(root),
            "cognition": cognition_panel(root),
        }
        print(json.dumps(output, indent=2))
    else:
        print(full_report(root))


if __name__ == "__main__":
    main()