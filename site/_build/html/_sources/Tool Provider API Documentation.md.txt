# Tool Provider API Documentation

This document provides detailed information about the tool provider system implementation in the agent-patterns library.

## Overview

The agent-patterns tool provider system offers a standardized way for agents to discover and use various tools without tightly coupling to specific implementations. This capability is crucial for creating flexible, powerful agents that can interact with external systems.

The tool provider system is designed to be:

- **Extensible**: Support for multiple tool provider implementations 
- **Interoperable**: Consistent interface across all agent patterns
- **Standardized**: Unified format for tool definitions and parameters
- **Modular**: Ability to combine tools from different providers

## Core Components

### ToolProvider Interface

All tool providers implement the abstract `ToolProvider` interface, which defines the contract for tool discovery and execution:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class ToolProvider(ABC):
    """Abstract interface for tool providers."""
    
    @abstractmethod
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools with their metadata."""
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool with the given parameters."""
        pass
```

### Tool Format

Tools are specified using a standardized format, ensuring consistency across different providers:

```python
tool_spec = {
    "name": "calculator",                # Unique tool identifier
    "description": "Perform calculations", # Human-readable description
    "parameters": {                       # Parameters specification
        "expression": {                   # Parameter name
            "type": "string",             # Parameter type
            "description": "Mathematical expression to evaluate"  # Parameter description
        }
    }
}
```

### Tool Registry

The `ToolRegistry` class provides a way to combine and manage multiple tool providers:

```python
from agent_patterns.core.tools.registry import ToolRegistry
from agent_patterns.core.tools.base import ToolProvider

# Create tool providers
provider1 = SomeToolProvider()
provider2 = AnotherToolProvider()

# Create registry with multiple providers
registry = ToolRegistry([provider1, provider2])

# List all tools from all providers
all_tools = registry.list_tools()

# Execute a tool (automatically finds the right provider)
result = registry.execute_tool("tool_name", {"param1": "value1"})
```

## MCP Tool Provider

The library includes a built-in implementation of the Model Context Protocol (MCP), allowing you to connect to any MCP-compatible tool servers.

### MCPToolProvider

The `MCPToolProvider` class allows agents to connect to one or more MCP servers:

```python
from agent_patterns.core.tools.providers.mcp_provider import (
    MCPToolProvider, 
    create_mcp_server_connection
)

# Create MCP server connections
mcp_servers = [
    create_mcp_server_connection("stdio", {
        "command": ["python", "search_server.py"],
        "working_dir": "./mcp_servers"
    }),
    create_mcp_server_connection("stdio", {
        "command": ["python", "calculator_server.py"],
        "working_dir": "./mcp_servers"
    })
]

# Create the tool provider
tool_provider = MCPToolProvider(mcp_servers)

# List available tools
tools = tool_provider.list_tools()

# Execute a tool
result = tool_provider.execute_tool("search", {"query": "quantum physics"})
```

### MCP Server Connection Types

The library supports multiple ways to connect to MCP servers:

#### 1. Standard Input/Output (stdio)

Spawns an MCP server process and communicates via standard input/output:

```python
stdio_server = create_mcp_server_connection("stdio", {
    "command": ["python", "calculator_server.py"],
    "working_dir": "./examples/mcp_servers",
    "env": {"DEBUG": "true"}  # Optional environment variables
})
```

#### 2. HTTP/SSE Connection (planned for future)

Connect to a remote MCP server via HTTP or Server-Sent Events:

```python
sse_server = create_mcp_server_connection("sse", {
    "url": "http://localhost:8080/mcp",
    "headers": {"Authorization": "Bearer token"}
})
```

### MCPServer Class

The `MCPServer` class handles the low-level details of communicating with an MCP server:

```python
from agent_patterns.core.tools.providers.mcp_provider import MCPServer

# Create server (usually you would use create_mcp_server_connection instead)
server = MCPServer(
    command=["python", "server.py"],
    working_dir="./servers",
    env={"API_KEY": "secret"},
    server_id="search-server"
)

# Start the server
server.start()

# List tools
tools = server.list_tools()

# Call a tool
result = server.call_tool("tool_name", {"param": "value"})

# Stop the server when done
server.stop()
```

## Integration with Agents

All agent patterns in the library support tool provider integration through the `BaseAgent` class:

```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.tools.providers.mcp_provider import (
    MCPToolProvider, 
    create_mcp_server_connection
)

# Create MCP server connection
mcp_server = create_mcp_server_connection("stdio", {
    "command": ["python", "calculator_server.py"],
    "working_dir": "./examples/mcp_servers"
})

# Create tool provider
tool_provider = MCPToolProvider([mcp_server])

# Create agent with tool provider
agent = ReActAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o"}},
    tool_provider=tool_provider
)

