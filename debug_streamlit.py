#!/usr/bin/env python3
"""
Debug script to test what the Streamlit app is actually receiving and displaying.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from coordinator.coordinator_agent import CoordinatorAgent

async def test_streamlit_response():
    """Test what the Streamlit app would receive"""
    print("🧪 Testing Streamlit Response Processing")
    print("=" * 50)
    
    try:
        # Initialize coordinator (like Streamlit does)
        coordinator = CoordinatorAgent()
        print("✅ Coordinator initialized")
        
        # Test query
        query = "What are the main types of neural networks?"
        print(f"\n🔍 Testing query: {query}")
        
        # Process query (like Streamlit does)
        response = await coordinator.process_user_query(query)
        
        print(f"\n📊 Raw Response from Coordinator:")
        print(f"  Type: {type(response)}")
        print(f"  Keys: {list(response.keys())}")
        
        # Check each field
        for key, value in response.items():
            print(f"  {key}: {type(value)} = {repr(value)}")
        
        # Test what Streamlit would display
        print(f"\n🎯 What Streamlit would display:")
        print(f"  synthesized_answer: {response.get('synthesized_answer', 'NOT FOUND')}")
        print(f"  confidence: {response.get('confidence', 'NOT FOUND')}")
        print(f"  execution_trace: {response.get('execution_trace', 'NOT FOUND')}")
        
        # Test the exact line from Streamlit app
        streamlit_display = response.get('synthesized_answer', 'No response')
        print(f"\n📱 Streamlit display line would show:")
        print(f"  'System: {streamlit_display}'")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_streamlit_response())
