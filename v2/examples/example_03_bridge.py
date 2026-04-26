#!/usr/bin/env python3
"""
Example 3: Consciousness Bridge

Demonstrates:
- Send query from conscious to substrate
- Check pending intuitions
- View bridge statistics
- Process corrections
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from substrate.agent.core import SubstrateAgent


def main():
    print("=" * 60)
    print("Substrate Agent - Example 3: Consciousness Bridge")
    print("=" * 60)
    
    memory_root = Path.home() / ".openclaw" / "workspace" / "knowledge-system"
    if not memory_root.exists():
        memory_root = Path(__file__).parent.parent.parent / "knowledge-system"
    
    agent = SubstrateAgent(memory_root)
    
    # Bridge statistics
    print("\n1. Bridge Statistics:")
    stats = agent.bridge.get_bridge_stats()
    print(f"   Inbox: {stats['inbox_count']}")
    print(f"   Outbox: {stats['outbox_count']}")
    print(f"   Pending intuitions: {stats['pending_intuitions']}")
    print(f"   Pending queries: {stats['pending_queries']}")
    
    # Pending intuitions
    print("\n2. Pending Intuitions:")
    intuitions = agent.bridge.get_pending_intuitions()
    if intuitions:
        print(f"   Found {len(intuitions)} intuitions:")
        for i in intuitions[:3]:
            print(f"   [{i['id']}] {i.get('title', 'Untitled')}")
            print(f"       Priority: {i.get('priority', 'normal')}")
    else:
        print("   No pending intuitions")
    
    # Send a query
    print("\n3. Sending a query to substrate...")
    query_id = agent.bridge.send_query(
        "What is the current state of memory system?",
        context={"source": "example_script"}
    )
    print(f"   Query sent: {query_id}")
    
    # Get pending queries
    pending = agent.bridge.get_pending_queries()
    print(f"   Pending queries: {len(pending)}")
    
    # Simulate receiving a response (in real use, substrate would respond)
    print("\n4. Simulating response...")
    response_id = agent.bridge.send_response(
        query_id=query_id,
        response={"content": "Memory system is operational"},
        confidence=0.85
    )
    print(f"   Response sent: {response_id}")
    
    # View inbox
    print("\n5. Inbox messages:")
    inbox = agent.bridge.get_inbox(limit=5)
    for msg in inbox:
        print(f"   [{msg['id']}] {msg['type']}: {msg.get('response', {}).get('content', '')[:50]}...")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
