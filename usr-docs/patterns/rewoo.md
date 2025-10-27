# REWOO Agent Pattern

The **REWOO** (Reason Without Observation) pattern separates planning from execution by having a Worker LLM create a complete plan with placeholders for tool results, then executing all tools, and finally integrating actual results. This minimizes expensive LLM calls, making it highly cost-effective.

## Overview

**Best For**: Cost-efficient multi-tool workflows with predictable dependencies

**Complexity**: ⭐⭐⭐ Advanced (Sophisticated planning with placeholders)

**Cost**: $$ Low-Medium (Minimal LLM calls despite tool complexity)

## When to Use REWOO

### Ideal Use Cases

✅ **Multi-tool workflows with known patterns**
- Plan all tool calls upfront
- Execute tools in parallel (when possible)
- Integrate results at the end
- Minimize LLM calls for cost efficiency

✅ **Batch processing tasks**
- Multiple related queries
- Predictable tool dependencies
- Can plan entire workflow upfront
- Want to minimize API costs

✅ **Research and data gathering**
- Multiple searches needed
- Information dependencies known upfront
- Synthesize all data at the end
- Cost is a concern

✅ **Pipeline-style workflows**
- Clear input → processing → output flow
- Tool calls can be orchestrated upfront
- Results combined systematically
- Efficiency matters

### When NOT to Use REWOO

❌ **Highly dynamic workflows** → Use ReAct for adaptive tool use
❌ **Unknown tool dependencies** → ReAct better for exploration
❌ **Simple single-tool tasks** → Overhead not worthwhile
❌ **Require iterative refinement** → Use Reflexion or Reflection

## How REWOO Works

### The Plan-Execute-Integrate Workflow

```
┌─────────────────────────────────────────┐
│                                         │
│  PHASE 1: WORKER PLAN (With Placeholders)│
│                                         │
│  Task: "Find CEO of Tesla and their    │
│         latest tweet"                   │
│  ↓                                      │
│  Plan Template:                         │
│  "Search for CEO of Tesla → {ceo_name} │
│   Search for latest tweet by           │
│   {ceo_name} → {latest_tweet}          │
│   Answer: The CEO is {ceo_name} and    │
│   their latest tweet is {latest_tweet}"│
│                                         │
│  Solver Requests:                       │
│  1. {ceo_name}: search("CEO of Tesla") │
│  2. {latest_tweet}: search("latest     │
│     tweet by {ceo_name}")              │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  PHASE 2: SOLVER EXECUTE (All Tools)    │
│                                         │
│  Execute request 1:                     │
│  {ceo_name} = search("CEO of Tesla")    │
│  Result: "Elon Musk"                    │
│  ↓                                      │
│  Execute request 2 (with filled value): │
│  {latest_tweet} = search("latest tweet  │
│                           by Elon Musk")│
│  Result: "Just launched Starship..."    │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  PHASE 3: WORKER INTEGRATE (Fill Plan)  │
│                                         │
│  Plan Template:                         │
│  "The CEO is {ceo_name} and their      │
│   latest tweet is {latest_tweet}"      │
│  ↓                                      │
│  Filled with actual results:            │
│  "The CEO is Elon Musk and their       │
│   latest tweet is 'Just launched       │
│   Starship...'"                        │
│  ↓                                      │
│  Worker synthesizes final answer        │
│                                         │
└─────────────────────────────────────────┘
```

### Theoretical Foundation

