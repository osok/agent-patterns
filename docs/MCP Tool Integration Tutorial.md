# MCP Tool Integration Tutorial

This tutorial provides step-by-step guidance on integrating Model Context Protocol (MCP) tools with agent patterns in the agent-patterns library.

## Introduction

Tool integration allows agents to perform actions beyond just generating text, such as:

- Searching the web
- Retrieving information from databases
- Making calculations
- Interacting with APIs
- Accessing file systems
- Running system commands

The agent-patterns library includes a flexible tool provider system with MCP integration, allowing agents to use a wide variety of external tools.

## What is MCP?

The Model Context Protocol (MCP) is a standardized interface for LLM agents to interact with external tools. MCP provides:

- A consistent format for tool definitions
- Standard request/response patterns
- Tool discovery mechanisms
- Error handling conventions

The protocol enables agents to work with tools from different providers without tightly coupling to specific implementations.

## Basic Tool Integration

### Step 1: Set Up an MCP Tool Provider

First, create an MCP tool provider that will manage connections to one or more MCP servers:

```python
from agent_patterns.core.tools.providers.mcp_provider import (
    MCPToolProvider, 
    create_mcp_server_connection
)

# Create an MCP server connection
mcp_server = create_mcp_server_connection("stdio", {
    "command": ["python", "calculator_server.py"],
    "working_dir": "./mcp_servers"
})

# Create the MCP tool provider
tool_provider = MCPToolProvider([mcp_server])
```

### Step 2: Configure an Agent with Tools

Add the tool provider to any agent pattern:

```python
from agent_patterns.patterns.re_act_agent import ReActAgent

agent = ReActAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o"}},
    tool_provider=tool_provider
)
```

### Step 3: Run the Agent

The agent will now have access to the tools provided by the MCP server:

```python
result = agent.run("Calculate the square root of 144")
```

## MCP Server Connection Types

The library supports multiple ways to connect to MCP tool servers:

### Standard Input/Output (stdio)

This method spawns a process and communicates via stdin/stdout. Ideal for local tools and development:

```python
stdio_server = create_mcp_server_connection("stdio", {
    "command": ["python", "calculator_server.py"],
    "working_dir": "./mcp_servers",
    "env": {"API_KEY": "your-api-key"}  # Optional environment variables
})
```

### HTTP/SSE Connection

Connect to remote MCP servers over HTTP or Server-Sent Events:

```python
http_server = create_mcp_server_connection("http", {
    "url": "http://localhost:8080/mcp",
    "headers": {"Authorization": "Bearer token"}
})
```

## Creating a Simple MCP Server

Here's how to create a basic MCP server that agents can connect to:

```python
import json
import sys

# Define available tools
TOOLS = [
    {
        "name": "calculator",
        "description": "Perform arithmetic calculations",
        "parameters": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate"
            }
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
        
        if tool_name == "calculator":
            try:
                # Safely evaluate the expression
                expression = params.get("expression", "")
                result = eval(expression, {"__builtins__": {}}, {"abs": abs, "max": max, "min": min})
                
                return {
                    "type": "call_tool_response",
                    "status": "success",
                    "result": str(result)
                }
            except Exception as e:
                return {
                    "type": "call_tool_response",
                    "status": "error",
                    "error_type": "evaluation_error",
                    "error": f"Error evaluating expression: {str(e)}"
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

# Main loop - read from stdin, write to stdout
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

Save this code to `calculator_server.py` and then connect to it using the MCP tool provider.

## Advanced Tool Integration

### Combining Multiple Tool Providers

You can combine tools from multiple sources:

```python
from agent_patterns.core.tools.providers.mcp_provider import (
    MCPToolProvider, 
    create_mcp_server_connection
)
from agent_patterns.core.tools.registry import ToolRegistry

# Create connections to different MCP servers
calculator_server = create_mcp_server_connection("stdio", {
    "command": ["python", "calculator_server.py"],
    "working_dir": "./mcp_servers"
})

search_server = create_mcp_server_connection("stdio", {
    "command": ["python", "search_server.py"],
    "working_dir": "./mcp_servers"
})

# Create individual providers
calculator_provider = MCPToolProvider([calculator_server])
search_provider = MCPToolProvider([search_server])

