# Configuration Guide

Complete guide to configuring LLMs, models, providers, and pattern-specific parameters for Agent Patterns.

## Overview

Agent Patterns provides flexible configuration for:
- **LLM Providers**: OpenAI, Anthropic, and others
- **Model Selection**: Choose models per role
- **Model Parameters**: Temperature, tokens, etc.
- **Pattern Parameters**: Pattern-specific settings
- **Environment Variables**: Centralized configuration

## LLM Configuration Structure

### Basic Structure

```python
llm_configs = {
    "role_name": {
        "provider": "openai",  # or "anthropic"
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000
    }
}
```

### Multi-Role Configuration

Different patterns use different roles:

```python
from agent_patterns.patterns import ReflectionAgent

llm_configs = {
    "documentation": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper model for generation
        "temperature": 0.8,  # Higher temp for creativity
        "max_tokens": 2000
    },
    "reflection": {
        "provider": "openai",
        "model": "gpt-4",  # Smarter model for critique
        "temperature": 0.3,  # Lower temp for focused analysis
        "max_tokens": 1500
    }
}

agent = ReflectionAgent(llm_configs=llm_configs)
```

## Provider Configuration

### OpenAI

```python
openai_config = {
    "provider": "openai",
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 2000,
    # Optional parameters
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

**Recommended Models**:
- **gpt-4-turbo**: Best quality, most expensive
- **gpt-4**: High quality, expensive
- **gpt-3.5-turbo**: Good quality, affordable
- **gpt-3.5-turbo-16k**: Longer context, affordable

### Anthropic

```python
anthropic_config = {
    "provider": "anthropic",
    "model": "claude-3-opus-20240229",
    "temperature": 0.7,
    "max_tokens": 2000
}
```

**Recommended Models**:
- **claude-3-opus**: Highest intelligence
- **claude-3-sonnet**: Balanced performance/cost
- **claude-3-haiku**: Fast, affordable

### Mixed Providers

```python
mixed_configs = {
    "thinking": {
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "temperature": 0.5
    },
    "execution": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
}
```

## Model Parameters

### Temperature

Controls randomness/creativity:

```python
# Low temperature (0.0-0.3): Focused, deterministic
# Good for: Analysis, factual tasks, code generation
config_focused = {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.2
}

# Medium temperature (0.4-0.7): Balanced
# Good for: General tasks, Q&A
config_balanced = {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7
}

# High temperature (0.8-1.0): Creative, diverse
# Good for: Creative writing, brainstorming
config_creative = {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.9
}
```

### Max Tokens

Controls output length:

```python
# Short responses
config_brief = {
    "provider": "openai",
    "model": "gpt-4",
    "max_tokens": 500
}

# Standard responses
config_standard = {
    "provider": "openai",
    "model": "gpt-4",
    "max_tokens": 2000
}

