"""
Base Agent Abstract Class - Foundation for all agents in the system.
Provides common functionality like message handling, capabilities, and logging.
All specialized agents inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from loguru import logger
from ..models.message import AgentMessage, TaskResult

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        """Initialize agent with ID and capabilities"""
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.message_history: List[AgentMessage] = []
        logger.info(f"Initialized {agent_id} with capabilities: {capabilities}")
    
    @abstractmethod
    async def process_task(self, message: AgentMessage) -> TaskResult:
        """Process a task message and return results - must be implemented by subclasses"""
        pass
    
    def can_handle_task(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type"""
        return task_type in self.capabilities
    
    def log_message(self, message: AgentMessage):
        """Log and store received message for history tracking"""
        self.message_history.append(message)
        logger.info(f"{self.agent_id} received: {message.type} from {message.sender}")