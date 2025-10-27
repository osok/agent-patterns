# Quick Start Guide

Get started with Agent Patterns in 5 minutes. This guide walks you through installation, configuration, and running your first agent.

## Prerequisites

- Python 3.10 or higher
- An OpenAI or Anthropic API key

## Installation

Install Agent Patterns via pip:

```bash
pip install agent-patterns
```

## Basic Setup

### 1. Set Up Your API Key

Create a `.env` file in your project directory:

```bash
# .env
OPENAI_API_KEY=your-openai-api-key-here
```

Or set it as an environment variable:

```bash
export OPENAI_API_KEY=your-openai-api-key-here
```

### 2. Your First Agent (30 seconds)

Create a file `hello_agent.py`:

```python
from agent_patterns.patterns import ReActAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the agent
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.7,
    }
}

# Define a simple tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create the agent with tools
agent = ReActAgent(
    llm_configs=llm_configs,
    tools={"calculator": calculator},
    max_iterations=3
)

# Run the agent
result = agent.run("What is 156 * 234?")
print(result)
```

Run it:

```bash
python hello_agent.py
```

Congratulations! You just ran your first agent with the ReAct pattern.

## 5-Minute Tutorial

Let's explore different patterns with progressively more complex examples.

### Example 1: ReAct Pattern (Reason + Act)

The ReAct pattern alternates between reasoning and taking actions. Perfect for tasks requiring tool use.

```python
from agent_patterns.patterns import ReActAgent
from dotenv import load_dotenv

load_dotenv()

# Configure LLM
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.7,
    }
}

# Define tools
def search_wikipedia(query: str) -> str:
    """Simulate Wikipedia search."""
    # In production, use actual Wikipedia API
    knowledge_base = {
        "python": "Python is a high-level programming language created by Guido van Rossum.",
        "langgraph": "LangGraph is a library for building stateful, multi-actor applications with LLMs.",
    }
    return knowledge_base.get(query.lower(), f"No information found for: {query}")

def calculator(expression: str) -> str:
    """Evaluate mathematical expressions."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create agent with multiple tools
agent = ReActAgent(
    llm_configs=llm_configs,
    tools={
        "search_wikipedia": search_wikipedia,
        "calculator": calculator,
    },
    max_iterations=5
)

# Ask a question requiring tool use
result = agent.run("What is Python? Also calculate 2^10.")
print(result)
```

**Key Concepts:**
- Tools are simple Python functions
- Agent decides which tools to use and when
- Iterates until finding the answer or reaching max iterations

### Example 2: Reflection Pattern

The Reflection pattern generates content, critiques it, and refines based on feedback.

```python
from agent_patterns.patterns import ReflectionAgent
from dotenv import load_dotenv

load_dotenv()

# Configure LLMs (can use different models for different roles)
llm_configs = {
    "documentation": {  # Generates content
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
    },
    "reflection": {  # Critiques content
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.5,
    },
}

# Create agent
agent = ReflectionAgent(
    llm_configs=llm_configs,
    max_reflection_cycles=1  # How many times to refine
)

# Generate and refine content
result = agent.run(
    "Write a short product description for a smart water bottle "
    "that tracks hydration and syncs with fitness apps."
)
print(result)
```

**Key Concepts:**
- Two LLM roles: one generates, one critiques
- Automatically refines output based on critique
- Control refinement depth with `max_reflection_cycles`

### Example 3: Plan & Solve Pattern

Plan & Solve separates planning from execution. Great for complex, multi-step tasks.

```python
from agent_patterns.patterns import PlanAndSolveAgent
from dotenv import load_dotenv

load_dotenv()

# Configure LLMs
llm_configs = {
    "planning": {  # Creates the plan
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.5,
    },
    "execution": {  # Executes each step
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.3,
    },
    "documentation": {  # Aggregates results
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
    },
}

# Create agent
agent = PlanAndSolveAgent(llm_configs=llm_configs)

# Solve complex task
result = agent.run(
    "Create a marketing strategy for launching a new AI-powered "
    "mobile app for language learning. Include target audience, "
    "channels, and timeline."
)
print(result)
```

