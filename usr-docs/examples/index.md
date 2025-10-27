# Examples Index

Complete index of examples demonstrating Agent Patterns usage.

## Quick Links

- [Basic Examples](#basic-examples) - Simple pattern usage
- [Advanced Examples](#advanced-examples) - Complex workflows
- [Customization Examples](#customization-examples) - Prompt customization
- [Integration Examples](#integration-examples) - Real-world integrations
- [Pattern Comparisons](#pattern-comparisons) - Side-by-side comparisons

## Basic Examples

### ReAct Pattern Example

**File**: `examples/react_example.py`

Demonstrates ReAct (Reason + Act) pattern with tool use for question answering.

**Features:**
- Multiple tools (search, calculator)
- Iterative reasoning
- Error handling
- Tool selection logic

**Key Code:**

```python
from agent_patterns.patterns import ReActAgent

def search_tool(query: str) -> str:
    """Simulate web search."""
    return f"Search results for: {query}"

def calculator(expression: str) -> str:
    """Calculate mathematical expressions."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

agent = ReActAgent(
    llm_configs={
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4-turbo"
        }
    },
    tools={"search": search_tool, "calculator": calculator},
    max_iterations=5
)

result = agent.run("What is the population of Tokyo times 3?")
```

**Learn More**: [ReAct Pattern API](../api/patterns.md#react-pattern)

---

### Reflection Pattern Example

**File**: `examples/reflection_example.py`

Shows how to use Reflection pattern for high-quality content generation.

**Features:**
- Generate-reflect-refine cycle
- Multiple LLM roles
- Configurable reflection cycles
- Quality improvement tracking

**Key Code:**

```python
from agent_patterns.patterns import ReflectionAgent

agent = ReflectionAgent(
    llm_configs={
        "documentation": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "reflection": {
            "provider": "openai",
            "model_name": "gpt-4-turbo"
        }
    },
    max_reflection_cycles=2
)

result = agent.run("Write a compelling product description for a smart water bottle")
```

**Learn More**: [Reflection Pattern API](../api/patterns.md#reflection-pattern)

---

## Advanced Examples

### LLM Compiler Pattern Example

**File**: `examples/llm_compiler_example.py`

Demonstrates parallel tool execution using DAG-based planning.

**Features:**
- DAG construction
- Parallel execution
- Dependency management
- Result synthesis

**Key Code:**

```python
from agent_patterns.patterns import LLMCompilerAgent

def weather_tool(location: str) -> str:
    """Get weather for location."""
    return f"Weather in {location}: 72°F, Sunny"

def population_tool(city: str) -> str:
    """Get population data."""
    return f"Population of {city}: ~10 million"

agent = LLMCompilerAgent(
    llm_configs={
        "planning": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "synthesis": {"provider": "openai", "model_name": "gpt-3.5-turbo"}
    },
    tools={
        "weather": weather_tool,
        "population": population_tool,
        "calculator": lambda x: str(eval(x))
    }
)

result = agent.run(
    "What's the weather in Paris and Tokyo? "
    "Also calculate their combined population."
)
```

**Learn More**: [LLM Compiler Pattern API](../api/patterns.md#llm-compiler-pattern)

---

### REWOO Pattern Example

**File**: `examples/rewoo_example.py`

Shows REWOO (Planner-Worker-Solver) pattern for efficient task completion.

**Features:**
- Complete upfront planning
- Worker execution
- Evidence compilation
- Solver synthesis

**Key Code:**

```python
from agent_patterns.patterns import REWOOAgent

def search_wikipedia(query: str) -> str:
    """Search Wikipedia."""
    return f"Wikipedia info on {query}"

def get_facts(topic: str) -> str:
    """Get facts about topic."""
    return f"Facts about {topic}"

agent = REWOOAgent(
    llm_configs={
        "planning": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "worker": {"provider": "openai", "model_name": "gpt-3.5-turbo"},
        "solver": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    tools={"search": search_wikipedia, "facts": get_facts}
)

result = agent.run("Who won the 2023 Nobel Prize in Physics and what was their contribution?")
```

**Learn More**: [REWOO Pattern API](../api/patterns.md#rewoo-pattern)

---

## Customization Examples

### Custom Instructions Example

**File**: `examples/custom_instructions_example.py`

Demonstrates adding domain-specific context to all prompts.

**Features:**
- Domain expertise injection
- Compliance requirements
- Tone/style guidelines
- Audience targeting

**Key Code:**

```python
from agent_patterns.patterns import ReActAgent

# Medical domain instructions
medical_instructions = """
DOMAIN: Medical Information

GUIDELINES:
- Prioritize medical accuracy
- Include appropriate disclaimers
- Use proper medical terminology
- Always recommend consulting healthcare professionals
- Cite sources when possible

CONSTRAINTS:
- Do not provide diagnoses
- Do not recommend specific treatments
- Clarify you are an AI assistant
"""

agent = ReActAgent(
    llm_configs={...},
    tools={...},
    custom_instructions=medical_instructions
)

result = agent.run("What are common symptoms of the flu?")
# Agent will apply medical domain context to all steps
```

**Use Cases:**
- Adding domain expertise (medical, legal, financial)
- Enforcing compliance (HIPAA, GDPR)
- Setting tone/style (formal, casual, technical)
- Specifying audience (beginners, experts)

**Learn More**: [README Customization Section](../../README.md#customizing-prompts)

---

### Prompt Overrides Example

**File**: `examples/prompt_overrides_example.py`

Shows programmatic prompt customization for fine-grained control.

**Features:**
- Complete prompt replacement
- Step-specific customization
- Dynamic prompt generation
- A/B testing support

**Key Code:**

```python
from agent_patterns.patterns import SelfDiscoveryAgent

# Override specific steps
overrides = {
    "DiscoverModules": {
        "system": "You are an expert at selecting reasoning strategies.",
        "user": """
Task: {task}

Available reasoning modules:
{modules}

Select the 3 most relevant modules for this task.
"""
    },
    "SynthesizeOutput": {
        "system": "You synthesize reasoning into clear, actionable answers.",
        "user": """
Original Task: {task}

Reasoning Steps:
{reasoning_steps}

Provide a comprehensive final answer that incorporates all reasoning.
"""
    }
}

agent = SelfDiscoveryAgent(
    llm_configs={...},
    prompt_overrides=overrides
)

result = agent.run("How can we improve urban sustainability?")
```

**Use Cases:**
- A/B testing prompts
- Experimenting with prompt engineering
- Creating specialized variants
- Adjusting for specific use cases

**Learn More**: [README Customization Section](../../README.md#3-prompt-overrides)

---

## Integration Examples

### API Integration

```python
"""Integration with external APIs."""
import requests
from agent_patterns.patterns import ReActAgent

def call_weather_api(location: str) -> str:
    """Call real weather API."""
    response = requests.get(
        f"https://api.weather.com/v1/location/{location}/observations.json",
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )
    data = response.json()
    return f"Temperature: {data['temperature']}°F, Conditions: {data['weather']}"

def call_news_api(query: str) -> str:
    """Call news API."""
    response = requests.get(
        f"https://newsapi.org/v2/everything?q={query}",
        headers={"X-API-Key": "YOUR_API_KEY"}
    )
    articles = response.json()["articles"][:3]
    return "\n".join([f"- {a['title']}" for a in articles])

agent = ReActAgent(
    llm_configs={...},
    tools={
        "weather": call_weather_api,
        "news": call_news_api
    }
)
```

### Database Integration

```python
"""Integration with databases."""
import sqlite3
from agent_patterns.patterns import ReActAgent

def query_database(sql_query: str) -> str:
    """Execute SQL query."""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return str(results)
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

agent = ReActAgent(
    llm_configs={...},
    tools={"database": query_database}
)
```

### File System Integration

```python
"""Integration with file system."""
from pathlib import Path
from agent_patterns.patterns import ReActAgent

def read_file(filepath: str) -> str:
    """Read file contents."""
    try:
        return Path(filepath).read_text()
    except Exception as e:
        return f"Error reading {filepath}: {e}"

def write_file(args: str) -> str:
    """Write to file. Args format: 'filepath|content'"""
    try:
        filepath, content = args.split("|", 1)
        Path(filepath).write_text(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error: {e}"

agent = ReActAgent(
    llm_configs={...},
    tools={
        "read_file": read_file,
        "write_file": write_file
    }
)
```

---

## Pattern Comparisons

### Simple Task: Question Answering

**ReAct Approach:**

```python
# Best for: Questions needing external data
agent = ReActAgent(
    llm_configs={...},
    tools={"search": search_tool}
)
result = agent.run("What is the capital of France?")
```

**Plan & Solve Approach:**

```python
# Best for: Multi-step research questions
agent = PlanAndSolveAgent(llm_configs={...})
result = agent.run(
    "Compare the economies of France and Germany, "
    "including GDP, unemployment, and trade balance"
)
```

### Content Generation

**Reflection Approach:**

```python
# Best for: Single piece of high-quality content
agent = ReflectionAgent(
    llm_configs={...},
    max_reflection_cycles=2
)
result = agent.run("Write a technical blog post about LangGraph")
```

**STORM Approach:**

```python
# Best for: Comprehensive multi-perspective reports
agent = STORMAgent(
    llm_configs={...},
    retrieval_tools={...}
)
result = agent.run("Create a comprehensive report on LangGraph")
```

### Complex Problem Solving

**Self-Discovery Approach:**

```python
# Best for: Novel problems requiring adaptive reasoning
agent = SelfDiscoveryAgent(llm_configs={...})
result = agent.run("Design a new algorithm for traffic optimization")
```

**LATS Approach:**

```python
# Best for: Exploring multiple solution paths
agent = LATSAgent(
    llm_configs={...},
    max_expansions=10
)
result = agent.run("Find the optimal solution for the knapsack problem")
```

---

## Example Categories

### By Complexity

**Beginner:**
- ReAct with simple tools
- Reflection with default settings
- Basic tool integration

**Intermediate:**
- Plan & Solve with multiple roles
- Custom instructions
- Lifecycle hooks
- Error handling

**Advanced:**
- LLM Compiler with DAG
- STORM with perspectives
- Prompt overrides
- Custom pattern creation

### By Use Case

**Research & Analysis:**
- STORM for comprehensive reports
- Plan & Solve for structured analysis
- Self-Discovery for novel problems

**Question Answering:**
- ReAct for tool-based Q&A
- REWOO for efficient retrieval
- Reflexion for learning from errors

**Content Creation:**
- Reflection for quality content
- STORM for multi-perspective writing

**Problem Solving:**
- LATS for exploration
- Self-Discovery for adaptive reasoning
- Reflexion for iterative improvement

---

## Running Examples

### Prerequisites

```bash
# Install dependencies
pip install agent-patterns

# Set up API keys
cp .env.example .env
# Edit .env with your keys
```

### Run an Example

```bash
# From repository root
python examples/react_example.py

# Or specific example
python examples/reflection_example.py
```

### Modify for Your Use Case

1. Copy example file
2. Update tools/functions for your domain
3. Adjust LLM configs
4. Add custom instructions if needed
5. Test and iterate

---

## Additional Resources

- [Quick Start Guide](../quickstart.md) - Get started in 5 minutes
- [Pattern API Reference](../api/patterns.md) - Complete API docs
- [Choosing a Pattern](../patterns/choosing-a-pattern.md) - Decision guide
- [GitHub Examples Directory](https://github.com/osok/agent-patterns/tree/main/examples)

## Contributing Examples

Have a great example? Contribute it!

1. Create example file in `examples/`
2. Add clear comments and docstrings
3. Include usage instructions
4. Submit PR with description
5. Update this index

See [Contributing Guide](../contributing.md) for details.
