# LLM Compiler Agent Pattern

The **LLM Compiler** pattern treats multi-tool workflows like a compiler, constructing a Directed Acyclic Graph (DAG) of tool calls with explicit dependencies, then executing nodes in topological order. This enables parallel execution of independent tools while respecting dependencies.

## Overview

**Best For**: Complex multi-tool workflows with parallelizable steps

**Complexity**: ⭐⭐⭐ Advanced (DAG construction and execution)

**Cost**: $$ Medium (Efficient execution despite complexity)

## When to Use LLM Compiler

### Ideal Use Cases

✅ **Parallel tool execution**
- Multiple independent tool calls
- Can execute simultaneously
- Respects dependencies when present
- Maximizes efficiency

✅ **Complex data pipelines**
- Multiple processing steps
- Clear dependencies between steps
- Benefits from parallel execution
- Structured workflow

✅ **Multi-source data gathering**
- Fetch from multiple sources
- Some sources independent
- Combine results systematically
- Optimize execution time

✅ **Workflow orchestration**
- Complex task dependencies
- Want optimal execution order
- Need to maximize parallelism
- Clear input/output relationships

### When NOT to Use LLM Compiler

❌ **Simple sequential tasks** → Use Plan & Solve
❌ **Highly dynamic workflows** → Use ReAct
❌ **Few tools needed** → Overhead not worthwhile
❌ **Unknown dependencies** → Hard to construct DAG upfront

## How LLM Compiler Works

### The DAG Construction and Execution

```
TASK: "Get weather in NYC and LA, calculate average temperature"

┌─────────────────────────────────────────┐
│  PHASE 1: PLANNER CREATES DAG           │
│                                         │
│  NODE: node1                            │
│  TOOL: get_weather                      │
│  ARGS: {"location": "NYC"}              │
│  DEPENDS_ON: []                         │
│                                         │
│  NODE: node2                            │
│  TOOL: get_weather                      │
│  ARGS: {"location": "LA"}               │
│  DEPENDS_ON: []                         │
│                                         │
│  NODE: node3                            │
│  TOOL: calculate                        │
│  ARGS: {"expr": "(#node1 + #node2) / 2"}│
│  DEPENDS_ON: [node1, node2]             │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  PHASE 2: EXECUTOR (Topological Order)  │
│                                         │
│  Iteration 1: Execute ready nodes       │
│  ├─ node1: weather("NYC") → "72°F"      │
│  └─ node2: weather("LA") → "85°F"       │
│  (Parallel execution!)                  │
│                                         │
│  Iteration 2: node1, node2 complete     │
│  └─ node3: calculate("(72+85)/2")       │
│     → "78.5°F"                          │
│                                         │
│  All nodes complete!                    │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  PHASE 3: SYNTHESIZER                   │
│                                         │
│  Results:                               │
│  - node1: 72°F                          │
│  - node2: 85°F                          │
│  - node3: 78.5°F                        │
│                                         │
│  Final Answer:                          │
│  "NYC weather: 72°F, LA weather: 85°F,  │
│   Average: 78.5°F"                      │
│                                         │
└─────────────────────────────────────────┘
```

### Key Concepts

**Directed Acyclic Graph (DAG)**:
- Nodes represent tool calls
- Edges represent dependencies
- No cycles (acyclic)
- Enables topological ordering

**Topological Execution**:
- Execute nodes when dependencies satisfied
- Parallel execution of independent nodes
- Efficient use of resources
- Guaranteed correct ordering

**Dependency Resolution**:
- `#node1` in parameters references another node's output
- Automatically resolved when node1 completes
- Enables data flow through DAG

### Theoretical Foundation

