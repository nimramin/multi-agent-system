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
    MEMORY_REUSE_DISTANCE_THRESHOLD = 0.8

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

    def _normalize_memory_context(self, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize various possible memory_agent return shapes into a predictable structure:
        {
        "results": [ { "content": ..., "metadata": ..., "distance": float|None, "id": ... }, ... ],
        "count": int,
        "best_distance": float|None
        }
        """
        if not memory_context:
            return {"results": [], "count": 0, "best_distance": None}

        # memory_agent returns 'results' for search, or 'memories' for retrieve recent.
        results = []
        if isinstance(memory_context, dict):
            if "results" in memory_context and isinstance(memory_context["results"], list):
                results = memory_context["results"]
            elif "memories" in memory_context and isinstance(memory_context["memories"], list):
                # normalize retrieve -> results with metadata shape similar to search hits
                results = []
                for m in memory_context["memories"]:
                    results.append({
                        "content": m.get("content") or m.get("data") or m.get("content", ""),
                        "metadata": {k: v for k, v in m.items() if k not in ("content", "data")},
                        "distance": m.get("distance") if "distance" in m else None,
                        "id": m.get("id")
                    })
            elif "memories" in memory_context and isinstance(memory_context["memories"], dict):
                # defensive: sometimes metadata carriers differ
                results = memory_context["memories"]
            # if memory_context itself looks like search response
            elif "action" in memory_context and memory_context.get("action") in ("searched", "retrieved"):
                # try to extract generic fields
                if "results" in memory_context:
                    results = memory_context["results"]
                elif "memories" in memory_context:
                    results = memory_context["memories"]

        # Ensure each result has distance key (may be None)
        best_distance = None
        for r in results:
            if isinstance(r, dict):
                d = r.get("distance", None)
                if d is not None:
                    try:
                        d_float = float(d)
                        if best_distance is None or d_float < best_distance:
                            best_distance = d_float
                    except Exception:
                        pass

        return {"results": results, "count": len(results), "best_distance": best_distance}

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
            # model="llama3-8b-8192",
            model="openai/gpt-oss-20b",
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
            
            # If we need to compare/analyze, we should also research first to get data
            if "research_agent" not in agents_needed:
                agents_needed.insert(0, "research_agent")
                execution_steps.insert(0, "research")

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
        """Get relevant context from memory. Always returns a normalized dict."""
        # Basic keywords extraction (keep existing logic but ensure metadata fields used by MemoryAgent)
        stop_words = {"the","a","an","and","or","but","in","on","at","to","for","of","with","by","about","is","are","what","find","search","retrieve","get"}
        query_words = query.lower().split()
        meaningful_words = [w.strip('.,:;!?#()[]{}"\'') for w in query_words if w not in stop_words and len(w) > 2]
        # Include both exact query and key terms
        search_content = f"{query} {' '.join(meaningful_words[:10])}"

        memory_message = AgentMessage(
            type=MessageType.TASK,
            sender=self.agent_id,
            recipient="memory_agent",
            content=search_content,  # Use enhanced search content
            metadata={
                "memory_type": "conversation",
                "limit": 5,
                "keywords": meaningful_words[:8]
            }
        )

        memory_result = await self.memory_agent.process_task(memory_message)
        # memory_result.data is expected to be a dict like {"action":"searched","results":[...],...}
        raw = memory_result.data if memory_result.success else {}
        normalized = self._normalize_memory_context(raw)
        # keep original raw (in case we want to persist full memory response)
        normalized["_raw"] = raw
        return normalized


    async def _execute_task_plan(self, query: str, task_plan: Dict[str, Any], memory_context: Dict[str, Any]) -> List[TaskResult]:
        results: List[TaskResult] = []
        accumulated_data = {"memory_context": memory_context}

        # Always append a memory_agent TaskResult (whether hits or not)
        mem_results = memory_context.get("results", []) if isinstance(memory_context, dict) else []
        memory_count = len(mem_results)
        best_distance = memory_context.get("best_distance") if isinstance(memory_context, dict) else None

        # Heuristic: prefer reuse if best_distance is present and below threshold,
        # Decide skip_research
        reuse_based_on_distance = (best_distance is not None and best_distance <= 0.8)
        reuse_based_on_count = (memory_count >= 2)  # Reduced from 3 to 2
        skip_research = reuse_based_on_distance or reuse_based_on_count

        memory_trace = TaskResult(
            agent_id="memory_agent",
            success=True,
            data={
                "results": mem_results,
                "count": memory_count,
                "best_distance": best_distance,
                "used": bool(skip_research),        # Did memory influence plan / replace research?
                "consulted": True
            },
            confidence=0.6 if memory_count > 0 else 0.3,
            execution_time=0.0
        )
        results.append(memory_trace)
    

        # Trace memory usage if any
        if memory_count > 0:
            memory_trace = TaskResult(
                agent_id="memory_agent",
                success=True,
                data={"results": mem_results, "count": memory_count, "best_distance": best_distance},
                confidence=0.6 if best_distance is None else max(0.1, 1.0 - float(best_distance)),
                execution_time=0.0
            )
            results.append(memory_trace)

        for step in task_plan.get("execution_order", []):
            if step == "research":
                if skip_research:
                    # Normalize memory hits into a research_results dict that AnalysisAgent expects
                    synthetic_data = {
                        "research_results": {
                            "source": "memory",
                            "hits": mem_results,
                            "best_distance": best_distance,
                            "reused": True
                        }
                    }
                    synthetic = TaskResult(
                        agent_id="research_agent",
                        success=True,
                        data=synthetic_data,
                        confidence=memory_trace.confidence if memory_count > 0 else 0.5,
                        execution_time=0.0
                    )
                    results.append(synthetic)
                    # keep accumulated_data consistent: analysis expects accumulated_data["research_results"] to be dict
                    accumulated_data["research_results"] = synthetic_data["research_results"]
                else:
                    result = await self._execute_research_task(query, accumulated_data)
                    results.append(result)
                    if result.success:
                        # Ensure we store research_results as a dict under accumulated_data
                        if isinstance(result.data, dict) and "research_results" in result.data:
                            accumulated_data["research_results"] = result.data["research_results"]
                        else:
                            # fallback wrap
                            accumulated_data["research_results"] = {"source": "fresh_research", "hits": result.data}
            elif step == "analysis":
                result = await self._execute_analysis_task(query, accumulated_data)
                results.append(result)
                if result.success:
                    accumulated_data["analysis_results"] = result.data
            elif step == "memory_retrieval":
                result = await self._execute_memory_task(query, accumulated_data)
                results.append(result)
                if result.success:
                    # Normalize store of memory retrieval data
                    data = result.data if isinstance(result.data, dict) else {"result": result.data}
                    accumulated_data["memory_results"] = data

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
        # #Generate synthesized answer
        # response["synthesized_answer"] = self._generate_synthesized_answer(query, response["agent_results"])
        # Generate detailed answer
        response["synthesized_answer"] = self._generate_detailed_answer(query, response["agent_results"])
        
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
    
    def _generate_detailed_answer(self, query: str, agent_results: Dict[str, Any]) -> str:
        """Generate detailed, comprehensive answer by extracting and formatting all available information"""
        
         # Check if research agent detected a knowledge limitation
        if "research_agent" in agent_results:
            research_data = agent_results["research_agent"]["data"]
            if research_data.get("limitation_detected"):
                limitation_info = research_data["research_results"].get("knowledge_limitation", {})
                return limitation_info.get("message", "I don't have information about this topic in my knowledge base.")
    
        answer_parts = []
        
        # Add detailed research findings
        if "research_agent" in agent_results:
            research_data = agent_results["research_agent"]["data"]
            if "research_results" in research_data:
                results = research_data["research_results"]
                if results:
                    answer_parts.append("Based on my research, I found the following information:")
                    # Support both dict-shaped KB results and memory reuse list results
                    if isinstance(results, dict):
                        for topic, data in results.items():
                            topic_name = topic.replace('_', ' ').title()
                            answer_parts.append(f"\n**{topic_name}:**")
                            if isinstance(data, dict):
                                if "description" in data:
                                    answer_parts.append(f"{data['description']}")
                                if "types" in data and data["types"]:
                                    answer_parts.append(f"The main types include: {', '.join(data['types'])}")
                                if "applications" in data and data["applications"]:
                                    answer_parts.append(f"These are commonly used for: {', '.join(data['applications'])}")
                                if "algorithms" in data and data["algorithms"]:
                                    answer_parts.append(f"Key algorithms include: {', '.join(data['algorithms'])}")
                                if "optimization" in data and data["optimization"]:
                                    answer_parts.append(f"Common optimization techniques: {', '.join(data['optimization'])}")
                                if "architectures" in data and data["architectures"]:
                                    answer_parts.append(f"Popular architectures: {', '.join(data['architectures'])}")
                                if "efficiency" in data and isinstance(data["efficiency"], dict):
                                    efficiency_info = [f"{k}: {v}" for k, v in data["efficiency"].items()]
                                    answer_parts.append(f"Efficiency considerations: {', '.join(efficiency_info)}")
                                if "tradeoffs" in data:
                                    answer_parts.append(f"Key tradeoffs: {data['tradeoffs']}")
                            else:
                                # If data is a string, just include it
                                answer_parts.append(str(data))
                    elif isinstance(results, list):
                        # Memory reuse path: results are search hits from memory
                        hits = results[:3]
                        for hit in hits:
                            meta = hit.get("metadata", {})
                            snippet = hit.get("content", "").split("\n")[0]
                            topic = meta.get("topic") or "Previous Context"
                            answer_parts.append(f"\n**{topic}:** {snippet[:240]}")
        
        # Add detailed analysis insights
        if "analysis_agent" in agent_results:
            analysis_data = agent_results["analysis_agent"]["data"]
            if "analysis" in analysis_data:
                analysis = analysis_data["analysis"]
                answer_parts.append("\n**Analysis:**")
                
                if "analysis_type" in analysis:
                    answer_parts.append(f"Analysis type: {analysis['analysis_type']}")
                
                if "findings" in analysis:
                    answer_parts.append(f"Key findings: {analysis['findings']}")
                
                if "insights" in analysis and isinstance(analysis["insights"], list):
                    insights_list = "; ".join(analysis["insights"])
                    answer_parts.append(f"Insights: {insights_list}")
                
                if "recommendation" in analysis:
                    answer_parts.append(f"Recommendation: {analysis['recommendation']}")
                
                if "metrics" in analysis and isinstance(analysis["metrics"], dict):
                    metrics_info = []
                    for key, value in analysis["metrics"].items():
                        metrics_info.append(f"{key}: {value}")
                    answer_parts.append(f"Metrics: {', '.join(metrics_info)}")
        
        # Add memory context
        if "memory_agent" in agent_results:
            memory_data = agent_results["memory_agent"]["data"]
            if "results" in memory_data and memory_data["results"]:
                answer_parts.append("\n**Previous Context:**")
                answer_parts.append("I found relevant information from our previous conversations that relates to your question.")
        
        if answer_parts:
            return "\n".join(answer_parts)
        else:
            return "I processed your query but couldn't find specific information to answer it. Please try rephrasing your question or asking about a different topic."
    
    async def _store_interaction(self, query: str, response: Dict[str, Any], results: List[TaskResult]):
        """Store the interaction in memory for future reference"""
        memory_message = AgentMessage(
            type=MessageType.TASK,
            sender=self.agent_id,
            recipient="memory_agent",
            content=f"{query}",
            metadata={
                "data": {
                    "query": query,
                    "response": response["synthesized_answer"],
                    "agents_used": list(response["agent_results"].keys()),
                    "confidence": response["confidence"]
                },
                "memory_type": "conversation",
                "source": "coordinator",
                "raw_answer": response["synthesized_answer"]
            },
        )
        
        await self.memory_agent.process_task(memory_message)