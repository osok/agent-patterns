# Getting Started Guide

This guide will help you install Agent Patterns, set up your environment, and create your first agent.

## Prerequisites

To use Agent Patterns, you'll need:

- Python 3.9 or higher
- An OpenAI API key (or API keys for other supported LLM providers)
- Basic familiarity with Python and LLMs

## Installation

Install Agent Patterns using pip:

```bash
pip install agent-patterns
```

Alternatively, clone the repository and install from source:

```bash
git clone https://github.com/yourusername/agent-patterns.git
cd agent-patterns
pip install -r requirements.txt
pip install -e .
```

## Environment Configuration

1. Create a `.env` file in your project root:

```bash
# .env file
OPENAI_API_KEY="your-key"

# Default model configuration
DEFAULT_MODEL_PROVIDER=openai
DEFAULT_MODEL_NAME="gpt-4o"

# Optional specialized model configurations
THINKING_MODEL_PROVIDER=openai
THINKING_MODEL_NAME="gpt-4-turbo"
REFLECTION_MODEL_PROVIDER=anthropic
REFLECTION_MODEL_NAME="claude-3-opus-20240229"
```

2. Load environment variables in your code:

```python
from dotenv import load_dotenv
import os

load_dotenv()
```

## First Agent: Step-by-Step

Let's create a simple ReAct agent that can solve problems using reasoning and tools.

### 1. Create a new Python file (e.g., `my_first_agent.py`)

### 2. Import necessary modules

```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from dotenv import load_dotenv
import os
```

### 3. Configure the agent

```python
# Load environment variables
load_dotenv()

# Configure the LLM
llm_configs = {
    "default": {
        "provider": os.getenv("DEFAULT_MODEL_PROVIDER", "openai"),
        "model_name": os.getenv("DEFAULT_MODEL_NAME", "gpt-4o"),
    }
}

# Create the agent
agent = ReActAgent(llm_configs=llm_configs)
```

### 4. Run the agent with a query

```python
# Run the agent
result = agent.run("What's the population of France? Then calculate what 15% of that number would be.")

# Print the result
print(result)
```

### 5. Execute your script

```bash
python my_first_agent.py
```

You should see the agent's response, which includes reasoning steps, tool usage (searching for population data and performing calculations), and a final answer.

## Simple End-to-End Example

Here's a complete example that creates a ReAct agent with both memory and tool capabilities:

```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.memory import CompositeMemory, SemanticMemory, EpisodicMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence
from agent_patterns.core.tools.providers.mcp_provider import (
    MCPToolProvider, create_mcp_server_connection
)
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure the LLM
llm_configs = {
    "default": {
        "provider": os.getenv("DEFAULT_MODEL_PROVIDER", "openai"),
        "model_name": os.getenv("DEFAULT_MODEL_NAME", "gpt-4o"),
    }
}

# Set up memory
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# Create memory components
semantic_memory = SemanticMemory(persistence, namespace="user_semantic")
episodic_memory = EpisodicMemory(persistence, namespace="user_episodic")

# Create composite memory
memory = CompositeMemory({
    "semantic": semantic_memory,
    "episodic": episodic_memory
})

# Pre-populate with user information
asyncio.run(memory.save_to(
    "semantic", 
    {"entity": "user", "attribute": "name", "value": "Alice"}
))

# Set up tools (optional)
# For this example, assuming a calculator MCP server is available
mcp_servers = [
    create_mcp_server_connection("stdio", {
        "command": ["python", "examples/mcp_servers/calculator_server.py"],
        "working_dir": "./"
    })
]
tool_provider = MCPToolProvider(mcp_servers)

# Create ReAct agent with memory and tools
agent = ReActAgent(
    llm_configs=llm_configs,
    memory=memory,
    memory_config={
        "semantic": True,  # Enable semantic memory
        "episodic": True   # Enable episodic memory
    },
    tool_provider=tool_provider
)

# Run the agent
result = agent.run("Hello! Can you calculate 25 divided by 5 for me?")
print(result)

# Run again to see memory in action
result = agent.run("What's my name? Can you remind me what calculation I asked about earlier?")
print(result)
```

## Troubleshooting Installation Issues

### API Key Issues

- Make sure your API keys are correctly set in the `.env` file
- Check that `load_dotenv()` is called before accessing environment variables
- Verify you have sufficient credits/quota with your LLM provider

### Module Not Found Errors

- Ensure you've installed all dependencies: `pip install -r requirements.txt`
- If installing from source, make sure you ran `pip install -e .`
- Check your Python version (3.9+ required)

### Connection Errors

- Check your internet connection
- Verify firewall settings aren't blocking API calls
- Ensure any proxy settings are correctly configured

## Next Steps

After you've created your first agent, you might want to:

- Explore other agent patterns in the [Patterns Guide](../patterns/index.md)
- Learn about adding memory to your agents in the [Memory System Guide](../core/memory.md)
- Add tools to your agent using the [Tool System Guide](../core/tools.md)
- See the [Pattern Selection Guide](pattern_selection.md) to choose the right pattern for your use case