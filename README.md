# Agent-Patterns

A Python library providing reusable, extensible, and well-documented base classes for common AI agent workflows using [LangGraph](https://langchain.com/docs/langgraph) and [LangChain](https://python.langchain.com/en/latest/).

## Overview

Agent-Patterns implements proven design patterns for AI agents, reducing boilerplate and encouraging consistent best practices. The library is especially useful for developers needing to quickly build or customize advanced AI workflows without reinventing the wheel.

## Documentation

For comprehensive documentation of all patterns and components, see our [Documentation Site](docs/index.md).

### Supported Patterns

- **[ReAct (Reason + Act)](docs/patterns/re_act.md)**: Iterative reasoning and action for tool-based problem solving [(arXiv Paper)](https://arxiv.org/abs/2210.03629)
- **[Plan & Solve](docs/patterns/plan_and_solve.md)**: Decoupled planning and execution phases [(arXiv Paper)](https://arxiv.org/abs/2305.04091)
- **[Reflection](docs/patterns/reflection.md)**: Periodic reflection for strategic adjustments
- **[Reflexion](docs/patterns/reflexion.md)**: ReAct with reflection capabilities for self-improvement [(arXiv Paper)](https://arxiv.org/abs/2303.11366)
- **[LLM Compiler](docs/patterns/llm_compiler.md)**: Dynamic execution graph construction and optimization [(arXiv Paper)](https://arxiv.org/abs/2312.04511)
- **[ReWOO](docs/patterns/rewoo.md)**: Reason, World model, Observe, Outcome for simulation [(arXiv Paper)](https://arxiv.org/abs/2305.18323)
- **[LATS](docs/patterns/lats.md)**: LangChain Agents Tracing System for comprehensive observability [(arXiv Paper)](https://arxiv.org/abs/2310.04406)
- **[STORM](docs/patterns/storm.md)**: Self-evaluation, Think of options, Options for reasoning, Reason step by step, Mistake detection [(NAACL Paper)](https://aclanthology.org/2024.naacl-long.347.pdf)
- **[Self-Discovery](docs/patterns/self_discovery.md)**: Agents that discover their own capabilities
- **[Reflection and Refinement](docs/patterns/reflection_and_refinement.md)**: Structured reflection with explicit refinement steps

### Integrations

- **Model Context Protocol (MCP)**: Connect agents to standardized tool providers using Anthropic's [Model Context Protocol](https://modelcontextprotocol.io/)

## Architecture

The library follows these key architectural principles:

1. **Modular Base Classes**: Abstract base classes define common agent operations and Graph structures
2. **Externalized Configuration & Prompts**: Templates and parameters stored outside core code
3. **Developer Clarity**: Clear documentation of responsibilities and extension points
4. **Testability & Extensibility**: Separated components for easy testing and maintenance

For a comprehensive overview of the architecture, see the [Design Documentation](docs/Design.md).

## Integration Descriptions

### Model Context Protocol (MCP)

The Model Context Protocol (MCP) integration allows agents to connect with standardized tool providers following Anthropic's open protocol. This integration enables agents to access a wide ecosystem of tools without having to implement custom integrations for each one.

Key features:
- Connect to any MCP-compatible server
- Automatic tool discovery and execution
- Support for multiple MCP servers simultaneously
- Standardized interface for tool providers
- Custom tool provider implementation support

For detailed documentation, see:
- [Tool Provider API Documentation](docs/Tool%20Provider%20API%20Documentation.md)
- [MCP Tool Integration Tutorial](docs/MCP%20Tool%20Integration%20Tutorial.md)
- [Agent Tools Design](docs/Agent%20Tools%20Design.md.md)

### Memory Systems

All agent patterns include comprehensive memory capabilities that allow agents to store and retrieve information across interactions. The memory system enables agents to maintain context, learn from past interactions, and provide personalized responses.

Key features:
- **Multiple Memory Types**: Semantic (facts), Episodic (experiences), and Procedural (patterns)
- **Flexible Persistence**: In-memory, file system, and vector store backends
- **Customizable Retrieval**: Query-based memory retrieval with filtering options
- **Seamless Integration**: Works across all agent patterns with consistent API

For detailed documentation, see:
- [Memory API Documentation](docs/Memory%20API%20Documentation.md)
- [Memory Integration Tutorial](docs/Memory%20Integration%20Tutorial.md)
- [Agent Memory Design](docs/Agent%20Memory%20Design.md)
- [Memory and MCP Integration](docs/memory_and_mcp_integration.md)

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your environment:
```bash
# .env file
OPENAI_API_KEY="your-key"
THINKING_MODEL_PROVIDER=openai
THINKING_MODEL_NAME="gpt-4-turbo"
REFLECTION_MODEL_PROVIDER=anthropic
REFLECTION_MODEL_NAME="claude-3.5"
```

3. Use a pattern:
```python
from agent_patterns.patterns.reflection_agent import ReflectionAgent
from dotenv import load_dotenv
import os

load_dotenv()
llm_configs = {
    "documentation": {
        "provider": os.getenv("DOCUMENTATION_MODEL_PROVIDER"),
        "model_name": os.getenv("DOCUMENTATION_MODEL_NAME"),
    },
    "reflection": {
        "provider": os.getenv("REFLECTION_MODEL_PROVIDER"),
        "model_name": os.getenv("REFLECTION_MODEL_NAME"),
    }
}

agent = ReflectionAgent(llm_configs=llm_configs)
result = agent.run("Write a short story about a robot dog.")
print(result)
```

4. Using memory integration:
```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.memory import (
    SemanticMemory, 
    EpisodicMemory, 
    CompositeMemory
)
from agent_patterns.core.memory.persistence import InMemoryPersistence
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
llm_configs = {
    "default": {
        "provider": "openai",
        "model_name": "gpt-4o",
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

# Create agent with memory
agent = ReActAgent(
    llm_configs=llm_configs,
    memory=memory,
    memory_config={
        "semantic": True,  # Enable semantic memory
        "episodic": True   # Enable episodic memory
    }
)

# The agent will now use and update memory during conversations
result = agent.run("Tell me a story about my favorite animal.")
print(result)
```

5. Using the MCP integration:
```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.tools.providers.mcp_provider import (
    MCPToolProvider, create_mcp_server_connection
)
from dotenv import load_dotenv
import os

load_dotenv()
llm_configs = {
    "default": {
        "provider": "openai",
        "model_name": "gpt-4o",
    }
}

# Create MCP server connections
mcp_servers = [
    create_mcp_server_connection("stdio", {
        "command": ["python", "mcp_servers/calculator_server.py"],
        "working_dir": "./examples"
    })
]

# Create tool provider
tool_provider = MCPToolProvider(mcp_servers)

# Create ReAct agent with MCP tool provider
agent = ReActAgent(
    llm_configs=llm_configs,
    tool_provider=tool_provider
)
result = agent.run("Calculate the sum of 5 and 7.")
print(result)
```

## Creating New Patterns

1. Subclass `BaseAgent` or `MultiAgentBase`
2. Define `build_graph()` with your LangGraph nodes and transitions
3. Implement node functions for each step
4. Add prompts in `prompts/<YourPatternClass>/`
5. Create example scripts and tests

For more guidance on next steps and development, see [Next Steps](docs/Next%20Steps.md).

## Contributing

We welcome contributions! To add a new pattern:

1. Review existing patterns in `patterns/` for consistency
2. Follow the architecture principles
3. Include comprehensive documentation
4. Add tests and example usage
5. Submit a PR with your changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

[Contact information to be added]