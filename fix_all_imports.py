#!/usr/bin/env python3
"""
Fix ALL relative imports in the multi-agent system to work with direct script execution.
This script will systematically fix imports in all Python files.
"""

from pathlib import Path
import re

def backup_file(file_path):
    """Create a backup of the original file"""
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
    if not backup_path.exists():  # Don't overwrite existing backups
        backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"📁 Backup created: {backup_path}")

def fix_imports_in_file(file_path, fixes):
    """Apply import fixes to a single file"""
    print(f"\n🔍 Processing: {file_path}")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    # Read file content
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # Apply each fix
    changes_made = False
    for old_pattern, new_pattern in fixes.items():
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print(f"  ✅ {old_pattern} → {new_pattern}")
            changes_made = True
    
    # If changes were made, backup and save
    if changes_made:
        backup_file(file_path)
        file_path.write_text(content, encoding='utf-8')
        print(f"  💾 Updated: {file_path}")
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False

def main():
    """Fix all import issues in the project"""
    print("🔧 COMPREHENSIVE IMPORT FIX FOR MULTI-AGENT SYSTEM")
    print("=" * 60)
    
    # Define all files that need fixing and their specific import fixes
    files_to_fix = {
        "src/agents/base_agent.py": {
            "from ..models.message import AgentMessage, TaskResult": "from models.message import AgentMessage, TaskResult"
        },
        
        "src/agents/research_agent.py": {
            "from .base_agent import BaseAgent": "from agents.base_agent import BaseAgent",
            "from ..models.message import AgentMessage, TaskResult": "from models.message import AgentMessage, TaskResult"
        },
        
        "src/agents/analysis_agent.py": {
            "from .base_agent import BaseAgent": "from agents.base_agent import BaseAgent", 
            "from ..models.message import AgentMessage, TaskResult": "from models.message import AgentMessage, TaskResult"
        },
        
        "src/memory/memory_agent.py": {
            "from ..agents.base_agent import BaseAgent": "from agents.base_agent import BaseAgent",
            "from ..models.message import AgentMessage, TaskResult": "from models.message import AgentMessage, TaskResult"
        },
        
        "src/coordinator/coordinator_agent.py": {
            "from ..agents.research_agent import ResearchAgent": "from agents.research_agent import ResearchAgent",
            "from ..agents.analysis_agent import AnalysisAgent": "from agents.analysis_agent import AnalysisAgent",
            "from ..memory.memory_agent import MemoryAgent": "from memory.memory_agent import MemoryAgent",
            "from ..models.message import AgentMessage, TaskResult": "from models.message import AgentMessage, TaskResult",
            "from ..agents.base_agent import BaseAgent": "from agents.base_agent import BaseAgent"
        }
    }
    
    # Check if we're in the right directory
    project_root = Path(".")
    if not (project_root / "src").exists():
        print("❌ Error: src/ directory not found!")
        print("Make sure you're running this from the project root directory.")
        return
    
    # Process each file
    total_fixed = 0
    for file_path_str, fixes in files_to_fix.items():
        file_path = Path(file_path_str)
        if fix_imports_in_file(file_path, fixes):
            total_fixed += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 IMPORT FIX COMPLETED!")
    print(f"📊 Files processed: {len(files_to_fix)}")
    print(f"📊 Files modified: {total_fixed}")
    
    if total_fixed > 0:
        print("\n✅ All relative imports have been converted to absolute imports!")
        print("💾 Original files backed up with .backup extension")
        print("\n🚀 Now try running:")
        print("  python run_scenarios.py")
        print("  or")
        print("  uv run python run_scenarios.py")
        print("  or")
        print("  uv run streamlit run app.py")
    else:
        print("\nℹ️  No changes were needed - imports may already be fixed.")
    
    # Additional check - verify imports work
    print("\n🧪 Testing imports...")
    try:
        import sys
        sys.path.insert(0, str(Path("src").absolute()))
        
        from models.message import AgentMessage
        print("✅ models.message - OK")
        
        from agents.base_agent import BaseAgent  
        print("✅ agents.base_agent - OK")
        
        from agents.research_agent import ResearchAgent
        print("✅ agents.research_agent - OK")
        
        from agents.analysis_agent import AnalysisAgent
        print("✅ agents.analysis_agent - OK")
        
        from memory.memory_agent import MemoryAgent
        print("✅ memory.memory_agent - OK")
        
        from coordinator.coordinator_agent import CoordinatorAgent
        print("✅ coordinator.coordinator_agent - OK")
        
        print("\n🎉 ALL IMPORTS WORKING! The system should run now.")
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        print("You may need to check for additional issues.")

if __name__ == "__main__":
    main()