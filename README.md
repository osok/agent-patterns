# Agent Patterns

A Python library of reusable AI agent workflow patterns implemented using LangGraph and LangChain. All patterns are synchronous and follow consistent architectural principles.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-read%20the%20docs-blue.svg)](https://agent-patterns.readthedocs.io/en/latest/)

📚 **[Full Documentation on Read the Docs](https://agent-patterns.readthedocs.io/en/latest/)**

> **⚠️ Breaking Change in v0.2.0**: This version is a complete rewrite from the ground up. The previous 0.1.x version used asyncio extensively, which caused significant reliability issues and made debugging extremely difficult. Version 0.2.0+ eliminates async/await entirely in favor of a **synchronous-only architecture**. This makes the library more reliable, easier to use, and much simpler to debug. If you were using v0.1.x, please note this is a breaking change - all patterns now use standard synchronous Python.

## Features

- **9 Battle-Tested Patterns**: ReAct, Plan & Solve, Reflection, Reflexion, LLM Compiler, REWOO, LATS, Self-Discovery, and STORM
- **Enterprise-Grade Prompts**: 150-300+ line comprehensive system prompts with 9-section structure (Role, Capabilities, Process, Examples, Edge Cases, Quality Standards, etc.) following Anthropic/OpenAI prompt engineering best practices
- **Synchronous Design**: No async/await complexity - simple, debuggable code
- **Flexible Prompt Customization**: Three ways to customize prompts - file-based, custom instructions, and programmatic overrides
- **Multi-Provider Support**: Works with OpenAI, Anthropic, and other LangChain-supported providers
- **Type-Safe**: Full type hints for better IDE support and fewer bugs
- **Extensible**: Abstract base classes make it easy to create custom patterns
- **Well-Tested**: Comprehensive test suite with >80% coverage

## Installation

### From PyPI (Recommended)

```bash
pip install agent-patterns
```

### From Source

```bash
# Clone the repository
git clone https://github.com/osok/agent-patterns.git
cd agent-patterns

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

### 1. Set Up Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your-key-here
THINKING_MODEL_PROVIDER=openai
THINKING_MODEL_NAME=gpt-4-turbo
```

### 2. Use a Pattern

#### ReAct Agent (Reason + Act)

```python
from agent_patterns.patterns import ReActAgent
import os
from dotenv import load_dotenv

load_dotenv()

# Configure LLMs
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.7,
    }
}

# Define tools
def search_tool(query):
    # Your search implementation
    return f"Results for: {query}"

tools = {"search": search_tool}

# Create and run agent
agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    max_iterations=5
)

result = agent.run("What is the weather in Paris?")
print(result)
```

#### Reflection Agent

```python
from agent_patterns.patterns import ReflectionAgent

llm_configs = {
    "documentation": {
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
    },
    "reflection": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
    },
}

agent = ReflectionAgent(
    llm_configs=llm_configs,
    max_reflection_cycles=1
)

result = agent.run("Write a short story about a robot dog")
print(result)
```

#### Plan & Solve Agent

```python
from agent_patterns.patterns import PlanAndSolveAgent

llm_configs = {
    "planning": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
    },
    "execution": {
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
    },
    "documentation": {
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
    },
}

agent = PlanAndSolveAgent(llm_configs=llm_configs)

result = agent.run("Write a research report on renewable energy")
print(result)
```

## Available Patterns

All 9 patterns are fully implemented and ready to use:

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **ReAct** | Reason + Act with tool use | Question answering with external tools |
| **Plan & Solve** | Planning then execution | Tasks requiring structured decomposition |
| **Reflection** | Generate, critique, refine | High-quality content generation |
| **Reflexion** | Multi-trial learning with reflection memory | Learning from mistakes across multiple attempts |
| **LLM Compiler** | DAG-based parallel tool execution | Optimized parallel task execution |
| **REWOO** | Worker-Solver pattern for cost efficiency | Efficient reasoning with reduced LLM calls |
| **LATS** | Tree search over reasoning paths | Exploring multiple solution strategies |
| **Self-Discovery** | Dynamic reasoning module selection | Adaptive problem-solving approach |
| **STORM** | Multi-perspective research synthesis | Comprehensive research from multiple viewpoints |

## Advanced Topics

For detailed information on the following topics, please see the [complete documentation](https://agent-patterns.readthedocs.io/en/latest/):

- **[Running Examples](https://agent-patterns.readthedocs.io/en/latest/)** - Detailed example usage
- **[Creating Custom Patterns](https://agent-patterns.readthedocs.io/en/latest/)** - Extend BaseAgent to build your own patterns
- **[Customizing Prompts](https://agent-patterns.readthedocs.io/en/latest/)** - File-based, custom instructions, and programmatic overrides
- **[Configuration](https://agent-patterns.readthedocs.io/en/latest/)** - LLM roles, environment variables, and settings
- **[Testing](https://agent-patterns.readthedocs.io/en/latest/)** - Running tests and contributing
- **[API Reference](https://agent-patterns.readthedocs.io/en/latest/)** - Complete API documentation

## Requirements

- Python 3.10+
- LangGraph >= 0.2.0
- LangChain >= 0.3.0
- python-dotenv >= 1.0.0

## Contributing

Contributions are welcome! Please see our [contribution guide](https://agent-patterns.readthedocs.io/en/latest/) for details on:

- Setting up your development environment
- Running tests and code quality tools
- Submitting pull requests
- Code style and conventions

Quick start for contributors:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format and lint
black agent_patterns tests examples
ruff check agent_patterns tests examples
mypy agent_patterns
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

📚 **[Complete documentation available on Read the Docs](https://agent-patterns.readthedocs.io/en/latest/)**

Additional resources in this repository:
- [Design Document](docs/Design.md) - Detailed architectural design
- [Task List](docs/task_list.md) - Development progress tracking
- [Implementation Notes](docs/notes.md) - Technical decisions and guidelines

## Support

- **Documentation**: [Read the Docs](https://agent-patterns.readthedocs.io/en/latest/)
- **Issues**: [GitHub Issues](https://github.com/osok/agent-patterns/issues)
- **Discussions**: [GitHub Discussions](https://github.com/osok/agent-patterns/discussions)
- **PyPI**: [agent-patterns on PyPI](https://pypi.org/project/agent-patterns/)

---

**Built with ❤️ for the AI agent community**
