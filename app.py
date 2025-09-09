import streamlit as st
import asyncio
import json
from datetime import datetime
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from coordinator.coordinator_agent import CoordinatorAgent
from memory.memory_agent import MemoryAgent
from loguru import logger

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
            # Initialize coordinator (which initializes all agents)
            st.session_state.coordinator = CoordinatorAgent()
            st.session_state.messages = []
            logger.info("Multi-agent system initialized successfully")
        except Exception as e:
            st.error(f"Failed to initialize system: {e}")
            logger.error(f"System initialization failed: {e}")
            return False
    return True

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

def display_memory_stats():
    """Display memory system statistics in sidebar"""
    if 'coordinator' in st.session_state:
        memory_agent = st.session_state.coordinator.memory_agent
        
        # Get memory stats
        conversation_count = len(memory_agent.conversation_memory)
        knowledge_count = len(memory_agent.knowledge_base)
        
        st.sidebar.subheader("📊 Memory Statistics")
        st.sidebar.metric("Conversations Stored", conversation_count)
        st.sidebar.metric("Knowledge Entries", knowledge_count)
        
        # Memory search
        st.sidebar.subheader("🔍 Search Memory")
        search_query = st.sidebar.text_input("Search past conversations:")
        if search_query and st.sidebar.button("Search"):
            try:
                results = memory_agent.search_memory(search_query, max_results=3)
                if results:
                    st.sidebar.write("**Recent relevant conversations:**")
                    for result in results[:3]:
                        st.sidebar.write(f"- {result.get('content', '')[:100]}...")
                else:
                    st.sidebar.write("No relevant conversations found.")
            except Exception as e:
                st.sidebar.error(f"Search failed: {e}")

async def process_query(query: str):
    """Process user query through the multi-agent system"""
    try:
        # Process query through coordinator
        response = await st.session_state.coordinator.process_user_query(query)
        return response
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        return {
            "response": f"I encountered an error processing your query: {str(e)}",
            "confidence": 0.0,
            "trace": []
        }

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
    if st.session_state.messages:
        st.subheader("Conversation History")
        for msg in st.session_state.messages:
            with st.container():
                if msg["role"] == "user":
                    st.write(f"**You:** {msg['content']}")
                else:
                    st.write(f"**System:** {msg['content']}")
                    if msg.get('confidence'):
                        st.caption(f"Confidence: {msg['confidence']:.2f}")
                    if msg.get('trace'):
                        display_agent_trace(msg['trace'])
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
        if 'coordinator' in st.session_state:
            # Reset conversation memory
            st.session_state.coordinator.memory_agent.conversation_memory = []
        st.rerun()
    
    # Process query
    if submit_button and query_input.strip():
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": query_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Show processing indicator
        with st.spinner("Processing query through multi-agent system..."):
            # Process query
            response_data = asyncio.run(process_query(query_input))
        
        # Add system response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_data.get("response", "No response generated"),
            "confidence": response_data.get("confidence", 0.0),
            "trace": response_data.get("trace", []),
            "timestamp": datetime.now().isoformat()
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