"""
Tests for message models and data structures.
Ensures Pydantic models work correctly and validate data properly.
"""
import pytest
from datetime import datetime
from src.models.message import AgentMessage, TaskResult, MessageType

def test_agent_message_creation():
    """Test that AgentMessage creates correctly with required fields"""
    message = AgentMessage(
        type=MessageType.QUERY,
        sender="test_sender",
        recipient="test_recipient",
        content="Test message"
    )

    assert message.type == MessageType.QUERY
    assert message.sender == "test_sender"
    assert message.recipient == "test_recipient"
    assert message.content == "Test message"
    assert isinstance(message.timestamp, datetime)
    assert message.metadata == {}
    print("✅ AgentMessage creation test passed")

def test_task_result_creation():
    """Test TaskResult model creation and validation"""
    result = TaskResult(
        agent_id="test_agent",
        success=True,
        data={"key": "value"},
        confidence=0.8,
        execution_time=1.5
    )

    assert result.agent_id == "test_agent"
    assert result.success == True
    assert result.data == {"key": "value"}
    assert result.confidence == 0.8
    assert result.execution_time == 1.5
    assert result.error is None
    print("✅ TaskResult creation test passed")