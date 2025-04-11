# Agent Patterns Documentation

Welcome to the Agent Patterns documentation. This project provides a collection of reusable agent patterns for building sophisticated AI agents.

## Overview

Agent Patterns is a library that implements various agent architectures and patterns for large language model (LLM) applications. It provides a structured approach to building agents that can reason, use tools, maintain memory, and adapt their strategies.

## Core Components

The library is built around these fundamental components:

- [Base Agent](core/base_agent.md): The foundation for all agent patterns
- [Memory System](core/memory.md): Enables agents to store and retrieve information
- [Tool System](core/tools.md): Allows agents to interact with external systems

## Patterns

The library includes the following agent patterns:

- [ReAct](patterns/re_act.md): Reason + Act pattern for alternating between reasoning and action
- [Reflexion](patterns/reflexion.md): ReAct with reflection capabilities for self-improvement
- [LLM Compiler](patterns/llm_compiler.md): Compilation-like approach separating planning from execution
- [Self-Discovery](patterns/self_discovery.md): Agents that discover their own capabilities
- [LATS](patterns/lats.md): LangChain Agents Tracing System for observability
- [Reflection](patterns/reflection.md): Periodic reflection for strategic adjustment
- [ReWOO](patterns/rewoo.md): Reason, World model, Observe, Outcome for simulation
- [Reflection and Refinement](patterns/reflection_and_refinement.md): Structured reflection with explicit refinement
- [Plan and Solve](patterns/plan_and_solve.md): Two-phase approach with planning and step execution
- [STORM](patterns/storm.md): Comprehensive metacognitive framework for reasoning

For a comparison and selection guide, see the [Patterns Overview](patterns/index.md).

## Getting Started

To use Agent Patterns in your project:

```python
from agent_patterns.patterns import ReActAgent, ReflexionAgent
from agent_patterns.core.tools import ToolRegistry
from agent_patterns.core.memory import CompositeMemory, EpisodicMemory

# Create tool registry with your tools
tool_registry = ToolRegistry([your_tools])

# Create memory system
memory = CompositeMemory({
    "episodic": EpisodicMemory()
})

# Configure LLM
llm_configs = {
    "default": {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.7
    }
}

# Initialize an agent
agent = ReActAgent(
    llm_configs=llm_configs,
    tool_provider=tool_registry,
    memory=memory
)

# Run the agent
result = agent.run("Your task or query here")
```

## Examples

Check the `examples/` directory for implementation examples of each pattern.

## Contributing

Contributions to Agent Patterns are welcome! See the [GitHub repository](https://github.com/your-repo/agent-patterns) for more information.