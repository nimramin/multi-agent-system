"""
Test runner script to execute all tests and verify system functionality.
Run this to ensure the multi-agent system components are working correctly.
"""
import subprocess
import sys
import os

def run_tests():
    """Execute all tests and display results"""
    print("🧪 Running Multi-Agent System Tests...")
    print("=" * 50)
    
    # Add src to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, 'src')
    sys.path.insert(0, src_path)
    
    try:
        # Import and run tests directly since we might not have pytest installed yet
        from tests.test_models import test_agent_message_creation, test_task_result_creation
        from tests.test_agents import test_research_agent_basic, test_analysis_agent_basic, test_research_agent_knowledge_retrieval
        
        print("📝 Testing Models...")
        test_agent_message_creation()
        test_task_result_creation()
        
        print("\n🤖 Testing Agents...")
        import asyncio
        
        # Run async tests
        asyncio.run(test_research_agent_basic())
        asyncio.run(test_analysis_agent_basic()) 
        asyncio.run(test_research_agent_knowledge_retrieval())
        
        print("\n✨ All tests passed! System is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)