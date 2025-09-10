import streamlit as st
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
        
        # Try to get conversation count from ChromaDB collections
        try:
            if hasattr(memory_agent, 'conversation_collection'):
                # ChromaDB collections have a count() method
                stats['conversations'] = memory_agent.conversation_collection.count()
            elif hasattr(memory_agent, 'conversation_metadata') and isinstance(memory_agent.conversation_metadata, list):
                stats['conversations'] = len(memory_agent.conversation_metadata)
            else:
                stats['conversations'] = 0
        except:
            stats['conversations'] = 0
        
        # Try to get knowledge count
        try:
            if hasattr(memory_agent, 'knowledge_collection'):
                stats['knowledge'] = memory_agent.knowledge_collection.count()
            elif hasattr(memory_agent, 'knowledge_base') and hasattr(memory_agent.knowledge_base, '__len__'):
                stats['knowledge'] = len(memory_agent.knowledge_base)
            else:
                stats['knowledge'] = 0
        except:
            stats['knowledge'] = 0
        
        return stats
    except Exception as e:
        return {'conversations': 0, 'knowledge': 0}
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
                memory_agent = st.session_state.coordinator.memory_agent
                st.sidebar.write("Search functionality not available")
            except Exception as e:
                st.sidebar.error(f"Search failed: {e}")

async def process_query(query: str):
    """Process user query through the multi-agent system"""
    try:
        # Use the correct method name (you fixed this already)
        response = await st.session_state.coordinator.process_user_query(query)
        return response
    except Exception as e:
        return {
            "synthesized_answer": f"I encountered an error processing your query: {str(e)}",
            "confidence": 0.0,
            "execution_trace": []
        }

def display_agent_trace(trace_data, agent_results=None):
    """Display agent execution trace in an expandable section.
    Now also shows memory-specific metadata when available (hit count, best_distance, reused).
    """
    if agent_results is None:
        agent_results = {}

    if not trace_data:
        return

    with st.expander("🔍 Agent Execution Trace", expanded=False):
        for i, step in enumerate(trace_data):
            agent = step.get('agent', 'Unknown')
            st.markdown(f"**Step {i+1}: {agent}**")
            st.write(f"*Success:* {step.get('success', 'N/A')}")
            if step.get('execution_time') is not None:
                st.write(f"*Execution time:* {step.get('execution_time'):.3f}s")
            # Show agent-level reported details if present in agent_results
            ar = agent_results.get(agent)
            if ar:
                # confidence + short data-preview
                conf = ar.get('confidence')
                if conf is not None:
                    st.write(f"*Reported confidence:* {conf:.2f}")
                exec_time = ar.get('execution_time')
                if exec_time is not None:
                    st.write(f"*Agent execution time (reported):* {exec_time:.3f}s")

                data = ar.get('data', {})
                # MEMORY AGENT: show useful metrics
                if agent == "memory_agent":
                    # handle multiple shapes returned by MemoryAgent
                    results = None
                    if isinstance(data, dict):
                        results = data.get("results") or data.get("memories") or data.get("memories", None)
                        # also allow normalized structure: data might already be {"results": [...], "count": N}
                        if results is None and "count" in data and isinstance(data.get("count"), int):
                            # use count and best_distance fields
                            pass
                    if results is None and isinstance(data, list):
                        results = data

                    count = len(results) if results else data.get("count", 0) if isinstance(data, dict) else 0
                    st.write(f"*Memory hits:* {count}")

                    best = None
                    if isinstance(data, dict):
                        best = data.get("best_distance") or data.get("distance")
                    if best is not None:
                        st.write(f"*Best distance:* {best}")

                    # Was memory actually reused for research? check research_agent's reported data
                    reused = False
                    research_data = agent_results.get("research_agent", {}).get("data", {})
                    if isinstance(research_data, dict):
                        rr = research_data.get("research_results") or {}
                        if isinstance(rr, dict) and rr.get("source") == "memory":
                            reused = True
                    st.write(f"*Memory reused for research:* {'✅' if reused else 'No'}")

                    # Small snippet of the first hit (if any)
                    if results:
                        try:
                            snippet = results[0].get("content") if isinstance(results[0], dict) else str(results[0])
                            snippet = (snippet or "")[:300]
                            st.write(f"*Top hit snippet:* {snippet}{'...' if len(snippet) == 300 else ''}")
                        except Exception:
                            pass
                else:
                    # Generic preview for other agents
                    try:
                        preview = None
                        if isinstance(data, dict):
                            # show up to 3 keys
                            keys = list(data.keys())[:3]
                            preview = {k: data[k] for k in keys}
                            st.text(json.dumps(preview, indent=2))
                        else:
                            st.write(f"*Data:* {str(data)[:300]}")
                    except Exception:
                        pass

            # legacy fields from older trace format
            if step.get('action'):
                st.write(f"*Action:* {step['action']}")
            if step.get('result'):
                r = step['result']
                if isinstance(r, str):
                    st.write(f"*Result:* {r[:200]}{'...' if len(r) > 200 else ''}")
            if step.get('timestamp'):
                st.write(f"*Time:* {step['timestamp']}")
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
        for msg in st.session_state.messages:
            with st.container():
                st.write(f"**You:** {msg['query']}")
                st.write(f"**System:** {msg['response'].get('synthesized_answer', 'No response')}")
                if msg['response'].get('confidence'):
                    st.caption(f"Confidence: {msg['response']['confidence']:.2f}")
                if msg['response'].get('execution_trace'):
                    display_agent_trace(
                        msg['response']['execution_trace'],
                        agent_results=msg['response'].get('agent_results', {}))
                st.write("---")
        # This helps scroll to the latest message
        st.markdown("*💬 Latest conversation above*")
    
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

            st.write("🔍 DEBUG: Memory check after query")
            memory_stats = get_memory_stats(st.session_state.coordinator)
            st.write(f"🔍 DEBUG: Conversations in memory: {memory_stats.get('conversations', 0)}")

            memory_agent = st.session_state.coordinator.memory_agent
            st.write(f"🔍 DEBUG: Raw conversation_metadata count: {len(memory_agent.conversation_metadata)}")
            if memory_agent.conversation_metadata:
                st.write("🔍 DEBUG: Sample stored conversation:")
                sample_key = list(memory_agent.conversation_metadata.keys())[0]
                st.write(f"🔍 DEBUG: {memory_agent.conversation_metadata[sample_key]}")

            st.write("🔍 DEBUG: Raw response from coordinator:")
            st.write("Response data:")
            for key, value in response_data.items():
                st.write(f"  {key}: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
            st.write(f"�� DEBUG: synthesized_answer = {response_data.get('synthesized_answer', 'NOT FOUND')}")
            st.write("DEBUG: agent_results (keys):", list(response_data.get('agent_results', {}).keys()))

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
