#!/usr/bin/env python3
"""
Substrate Agent Demo — Test with real Qwen model
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "v2"))

from substrate.agent.core import SubstrateAgent


def main():
    print("=" * 60)
    print("Substrate Agent Demo — With Real Qwen Model")
    print("=" * 60)
    
    # Memory root
    memory_root = Path.home() / ".openclaw" / "workspace" / "knowledge-system"
    if not memory_root.exists():
        memory_root = Path.home() / ".openclaw" / "workspace"
    
    # Config path (in hybrid-memory-system v2)
    v2_root = Path(__file__).parent
    config_path = v2_root / "substrate" / "config" / "default.yaml"
    
    print(f"\nMemory root: {memory_root}")
    print(f"Config: {config_path}")
    
    # Initialize agent
    agent = SubstrateAgent(memory_root, config_path)
    
    # Load model (this will take a moment)
    print("\nLoading model...")
    agent.load_model()
    print("Model loaded!")
    
    # Test 1: Serve a query
    print("\n" + "=" * 60)
    print("Test 1: Serve a query")
    print("=" * 60)
    result = agent.serve("What do you know about the user Pakorn?")
    print(f"\nSource: {result['source']}")
    print(f"Confidence: {result['confidence']}")
    print(f"\nWoven content:\n{result['data'].get('woven_content', '')[:500]}")
    
    # Test 2: Absorb new context
    print("\n" + "=" * 60)
    print("Test 2: Absorb new context")
    print("=" * 60)
    context = {
        "source": "demo_test",
        "content": "The user Pakorn is interested in AI memory systems and autonomous agents. They are working on a project to build a Hybrid Memory System with a Substrate Agent that uses Qwen 1.5B.",
        "scenario": "user_interest_ai"
    }
    agent.absorb(context)
    print("Context absorbed!")
    
    # Test 3: Get beliefs
    print("\n" + "=" * 60)
    print("Test 3: Get beliefs")
    print("=" * 60)
    beliefs = agent.get_beliefs()
    print(f"Total beliefs: {len(beliefs)}")
    for b in beliefs[-3:]:  # Show last 3
        print(f"\n[{b['id']}] {b.get('statement', '')[:100]}")
        print(f"   Confidence: {b.get('confidence', 0):.2f} | Status: {b.get('status', 'unknown')}")
    
    # Test 4: Stats
    print("\n" + "=" * 60)
    print("Test 4: Statistics")
    print("=" * 60)
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✓ Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