Based on the paper ["REWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models"](https://arxiv.org/abs/2305.18323). Key principles:

1. **Plan with placeholders**: Worker reasons about workflow without seeing results
2. **Deferred observation**: Don't call LLM after each tool use
3. **Batch execution**: Execute all tools, potentially in parallel
4. **Late integration**: Worker sees all results together at the end

**Cost savings**: Instead of LLM call after each tool use (ReAct), REWOO makes just 2 LLM calls (plan + integrate), regardless of number of tools.

### Algorithm

```python
def rewoo_workflow(task, tools):
    """Simplified REWOO algorithm"""

    # Phase 1: Worker creates plan with placeholders
    plan_template, solver_requests = worker_llm_plan(task, tools)
    # plan_template: "Find {x}, then calculate {y} based on {x}"
    # solver_requests: [{placeholder: "x", tool: "search", params: {...}}, ...]

    # Phase 2: Execute all solver requests
    solver_results = {}
    for request in solver_requests:
        # Resolve dependencies using previous results
        resolved_params = resolve_placeholders(
            request.params,
            solver_results
        )

        # Execute tool
        result = tools[request.tool](**resolved_params)
        solver_results[request.placeholder] = result

    # Phase 3: Worker integrates results
    final_answer = worker_llm_integrate(
        task,
        plan_template,
        solver_results
    )

    return final_answer
```

## API Reference

### Class: `REWOOAgent`

```python
from agent_patterns.patterns import REWOOAgent

agent = REWOOAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    tools: Optional[Dict[str, Callable]] = None,
    solver_llm_role: str = "solver",
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configs for "thinking" and optional "solver" roles |
| `tools` | `Dict[str, Callable]` | No | Dictionary mapping tool names to functions |
| `solver_llm_role` | `str` | No | Role name for solver LLM (default: "solver") |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict` | No | Override specific prompts programmatically |

#### LLM Roles

- **thinking**: Worker LLM for planning and integration
- **solver** (optional): Cheaper LLM for tool execution fallback

#### Methods

**`run(input_data: str) -> str`**

Executes the REWOO pattern on the given input.

- **Parameters**:
  - `input_data` (str): The task requiring tool use
- **Returns**: str - The final integrated answer
- **Raises**: ValueError if graph not built

**`build_graph() -> None`**

Builds the LangGraph state graph. Called automatically during initialization.

## Complete Examples

### Basic Usage

```python
from agent_patterns.patterns import REWOOAgent

# Define tools
def search_web(query: str) -> str:
    """Search the web for information"""
    import requests
    response = requests.get(f"https://api.search.com?q={query}")
    return response.json()["snippet"]

def calculate(expression: str) -> float:
    """Evaluate a mathematical expression"""
    return eval(expression)  # Use safe_eval in production

def get_weather(location: str) -> str:
    """Get current weather"""
    # API call
    return f"Weather in {location}: Sunny, 72°F"

# Configure LLMs
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4",  # Strong model for planning
        "temperature": 0.3,
    },
    "solver": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper model for simple tool use
        "temperature": 0,
    }
}

# Create agent
agent = REWOOAgent(
    llm_configs=llm_configs,
    tools={
        "search": search_web,
        "calculate": calculate,
        "weather": get_weather,
    }
)

# Execute complex multi-tool workflow
result = agent.run("""
Find the population of Tokyo, then the population of London,
then calculate which is larger and by what percentage.
Also get the current weather in both cities.
""")

print(result)
# Agent will:
# 1. PLAN: Create workflow with placeholders
#    {tokyo_pop}, {london_pop}, {percentage}, {tokyo_weather}, {london_weather}
# 2. EXECUTE: Run all searches and calculations
# 3. INTEGRATE: Combine results into final answer
# Total LLM calls: 2 (plan + integrate)
```

### With Custom Instructions

```python
research_guidelines = """
You are a research assistant using REWOO for efficient information gathering.

PLANNING:
- Identify all information needs upfront
- Create placeholders for each piece of data
- Show clear dependencies between data points
- Plan for parallel execution where possible

INTEGRATION:
- Synthesize all gathered data coherently
- Cite sources for each piece of information
- Provide comprehensive analysis
- Structure answer logically
"""

agent = REWOOAgent(
    llm_configs=llm_configs,
    tools={"search": search_web, "calculate": calculate},
    custom_instructions=research_guidelines
)

result = agent.run("""
Research the history of space exploration:
- When was the first satellite launched?
- When was the first human in space?
- When was the moon landing?
- Calculate the years between each milestone
- Summarize the progression
""")
```

### With Prompt Overrides

```python
# Customize planning format
overrides = {
    "WorkerPlan": {
        "system": """You are a planning expert using the REWOO pattern.
Create plans with placeholders for tool results you haven't seen yet.""",
        "user": """Task: {task}

Available tools:
{tools}

Create a plan using placeholders like {{result1}}, {{result2}}, etc.

Output format:
PLAN: <description of plan with placeholders>

SOLVER: <placeholder_name>
TOOL: <tool_name>
PARAMS: <JSON params, can reference other placeholders>

(Repeat SOLVER blocks for each tool call needed)

Your plan:"""
    },
    "WorkerIntegrate": {
        "system": "You synthesize information from multiple sources into coherent answers.",
        "user": """Task: {task}

Planned workflow:
{plan}

Actual results:
{results}

Combine these results into a comprehensive final answer that addresses
the original task. Be specific and cite the information gathered.

Your answer:"""
    }
}

agent = REWOOAgent(
    llm_configs=llm_configs,
    tools={"search": search_web},
    prompt_overrides=overrides
)
```

## Tool Definition Guidelines

### Tool Function Signature

Same as ReAct pattern:

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

### Placeholder Resolution

REWOO automatically resolves placeholders in parameters:

```python
# Solver request:
# SOLVER: result2
# TOOL: search
# PARAMS: {"query": "population of {result1}"}

# If {result1} = "Tokyo", params become:
# {"query": "population of Tokyo"}
```

## Customizing Prompts

### Understanding the System Prompt Structure

Version 0.2.0 introduces **enterprise-grade prompts** with a comprehensive 9-section structure (150-300+ lines vs ~32 lines).

**The 9-Section Structure**: All prompts include Role and Identity, Core Capabilities, Process, Output Format, Decision-Making Guidelines, Quality Standards, Edge Cases, Examples, and Critical Reminders. **Benefits**: Better reliability and transparency.

### Understanding REWOO Prompts

REWOO uses two main prompts (both now with comprehensive 9-section structure):

1. **WorkerPlan**: Worker LLM creates plan with placeholders and solver requests using systematic guidance
2. **WorkerIntegrate**: Worker LLM combines solver results into final answer with quality standards

### Method 1: Custom Instructions

```python
agent = REWOOAgent(
    llm_configs=llm_configs,
    tools=tools,
    custom_instructions="""
    EFFICIENCY FOCUS:
    - Plan for maximum parallel execution
    - Minimize total tool calls
    - Identify dependencies explicitly

    QUALITY FOCUS:
    - Ensure plan covers all task requirements
    - Create clear placeholders
    - Provide comprehensive final synthesis
    """
)
```

### Method 2: Prompt Overrides

See "With Prompt Overrides" example above.

### Method 3: Custom Prompt Directory

```bash
my_prompts/
└── REWOOAgent/
    ├── WorkerPlan/
    │   ├── system.md
    │   └── user.md
    └── WorkerIntegrate/
        ├── system.md
        └── user.md
```

## Setting Agent Goals

### Via Task Description

```python
# Clear task with multiple steps
agent.run("""
Goal: Compare cloud providers for ML workloads

Steps needed:
1. Find pricing for GPU instances on AWS, GCP, Azure
2. Find ML framework support for each
3. Find typical training times reported by users
4. Calculate cost for 100 hours of training
5. Provide recommendation with justification
""")
```

### Via Custom Instructions

```python
agent = REWOOAgent(
    llm_configs=llm_configs,
    tools=tools,
    custom_instructions="""
    GOAL: Provide data-driven, cost-effective answers

    PLANNING GOALS:
    - Gather all necessary data in one pass
    - Minimize redundant tool calls
    - Structure for efficient execution

    INTEGRATION GOALS:
    - Present findings clearly
    - Support recommendations with data
    - Note any limitations in gathered information
    """
)
```

## Advanced Usage

### Parallel Tool Execution

```python
# REWOO naturally supports parallel execution
# because dependencies are explicit in the plan

# Worker plans:
# SOLVER: result1
# TOOL: search
# PARAMS: {"query": "topic A"}
# DEPENDS_ON: []
#
# SOLVER: result2
# TOOL: search
# PARAMS: {"query": "topic B"}
# DEPENDS_ON: []
#
# → result1 and result2 can execute in parallel

# SOLVER: result3
# TOOL: calculate
# PARAMS: {"expr": "{result1} + {result2}"}
# DEPENDS_ON: [result1, result2]
#
# → result3 waits for result1 and result2
```

### Custom Solver Logic

```python
class CustomREWOOAgent(REWOOAgent):
    def _call_solver(self, tool_name, params):
        """Override to add custom solver behavior"""

        # Add logging
        print(f"Executing {tool_name} with {params}")

        # Add caching
        cache_key = f"{tool_name}:{str(params)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Execute tool
        result = super()._call_solver(tool_name, params)

        # Cache result
        self.cache[cache_key] = result

        return result

    def __init__(self, *args, **kwargs):
        self.cache = {}
        super().__init__(*args, **kwargs)

agent = CustomREWOOAgent(llm_configs=llm_configs, tools=tools)
```

### Fallback to Solver LLM

```python
# If a tool isn't available, REWOO can use solver LLM
llm_configs = {
    "thinking": {"provider": "openai", "model": "gpt-4"},
    "solver": {"provider": "openai", "model": "gpt-3.5-turbo"}
}

agent = REWOOAgent(
    llm_configs=llm_configs,
    tools={"search": search_web}  # Only one tool
)

# If plan requests unavailable tool, solver LLM attempts it
```

## Performance Considerations

### Cost Optimization

REWOO's key advantage is cost efficiency:

**ReAct cost** for N tools:
- Plan: 1 call
- Tool 1: 1 call (reason after observation)
- Tool 2: 1 call
- Tool N: 1 call
- **Total: N + 1 LLM calls**

**REWOO cost** for N tools:
- Plan: 1 call
- Execute: 0 LLM calls (just tools)
- Integrate: 1 call
- **Total: 2 LLM calls** (regardless of N!)

```python
# Example: 10 tool calls
# ReAct: 11 LLM calls
# REWOO: 2 LLM calls
# Savings: 82% reduction in LLM calls
```

### When REWOO Saves Money

✅ **Many tools**: More tools = more savings vs ReAct
✅ **Expensive LLM**: Cost savings multiply with expensive models
✅ **Predictable workflows**: Can plan everything upfront
✅ **Batch processing**: Process many similar tasks

### When ReAct is Better

❌ **Highly dynamic**: Next tool depends unpredictably on results
❌ **Exploratory**: Don't know what tools needed upfront
❌ **Few tools**: Overhead not worthwhile for 1-2 tools
❌ **Complex dependencies**: Hard to plan without seeing results

## Comparison with Other Patterns

| Aspect | REWOO | ReAct | LLM Compiler |
|--------|-------|-------|--------------|
| **LLM Calls** | 2 (fixed) | N + 1 | Variable |
| **Planning** | Upfront with placeholders | Adaptive | DAG construction |
| **Tool Execution** | Batch | Sequential | Topological order |
| **Cost** | Low | Medium | Medium |
| **Flexibility** | Medium | High | Medium |
| **Best For** | Cost efficiency | Dynamic workflows | Complex dependencies |

## Common Pitfalls

### 1. Unpredictable Dependencies

❌ **Bad**: Using REWOO when you can't plan upfront
```python
# Task: "Search for information, and depending on what you find,
#        search for more related information"
# → Can't create placeholders without knowing what you'll find
# → Use ReAct instead
```

✅ **Good**: Predictable workflow
```python
# Task: "Find population of city X, population of city Y, calculate difference"
# → Can plan all steps upfront
# → REWOO perfect for this
```

### 2. Poor Placeholder Naming

❌ **Bad**: Unclear placeholder names
```python
# SOLVER: x
# SOLVER: y
# SOLVER: z
# → Hard to track what each represents
```

✅ **Good**: Descriptive placeholders
```python
# SOLVER: tokyo_population
# SOLVER: london_population
# SOLVER: population_difference
```

### 3. Missing Dependencies

❌ **Bad**: Not specifying parameter dependencies

✅ **Good**: Explicit placeholder references
```python
# SOLVER: city_name
# TOOL: search
# PARAMS: {"query": "capital of France"}
#
# SOLVER: weather
# TOOL: get_weather
# PARAMS: {"location": "{city_name}"}  # ✅ Clear dependency
```

### 4. Over-Planning

❌ **Bad**: Creating overly complex plans

✅ **Good**: Keep plans straightforward
```python
# Aim for 3-7 solver requests for typical tasks
# If plan gets too complex, might not be right pattern
```

## Troubleshooting

### Plan Doesn't Parse Correctly

**Symptom**: Solver requests not extracted properly

**Solutions**:
```python
# Override WorkerPlan prompt with stricter format
overrides = {
    "WorkerPlan": {
        "user": """...
STRICT FORMAT - Follow exactly:

PLAN: <your plan description with {placeholders}>

SOLVER: placeholder_name
TOOL: exact_tool_name
PARAMS: {"param": "value", "param2": "{other_placeholder}"}

(Blank line between each SOLVER block)

Your plan:"""
    }
}
```

### Results Not Integrating Well

**Symptom**: Final answer doesn't use all solver results

**Solutions**:
```python
# Strengthen integration prompt
overrides = {
    "WorkerIntegrate": {
        "user": """Task: {task}

Plan you created:
{plan}

Results from executing plan:
{results}

Using ALL the results above, create a comprehensive answer.
Make sure to incorporate every piece of information gathered.

Your integrated answer:"""
    }
}
```

### Tool Execution Failures

**Symptom**: Tools fail or return errors

**Solutions**:
```python
# Add error handling to tools
def robust_search(query: str) -> str:
    try:
        return actual_search(query)
    except Exception as e:
        return f"Search failed: {str(e)}. Please try different query."

# REWOO will integrate error messages, Worker can handle gracefully
```

## Next Steps

- Try the [complete examples](../examples/rewoo-examples.md)
- Learn about [ReAct](react.md) for dynamic tool use
- Explore [LLM Compiler](llm-compiler.md) for DAG-based execution
- Read the [original paper](https://arxiv.org/abs/2305.18323)

## References

- Original paper: [REWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models](https://arxiv.org/abs/2305.18323)
- Related: Planning and execution separation in AI systems
- Cost optimization strategies for LLM-based agents
