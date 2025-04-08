# Agent-Patterns

A Python library providing reusable, extensible, and well-documented base classes for common AI agent workflows using [LangGraph](https://langchain.com/docs/langgraph) and [LangChain](https://python.langchain.com/en/latest/).

## Overview

Agent-Patterns implements proven design patterns for AI agents, reducing boilerplate and encouraging consistent best practices. The library is especially useful for developers needing to quickly build or customize advanced AI workflows without reinventing the wheel.

### Supported Patterns

- **ReAct (Tool Use)**: Iterative reasoning and action for tool-based problem solving [(arXiv Paper)](https://arxiv.org/abs/2210.03629)
- **Plan & Solve**: Decoupled planning and execution phases [(arXiv Paper)](https://arxiv.org/abs/2305.04091)
- **Reflection**: Self-critique and refinement of generated outputs
- **Reflexion**: Multi-trial learning with reflection memory [(arXiv Paper)](https://arxiv.org/abs/2303.11366)
- **LLM Compiler**: Dynamic execution graph construction and optimization [(arXiv Paper)](https://arxiv.org/abs/2312.04511)
- **REWOO (Worker-Solver)**: Separated reasoning and execution agents [(arXiv Paper)](https://arxiv.org/abs/2305.18323)
- **LATS (Language Agent Tree Search)**: Tree search over reasoning paths [(arXiv Paper)](https://arxiv.org/abs/2310.04406)
- **Self-Discovery**: Dynamic selection and adaptation of reasoning modules
- **STORM**: Structured topic research with multi-perspective synthesis

## Architecture

The library follows these key architectural principles:

1. **Modular Base Classes**: Abstract base classes define common agent operations and Graph structures
2. **Externalized Configuration & Prompts**: Templates and parameters stored outside core code
3. **Developer Clarity**: Clear documentation of responsibilities and extension points
4. **Testability & Extensibility**: Separated components for easy testing and maintenance

## Pattern Descriptions

### ReAct

ReAct (Reasoning and Acting) is a pattern that synergizes reasoning traces and task-specific actions in an interleaved manner. The agent explicitly generates verbal reasoning to track its thought process, updates action plans, and handles exceptions while also executing actions that allow it to interface with external sources like knowledge bases or environments. 

ReAct is best used for interactive tasks requiring both reasoning and tool use, such as question answering with information retrieval, fact verification, and interactive decision-making scenarios. It excels when tasks require accessing external information or when traceability and interpretability of the agent's decision process are important.

### Plan & Solve

Plan & Solve is a pattern that decouples the planning and execution phases of problem-solving. It first creates a strategic plan that divides complex tasks into smaller, manageable subtasks, and then systematically executes each subtask according to the plan. This approach helps address common issues like missing steps in the reasoning process.

This pattern is particularly effective for multi-step reasoning tasks, mathematical problem-solving, and complex workflows that benefit from explicit planning. It's ideal when accuracy is critical and when a structured approach to breaking down problems would help avoid errors or incomplete solutions.

### Reflection

Reflection is a pattern where an agent evaluates its own outputs, identifies potential issues, and refines its responses. It introduces a self-critique step where the agent analyzes the quality, accuracy, and completeness of its initial response before generating an improved version.

This pattern is best used when output quality and correctness are paramount, such as in content generation, code writing, and analytical tasks. It's especially valuable for reducing hallucinations, addressing reasoning errors, and enhancing the quality of complex generations without requiring external feedback.

### Reflexion

Reflexion enables agents to learn from previous attempts and mistakes through verbal reinforcement learning. Rather than updating model weights, Reflexion agents reflect on task feedback signals, maintaining their reflections in an episodic memory buffer to improve decision-making in subsequent attempts.

This pattern excels in scenarios requiring trial-and-error learning, such as complex problem-solving, coding tasks, and interactive environments where immediate adaptation is necessary. It's particularly effective when fine-tuning a model is impractical but learning from experience is essential.

### LLM Compiler

LLM Compiler treats language model function calling as a compilation process that optimizes execution flow. It consists of a Function Calling Planner that formulates execution plans, a Task Fetching Unit that dispatches function calling tasks, and an Executor that runs these tasks in parallel.

This pattern is ideal for workflows requiring multiple function calls that can be executed concurrently, significantly reducing latency and cost. It works best in scenarios like complex information gathering, multi-tool tasks, and when efficiency in orchestrating multiple API calls or tools is a priority.

### REWOO

REWOO (Reasoning WithOut Observation) decouples the reasoning process from external observations. Instead of interleaving reasoning and tool use, it separates them into distinct phases: a Worker that handles pure reasoning and planning, and a Solver that executes the actions and integrates observations.

This pattern is optimal for reducing token consumption and computational complexity, especially in multi-step tasks requiring external tool calls. It's well-suited for question answering, fact verification, and any scenario where efficiently separating thinking from acting provides performance or cost benefits.

### LATS

LATS (Language Agent Tree Search) integrates Monte Carlo Tree Search with language models to enable better planning and decision-making. It uses LMs for both policy (action selection) and value (state evaluation) functions, leveraging self-reflection and environment feedback to guide exploration of the action space.

This pattern excels in complex decision-making tasks with long horizons or multiple possible paths, such as programming, interactive question-answering, web navigation, and math problem-solving. It's particularly valuable when simple sequential decision-making isn't sufficient and deeper exploration of potential action sequences is beneficial.

### Self-Discovery

Self-Discovery is a pattern where agents dynamically select and adapt reasoning modules based on the task at hand. The agent evaluates which reasoning approaches are most appropriate for a given problem and can switch between different reasoning strategies as needed.

This pattern is best suited for dealing with diverse problems that might require different solving techniques, or when the most effective approach isn't known in advance. It's especially valuable for general-purpose assistants that must handle a wide range of query types with different optimal solving strategies.

### STORM

STORM (Structured Topic Research with Multi-perspective synthesis) is a pattern designed for comprehensive research tasks. It approaches complex topics by systematically breaking them down, exploring multiple perspectives, gathering diverse information, and synthesizing findings into coherent, balanced outputs.

This pattern is ideal for in-depth research questions, literature reviews, balanced analysis of controversial topics, and any task requiring comprehensive information gathering and synthesis. It's particularly effective when thoroughness, multiple viewpoints, and structured exploration of a topic are important.

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

## Creating New Patterns

1. Subclass `BaseAgent` or `MultiAgentBase`
2. Define `build_graph()` with your LangGraph nodes and transitions
3. Implement node functions for each step
4. Add prompts in `prompts/<YourPatternClass>/`
5. Create example scripts and tests

## Contributing

We welcome contributions! To add a new pattern:

1. Review existing patterns in `patterns/` for consistency
2. Follow the architecture principles
3. Include comprehensive documentation
4. Add tests and example usage
5. Submit a PR with your changes

## License

[License details to be added]

## Contact

[Contact information to be added]