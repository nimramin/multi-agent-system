# Multi-Agent Chat System

A minimal multi-agent system where a Coordinator orchestrates three specialized worker agents to answer user questions with structured memory, adaptive decision-making, and inter-agent collaboration.

## Architecture Overview

The system consists of four main components:

1. **Coordinator Agent** (`coordinator_agent.py`) - Main orchestrator that:

   - Receives user queries and analyzes complexity
   - Routes tasks to appropriate worker agents
   - Coordinates dependencies and synthesizes results
   - Maintains conversation context and global state

2. **Research Agent** (`research_agent.py`) - Information retrieval specialist:

   - Searches mock knowledge base for relevant information
   - Handles topics like neural networks, machine learning, transformers
   - Returns structured research results with confidence scores

3. **Analysis Agent** (`analysis_agent.py`) - Data processing and reasoning:

   - Performs comparisons and evaluations on research data
   - Analyzes effectiveness and generates insights
   - Supports calculation and general analysis tasks

4. **Memory Agent** (`memory_agent.py`) - Long-term storage and retrieval:
   - Uses ChromaDB for vector similarity search
   - Maintains conversation history and knowledge base
   - Supports keyword and semantic search capabilities

## System Flow

```
User Query → Coordinator → Task Analysis → Agent Routing → Result Synthesis → Memory Storage
                ↓
          [Research] → [Analysis] → [Memory Lookup/Store]
                ↓
          Final Response with Execution Trace
```

## Features

- **LLM Integration**: Optional Groq API integration for intelligent task decomposition
- **Vector Search**: ChromaDB-based semantic similarity search
- **Memory Reuse**: Avoids redundant research by reusing similar past results
- **Execution Tracing**: Detailed logging of agent interactions and decision-making
- **Confidence Scoring**: Each agent provides confidence metrics for their outputs
- **Graceful Degradation**: Falls back to rule-based analysis when LLM unavailable

## Installation & Setup

### Prerequisites

- Python 3.8+
- Docker (optional)
- Groq API key (optional, for enhanced LLM features)

### Local Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd multi-agent-system
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set up Groq API key:

```bash
export GROQ_API_KEY="your-api-key-here"
```

### Docker Installation

1. Build and run with Docker Compose:

```bash
docker-compose up --build
```

2. Access the application at `http://localhost:8501`

## Usage

### Web Interface (Streamlit)

Start the web application:

```bash
streamlit run app_compatible.py
```

Features:

- Interactive chat interface
- Real-time agent execution tracing
- Memory statistics and search
- Sample query buttons
- Conversation history

### Console Interface

Run test scenarios:

```bash
python console_interface.py
```

This will execute all 5 required test scenarios and save outputs to the `outputs/` directory.

## Test Scenarios

The system includes 5 comprehensive test scenarios:

1. **Simple Query**: "What are the main types of neural networks?"
2. **Complex Query**: "Research transformer architectures, analyze their computational efficiency, and summarize key trade-offs."
3. **Memory Test**: "What did we discuss about neural networks earlier?"
4. **Multi-step**: "Find recent papers on reinforcement learning, analyze their methodologies, and identify common challenges."
5. **Collaborative**: "Compare two machine-learning approaches and recommend which is better for our use case."

Run individual tests:

```bash
python -m tests.test_scenarios
```

## Memory System Design

The memory system uses a hybrid approach:

### Storage Components

- **ChromaDB Collections**: Vector embeddings for semantic search
- **JSON Metadata**: Structured information with timestamps, topics, keywords
- **File Persistence**: Conversation and knowledge metadata storage

### Search Capabilities

- **Vector Similarity**: Semantic matching using embeddings
- **Keyword Filtering**: Topic and keyword-based retrieval
- **Hybrid Fallback**: Text-based search when embeddings unavailable

### Memory Types

- **Conversation Memory**: Full interaction history with context
- **Knowledge Base**: Persistent learned facts with provenance
- **Agent State**: Track what each agent learned per task

## Configuration

### Environment Variables

- `GROQ_API_KEY`: Optional Groq API key for LLM features
- `STORAGE_PATH`: Custom memory storage location (default: memory_storage)

### LLM Configuration

The system supports graceful degradation:

- **With LLM**: Advanced task decomposition and analysis
- **Without LLM**: Rule-based task routing and fallback behavior

## Project Structure

```
multi-agent-system/
├── src/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── research_agent.py
│   │   ├── analysis_agent.py
│   ├── coordinator/
│   │   └── coordinator_agent.py
│   ├── memory/
│   │   └── memory_agent.py
│   └── models/
│       └── message.py
├── tests/
│   └── test_scenarios.py
├── outputs/
│   ├── simple_query.txt
│   ├── complex_query.txt
│   ├── memory_test.txt
│   ├── multi_step.txt
│   └── collaborative.txt
├── memory_storage/
├── app_compatible.py
├── console_interface.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

## API Reference

### Coordinator Agent

```python
coordinator = CoordinatorAgent(groq_api_key="optional-key")
response = await coordinator.process_user_query("your question")
```

### Individual Agents

```python
# Research Agent
research_agent = ResearchAgent()
result = await research_agent.process_task(message)

# Analysis Agent
analysis_agent = AnalysisAgent()
result = await analysis_agent.process_task(message)

# Memory Agent
memory_agent = MemoryAgent(storage_path="custom_path")
result = await memory_agent.process_task(message)
```

## Known Limitations

1. **Knowledge Base**: Currently uses mock data for AI/ML topics only
2. **Embeddings**: Basic ChromaDB embeddings (sentence-transformers removed for compatibility)
3. **Memory Hits**: Vector similarity search may need tuning for optimal reuse
4. **LLM Dependency**: Advanced features require Groq API key

## Troubleshooting

### Memory System Issues

- Check ChromaDB collection initialization
- Verify storage permissions in `memory_storage/` directory
- Review memory search parameters and thresholds

### Embedding Problems

- System falls back to text-based search automatically
- ChromaDB uses default embeddings when custom ones unavailable
- Check distance thresholds for memory reuse

### Docker Issues

- Ensure ports 8501 is available
- Check Docker Compose logs for initialization errors
- Verify environment variables are properly set

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.
