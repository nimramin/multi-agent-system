#!/usr/bin/env python3
"""
Fix ChromaDB collection initialization issues.
This script helps diagnose and fix ChromaDB collection problems.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("src").absolute()))

def test_chromadb_setup():
    """Test ChromaDB setup and create collections if needed"""
    print("🔍 Testing ChromaDB Setup")
    print("=" * 40)
    
    try:
        import chromadb
        print("✅ ChromaDB imported successfully")
        
        # Try to create a client
        client = chromadb.Client()
        print("✅ ChromaDB client created")
        
        # List existing collections
        collections = client.list_collections()
        print(f"📊 Existing collections: {[c.name for c in collections]}")
        
        # Collections that should exist
        required_collections = ["conversations", "knowledge", "agent_state"]
        
        for collection_name in required_collections:
            try:
                collection = client.get_collection(collection_name)
                print(f"✅ Collection '{collection_name}' exists")
            except Exception:
                print(f"❌ Collection '{collection_name}' missing - will be created")
                try:
                    collection = client.create_collection(collection_name)
                    print(f"✅ Created collection '{collection_name}'")
                except Exception as e:
                    print(f"❌ Failed to create collection '{collection_name}': {e}")
        
        return True
        
    except ImportError:
        print("❌ ChromaDB not installed")
        print("Install with: uv add chromadb")
        return False
    except Exception as e:
        print(f"❌ ChromaDB error: {e}")
        return False

def check_memory_agent():
    """Check if memory agent initializes correctly"""
    print("\n🧠 Testing Memory Agent Initialization")
    print("=" * 40)
    
    try:
        from memory.memory_agent import MemoryAgent
        print("✅ MemoryAgent imported")
        
        # Try to initialize
        memory_agent = MemoryAgent()
        print("✅ MemoryAgent initialized successfully")
        
        # Test basic operations
        test_message = "This is a test message for ChromaDB"
        memory_agent.store_conversation("test_user", test_message, "test_response")
        print("✅ Test conversation stored")
        
        # Test search
        results = memory_agent.search_memory("test", max_results=1)
        print(f"✅ Memory search works: found {len(results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ MemoryAgent error: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False

def fix_memory_agent_file():
    """Check and potentially fix the memory agent file"""
    print("\n🔧 Checking Memory Agent File")
    print("=" * 40)
    
    memory_file = Path("src/memory/memory_agent.py")
    if not memory_file.exists():
        print(f"❌ File not found: {memory_file}")
        return False
    
    content = memory_file.read_text(encoding='utf-8')
    
    # Look for collection creation patterns
    if "get_or_create_collection" in content:
        print("✅ Using get_or_create_collection (good)")
    elif "get_collection" in content and "create_collection" not in content:
        print("❌ Only using get_collection (bad - will fail if collection doesn't exist)")
        print("💡 Should use get_or_create_collection instead")
    elif "create_collection" in content:
        print("⚠️  Using create_collection - might fail if collection already exists")
        print("💡 Should use get_or_create_collection instead")
    
    # Check for proper error handling
    if "try:" in content and "except" in content:
        print("✅ Has error handling")
    else:
        print("⚠️  No error handling found")
    
    return True

def create_simple_memory_test():
    """Create a simple test to verify memory agent works"""
    print("\n📝 Creating Simple Memory Test")
    print("=" * 40)
    
    test_script = '''#!/usr/bin/env python3
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
'''
    
    test_file = Path("test_memory_simple.py")
    test_file.write_text(test_script, encoding='utf-8')
    print(f"✅ Created simple test: {test_file}")
    
    return test_file

def main():
    """Main diagnostic and fix function"""
    print("🔧 CHROMADB COLLECTION FIX")
    print("=" * 50)
    
    # Step 1: Test ChromaDB setup
    if not test_chromadb_setup():
        print("\n❌ ChromaDB setup failed. Install ChromaDB first:")
        print("  uv add chromadb")
        return
    
    # Step 2: Check memory agent file
    fix_memory_agent_file()
    
    # Step 3: Test memory agent
    if check_memory_agent():
        print("\n🎉 Memory agent works correctly!")
    else:
        print("\n🔧 Memory agent needs fixing...")
        
        # Create a simple test for debugging
        test_file = create_simple_memory_test()
        print(f"\nTry running the simple test:")
        print(f"  python {test_file}")
    
    print("\n" + "=" * 50)
    print("💡 COMMON CHROMADB FIXES:")
    print("1. Use get_or_create_collection() instead of get_collection()")
    print("2. Add try/except blocks around collection operations")
    print("3. Initialize collections in __init__ method")
    print("4. Clear ChromaDB data: rm -rf ./chroma_db/")

if __name__ == "__main__":
    main()