**Key Concepts:**
- Phase 1: Create a detailed plan
- Phase 2: Execute each step sequentially
- Phase 3: Aggregate results into final answer
- Different models for different phases (cost optimization)

## Basic Concepts

### 1. LLM Configuration

Every agent needs LLM configuration specifying the provider and model:

```python
llm_configs = {
    "thinking": {           # Role name (varies by pattern)
        "provider": "openai",      # "openai" or "anthropic"
        "model_name": "gpt-4-turbo",  # Specific model
        "temperature": 0.7,        # Optional: creativity (0-1)
        "max_tokens": 2000,        # Optional: max response length
    }
}
```

### 2. Common LLM Roles

Different patterns use different roles:

| Role | Purpose | Typical Model |
|------|---------|---------------|
| `thinking` | Primary reasoning | GPT-4, Claude 3.5 Sonnet |
| `reflection` | Self-critique | GPT-4, Claude 3.5 Sonnet |
| `documentation` | Output generation | GPT-3.5, Claude 3 Haiku |
| `planning` | Task decomposition | GPT-4, Claude 3.5 Sonnet |
| `execution` | Step execution | GPT-3.5, Claude 3 Haiku |

### 3. Tool Functions

Tools are simple Python functions:

```python
def my_tool(input: str) -> str:
    """Tool description (helps the agent understand what it does)."""
    # Your logic here
    return result
```

**Tool Guidelines:**
- Take string input (or simple types)
- Return string output
- Include clear docstring
- Handle errors gracefully

### 4. Pattern Selection

Choose based on your task:

| Pattern | Best For | Example Use Case |
|---------|----------|------------------|
| **ReAct** | Tool-based reasoning | Q&A with web search |
| **Reflection** | High-quality content | Writing, coding, design |
| **Plan & Solve** | Multi-step tasks | Research reports, analysis |
| **Reflexion** | Learning from failures | Complex problem-solving |
| **LLM Compiler** | Parallel tool execution | Multi-source data gathering |
| **REWOO** | Cost-efficient workflows | Large-scale batch processing |
| **LATS** | Exploring solutions | Creative tasks, optimization |
| **Self-Discovery** | Adaptive reasoning | Novel problems |
| **STORM** | Multi-perspective research | Comprehensive reports |

See [Choosing a Pattern](patterns/choosing-a-pattern.md) for detailed guidance.

## Common Patterns

### Environment Variables

Use `.env` file for configuration:

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Model defaults
THINKING_MODEL_PROVIDER=openai
THINKING_MODEL_NAME=gpt-4-turbo
THINKING_TEMPERATURE=0.7
```

Load in Python:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
```

### Multiple Providers

Mix OpenAI and Anthropic:

```python
llm_configs = {
    "thinking": {
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-20241022",
    },
    "documentation": {
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
    },
}
```

### Error Handling

```python
try:
    result = agent.run(query)
    print(f"Success: {result}")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Runtime error: {e}")
```

### Lifecycle Hooks

Override lifecycle methods for logging:

```python
class MyReActAgent(ReActAgent):
    def on_start(self, input_data):
        print(f"Starting: {input_data}")

    def on_finish(self, result):
        print(f"Finished: {result}")

    def on_error(self, error):
        print(f"Error occurred: {error}")
```

## Project Structure

Organize your agent project:

```
my_agent_project/
├── .env                 # API keys (gitignore this!)
├── .env.example         # Template for others
├── requirements.txt     # Dependencies
├── agents/
│   ├── __init__.py
│   ├── react_agent.py   # Your ReAct agent
│   └── reflection_agent.py
├── tools/
│   ├── __init__.py
│   ├── search.py        # Search tool
│   └── calculator.py    # Calculator tool
└── main.py             # Entry point
```

Example `requirements.txt`:

