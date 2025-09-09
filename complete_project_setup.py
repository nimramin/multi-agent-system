#!/usr/bin/env python3
"""
Complete project setup script for the multi-agent system.
This script helps finalize the project based on your existing codebase structure.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n[Step {step}] {description}")
    print("-" * 40)

def check_and_create_file(filepath, content, description):
    """Check if file exists, create if missing"""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description}: {filepath} (EXISTS)")
        return True
    else:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {description}: {filepath} (CREATED)")
            return True
        except Exception as e:
            print(f"❌ {description}: {filepath} (FAILED: {e})")
            return False

def validate_current_structure():
    """Validate the current project structure"""
    print_step(1, "Validating Current Project Structure")
    
    required_files = [
        "src/agents/base_agent.py",
        "src/agents/research_agent.py", 
        "src/agents/analysis_agent.py",
        "src/coordinator/coordinator_agent.py",
        "src/memory/memory_agent.py",
        "src/models/message.py",
        "pyproject.toml",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (MISSING)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  WARNING: {len(missing_files)} required files are missing")
        return False
    else:
        print(f"\n✅ All core files present!")
        return True

def create_missing_files():
    """Create missing required files"""
    print_step(2, "Creating Missing Project Files")
    
    # Create .env template if missing
    env_content = """# Multi-Agent System Environment Variables
GROQ_API_KEY=your_groq_api_key_here
PYTHONPATH=./src
LOG_LEVEL=INFO

# Optional: Database settings
CHROMA_DB_PATH=./data/chroma_db
"""
    check_and_create_file(".env.template", env_content, "Environment template")
    
    # Create .dockerignore
    dockerignore_content = """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
