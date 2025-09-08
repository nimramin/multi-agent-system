"""
Simple demonstration script to show agents working.
This script shows basic agent functionality without full system integration.
"""
import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.research_agent import ResearchAgent
from src.agents.analysis_agent import AnalysisAgent  
from src.models.message import AgentMessage, MessageType

async def demo_agents():
    """Demonstrate basic agent functionality"""
    print("🚀 Multi-Agent System Demo")
    print("=" * 40)
    
    # Initialize agents
    research_agent = ResearchAgent()
    analysis_agent = AnalysisAgent()
    
    print(f"✅ Initialized {research_agent.agent_id}")
    print(f"✅ Initialized {analysis_agent.agent_id}")
    
    # Demo 1: Research Agent
    print("\n🔍 Demo 1: Research Agent Query")
    research_msg = AgentMessage(
        type=MessageType.TASK,
        sender="demo",
        recipient="research_agent",
        content="What are neural networks?"
    )
    
    research_result = await research_agent.process_task(research_msg)
    print(f"Success: {research_result.success}")
    print(f"Confidence: {research_result.confidence:.2f}")
    print(f"Results found: {len(research_result.data.get('research_results', {}))}")
    
    # Demo 2: Analysis Agent  
    print("\n📊 Demo 2: Analysis Agent")
    analysis_msg = AgentMessage(
        type=MessageType.TASK,
        sender="demo", 
        recipient="analysis_agent",
        content="analyze the effectiveness of these approaches",
        metadata={"data": research_result.data}
    )
    
    analysis_result = await analysis_agent.process_task(analysis_msg)
    print(f"Success: {analysis_result.success}")
    print(f"Confidence: {analysis_result.confidence:.2f}")
    print(f"Analysis type: {analysis_result.data.get('analysis', {}).get('analysis_type', 'N/A')}")
    
    print("\n🎉 Demo completed successfully!")

if __name__ == "__main__":
    asyncio.run(demo_agents())