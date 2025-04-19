"""Pytest configuration file."""

import os
import pytest
import shutil
from pathlib import Path


@pytest.fixture
def test_prompts_dir(tmp_path):
    """Create a temporary directory with test prompts for ReAct agent."""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only


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
    
    # Create directory structure for LLMCompilerAgent
    llm_compiler_dir = prompts_dir / "LLMCompilerAgent"
    llm_compiler_dir.mkdir()
    planner_step_dir = llm_compiler_dir / "PlannerStep"
    planner_step_dir.mkdir()
    executor_step_dir = llm_compiler_dir / "ExecutorStep"
    executor_step_dir.mkdir()
    joiner_step_dir = llm_compiler_dir / "JoinerStep"
    joiner_step_dir.mkdir()
    
    # Create test prompt files for PlannerStep
    planner_system_content = """You are a task planner for a modular AI system. Your job is to analyze user requests and break them down into a sequence of steps.

# RESPONSE FORMAT
1. task_1(tool="tool_name", inputs={"param1": "value1"})
2. task_2(tool="tool_name", inputs={"param1": "value1"}, depends_on=[1])
"""

    planner_user_content = """## User Input
{input_query}

## Available Tools
{available_tools}

Please create an optimized plan that maximizes parallel execution when possible."""
    
    # Create test prompt files for ExecutorStep
    executor_system_content = """You are a task executor responsible for running tasks according to a plan.

# RESPONSE FORMAT
Execute the task and return the result."""

    executor_user_content = """## Current Task
{current_task}

## Available Tools
{available_tools}

Execute only this specific task and return the results."""
    
    # Create test prompt files for JoinerStep
    joiner_system_content = """You are a response synthesizer for a modular AI system.

# RESPONSE FORMAT
Provide a concise final answer and specify if replanning is needed."""

    joiner_user_content = """## Original User Query
{input_query}

## Task Results
{task_results}

Synthesize these results and specify needs_replanning=True or needs_replanning=False."""
    
    # Write PlannerStep prompts
    with open(planner_step_dir / "system.md", "w") as f:
        f.write(planner_system_content)
    
    with open(planner_step_dir / "user.md", "w") as f:
        f.write(planner_user_content)
    
    # Write ExecutorStep prompts
    with open(executor_step_dir / "system.md", "w") as f:
        f.write(executor_system_content)
    
    with open(executor_step_dir / "user.md", "w") as f:
        f.write(executor_user_content)
    
    # Write JoinerStep prompts
    with open(joiner_step_dir / "system.md", "w") as f:
        f.write(joiner_system_content)
    
    with open(joiner_step_dir / "user.md", "w") as f:
        f.write(joiner_user_content)
    
    return prompts_dir 