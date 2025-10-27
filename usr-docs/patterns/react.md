# ReAct Agent Pattern

The **ReAct** (Reasoning + Acting) pattern combines reasoning with action execution, allowing agents to interact with external tools and APIs while maintaining a clear thought process.

## Overview

**Best For**: Tasks requiring external tool use, API interaction, and dynamic decision-making

**Complexity**: ⭐ Simple (Great for beginners)

**Cost**: $$ Medium (Iterative LLM calls)

## When to Use ReAct

### Ideal Use Cases

✅ **Question answering with web search**
- Agent reasons about what to search
- Executes search queries
- Synthesizes results into answers

✅ **API orchestration**
- Determines which APIs to call
- Makes API requests based on responses
- Adapts strategy based on results

✅ **Data gathering tasks**
- Decides what data to collect
- Uses tools to retrieve data
- Continues until sufficient information gathered

✅ **Interactive workflows**
- Reasons about next steps
- Executes actions
- Adjusts based on outcomes

### When NOT to Use ReAct

❌ **Pure reasoning tasks** → Use Self-Discovery or Reflection
❌ **Predetermined workflows** → Use Plan & Solve
❌ **Cost-sensitive tool usage** → Use REWOO
❌ **Tasks requiring learning from failures** → Use Reflexion

## How ReAct Works

### The Reasoning-Action Cycle

```
┌─────────────────────────────────────────┐
│                                         │
│  1. THOUGHT: What should I do next?    │
│     "I need to search for information   │
│      about quantum computing"           │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  2. ACTION: Execute the decision        │
│     search("quantum computing basics")  │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  3. OBSERVATION: Process result         │
│     "Found 10 articles about quantum    │
│      computing fundamentals..."         │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
              [Repeat until task complete]
```

### Theoretical Foundation

ReAct is based on the paper "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al., 2022). The key insight is that interleaving reasoning traces with actions:

1. **Improves interpretability**: Explicit reasoning makes decisions transparent
2. **Enables dynamic planning**: Can adjust strategy based on observations
3. **Reduces hallucination**: Grounds reasoning in actual observations
4. **Supports error recovery**: Can detect and correct mistakes

### Algorithm

```python
def react_loop(task, tools, max_iterations=5):
    """Simplified ReAct algorithm"""
    context = []

    for i in range(max_iterations):
        # 1. Reasoning step
        thought = llm.generate_thought(task, context)

        # 2. Decide on action
        action, action_input = llm.decide_action(thought, tools)

        # 3. Execute action
        if action == "FINISH":
            return generate_final_answer(context)

        observation = execute_tool(action, action_input)

        # 4. Update context
        context.append({
            "thought": thought,
            "action": action,
            "observation": observation
        })

    return generate_final_answer(context)
```

## API Reference

### Class: `ReActAgent`

```python
from agent_patterns.patterns import ReActAgent

agent = ReActAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    tools: Dict[str, Callable],
    max_iterations: int = 5,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configuration for "thinking" role |
| `tools` | `Dict[str, Callable]` | Yes | Dictionary mapping tool names to functions |
| `max_iterations` | `int` | No | Maximum reasoning-action cycles (default: 5) |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict` | No | Override specific prompts programmatically |

#### LLM Roles

- **thinking**: Used for reasoning, action selection, and answer generation

#### Methods

**`run(input_data: str) -> str`**

Executes the ReAct pattern on the given input.

- **Parameters**:
  - `input_data` (str): The task or question to solve
- **Returns**: str - The final answer
- **Raises**: ValueError if graph not built

**`build_graph() -> None`**

Builds the LangGraph state graph. Called automatically during initialization.

## Complete Example

### Basic Usage