# Long responses
config_long = {
    "provider": "openai",
    "model": "gpt-4",
    "max_tokens": 4000
}
```

## Role-Based Configuration

### Role Purposes by Pattern

**ReActAgent**:
```python
react_configs = {
    "thinking": {  # For reasoning and tool selection
        "provider": "openai",
        "model": "gpt-4",  # Use smart model
        "temperature": 0.5  # Focused reasoning
    }
}
```

**ReflectionAgent**:
```python
reflection_configs = {
    "documentation": {  # For generating content
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Can use cheaper model
        "temperature": 0.8  # Creative generation
    },
    "reflection": {  # For critique
        "provider": "openai",
        "model": "gpt-4",  # Use smart model
        "temperature": 0.3  # Focused critique
    }
}
```

**SelfDiscoveryAgent**:
```python
discovery_configs = {
    "thinking": {  # For strategy selection and planning
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.5
    },
    "execution": {  # For executing steps
        "provider": "openai",
        "model": "gpt-4",  # Keep quality high
        "temperature": 0.6
    }
}
```

**PlanAndSolveAgent**:
```python
plan_solve_configs = {
    "planning": {  # For creating plans
        "provider": "openai",
        "model": "gpt-4",  # Smart planning
        "temperature": 0.4  # Focused planning
    },
    "execution": {  # For executing steps
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Can be cheaper
        "temperature": 0.7
    },
    "documentation": {  # For final output
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
}
```

**ReflexionAgent**:
```python
reflexion_configs = {
    "execution": {  # For attempting solutions
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7
    },
    "reflection": {  # For learning from failures
        "provider": "openai",
        "model": "gpt-4",  # Keep smart
        "temperature": 0.3  # Focused reflection
    }
}
```

## Pattern-Specific Parameters

### ReAct

```python
from agent_patterns.patterns import ReActAgent

agent = ReActAgent(
    llm_configs=configs,
    tools=tools,
    max_iterations=5,  # Max reasoning cycles
    prompt_dir="prompts",
    custom_instructions=None,
    prompt_overrides=None
)
```

### Reflection

```python
from agent_patterns.patterns import ReflectionAgent

agent = ReflectionAgent(
    llm_configs=configs,
    max_reflection_cycles=2,  # How many refine cycles
    prompt_dir="prompts",
    custom_instructions=None,
    prompt_overrides=None
)
```

### Self-Discovery

```python
from agent_patterns.patterns import SelfDiscoveryAgent

agent = SelfDiscoveryAgent(
    llm_configs=configs,
    reasoning_modules=None,  # Use custom modules
    max_selected_modules=3,  # How many strategies
    prompt_dir="prompts",
    custom_instructions=None,
    prompt_overrides=None
)
```

### REWOO

```python
from agent_patterns.patterns import REWOOAgent

agent = REWOOAgent(
    llm_configs=configs,
    tools=tools,
    prompt_dir="prompts",
    custom_instructions=None,
    prompt_overrides=None
)
```

### Reflexion

```python
from agent_patterns.patterns import ReflexionAgent

agent = ReflexionAgent(
    llm_configs=configs,
    max_trials=3,  # Max retry attempts
    prompt_dir="prompts",
    custom_instructions=None,
    prompt_overrides=None
)
```

## Environment Variables

### Setup

Create `.env` file:

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Default Models
THINKING_MODEL_PROVIDER=openai
THINKING_MODEL_NAME=gpt-4
THINKING_TEMPERATURE=0.7
THINKING_MAX_TOKENS=2000

DOCUMENTATION_MODEL_PROVIDER=openai
DOCUMENTATION_MODEL_NAME=gpt-3.5-turbo
DOCUMENTATION_TEMPERATURE=0.7

# Pattern Defaults
MAX_ITERATIONS=5
MAX_REFLECTION_CYCLES=2
MAX_TRIALS=3
```

### Loading Environment

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Build configs from environment
llm_configs = {
    "thinking": {
        "provider": os.getenv("THINKING_MODEL_PROVIDER", "openai"),
        "model": os.getenv("THINKING_MODEL_NAME", "gpt-4"),
        "temperature": float(os.getenv("THINKING_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("THINKING_MAX_TOKENS", "2000"))
    }
}

# Pattern parameters
max_iterations = int(os.getenv("MAX_ITERATIONS", "5"))
```

## Cost Optimization

### Strategy 1: Use Cheaper Models for Simple Steps

```python
cost_optimized_configs = {
    "planning": {
        "provider": "openai",
        "model": "gpt-4",  # Smart planning
        "temperature": 0.5
    },
    "execution": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper execution
        "temperature": 0.7
    },
    "documentation": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper writing
        "temperature": 0.7
    }
}
```

### Strategy 2: Reduce Max Tokens

```python
token_optimized = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4",
        "max_tokens": 1000  # Reduced from 2000
    }
}
```

### Strategy 3: Limit Iterations/Cycles

```python
# Limit ReAct iterations
agent = ReActAgent(llm_configs=configs, tools=tools, max_iterations=3)

# Limit Reflection cycles
agent = ReflectionAgent(llm_configs=configs, max_reflection_cycles=1)
```

### Strategy 4: Use REWOO for Tool-Heavy Tasks

REWOO pattern plans all tool calls upfront, avoiding iterative LLM calls.

## Performance Optimization

### Faster Models

```python
fast_configs = {
    "thinking": {
        "provider": "anthropic",
        "model": "claude-3-haiku-20240307",  # Fastest
        "temperature": 0.7
    }
}
```

### Parallel Execution

Some patterns (like LLM Compiler) support parallel execution:

```python
from agent_patterns.patterns import LLMCompilerAgent

agent = LLMCompilerAgent(
    llm_configs=configs,
    tools=tools,
    # Will execute independent tool calls in parallel
)
```

## Quality Optimization

### Use Best Models

```python
quality_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4-turbo",  # Best OpenAI model
        "temperature": 0.5
    },
    "reflection": {
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",  # Best Anthropic model
        "temperature": 0.3
    }
}
```

### Increase Iterations/Cycles

```python
# More thorough reflection
agent = ReflectionAgent(
    llm_configs=configs,
    max_reflection_cycles=3  # More refinement
)

# More retry attempts
agent = ReflexionAgent(
    llm_configs=configs,
    max_trials=5  # More learning attempts
)
```

## Configuration Profiles

### Development Profile

```python
dev_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheap, fast
        "temperature": 0.7,
        "max_tokens": 1000
    }
}

