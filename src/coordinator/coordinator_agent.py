"""
Coordinator Agent - Main orchestrator of the multi-agent system.
Analyzes user queries, determines task complexity, routes to appropriate agents,
coordinates dependencies, and synthesizes final results.
"""
import asyncio
from typing import Dict, Any, List, Optional
from groq import Groq
from loguru import logger
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from memory.memory_agent import MemoryAgent
from models.message import AgentMessage, MessageType, TaskResult

class CoordinatorAgent:
    """
    Main coordinator that orchestrates all other agents.
    Handles task decomposition, agent routing, and result synthesis.
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize coordinator with all worker agents"""
        self.agent_id = "coordinator"
        
        # Initialize worker agents
        self.research_agent = ResearchAgent()
        self.analysis_agent = AnalysisAgent()
        self.memory_agent = MemoryAgent()
        
        # Initialize LLM client if API key provided
        self.groq_client = None
        if groq_api_key:
            try:
                self.groq_client = Groq(api_key=groq_api_key)
                logger.info("Groq LLM client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
        
        # Task execution history
        self.execution_history: List[Dict[str, Any]] = []
        
        logger.info("Coordinator initialized with all agents")
    
    async def process_user_query(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for processing user queries.
        Analyzes complexity, routes to agents, and synthesizes results.
        """
        logger.info(f"Processing user query: {query}")
        
        # Step 1: Analyze query complexity
        task_plan = await self._analyze_query_complexity(query)
        
        # Step 2: Check memory for relevant past information
        memory_context = await self._get_memory_context(query)
        
        # Step 3: Execute task plan
        execution_results = await self._execute_task_plan(query, task_plan, memory_context)
        
        # Step 4: Synthesize final response
        final_response = await self._synthesize_response(query, execution_results)
        
        # Step 5: Store interaction in memory
        await self._store_interaction(query, final_response, execution_results)
        
        return final_response
    
    async def _analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to determine which agents are needed and in what order.
        Uses LLM if available, otherwise falls back to rule-based analysis.
        """
        if self.groq_client:
            try:
                return await self._llm_analyze_complexity(query)
            except Exception as e:
                logger.warning(f"LLM analysis failed, using rule-based: {e}")
        
        return self._rule_based_analyze_complexity(query)
    
    async def _llm_analyze_complexity(self, query: str) -> Dict[str, Any]:
        """Use LLM to analyze query complexity and create task plan"""
        prompt = f"""Analyze this user query and determine what agents are needed:

Query: "{query}"

Available agents:
1. research_agent - finds information on topics
2. analysis_agent - compares, analyzes, evaluates data  
3. memory_agent - stores/retrieves past information

Respond with a JSON plan:
{{
    "complexity": "simple|moderate|complex",
    "agents_needed": ["agent1", "agent2"],
    "execution_order": ["step1", "step2"],
    "reasoning": "explanation"
}}"""

        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.1
        )

        # Parse LLM response (simplified - in production would need better parsing)
        content = response.choices[0].message.content

        # Fallback to rule-based if parsing fails
        try:
            import json
            return json.loads(content)
        except:
            return self._rule_based_analyze_complexity(query)

    def _rule_based_analyze_complexity(self, query: str) -> Dict[str, Any]:
        """Rule-based query analysis as fallback"""
        query_lower = query.lower()

        # Determine agents needed based on keywords
        agents_needed = []
        execution_steps = []

        # Check if research is needed
        if any(word in query_lower for word in ["find", "search", "what", "types", "information", "about"]):
            agents_needed.append("research_agent")
            execution_steps.append("research")

        # Check if analysis is needed
        if any(word in query_lower for word in ["compare", "analyze", "evaluate", "effective", "better", "best"]):
            agents_needed.append("analysis_agent")
            execution_steps.append("analysis")

        # Check if memory is needed
        if any(word in query_lower for word in ["remember", "earlier", "before", "what did", "previous"]):
            agents_needed.append("memory_agent")
            execution_steps.insert(0, "memory_retrieval")  # Memory first

        # Determine complexity
        if len(agents_needed) == 1:
            complexity = "simple"
        elif len(agents_needed) == 2:
            complexity = "moderate"
        else:
            complexity = "complex"

        # Default to research if no specific agents identified
        if not agents_needed:
            agents_needed = ["research_agent"]
            execution_steps = ["research"]
            complexity = "simple"

        return {
            "complexity": complexity,
            "agents_needed": agents_needed,
            "execution_order": execution_steps,
            "reasoning": f"Rule-based analysis: {len(agents_needed)} agents needed"
        }

    async def _get_memory_context(self, query: str) -> Dict[str, Any]:
        """Get relevant context from memory"""
        memory_message = AgentMessage(
            type=MessageType.TASK,
            sender=self.agent_id,
            recipient="memory_agent",
            content=f"search for relevant information about: {query}",
            metadata={"memory_type": "conversation", "limit": 3}
        )

        memory_result = await self.memory_agent.process_task(memory_message)
        return memory_result.data if memory_result.success else {}

    async def _execute_task_plan(self, query: str, task_plan: Dict[str, Any], memory_context: Dict[str, Any]) -> List[TaskResult]:
        """Execute the planned tasks with proper agent coordination"""
        results = []
        accumulated_data = {"memory_context": memory_context}

        for step in task_plan["execution_order"]:
            if step == "research":
                result = await self._execute_research_task(query, accumulated_data)
                results.append(result)
                if result.success:
                    accumulated_data["research_results"] = result.data

            elif step == "analysis":
                result = await self._execute_analysis_task(query, accumulated_data)
                results.append(result)
                if result.success:
                    accumulated_data["analysis_results"] = result.data

            elif step == "memory_retrieval":
                result = await self._execute_memory_task(query, accumulated_data)
                results.append(result)
                if result.success:
                    accumulated_data["memory_results"] = result.data

        return results

    async def _execute_research_task(self, query: str, context: Dict[str, Any]) -> TaskResult:
        """Execute research task"""
        message = AgentMessage(
            type=MessageType.TASK,
            sender=self.agent_id,
            recipient="research_agent",
            content=query,
            metadata=context
        )
        return await self.research_agent.process_task(message)

    async def _execute_analysis_task(self, query: str, context: Dict[str, Any]) -> TaskResult:
        """Execute analysis task"""
        message = AgentMessage(
            type=MessageType.TASK,
            sender=self.agent_id,
            recipient="analysis_agent", 
            content=query,
            metadata={"data": context}
        )
        return await self.analysis_agent.process_task(message)

    async def _execute_memory_task(self, query: str, context: Dict[str, Any]) -> TaskResult:
        """Execute memory task"""
        message = AgentMessage(
            type=MessageType.TASK,
            sender=self.agent_id,
            recipient="memory_agent",
            content=query,
            metadata=context
        )
        return await self.memory_agent.process_task(message)

    async def _synthesize_response(self, query: str, results: List[TaskResult]) -> Dict[str, Any]:
        """Synthesize final response from all agent results"""
        response = {
            "query": query,
            "success": all(r.success for r in results),
            "agent_results": {},
            "synthesized_answer": "",
            "confidence": 0.0,
            "execution_trace": []
        }

        # Collect results from each agent
        total_confidence = 0
        successful_agents = 0

        for result in results:
            if result.success:
                response["agent_results"][result.agent_id] = {
                    "data": result.data,
                    "confidence": result.confidence,
                    "execution_time": result.execution_time
                }
                total_confidence += result.confidence
                successful_agents += 1

                response["execution_trace"].append({
                    "agent": result.agent_id,
                    "success": True,
                    "execution_time": result.execution_time
                })
            else:
                response["execution_trace"].append({
                    "agent": result.agent_id,
                    "success": False,
                    "error": result.error
                })
        
        # Calculate overall confidence
        if successful_agents > 0:
            response["confidence"] = total_confidence / successful_agents
        
        # Generate synthesized answer
        response["synthesized_answer"] = self._generate_synthesized_answer(query, response["agent_results"])
        
        return response
    
    def _generate_synthesized_answer(self, query: str, agent_results: Dict[str, Any]) -> str:
        """Generate final answer by combining agent results"""
        answer_parts = []
        
        # Add research findings
        if "research_agent" in agent_results:
            research_data = agent_results["research_agent"]["data"]
            if "research_results" in research_data:
                results = research_data["research_results"]
                if results:
                    answer_parts.append(f"Research findings: Found information about {', '.join(results.keys())}")
        
        # Add analysis insights
        if "analysis_agent" in agent_results:
            analysis_data = agent_results["analysis_agent"]["data"]
            if "analysis" in analysis_data:
                analysis = analysis_data["analysis"]
                if "findings" in analysis:
                    answer_parts.append(f"Analysis: {analysis['findings']}")
        
        # Add memory context
        if "memory_agent" in agent_results:
            memory_data = agent_results["memory_agent"]["data"]
            if "results" in memory_data and memory_data["results"]:
                answer_parts.append("Found relevant information from previous conversations")
        
        if answer_parts:
            return ". ".join(answer_parts) + "."
        else:
            return "I processed your query but couldn't find specific information to answer it."
    
    async def _store_interaction(self, query: str, response: Dict[str, Any], results: List[TaskResult]):
        """Store the interaction in memory for future reference"""
        memory_message = AgentMessage(
            type=MessageType.TASK,
            sender=self.agent_id,
            recipient="memory_agent",
            content=f"User asked: {query}",
            metadata={
                "data": {
                    "query": query,
                    "response": response["synthesized_answer"],
                    "agents_used": list(response["agent_results"].keys()),
                    "confidence": response["confidence"]
                },
                "memory_type": "conversation",
                "source": "coordinator"
            }
        )
        
        await self.memory_agent.process_task(memory_message)