# Agent-Patterns

A Python library providing reusable, extensible, and well-documented base classes for common AI agent workflows using [LangGraph](https://langchain.com/docs/langgraph) and [LangChain](https://python.langchain.com/en/latest/).

## Overview

Agent-Patterns implements proven design patterns for AI agents, reducing boilerplate and encouraging consistent best practices. The library is especially useful for developers needing to quickly build or customize advanced AI workflows without reinventing the wheel.

### Supported Patterns

- **ReAct (Tool Use)**: Iterative reasoning and action for tool-based problem solving
- **Plan & Solve**: Decoupled planning and execution phases
- **Reflection**: Self-critique and refinement of generated outputs
- **Reflexion**: Multi-trial learning with reflection memory
- **LLM Compiler**: Dynamic execution graph construction and optimization
- **REWOO (Worker-Solver)**: Separated reasoning and execution agents
- **LATS (Language Agent Tree Search)**: Tree search over reasoning paths
- **Self-Discovery**: Dynamic selection and adaptation of reasoning modules
- **STORM**: Structured topic research with multi-perspective synthesis

## Architecture

The library follows these key architectural principles:

1. **Modular Base Classes**: Abstract base classes define common agent operations and Graph structures
2. **Externalized Configuration & Prompts**: Templates and parameters stored outside core code
3. **Developer Clarity**: Clear documentation of responsibilities and extension points
4. **Testability & Extensibility**: Separated components for easy testing and maintenance

## Repository Structure

```
agent_patterns/
├── core/
│   ├── base_agent.py
│   └── multi_agent_base.py
├── patterns/
│   ├── re_act_agent.py
│   ├── plan_and_solve_agent.py
│   ├── reflection_agent.py
│   ├── reflexion_agent.py
│   ├── llm_compiler_agent.py
│   ├── rewoo_agent.py
│   ├── lats_agent.py
│   ├── self_discovery_agent.py
│   └── storm_agent.py
├── prompts/
│   ├── reflection/
│   │   ├── critic_prompt.md
│   │   └── revision_prompt.md
│   └── ...
├── examples/
│   ├── reflection_example.py
│   └── plan_example.py
├── tests/
│   ├── test_reflection.py
│   └── ...
├── .env
├── pyproject.toml
└── README.md
```

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