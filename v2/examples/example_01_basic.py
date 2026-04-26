#!/usr/bin/env python3
"""
Example 1: Basic Usage

Demonstrates:
- Initialize Substrate Agent
- Start background processing
- Query the agent
- Stop the agent
"""

import sys
from pathlib import Path

# Add v2 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from substrate.agent.core import SubstrateAgent


def main():
    print("=" * 60)
    print("Substrate Agent - Example 1: Basic Usage")
    print("=" * 60)
    
    # Find memory root
    memory_root = Path.home() / ".openclaw" / "workspace" / "knowledge-system"
    if not memory_root.exists():
        memory_root = Path(__file__).parent.parent.parent / "knowledge-system"
    
    print(f"\nMemory root: {memory_root}")
    
    # Initialize agent
    print("\n1. Initializing agent...")
    agent = SubstrateAgent(memory_root)
    
    # Start background processing
    print("\n2. Starting background processing...")
    agent.start()
    
    # Serve a query
    print("\n3. Serving a query...")
    result = agent.serve("What is the Hybrid Memory System?")
    print(f"   Source: {result['source']}")
    print(f"   Confidence: {result['confidence']}")
    
    # Get stats
    print("\n4. Agent statistics:")
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Stop
    print("\n5. Stopping agent...")
    agent.stop()
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
