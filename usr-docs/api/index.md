# API Reference

Complete API reference for the Agent Patterns library.

## Overview

The Agent Patterns library is organized into three main modules:

- **`agent_patterns.core`** - Base classes and core infrastructure
- **`agent_patterns.patterns`** - All 9 agent pattern implementations
- **`agent_patterns.prompts`** - Prompt templates for each pattern

## Quick Links

- [BaseAgent](base-agent.md) - Abstract base class for all patterns
- [Pattern APIs](patterns.md) - Complete reference for all 9 patterns
- [Type Definitions](types.md) - Type hints and data structures

## Import Structure

```python
# Import specific patterns
from agent_patterns.patterns import (
    ReActAgent,
    ReflectionAgent,
    SelfDiscoveryAgent,
    STORMAgent,
    PlanAndSolveAgent,
    ReflexionAgent,
    REWOOAgent,
    LATSAgent,
    LLMCompilerAgent
)

# Import base classes (for extending)
from agent_patterns.core import BaseAgent, MultiAgentBase
```

## Common Patterns

### Basic Usage

```python
from agent_patterns.patterns import ReflectionAgent

# Configure LLM
llm_configs = {
    "documentation": {"provider": "openai", "model": "gpt-4"},
    "reflection": {"provider": "openai", "model": "gpt-4"}
}

# Create agent
agent = ReflectionAgent(llm_configs=llm_configs)

# Run
result = agent.run("Your task here")
```

### With Customization

```python
agent = ReflectionAgent(
    llm_configs=llm_configs,
    max_reflection_cycles=2,
    custom_instructions="Domain-specific guidelines",
    prompt_overrides={"Generate": {"system": "...", "user": "..."}}
)
```

## Core Classes

### BaseAgent

Abstract base class for all agent patterns.

```python
class BaseAgent(ABC):
    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    )

    @abstractmethod
    def build_graph(self) -> None:
        """Build the LangGraph state graph"""

    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """Execute the pattern"""
```

**See**: [BaseAgent Documentation](base-agent.md)

### Pattern Classes

All pattern classes inherit from `BaseAgent` and implement the same interface:

| Class | LLM Roles | Key Parameters |
|-------|-----------|----------------|
| [ReActAgent](patterns.md#reactagent) | `thinking` | `tools`, `max_iterations` |
| [ReflectionAgent](patterns.md#reflectionagent) | `documentation`, `reflection` | `max_reflection_cycles` |
| [SelfDiscoveryAgent](patterns.md#selfdiscoveryagent) | `thinking`, `execution` | `reasoning_modules`, `max_selected_modules` |
| [STORMAgent](patterns.md#stormagent) | `thinking`, `documentation` | `retrieval_tools`, `perspectives` |
| [PlanAndSolveAgent](patterns.md#planandsolveagent) | `planning`, `execution`, `documentation` | None |
| [ReflexionAgent](patterns.md#reflexionagent) | `execution`, `reflection` | `max_trials` |
| [REWOOAgent](patterns.md#rewooagent) | `planning`, `execution` | `tools` |
| [LATSAgent](patterns.md#latsagent) | `thinking`, `evaluation` | `max_iterations`, `num_candidates` |
| [LLMCompilerAgent](patterns.md#llmcompileragent) | `planning`, `execution`, `synthesis` | `tools` |

**See**: [Pattern APIs](patterns.md)

## Type Definitions

### LLM Configuration

```python
from typing import Dict, Any

LLMConfig = Dict[str, Any]
# Example:
{
    "provider": "openai",  # or "anthropic"
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "api_key": "...",  # optional, reads from env
}

LLMConfigs = Dict[str, LLMConfig]
# Example:
{
    "thinking": {"provider": "openai", "model": "gpt-4"},
    "execution": {"provider": "openai", "model": "gpt-3.5-turbo"}
}
```

### Prompt Overrides

```python
from typing import Dict, Optional

PromptOverrides = Optional[Dict[str, Dict[str, str]]]
# Example:
{
    "StepName": {
        "system": "System prompt content",
        "user": "User prompt template with {placeholders}"
    }
}
```

### Tool Definition

```python
from typing import Callable

Tool = Callable[[str], str]
# Tools must:
# - Take string parameters
# - Return string results
# - Have clear docstrings

Tools = Dict[str, Tool]
```

**See**: [Type Definitions](types.md)

## Common Parameters

All patterns support these parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configuration for each role |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict[str, Dict[str, str]]` | No | Override specific prompts |

## LLM Providers

### OpenAI

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-4",  # or gpt-3.5-turbo, gpt-4-turbo, etc.
    "temperature": 0.7,
    "max_tokens": 2000,
    "api_key": "sk-...",  # optional, defaults to OPENAI_API_KEY env var
}
```

### Anthropic

```python
llm_config = {
    "provider": "anthropic",
    "model": "claude-3-opus-20240229",  # or claude-3-sonnet, etc.
    "temperature": 0.7,
    "max_tokens": 2000,
    "api_key": "sk-ant-...",  # optional, defaults to ANTHROPIC_API_KEY env var
}
```

## Error Handling

All patterns may raise:

- `ValueError` - Invalid configuration or parameters
- `RuntimeError` - Execution errors
- Provider-specific exceptions (OpenAI, Anthropic)

```python
from agent_patterns.patterns import ReflectionAgent

try:
    agent = ReflectionAgent(llm_configs=llm_configs)
    result = agent.run("task")
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"Execution error: {e}")
```

## Lifecycle Hooks

BaseAgent provides lifecycle hooks for monitoring:

```python
class CustomAgent(BaseAgent):
    def on_start(self, input_data: Any) -> None:
        """Called before execution starts"""
        print(f"Starting with: {input_data}")

    def on_finish(self, result: Any) -> None:
        """Called after successful completion"""
        print(f"Finished with: {result}")

    def on_error(self, error: Exception) -> None:
        """Called when an error occurs"""
        print(f"Error: {error}")
```

## Advanced Usage

### Custom Pattern Creation

```python
from agent_patterns.core import BaseAgent
from langgraph.graph import StateGraph, END

class MyCustomAgent(BaseAgent):
    def build_graph(self) -> None:
        workflow = StateGraph(dict)
        # Build your graph
        self.graph = workflow.compile()

    def run(self, input_data: str) -> str:
        if self.graph is None:
            raise ValueError("Graph not built")
        result = self.graph.invoke({"input": input_data})
        return result.get("output")
```

**See**: [Extending Patterns Guide](../guides/extending-patterns.md)

### Pattern Composition

```python
# Sequential composition
storm_agent = STORMAgent(...)
reflection_agent = ReflectionAgent(...)

research = storm_agent.run("Topic")
polished = reflection_agent.run(f"Polish this: {research}")
```

**See**: [Best Practices Guide](../guides/best-practices.md)

## Next Steps

- [BaseAgent API](base-agent.md) - Detailed base class documentation
- [Pattern APIs](patterns.md) - All pattern class references
- [Type Definitions](types.md) - Type hints and structures
- [Configuration Guide](../guides/configuration.md) - LLM setup
- [Extending Patterns](../guides/extending-patterns.md) - Create custom patterns
