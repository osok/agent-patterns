# MCP Servers Examples

This directory contains example Model Context Protocol (MCP) server implementations that can be used with the agent-patterns library.

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol for enabling AI models to use tools through a JSON-based message passing interface. MCP servers implement this protocol to provide tools that can be used by AI agents.

## Server Examples

### Calculator Server

The `calculator_server.py` implements a simple math calculator service with operations like addition, subtraction, multiplication, division, and more advanced math functions.

### Search Server

The `search_server.py` implements a mock search engine that can search for information on various topics.

## Running the Servers

Each server can be run independently from the command line:

```bash
# Start the calculator server
python examples/mcp_servers/calculator_server.py

# Start the search server
python examples/mcp_servers/search_server.py
```

The servers will automatically handle handshaking and tool discovery when an MCP client connects.

## Server Communication Details

MCP servers communicate via stdin/stdout with the following message format:

1. **Handshake**:
   - Client sends: `{"type": "handshake", "version": "v1"}`
   - Server responds: `{"type": "handshake_response", "status": "success", "version": "v1"}`

2. **Tool Discovery**:
   - Client sends: `{"type": "list_tools"}`
   - Server responds: `{"type": "list_tools_response", "status": "success", "tools": [...]}`

3. **Tool Execution**:
   - Client sends: `{"type": "call_tool", "name": "tool_name", "params": {...}}`
   - Server responds: `{"type": "call_tool_response", "status": "success", "result": ...}`

## Implementing Your Own MCP Server

To implement your own MCP server:

1. Create a new Python file in this directory.
2. Implement the MCP protocol (handshake, tool listing, tool execution).
3. Define your tools with appropriate functions.
4. Handle stdin/stdout communication correctly.

Here's a template to get started:

```python
#!/usr/bin/env python3
"""Custom MCP server template."""

import json
import sys
import logging
from typing import Dict, List, Any, Optional

# Configure logging to file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='custom_server.log',
    filemode='w'
)
logger = logging.getLogger("CustomMCPServer")

# Define your tool functions
def my_tool(param1: str, param2: int) -> str:
    """Example tool function."""
    return f"Processed {param1} with {param2}"

# Define your tools
TOOLS = [
    {
        "name": "my_tool",
        "description": "Example tool description",
        "parameters": {
            "param1": {"type": "string", "description": "First parameter"},
            "param2": {"type": "integer", "description": "Second parameter"}
        }
    }
]

# Main server loop
def main():
    """Main server loop."""
    while True:
        try:
            # Read a message from stdin
            message_str = sys.stdin.readline().strip()
            if not message_str:
                continue
                
            # Parse the message
            message = json.loads(message_str)
            logger.debug(f"Received message: {message}")
            
            # Handle the message
            if message.get("type") == "handshake":
                # Respond to handshake
                response = {"type": "handshake_response", "status": "success", "version": "v1"}
            elif message.get("type") == "list_tools":
                # Respond with tool list
                response = {"type": "list_tools_response", "status": "success", "tools": TOOLS}
            elif message.get("type") == "call_tool":
                # Execute the requested tool
                tool_name = message.get("name")
                params = message.get("params", {})
                
                if tool_name == "my_tool":
                    result = my_tool(params.get("param1", ""), params.get("param2", 0))
                    response = {"type": "call_tool_response", "status": "success", "result": result}
                else:
                    response = {"type": "call_tool_response", "status": "error", "error": f"Tool {tool_name} not found"}
            else:
                # Unknown message type
                response = {"type": "error", "error": f"Unknown message type: {message.get('type')}"}
            
            # Send the response
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            logger.debug(f"Sent response: {response}")
            
        except Exception as e:
            # Handle any errors
            logger.error(f"Error processing message: {e}")
            error_response = {"type": "error", "error": str(e)}
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
```

## Integration with Agent-Patterns

To use these MCP servers with agent-patterns:

1. Start the MCP server(s) in a separate terminal.
2. Use the `MCPToolProvider` from `agent_patterns.core.tools.providers.mcp_provider` to connect to the server.
3. Pass the tool provider to your agent during initialization.

See the `examples/mcp/mcp_example.py` script for a complete example of how to connect to MCP servers and use them with the ReActAgent pattern. 