# Run the agent (will have access to tools)
result = agent.run("Calculate the square root of 144")
```

## Creating Custom Tool Providers

You can create custom tool providers by implementing the `ToolProvider` interface:

```python
from agent_patterns.core.tools.base import ToolProvider
from typing import Dict, List, Any

class CustomToolProvider(ToolProvider):
    """A custom tool provider implementation."""
    
    def __init__(self):
        """Initialize the tool provider."""
        # Initialize any resources needed
        pass
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """List the available tools."""
        return [
            {
                "name": "custom_tool",
                "description": "Description of what the tool does",
                "parameters": {
                    "param1": {
                        "type": "string",
                        "description": "Description of parameter 1"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Description of parameter 2"
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute the requested tool with the provided parameters."""
        if tool_name == "custom_tool":
            # Implement tool logic here
            param1 = params.get("param1", "")
            param2 = params.get("param2", 0)
            
            # Process and return result
            return f"Processed {param1} with {param2}"
        else:
            # Handle unknown tool
            from agent_patterns.core.tools.base import ToolNotFoundError
            raise ToolNotFoundError(f"Tool '{tool_name}' not found")
```

## Creating MCP Servers

While the agent-patterns library is focused on the client side of MCP, you can create your own MCP-compatible servers that agents can connect to:

### Simple MCP Server Example

```python
import json
import sys

# Available tools
TOOLS = [
    {
        "name": "echo",
        "description": "Echoes the input text",
        "parameters": {
            "text": {"type": "string", "description": "Text to echo"}
        }
    }
]

def handle_message(message):
    """Handle incoming MCP messages."""
    if message["type"] == "handshake":
        return {
            "type": "handshake_response",
            "status": "success",
            "version": "v1"
        }
    elif message["type"] == "list_tools":
        return {
            "type": "list_tools_response",
            "status": "success",
            "tools": TOOLS
        }
    elif message["type"] == "call_tool":
        tool_name = message["tool"]
        params = message["params"]
        
        if tool_name == "echo":
            result = params.get("text", "")
            return {
                "type": "call_tool_response",
                "status": "success",
                "result": result
            }
        else:
            return {
                "type": "call_tool_response",
                "status": "error",
                "error_type": "tool_not_found",
                "error": f"Tool '{tool_name}' not found"
            }
    else:
        return {
            "type": "error",
            "error": f"Unknown message type: {message['type']}"
        }

# Main loop
for line in sys.stdin:
    try:
        message = json.loads(line)
        response = handle_message(message)
        print(json.dumps(response), flush=True)
    except json.JSONDecodeError:
        print(json.dumps({"type": "error", "error": "Invalid JSON"}), flush=True)
    except Exception as e:
        print(json.dumps({"type": "error", "error": str(e)}), flush=True)
```

## Exception Handling

The tool provider system defines specific exceptions for error handling:

### ToolNotFoundError

Raised when a requested tool doesn't exist:

```python
from agent_patterns.core.tools.base import ToolNotFoundError

try:
    result = tool_provider.execute_tool("nonexistent_tool", {})
except ToolNotFoundError as e:
    print(f"Tool not found: {e}")
```

### ToolExecutionError

Raised when a tool execution fails:

```python
from agent_patterns.core.tools.base import ToolExecutionError

try:
    result = tool_provider.execute_tool("calculator", {"expression": "1/0"})
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
```

## Best Practices

1. **Tool Design**:
   - Use clear, descriptive names for tools and parameters
   - Provide comprehensive descriptions of what each tool does
   - Properly specify parameter types and constraints
   - Keep tools focused on doing one thing well

2. **Error Handling**:
   - Always handle tool execution errors in your agents
   - Provide specific error messages that help diagnose issues
   - Use the appropriate exception types for different error cases

3. **Performance**:
   - Consider caching tool descriptions when appropriate
   - Reuse tool provider instances rather than creating new ones for each call
   - For long-running agents, consider connection management strategies

4. **Security**:
   - Validate inputs before passing them to tools
   - Be cautious about exposing sensitive operations through tools
   - Consider implementing access controls for different tools

## Examples

The library includes several examples demonstrating tool provider usage:

1. **Basic MCP Integration**: `examples/mcp/mcp_example.py`
2. **Custom Tool Provider**: `examples/mcp/custom_provider_example.py`
3. **MCP Server Implementation**: `examples/mcp_servers/calculator_server.py`
4. **Combined Memory and Tools**: `examples/combined_memory_tools_example.py`

For a full working example of an agent using tools, see the examples directory in the repository.

## Conclusion

The tool provider system offers a powerful, flexible way to extend agent capabilities through external tools. By using a standardized interface, agents can leverage a wide range of tools without being tightly coupled to specific implementations.

For more information on the MCP standard, see the [Model Context Protocol specification](https://modelcontextprotocol.io/).