# Multi-Agent Chat System

A multi-agent system where a Coordinator orchestrates Research, Analysis, and Memory agents with ChromaDB vector storage and LLM integration.

## Quick Start

```bash
# Using UV (recommended)
uv run python generate_outputs.py  # Generate all test outputs
uv run streamlit run app_compatible.py  # Start web interface

# Using Docker
docker-compose up --build  # Start web service
docker-compose run --rm test-runner  # Run tests
```

## Architecture

- **Coordinator Agent**: Task analysis, routing, and result synthesis
- **Research Agent**: Information retrieval from mock knowledge base
- **Analysis Agent**: Data comparison, reasoning, and calculations
- **Memory Agent**: ChromaDB vector storage with conversation history

## Architecture Diagram

```mermaid
graph TD
    U[User Interface<br/>Streamlit] --> C[Coordinator Agent]

    C --> RA[Research Agent]
    C --> AA[Analysis Agent]
    C --> MA[Memory Agent]

    RA --> KB[(Knowledge Base)]
    C --> LLM[Groq LLM]

    MA --> VDB[(ChromaDB Vector Store)]
    MA --> JSON[(JSON Metadata)]
    MA --> CACHE[In-Memory Cache]

    subgraph Memory
        VDB
        JSON
        CACHE
    end


## Test Scenarios

All 5 required scenarios included:
1. Simple Query: "What are the main types of neural networks?"
2. Complex Query: Transformer architectures analysis
3. Memory Test: Previous conversation retrieval
4. Multi-step: Reinforcement learning research pipeline
5. Collaborative: ML approach comparison

## Features

- Vector semantic search with ChromaDB
- Memory reuse to avoid redundant research
- Groq LLM integration (optional)
- Comprehensive execution tracing
- Confidence scoring per agent
- Web and console interfaces

## Project Structure

```

├── src/agents/ - All agent implementations
├── src/coordinator/ - Main orchestrator  
├── src/memory/ - Memory management
├── outputs/ - Test scenario results
├── docker-compose.yml - Container orchestration
└── generate_outputs.py - Test runner

```

## Memory System

- **Vector Search**: ChromaDB with similarity matching
- **Structured Storage**: JSON metadata with timestamps
- **Context Reuse**: Avoids redundant queries via distance thresholds

## Requirements

- Python 3.9+, UV package manager
- ChromaDB, Streamlit, Groq (optional)
- Docker for containerized deployment
```
