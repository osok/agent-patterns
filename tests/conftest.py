"""Pytest configuration file."""

import os
import pytest
import shutil
from pathlib import Path


@pytest.fixture
def test_prompts_dir(tmp_path):
    """Create a temporary directory with test prompts for ReAct agent."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    
    # Create test prompt files
    generate_thought_content = """You are an AI assistant that uses tools to accomplish a task.

# TASK
{task}

# AVAILABLE TOOLS
{tools}

# HISTORY
{history}

# RESPONSE FORMAT
Thought: I need to think about what to do next...
Action: tool_name(specific input for the tool)"""

    final_answer_content = """You are an AI assistant tasked with providing a clear, concise final answer based on your execution history.

# ORIGINAL TASK
{task}

# EXECUTION HISTORY
{history}

Now, provide your final answer:"""
    
    with open(prompts_dir / "generate_thought_prompt.txt", "w") as f:
        f.write(generate_thought_content)
        
    with open(prompts_dir / "format_final_answer_prompt.txt", "w") as f:
        f.write(final_answer_content)
    
    return prompts_dir 