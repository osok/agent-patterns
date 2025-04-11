# Agent Patterns Overview

This section provides documentation for each agent pattern implemented in this library. Each pattern represents a different approach to building AI agents with large language models (LLMs).

## Available Patterns

### Basic Patterns

- [ReAct](re_act.md): The foundational Reason + Act pattern that alternates between reasoning and action
- [Reflexion](reflexion.md): Extends ReAct with reflection capabilities for self-improvement

### Planning Patterns

- [LLM Compiler](llm_compiler.md): Separates planning from execution in a compilation-like approach
- [Plan and Solve](plan_and_solve.md): Two-phase approach with explicit planning followed by step execution

### Metacognitive Patterns

- [Reflection](reflection.md): Implements periodic reflection for strategic adjustment
- [Reflection and Refinement](reflection_and_refinement.md): Extends reflection with explicit refinement steps
- [STORM](storm.md): Comprehensive metacognitive framework for structured reasoning

### Simulation Patterns

- [ReWOO](rewoo.md): Reason, World model, Observe, Outcome for simulating actions before execution

### Advanced Patterns

- [Self-Discovery](self_discovery.md): Enables agents to discover their own capabilities
- [LATS](lats.md): LangChain Agents Tracing System for comprehensive observability

## Pattern Selection Guide

When selecting a pattern for your application, consider the following factors:

1. **Task Complexity**: For simple, direct tasks, use ReAct. For complex tasks requiring careful planning, consider LLM Compiler or Plan and Solve.

2. **Learning Requirements**: If the agent needs to improve over time, consider Reflexion or Reflection and Refinement.

3. **Exploration**: For tasks in unknown domains, Self-Discovery can help the agent adapt.

4. **Risk Management**: When safety is critical, STORM or ReWOO can provide more careful reasoning.

5. **Observability Needs**: If detailed monitoring is important, LATS provides comprehensive tracing.

6. **Reasoning Depth**: For complex reasoning tasks, STORM offers the most structured approach.

The following table provides a quick comparison:

| Pattern | Complexity | Planning | Reflection | Simulation | Tool Use | Observability |
|---------|------------|----------|------------|------------|----------|--------------|
| ReAct | Low | No | No | No | Yes | Basic |
| Reflexion | Medium | No | Yes | No | Yes | Basic |
| LLM Compiler | Medium | Yes | No | No | Yes | Medium |
| Self-Discovery | Medium | No | No | No | Yes | Medium |
| LATS | Low | No | No | No | Yes | High |
| Reflection | Medium | No | Yes | No | Yes | Medium |
| ReWOO | High | No | No | Yes | Yes | Medium |
| Reflection and Refinement | High | No | Yes | No | Yes | Medium |
| Plan and Solve | Medium | Yes | No | No | Yes | Medium |
| STORM | High | No | Yes | No | Yes | High |