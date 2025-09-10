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
    page_title="Multi-Agent System - DEBUG",
    page_icon="🐛",
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

async def process_query(query: str):
    """Process user query through the multi-agent system with debug info"""
    try:
        st.write("🔍 **DEBUG: Processing query...**")
        response = await st.session_state.coordinator.process_user_query(query)
        
        st.write("🔍 **DEBUG: Raw response from coordinator:**")
        st.json(response)
        
        st.write("🔍 **DEBUG: Response type and keys:**")
        st.write(f"Type: {type(response)}")
        st.write(f"Keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        if isinstance(response, dict):
            st.write("🔍 **DEBUG: Individual fields:**")
            for key, value in response.items():
                st.write(f"  {key}: {type(value)} = {repr(str(value)[:200])}{'...' if len(str(value)) > 200 else ''}")
        
        return response
    except Exception as e:
        st.error(f"❌ Error in process_query: {e}")
        import traceback
        st.error(traceback.format_exc())
        return {
            "synthesized_answer": f"I encountered an error processing your query: {str(e)}",
            "confidence": 0.0,
            "execution_trace": []
        }

def main():
    st.title("🐛 Multi-Agent System - DEBUG MODE")
    st.markdown("*Debug version to identify response display issues*")
    
    # Initialize system
    if not init_system():
        st.stop()
    
    # Debug info
    st.sidebar.title("🐛 Debug Info")
    st.sidebar.write(f"Messages in session: {len(st.session_state.get('messages', []))}")
    
    # Main interface
    st.subheader("💬 Test Query Processing")
    
    query = st.text_input(
        "Your question:",
        value="What are the main types of neural networks?",
        placeholder="Ask me anything..."
    )
    
    if st.button("Process Query", type="primary"):
        with st.spinner("Processing query..."):
            response_data = asyncio.run(process_query(query))
        
        st.write("🔍 **DEBUG: Response data to be stored:**")
        st.json(response_data)
        
        # Store message
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
        message_to_store = {
            'query': query,
            'response': response_data,
            'timestamp': datetime.now().isoformat()
        }
        
        st.write("🔍 **DEBUG: Message to be stored:**")
        st.json(message_to_store)
        
        st.session_state.messages.append(message_to_store)
        
        st.write("🔍 **DEBUG: Stored messages count:**")
        st.write(f"Total messages: {len(st.session_state.messages)}")
    
    # Display conversation history with debug info
    if st.session_state.get('messages'):
        st.subheader("📜 Conversation History (Debug)")
        for i, msg in enumerate(reversed(st.session_state.messages), 1):
            with st.expander(f"Message {i}: {msg['query'][:50]}...", expanded=True):
                st.write("🔍 **DEBUG: Full message structure:**")
                st.json(msg)
                
                st.write("🔍 **DEBUG: Response field analysis:**")
                response_field = msg['response']
                st.write(f"Response type: {type(response_field)}")
                st.write(f"Response keys: {list(response_field.keys()) if isinstance(response_field, dict) else 'Not a dict'}")
                
                if isinstance(response_field, dict):
                    synthesized_answer = response_field.get('synthesized_answer', 'NOT FOUND')
                    st.write(f"🔍 **DEBUG: synthesized_answer field:**")
                    st.write(f"Value: {repr(synthesized_answer)}")
                    st.write(f"Type: {type(synthesized_answer)}")
                    st.write(f"Length: {len(str(synthesized_answer))}")
                
                st.write("🔍 **DEBUG: What would be displayed:**")
                display_value = msg['response'].get('synthesized_answer', 'No response')
                st.write(f"Display value: {repr(display_value)}")
                st.write(f"**System:** {display_value}")
                
                st.write("---")

if __name__ == "__main__":
    main()
