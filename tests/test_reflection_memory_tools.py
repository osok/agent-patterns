"""Tests for memory and tool integration in ReflectionAgent."""

import pytest
import logging
import inspect
from unittest.mock import MagicMock, patch, call

from agent_patterns.patterns.reflection_agent import ReflectionAgent
from agent_patterns.core.memory.composite import CompositeMemory
from agent_patterns.core.memory.semantic import SemanticMemory
from agent_patterns.core.memory.episodic import EpisodicMemory
from agent_patterns.core.tools.base import ToolProvider


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
    """Create a ReflectionAgent with mock components for testing."""
    llm_configs = {
        "generator": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "critic": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        }
    }
    
    return ReflectionAgent(
        llm_configs=llm_configs,
        memory=mock_memory,
        tool_provider=mock_tool_provider,
        log_level=logging.ERROR
    )


@patch("langchain_openai.ChatOpenAI")
def test_reflection_agent_constructor(mock_llm, mock_memory, mock_tool_provider):
    """Test that the constructor correctly accepts memory and tool_provider."""
    # Arrange
    llm_configs = {
        "generator": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "critic": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        }
    }

    # Act
    agent = ReflectionAgent(
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
def test_reflection_agent_memory_integration(mock_llm, test_agent):
    """Test that memory integration is properly implemented."""
    # Verify that _retrieve_memories and _save_memory methods exist
    assert hasattr(test_agent, '_retrieve_memories')
    assert hasattr(test_agent, '_save_memory')
    
    # Check memory integration in generate_initial_output
    initial_output_code = inspect.getsource(test_agent._generate_initial_output)
    assert "retrieve_memories" in initial_output_code or "_retrieve_memories" in initial_output_code
    
    # Check memory integration in generate_reflection
    reflection_code = inspect.getsource(test_agent._generate_reflection)
    assert "save_memory" in reflection_code or "_save_memory" in reflection_code
    
    # Check memory integration in generate_refined_output
    refined_output_code = inspect.getsource(test_agent._generate_refined_output)
    assert "save_memory" in refined_output_code or "_save_memory" in refined_output_code


@patch("langchain_openai.ChatOpenAI")
def test_reflection_agent_tool_integration(mock_llm, test_agent, mock_tool_provider):
    """Test that tool provider integration is properly implemented."""
    # Verify that tool_provider is correctly passed and stored
    assert test_agent.tool_provider == mock_tool_provider
    
    # Verify tool_provider code integration in _generate_initial_output
    code = inspect.getsource(test_agent._generate_initial_output)
    assert "tool_provider" in code
    assert "execute_tool" in code
    
    # Verify the pattern for extracting tool calls exists
    assert "USE_TOOL:" in code or "tool_call_pattern" in code or "tool_call_match" in code 


@patch("langchain_openai.ChatOpenAI")
def test_reflection_with_memory_usage(mock_llm, test_agent):
    """Test that memory is properly used during the reflection process."""
    # Setup mock responses
    initial_response = MagicMock()
    initial_response.content = "Initial response"
    
    reflection_response = MagicMock()
    reflection_response.content = "This could be improved by adding more context."
    
    refined_response = MagicMock()
    refined_response.content = "Improved response with more context."
    
    # Configure mock to return different responses
    mock_llm.return_value.invoke.side_effect = [
        initial_response, reflection_response, refined_response
    ]
    
    # Mock the memory methods
    test_agent._retrieve_memories = MagicMock(return_value={
        "semantic": [{"fact": "Important context about the query"}],
        "episodic": [{"event": "Previous interaction about this topic"}]
    })
    
    test_agent._save_memory = MagicMock()
    
    # Run the agent
    result = test_agent.run("Test query")
    
    # Verify memory retrieval was called
    test_agent._retrieve_memories.assert_called_once_with("Test query")
    
    # Verify memory was saved at least once
    assert test_agent._save_memory.call_count >= 1
    
    # Verify result contains the refined output
    assert result == "Improved response with more context." 