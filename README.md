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

### Currently Implemented

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **ReAct** | Reason + Act with tool use | Question answering with external tools |
| **Plan & Solve** | Planning then execution | Tasks requiring structured decomposition |
| **Reflection** | Generate, critique, refine | High-quality content generation |

### Coming Soon

- **Reflexion**: Multi-trial learning with reflection memory
- **LLM Compiler**: DAG-based parallel tool execution
- **REWOO**: Worker-Solver pattern for cost efficiency
- **LATS**: Tree search over reasoning paths
- **Self-Discovery**: Dynamic reasoning module selection
- **STORM**: Multi-perspective research synthesis

## Project Structure

```
agent-patterns/
├── agent_patterns/
│   ├── core/              # Base classes
│   │   ├── base_agent.py
│   │   └── multi_agent_base.py
│   ├── patterns/          # Pattern implementations
│   │   ├── re_act_agent.py
│   │   ├── plan_and_solve_agent.py
│   │   └── reflection_agent.py
│   └── prompts/           # Externalized prompt templates
│       ├── ReActAgent/
│       ├── PlanAndSolveAgent/
│       └── ReflectionAgent/
├── examples/              # Usage examples
│   ├── react_example.py
│   └── reflection_example.py
├── tests/                 # Unit tests
│   ├── test_base_agent.py
│   ├── test_re_act_agent.py
│   └── test_reflection_agent.py
└── docs/                  # Documentation
    ├── Design.md
    ├── task_list.md
    └── notes.md
```

## Running Examples

```bash
# Ensure you're in the virtual environment and have set up .env

# Run ReAct example
python examples/react_example.py

# Run Reflection example
python examples/reflection_example.py
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent_patterns --cov-report=html

# Run specific test file
pytest tests/test_base_agent.py

# Run with verbose output
pytest -v
```

## Creating Custom Patterns

Extend `BaseAgent` to create your own pattern:

```python
from agent_patterns.core import BaseAgent
from langgraph.graph import StateGraph, END

class MyCustomAgent(BaseAgent):
    def build_graph(self):
        workflow = StateGraph(dict)

        # Define your nodes
        workflow.add_node("step1", self._step1)
        workflow.add_node("step2", self._step2)

        # Define edges
        workflow.set_entry_point("step1")
        workflow.add_edge("step1", "step2")
        workflow.add_edge("step2", END)

        # Compile
        self.graph = workflow.compile()

    def run(self, input_data):
        if self.graph is None:
            raise ValueError("Graph not built")

        initial_state = {
            "input": input_data,
            "output": None
        }

        result_state = self.graph.invoke(initial_state)
        return result_state.get("output")

    def _step1(self, state):
        # Your logic here
        return state

    def _step2(self, state):
        # Your logic here
        return state
```

## Customizing Prompts

Agent Patterns provides three flexible ways to customize prompts without modifying the library code:

### 1. File-Based Customization (Default)

Prompts are stored as markdown files in `agent_patterns/prompts/{PatternName}/{StepName}/`:

```
prompts/
└── ReActAgent/
    └── ThoughtStep/
        ├── system.md    # System prompt
        └── user.md      # User prompt template
```

You can provide a custom prompt directory:

```python
agent = ReActAgent(
    llm_configs=llm_configs,
    prompt_dir="my_custom_prompts"  # Use your custom prompt directory
)
```

### 2. Custom Instructions

Add domain-specific context, constraints, or guidelines that apply to ALL prompts in the workflow:

```python
medical_instructions = """
You are providing information in the MEDICAL domain:
- Always prioritize medical accuracy
- Include appropriate medical disclaimers
- Use proper medical terminology
- Recommend consulting healthcare professionals
"""

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=medical_instructions  # Applied to all system prompts
)
```

**Use Cases:**
- Adding domain expertise (medical, legal, financial)
- Enforcing compliance requirements
- Setting tone/style guidelines
- Specifying audience level
- Adding ethical guidelines

See [examples/custom_instructions_example.py](examples/custom_instructions_example.py) for comprehensive examples.

### 3. Prompt Overrides

Programmatically replace specific prompts for fine-grained control:

```python
overrides = {
    "DiscoverModules": {
        "system": "You are an expert at selecting reasoning strategies.",
        "user": "Task: {task}\n\nSelect the best modules:\n{modules}"
    },
    "SynthesizeOutput": {
        "system": "You synthesize reasoning into clear answers.",
        "user": "Task: {task}\n\nSteps:\n{reasoning_steps}\n\nFinal answer:"
    }
}

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=overrides  # Override specific prompts
)
```

**Use Cases:**
- A/B testing different prompts
- Experimenting with prompt engineering
- Creating specialized pattern variants
- Dynamic prompt generation
- Adjusting complexity levels

See [examples/prompt_overrides_example.py](examples/prompt_overrides_example.py) for comprehensive examples.

### 4. Combining Approaches

You can combine all three methods for maximum flexibility:

```python
agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_dir="my_prompts",           # 1. Custom directory
    custom_instructions=instructions,   # 2. Add domain context
    prompt_overrides=overrides         # 3. Override specific steps
)
```

**Priority Order:**
1. `prompt_overrides` (highest priority - complete replacement)
2. File system prompts from `prompt_dir`
3. `custom_instructions` (lowest priority - appended to system prompts)

This allows you to start with base prompts, add domain-specific context, and selectively override specific steps as needed.

## Configuration

### LLM Roles

Different patterns use different LLM roles:

- **thinking**: Primary reasoning (usually expensive model like GPT-4)
- **reflection**: Self-critique (can be same or different model)
- **documentation**: Output generation (can use cheaper model)
- **planning**: Task decomposition (usually expensive model)
- **execution**: Task execution (can use cheaper model)

### Environment Variables

See `.env.example` for all configuration options:

```env
# API Keys
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Model Configuration
THINKING_MODEL_PROVIDER=openai
THINKING_MODEL_NAME=gpt-4-turbo
THINKING_TEMPERATURE=0.7
THINKING_MAX_TOKENS=2000

# Pattern-Specific
MAX_ITERATIONS=5
MAX_TRIALS=3
MAX_REFLECTION_CYCLES=2
```

## Design Principles

1. **Synchronous Only**: No async/await for simplicity and debuggability
2. **Externalized Configuration**: Prompts and settings outside code
3. **Type Safety**: Full type hints throughout
4. **Testability**: Designed for easy mocking and testing
5. **Extensibility**: Clear extension points via abstract methods

## Requirements

- Python 3.10+
- LangGraph >= 0.2.0
- LangChain >= 0.3.0
- python-dotenv >= 1.0.0

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-pattern`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -am 'Add amazing pattern'`)
6. Push to the branch (`git push origin feature/amazing-pattern`)
7. Create a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black agent_patterns tests examples

# Lint code
ruff check agent_patterns tests examples

# Type check
mypy agent_patterns
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on [LangGraph](https://github.com/langchain-ai/langgraph) for state graph management
- Uses [LangChain](https://github.com/langchain-ai/langchain) for LLM integrations
- Inspired by research papers and best practices from the AI agent community

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

## Roadmap

- [ ] Implement remaining 6 patterns
- [ ] Add streaming support
- [ ] Create interactive examples/demos
- [ ] Add more comprehensive documentation
- [ ] Create video tutorials
- [ ] Add pattern composition capabilities
- [ ] Implement tool registry module

---

**Built with ❤️ for the AI agent community**
