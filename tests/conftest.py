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
    
    # Create directory structure for ReActAgent
    react_dir = prompts_dir / "ReActAgent"
    react_dir.mkdir()
    thought_step_dir = react_dir / "ThoughtStep"
    thought_step_dir.mkdir()
    final_answer_dir = react_dir / "FinalAnswer"
    final_answer_dir.mkdir()
    
    # Create test prompt files for ThoughtStep
    thought_system_content = """You are an AI assistant that uses tools to accomplish a task.

# TASK
{input}

# AVAILABLE TOOLS
{tools}

# RESPONSE FORMAT
Thought: I need to think about what to do next...
Action: tool_name(specific input for the tool)"""

    thought_user_content = """What is your next step to solve this task? Remember to format your response as:

Thought: your reasoning
Action: tool_name(tool_input)"""
    
    # Create test prompt files for FinalAnswer
    final_system_content = """You are an AI assistant tasked with providing a clear, concise final answer based on your execution history.

# ORIGINAL TASK
{input}

# EXECUTION HISTORY
{intermediate_steps}

Now, provide your final answer:"""

    final_user_content = """Based on the solution steps above, provide a clear and complete answer to the original question."""
    
    # Write ThoughtStep prompts
    with open(thought_step_dir / "system.md", "w") as f:
        f.write(thought_system_content)
    
    with open(thought_step_dir / "user.md", "w") as f:
        f.write(thought_user_content)
    
    # Write FinalAnswer prompts
    with open(final_answer_dir / "system.md", "w") as f:
        f.write(final_system_content)
    
    with open(final_answer_dir / "user.md", "w") as f:
        f.write(final_user_content)
    
    return prompts_dir 