```
agent-patterns>=0.2.0
python-dotenv>=1.0.0
```

## Next Steps

Now that you're familiar with basics:

1. **Deep Dive**: Read [What Are Patterns?](concepts/what-are-patterns.md) to understand the theory
2. **Architecture**: Learn [how patterns work internally](concepts/architecture.md)
3. **API Reference**: Explore the complete [Pattern API](api/patterns.md)
4. **Examples**: Study [real-world examples](examples/index.md)
5. **Customize**: Learn about [prompt customization](../README.md#customizing-prompts)

## Complete Example: Task Manager Bot

Here's a complete working example combining multiple concepts:

```python
#!/usr/bin/env python3
"""Task Manager Bot using ReAct pattern."""

from agent_patterns.patterns import ReActAgent
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment
load_dotenv()

# Simple in-memory task storage
TASKS = []

# Tool definitions
def add_task(task_description: str) -> str:
    """Add a new task to the task list."""
    task_id = len(TASKS) + 1
    task = {"id": task_id, "description": task_description, "completed": False}
    TASKS.append(task)
    return f"Added task #{task_id}: {task_description}"

def list_tasks(filter_type: str = "all") -> str:
    """List tasks. Filter: 'all', 'completed', 'pending'."""
    if not TASKS:
        return "No tasks found."

    if filter_type == "completed":
        tasks = [t for t in TASKS if t["completed"]]
    elif filter_type == "pending":
        tasks = [t for t in TASKS if not t["completed"]]
    else:
        tasks = TASKS

    if not tasks:
        return f"No {filter_type} tasks found."

    result = [f"Task #{t['id']}: {t['description']} [{'✓' if t['completed'] else '✗'}]"
              for t in tasks]
    return "\n".join(result)

def complete_task(task_id: str) -> str:
    """Mark a task as completed."""
    try:
        tid = int(task_id)
        for task in TASKS:
            if task["id"] == tid:
                task["completed"] = True
                return f"Task #{tid} marked as completed!"
        return f"Task #{tid} not found."
    except ValueError:
        return "Invalid task ID. Please provide a number."

# Configure agent
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.3,  # Lower temperature for precise task management
    }
}

# Create agent
agent = ReActAgent(
    llm_configs=llm_configs,
    tools={
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
    },
    max_iterations=5
)

# Interactive loop
def main():
    print("Task Manager Bot - Type 'quit' to exit")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            result = agent.run(user_input)
            print(f"\nBot: {result}")
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
```

Save as `task_manager.py` and run:

```bash
python task_manager.py
```

Example interaction:

```
You: Add a task to review the documentation
Bot: I've added the task "review the documentation" to your task list.

You: Add another task to write unit tests
Bot: I've added the task "write unit tests" to your task list.

You: Show me all my tasks
Bot: Here are your tasks:
Task #1: review the documentation [✗]
Task #2: write unit tests [✗]

You: Mark task 1 as done
Bot: Task #1 has been marked as completed!
```

## Tips for Success

1. **Start Simple**: Begin with ReAct or Reflection patterns
2. **Good Prompts**: Clear, specific queries get better results
3. **Tool Design**: Keep tools focused and well-documented
4. **Error Handling**: Always handle exceptions gracefully
5. **Iterate**: Adjust temperature and max_iterations based on results
6. **Cost Management**: Use cheaper models for simple roles
7. **Test Thoroughly**: Test with various inputs and edge cases

## Getting Help

- **Documentation**: Continue reading the [user docs](index.md)
- **Examples**: Check the [examples directory](examples/index.md)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/osok/agent-patterns/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/osok/agent-patterns/discussions)

## What's Next?

- [Learn about agent patterns and why they matter](concepts/what-are-patterns.md)
- [Understand the library architecture](concepts/architecture.md)
- [Explore all 9 available patterns](api/patterns.md)
- [Customize prompts for your domain](../README.md#customizing-prompts)
- [Choose the right pattern for your task](patterns/choosing-a-pattern.md)
