# Agent-Patterns

A Python library providing reusable, extensible, and well-documented base classes for common AI agent workflows using [LangGraph](https://langchain.com/docs/langgraph) and [LangChain](https://python.langchain.com/en/latest/).

## Overview

Agent-Patterns implements proven design patterns for AI agents, reducing boilerplate and encouraging consistent best practices. The library is especially useful for developers needing to quickly build or customize advanced AI workflows without reinventing the wheel.

## Documentation

For comprehensive documentation of all patterns and components, see our [Documentation Site](docs/index.md).

### Guides

- **[Getting Started Guide](docs/guides/getting_started.md)**: Installation and your first agent
- **[Pattern Selection Guide](docs/guides/pattern_selection.md)**: Choosing the right pattern for your use case
- **[Advanced Customization Guide](docs/guides/advanced_customization.md)**: Extending the library
- **[Troubleshooting Guide](docs/guides/troubleshooting.md)**: Solving common issues
- **[Deployment Guide](docs/guides/deployment.md)**: Deploying in production environments
- **[Migration Guide](docs/guides/migration.md)**: Migrating from other frameworks

See all guides in the [Guides Index](docs/guides/index.md).

### Tutorials

- **[Research Assistant](docs/tutorials/research_assistant.md)**: Building an AI research assistant
- **[Customer Support Bot](docs/tutorials/customer_support_bot.md)**: Creating a support agent
- **[Code Generation Agent](docs/tutorials/code_generation_agent.md)**: Developing a code generator
- **[Multi-Agent System](docs/tutorials/multi_agent_system.md)**: Building a collaborative system

See all tutorials in the [Tutorials Index](docs/tutorials/index.md).

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

See all patterns in the [Patterns Index](docs/patterns/index.md).

### API Reference

- **[Core API](docs/api/core.md)**: Base classes and core components
- **[Patterns API](docs/api/patterns.md)**: Pattern implementations
- **[Memory API](docs/api/memory.md)**: Memory system
- **[Tools API](docs/api/tools.md)**: Tool system

See the complete API documentation in the [API Reference Index](docs/api/index.md).

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