data/
logs/
*.env
!.env.template
outputs/*.txt
"""
    check_and_create_file(".dockerignore", dockerignore_content, "Docker ignore file")

def create_streamlit_app():
    """Create the Streamlit application"""
    print_step(3, "Creating Streamlit Web Interface")
    
    app_content = '''import streamlit as st
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

def main():
    st.title("🤖 Multi-Agent System")
    st.markdown("*Intelligent coordination across Research, Analysis, and Memory agents*")
    
    # Initialize system
    if not init_system():
        st.stop()
    
    # Sample queries in sidebar
    st.sidebar.title("🎯 Sample Queries")
    sample_queries = [
        "What are the main types of neural networks?",
        "Research transformer architectures and analyze their efficiency",
        "What did we discuss about neural networks earlier?",
        "Find recent papers on reinforcement learning",
        "Compare two machine learning approaches"
    ]
    
    for i, sample in enumerate(sample_queries, 1):
        if st.sidebar.button(f"Query {i}", key=f"sample_{i}"):
            st.session_state.current_query = sample
    
    # Main interface
    st.subheader("💬 Ask the Multi-Agent System")
    
    query = st.text_input(
        "Your question:",
        value=st.session_state.get('current_query', ''),
        placeholder="Ask me anything about AI, ML, or previous conversations..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("Ask", type="primary")
    with col2:
        clear_button = st.button("Clear History")
    
    if clear_button:
        st.session_state.messages = []
        st.rerun()
    
    if ask_button and query.strip():
        with st.spinner("🤔 Processing your query..."):
            try:
                # Process query through coordinator
                response = asyncio.run(st.session_state.coordinator.process_user_query(query))
                
                # Display response
                st.subheader("🤖 Response")
                st.write(response.get('response', 'No response generated'))
                
                if response.get('confidence'):
                    st.caption(f"Confidence: {response['confidence']:.2f}")
                
                # Show execution trace
                if response.get('trace'):
                    with st.expander("🔍 Agent Execution Trace"):
                        for i, step in enumerate(response['trace'], 1):
                            st.write(f"**Step {i}: {step.get('agent', 'Unknown')}**")
                            st.write(f"Action: {step.get('action', 'N/A')}")
                            if step.get('result'):
                                st.write(f"Result: {step['result'][:200]}{'...' if len(step['result']) > 200 else ''}")
                            st.write("---")
                
                # Store in session history
                st.session_state.messages.append({
                    'query': query,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                st.error(f"Error processing query: {e}")
    
    # Show conversation history
    if st.session_state.get('messages'):
        st.subheader("📜 Conversation History")
        for i, msg in enumerate(reversed(st.session_state.messages), 1):
            with st.expander(f"Conversation {i}: {msg['query'][:50]}..."):
                st.write(f"**Query:** {msg['query']}")
                st.write(f"**Response:** {msg['response'].get('response', 'No response')}")
                st.caption(f"Time: {msg['timestamp']}")

if __name__ == "__main__":
    main()
'''
    
    check_and_create_file("app.py", app_content, "Streamlit application")

def create_output_generator():
    """Create the output generation script"""
    print_step(4, "Creating Output Generation Script")
    
    generator_content = '''#!/usr/bin/env python3
"""Generate sample outputs for all 5 required test scenarios."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from coordinator.coordinator_agent import CoordinatorAgent

async def run_scenario(coordinator, scenario_name, query, filename):
    """Run a single test scenario and save output"""
    print(f"\\n{'='*60}")
    print(f"Running: {scenario_name}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    try:
        response = await coordinator.process_user_query(query)
        
        # Prepare output
        output_lines = [
            f"Multi-Agent System - {scenario_name}",
            f"Query: {query}",
            f"Timestamp: {datetime.now().isoformat()}",
            "=" * 60,
            "",
            "RESPONSE:",
            response.get('response', 'No response generated'),
            "",
            f"CONFIDENCE: {response.get('confidence', 0.0):.2f}",
            "",
            "EXECUTION TRACE:"
        ]
        
        # Add trace
        for i, step in enumerate(response.get('trace', []), 1):
            output_lines.extend([
                f"Step {i}: {step.get('agent', 'Unknown')}",
                f"  Action: {step.get('action', 'N/A')}",
                f"  Result: {step.get('result', 'N/A')[:200]}{'...' if len(step.get('result', '')) > 200 else ''}",
                ""
            ])
        
        # Save to file
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        output_file = outputs_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\\n'.join(output_lines))
        
        print(f"✅ Saved: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Generate all sample outputs"""
    scenarios = [
        ("Simple Query", "What are the main types of neural networks?", "simple_query.txt"),
        ("Complex Query", "Research transformer architectures, analyze their computational efficiency, and summarize key trade-offs.", "complex_query.txt"),
        ("Memory Test", "What did we discuss about neural networks earlier?", "memory_test.txt"),
        ("Multi-step", "Find recent papers on reinforcement learning, analyze their methodologies, and identify common challenges.", "multi_step.txt"),
        ("Collaborative", "Compare two machine-learning approaches and recommend which is better for our use case.", "collaborative.txt")
    ]
    
    print("Initializing Multi-Agent System...")
    coordinator = CoordinatorAgent()
    
    for scenario_name, query, filename in scenarios:
        await run_scenario(coordinator, scenario_name, query, filename)
        await asyncio.sleep(1)  # Brief pause between scenarios
    
    print(f"\\n{'='*60}")
    print("All scenarios completed! Check the outputs/ directory.")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    check_and_create_file("generate_outputs.py", generator_content, "Output generation script")

def create_docker_files():
    """Create Docker configuration files"""
    print_step(5, "Creating Docker Configuration")
    
    dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY src/ ./src/
COPY app.py ./
COPY generate_outputs.py ./
COPY run_tests.py ./
COPY simple_demo.py ./
COPY main.py ./

# Create directories
RUN mkdir -p outputs data logs

# Create non-root user
RUN useradd -m -s /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
'''
    
    check_and_create_file("Dockerfile", dockerfile_content, "Dockerfile")
    
    compose_content = '''version: '3.8'

services:
  multi-agent-system:
    build: .
    ports:
      - "8501:8501"
    environment:
      - PYTHONPATH=/app/src
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./outputs:/app/outputs
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  test-runner:
    build: .
    environment:
      - PYTHONPATH=/app/src
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./outputs:/app/outputs
    command: ["uv", "run", "python", "generate_outputs.py"]
    profiles: [testing]
'''
    
    check_and_create_file("docker-compose.yml", compose_content, "Docker Compose")

def update_readme():
    """Update README with current structure"""
    print_step(6, "Updating Documentation")
    
    if Path("README.md").exists():
        print("✅ README.md already exists - please manually update it with the new components")
    else:
        readme_content = '''# Multi-Agent System

A sophisticated multi-agent system with intelligent coordination, structured memory, and adaptive decision-making.

## Quick Start

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment:
   ```bash
   cp .env.template .env
   # Edit .env and add your GROQ_API_KEY
   ```

3. Run the web interface:
   ```bash
   uv run streamlit run app.py
   ```

4. Or generate sample outputs:
   ```bash
   python generate_outputs.py
   ```

## Docker Deployment

```bash
docker-compose up --build
```

For testing:
```bash
docker-compose --profile testing up test-runner
```

## Architecture

- **Coordinator Agent**: Orchestrates tasks across specialized agents
- **Research Agent**: Handles information retrieval
- **Analysis Agent**: Performs data analysis and reasoning  
- **Memory Agent**: Manages persistent storage with vector search

See the `src/` directory for implementation details.
'''
        check_and_create_file("README.md", readme_content, "README documentation")

def main():
    """Main setup function"""
    print_header("Multi-Agent System - Project Completion Setup")
    
    print("This script will help you complete your multi-agent system project.")
    print("Based on your current directory structure:")
    print("- src/agents/")
    print("- src/coordinator/")  
    print("- src/memory/")
    print("- src/models/")
    
    # Validate current structure
    if not validate_current_structure():
        print("\n⚠️  Some core files are missing. Please ensure your codebase is complete first.")
        return
    
    # Create missing files
    create_missing_files()
    create_streamlit_app()
    create_output_generator()
    create_docker_files()
    update_readme()
    
    print_header("Setup Complete!")
    
    print("✅ Next steps:")
    print("1. Copy your GROQ API key to .env file")
    print("2. Test the system: python run_tests.py")
    print("3. Generate outputs: python generate_outputs.py") 
    print("4. Run web interface: uv run streamlit run app.py")
    print("5. Test Docker: docker-compose up --build")
    
    print("\n🎯 Your project now includes:")
    print("- ✅ Streamlit web interface (app.py)")
    print("- ✅ Output generation script")
    print("- ✅ Docker configuration")
    print("- ✅ Environment templates")
    print("- ✅ Updated documentation")

if __name__ == "__main__":
    main()