# Agent-Patterns

A Python library providing reusable, extensible, and well-documented base classes for common AI agent workflows using [LangGraph](https://langchain.com/docs/langgraph) and [LangChain](https://python.langchain.com/en/latest/).

## Overview

Agent-Patterns implements proven design patterns for AI agents, reducing boilerplate and encouraging consistent best practices. The library is especially useful for developers needing to quickly build or customize advanced AI workflows without reinventing the wheel.

## Documentation

For comprehensive documentation of all patterns and components, see our [Documentation Site](https://agent-patterns.readthedocs.io/).

### Guides

- **[Getting Started Guide](https://agent-patterns.readthedocs.io/en/latest/guides/getting_started.html)**: Installation and your first agent
- **[Pattern Selection Guide](https://agent-patterns.readthedocs.io/en/latest/guides/pattern_selection.html)**: Choosing the right pattern for your use case
- **[Advanced Customization Guide](https://agent-patterns.readthedocs.io/en/latest/guides/advanced_customization.html)**: Extending the library
- **[Troubleshooting Guide](https://agent-patterns.readthedocs.io/en/latest/guides/troubleshooting.html)**: Solving common issues
- **[Deployment Guide](https://agent-patterns.readthedocs.io/en/latest/guides/deployment.html)**: Deploying in production environments
- **[Migration Guide](https://agent-patterns.readthedocs.io/en/latest/guides/migration.html)**: Migrating from other frameworks

See all guides in the [Guides Index](https://agent-patterns.readthedocs.io/en/latest/guides/index.html).

### Tutorials

- **[Research Assistant](https://agent-patterns.readthedocs.io/en/latest/tutorials/research_assistant.html)**: Building an AI research assistant
- **[Customer Support Bot](https://agent-patterns.readthedocs.io/en/latest/tutorials/customer_support_bot.html)**: Creating a support agent
- **[Code Generation Agent](https://agent-patterns.readthedocs.io/en/latest/tutorials/code_generation_agent.html)**: Developing a code generator
- **[Multi-Agent System](https://agent-patterns.readthedocs.io/en/latest/tutorials/multi_agent_system.html)**: Building a collaborative system

See all tutorials in the [Tutorials Index](https://agent-patterns.readthedocs.io/en/latest/tutorials/index.html).

### Supported Patterns

- **[ReAct (Reason + Act)](https://agent-patterns.readthedocs.io/en/latest/patterns/re_act.html)**: Iterative reasoning and action for tool-based problem solving [(arXiv Paper)](https://arxiv.org/abs/2210.03629)
- **[Plan & Solve](https://agent-patterns.readthedocs.io/en/latest/patterns/plan_and_solve.html)**: Decoupled planning and execution phases [(arXiv Paper)](https://arxiv.org/abs/2305.04091)
- **[Reflection](https://agent-patterns.readthedocs.io/en/latest/patterns/reflection.html)**: Periodic reflection for strategic adjustments
- **[Reflexion](https://agent-patterns.readthedocs.io/en/latest/patterns/reflexion.html)**: ReAct with reflection capabilities for self-improvement [(arXiv Paper)](https://arxiv.org/abs/2303.11366)
- **[LLM Compiler](https://agent-patterns.readthedocs.io/en/latest/patterns/llm_compiler.html)**: Dynamic execution graph construction and optimization [(arXiv Paper)](https://arxiv.org/abs/2312.04511)
- **[ReWOO](https://agent-patterns.readthedocs.io/en/latest/patterns/rewoo.html)**: Reason, World model, Observe, Outcome for simulation [(arXiv Paper)](https://arxiv.org/abs/2305.18323)
- **[LATS](https://agent-patterns.readthedocs.io/en/latest/patterns/lats.html)**: LangChain Agents Tracing System for comprehensive observability [(arXiv Paper)](https://arxiv.org/abs/2310.04406)
- **[STORM](https://agent-patterns.readthedocs.io/en/latest/patterns/storm.html)**: Self-evaluation, Think of options, Options for reasoning, Reason step by step, Mistake detection [(NAACL Paper)](https://aclanthology.org/2024.naacl-long.347.pdf)
- **[Self-Discovery](https://agent-patterns.readthedocs.io/en/latest/patterns/self_discovery.html)**: Agents that discover their own capabilities
- **[Reflection and Refinement](https://agent-patterns.readthedocs.io/en/latest/patterns/reflection_and_refinement.html)**: Structured reflection with explicit refinement steps

See all patterns in the [Patterns Index](https://agent-patterns.readthedocs.io/en/latest/patterns/index.html).

### API Reference

- **[Core API](https://agent-patterns.readthedocs.io/en/latest/api/core.html)**: Base classes and core components
- **[Patterns API](https://agent-patterns.readthedocs.io/en/latest/api/patterns.html)**: Pattern implementations
- **[Memory API](https://agent-patterns.readthedocs.io/en/latest/api/memory.html)**: Memory system
- **[Tools API](https://agent-patterns.readthedocs.io/en/latest/api/tools.html)**: Tool system

See the complete API documentation in the [API Reference Index](https://agent-patterns.readthedocs.io/en/latest/api/index.html).

### Integrations

- **Model Context Protocol (MCP)**: Connect agents to standardized tool providers using Anthropic's [Model Context Protocol](https://modelcontextprotocol.io/)

## Architecture

The library follows these key architectural principles:

1. **Modular Base Classes**: Abstract base classes define common agent operations and Graph structures
2. **Externalized Configuration & Prompts**: Templates and parameters stored outside core code
3. **Developer Clarity**: Clear documentation of responsibilities and extension points
4. **Testability & Extensibility**: Separated components for easy testing and maintenance

For a comprehensive overview of the architecture, see the [Design Documentation](https://agent-patterns.readthedocs.io/en/latest/Design.html).

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
- [Tool Provider API Documentation](https://agent-patterns.readthedocs.io/en/latest/Tool%20Provider%20API%20Documentation.html)
- [MCP Tool Integration Tutorial](https://agent-patterns.readthedocs.io/en/latest/MCP%20Tool%20Integration%20Tutorial.html)
- [Agent Tools Design](https://agent-patterns.readthedocs.io/en/latest/Agent%20Tools%20Design.html)

### Memory Systems

All agent patterns include comprehensive memory capabilities that allow agents to store and retrieve information across interactions. The memory system enables agents to maintain context, learn from past interactions, and provide personalized responses.

Key features:
- **Multiple Memory Types**: Semantic (facts), Episodic (experiences), and Procedural (patterns)
- **Flexible Persistence**: In-memory, file system, and vector store backends
- **Customizable Retrieval**: Query-based memory retrieval with filtering options
- **Seamless Integration**: Works across all agent patterns with consistent API

For detailed documentation, see:
- [Memory API Documentation](https://agent-patterns.readthedocs.io/en/latest/Memory%20API%20Documentation.html)
- [Memory Integration Tutorial](https://agent-patterns.readthedocs.io/en/latest/Memory%20Integration%20Tutorial.html)
- [Agent Memory Design](https://agent-patterns.readthedocs.io/en/latest/Agent%20Memory%20Design.html)
- [Memory and MCP Integration](https://agent-patterns.readthedocs.io/en/latest/memory_and_mcp_integration.html)

## Creating New Patterns

1. Subclass `BaseAgent` or `MultiAgentBase`
2. Define `build_graph()` with your LangGraph nodes and transitions
3. Implement node functions for each step
4. Add prompts in `prompts/<YourPatternClass>/`
5. Create example scripts and tests

For more guidance on next steps and development, see [Next Steps](https://agent-patterns.readthedocs.io/en/latest/Next%20Steps.html).

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