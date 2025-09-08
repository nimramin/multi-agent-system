"""
Research Agent - Handles information retrieval and search tasks.
Uses a mock knowledge base to simulate web search functionality.
Searches for topics like neural networks, machine learning, etc.
"""
import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent
from ..models.message import AgentMessage, TaskResult

class ResearchAgent(BaseAgent):
    """Agent specialized for research and information retrieval"""
    def __init__(self):
        """Initialize with search capabilities and mock knowledge base"""
        super().__init__("research_agent", ["search", "retrieve", "find"])

        # Mock knowledge base - simulates external data sources
        self.knowledge_base = {
            "neural_networks": {
                "types": ["CNN", "RNN", "LSTM", "GRU", "Transformer"],
                "applications": ["image recognition", "NLP", "time series"],
                "description": "Neural networks are computing systems inspired by biological neural networks"
            },
            "machine_learning": {
                "algorithms": ["SVM", "Random Forest", "Gradient Boosting", "Neural Networks"],
                "types": ["supervised", "unsupervised", "reinforcement"],
                "optimization": ["gradient descent", "adam", "rmsprop", "adagrad"]
            },
            "transformers": {
                "architectures": ["BERT", "GPT", "T5", "BART"],
                "efficiency": {"BERT": "high memory", "GPT": "autoregressive", "T5": "text-to-text"},
                "tradeoffs": "computational cost vs performance"
            }
        }

    async def process_task(self, message: AgentMessage) -> TaskResult:
        """Process research query and return relevant information"""
        start_time = asyncio.get_event_loop().time()
        self.log_message(message)

        try:
            query = message.content.lower()
            results = {}
            confidence = 0.0

            # Direct keyword matching in topic names
            for topic, data in self.knowledge_base.items():
                if any(keyword in query for keyword in topic.split('_')):
                    results[topic] = data
                    confidence += 0.3

            # Fuzzy search in content if no direct matches
            if not results:
                for topic, data in self.knowledge_base.items():
                    if any(word in str(data).lower() for word in query.split()):
                        results[topic] = data
                        confidence += 0.2

            confidence = min(confidence, 1.0)
            execution_time = asyncio.get_event_loop().time() - start_time

            return TaskResult(
                agent_id=self.agent_id,
                success=bool(results),
                data={"research_results": results, "query": query},
                confidence=confidence,
                execution_time=execution_time
            )

        except Exception as e:
            return TaskResult(
                agent_id=self.agent_id,
                success=False,
                data={},
                confidence=0.0,
                execution_time=asyncio.get_event_loop().time() - start_time,
                error=str(e)
            )