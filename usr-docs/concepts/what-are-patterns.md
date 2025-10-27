# What Are Agent Patterns?

Agent patterns are reusable architectural blueprints for building AI agent workflows. Just as design patterns in software engineering provide proven solutions to common problems, agent patterns provide structured approaches to common AI agent challenges.

## The Problem with Ad-Hoc Agents

When building AI agents from scratch, developers often face:

1. **Inconsistent Results**: Single-prompt approaches are unreliable for complex tasks
2. **Hard to Debug**: Monolithic prompt chains are difficult to troubleshoot
3. **No Structure**: Each agent is built from scratch with unique logic
4. **Limited Reusability**: Solutions don't transfer across projects
5. **Unpredictable Behavior**: Without structure, agents behave inconsistently

### Example: Ad-Hoc Approach

```python
# Ad-hoc approach - no pattern
def answer_question(question: str) -> str:
    prompt = f"Answer this question: {question}"
    response = llm.invoke(prompt)
    return response

# Problems:
# - No tool use
# - No verification
# - No reasoning structure
# - No error handling
# - No iterative refinement
```

This works for simple queries but fails for complex tasks requiring:
- Multiple reasoning steps
- Tool/API interactions
- Self-correction
- Quality refinement
- Exploration of alternatives

## What Are Patterns?

Agent patterns are **structured workflows** that break complex agent behavior into:

1. **Clear Stages**: Distinct phases with specific responsibilities
2. **State Management**: Tracking progress and intermediate results
3. **Conditional Logic**: Decision points for routing and iteration
4. **Tool Integration**: Structured approach to external interactions
5. **Quality Control**: Built-in verification and refinement

### Example: Pattern-Based Approach

```python
# ReAct Pattern - structured workflow
agent = ReActAgent(
    llm_configs=configs,
    tools={"search": search_tool, "calculator": calc_tool},
    max_iterations=5
)

result = agent.run("What is the population of Tokyo times 2?")

# Workflow:
# 1. Thought: "I need to find Tokyo's population"
# 2. Action: search("Tokyo population")
# 3. Observation: "~14 million"
# 4. Thought: "Now I need to multiply by 2"
# 5. Action: calculator("14000000 * 2")
# 6. Observation: "28000000"
# 7. Final Answer: "28 million"
```

The pattern provides:
- Structured reasoning loop
- Tool selection logic
- Error recovery
- Iteration control
- State tracking

## Why Patterns Matter

### 1. Reliability

Patterns provide consistent, predictable behavior:

```python
# Without pattern: unpredictable
response = llm.invoke("Write a story")
# Quality varies wildly, no guarantee of structure

# With Reflection pattern: consistent quality
agent = ReflectionAgent(llm_configs=configs)
response = agent.run("Write a story")
# Always generates, critiques, and refines
```

### 2. Debuggability

Patterns break workflows into inspectable stages:

```python
# Without pattern: black box
result = complex_prompt(input)
# Can't see intermediate steps

# With Plan & Solve pattern: transparent
agent = PlanAndSolveAgent(llm_configs=configs)
result = agent.run(input)
# Can inspect: plan, step results, aggregation
```

### 3. Reusability

Patterns transfer across domains:

```python
# Same ReAct pattern, different domains

# Domain 1: Customer Service
customer_agent = ReActAgent(
    tools={"check_order": check_order_status, "cancel_order": cancel},
    llm_configs=configs
)

# Domain 2: Data Analysis
data_agent = ReActAgent(
    tools={"query_db": run_sql, "plot": create_chart},
    llm_configs=configs
)

# Same pattern, different tools!
```

### 4. Best Practices

Patterns encode research-backed approaches:

