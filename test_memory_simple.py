#!/usr/bin/env python3
"""Simple test for memory agent functionality"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").absolute()))

def test_memory_basic():
    """Basic memory agent test"""
    try:
        from memory.memory_agent import MemoryAgent
        
        print("Creating MemoryAgent...")
        memory = MemoryAgent()
        
        print("Storing test data...")
        memory.store_conversation("user", "What is AI?", "AI is artificial intelligence")
        
        print("Searching memory...")
        results = memory.search_memory("AI", max_results=1)
        
        print(f"Found {len(results)} results")
        if results:
            print(f"Result: {results[0]}")
        
        print("✅ Memory agent test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Memory agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_memory_basic()
