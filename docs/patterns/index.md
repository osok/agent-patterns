# Agent Patterns Overview

This section provides detailed information about the agent patterns implemented in this library.

Agent patterns are reusable architectural approaches for implementing LLM-based agent systems. Each pattern has strengths and weaknesses, making them suitable for different types of tasks and requirements.

## Available Patterns

- [ReAct](re_act.md): Combines reasoning and acting in a step-by-step manner
- [Reflexion](reflexion.md): Enables agents to reflect on past performance to improve future actions
- [LLM Compiler](llm_compiler.md): Structures agent tasks as compilable execution plans
- [Self-Discovery](self_discovery.md): Allows agents to discover their own capabilities and limitations
- [LATS](lats.md): Language Agent Task Solver pattern that breaks down complex tasks
- [Reflection](reflection.md): Implements structured reflection on intermediate results
- [ReWOO](rewoo.md): Reasoning With Out-of-Order execution
- [Reflection and Refinement](reflection_and_refinement.md): Iterative refinement through reflection
- [Plan and Solve](plan_and_solve.md): Explicit planning before solution implementation
- [STORM](storm.md): Self-Taught Operational Reasoning Mechanism