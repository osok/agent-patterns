"""Tests for MCP tool provider integration."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import logging
import json
from typing import Dict, List, Any

from agent_patterns.core.tools.base import ToolProvider, ToolNotFoundError, ToolExecutionError
from agent_patterns.core.tools.providers.mcp_provider import MCPToolProvider, MCPServer
from agent_patterns.core.tools.registry import ToolRegistry
from agent_patterns.patterns.re_act_agent import ReActAgent
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import AIMessage


class MockMCPServer:
    """Mock implementation of an MCP server for testing."""
    
    def __init__(self, tools: List[Dict[str, Any]], server_id: str = "mock-server"):
        self.tools = tools
        self.server_id = server_id
        self.is_running = True
        self.call_history = []
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        return self.tools
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Call a tool with the given parameters."""
        self.call_history.append((tool_name, params))
        
        # Check if the tool exists
        matching_tools = [t for t in self.tools if t.get("name") == tool_name]
        if not matching_tools:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found")
        
        # Return a mock result
        return f"Mock result for {tool_name} with params {params}"


class MockMCPToolProvider(ToolProvider):
    """Mock implementation of the MCP tool provider for testing."""
    
    def __init__(self, tools: List[Dict[str, Any]]):
        self.tools = tools
        self.mock_server = MockMCPServer(tools)
        self.call_history = []
    
    def list_tools(self) -> List[Dict]:
        """List available tools."""
        return self.tools
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool with the given parameters."""
        self.call_history.append((tool_name, params))
        return self.mock_server.call_tool(tool_name, params)


@pytest.fixture
def mock_tool_provider():
    """Create a mock tool provider with some test tools."""
    tools = [
        {
            "name": "search_tool",
            "description": "Search for information",
            "parameters": {"query": {"type": "string"}}
        },
        {
            "name": "calculator",
            "description": "Perform calculations",
            "parameters": {"expression": {"type": "string"}}
        }
    ]
    return MockMCPToolProvider(tools)


@pytest.fixture
def mock_llm_configs():
    """Create mock LLM configs for testing."""
    from langchain_core.messages import AIMessage
    
    # Track if a tool was already called
    tool_called = {"value": False}
    
    def mock_llm_invoke(messages):
        """Mock LLM that returns a tool call first, then a final answer."""
        if not tool_called["value"]:
            # First call - return a tool call
            tool_called["value"] = True
            return AIMessage(content=(
                "Thought: I need to search for information.\n"
                "Action: search_tool(\"test query\")"
            ))
        else:
            # Second call - return a final answer
            return AIMessage(content=(
                "Thought: I have the information I need.\n"
                "Final Answer: Here is the search result for test query."
            ))
    
    mock_llm = MagicMock()
    mock_llm.invoke = mock_llm_invoke
    
    return {"default": mock_llm}


@pytest.fixture
def test_prompt_dir():
    """Get the path to test prompts directory."""
    # Get the path to the current test file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Return the path to the prompts directory
    return os.path.join(current_dir, "prompts")


def test_react_agent_with_mcp_tool_provider(mock_tool_provider, mock_llm_configs, test_prompt_dir):
    """Test that ReActAgent can use MCP tool provider."""
    # Create a ReActAgent with the mock tool provider
    agent = ReActAgent(
        llm_configs=mock_llm_configs,
        tool_provider=mock_tool_provider,
        prompt_dir=test_prompt_dir
    )
    
    # Run the agent with a test query
    result = agent.run("Test query")
    
    # Check that the tool provider was used
    assert len(mock_tool_provider.call_history) > 0
    assert mock_tool_provider.call_history[0][0] == "search_tool"
    assert "input" in mock_tool_provider.call_history[0][1]


def test_tool_registry_with_mcp_provider(mock_tool_provider):
    """Test that ToolRegistry works with MCPToolProvider."""
    # Create a tool registry with the mock provider
    registry = ToolRegistry([mock_tool_provider])
    
    # List tools
    tools = registry.list_tools()
    assert len(tools) == 2
    assert tools[0]["name"] == "search_tool"
    assert tools[1]["name"] == "calculator"
    
    # Execute a tool
    result = registry.execute_tool("search_tool", {"query": "test"})
    assert "Mock result" in result
    assert "search_tool" in result
    
    # Check that the tool provider was used
    assert len(mock_tool_provider.call_history) > 0
    assert mock_tool_provider.call_history[-1][0] == "search_tool"


def test_mcp_tool_provider_tool_not_found(mock_tool_provider):
    """Test that MCPToolProvider correctly handles tool not found errors."""
    with pytest.raises(ToolNotFoundError):
        mock_tool_provider.execute_tool("nonexistent_tool", {})


@patch('subprocess.Popen')
def test_mcp_server_communication(mock_popen):
    """Test that MCPServer correctly handles communication with the server process."""
    # Mock the process stdin, stdout, stderr
    mock_stdin = MagicMock()
    mock_stdout = MagicMock()
    mock_stderr = MagicMock()
    
    # Configure the mock_popen to return a process with stdin, stdout, stderr
    mock_process = MagicMock()
    mock_process.stdin = mock_stdin
    mock_process.stdout = mock_stdout
    mock_process.stderr = mock_stderr
    mock_process.poll.return_value = None
    
    # Configure mock_stdout.readline to return handshake and then tool list responses
    mock_stdout.readline.side_effect = [
        json.dumps({"type": "handshake_response", "status": "success", "version": "v1"}),
        json.dumps({"type": "list_tools_response", "status": "success", "tools": [{"name": "test_tool"}]})
    ]
    
    # Configure mock_popen to return mock_process
    mock_popen.return_value = mock_process
    
    # Create an MCPServer
    server = MCPServer(command=["test_command"], server_id="test-server")
    
    # Start the server (should trigger handshake)
    server.start()
    
    # Check that handshake message was sent
    mock_stdin.write.assert_called_with(json.dumps({"type": "handshake", "version": "v1"}) + "\n")
    
    # List tools
    tools = server.list_tools()
    
    # Check that list_tools message was sent
    assert mock_stdin.write.call_count == 2
    mock_stdin.write.assert_called_with(json.dumps({"type": "list_tools"}) + "\n")
    
    # Check tools response was parsed correctly
    assert len(tools) == 1
    assert tools[0]["name"] == "test_tool" 