# Combine providers using the registry
registry = ToolRegistry([calculator_provider, search_provider])

# Use the registry with an agent
agent = ReActAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o"}},
    tool_provider=registry
)
```

### Creating a Custom Tool Provider

You can implement custom tool providers by extending the `ToolProvider` interface:

```python
from agent_patterns.core.tools.base import ToolProvider
from typing import Dict, List, Any

class CustomToolProvider(ToolProvider):
    """A custom tool provider implementation."""
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List the available tools."""
        return [
            {
                "name": "weather",
                "description": "Get weather information for a location",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "The location to get weather for"
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute the requested tool with the provided parameters."""
        if tool_name == "weather":
            location = params.get("location", "")
            # In a real implementation, you'd call a weather API here
            return f"The weather in {location} is sunny with a high of 75°F"
        else:
            from agent_patterns.core.tools.base import ToolNotFoundError
            raise ToolNotFoundError(f"Tool '{tool_name}' not found")
```

### Memory-Aware Tool Provider

You can enhance tools with memory awareness, allowing them to incorporate memory context into their execution:

```python
from agent_patterns.core.tools.base import ToolProvider
from agent_patterns.core.memory import CompositeMemory
import asyncio

class MemoryAwareToolProvider(ToolProvider):
    """A tool provider that incorporates memory context into tool calls."""
    
    def __init__(self, base_provider, memory=None):
        """Initialize with a base provider and optional memory."""
        self.base_provider = base_provider
        self.memory = memory
    
    def list_tools(self):
        """List all available tools from the base provider."""
        return self.base_provider.list_tools()
    
    def execute_tool(self, tool_name, params):
        """Execute a tool, potentially enhancing the call with memory context."""
        # If we have memory and the tool is search, add memory context
        if self.memory and tool_name == "search":
            # Get relevant memories
            memory_context = asyncio.run(self._get_memory_context())
            
            # Add memory context to the parameters
            params = params.copy()  # Make a copy to avoid modifying the original
            params["memory_context"] = memory_context
        
        # Execute the tool with the potentially enhanced parameters
        return self.base_provider.execute_tool(tool_name, params)
    
    async def _get_memory_context(self):
        """Get a simplified string representation of key memories."""
        if not self.memory:
            return ""
        
        # Retrieve relevant memories
        memories = await self.memory.retrieve_all("user interests preferences", limits={"semantic": 3})
        
        # Extract user interests from semantic memory
        interests = []
        for item in memories.get("semantic", []):
            if isinstance(item, dict) and item.get("attribute") == "interests":
                interests.extend(item.get("value", []))
        
        # Create a simple context string
        if interests:
            return f"User interests: {', '.join(interests)}"
        return ""
```

## Tool Integration with Different Agent Patterns

Each agent pattern integrates tools at appropriate points in its workflow:

### ReActAgent

The ReAct agent is specifically designed for tool use, integrating tools directly into its reasoning loop:

```python
agent = ReActAgent(
    llm_configs=llm_configs,
    tool_provider=tool_provider
)
```

### PlanAndSolveAgent

The PlanAndSolve agent can use tools during the execution of its plan steps:

```python
agent = PlanAndSolveAgent(
    llm_configs=llm_configs,
    tool_provider=tool_provider
)
```

### ReflexionAgent

The Reflexion agent can use tools during action execution and evaluate their results during reflection:

```python
agent = ReflexionAgent(
    llm_configs=llm_configs,
    tool_provider=tool_provider
)
```

### LLMCompilerAgent

The LLM Compiler agent can incorporate tools into its computation graph:

```python
agent = LLMCompilerAgent(
    llm_configs=llm_configs,
    tool_provider=tool_provider
)
```

## Example: Building a Tool-Enhanced Agent

Here's a complete example of building a ReActAgent with MCP tools:

```python
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add the parent directory to the path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.tools.providers.mcp_provider import (
    MCPToolProvider, 
    create_mcp_server_connection
)

