#!/usr/bin/env python3
"""
Simple runner script that handles imports correctly for generating outputs.
This avoids the relative import issues by running from the correct context.
"""

import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime

# Ensure we can import from src
project_root = Path(__file__).parent
src_path = project_root / "src"

# Add to Python path
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Change working directory to project root
os.chdir(project_root)

def create_outputs_directory():
    """Ensure outputs directory exists"""
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    return outputs_dir

async def run_single_scenario(coordinator, name, query, filename):
    """Run one scenario and save the output"""
    print(f"\n{'='*50}")
    print(f"Running: {name}")
    print(f"Query: {query}")
    print(f"{'='*50}")
    
    try:
        # Process the query
        response = await coordinator.process_user_query(query)
        
        # Format the output
        lines = [
            f"Multi-Agent System Output - {name}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            f"QUERY: {query}",
            "",
            "RESPONSE:",
            response.get('response', 'No response generated'),
            "",
            f"CONFIDENCE: {response.get('confidence', 0.0):.2f}",
            "",
            "EXECUTION TRACE:",
        ]
        
        # Add trace information
        trace = response.get('trace', [])
        if trace:
            for i, step in enumerate(trace, 1):
                lines.extend([
                    f"  Step {i}: {step.get('agent', 'Unknown')}",
                    f"    Action: {step.get('action', 'N/A')}",
                    f"    Result: {str(step.get('result', 'N/A'))[:150]}...",
                    ""
                ])
        else:
            lines.append("  No trace available")
        
        # Save to file
        outputs_dir = create_outputs_directory()
        output_file = outputs_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Output saved to: {output_file}")
        print(f"Response preview: {response.get('response', 'No response')[:100]}...")
        
        # Small delay between requests
        await asyncio.sleep(1)
        
    except Exception as e:
        print(f"❌ Error in scenario '{name}': {e}")
        # Save error to output file anyway
        error_lines = [
            f"Multi-Agent System Output - {name} (ERROR)",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            f"QUERY: {query}",
            "",
            f"ERROR: {str(e)}",
            "",
            "This scenario failed to execute properly.",
        ]
        
        outputs_dir = create_outputs_directory()
        output_file = outputs_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(error_lines))

async def main():
    """Main function to run all scenarios"""
    print("Multi-Agent System - Scenario Runner")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path includes: {src_path}")
    
    # Define all test scenarios as required
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
    
    try:
        # Import the coordinator (this should work now)
        print("Importing CoordinatorAgent...")
        from coordinator.coordinator_agent import CoordinatorAgent
        
        # Initialize the system
        print("Initializing coordinator...")
        coordinator = CoordinatorAgent()
        print("✅ Coordinator initialized successfully")
        
        # Run all scenarios
        print(f"\nRunning {len(scenarios)} test scenarios...")
        for scenario in scenarios:
            await run_single_scenario(
                coordinator,
                scenario["name"],
                scenario["query"], 
                scenario["filename"]
            )
        
        print(f"\n{'='*60}")
        print("🎉 ALL SCENARIOS COMPLETED!")
        print("Check the 'outputs/' directory for all generated files.")
        print(f"{'='*60}")
        
    except ImportError as e:
        print(f"❌ Failed to import CoordinatorAgent: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you're in the project root directory")
        print("2. Try: PYTHONPATH=./src python run_scenarios.py")
        print("3. Or try: uv run python run_scenarios.py")
        print("4. Check that all files exist in src/coordinator/")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())