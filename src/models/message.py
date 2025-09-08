# src/models/message.py
"""
Message Models - Pydantic models for structured communication between agents.
Defines standard message formats for task routing, results, and error handling.
Ensures type safety and consistent data structures across the system.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    """Types of messages that can be sent between agents"""
    QUERY = "query"    # User input queries
    TASK = "task"      # Task assignments
    RESULT = "result"  # Task completion results
    ERROR = "error"    # Error messages

class AgentMessage(BaseModel):
    """Standard message format for agent communication"""
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    type: MessageType
    sender: str        # Agent ID that sent the message
    recipient: str     # Agent ID that should receive it
    content: str       # Main message content
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional context
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: Optional[float] = None  # Confidence in message content

class TaskResult(BaseModel):
    """Standardized result format returned by agents"""
    agent_id: str           # Which agent produced this result
    success: bool           # Whether task completed successfully
    data: Dict[str, Any]    # The actual result data
    confidence: float       # Agent's confidence in result
    execution_time: float   # Task execution time
    error: Optional[str] = None  # Error message if task failed