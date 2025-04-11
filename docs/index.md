# Agent-Patterns

A Python library providing reusable, extensible, and well-documented base classes for common AI agent workflows using [LangGraph](https://langchain.com/docs/langgraph) and [LangChain](https://python.langchain.com/en/latest/).

## Overview

Agent-Patterns implements proven design patterns for AI agents, reducing boilerplate and encouraging consistent best practices. The library is especially useful for developers needing to quickly build or customize advanced AI workflows without reinventing the wheel.

## Guides

- **[Getting Started Guide](guides/getting_started.md)**: Installation and your first agent
- **[Pattern Selection Guide](guides/pattern_selection.md)**: Choosing the right pattern for your use case
- **[Advanced Customization Guide](guides/advanced_customization.md)**: Extending the library
- **[Troubleshooting Guide](guides/troubleshooting.md)**: Solving common issues
- **[Deployment Guide](guides/deployment.md)**: Deploying in production environments
- **[Migration Guide](guides/migration.md)**: Migrating from other frameworks

See all guides in the [Guides Index](guides/index.md).

## Tutorials

- **[Research Assistant](tutorials/research_assistant.md)**: Building an AI research assistant
- **[Customer Support Bot](tutorials/customer_support_bot.md)**: Creating a support agent
- **[Code Generation Agent](tutorials/code_generation_agent.md)**: Developing a code generator
- **[Multi-Agent System](tutorials/multi_agent_system.md)**: Building a collaborative system

See all tutorials in the [Tutorials Index](tutorials/index.md).

## Supported Patterns

- **[ReAct (Reason + Act)](patterns/re_act.md)**: Iterative reasoning and action for tool-based problem solving [(arXiv Paper)](https://arxiv.org/abs/2210.03629)
- **[Plan & Solve](patterns/plan_and_solve.md)**: Decoupled planning and execution phases [(arXiv Paper)](https://arxiv.org/abs/2305.04091)
- **[Reflection](patterns/reflection.md)**: Periodic reflection for strategic adjustments
- **[Reflexion](patterns/reflexion.md)**: ReAct with reflection capabilities for self-improvement [(arXiv Paper)](https://arxiv.org/abs/2303.11366)
- **[LLM Compiler](patterns/llm_compiler.md)**: Dynamic execution graph construction and optimization [(arXiv Paper)](https://arxiv.org/abs/2312.04511)
- **[ReWOO](patterns/rewoo.md)**: Reason, World model, Observe, Outcome for simulation [(arXiv Paper)](https://arxiv.org/abs/2305.18323)
- **[LATS](patterns/lats.md)**: LangChain Agents Tracing System for comprehensive observability [(arXiv Paper)](https://arxiv.org/abs/2310.04406)
- **[STORM](patterns/storm.md)**: Self-evaluation, Think of options, Options for reasoning, Reason step by step, Mistake detection [(NAACL Paper)](https://aclanthology.org/2024.naacl-long.347.pdf)
- **[Self-Discovery](patterns/self_discovery.md)**: Agents that discover their own capabilities
- **[Reflection and Refinement](patterns/reflection_and_refinement.md)**: Structured reflection with explicit refinement steps

See all patterns in the [Patterns Index](patterns/index.md).

## API Reference

- **[Core API](api/core.md)**: Base classes and core components
- **[Patterns API](api/patterns.md)**: Pattern implementations
- **[Memory API](api/memory.md)**: Memory system
- **[Tools API](api/tools.md)**: Tool system

See the complete API documentation in the [API Reference Index](api/index.md).

## Integrations

### Model Context Protocol (MCP)

The Model Context Protocol (MCP) integration allows agents to connect with standardized tool providers following Anthropic's open protocol. This integration enables agents to access a wide ecosystem of tools without having to implement custom integrations for each one.

Key features:
- Connect to any MCP-compatible server
- Automatic tool discovery and execution
- Support for multiple MCP servers simultaneously
- Standardized interface for tool providers
- Custom tool provider implementation support

For detailed documentation, see:
- [Tool Provider API Documentation](Tool Provider API Documentation.md)
- [MCP Tool Integration Tutorial](MCP Tool Integration Tutorial.md)
- [Agent Tools Design](Agent_Tools_Design.md)

### Memory Systems

All agent patterns include comprehensive memory capabilities that allow agents to store and retrieve information across interactions. The memory system enables agents to maintain context, learn from past interactions, and provide personalized responses.

Key features:
- **Multiple Memory Types**: Semantic (facts), Episodic (experiences), and Procedural (patterns)
- **Flexible Persistence**: In-memory, file system, and vector store backends
- **Customizable Retrieval**: Query-based memory retrieval with filtering options
- **Seamless Integration**: Works across all agent patterns with consistent API

For detailed documentation, see:
- [Memory API Documentation](Memory API Documentation.md)
- [Memory Integration Tutorial](Memory Integration Tutorial.md)
- [Agent Memory Design](Agent Memory Design.md)
- [Memory and MCP Integration](memory_and_mcp_integration.md)

## Architecture

The library follows these key architectural principles:

1. **Modular Base Classes**: Abstract base classes define common agent operations and Graph structures
2. **Externalized Configuration & Prompts**: Templates and parameters stored outside core code
3. **Developer Clarity**: Clear documentation of responsibilities and extension points
4. **Testability & Extensibility**: Separated components for easy testing and maintenance

For a comprehensive overview of the architecture, see the [Design Documentation](Design.md).

## Creating New Patterns

1. Subclass `BaseAgent` or `MultiAgentBase`
2. Define `build_graph()` with your LangGraph nodes and transitions
3. Implement node functions for each step
4. Add prompts in `prompts/<YourPatternClass>/`
5. Create example scripts and tests

For more guidance on next steps and development, see [Next Steps](Next Steps.md).

## Contributing

We welcome contributions! To add a new pattern:

1. Review existing patterns in `patterns/` for consistency
2. Follow the architecture principles
3. Include comprehensive documentation
4. Add tests and example usage
5. Submit a PR with your changes

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/osok/agent-patterns/blob/main/LICENSE) file for details.

## Common Issues

### Package Installation
When installing the package via pip, you might encounter the following issues:

1. **Import Errors**: The package structure is different when installed via pip vs running from source:
   - Source code: `from src.agent_patterns...`
   - Installed package: `from agent_patterns...`

2. **Prompt Directory Path**: The examples might be looking for prompts in the wrong location:
   - Source code: `project_root / "src" / "agent_patterns" / "prompts"`
   - Installed package: `project_root / "agent_patterns" / "prompts"`

3. **Missing Agents in __init__.py**: Some agent classes might not be included in the package's `__init__.py` files.

### Fixing the Issues

We provide a helper script to automatically fix import paths and prompt directory issues:

```bash
# Run from the repository root
python tools/fix_imports.py
```

If you encounter import errors after installing the package, you may need to update the affected `__init__.py` files to include the missing classes.