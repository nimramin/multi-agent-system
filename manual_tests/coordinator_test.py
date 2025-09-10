import asyncio
from coordinator.coordinator_agent import CoordinatorAgent
from models.message import AgentMessage, MessageType

coord = CoordinatorAgent()

async def go():
    # seed a convo memory
    await coord.memory_agent.process_task(
        AgentMessage(
            type=MessageType.TASK,
            sender="coordinator",
            recipient="memory_agent",
            content="store: previous finding about transformers tradeoffs",
            metadata={
                "memory_type": "conversation",
                "data": {"topic": "transformers", "note": "tradeoffs noted"}
            }
        )
    )
    # query that should reuse memory via keywords
    res = await coord.process_user_query("Research transformer architectures and summarize tradeoffs")
    print(res["synthesized_answer"])

asyncio.run(go())