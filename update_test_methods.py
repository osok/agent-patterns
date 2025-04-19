#!/usr/bin/env python3

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only

"""
Script to update memory method calls in test files from sync_* to _* 
as we're moving from asynchronous to synchronous memory methods.
"""

import os
import re
from pathlib import Path

def update_file(file_path):
    """Update memory method calls in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace assertions for sync_retrieve_memories
    new_content = re.sub(
        r"assert hasattr\(.*?, 'sync_retrieve_memories'\)",
        r"assert hasattr(test_agent, '_retrieve_memories')",
        content
    )
    
    # Replace assertions for sync_save_memory
    new_content = re.sub(
        r"assert hasattr\(.*?, 'sync_save_memory'\)",
        r"assert hasattr(test_agent, '_save_memory')",
        new_content
    )
    
    # Replace mock assignments
    new_content = re.sub(
        r"agent\.sync_retrieve_memories = mock_retrieve_memories",
        r"agent._retrieve_memories = mock_retrieve_memories",
        new_content
    )
    
    new_content = re.sub(
        r"agent\.sync_save_memory = mock_save_memory",
        r"agent._save_memory = mock_save_memory",
        new_content
    )
    
    # Replace assertions on mock calls
    new_content = re.sub(
        r"mock_retrieve_memories\.assert_called",
        r"mock_retrieve_memories.assert_called",
        new_content
    )
    
    new_content = re.sub(
        r"agent\.sync_retrieve_memories\.assert_called",
        r"agent._retrieve_memories.assert_called",
        new_content
    )
    
    new_content = re.sub(
        r"agent\.sync_save_memory\.assert_called",
        r"agent._save_memory.assert_called",
        new_content
    )
    
    # Replace string occurrences in assert statements
    new_content = re.sub(
        r"\"sync_retrieve_memories\"", 
        r"\"_retrieve_memories\"", 
        new_content
    )
    
    new_content = re.sub(
        r"\"sync_save_memory\"", 
        r"\"_save_memory\"", 
        new_content
    )
    
    # Only write if changes were made
    if content != new_content:
        print(f"Updating {file_path}")
        with open(file_path, 'w') as f:
            f.write(new_content)
        return True
    return False

def main():
    # Define test files to update
    test_dir = Path('tests')
    test_files = [
        test_dir / 'test_lats_agent.py',
        test_dir / 'test_plan_and_solve_memory_tools.py',
        test_dir / 'test_reflection_memory_tools.py',
        test_dir / 'test_reflexion_memory_tools.py',
        test_dir / 'test_rewoo_agent.py',
        test_dir / 'test_self_discovery_agent.py',
        test_dir / 'test_storm_agent.py',
        test_dir / 'test_memory_integration.py',
        test_dir / 'test_multi_pattern_memory_integration.py',
        test_dir / 'test_llm_compiler_agent.py'
    ]
    
    updated_count = 0
    for file_path in test_files:
        if os.path.exists(file_path):
            if update_file(file_path):
                updated_count += 1
    
    print(f"Updated {updated_count} test files")

if __name__ == "__main__":
    main() 