def main():
    """Run the MCP tools example."""
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent
    mcp_servers_dir = str(project_root / "examples" / "mcp_servers")
    
    # Set up MCP server connections
    calculator_server = create_mcp_server_connection("stdio", {
        "command": ["python", "calculator_server.py"],
        "working_dir": mcp_servers_dir,
    })
    
    search_server = create_mcp_server_connection("stdio", {
        "command": ["python", "search_server.py"],
        "working_dir": mcp_servers_dir,
    })
    
    # Create MCP tool provider with multiple servers
    tool_provider = MCPToolProvider([calculator_server, search_server])
    
    # Configure LLM
    llm_configs = {
        "default": {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.7,
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    }
    
    # Create a ReActAgent with tools
    agent = ReActAgent(
        llm_configs=llm_configs,
        tool_provider=tool_provider
    )
    
    # Print available tools
    print("Available tools:")
    for tool in tool_provider.list_tools():
        print(f"- {tool['name']}: {tool['description']}")
    
    # Run a series of interactions to demonstrate tool usage
    examples = [
        "Calculate 15 * 7 + 22",
        "Search for information about quantum computing",
        "What's the square root of 256?",
        "Find recent news about artificial intelligence"
    ]
    
    for i, example in enumerate(examples):
        print(f"\n\n======= EXAMPLE {i+1} =======")
        print(f"User: {example}")
        
        # Run the agent
        result = agent.run(example)
        
        # Display the result
        print("\nAgent response:")
        print(result["output"])
        
        # Print the intermediate steps to show the tool usage
        print("\nIntermediate steps:")
        for j, step in enumerate(result.get("intermediate_steps", [])):
            print(f"Step {j+1}:")
            if len(step) >= 2:
                print(f"  Thought: {step[0]}")
                print(f"  Action: {step[1]}")
            if len(step) >= 3:
                print(f"  Observation: {step[2]}")

if __name__ == "__main__":
    main()
```

## Combining Memory and Tools

For the most powerful agents, you can combine memory and tool capabilities:

```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.memory import CompositeMemory
from agent_patterns.core.tools.providers.mcp_provider import MCPToolProvider

# Set up memory
memory = setup_memory()  # Your function that creates memory

# Set up tool provider
tool_provider = setup_tool_provider()  # Your function that creates tool provider

# Create a memory-aware tool provider
memory_tool_provider = MemoryAwareToolProvider(tool_provider, memory)

# Create an agent with both memory and tools
agent = ReActAgent(
    llm_configs=llm_configs,
    tool_provider=memory_tool_provider,
    memory=memory,
    memory_config={
        "semantic": True,
        "episodic": True,
        "procedural": True
    }
)
```

## Tool Execution Error Handling

The tool provider system includes error handling for various failure scenarios:

```python
from agent_patterns.core.tools.base import ToolNotFoundError, ToolExecutionError

try:
    result = tool_provider.execute_tool("nonexistent_tool", {})
except ToolNotFoundError as e:
    print(f"Tool not found: {e}")
    # Handle missing tool appropriately
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
    # Handle execution failure appropriately
```

## Best Practices

1. **Tool Design**:
   - Keep tools focused on doing one thing well
   - Use clear, descriptive names and descriptions
   - Properly document parameter requirements
   - Return structured, consistent results

2. **Security Considerations**:
   - Validate inputs before executing tool actions
   - Implement appropriate authentication for remote tools
   - Consider sandboxing for system-level operations
   - Be cautious about exposing sensitive functionality

3. **Performance Optimization**:
   - Reuse server connections when possible
   - Implement caching for frequent tool calls
   - Consider asynchronous tool execution for long-running operations
   - Balance tool complexity with execution speed

4. **Error Handling**:
   - Implement robust error handling in tool servers
   - Provide clear error messages that help diagnose issues
   - Consider retry mechanisms for transient failures
   - Avoid exposing sensitive information in error messages

5. **Agent Integration**:
   - Ensure prompt templates properly describe available tools
   - Consider providing examples of tool usage in prompts
   - Test edge cases and failure modes
   - Implement logging to track tool usage patterns

## Conclusion

Tool integration transforms agents from passive responders to active problem solvers capable of performing real-world actions. By incorporating MCP tools, you can build agents that can access external data, perform calculations, interact with APIs, and much more.

For more detailed information on the tool provider system, refer to the [Tool Provider API Documentation](Tool%20Provider%20API%20Documentation.md). 