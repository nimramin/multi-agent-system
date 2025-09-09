"""
Test suite for Memory Agent functionality.
Tests vector storage, retrieval, and search capabilities.
Run this to verify Memory Agent is working correctly.
"""
import sys
import os
import asyncio
import shutil
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.memory_agent import MemoryAgent
from models.message import AgentMessage, MessageType

async def test_memory_agent_initialization():
    """Test Memory Agent initializes correctly"""
    print("🧠 Testing Memory Agent Initialization...")
    
    # Use temporary storage for testing
    test_storage_path = "test_memory_storage"
    
    try:
        agent = MemoryAgent(storage_path=test_storage_path)
        
        # Check basic properties
        assert agent.agent_id == "memory_agent"
        assert "store" in agent.capabilities
        assert "retrieve" in agent.capabilities
        assert "search" in agent.capabilities
        assert os.path.exists(test_storage_path)
        
        print("✅ Memory Agent initialization test passed")
        return agent
        
    except Exception as e:
        print(f"❌ Memory Agent initialization failed: {e}")
        raise

async def test_memory_storage(agent):
    """Test storing information in memory"""
    print("💾 Testing Memory Storage...")
    
    try:
        # Test storing conversation memory
        store_message = AgentMessage(
            type=MessageType.TASK,
            sender="test",
            recipient="memory_agent",
            content="store information about neural networks",
            metadata={
                "data": {
                    "topic": "neural networks",
                    "content": "Neural networks are powerful for pattern recognition"
                },
                "memory_type": "conversation"
            }
        )
        
        result = await agent.process_task(store_message)
        
        assert result.success == True
        assert result.agent_id == "memory_agent"
        assert "stored" in result.data["action"]
        assert "memory_id" in result.data
        
        print("✅ Memory storage test passed")
        return result.data["memory_id"]
        
    except Exception as e:
        print(f"❌ Memory storage test failed: {e}")
        raise

async def test_memory_retrieval(agent, memory_id):
    """Test retrieving stored information"""
    print("🔍 Testing Memory Retrieval...")
    
    try:
        # Test retrieving specific memory by ID
        retrieve_message = AgentMessage(
            type=MessageType.TASK,
            sender="test",
            recipient="memory_agent",
            content="retrieve stored information",
            metadata={
                "memory_id": memory_id,
                "memory_type": "conversation"
            }
        )
        
        result = await agent.process_task(retrieve_message)
        
        assert result.success == True
        assert "retrieved" in result.data["action"]
        assert "memory" in result.data
        assert result.data["memory"]["content"] == "store information about neural networks"
        
        print("✅ Memory retrieval test passed")
        
        # Test retrieving recent memories
        recent_message = AgentMessage(
            type=MessageType.TASK,
            sender="test",
            recipient="memory_agent",
            content="get recent memories",
            metadata={
                "memory_type": "conversation",
                "limit": 3
            }
        )
        
        recent_result = await agent.process_task(recent_message)
        
        assert recent_result.success == True
        assert "memories" in recent_result.data
        assert len(recent_result.data["memories"]) >= 1
        
        print("✅ Recent memory retrieval test passed")
        
    except Exception as e:
        print(f"❌ Memory retrieval test failed: {e}")
        raise

async def test_memory_search(agent):
    """Test vector similarity search"""
    print("🔎 Testing Memory Search...")
    
    try:
        # Store a few more memories for search testing
        memories_to_store = [
            "machine learning algorithms are diverse",
            "deep learning uses neural networks", 
            "transformers revolutionized NLP"
        ]
        
        for memory_content in memories_to_store:
            store_msg = AgentMessage(
                type=MessageType.TASK,
                sender="test",
                recipient="memory_agent", 
                content=f"store {memory_content}",
                metadata={
                    "data": {"content": memory_content},
                    "memory_type": "knowledge"
                }
            )
            await agent.process_task(store_msg)
        
        # Test search functionality
        search_message = AgentMessage(
            type=MessageType.TASK,
            sender="test",
            recipient="memory_agent",
            content="search for neural network information",
            metadata={
                "memory_type": "knowledge",
                "limit": 2
            }
        )
        
        search_result = await agent.process_task(search_message)
        
        assert search_result.success == True
        assert "searched" in search_result.data["action"]
        assert "results" in search_result.data
        assert len(search_result.data["results"]) > 0
        
        print("✅ Memory search test passed")
        
    except Exception as e:
        print(f"❌ Memory search test failed: {e}")
        raise

async def test_memory_stats(agent):
    """Test memory statistics"""
    print("📊 Testing Memory Statistics...")
    
    try:
        stats = agent.get_memory_stats()
        
        assert "conversation_count" in stats
        assert "knowledge_count" in stats
        assert "storage_path" in stats
        assert stats["conversation_count"] >= 1  # We stored at least one
        assert stats["knowledge_count"] >= 3   # We stored three knowledge items
        
        print(f"✅ Memory stats test passed - {stats['conversation_count']} conversations, {stats['knowledge_count']} knowledge items")
        
    except Exception as e:
        print(f"❌ Memory stats test failed: {e}")
        raise

def cleanup_test_storage():
    """Clean up test storage directory"""
    test_storage_path = "test_memory_storage"
    if os.path.exists(test_storage_path):
        shutil.rmtree(test_storage_path)
    print("🧹 Test storage cleaned up")

async def run_memory_agent_tests():
    """Run all Memory Agent tests"""
    print("🧪 Running Memory Agent Tests...")
    print("=" * 50)
    
    agent = None
    memory_id = None
    
    try:
        # Test 1: Initialization
        agent = await test_memory_agent_initialization()
        
        # Test 2: Storage
        memory_id = await test_memory_storage(agent)
        
        # Test 3: Retrieval  
        await test_memory_retrieval(agent, memory_id)
        
        # Test 4: Search
        await test_memory_search(agent)
        
        # Test 5: Statistics
        await test_memory_stats(agent)
        
        print("\n✨ All Memory Agent tests passed!")
        print("Memory Agent is working correctly with:")
        print("  - Vector storage and retrieval")
        print("  - Similarity search")  
        print("  - Metadata management")
        print("  - Multiple memory types")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Memory Agent tests failed: {e}")
        return False
        
    finally:
        # Always clean up
        cleanup_test_storage()

if __name__ == "__main__":
    print("🚀 Memory Agent Test Suite")
    print("Tests ChromaDB integration, vector search, and storage")
    print()
    
    success = asyncio.run(run_memory_agent_tests())
    
    if success:
        print("\n🎉 Memory Agent is ready for integration!")
        print("Next steps:")
        print("1. Test Coordinator Agent")  
        print("2. Run integration tests")
        print("3. Build Streamlit UI")
    else:
        print("\n⚠️  Fix Memory Agent issues before proceeding")
    
    sys.exit(0 if success else 1)