dev_agent = ReActAgent(
    llm_configs=dev_configs,
    tools=tools,
    max_iterations=3  # Fewer iterations
)
```

### Production Profile

```python
prod_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4",  # High quality
        "temperature": 0.7,
        "max_tokens": 2000
    }
}

prod_agent = ReActAgent(
    llm_configs=prod_configs,
    tools=tools,
    max_iterations=5
)
```

### Testing Profile

```python
test_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.0,  # Deterministic for testing
        "max_tokens": 500
    }
}
```

## Configuration Best Practices

### 1. Use Environment Variables for Secrets

```python
# Never hardcode API keys
❌ config = {"provider": "openai", "api_key": "sk-..."}

# Use environment variables
✅ load_dotenv()
✅ config = {"provider": "openai"}  # API key from OPENAI_API_KEY env var
```

### 2. Match Model Capability to Task Complexity

```python
# Simple tasks: cheaper models
simple_configs = {"thinking": {"provider": "openai", "model": "gpt-3.5-turbo"}}

# Complex tasks: smarter models
complex_configs = {"thinking": {"provider": "openai", "model": "gpt-4"}}
```

### 3. Adjust Temperature by Use Case

```python
# Factual/analytical: low temperature
analytical_config = {"temperature": 0.2}

# Creative/diverse: high temperature
creative_config = {"temperature": 0.9}
```

### 4. Set Appropriate Token Limits

```python
# Brief answers
brief_config = {"max_tokens": 500}

# Detailed analysis
detailed_config = {"max_tokens": 3000}
```

### 5. Version Your Configurations

```python
# configs_v1.py
V1_CONFIGS = {
    "thinking": {"provider": "openai", "model": "gpt-3.5-turbo"}
}

# configs_v2.py
V2_CONFIGS = {
    "thinking": {"provider": "openai", "model": "gpt-4"}
}
```

## Troubleshooting

### Issue: Rate Limiting

**Solution**: Add retry logic or reduce concurrency

```python
import time
from openai import RateLimitError

def create_agent_with_retry():
    max_retries = 3
    for i in range(max_retries):
        try:
            return ReActAgent(llm_configs=configs, tools=tools)
        except RateLimitError:
            if i < max_retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                raise
```

### Issue: High Costs

**Solutions**:
1. Use cheaper models where possible
2. Reduce max_tokens
3. Limit iterations/cycles
4. Use REWOO pattern for tool-heavy workflows

### Issue: Poor Quality

**Solutions**:
1. Use smarter models (gpt-4, claude-3-opus)
2. Increase reflection cycles
3. Lower temperature for focused tasks
4. Add better custom instructions

### Issue: Slow Performance

**Solutions**:
1. Use faster models (gpt-3.5-turbo, claude-haiku)
2. Reduce max_tokens
3. Limit iterations
4. Use patterns with parallel execution (LLM Compiler)

## Next Steps

- Review [Error Handling](error-handling.md) for robust configuration
- See [Deployment Guide](deployment.md) for production configs
- Explore [Best Practices](best-practices.md) for optimization
- Check individual pattern docs for pattern-specific configs

## Reference

### Model Comparison

| Model | Provider | Quality | Speed | Cost | Best For |
|-------|----------|---------|-------|------|----------|
| gpt-4-turbo | OpenAI | Excellent | Medium | High | Complex reasoning |
| gpt-4 | OpenAI | Excellent | Slow | High | High-quality output |
| gpt-3.5-turbo | OpenAI | Good | Fast | Low | General tasks |
| claude-3-opus | Anthropic | Excellent | Medium | High | Complex reasoning |
| claude-3-sonnet | Anthropic | Very Good | Fast | Medium | Balanced tasks |
| claude-3-haiku | Anthropic | Good | Very Fast | Low | Simple tasks |

### Configuration Parameters Reference

**LLM Config Parameters**:
- `provider`: "openai" or "anthropic"
- `model`: Model name/ID
- `temperature`: 0.0-1.0 (default: 0.7)
- `max_tokens`: Integer (default: 2000)
- `top_p`: 0.0-1.0 (optional)
- `frequency_penalty`: -2.0-2.0 (optional, OpenAI)
- `presence_penalty`: -2.0-2.0 (optional, OpenAI)

**Pattern Parameters**:
- ReAct: `max_iterations`
- Reflection: `max_reflection_cycles`
- Self-Discovery: `max_selected_modules`, `reasoning_modules`
- Reflexion: `max_trials`
- All patterns: `prompt_dir`, `custom_instructions`, `prompt_overrides`
