import asyncio
from coordinator.coordinator_agent import CoordinatorAgent
from models.message import AgentMessage, MessageType


async def run():
    coord = CoordinatorAgent()

    query = "Research transformer architectures and summarize tradeoffs"

    # 1) Cold run (should perform research)
    cold = await coord.process_user_query(query)
    cold_trace = cold.get("execution_trace", [])
    cold_research = next((t for t in cold_trace if t.get("agent") == "research_agent"), {})
    print("\n--- Cold run ---")
    print("Research exec time:", cold_research.get("execution_time"))
    print("Synthesis:\n", cold.get("synthesized_answer", ""))

    # 2) Seed memory with two relevant conversation notes
    for note in [
        "store: previous finding about transformers efficiency tradeoffs",
        "store: prior summary mentioning transformer architectures and their costs",
    ]:
        await coord.memory_agent.process_task(
            AgentMessage(
                type=MessageType.TASK,
                sender="tester",
                recipient="memory_agent",
                content=note,
                metadata={
                    "memory_type": "conversation",
                    "data": {"topic": "transformers", "note": note},
                },
            )
        )

    # 3) Warm run (should reuse memory and skip research)
    warm = await coord.process_user_query(query)
    warm_trace = warm.get("execution_trace", [])
    warm_research = next((t for t in warm_trace if t.get("agent") == "research_agent"), {})

    print("\n--- Warm run (after seeding memory) ---")
    print("Research exec time:", warm_research.get("execution_time"))
    print("Synthesis:\n", warm.get("synthesized_answer", ""))

    # Heuristic check: research exec time should be 0.0 in warm run
    reused = warm_research.get("execution_time") == 0.0
    print("\nAdaptive reuse engaged:", reused)


if __name__ == "__main__":
    asyncio.run(run())


