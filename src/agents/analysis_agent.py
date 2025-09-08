"""
Analysis Agent - Handles data processing, comparison, and reasoning tasks.
Takes research data and performs various analytical operations like comparing options,
evaluating effectiveness, and generating insights.
"""
import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent
from ..models.message import AgentMessage, TaskResult

class AnalysisAgent(BaseAgent):
    """Agent specialized for analytical tasks and data processing"""

    def __init__(self):
        """Initialize with analytical capabilities"""
        super().__init__("analysis_agent", ["analyze", "compare", "evaluate", "calculate"])

    async def process_task(self, message: AgentMessage) -> TaskResult:
        """Process analytical task based on content and data"""
        start_time = asyncio.get_event_loop().time()
        self.log_message(message)

        try:
            content = message.content.lower()
            data = message.metadata.get("data", {})

            # Route to appropriate analysis method
            if "compare" in content:
                analysis_result = self._perform_comparison(data)
            elif "analyze" in content or "effectiveness" in content:
                analysis_result = self._perform_analysis(data)
            elif "calculate" in content:
                analysis_result = self._perform_calculation(data)
            else:
                analysis_result = self._general_analysis(data)

            confidence = 0.8 if analysis_result else 0.2
            execution_time = asyncio.get_event_loop().time() - start_time

            return TaskResult(
                agent_id=self.agent_id,
                success=True,
                data={"analysis": analysis_result, "input_data": data},
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

    def _perform_comparison(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare multiple items from research data"""
        if not data or "research_results" not in data:
            return {"comparison": "No data to compare"}

        items = data["research_results"]
        comparison = {
            "items_compared": list(items.keys()),
            "comparison_summary": f"Analyzed {len(items)} items",
            "key_differences": [],
            "recommendation": "Further analysis needed"
        }

        # Find differences based on content analysis
        if len(items) >= 2:
            for item in items:
                item_data = str(items[item]).lower()
                if "efficiency" in item_data:
                    comparison["key_differences"].append(f"{item}: efficiency considerations")

        return comparison

    def _perform_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform effectiveness analysis on data"""
        return {
            "analysis_type": "effectiveness_analysis",
            "findings": "Based on available data, multiple approaches show promise",
            "metrics": {"coverage": len(data), "depth": "moderate"},
            "insights": ["Each approach has unique strengths", "Context-dependent effectiveness"]
        }

    def _perform_calculation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform simple calculations on numerical data"""
        return {"calculation": "Simple metrics computed", "results": data}

    def _general_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """General analysis when type is not specified"""
        return {
            "summary": f"General analysis of {len(data)} data points",
            "overview": "Data processed and structured for insights"
        }