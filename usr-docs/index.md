# Agent Patterns Documentation

Welcome to the **Agent Patterns** documentation! This library provides 9 battle-tested AI agent workflow patterns implemented with LangGraph and LangChain.

```{admonition} Breaking Change in v0.2.0
:class: warning

This version is a complete rewrite from the ground up. The previous 0.1.x version used asyncio extensively, which caused significant reliability issues. Version 0.2.0+ uses a **synchronous-only architecture** for better reliability and easier debugging.
```

## What is Agent Patterns?

Agent Patterns is a Python library that implements proven AI agent architectures as reusable, composable patterns. Each pattern represents a different approach to building intelligent agents that can reason, plan, reflect, and execute tasks.

### Key Features

- **9 Production-Ready Patterns**: ReAct, Reflection, Self-Discovery, STORM, and more
- **Synchronous Design**: Simple, debuggable code without async complexity
- **Flexible Customization**: Multiple ways to customize prompts and behavior
- **Type-Safe**: Full type hints throughout
- **Multi-Provider**: Works with OpenAI, Anthropic, and other LLM providers

## Quick Start

```bash
pip install agent-patterns
```

```python
from agent_patterns.patterns import ReflectionAgent

agent = ReflectionAgent(
    llm_configs={
        "documentation": {"provider": "openai", "model": "gpt-4"},
        "reflection": {"provider": "openai", "model": "gpt-4"}
    }
)

result = agent.run("Write a blog post about AI agents")
print(result)
```

## Your Learning Journey

### 1. **Start Here: Understanding Patterns**

Begin by understanding what agent patterns are and how they differ:

- [What Are Agent Patterns?](concepts/what-are-patterns.md) - Core concepts
- [Choosing the Right Pattern](patterns/choosing-a-pattern.md) - Decision guide
- [Pattern Comparison Matrix](patterns/comparison-matrix.md) - Side-by-side comparison

### 2. **Learn Individual Patterns**

Dive deep into each pattern with theory, examples, and use cases:

**Foundational Patterns** (Start Here)
- [ReAct Agent](patterns/react.md) - Reason + Act with tool use
- [Reflection Agent](patterns/reflection.md) - Generate, critique, refine

**Planning & Execution**
- [Plan & Solve Agent](patterns/plan-and-solve.md) - Structured decomposition
- [Self-Discovery Agent](patterns/self-discovery.md) - Dynamic reasoning selection
- [REWOO Agent](patterns/rewoo.md) - Efficient planner-worker pattern

**Advanced Reasoning**
- [Reflexion Agent](patterns/reflexion.md) - Learning from failures
- [LATS Agent](patterns/lats.md) - Tree search over reasoning paths
- [LLM Compiler Agent](patterns/llm-compiler.md) - Parallel task execution

**Research & Synthesis**
- [STORM Agent](patterns/storm.md) - Multi-perspective research

### 3. **Customize Your Agents**

Learn how to tailor patterns to your specific needs:

- [Prompt Customization Guide](guides/prompt-customization.md) - Complete customization reference
- [Custom Instructions](guides/custom-instructions.md) - Add domain expertise
- [Prompt Overrides](guides/prompt-overrides.md) - Programmatic control
- [Setting Agent Goals](guides/setting-goals.md) - Configure objectives

### 4. **Build Production Systems**

Ready to deploy? Learn best practices:

- [API Reference](api/index.md) - Complete API documentation
- [Configuration Guide](guides/configuration.md) - LLM setup and tuning
- [Error Handling](guides/error-handling.md) - Robust error management
- [Testing Strategies](guides/testing.md) - Test your agents
- [Deployment Guide](guides/deployment.md) - Production deployment

## Pattern Overview

Quick reference for all patterns:

| Pattern | Best For | Complexity | When to Use |
|---------|----------|------------|-------------|
| **ReAct** | Tool-using tasks | Low | Need to interact with external tools/APIs |
| **Reflection** | High-quality content | Low | Want iterative refinement of outputs |
| **Plan & Solve** | Structured problems | Medium | Clear decomposable tasks |
| **Self-Discovery** | Complex reasoning | Medium | Need adaptive reasoning strategies |
| **Reflexion** | Trial-and-error | Medium | Learning from failures is important |
| **REWOO** | Efficient planning | Medium | Cost-conscious tool usage |
| **LATS** | Exploration tasks | High | Need to explore multiple solution paths |
| **LLM Compiler** | Parallel execution | High | Independent subtasks that can run concurrently |
| **STORM** | Research synthesis | High | Multi-perspective research reports |

## Use Case Quick Finder

Find the right pattern for your use case:

**Content Generation**
- Blog posts, articles → [Reflection](patterns/reflection.md)
- Research reports → [STORM](patterns/storm.md)
- Technical documentation → [Plan & Solve](patterns/plan-and-solve.md)

**Problem Solving**
- Mathematical problems → [Self-Discovery](patterns/self-discovery.md)
- Code debugging → [Reflexion](patterns/reflexion.md)
- Complex analysis → [LATS](patterns/lats.md)

**Task Execution**
- API interactions → [ReAct](patterns/react.md)
- Multi-step workflows → [LLM Compiler](patterns/llm-compiler.md)
- Efficient automation → [REWOO](patterns/rewoo.md)

**Research & Analysis**
- Multi-source research → [STORM](patterns/storm.md)
- Comparative analysis → [Self-Discovery](patterns/self-discovery.md)
- Exploratory research → [LATS](patterns/lats.md)

See the [full comparison matrix](patterns/comparison-matrix.md) for detailed use case analysis.

## Core Concepts

```{toctree}
:maxdepth: 2
:caption: Getting Started

installation
quickstart
concepts/what-are-patterns
concepts/architecture
```

```{toctree}
:maxdepth: 2
:caption: Agent Patterns

patterns/choosing-a-pattern
patterns/comparison-matrix
patterns/react
patterns/reflection
patterns/plan-and-solve
patterns/self-discovery
patterns/reflexion
patterns/rewoo
patterns/lats
patterns/llm-compiler
patterns/storm
```

```{toctree}
:maxdepth: 2
:caption: Customization Guides

guides/prompt-customization
guides/custom-instructions
guides/prompt-overrides
guides/setting-goals
guides/configuration
```

```{toctree}
:maxdepth: 2
:caption: Advanced Topics

guides/error-handling
guides/testing
guides/deployment
guides/extending-patterns
guides/best-practices
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/index
api/base-agent
api/patterns
api/types
```

```{toctree}
:maxdepth: 1
:caption: Additional Resources

examples/index
faq
troubleshooting
changelog
contributing
```

## Support & Community

- **GitHub**: [osok/agent-patterns](https://github.com/osok/agent-patterns)
- **Issues**: [Report bugs or request features](https://github.com/osok/agent-patterns/issues)
- **PyPI**: [agent-patterns](https://pypi.org/project/agent-patterns/)

## License

Agent Patterns is licensed under the MIT License. See [LICENSE](https://github.com/osok/agent-patterns/blob/main/LICENSE) for details.
