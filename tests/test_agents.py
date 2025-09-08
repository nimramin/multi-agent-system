"""
Tests for agent functionality and communication.
Validates that agents can process tasks and return proper results.
"""
import pytest
import asyncio
from src.agents.research_agent import ResearchAgent
from src.agents.analysis_agent import AnalysisAgent
from src.models.message import AgentMessage, MessageType

@pytest.mark.asyncio
async def test_research_agent_basic():
    """Test Research Agent can handle basic queries"""
    agent = ResearchAgent()

    # Test agent initialization
    assert agent.agent_id == "research_agent"
    assert "search" in agent.capabilities
    assert "retrieve" in agent.capabilities

    # Test task processing
    message = AgentMessage(
        type=MessageType.TASK,
        sender="coordinator",
        recipient="research_agent",
        content="neural networks"
    )

    result = await agent.process_task(message)

    assert result.success == True
    assert result.agent_id == "research_agent"
    assert "research_results" in result.data
    assert result.confidence > 0
    print("✅ Research Agent basic test passed")

@pytest.mark.asyncio
async def test_analysis_agent_basic():
    """Test Analysis Agent can handle basic analysis tasks"""
    agent = AnalysisAgent()

    # Test agent initialization
    assert agent.agent_id == "analysis_agent"
    assert "analyze" in agent.capabilities
    assert "compare" in agent.capabilities

    # Test analysis task
    message = AgentMessage(
        type=MessageType.TASK,
        sender="coordinator",
        recipient="analysis_agent",
        content="analyze effectiveness",
        metadata={"data": {"test": "data"}}
    )

    result = await agent.process_task(message)

    assert result.success == True
    assert result.agent_id == "analysis_agent"
    assert "analysis" in result.data
    assert result.confidence > 0
    print("✅ Analysis Agent basic test passed")

@pytest.mark.asyncio
async def test_research_agent_knowledge_retrieval():
    """Test that Research Agent can find information from knowledge base"""
    agent = ResearchAgent()

    message = AgentMessage(
        type=MessageType.TASK,
        sender="coordinator",
        recipient="research_agent",
        content="machine learning optimization"
    )

    result = await agent.process_task(message)

    assert result.success == True
    assert "research_results" in result.data
    assert "machine_learning" in result.data["research_results"]
    assert "optimization" in str(result.data["research_results"]["machine_learning"])
    print("✅ Research Agent knowledge retrieval")