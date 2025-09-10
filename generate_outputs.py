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
        """Run a single test scenario and save comprehensive output"""
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario_name}")
        print(f"QUERY: {query}")
        print(f"{'='*60}")
        
        try:
            # Process query
            response = await self.coordinator.process_user_query(query)
            
            # Prepare comprehensive output content
            output_content = [
                f"Multi-Agent System Test Output",
                f"={'*'*60}",
                f"Scenario: {scenario_name}",
                f"Query: {query}",
                f"Timestamp: {datetime.now().isoformat()}",
                f"={'*'*60}",
                "",
                f"SYNTHESIZED ANSWER:",
                f"{'-'*40}",
                response.get('synthesized_answer', 'No response generated'),
                "",
                f"SYSTEM METRICS:",
                f"{'-'*40}",
                f"Overall Confidence: {response.get('confidence', 0.0):.2f}",
                f"Success: {response.get('success', False)}",
                f"Agents Involved: {len(response.get('agent_results', {}))}"
            ]
            
            # Add detailed agent results
            agent_results = response.get('agent_results', {})
            if agent_results:
                output_content.extend([
                    "",
                    f"AGENT EXECUTION DETAILS:",
                    f"{'-'*40}"
                ])
                
                for agent_name, data in agent_results.items():
                    output_content.extend([
                        f"{agent_name.upper().replace('_', ' ')}:",
                        f"  Confidence: {data.get('confidence', 0.0):.2f}",
                        f"  Execution Time: {data.get('execution_time', 0.0):.3f}s"
                    ])
                    
                    # Add agent-specific data summary
                    agent_data = data.get('data', {})
                    if agent_name == 'research_agent' and 'research_results' in agent_data:
                        results = agent_data['research_results']
                        if isinstance(results, dict):
                            output_content.append(f"  Topics Found: {', '.join(results.keys())}")
                        elif isinstance(results, list):
                            output_content.append(f"  Results Count: {len(results)}")
                    
                    elif agent_name == 'analysis_agent' and 'analysis' in agent_data:
                        analysis = agent_data['analysis']
                        if isinstance(analysis, dict):
                            analysis_type = analysis.get('analysis_type', 'general')
                            output_content.append(f"  Analysis Type: {analysis_type}")
                    
                    elif agent_name == 'memory_agent':
                        if 'results' in agent_data:
                            count = len(agent_data['results']) if isinstance(agent_data['results'], list) else agent_data.get('count', 0)
                            output_content.append(f"  Memory Hits: {count}")
                            best_distance = agent_data.get('best_distance')
                            if best_distance is not None:
                                output_content.append(f"  Best Distance: {best_distance:.3f}")
                    
                    output_content.append("")
            
            # Add execution trace
            trace = response.get('execution_trace', [])
            if trace:
                output_content.extend([
                    f"EXECUTION TRACE:",
                    f"{'-'*40}"
                ])
                
                for i, step in enumerate(trace, 1):
                    agent = step.get('agent', 'Unknown')
                    success = step.get('success', False)
                    exec_time = step.get('execution_time', 0.0)
                    output_content.extend([
                        f"Step {i}: {agent}",
                        f"  Status: {'SUCCESS' if success else 'FAILED'}",
                        f"  Time: {exec_time:.3f}s"
                    ])
                    if step.get('error'):
                        output_content.append(f"  Error: {step['error']}")
                    output_content.append("")
            
            # Add memory system status
            try:
                memory_stats = self.coordinator.memory_agent.get_memory_stats()
                output_content.extend([
                    f"MEMORY SYSTEM STATUS:",
                    f"{'-'*40}",
                    f"Conversations Stored: {memory_stats.get('conversation_count', 0)}",
                    f"Knowledge Entries: {memory_stats.get('knowledge_count', 0)}",
                    f"Storage Path: {memory_stats.get('storage_path', 'N/A')}",
                    ""
                ])
            except Exception as e:
                output_content.extend([
                    f"MEMORY SYSTEM STATUS:",
                    f"{'-'*40}",
                    f"Error retrieving memory stats: {str(e)}",
                    ""
                ])
            
            # Add collaboration summary
            output_content.extend([
                f"AGENT COLLABORATION SUMMARY:",
                f"{'-'*40}",
                f"This scenario demonstrated multi-agent coordination where:",
            ])
            
            if 'research_agent' in agent_results:
                output_content.append("- Research Agent retrieved relevant information from knowledge base")
            if 'analysis_agent' in agent_results:
                output_content.append("- Analysis Agent processed and analyzed the research data")
            if 'memory_agent' in agent_results:
                output_content.append("- Memory Agent stored/retrieved conversation context")
            
            output_content.extend([
                "- Coordinator orchestrated the entire process and synthesized results",
                "",
                f"{'='*60}",
                f"End of {scenario_name} Test Output",
                f"{'='*60}"
            ])
            
            # Save to file
            output_file = self.outputs_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_content))
            
            print(f"\nRESPONSE: {response.get('synthesized_answer', 'No response')[:200]}...")
            print(f"CONFIDENCE: {response.get('confidence', 0.0):.2f}")
            print(f"OUTPUT SAVED TO: {output_file}")
            
            # Add delay between scenarios for memory persistence
            await asyncio.sleep(2)
            
        except Exception as e:
            error_msg = f"Error processing scenario '{scenario_name}': {str(e)}"
            print(f"ERROR: {error_msg}")
            logger.error(error_msg)
            
            # Still save error output with full details
            output_file = self.outputs_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Multi-Agent System Test Output\n")
                f.write(f"{'*'*60}\n")
                f.write(f"Scenario: {scenario_name}\n")
                f.write(f"Query: {query}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"{'*'*60}\n\n")
                f.write(f"ERROR OCCURRED:\n")
                f.write(f"{'-'*40}\n")
                f.write(f"{error_msg}\n\n")
                f.write(f"This indicates a system issue that needs to be resolved.\n")
                f.write(f"The multi-agent system architecture is present but encountered\n")
                f.write(f"a runtime error during execution.\n")

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
                "name": "Multi-step Query",
                "query": "Find recent papers on reinforcement learning, analyze their methodologies, and identify common challenges.",
                "filename": "multi_step.txt"
            },
            {
                "name": "Collaborative Query",
                "query": "Compare two machine-learning approaches and recommend which is better for our use case.",
                "filename": "collaborative.txt"
            }
        ]
        
        print("Starting Multi-Agent System Output Generation")
        print(f"Outputs will be saved to: {self.outputs_dir.absolute()}")
        print(f"System Architecture: Coordinator + Research + Analysis + Memory Agents")
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[{i}/{len(scenarios)}] Processing scenario...")
            await self.run_scenario(
                scenario["name"], 
                scenario["query"], 
                scenario["filename"]
            )
        
        print(f"\n{'='*60}")
        print("ALL SCENARIOS COMPLETED")
        print(f"Generated {len(scenarios)} output files in '{self.outputs_dir}'")
        
        # List generated files
        print("\nGenerated files:")
        for scenario in scenarios:
            filepath = self.outputs_dir / scenario["filename"]
            if filepath.exists():
                file_size = filepath.stat().st_size
                print(f"  ✓ {scenario['filename']} ({file_size} bytes)")
            else:
                print(f"  ✗ {scenario['filename']} (failed to generate)")
        
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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())