#!/usr/bin/env python3
"""
Example 2: Working with Growth System

Demonstrates:
- Validate beliefs
- Check for contradictions
- Recognize patterns
- View growth summary
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from substrate.agent.core import SubstrateAgent


def main():
    print("=" * 60)
    print("Substrate Agent - Example 2: Growth System")
    print("=" * 60)

    memory_root = Path.home() / ".openclaw" / "workspace" / "knowledge-system"
    if not memory_root.exists():
        memory_root = Path(__file__).parent.parent.parent / "knowledge-system"

    agent = SubstrateAgent(memory_root)

    # Growth summary
    print("\n1. Growth Summary:")
    summary = agent.growth.get_growth_summary()
    print(f"   Total beliefs: {summary['total_beliefs']}")
    print(f"   Active: {summary['active_beliefs']}")
    print(f"   Decaying: {summary['decaying_beliefs']}")
    print(f"   Contradicted: {summary['contradicted_beliefs']}")
    print(f"   Average confidence: {summary['avg_confidence']:.3f}")

    # Detect contradictions
    print("\n2. Checking for contradictions...")
    contradictions = agent.growth.detect_contradictions()
    if contradictions:
        print(f"   Found {len(contradictions)} contradictions:")
        for c in contradictions[:3]:  # Show first 3
            print(f"   - {c['belief1']} <> {c['belief2']}")
    else:
        print("   No contradictions found!")

    # Validate stale beliefs
    print("\n3. Validating stale beliefs...")
    validated = agent.growth.validate_all_stale(days=7)  # 7 days for demo
    print(f"   Validated {len(validated)} beliefs")

    # Recognize patterns
    print("\n4. Recognizing patterns...")
    patterns = agent.growth.recognize_patterns(min_occurrences=2)
    if patterns:
        print(f"   Found {len(patterns)} patterns:")
        for p in patterns[:3]:
            print(f"   - {p['subject']}: {p['belief_count']} beliefs")
    else:
        print("   No patterns found (need more beliefs)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