```python
from agent_patterns.patterns import ReActAgent
import requests

# Define tools
def search_web(query: str) -> str:
    """Search the web for information"""
    # Simplified - use actual search API in production
    response = requests.get(f"https://api.search.com/search?q={query}")
    return response.json()["results"]

def get_weather(location: str) -> str:
    """Get current weather for a location"""
    response = requests.get(f"https://api.weather.com/current?loc={location}")
    return f"Weather in {location}: {response.json()['condition']}"

def calculate(expression: str) -> str:
    """Evaluate a mathematical expression"""
    try:
        result = eval(expression)  # Use safe_eval in production!
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# Configure LLM
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
    }
}

# Create agent with tools
tools = {
    "search": search_web,
    "weather": get_weather,
    "calculate": calculate,
}

agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    max_iterations=5
)

# Run agent
result = agent.run("What is the weather in the capital of France?")
print(result)
# Expected: Agent searches for "capital of France", gets "Paris",
#           then calls weather("Paris") to get the weather
```

### With Custom Instructions

```python
# Add domain-specific guidance
customer_support_instructions = """
You are a customer support agent. Follow these guidelines:
- Be polite and empathetic
- Gather all necessary information before taking action
- Confirm actions with the user when possible
- Provide clear explanations of what you're doing
"""

agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    custom_instructions=customer_support_instructions
)

result = agent.run("I need to cancel my order #12345")
```

### With Prompt Overrides

```python
# Customize the thought process
overrides = {
    "ThoughtStep": {
        "system": "You are a methodical problem solver. Think step-by-step.",
        "user": """Task: {input}

Previous steps: {history}

Think carefully about what to do next. Consider:
1. What information do I need?
2. Which tool is most appropriate?
3. How will this help solve the task?

Your thought:"""
    }
}

agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    prompt_overrides=overrides
)
```

## Tool Definition Guidelines

### Tool Function Signature

```python
def tool_name(param1: str, param2: int = 0) -> str:
    """
    Clear description of what the tool does.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (optional)

    Returns:
        A string description of the result
    """
    # Tool implementation
    return result_string
```

### Tool Best Practices

1. **Return strings**: Always return string results for consistency
2. **Handle errors gracefully**: Return error messages as strings
3. **Be descriptive**: Clear docstrings help the LLM use tools correctly
4. **Keep it focused**: Each tool should do one thing well
5. **Validate inputs**: Check parameters before execution

### Example Tools

```python
def read_file(filepath: str) -> str:
    """Read contents of a file"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Write content to a file"""
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to '{filepath}'"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_directory(path: str = ".") -> str:
    """List contents of a directory"""
    import os
    try:
        files = os.listdir(path)
        return "\\n".join(files)
    except Exception as e:
        return f"Error listing directory: {str(e)}"
```

## Customizing Prompts

### Understanding ReAct Prompts

ReAct uses the following prompt structure:

**ThoughtStep/system.md**: System prompt for reasoning
- Sets the agent's role and capabilities
- Lists available tools and their descriptions
- Defines output format

**ThoughtStep/user.md**: User prompt for each iteration
- Current task
- History of previous thoughts and observations
- Prompt to generate next thought and action

### Method 1: Custom Instructions

Add guidelines without changing core prompts:

```python
agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    custom_instructions="""
    When searching, always verify information from multiple sources.
    If a tool returns an error, try an alternative approach.
    Be concise in your final answer.
    """
)
```

### Method 2: Prompt Overrides

Replace prompts entirely:

```python
overrides = {
    "ThoughtStep": {
        "system": """You are a research assistant with access to these tools:
{tool_descriptions}

Format your response as:
Thought: [your reasoning]
Action: [tool_name]
Action Input: [tool parameters]

When done, use Action: FINISH with your final answer.""",
        "user": """Task: {input}

History:
{history}

What's your next step?"""
    }
}

agent = ReActAgent(llm_configs=llm_configs, tools=tools, prompt_overrides=overrides)
```

### Method 3: Custom Prompt Directory

For extensive customization:

```bash
my_prompts/
└── ReActAgent/
    └── ThoughtStep/
        ├── system.md
        └── user.md
```

```python
agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    prompt_dir="my_prompts"
)
```

## Setting Agent Goals

### Via Task Description

The clearest way to set goals is through the task description:

```python
# Specific goal
agent.run("Find the current stock price of AAPL and calculate 5% of that value")

# Multi-part goal
agent.run("""
1. Search for the population of Tokyo
2. Search for the population of London
3. Calculate which is larger and by how much
""")
```

