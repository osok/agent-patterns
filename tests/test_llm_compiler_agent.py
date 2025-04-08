"""Tests for the LLM Compiler Agent pattern."""

import pytest
from unittest.mock import MagicMock, patch
import os
import json
from typing import Dict, Any, List
import re

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool, tool

from agent_patterns.patterns.llm_compiler_agent import LLMCompilerAgent, LLMCompilerState


@pytest.fixture
def mock_llm():
    """Create a mock LLM that returns predefined responses."""
    mock = MagicMock(spec=BaseLanguageModel)
    
    # Configure the mock to return specific responses based on the input
    def side_effect(messages):
        # Extract the last message content to determine which function called it
        last_message = messages[-1].content if hasattr(messages[-1], "content") else messages[-1]["content"]
        
        if "plan" in last_message.lower():
            return AIMessage(content="""
1. task_1(tool="search_web", inputs={"query": "weather in San Francisco"})
2. task_2(tool="search_web", inputs={"query": "temperature conversion formula"})
3. task_3(tool="calculate", inputs={"expression": "5 * 9"}, depends_on=[1, 2])
            """)
        elif "execute" in last_message.lower():
            return AIMessage(content="Mock execution result.")
        elif "synthesize" in last_message.lower() or "join" in last_message.lower():
            return AIMessage(content="I have synthesized the final answer based on all tasks. needs_replanning=False")
        else:
            return AIMessage(content="Default mock response")
    
    mock.invoke.side_effect = side_effect
    return mock


@pytest.fixture
def mock_prompt_template():
    """Create a mock prompt template."""
    mock = MagicMock(spec=ChatPromptTemplate)
    mock.invoke.return_value.to_messages.return_value = [{"role": "user", "content": "Mock prompt"}]
    return mock


@pytest.fixture
def mock_tools():
    """Create some mock tools for testing."""
    @tool
    def search_web(query: str) -> str:
        """Search the web for information."""
        return f"Search results for '{query}'"

    @tool
    def calculate(expression: str) -> str:
        """Calculate the result of a mathematical expression."""
        return f"Result of '{expression}'"

    return [search_web, calculate]


@pytest.fixture
def llm_compiler_agent(mock_llm, mock_prompt_template, mock_tools):
    """Create a LLMCompilerAgent with mocked components."""
    
    # Setup for LLM configs
    llm_configs = {
        "planner": {"provider": "mock", "model_name": "mock-model"},
        "executor": {"provider": "mock", "model_name": "mock-model"},
        "joiner": {"provider": "mock", "model_name": "mock-model"}
    }
    
    # Create a custom _load_prompt_template method that returns our mock
    def mock_load_prompt_template(self, step_name):
        return mock_prompt_template
    
    # Create a mock tool executor
    mock_tool_executor = MagicMock()
    mock_tool_executor.execute.return_value = "Mock tool execution result"
    
    with patch.object(LLMCompilerAgent, '_get_llm', return_value=mock_llm):
        with patch.object(LLMCompilerAgent, '_load_prompt_template', mock_load_prompt_template):
            agent = LLMCompilerAgent(llm_configs=llm_configs, tools=mock_tools)
            agent.tool_executor = mock_tool_executor  # Override with our mock
            return agent


def test_llm_compiler_agent_initialization(llm_compiler_agent, mock_tools):
    """Test that the LLMCompilerAgent initializes correctly."""
    assert llm_compiler_agent is not None
    assert llm_compiler_agent.graph is not None
    assert len(llm_compiler_agent.tools) == len(mock_tools)
    assert llm_compiler_agent.tool_executor is not None


def test_plan_tasks(llm_compiler_agent):
    """Test the task planning functionality."""
    initial_state = {
        "input_query": "What's the weather in San Francisco and convert it to Celsius?",
        "available_tools": [
            {"name": "search_web", "description": "Search the web", "args_schema": "{'query': str}"},
            {"name": "calculate", "description": "Calculate expressions", "args_schema": "{'expression': str}"}
        ],
        "task_graph": {},
        "tasks_pending": [],
        "tasks_in_progress": [],
        "tasks_completed": [],
        "task_results": {},
        "needs_replanning": False,
        "final_answer": None
    }
    
    result = llm_compiler_agent._plan_tasks(initial_state)
    
    assert "task_graph" in result
    assert len(result["task_graph"]) > 0
    assert "tasks_pending" in result
    assert len(result["tasks_pending"]) > 0
    # Only root tasks should be in pending initially
    for task in result["tasks_pending"]:
        task_id = task["id"]
        assert not result["task_graph"][task_id].get("depends_on", [])


def test_parse_task_plan(llm_compiler_agent):
    """Test the task plan parsing functionality."""
    plan_text = """
1. task_1(tool="search_web", inputs={"query": "weather in New York"})
2. task_2(tool="calculate", inputs={"expression": "32 - 32 * 5/9"}, depends_on=[1])
3. task_3(tool="search_web", inputs={"query": "convert Fahrenheit to Celsius"})
    """
    
    task_graph = llm_compiler_agent._parse_task_plan(plan_text)
    
    assert len(task_graph) == 3
    assert "1" in task_graph
    assert "2" in task_graph
    assert "3" in task_graph
    assert task_graph["1"]["tool"] == "search_web"
    assert task_graph["2"]["depends_on"] == ["1"]
    assert "inputs" in task_graph["3"]
    assert "query" in task_graph["3"]["inputs"]


