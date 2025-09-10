"""
Research Agent - Handles information retrieval and search tasks.
Uses a mock knowledge base to simulate web search functionality.
Searches for topics like neural networks, machine learning, etc.
"""
import asyncio
from typing import Dict, Any
from agents.base_agent import BaseAgent
from models.message import AgentMessage, TaskResult

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
                # Check for meaningful query words (excluding common stop words)
                stop_words = {'what', 'is', 'are', 'how', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'from', 'can', 'you', 'tell', 'me'}
                query_words = [word for word in query.split() if word not in stop_words and len(word) > 2]
                
                # Only do fuzzy search if we have meaningful words
                if query_words:
                    for topic, data in self.knowledge_base.items():
                        data_text = str(data).lower()
                        matching_words = sum(1 for word in query_words if word in data_text)
                        
                        # Only include if at least 30% of meaningful query words match
                        if len(query_words) > 0 and (matching_words / len(query_words)) >= 0.3:
                            results[topic] = data
                            confidence += 0.2

            # If still no results, check if this is outside our domain
            if not results:
                # Check if the query is asking about our domain topics at all
                domain_keywords = ['neural', 'network', 'machine', 'learning', 'transformer', 'ai', 'artificial', 'intelligence', 'algorithm', 'model', 'training', 'data', 'deep', 'classification', 'regression', 'supervised', 'unsupervised', 'reinforcement']
                
                has_domain_keywords = any(keyword in query for keyword in domain_keywords)
                
                if not has_domain_keywords:
                    # Query is outside our domain - return limitation message
                    return TaskResult(
                        agent_id=self.agent_id,
                        success=True,  # This is successful - we successfully identified it's outside our domain
                        data={
                            "research_results": {
                                "knowledge_limitation": {
                                    "message": f"I don't have specific information about '{message.content}' in my current knowledge base. My expertise covers machine learning, neural networks, transformers, optimization techniques, and related AI topics. Could you ask about one of these areas instead?",
                                    "domain": "AI/ML topics only",
                                    "suggested_topics": ["neural networks", "machine learning algorithms", "transformer architectures", "optimization techniques"]
                                }
                            },
                            "query": query,
                            "limitation_detected": True
                        },
                        confidence=0.9,  # High confidence that we don't know this topic
                        execution_time=asyncio.get_event_loop().time() - start_time
                    )

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