| Pattern | Research Paper | Key Insight |
|---------|---------------|-------------|
| ReAct | [Yao et al., 2023](https://arxiv.org/abs/2210.03629) | Interleaving reasoning and acting improves performance |
| Reflection | [Shinn et al., 2023](https://arxiv.org/abs/2303.11366) | Self-reflection improves output quality |
| Plan & Solve | [Wang et al., 2023](https://arxiv.org/abs/2305.04091) | Separating planning from execution increases reliability |
| STORM | [Shao et al., 2024](https://arxiv.org/abs/2402.14207) | Multi-perspective synthesis improves comprehensiveness |

## Pattern vs Non-Pattern Approaches

### Comparison Table

| Aspect | Non-Pattern | Pattern-Based |
|--------|-------------|---------------|
| **Structure** | Ad-hoc prompts | Defined workflow stages |
| **State** | None or implicit | Explicit state tracking |
| **Tools** | Manual integration | Structured tool use |
| **Iteration** | One-shot | Controlled loops |
| **Debugging** | Difficult (black box) | Easy (inspectable stages) |
| **Quality** | Inconsistent | Predictable |
| **Reusability** | Low | High |
| **Maintenance** | Brittle | Modular |

### Real-World Example

**Task**: Generate a research report on quantum computing

**Non-Pattern Approach:**

```python
prompt = """
Write a comprehensive research report on quantum computing.
Include history, current state, applications, and future outlook.
Use authoritative sources and cite them.
"""

report = llm.invoke(prompt)
# Problems:
# - No source verification
# - May hallucinate facts
# - No structured research process
# - Can't trace reasoning
# - Single attempt, no refinement
```

**Pattern Approach (STORM):**

```python
agent = STORMAgent(
    llm_configs=configs,
    retrieval_tools={"search": wikipedia_search, "scholar": academic_search}
)

report = agent.run("quantum computing")

# Workflow:
# 1. Generate outline (intro, history, applications, future, conclusion)
# 2. Generate perspectives (physicist, engineer, business analyst)
# 3. Generate questions per perspective per section
# 4. Retrieve information for each question
# 5. Synthesize each section from retrieved info
# 6. Compile final report with citations

# Benefits:
# - Systematic research process
# - Multiple viewpoints
# - Source-backed claims
# - Transparent methodology
# - Structured output
```

## Common Pattern Categories

### 1. Tool-Using Patterns

Agents that interact with external systems:

- **ReAct**: Reason about what to do, act with tools
- **LLM Compiler**: Plan and execute tools in parallel
- **REWOO**: Separate planning from tool execution for efficiency

**Use When**: Need to search, calculate, query APIs, or access external data

### 2. Refinement Patterns

Agents that improve output through iteration:

- **Reflection**: Generate, critique, refine
- **Reflexion**: Learn from failures across trials
- **LATS**: Explore multiple solution paths

**Use When**: Output quality is critical (writing, coding, design)

### 3. Planning Patterns

Agents that decompose complex tasks:

- **Plan & Solve**: Create plan, execute sequentially
- **Self-Discovery**: Dynamically select reasoning strategies

**Use When**: Task has multiple logical steps or requires strategic thinking

### 4. Multi-Perspective Patterns

Agents that synthesize diverse viewpoints:

- **STORM**: Multi-perspective research and synthesis

**Use When**: Need comprehensive, well-rounded analysis

## When to Use Patterns

### Use Patterns When:

1. **Task Complexity**: Requires multiple steps or reasoning stages
2. **Quality Matters**: Output must be reliable and consistent
3. **Need Tools**: Must interact with external systems/data
4. **Refinement Required**: Initial output needs improvement
5. **Reusability**: Will apply same workflow to different inputs
6. **Debugging**: Need to understand agent behavior
7. **Collaboration**: Others will work on or extend the agent

### Use Simple Prompts When:

1. **Task is Trivial**: Single, straightforward question
2. **Speed Critical**: Can't afford multi-step workflow
3. **Prototyping**: Exploring what's possible
4. **Budget Constrained**: Multiple LLM calls are too expensive

### Example Decision:

```python
# Simple task - direct prompt is fine
answer = llm.invoke("What is the capital of France?")

# Complex task - use pattern
agent = ReActAgent(
    tools={"search": search, "calculate": calc},
    llm_configs=configs
)
answer = agent.run(
    "Find the GDP of France and Germany, "
    "calculate the ratio, and explain the economic factors"
)
```

## The Agent Patterns Library

This library provides 9 battle-tested patterns:

| Pattern | Category | Best For |
|---------|----------|----------|
| **ReAct** | Tool-Using | Q&A with external data |
| **Reflection** | Refinement | High-quality content |
| **Plan & Solve** | Planning | Multi-step tasks |
| **Reflexion** | Refinement | Learning from failures |
| **LLM Compiler** | Tool-Using | Parallel tool execution |
| **REWOO** | Tool-Using | Cost-efficient workflows |
| **LATS** | Refinement | Exploring solutions |
| **Self-Discovery** | Planning | Adaptive reasoning |
| **STORM** | Multi-Perspective | Comprehensive research |

Each pattern is:
- **Fully Implemented**: Ready to use out of the box
- **Customizable**: Override prompts and behavior
- **Type-Safe**: Full type hints for IDE support
- **Well-Tested**: Comprehensive test coverage
- **Documented**: Clear API and examples

## Design Philosophy

Agent Patterns follows these principles:

### 1. Synchronous by Design

```python
# Synchronous - simple and debuggable
result = agent.run(input)

# NOT async - complexity removed
# result = await agent.run(input)
```

**Why**: Async adds complexity, makes debugging harder, and isn't needed for most agent workflows.

### 2. Externalized Configuration

```python
# Prompts in files, not code
agent = ReActAgent(prompt_dir="my_prompts")

# Easy to customize without touching code
```

**Why**: Separates prompt engineering from software engineering, enables non-coders to customize.

### 3. Explicit State

```python
# State is explicit and inspectable
state = {
    "input": "query",
    "thought": "...",
    "action": {...},
    "observation": "...",
}
```

**Why**: Makes debugging and monitoring straightforward.

### 4. Composable Tools

```python
# Tools are simple functions
def my_tool(input: str) -> str:
    return result

# Easy to test, mock, and reuse
```

**Why**: Keep tools simple, focused, and testable.

## Next Steps

- **Understand the Architecture**: Learn [how patterns work internally](architecture.md)
- **Choose a Pattern**: Use the [pattern selection guide](../patterns/choosing-a-pattern.md)
- **See Examples**: Explore [real-world examples](../examples/index.md)
- **API Reference**: Study the [complete API documentation](../api/patterns.md)
- **Build Custom**: Learn to [extend BaseAgent](../api/base-agent.md) for custom patterns

## Key Takeaways

1. Patterns provide **structure** for complex agent workflows
2. They improve **reliability, debuggability, and reusability**
3. Use patterns for **complex tasks**, simple prompts for **trivial queries**
4. Each pattern encodes **research-backed best practices**
5. The library provides **9 production-ready patterns**
6. All patterns share a **consistent architecture** making them easy to learn and use