def test_schedule_tasks(llm_compiler_agent):
    """Test the task scheduling functionality."""
    state = {
        "input_query": "Test query",
        "task_graph": {
            "1": {"tool": "search_web", "inputs": {"query": "test"}, "depends_on": []},
            "2": {"tool": "calculate", "inputs": {"expression": "1+1"}, "depends_on": ["1"]},
            "3": {"tool": "search_web", "inputs": {"query": "another test"}, "depends_on": []}
        },
        "tasks_pending": [],
        "tasks_in_progress": [],
        "tasks_completed": [{"id": "1", "tool": "search_web", "inputs": {"query": "test"}}],
        "task_results": {"1": "Mock result for task 1"}
    }
    
    result = llm_compiler_agent._schedule_tasks(state)
    
    assert "tasks_pending" in result
    assert len(result["tasks_pending"]) > 0
    # Task 2 should be scheduled now that task 1 is completed
    task2_scheduled = False
    for task in result["tasks_pending"]:
        if task["id"] == "2":
            task2_scheduled = True
            break
    assert task2_scheduled, "Task 2 should be scheduled after its dependency (Task 1) is completed"
    # Task 3 should also be scheduled as it has no dependencies
    task3_scheduled = False
    for task in result["tasks_pending"]:
        if task["id"] == "3":
            task3_scheduled = True
            break
    assert task3_scheduled, "Task 3 should be scheduled as it has no dependencies"


def test_execute_tasks(llm_compiler_agent):
    """Test the task execution functionality."""
    state = {
        "tasks_in_progress": [{"id": "1", "tool": "search_web", "inputs": {"query": "test"}}],
        "task_results": {}
    }
    
    result = llm_compiler_agent._execute_tasks(state)
    
    assert "task_results" in result
    assert "1" in result["task_results"]
    assert result["task_results"]["1"] == "Mock tool execution result"


def test_update_task_status(llm_compiler_agent):
    """Test updating task status after execution."""
    state = {
        "tasks_in_progress": [
            {"id": "1", "tool": "search_web", "inputs": {"query": "test"}},
            {"id": "2", "tool": "calculate", "inputs": {"expression": "1+1"}}
        ],
        "tasks_completed": [{"id": "3", "tool": "search_web", "inputs": {"query": "other"}}]
    }
    
    result = llm_compiler_agent._update_task_status(state)
    
    assert "tasks_in_progress" in result
    assert "tasks_completed" in result
    assert len(result["tasks_in_progress"]) == 1
    assert len(result["tasks_completed"]) == 2
    assert result["tasks_in_progress"][0]["id"] == "2"
    assert result["tasks_completed"][1]["id"] == "1"


def test_should_continue_execution(llm_compiler_agent):
    """Test the continuation decision logic."""
    # Should continue - tasks pending
    state1 = {
        "tasks_pending": [{"id": "1", "tool": "search_web", "inputs": {"query": "test"}}],
        "tasks_in_progress": []
    }
    assert llm_compiler_agent._should_continue_execution(state1)
    
    # Should continue - tasks in progress
    state2 = {
        "tasks_pending": [],
        "tasks_in_progress": [{"id": "1", "tool": "search_web", "inputs": {"query": "test"}}]
    }
    assert llm_compiler_agent._should_continue_execution(state2)
    
    # Should not continue - no tasks
    state3 = {
        "tasks_pending": [],
        "tasks_in_progress": []
    }
    assert not llm_compiler_agent._should_continue_execution(state3)


def test_synthesize_results(llm_compiler_agent):
    """Test the result synthesis functionality."""
    state = {
        "input_query": "Test query",
        "tasks_completed": [
            {"id": "1", "tool": "search_web", "inputs": {"query": "test"}},
            {"id": "2", "tool": "calculate", "inputs": {"expression": "1+1"}}
        ],
        "task_results": {
            "1": "Search results for test",
            "2": "2"
        }
    }
    
    # Mock the _load_prompt_template method to return a mock template
    mock_prompt = MagicMock()
    mock_prompt.invoke.return_value.to_messages.return_value = [{"role": "user", "content": "Mock prompt"}]
    llm_compiler_agent._load_prompt_template = lambda x: mock_prompt
    
    # Mock the LLM to return a response with "synthesized" in it
    mock_joiner_llm = MagicMock()
    mock_joiner_llm.invoke.return_value = AIMessage(content="I have synthesized the results. needs_replanning=False")
    llm_compiler_agent.joiner_llm = mock_joiner_llm
    
    result = llm_compiler_agent._synthesize_results(state)
    
    assert "final_answer" in result
    assert "needs_replanning" in result
    assert result["needs_replanning"] is False
    assert result["final_answer"] is not None
    assert "synthesized" in result["final_answer"].lower()


