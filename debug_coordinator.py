#!/usr/bin/env python3
"""
Debug script to test the coordinator directly and see what's happening.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from coordinator.coordinator_agent import CoordinatorAgent

async def test_coordinator():
    """Test the coordinator directly"""
    print("🧪 Testing Coordinator Agent Directly")
    print("=" * 50)
    
    try:
        # Initialize coordinator
        coordinator = CoordinatorAgent()
        print("✅ Coordinator initialized")
        
        # Test simple query
        query = "What are the main types of neural networks?"
        print(f"\n🔍 Testing query: {query}")
        
        response = await coordinator.process_user_query(query)
        
        print(f"\n📊 Response structure:")
        print(f"  Type: {type(response)}")
        print(f"  Keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        if isinstance(response, dict):
            for key, value in response.items():
                print(f"  {key}: {type(value)} = {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
        
        print(f"\n🎯 Synthesized answer: {response.get('synthesized_answer', 'NOT FOUND')}")
        print(f"🎯 Success: {response.get('success', 'NOT FOUND')}")
        print(f"🎯 Confidence: {response.get('confidence', 'NOT FOUND')}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_coordinator())
