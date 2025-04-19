#!/usr/bin/env python3

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only

"""
Script to update memory method calls in agent patterns from sync_* to _* 
as we're moving from asynchronous to synchronous memory methods.
"""

import os
import re
from pathlib import Path

def update_file(file_path):
    """Update memory method calls in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace sync_retrieve_memories with _retrieve_memories
    new_content = re.sub(r'sync_retrieve_memories', '_retrieve_memories', content)
    
    # Replace sync_save_memory with _save_memory
    new_content = re.sub(r'sync_save_memory', '_save_memory', new_content)
    
    # Only write if changes were made
    if content != new_content:
        print(f"Updating {file_path}")
        with open(file_path, 'w') as f:
            f.write(new_content)
        return True
    return False

def main():
    # Define agent pattern files to update
    pattern_dir = Path('src/agent_patterns/patterns')
    pattern_files = [
        pattern_dir / 'storm_agent.py',
        pattern_dir / 'plan_and_solve_agent.py',
        pattern_dir / 'reflexion_agent.py',
        pattern_dir / 'lats_agent.py',
        pattern_dir / 'llm_compiler_agent.py',
        pattern_dir / 'reflection_agent.py',
        pattern_dir / 'self_discovery_agent.py',
        pattern_dir / 'rewoo_agent.py'
    ]
    
    updated_count = 0
    for file_path in pattern_files:
        if os.path.exists(file_path):
            if update_file(file_path):
                updated_count += 1
    
    print(f"Updated {updated_count} files")

if __name__ == "__main__":
    main() 