def test_needs_replanning(llm_compiler_agent):
    """Test the replanning decision logic."""
    state1 = {"needs_replanning": True}
    assert llm_compiler_agent._needs_replanning(state1)
    
    state2 = {"needs_replanning": False}
    assert not llm_compiler_agent._needs_replanning(state2)


def test_run_method(llm_compiler_agent):
    """Test the run method of the LLMCompilerAgent."""
    # Patch the graph.invoke method to return a predefined state
    final_state = {
        "input_query": "Test query",
        "available_tools": [],
        "task_graph": {"1": {}, "2": {}, "3": {}},
        "tasks_pending": [],
        "tasks_in_progress": [],
        "tasks_completed": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
        "task_results": {"1": "Result 1", "2": "Result 2", "3": "Result 3"},
        "needs_replanning": False,
        "final_answer": "Final synthesized answer"
    }
    
    llm_compiler_agent.graph.invoke = MagicMock(return_value=final_state)
    
    result = llm_compiler_agent.run("Test query")
    
    assert "output" in result
    assert "metadata" in result
    assert result["output"] == "Final synthesized answer"
    assert result["metadata"]["tasks_planned"] == 3
    assert result["metadata"]["tasks_completed"] == 3
    assert result["metadata"]["needed_replanning"] is False


def test_stream_method(llm_compiler_agent):
    """Test the stream method of the LLMCompilerAgent."""
    # Create a generator that returns some state updates
    def mock_stream(state):
        yield {"task_graph": {"1": {}, "2": {}}}
        yield {"tasks_pending": [{"id": "1"}]}
        yield {"task_results": {"1": "Result 1"}}
        yield {"tasks_completed": [{"id": "1"}]}
        yield {"final_answer": "Final answer"}
    
    llm_compiler_agent.graph.stream = MagicMock(side_effect=mock_stream)
    
    # Collect all yielded items from the stream
    results = list(llm_compiler_agent.stream("Test query"))
    
    assert len(results) == 5
    assert "task_graph" in results[0]
    assert "final_answer" in results[-1]


def test_integration_with_mocks(llm_compiler_agent):
    """Test the complete flow with mocked components."""
    input_query = "What's the weather in San Francisco and convert it to Celsius?"
    
    # Create a more realistic mock for the graph invoke that simulates the full flow
    def simulate_graph_invoke(state):
        # Simulate planning
        state = {**state, **llm_compiler_agent._plan_tasks(state)}
        
        # Process all tasks
        while llm_compiler_agent._should_continue_execution(state):
            state = {**state, **llm_compiler_agent._schedule_tasks(state)}
            state = {**state, **llm_compiler_agent._execute_tasks(state)}
            state = {**state, **llm_compiler_agent._update_task_status(state)}
        
        # Synthesize results
        state = {**state, **llm_compiler_agent._synthesize_results(state)}
        
        # If replanning needed, do one more round of planning (simplified)
        if state["needs_replanning"]:
            state["needs_replanning"] = False  # Avoid infinite loop in test
            state = {**state, **llm_compiler_agent._plan_tasks(state)}
            
            # Process additional tasks
            while llm_compiler_agent._should_continue_execution(state):
                state = {**state, **llm_compiler_agent._schedule_tasks(state)}
                state = {**state, **llm_compiler_agent._execute_tasks(state)}
                state = {**state, **llm_compiler_agent._update_task_status(state)}
            
            # Final synthesis
            state = {**state, **llm_compiler_agent._synthesize_results(state)}
        
        return state
    
    llm_compiler_agent.graph.invoke = MagicMock(side_effect=simulate_graph_invoke)
    
    result = llm_compiler_agent.run(input_query)
    
    assert "output" in result
    assert "metadata" in result
    assert result["metadata"]["tasks_planned"] > 0
    assert result["metadata"]["tasks_completed"] > 0
    assert isinstance(result["output"], str)


def test_parsing_edge_cases(llm_compiler_agent):
    """Test task plan parsing with edge cases."""
    # Poorly formatted plan
    malformed_plan = """
1. search_web("weather in London")
2. This is not properly formatted
3. calculate(expression=1+1)
    """
    
    task_graph = llm_compiler_agent._parse_task_plan(malformed_plan)
    assert len(task_graph) == 0  # Should handle gracefully and return empty dict
    
    # Empty plan
    empty_plan = ""
    task_graph = llm_compiler_agent._parse_task_plan(empty_plan)
    assert len(task_graph) == 0
    
    # Simplified but well-formatted plan
    simple_plan = """
1. task_1(tool="search_web", inputs={"query": "weather"})
2. task_2(tool="calculate", inputs={"expression": "1+1"}, depends_on=[1])
    """
    
    task_graph = llm_compiler_agent._parse_task_plan(simple_plan)
    assert len(task_graph) > 0
    assert task_graph["1"]["tool"] == "search_web"
    assert "query" in task_graph["1"]["inputs"]
    assert task_graph["1"]["inputs"]["query"] == "weather" 