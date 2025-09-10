"""
Pytest configuration and fixtures.
Sets up common test utilities and environment.
"""
import sys
import os
import asyncio
import pytest
import pytest_asyncio

# Add src directory to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Provide async fixtures to satisfy tests expecting `agent` and `memory_id`
from memory.memory_agent import MemoryAgent
from models.message import AgentMessage, MessageType

@pytest_asyncio.fixture(scope="module")
async def agent(tmp_path_factory):
    storage = str(tmp_path_factory.mktemp("test_mem_store"))
    ag = MemoryAgent(storage_path=storage)
    yield ag

@pytest_asyncio.fixture
async def memory_id(agent):
    msg = AgentMessage(
        type=MessageType.TASK,
        sender="test",
        recipient="memory_agent",
        content="store information about neural networks",
        metadata={
            "data": {"topic": "neural networks", "content": "Neural networks are powerful"},
            "memory_type": "conversation"
        }
    )
    res = await agent.process_task(msg)
    return res.data.get("memory_id")