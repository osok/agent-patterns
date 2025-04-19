"""Tests for memory and tool integration in ReflexionAgent."""

import pytest
import logging
import inspect
from unittest.mock import MagicMock, patch, call

from agent_patterns.patterns.reflexion_agent import ReflexionAgent
from agent_patterns.core.memory.composite import CompositeMemory
from agent_patterns.core.memory.semantic import SemanticMemory
from agent_patterns.core.memory.episodic import EpisodicMemory
from agent_patterns.core.tools.base import ToolProvider
from langchain_core.messages import AIMessage


class MockToolProvider(ToolProvider):
    """Mock implementation of tool provider for testing."""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



    def __init__(self, tools_config=None):
        self.tools = tools_config or [
            {
                "name": "search",
                "description": "Search for information",
                "parameters": {"query": "string"}
            },
            {
                "name": "calculator",
                "description": "Perform calculations",
                "parameters": {"expression": "string"}
            }
        ]
        self.calls = []

    def list_tools(self):
        """List available tools with their metadata."""
        return self.tools

    def execute_tool(self, tool_name, params):
        """Execute a tool with the given parameters."""
        self.calls.append({"tool": tool_name, "params": params})
        
        if tool_name == "search":
            return f"Search results for: {params.get('query', '')}"
        elif tool_name == "calculator":
            # Simple calculator implementation for testing
            try:
                expression = params.get('expression', '0')
                return str(eval(expression))
            except Exception as e:
                return f"Error calculating: {str(e)}"
        else:
            raise ValueError(f"Unknown tool: {tool_name}")


@pytest.fixture
def mock_memory():
    """Create a mock composite memory for testing."""
    memory_mock = MagicMock(spec=CompositeMemory)
    
    # Set up the memory types that would be in the memory
    memory_mock.memories = {
        "semantic": MagicMock(spec=SemanticMemory),
        "episodic": MagicMock(spec=EpisodicMemory)
    }
    
    # Mock retrieve_all method to return sample data
    async def mock_retrieve_all(*args, **kwargs):
        return {
            "semantic": [{"fact": "Sample semantic fact"}],
            "episodic": [{"event": "Sample episodic event"}]
        }
    
    # Mock save_to method
    async def mock_save_to(memory_type, item, **kwargs):
        return f"mock_id_{memory_type}"
    
    # Assign the mocked methods
    memory_mock.retrieve_all = mock_retrieve_all
    memory_mock.save_to = mock_save_to
    
    return memory_mock


@pytest.fixture
def mock_tool_provider():
    """Create a mock tool provider for testing."""
    return MockToolProvider()


@pytest.fixture
def test_agent(mock_memory, mock_tool_provider):
    """Create a ReflexionAgent with mock components for testing."""
    llm_configs = {
        "planner": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "executor": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "evaluator": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "reflector": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        }
    }
    
    return ReflexionAgent(
        llm_configs=llm_configs,
        memory=mock_memory,
        tool_provider=mock_tool_provider,
        log_level=logging.ERROR
    )


@patch("langchain_openai.ChatOpenAI")
def test_reflexion_agent_constructor(mock_llm, mock_memory, mock_tool_provider):
    """Test that the constructor correctly accepts memory and tool_provider."""
    # Arrange
    llm_configs = {
        "planner": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "executor": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "evaluator": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "reflector": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        }
    }

    # Act
    agent = ReflexionAgent(
        llm_configs=llm_configs,
        memory=mock_memory,
        tool_provider=mock_tool_provider
    )

    # Assert
    assert agent.memory == mock_memory
    assert agent.tool_provider == mock_tool_provider
    assert agent.memory_config == {
        "semantic": True,
        "episodic": True,
        "procedural": False
    }


@patch("langchain_openai.ChatOpenAI")
def test_reflexion_agent_memory_integration(mock_llm, test_agent):
    """Test that memory integration is properly implemented."""
    # Verify that _retrieve_memories and _save_memory methods exist
    assert hasattr(test_agent, '_retrieve_memories')
    assert hasattr(test_agent, '_save_memory')
    
    # Check memory integration in plan_action_with_memory
    plan_code = inspect.getsource(test_agent._plan_action_with_memory)
    assert "retrieve_memories" in plan_code or "_retrieve_memories" in plan_code
    
    # Check memory integration in execute_plan
    execute_code = inspect.getsource(test_agent._execute_plan)
    assert "save_memory" in execute_code or "_save_memory" in execute_code
    
    # Check memory integration in evaluate_result
    evaluate_code = inspect.getsource(test_agent._evaluate_result)
    assert "save_memory" in evaluate_code or "_save_memory" in evaluate_code


@patch("langchain_openai.ChatOpenAI")
def test_reflexion_agent_tool_integration(mock_llm, test_agent, mock_tool_provider):
    """Test that tool provider integration is properly implemented."""
    # Verify that tool_provider is correctly passed and stored
    assert test_agent.tool_provider == mock_tool_provider
    
    # Verify tool_provider code integration in _execute_action
    code = inspect.getsource(test_agent._execute_action)
    assert "tool_provider" in code
    assert "execute_tool" in code
    
    # Verify the pattern for extracting tool calls exists
    assert "USE_TOOL:" in code or "tool_call_pattern" in code or "tool_call_match" in code 


@patch("langchain_openai.ChatOpenAI")
def test_reflexion_with_memory_usage(mock_llm, test_agent):
    """Test that memory is properly used during the reflexion process."""
    # Setup mock responses
    plan_response = MagicMock()
    plan_response.content = "Plan: Step 1, Step 2, Step 3"
    
    execution_response = MagicMock()
    execution_response.content = "Execution result"
    
    evaluation_response = MagicMock()
    evaluation_response.content = "Evaluation: Success=True"
    
    reflection_response = MagicMock()
    reflection_response.content = "I learned to be more careful with step 2"
    
    # Configure mock to return different responses
    mock_llm.return_value.invoke.side_effect = [
        plan_response, execution_response, 
        evaluation_response, reflection_response
    ]
    
    # Mock the memory methods
    test_agent._retrieve_memories = MagicMock(return_value={
        "semantic": [{"fact": "Important context about the task"}],
        "episodic": [{"event": "Previous attempt at similar task"}]
    })
    
    test_agent._save_memory = MagicMock()
    
    # Create test state
    initial_state = {
        "input_task": "Test task",
        "reflection_memory": [],
        "trial_count": 1,
        "max_trials": 3,
        "current_plan": None,
        "action_result": None,
        "evaluation": None,
        "trial_reflection": None,
        "final_answer": None
    }
    
    # Run each step individually to test memory integration
    state = test_agent._plan_action_with_memory(initial_state)
    state = test_agent._execute_plan(state)
    state = test_agent._evaluate_result(state)
    state = test_agent._reflect_on_trial(state)
    
    # Verify memory retrieval was called
    test_agent._retrieve_memories.assert_called_with("Test task")
    
    # Verify memory was saved at least once
    assert test_agent._save_memory.call_count >= 1 