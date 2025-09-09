#!/usr/bin/env python3
"""
Check the actual structure of your MemoryAgent class and fix compatibility issues.
"""

import sys
from pathlib import Path
import inspect

# Add src to path
sys.path.insert(0, str(Path("src").absolute()))

def examine_memory_agent():
    """Examine the MemoryAgent class structure"""
    print("🧠 EXAMINING MEMORY AGENT")
    print("=" * 50)
    
    try:
        from memory.memory_agent import MemoryAgent
        print("✅ MemoryAgent imported successfully")
        
        # Create an instance
        memory_agent = MemoryAgent()
        print("✅ MemoryAgent instantiated")
        
        # Get all attributes and methods
        all_attrs = dir(memory_agent)
        public_attrs = [attr for attr in all_attrs if not attr.startswith('_')]
        
        print(f"\n📋 PUBLIC ATTRIBUTES AND METHODS:")
        for attr in sorted(public_attrs):
            try:
                attr_obj = getattr(memory_agent, attr)
                if callable(attr_obj):
                    try:
                        signature = inspect.signature(attr_obj)
                        print(f"  🔹 {attr}{signature} (method)")
                    except:
                        print(f"  🔹 {attr}(...) (method)")
                else:
                    attr_type = type(attr_obj).__name__
                    print(f"  🔸 {attr}: {attr_type} (attribute)")
            except Exception as e:
                print(f"  ❓ {attr}: Error accessing - {e}")
        
        # Look for memory-related attributes
        memory_attrs = [attr for attr in public_attrs if 'memory' in attr.lower() or 'collection' in attr.lower() or 'store' in attr.lower()]
        
        if memory_attrs:
            print(f"\n🧠 MEMORY-RELATED ATTRIBUTES:")
            for attr in memory_attrs:
                try:
                    attr_obj = getattr(memory_agent, attr)
                    attr_type = type(attr_obj).__name__
                    print(f"  ⭐ {attr}: {attr_type}")
                except:
                    print(f"  ⭐ {attr}: (error accessing)")
        
        # Look for collection-related methods
        collection_methods = [attr for attr in public_attrs if callable(getattr(memory_agent, attr, None)) and any(keyword in attr.lower() for keyword in ['search', 'store', 'retrieve', 'get', 'add'])]
        
        if collection_methods:
            print(f"\n🔍 DATA ACCESS METHODS:")
            for method in collection_methods:
                try:
                    method_obj = getattr(memory_agent, method)
                    signature = inspect.signature(method_obj)
                    print(f"  ⭐ {method}{signature}")
                except:
                    print(f"  ⭐ {method}(...)")
        
        return memory_agent, public_attrs
        
    except Exception as e:
        print(f"❌ Error examining MemoryAgent: {e}")
        import traceback
        traceback.print_exc()
        return None, []

