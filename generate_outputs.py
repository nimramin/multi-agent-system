#!/usr/bin/env python3
"""
Generate sample outputs for the 5 required test scenarios.
This script runs the multi-agent system with predefined queries and saves outputs.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add src to path and handle imports properly
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from coordinator.coordinator_agent import CoordinatorAgent
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import method...")
    
    # Alternative: try importing with absolute imports
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "coordinator_agent", 
        src_path / "coordinator" / "coordinator_agent.py"
    )
    coordinator_module = importlib.util.module_from_spec(spec)
    sys.modules["coordinator_agent"] = coordinator_module
    spec.loader.exec_module(coordinator_module)
    CoordinatorAgent = coordinator_module.CoordinatorAgent

class OutputGenerator:
    def __init__(self):
        self.coordinator = CoordinatorAgent()
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(exist_ok=True)
        
        # Configure logger for this session
        logger.remove()  # Remove default handler
        logger.add(
            sys.stdout, 
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
    
    async def run_scenario(self, scenario_name: str, query: str, filename: str):
        """Run a single test scenario and save output"""
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario_name}")
        print(f"QUERY: {query}")
        print(f"{'='*60}")
        
        try:
            # Process query
            response = await self.coordinator.process_user_query(query)
            
            # Prepare output content
            output_content = [
                f"Multi-Agent System Test Output",
                f"Scenario: {scenario_name}",
                f"Query: {query}",
                f"Timestamp: {datetime.now().isoformat()}",
                f"{'='*60}",
                "",
                f"RESPONSE:",
                response.get('response', 'No response generated'),
                "",
                f"CONFIDENCE: {response.get('confidence', 0.0):.2f}",
                "",
                f"AGENT EXECUTION TRACE:",
            ]
            
            # Add trace information
            trace = response.get('trace', [])
            if trace:
                for i, step in enumerate(trace, 1):
                    output_content.extend([
                        f"Step {i}: {step.get('agent', 'Unknown Agent')}",
                        f"  Action: {step.get('action', 'No action recorded')}",
                        f"  Result: {step.get('result', 'No result recorded')[:200]}{'...' if len(step.get('result', '')) > 200 else ''}",
                        f"  Timestamp: {step.get('timestamp', 'No timestamp')}",
                        ""
                    ])
            else:
                output_content.append("No trace information available")
            
            # Add memory state
            output_content.extend([
                "",
                f"MEMORY STATE:",
                f"Conversations stored: {len(self.coordinator.memory_agent.conversation_memory)}",
                f"Knowledge entries: {len(self.coordinator.memory_agent.knowledge_base)}",
                ""
            ])
            
            # Save to file
            output_file = self.outputs_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_content))
            
            print(f"\nRESPONSE: {response.get('response', 'No response')}")
            print(f"CONFIDENCE: {response.get('confidence', 0.0):.2f}")
            print(f"OUTPUT SAVED TO: {output_file}")
            
            # Add delay between scenarios
            await asyncio.sleep(2)
            
        except Exception as e:
            error_msg = f"Error processing scenario '{scenario_name}': {str(e)}"
            print(f"ERROR: {error_msg}")
            logger.error(error_msg)
            
            # Still save error output
            output_file = self.outputs_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Error occurred during scenario execution:\n{error_msg}")

    async def generate_all_outputs(self):
        """Generate outputs for all required test scenarios"""
        scenarios = [
            {
                "name": "Simple Query",
                "query": "What are the main types of neural networks?",
                "filename": "simple_query.txt"
            },
            {
                "name": "Complex Query",
                "query": "Research transformer architectures, analyze their computational efficiency, and summarize key trade-offs.",
                "filename": "complex_query.txt"
            },
            {
                "name": "Memory Test",
                "query": "What did we discuss about neural networks earlier?",
                "filename": "memory_test.txt"
            },
            {
                "name": "Multi-step",
                "query": "Find recent papers on reinforcement learning, analyze their methodologies, and identify common challenges.",
                "filename": "multi_step.txt"
            },
            {
                "name": "Collaborative",
                "query": "Compare two machine-learning approaches and recommend which is better for our use case.",
                "filename": "collaborative.txt"
            }
        ]
        
        print("Starting Multi-Agent System Output Generation")
        print(f"Outputs will be saved to: {self.outputs_dir.absolute()}")
        
        for scenario in scenarios:
            await self.run_scenario(
                scenario["name"], 
                scenario["query"], 
                scenario["filename"]
            )
        
        print(f"\n{'='*60}")
        print("ALL SCENARIOS COMPLETED")
        print(f"Check the '{self.outputs_dir}' directory for all output files.")
        print(f"{'='*60}")

async def main():
    """Main execution function"""
    try:
        generator = OutputGenerator()
        await generator.generate_all_outputs()
    except KeyboardInterrupt:
        print("\nOutput generation interrupted by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        logger.error(f"Fatal error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())