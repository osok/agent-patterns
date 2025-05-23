"""Tests for memory and tool integration in PlanAndSolveAgent."""

import pytest
import logging
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock, patch, call
import inspect

from agent_patterns.patterns.plan_and_solve_agent import PlanAndSolveAgent
from agent_patterns.core.memory.composite import CompositeMemory
from agent_patterns.core.memory.semantic import SemanticMemory
from agent_patterns.core.memory.episodic import EpisodicMemory
from agent_patterns.core.tools.base import ToolProvider
from langchain_core.prompts import PromptTemplate


class MockMemoryPersistence:
    """Mock implementation of memory persistence for testing."""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



    def __init__(self):
        self.data = {}

    async def initialize(self) -> None:
        """Initialize the persistence layer."""
        # Nothing to initialize for the mock
        pass

    async def store(self, namespace: str, key: str, value: Any, metadata: Dict = None) -> None:
        """Store a value with an associated key."""
        if namespace not in self.data:
            self.data[namespace] = {}
        self.data[namespace][key] = {"value": value, "metadata": metadata or {}}

    async def retrieve(self, namespace: str, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        if namespace not in self.data or key not in self.data[namespace]:
            return None
        return self.data[namespace][key]["value"]

    async def search(self, namespace: str, query: Any, limit: int = 10, **filters) -> List[Dict]:
        """Search for values matching a query."""
        if namespace not in self.data:
            return []
        
        # In a real implementation, this would do semantic search
        # For testing, just return the most recent items up to the limit
        results = []
        for key, item in list(self.data[namespace].items())[:limit]:
            results.append({
                "id": key,
                "value": item["value"],
                "metadata": item["metadata"],
                "score": 0.9  # Mock relevance score
            })
        
        return results

    async def delete(self, namespace: str, key: str) -> bool:
        """Delete a value by key."""
        if namespace not in self.data or key not in self.data[namespace]:
            return False
        del self.data[namespace][key]
        return True

    async def clear_namespace(self, namespace: str) -> None:
        """Clear all data in a namespace."""
        if namespace in self.data:
            self.data[namespace] = {}


class MockToolProvider(ToolProvider):
    """Mock implementation of tool provider for testing."""

    def __init__(self, tools_config: List[Dict] = None):
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

    def list_tools(self) -> List[Dict]:
        """List available tools with their metadata."""
        return self.tools

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
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
    """Create a composite memory with mock persistence for testing."""
    # For testing, we'll create a simplified version of CompositeMemory
    # that uses synchronous methods instead of async
    
    # Create a mock that simulates a CompositeMemory
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
    """Create a PlanAndSolveAgent with mock components for testing."""
    llm_configs = {
        "planner": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "executor": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        }
    }
    
    return PlanAndSolveAgent(
        llm_configs=llm_configs,
        memory=mock_memory,
        tool_provider=mock_tool_provider,
        log_level=logging.ERROR
    )


@patch("langchain_openai.ChatOpenAI")
def test_plan_and_solve_constructor(mock_llm, mock_memory, mock_tool_provider):
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
        }
    }

    # Act
    agent = PlanAndSolveAgent(
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
def test_plan_and_solve_memory_integration(mock_llm, test_agent):
    """Test that memory integration is properly implemented."""
    # Verify that _retrieve_memories and _save_memory methods exist
    assert hasattr(test_agent, '_retrieve_memories')
    assert hasattr(test_agent, '_save_memory')
    
    # Check that memory methods are used in the codebase
    plan_solve_source = inspect.getsource(test_agent._plan_steps)
    assert "retrieve_memories" in plan_solve_source or "_retrieve_memories" in plan_solve_source
    
    execution_source = inspect.getsource(test_agent._execute_plan)
    assert "save_memory" in execution_source or "_save_memory" in execution_source
    
    # Verify memory retrieval in answer generation
    answer_source = inspect.getsource(test_agent._generate_answer)
    assert "retrieve_memories" in answer_source or "_retrieve_memories" in answer_source


@patch("langchain_openai.ChatOpenAI")
def test_plan_and_solve_tool_integration(mock_llm, test_agent, mock_tool_provider):
    """Test that tool provider integration is properly implemented."""
    # Verify that tool_provider is correctly passed and stored
    assert test_agent.tool_provider == mock_tool_provider
    
    # Verify tool_provider code integration in _execute_plan_step
    code = inspect.getsource(test_agent._execute_plan_step)
    assert "tool_provider" in code
    assert "execute_tool" in code
    
    # Verify the pattern for extracting tool calls exists
    assert "USE_TOOL:" in code or "tool_call_pattern" in code or "tool_call_match" in code 


@patch("langchain_openai.ChatOpenAI")
def test_plan_and_solve_tool_registration(mock_llm, test_agent):
    """Test that tools are correctly registered and used."""
    # Verify tool registry
    assert "echo" in test_agent.tool_registry.get_available_tool_names()
    
    # Check tool usage in code
    echo_tool = test_agent.tool_registry.get_tool("echo")
    assert echo_tool is not None
    assert echo_tool.name == "echo"
    
    # Test tool execution
    result = echo_tool.execute({"text": "test"})
    assert result == "Echo: test"


@patch("langchain_openai.ChatOpenAI")
def test_plan_and_solve_agent_execution(mock_llm, test_agent):
    """Test agent execution with tools."""
    # Mock the planning LLM to return a plan
    planning_response = MagicMock()
    planning_response.content = "1. Plan step 1: Use echo tool with 'test input'"
    
    # Mock the solving LLM to return final answer
    solving_response = MagicMock()
    solving_response.content = "Final answer: Echo test successful"
    
    # Configure mock to return different responses based on role
    mock_llm.return_value.invoke.side_effect = [planning_response, solving_response]
    
    # Replace private methods to avoid actual execution
    test_agent._execute_tool = MagicMock(return_value="Echo: test input")
    
    # Run the agent
    result = test_agent.run("Test query")
    
    # Verify result
    assert "Echo test successful" in result
    
    # Verify tool was called
    test_agent._execute_tool.assert_called_once()


@patch("langchain_openai.ChatOpenAI")
def test_plan_and_solve_with_function_calling(mock_llm, test_agent):
    """Test function calling setup for tool execution."""
    # Check that _get_available_tools function exists
    assert hasattr(test_agent, '_get_available_tools')
    
    # Verify function returns tools in correct format
    tools = test_agent._get_available_tools()
    assert isinstance(tools, list)
    assert len(tools) > 0
    assert "echo" in [tool.name for tool in tools]


def test_plan_and_solve_prompt_customization():
    """Test that prompts can be customized."""
    # Create custom prompts
    custom_planner_prompt = PromptTemplate.from_template(
        "Custom planner prompt: {input}"
    )
    
    custom_solver_prompt = PromptTemplate.from_template(
        "Custom solver prompt: {plan}\n{step_results}\n{input}"
    )
    
    # Create agent with custom prompts
    agent = PlanAndSolveAgent(
        llm_configs={
            "planner": "test_planner",
            "solver": "test_solver"
        },
        prompts={
            "planner": custom_planner_prompt,
            "solver": custom_solver_prompt
        }
    )
    
    # Verify custom prompts were set
    assert agent.prompts["planner"] == custom_planner_prompt
    assert agent.prompts["solver"] == custom_solver_prompt 