def create_compatible_streamlit_app(memory_agent, attrs):
    """Create a Streamlit app compatible with your actual MemoryAgent structure"""
    print(f"\n🔧 CREATING COMPATIBLE STREAMLIT APP")
    print("=" * 50)
    
    if not memory_agent:
        print("❌ Cannot create compatible app - MemoryAgent not accessible")
        return
    
    # Try to find memory access methods
    search_methods = [attr for attr in attrs if 'search' in attr.lower() and callable(getattr(memory_agent, attr, None))]
    store_methods = [attr for attr in attrs if any(keyword in attr.lower() for keyword in ['store', 'add', 'save']) and callable(getattr(memory_agent, attr, None))]
    
    print(f"Found search methods: {search_methods}")
    print(f"Found store methods: {store_methods}")
    
    # Create compatible Streamlit app
    streamlit_code = '''import streamlit as st
import asyncio
import json
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from coordinator.coordinator_agent import CoordinatorAgent
    from memory.memory_agent import MemoryAgent
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Make sure all required dependencies are installed and the src path is correct.")
    st.stop()

# Configure page
st.set_page_config(
    page_title="Multi-Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_system():
    """Initialize the multi-agent system"""
    if 'coordinator' not in st.session_state:
        try:
            st.session_state.coordinator = CoordinatorAgent()
            st.session_state.messages = []
            st.success("✅ Multi-agent system initialized successfully")
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize system: {e}")
            return False
    return True

def get_memory_stats(coordinator):
    """Get memory statistics in a safe way"""
    try:
        memory_agent = coordinator.memory_agent
        stats = {}
        
        # Try different ways to get memory count'''
    
    # Add memory access based on what's available
    if 'conversation_memory' in attrs:
        streamlit_code += '''
        if hasattr(memory_agent, 'conversation_memory'):
            stats['conversations'] = len(memory_agent.conversation_memory)
        '''
    elif any('conversation' in attr.lower() for attr in attrs):
        conv_attrs = [attr for attr in attrs if 'conversation' in attr.lower()]
        streamlit_code += f'''
        # Try accessing conversation data through: {conv_attrs}
        '''
        for attr in conv_attrs[:1]:  # Just try the first one
            streamlit_code += f'''
        try:
            if hasattr(memory_agent, '{attr}'):
                conv_data = getattr(memory_agent, '{attr}')
                if hasattr(conv_data, '__len__'):
                    stats['conversations'] = len(conv_data)
        except:
            pass
        '''
    
    if 'knowledge_base' in attrs:
        streamlit_code += '''
        if hasattr(memory_agent, 'knowledge_base'):
            stats['knowledge'] = len(memory_agent.knowledge_base)
        '''
    
    # Add search functionality
    if search_methods:
        search_method = search_methods[0]  # Use the first available search method
        streamlit_code += f'''
        
        # Memory search using {search_method}
        if hasattr(memory_agent, '{search_method}'):
            search_func = getattr(memory_agent, '{search_method}')
        '''
    
    streamlit_code += '''
        
        return stats
    except Exception as e:
        st.error(f"Error getting memory stats: {e}")
        return {}

def display_memory_stats():
    """Display memory system statistics in sidebar"""
    if 'coordinator' in st.session_state:
        stats = get_memory_stats(st.session_state.coordinator)
        
        st.sidebar.subheader("📊 Memory Statistics")
        st.sidebar.metric("Conversations Stored", stats.get('conversations', 'Unknown'))
        st.sidebar.metric("Knowledge Entries", stats.get('knowledge', 'Unknown'))
        
        # Memory search (simplified)
        st.sidebar.subheader("🔍 Search Memory")
        search_query = st.sidebar.text_input("Search past conversations:")
        if search_query and st.sidebar.button("Search"):
            try:
                memory_agent = st.session_state.coordinator.memory_agent'''
    
    # Add search implementation based on available methods
    if search_methods:
        search_method = search_methods[0]
        streamlit_code += f'''
                if hasattr(memory_agent, '{search_method}'):
                    search_func = getattr(memory_agent, '{search_method}')
                    # Try to call the search method (parameters may vary)
                    try:
                        results = search_func(search_query)
                        if results:
                            st.sidebar.write("**Recent relevant conversations:**")
                            # Display results (format may vary)
                            for i, result in enumerate(results[:3]):
                                st.sidebar.write(f"- Result {i+1}: {str(result)[:100]}...")
                        else:
                            st.sidebar.write("No relevant conversations found.")
                    except Exception as e:
                        st.sidebar.error(f"Search failed: {e}")'''
    else:
        streamlit_code += '''
                st.sidebar.write("Search functionality not available")'''
    
    streamlit_code += '''
            except Exception as e:
                st.sidebar.error(f"Search failed: {e}")

async def process_query(query: str):
    """Process user query through the multi-agent system"""
    try:
        # Use the correct method name (you fixed this already)
        response = await st.session_state.coordinator.process_query(query)
        return response
    except Exception as e:
        return {
            "response": f"I encountered an error processing your query: {str(e)}",
            "confidence": 0.0,
            "trace": []
        }

def display_agent_trace(trace_data):
    """Display agent execution trace in an expandable section"""
    if not trace_data:
        return
        
    with st.expander("🔍 Agent Execution Trace", expanded=False):
        for i, step in enumerate(trace_data):
            st.write(f"**Step {i+1}: {step.get('agent', 'Unknown')}**")
            if step.get('action'):
                st.write(f"*Action*: {step['action']}")
            if step.get('result'):
                st.write(f"*Result*: {step['result'][:200]}{'...' if len(step['result']) > 200 else ''}")
            if step.get('timestamp'):
                st.write(f"*Time*: {step['timestamp']}")
            st.write("---")

def main():
    st.title("🤖 Multi-Agent System")
    st.markdown("*Intelligent coordination across Research, Analysis, and Memory agents*")
    
    # Initialize system
    if not init_system():
        st.stop()
    
    # Sidebar with system info
    st.sidebar.title("System Status")
    st.sidebar.success("✅ All agents online")
    
    # Display memory stats
    display_memory_stats()
    
    # Sample queries
    st.sidebar.subheader("📝 Sample Queries")
    sample_queries = [
        "What are the main types of neural networks?",
        "Research transformer architectures and analyze their efficiency",
        "What did we discuss about neural networks earlier?",
        "Find recent papers on reinforcement learning",
        "Compare two machine learning approaches"
    ]
    
    for i, sample in enumerate(sample_queries):
        if st.sidebar.button(f"Sample {i+1}", key=f"sample_{i}"):
            st.session_state.current_query = sample
    
    # Main chat interface
    st.subheader("💬 Chat with the Multi-Agent System")
    
    # Display conversation history
    if st.session_state.get('messages'):
        st.subheader("Conversation History")
        for msg in reversed(st.session_state.messages):
            with st.container():
                st.write(f"**You:** {msg['query']}")
                st.write(f"**System:** {msg['response'].get('response', 'No response')}")
                if msg['response'].get('confidence'):
                    st.caption(f"Confidence: {msg['response']['confidence']:.2f}")
                if msg['response'].get('trace'):
                    display_agent_trace(msg['response']['trace'])
                st.write("---")
    
    # Query input
    query_input = st.text_input(
        "Enter your question:",
        value=st.session_state.get('current_query', ''),
        key="query_input",
        placeholder="Ask me anything about AI, ML, or previous conversations..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.button("Send", type="primary")
    with col2:
        clear_button = st.button("Clear History")
    
    if clear_button:
        st.session_state.messages = []
        st.rerun()
    
    # Process query
    if submit_button and query_input.strip():
        with st.spinner("Processing query through multi-agent system..."):
            response_data = asyncio.run(process_query(query_input))
        
        # Store message
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
        st.session_state.messages.append({
            'query': query_input,
            'response': response_data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Clear input and rerun
        st.session_state.current_query = ""
        st.rerun()
    
    # System information
    with st.expander("ℹ️ System Information", expanded=False):
        st.write("""
        **Multi-Agent System Architecture:**
        
        - **Coordinator Agent**: Orchestrates tasks and manages agent communication
        - **Research Agent**: Handles information retrieval from knowledge base
        - **Analysis Agent**: Performs comparisons, reasoning, and calculations
        - **Memory Agent**: Manages persistent storage with vector search capabilities
        
        **Features:**
        - Vector-based semantic search using ChromaDB
        - LLM integration with Groq for intelligent task decomposition
        - Comprehensive logging and execution tracing
        - Persistent memory across sessions
        """)

if __name__ == "__main__":
    main()
'''
    
    # Save the compatible app
    app_file = Path("app_compatible.py")
    app_file.write_text(streamlit_code, encoding='utf-8')
    print(f"✅ Created compatible Streamlit app: {app_file}")
    
    return app_file

def main():
    """Main examination and fix function"""
    print("🔧 MEMORY AGENT COMPATIBILITY FIX")
    print("=" * 60)
    
    memory_agent, attrs = examine_memory_agent()
    
    if memory_agent and attrs:
        app_file = create_compatible_streamlit_app(memory_agent, attrs)
        print(f"\n🚀 NEXT STEPS:")
        print(f"1. Try running: uv run streamlit run {app_file}")
        print("2. Or replace your current app.py with the compatible version")
        print("3. The new app should work with your actual MemoryAgent structure")
    else:
        print("\n❌ Could not examine MemoryAgent - fix import issues first")

if __name__ == "__main__":
    main()