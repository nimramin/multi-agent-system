# setup.sh - Complete setup script
#!/bin/bash
echo "🚀 Setting up Multi-Agent System..."

# Create project structure
mkdir -p src/{agents,memory,coordinator,models,utils}
mkdir -p tests outputs

# Install dependencies with uv
echo "📦 Installing dependencies..."
uv add groq streamlit chromadb pydantic loguru python-dotenv numpy pandas

# Create __init__.py files for proper Python imports
touch src/__init__.py
touch src/agents/__init__.py  
touch src/memory/__init__.py
touch src/coordinator/__init__.py
touch src/models/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

echo "✅ Setup complete!"

# Commands to run step by step:

# 1. FIRST - Create the project and install dependencies:
uv init
# Copy pyproject.toml content from artifact
uv sync

# 2. SECOND - Create all the Python files:
# Copy content from artifacts to:
# - src/models/message.py
# - src/agents/base_agent.py  
# - src/agents/research_agent.py
# - src/agents/analysis_agent.py
# - tests/test_models.py
# - tests/test_agents.py
# - tests/conftest.py
# - run_tests.py
# - simple_demo.py

# 3. THIRD - Test the system:
python run_tests.py

# Expected output:
# 🧪 Running Multi-Agent System Tests...
# ==================================================
# 📝 Testing Models...
# ✅ AgentMessage creation test passed
# ✅ TaskResult creation test passed
# 
# 🤖 Testing Agents...
# ✅ Research Agent basic test passed
# ✅ Analysis Agent basic test passed  
# ✅ Research Agent knowledge retrieval test passed
# 
# ✨ All tests passed! System is working correctly.

# 4. FOURTH - Run the demo:
python simple_demo.py

# Expected output:
# 🚀 Multi-Agent System Demo
# ========================================
# ✅ Initialized research_agent
# ✅ Initialized analysis_agent
# 
# 🔍 Demo 1: Research Agent Query
# Success: True
# Confidence: 0.30
# Results found: 1
# 
# 📊 Demo 2: Analysis Agent
# Success: True  
# Confidence: 0.80
# Analysis type: effectiveness_analysis
# 
# 🎉 Demo completed successfully!

# Alternative: Run with uv (if you prefer):
# uv run python run_tests.py
# uv run python simple_demo.py