### Via Custom Instructions

Set persistent goals across all tasks:

```python
agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    custom_instructions="""
    GOAL: Provide accurate, well-researched answers with citations.

    CONSTRAINTS:
    - Always cite sources for factual claims
    - Verify information from multiple sources when possible
    - Acknowledge uncertainty rather than guessing
    """
)
```

### Via System Prompt Override

Set goals at the system level:

```python
overrides = {
    "ThoughtStep": {
        "system": """You are a fact-checking agent. Your goal is to verify claims using available tools.

For each claim:
1. Search for supporting evidence
2. Search for contradicting evidence
3. Evaluate credibility of sources
4. Provide a confidence level

Available tools:
{tool_descriptions}"""
    }
}
```

## Advanced Usage

### Limiting Iterations

```python
# Quick tasks
agent = ReActAgent(llm_configs=llm_configs, tools=tools, max_iterations=3)

# Complex tasks
agent = ReActAgent(llm_configs=llm_configs, tools=tools, max_iterations=10)
```

### Tool Access Control

Provide different tools for different tasks:

```python
# Read-only tools for analysis
analysis_tools = {"search": search_web, "calculate": calculate}
analysis_agent = ReActAgent(llm_configs=llm_configs, tools=analysis_tools)

# Full access for automation
full_tools = {**analysis_tools, "write_file": write_file, "send_email": send_email}
automation_agent = ReActAgent(llm_configs=llm_configs, tools=full_tools)
```

### Error Handling

```python
try:
    result = agent.run("Find information about XYZ")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Runtime error: {e}")
```

## Performance Considerations

### Cost Optimization

ReAct makes iterative LLM calls, so costs can add up:

```python
# Use cheaper model for routine tasks
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper than gpt-4
        "temperature": 0.7,
    }
}

# Or limit iterations
agent = ReActAgent(llm_configs=llm_configs, tools=tools, max_iterations=3)
```

Consider **REWOO** pattern for cost-sensitive applications.

### Speed Optimization

- Limit `max_iterations` for faster responses
- Use faster LLM models
- Optimize tool execution time
- Cache tool results when appropriate

## Comparison with Other Patterns

| Aspect | ReAct | REWOO | Reflexion |
|--------|-------|-------|-----------|
| **Tool Usage** | Interactive, adaptive | Planned upfront | Learning-based |
| **Cost** | Medium | Low | High |
| **Flexibility** | High | Medium | High |
| **Best For** | Dynamic tasks | Efficient automation | Learning from errors |

## Common Pitfalls

### 1. Unclear Tool Descriptions

❌ **Bad**:
```python
def search(q): ...
```

✅ **Good**:
```python
def search(query: str) -> str:
    """Search the web for information about a topic.

    Args:
        query: The search query string

    Returns:
        A summary of search results
    """
```

### 2. Too Many Tools

Providing 20+ tools can confuse the agent. Group related functionality:

❌ **Bad**: `search_google`, `search_bing`, `search_duckduckgo`
✅ **Good**: One `search` tool that handles different engines

### 3. Insufficient Iterations

If tasks consistently hit `max_iterations`, increase the limit.

### 4. Non-Deterministic Tools

Tools with random behavior can confuse the agent. Make tools deterministic when possible.

## Troubleshooting

### Agent Doesn't Use Tools

- Check tool descriptions are clear
- Verify tools are passed correctly
- Try prompt override to emphasize tool usage

### Agent Loops Infinitely

- Reduce `max_iterations`
- Add custom instructions about when to finish
- Override prompt to add loop detection

### Poor Quality Answers

- Use stronger LLM model (gpt-4 vs gpt-3.5)
- Add quality criteria in custom instructions
- Increase `max_iterations` for complex tasks

## Next Steps

- Try the [complete examples](../examples/react-examples.md)
- Learn about [REWOO](rewoo.md) for cost-efficient alternative
- Explore [Reflexion](reflexion.md) for learning from failures
- Read about [prompt customization](../guides/prompt-customization.md)

## References

- Original paper: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [LangChain ReAct documentation](https://python.langchain.com/docs/modules/agents/agent_types/react)