Based on the paper ["An LLM Compiler for Parallel Function Calling"](https://arxiv.org/abs/2312.04511). Inspired by compiler optimization techniques.

Key principles:
1. **Static analysis**: Determine dependencies upfront
2. **Optimization**: Identify parallelizable operations
3. **Efficient execution**: Run independent operations simultaneously
4. **Correctness**: Respect all dependencies

### Algorithm

```python
def llm_compiler(task, tools):
    """Simplified LLM Compiler algorithm"""

    # Phase 1: Construct DAG
    dag = planner_llm_generate_graph(task, tools)
    # dag = {
    #   "nodes": [
    #     {"id": "node1", "tool": "search", "args": {...}, "depends_on": []},
    #     {"id": "node2", "tool": "calc", "args": {"x": "#node1"}, "depends_on": ["node1"]},
    #   ]
    # }

    # Phase 2: Execute in topological order
    results = {}

    while not all_nodes_complete(dag, results):
        # Find nodes ready to execute (dependencies satisfied)
        ready_nodes = [
            n for n in dag["nodes"]
            if n["id"] not in results
            and all(dep in results for dep in n["depends_on"])
        ]

        # Execute ready nodes (can be parallelized)
        for node in ready_nodes:
            # Resolve dependencies in arguments
            resolved_args = resolve_references(node["args"], results)

            # Execute tool
            result = tools[node["tool"]](**resolved_args)
            results[node["id"]] = result

    # Phase 3: Synthesize final answer
    final_answer = synthesizer_llm(task, dag, results)

    return final_answer
```

## API Reference

### Class: `LLMCompilerAgent`

```python
from agent_patterns.patterns import LLMCompilerAgent

agent = LLMCompilerAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    tools: Optional[Dict[str, Callable]] = None,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configs for "thinking" and "documentation" roles |
| `tools` | `Dict[str, Callable]` | No | Dictionary mapping tool names to functions |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict` | No | Override specific prompts programmatically |

#### LLM Roles

- **thinking**: Used for planning (DAG generation)
- **documentation**: Used for synthesizing final answer

#### Methods

**`run(input_data: str) -> str`**

Executes the LLM Compiler pattern on the given input.

- **Parameters**:
  - `input_data` (str): The task requiring multiple tools
- **Returns**: str - The final synthesized answer
- **Raises**: ValueError if graph not built

**`build_graph() -> None`**

Builds the LangGraph state graph. Called automatically during initialization.

## Complete Examples

### Basic Usage

```python
from agent_patterns.patterns import LLMCompilerAgent

# Define tools
def search_tool(query: str) -> str:
    """Search for information"""
    # API call
    return f"Search results for: {query}"

def calculate_tool(expression: str) -> float:
    """Evaluate mathematical expression"""
    return eval(expression)  # Use safe_eval in production

def get_price(product: str) -> float:
    """Get product price"""
    prices = {"laptop": 999, "phone": 699, "tablet": 499}
    return prices.get(product, 0)

# Configure LLMs
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,
    },
    "documentation": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
    }
}

# Create agent
agent = LLMCompilerAgent(
    llm_configs=llm_configs,
    tools={
        "search": search_tool,
        "calculate": calculate_tool,
        "get_price": get_price,
    }
)

# Execute complex workflow
result = agent.run("""
Find the prices of laptop, phone, and tablet.
Calculate the total cost if I buy one of each.
Also search for information about each product's warranty.
Provide a summary with total cost and warranty info.
""")

print(result)
# Agent will:
# 1. PLAN: Create DAG with parallel price lookups and searches
# 2. EXECUTE: Run get_price and search calls in parallel
#    Then calculate total (depends on prices)
# 3. SYNTHESIZE: Combine all results into summary
```

### With Custom Instructions

```python
data_pipeline_instructions = """
You are orchestrating data processing pipelines.

DAG CONSTRUCTION:
- Identify all data sources (parallel)
- Identify processing steps (sequential when dependent)
- Identify aggregation steps (after all data ready)
- Maximize parallelism where safe

TOOL EXECUTION:
- Respect all dependencies
- Never execute before dependencies ready
- Handle errors gracefully

SYNTHESIS:
- Present data clearly
- Highlight key insights
- Show data lineage
"""

agent = LLMCompilerAgent(
    llm_configs=llm_configs,
    tools=tools,
    custom_instructions=data_pipeline_instructions
)

result = agent.run("""
Analyze sales data:
1. Fetch sales from Q1, Q2, Q3, Q4 (parallel)
2. Calculate total annual sales
3. Calculate quarter-over-quarter growth rates
4. Identify best and worst performing quarters
5. Generate executive summary
""")
```

### With Prompt Overrides

```python
# Customize DAG planning
overrides = {
    "PlanGraph": {
        "system": """You are an expert at constructing execution graphs for
multi-tool workflows. Create DAGs that maximize parallelism while respecting
all dependencies.""",
        "user": """Task: {task}

Available tools:
{tools}

Create a DAG (Directed Acyclic Graph) for this task.

For each node in the graph, specify:
NODE: <unique_id>
TOOL: <tool_name>
ARGS: <JSON args, use #node_id to reference other nodes>
DEPENDS_ON: <list of node_ids this depends on, or []>

Make independent operations parallelizable by having empty or non-overlapping
dependencies.

Your DAG:"""
    },
    "Synthesize": {
        "system": "You synthesize results from complex workflows into clear answers.",
        "user": """Task: {task}

Execution results:
{results}

Create a comprehensive answer that:
1. Addresses the original task completely
2. Presents information logically
3. Highlights key findings
4. Shows how results relate to each other

Your answer:"""
    }
}

agent = LLMCompilerAgent(
    llm_configs=llm_configs,
    tools=tools,
    prompt_overrides=overrides
)
```

## Tool Definition Guidelines

### Tool Function Signature

```python
def tool_name(param1: str, param2: int = 0) -> Any:
    """
    Clear description of what the tool does.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (optional)

    Returns:
        Result (can be any type, will be converted to string)
    """
    # Tool implementation
    return result
```

### Dependency References

Tools can reference other node outputs using `#node_id`:

```python
# In DAG:
# NODE: node1
# TOOL: get_data
# ARGS: {"source": "api"}
# DEPENDS_ON: []
#
# NODE: node2
# TOOL: process_data
# ARGS: {"data": "#node1"}  # References node1's output
# DEPENDS_ON: [node1]

# When executing node2, #node1 is replaced with actual result
```

## Customizing Prompts

### Understanding LLM Compiler Prompts

Uses two main prompts:

1. **PlanGraph**: Planner LLM creates DAG structure
2. **Synthesize**: Synthesizer LLM combines results

### Method 1: Custom Instructions

```python
agent = LLMCompilerAgent(
    llm_configs=llm_configs,
    tools=tools,
    custom_instructions="""
    OPTIMIZATION GOAL: Maximize parallelism
    CORRECTNESS GOAL: Respect all dependencies
    CLARITY GOAL: Clear, structured final answers
    """
)
```

### Method 2: Prompt Overrides

See "With Prompt Overrides" example above.

### Method 3: Custom Prompt Directory

```bash
my_prompts/
└── LLMCompilerAgent/
    ├── PlanGraph/
    │   ├── system.md
    │   └── user.md
    └── Synthesize/
        ├── system.md
        └── user.md
```

## Setting Agent Goals

### Via Task Description

```python
# Clear task with sub-goals
agent.run("""
Goal: Compare three cloud providers (AWS, GCP, Azure)

Sub-tasks (can be parallelized):
1. Get pricing for each provider
2. Get features for each provider
3. Search for reviews of each provider

Then:
4. Create comparison matrix
5. Generate recommendation

Provide detailed comparison.
""")
```

### Via Custom Instructions

```python
agent = LLMCompilerAgent(
    llm_configs=llm_configs,
    tools=tools,
    custom_instructions="""
    GOAL: Efficient, parallel execution of multi-tool workflows

    PLANNING:
    - Identify all independent operations
    - Enable maximum parallelism
    - Clear dependency chains

    EXECUTION:
    - Respect topological order
    - Handle errors without blocking entire workflow

    OUTPUT:
    - Comprehensive synthesis
    - Clear presentation
    - Actionable insights
    """
)
```

## Advanced Usage

### Parallel Execution Simulation

```python
# Current implementation executes sequentially
# But DAG enables parallel execution in production

class ParallelLLMCompilerAgent(LLMCompilerAgent):
    def _executor_dispatch(self, state):
        """Override to add parallel execution"""
        import concurrent.futures

        graph = state["execution_graph"]
        results = state["node_results"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            while not self._all_complete(graph, results):
                # Find ready nodes
                ready_nodes = self._get_ready_nodes(graph, results)

                if not ready_nodes:
                    break

                # Submit all ready nodes to executor
                futures = {
                    executor.submit(
                        self._execute_tool,
                        node["tool"],
                        node["args"],
                        results
                    ): node
                    for node in ready_nodes
                }

                # Collect results
                for future in concurrent.futures.as_completed(futures):
                    node = futures[future]
                    result = future.result()
                    results[node["id"]] = result

        state["node_results"] = results
        return state

agent = ParallelLLMCompilerAgent(llm_configs=llm_configs, tools=tools)
```

### DAG Visualization

```python
class VisualizingLLMCompilerAgent(LLMCompilerAgent):
    def run(self, input_data):
        """Override to visualize DAG"""
        result = super().run(input_data)

        # Access DAG (would need to store during execution)
        print("\n=== Execution DAG ===")
        self._print_dag()

        return result

    def _print_dag(self):
        """Print DAG structure"""
        # Implementation to visualize the execution graph
        pass

agent = VisualizingLLMCompilerAgent(llm_configs=llm_configs, tools=tools)
```

## Performance Considerations

### Cost Analysis

LLM Compiler cost:
- Plan DAG: 1 LLM call
- Execute tools: 0 LLM calls (just tool execution)
- Synthesize: 1 LLM call
- **Total: 2 LLM calls** (like REWOO)

**Efficiency gains**:
- Parallel execution reduces wall-clock time
- Only 2 LLM calls regardless of tool count
- Optimal execution order minimizes waste

### When LLM Compiler Excels

✅ **Many independent tools**: Parallel execution shines
✅ **Complex dependencies**: DAG handles correctly
✅ **Time-sensitive**: Parallelism speeds up execution
✅ **Clear structure**: Can plan DAG upfront

### When to Use Other Patterns

| Scenario | Better Pattern | Reason |
|----------|---------------|---------|
| Dynamic workflow | ReAct | Can't plan DAG upfront |
| Simple sequence | Plan & Solve | DAG overhead unnecessary |
| No tools | Self-Discovery, Reflection | LLM Compiler needs tools |
| Unknown dependencies | ReAct | Adaptive approach better |

## Comparison with Other Patterns

| Aspect | LLM Compiler | REWOO | ReAct |
|--------|--------------|-------|-------|
| **Planning** | DAG construction | Linear with placeholders | Adaptive |
| **Execution** | Topological order | Sequential | Iterative |
| **Parallelism** | Explicit support | No | No |
| **LLM Calls** | 2 (fixed) | 2 (fixed) | N + 1 |
| **Dependencies** | Explicit in DAG | Implicit in placeholders | Adaptive |
| **Best For** | Complex workflows | Batch operations | Dynamic exploration |

## Common Pitfalls

### 1. Circular Dependencies

❌ **Bad**: Creating cycles in DAG
```python
# NODE: node1 depends on node2
# NODE: node2 depends on node1
# → Impossible to execute!
```

✅ **Good**: Acyclic dependencies
```python
# NODE: node1 depends on []
# NODE: node2 depends on [node1]
# NODE: node3 depends on [node1, node2]
```

### 2. Missing Dependencies

❌ **Bad**: Not specifying required dependencies
```python
# NODE: node2 uses #node1 in args
# DEPENDS_ON: []  # Missing node1!
```

✅ **Good**: Explicit dependencies
```python
# NODE: node2 uses #node1 in args
# DEPENDS_ON: [node1]  # ✅ Correct
```

### 3. Over-Sequencing

❌ **Bad**: Making everything depend on everything

✅ **Good**: Only specify actual dependencies
```python
# If node2 and node3 are independent:
# NODE: node2 DEPENDS_ON: []
# NODE: node3 DEPENDS_ON: []
# → Can execute in parallel!
```

### 4. Incorrect Reference Syntax

❌ **Bad**: Wrong reference format
```python
# ARGS: {"data": "node1"}  # Missing #
```

✅ **Good**: Correct reference
```python
# ARGS: {"data": "#node1"}  # ✅ Will be resolved
```

## Troubleshooting

### DAG Parsing Failures

**Symptom**: Can't extract DAG from plan

**Solutions**:
```python
# Strengthen PlanGraph prompt format
overrides = {
    "PlanGraph": {
        "user": """...
STRICT FORMAT (follow exactly):

NODE: node1
TOOL: tool_name
ARGS: {"param": "value"}
DEPENDS_ON: []

NODE: node2
TOOL: tool_name
ARGS: {"param": "#node1"}
DEPENDS_ON: [node1]

(Blank line between nodes)

Your DAG:"""
    }
}
```

### Execution Hangs

**Symptom**: Some nodes never execute

**Solutions**:
```python
# Check for:
# 1. Circular dependencies (impossible to resolve)
# 2. Missing tools (can't execute)
# 3. Incorrect dependency specification

# Add validation:
class ValidatingLLMCompilerAgent(LLMCompilerAgent):
    def _planner_generate_graph(self, state):
        state = super()._planner_generate_graph(state)

        # Validate DAG
        if self._has_cycles(state["execution_graph"]):
            state["error"] = "Circular dependencies detected"

        return state
```

### Poor Parallelism

**Symptom**: Nodes execute sequentially despite being independent

**Solutions**:
```python
# Emphasize parallelism in planning
custom_instructions = """
DAG PLANNING:
When creating the DAG, actively look for opportunities for parallel execution.
If two nodes don't depend on each other, they should have independent DEPENDS_ON lists.
"""
```

## Next Steps

- Try the [complete examples](../examples/llm-compiler-examples.md)
- Learn about [REWOO](rewoo.md) for simpler batch execution
- Explore [ReAct](react.md) for dynamic tool workflows
- Read the [original paper](https://arxiv.org/abs/2312.04511)

## References

- Original paper: [An LLM Compiler for Parallel Function Calling](https://arxiv.org/abs/2312.04511)
- DAG concepts: [Directed Acyclic Graphs](https://en.wikipedia.org/wiki/Directed_acyclic_graph)
- Topological sorting: [Topological Sort](https://en.wikipedia.org/wiki/Topological_sorting)
- Compiler optimization techniques applied to LLM workflows
