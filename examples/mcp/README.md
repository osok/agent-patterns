# MCP Integration Examples

This directory contains examples for using the Model Context Protocol (MCP) integration with agent-patterns, demonstrating how to connect agents to external tool providers using the standardized MCP interface.

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol developed by Anthropic for enabling AI models to use tools through a JSON-based message passing interface. It allows for consistent tool discovery and execution across different systems and models.

## Examples

### MCP Example (mcp_example.py)

This example demonstrates how to:
1. Connect to MCP-compatible servers
2. Create a ReActAgent with an MCP tool provider
3. Use tools provided by the MCP servers to solve tasks

## Running the Examples

To run the examples, you need to:

1. Start the MCP server(s) in a separate terminal. Example servers are provided in the `examples/mcp_servers/` directory:

```bash
# Start the calculator server
python examples/mcp_servers/calculator_server.py

# In another terminal, start the search server
python examples/mcp_servers/search_server.py
```

2. Run the MCP integration example:

```bash
python examples/mcp/mcp_example.py
```

## Configuration

The example code uses environment variables for configuration. You can set these in a `.env` file or directly in your environment:

```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.7

# MCP Server Configuration
MCP_SERVER_STDIO_COMMAND=examples/mcp_servers/calculator_server.py
MCP_SERVER_STDIO_WORKING_DIR=.

# Add more MCP servers as needed
MCP_SERVER_ANOTHER_SERVER_COMMAND=examples/mcp_servers/search_server.py
MCP_SERVER_ANOTHER_SERVER_WORKING_DIR=.
```

## Creating Your Own MCP Integration

You can integrate your own MCP-compatible servers by following these steps:

1. Create an MCP server that follows the protocol specification (see `examples/mcp_servers/README.md`)
2. Use `create_mcp_server_connection()` to connect to your server
3. Create an `MCPToolProvider` with your server connection(s)
4. Pass the tool provider to your agent during initialization

Example code:

```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.tools.providers.mcp_provider import (
    MCPToolProvider, create_mcp_server_connection
)

# Create MCP server connections
mcp_servers = [
    create_mcp_server_connection("stdio", {
        "command": ["python", "path/to/your/server.py"],
        "working_dir": "./your_working_dir"
    })
]

# Create tool provider
tool_provider = MCPToolProvider(mcp_servers)

# Create agent with MCP tool provider
agent = ReActAgent(
    llm_configs=your_llm_configs,
    tool_provider=tool_provider
)

# Run the agent
result = agent.run("Your query here")
print(result)
``` 