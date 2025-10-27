# Choosing a Pattern

A comprehensive guide to selecting the right agent pattern for your task.

## Quick Decision Tree

Start here for a quick recommendation:

```
Do you need to use external tools/APIs?
├─ YES → Do you need parallel tool execution?
│  ├─ YES → Use LLM Compiler
│  └─ NO → Do you need cost efficiency?
│     ├─ YES → Use REWOO
│     └─ NO → Use ReAct
│
└─ NO → Is this a content generation task?
   ├─ YES → Do you need multiple perspectives?
   │  ├─ YES → Use STORM
   │  └─ NO → Use Reflection
   │
   └─ NO → Can you break it into clear steps?
      ├─ YES → Use Plan & Solve
      └─ NO → Is it a novel/complex problem?
         ├─ YES (adaptive) → Use Self-Discovery
         ├─ YES (explore) → Use LATS
         └─ NO (learn) → Use Reflexion
```

## Detailed Pattern Guide

### ReAct Pattern

**Best For:**
- Question answering with external data
- Tasks requiring tool use
- Real-time information lookups
- API integrations

**Use When:**
- Need to search, calculate, or query external systems
- Tool selection should be dynamic
- Iterative reasoning is beneficial
- Response time is important

**Avoid When:**
- No tools needed
- Parallel execution more efficient
- Cost is primary concern

**Example Use Cases:**
- "What's the weather in Tokyo and what's happening there today?"
- "Find the stock price of AAPL and calculate percent change from last week"
- "Search for recent papers on transformers and summarize the findings"

**Configuration:**
```python
agent = ReActAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    tools={
        "search": search_tool,
        "calculator": calc_tool,
        "database": db_tool
    },
    max_iterations=5  # Adjust based on complexity
)
```

**Pros:**
- Flexible tool selection
- Good for exploratory tasks
- Natural reasoning flow

**Cons:**
- Sequential tool execution (not parallel)
- More LLM calls than REWOO
- Can loop if not careful

---

### Reflection Pattern

**Best For:**
- High-quality content generation
- Writing, coding, design
- Tasks where quality matters more than speed
- Iterative refinement

**Use When:**
- Initial output quality insufficient
- Self-critique would improve results
- Have budget for multiple LLM calls
- Quality more important than cost

**Avoid When:**
- Simple queries
- Speed critical
- First attempt usually sufficient
- Very constrained budget

**Example Use Cases:**
- "Write a technical blog post about microservices"
- "Create a product description for our smart thermostat"
- "Draft an email to investors about Q4 results"
- "Write a function to parse CSV files with error handling"

**Configuration:**
```python
agent = ReflectionAgent(
    llm_configs={
        "documentation": {  # Generates content
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "reflection": {  # Critiques content
            "provider": "openai",
            "model_name": "gpt-4-turbo"
        }
    },
    max_reflection_cycles=1  # 1-2 usually sufficient
)
```

**Pros:**
- Significantly improves output quality
- Catches errors and omissions
- Natural refinement process

**Cons:**
- Higher cost (multiple LLM calls)
- Slower than single-pass
- Diminishing returns after 2-3 cycles

---

### Plan & Solve Pattern

**Best For:**
- Multi-step tasks with clear structure
- Research and analysis
- Tasks requiring decomposition
- Sequential workflows

**Use When:**
- Task has logical steps
- Planning improves execution
- Each step builds on previous
- Want structured approach

**Avoid When:**
- Single-step task
- Iterative exploration needed
- Tool use required (use ReAct instead)
- Steps are unclear upfront

**Example Use Cases:**
- "Create a marketing strategy for our new product launch"
- "Analyze the competitive landscape for AI code assistants"
- "Design a database schema for an e-commerce platform"
- "Write a comprehensive guide to Python decorators"

**Configuration:**
```python
agent = PlanAndSolveAgent(
    llm_configs={
        "planning": {  # Creates plan
            "provider": "openai",
            "model_name": "gpt-4-turbo"
        },
        "execution": {  # Executes steps
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        },
        "documentation": {  # Aggregates results
            "provider": "openai",
            "model_name": "gpt-3.5-turbo"
        }
    }
)
```

**Pros:**
- Structured approach
- Clear progress tracking
- Good for complex tasks
- Can use cheaper model for execution

**Cons:**
- No tool use
- Less flexible than ReAct
- Plan may be suboptimal

---

### Reflexion Pattern

**Best For:**
- Tasks benefiting from trial and error
- Complex problem-solving
- Code generation with testing
- Learning from failures

**Use When:**
- Have evaluator function
- Multiple attempts acceptable
- Failure provides learning signal
- Quality critical

**Avoid When:**
- No clear success metric
- Can't afford multiple trials
- Task is simple
- Immediate answer needed

**Example Use Cases:**
- "Write a function to solve this algorithmic problem" (with test cases)
- "Generate SQL query that passes these validation tests"
- "Create a regex pattern matching these examples"
- "Design an API that meets these requirements" (with validation)

**Configuration:**
```python
def evaluator(code: str) -> bool:
    """Test if generated code is correct."""
    try:
        exec(code)
        # Run test cases
        return all_tests_pass
    except:
        return False

agent = ReflexionAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "reflection": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    evaluator=evaluator,
    max_trials=3
)
```

**Pros:**
- Learns from failures
- Improves with each trial
- Great with test-driven tasks

**Cons:**
- Expensive (multiple full attempts)
- Requires evaluator function
- May not converge

---

### LLM Compiler Pattern

**Best For:**
- Parallel tool execution
- Multi-source data gathering
- DAG-structured workflows
- Performance-critical applications

**Use When:**
- Tools can run in parallel
- Have clear dependencies
- Speed matters
- Multiple independent data sources

**Avoid When:**
- Tools must run sequentially
- Dependencies too complex
- Simple linear workflow
- Single tool sufficient

**Example Use Cases:**
- "Get weather in 5 cities and compare" (parallel weather calls)
- "Fetch user data, order history, and recommendations simultaneously"
- "Query multiple databases and aggregate results"
- "Search multiple APIs and synthesize findings"

**Configuration:**
```python
agent = LLMCompilerAgent(
    llm_configs={
        "planning": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "synthesis": {"provider": "openai", "model_name": "gpt-3.5-turbo"}
    },
    tools={
        "weather": weather_api,
        "news": news_api,
        "stocks": stock_api,
        "database": db_query
    }
)
```

**Pros:**
- Parallel execution (faster)
- Efficient use of tools
- Handles dependencies

**Cons:**
- More complex than ReAct
- Requires independent tools
- Overhead for simple tasks

---

### REWOO Pattern

**Best For:**
- Cost-efficient workflows
- Predictable tool needs
- Batch processing
- When tools are expensive

**Use When:**
- Tool execution cost > LLM cost
- Can plan tools upfront
- Don't need dynamic tool selection
- Want to minimize LLM calls

**Avoid When:**
- Tool needs unpredictable
- Dynamic exploration required
- LLM cost > tool cost
- Need adaptive behavior

**Example Use Cases:**
- "Who won the Nobel Prize in Physics in 2023 and what was their work?"
- "Find information about Tesla's founding and key milestones"
- "Research the history of the internet"
- Tasks with predictable information needs

**Configuration:**
```python
agent = REWOOAgent(
    llm_configs={
        "planning": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "worker": {"provider": "openai", "model_name": "gpt-3.5-turbo"},
        "solver": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    tools={
        "search": search_tool,
        "wikipedia": wiki_tool
    }
)
```

**Pros:**
- Fewer LLM calls than ReAct
- Predictable cost
- Efficient tool use

**Cons:**
- Less flexible
- Can't adapt plan mid-execution
- May gather unnecessary data

---

### LATS Pattern

**Best For:**
- Exploring solution spaces
- Creative tasks
- Optimization problems
- When multiple approaches possible

**Use When:**
- Want to explore alternatives
- Quality more important than cost
- Problem has multiple solutions
- Benefit from searching options

**Avoid When:**
- Simple task with obvious solution
- Cost constrained
- Time constrained
- Single correct answer

**Example Use Cases:**
- "Design an optimal algorithm for task scheduling"
- "Create three different marketing slogans and pick the best"
- "Find the best route for visiting these cities"
- "Generate and evaluate multiple solution approaches"

**Configuration:**
```python
agent = LATSAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "evaluation": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    max_expansions=10,  # How many nodes to explore
    max_depth=5  # How deep to search
)
```

**Pros:**
- Explores multiple paths
- Finds better solutions
- Good for optimization

**Cons:**
- Very expensive (many LLM calls)
- Slow (explores many options)
- May over-complicate simple tasks

---

### Self-Discovery Pattern

**Best For:**
- Novel problems without clear approach
- Adaptive reasoning
- Complex reasoning tasks
- When best strategy unclear

**Use When:**
- Problem doesn't fit standard pattern
- Want agent to select reasoning approach
- Problem requires multiple reasoning strategies
- Exploring new problem types

**Avoid When:**
- Problem well-understood
- Standard approach works
- Simplicity preferred
- Reasoning strategy obvious

**Example Use Cases:**
- "How can we reduce urban traffic congestion?"
- "Design a new approach to online education"
- "Solve this novel optimization problem"
- "Create an innovative business model for X"

**Configuration:**
```python
agent = SelfDiscoveryAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "execution": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    max_selected_modules=3,  # How many reasoning strategies to use
    reasoning_modules=custom_modules  # Optional custom strategies
)
```

**Pros:**
- Adaptive to problem type
- Uses appropriate reasoning strategies
- Good for novel problems

**Cons:**
- Complex
- Higher cost
- May be overkill for simple tasks

---

### STORM Pattern

**Best For:**
- Comprehensive research reports
- Multi-perspective analysis
- In-depth content creation
- Structured documents

**Use When:**
- Need thorough, well-researched content
- Multiple viewpoints important
- Creating reference material
- Quality and comprehensiveness critical

**Avoid When:**
- Simple content needs
- Single perspective sufficient
- Time constrained
- Cost constrained

**Example Use Cases:**
- "Create a comprehensive report on artificial intelligence in healthcare"
- "Write an in-depth guide to quantum computing"
- "Research and document the history of the internet"
- "Analyze climate change from multiple expert perspectives"

**Configuration:**
```python
agent = STORMAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "documentation": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    retrieval_tools={
        "search": search_tool,
        "wikipedia": wiki_tool,
        "scholar": academic_search
    },
    perspectives=[  # Optional custom perspectives
        {"name": "expert", "description": "Technical expert"},
        {"name": "beginner", "description": "Novice learner"}
    ]
)
```

**Pros:**
- Comprehensive, well-structured
- Multiple perspectives
- Source-backed content

**Cons:**
- Very expensive (many LLM calls)
- Very slow (complex workflow)
- Overkill for simple content

---

## Pattern Comparison Matrix

| Pattern | Tool Use | Cost | Speed | Quality | Complexity | Best For |
|---------|----------|------|-------|---------|------------|----------|
| **ReAct** | Yes | Medium | Fast | Good | Low | Q&A with tools |
| **Reflection** | No | Medium | Medium | High | Low | Quality content |
| **Plan & Solve** | No | Medium | Medium | Good | Medium | Multi-step tasks |
| **Reflexion** | Yes | High | Slow | Very High | Medium | Learning tasks |
| **LLM Compiler** | Yes | High | Fast | Good | High | Parallel execution |
| **REWOO** | Yes | Low | Fast | Good | Medium | Cost efficiency |
| **LATS** | Yes | Very High | Very Slow | Very High | High | Exploration |
| **Self-Discovery** | No | Medium | Medium | High | High | Novel problems |
| **STORM** | Yes | Very High | Very Slow | Very High | High | Research reports |

**Legend:**
- **Cost**: LLM API costs (Low = 1-3 calls, Medium = 3-7 calls, High = 7-15 calls, Very High = 15+ calls)
- **Speed**: Execution time (Fast = seconds, Medium = 10-30s, Slow = 30-60s, Very Slow = 1-5 minutes)
- **Quality**: Output quality potential
- **Complexity**: Implementation and understanding complexity

---

## Use Case Mapping

### By Domain

**Customer Service:**
- Simple Q&A: **ReAct** (with search/knowledge base tools)
- Complex issues: **Plan & Solve** (decompose into steps)

**Content Creation:**
- Blog posts: **Reflection**
- Research articles: **STORM**
- Marketing copy: **Reflection**
- Technical docs: **Plan & Solve** or **Reflection**

**Data Analysis:**
- Multi-source data: **LLM Compiler** (parallel queries)
- Sequential analysis: **Plan & Solve**
- Exploratory: **ReAct**

**Software Development:**
- Code generation: **Reflexion** (with tests)
- API design: **Plan & Solve**
- Algorithm design: **LATS** or **Self-Discovery**

**Research:**
- Quick facts: **ReAct** or **REWOO**
- Comprehensive reports: **STORM**
- Literature review: **STORM**
- Analysis: **Plan & Solve**

### By Task Complexity

**Simple (1-2 steps):**
- **ReAct**: If tools needed
- **Direct LLM**: If no tools needed

**Medium (3-5 steps):**
- **ReAct**: If tools needed
- **Plan & Solve**: If structured approach beneficial
- **Reflection**: If quality critical

**Complex (6+ steps):**
- **Plan & Solve**: Structured tasks
- **STORM**: Research tasks
- **Self-Discovery**: Novel problems
- **LATS**: Exploration needed

### By Budget

**Budget Conscious:**
- **REWOO**: Most efficient with tools
- **ReAct**: Good balance (limit iterations)
- **Reflection**: 1 cycle only

**Moderate Budget:**
- **ReAct**: Standard usage
- **Reflection**: 2-3 cycles
- **Plan & Solve**: Complex tasks
- **Self-Discovery**: Adaptive tasks

**Budget Not a Concern:**
- **LATS**: Explore all options
- **STORM**: Comprehensive research
- **Reflexion**: Multiple trials
- **LLM Compiler**: Parallel everything

---

## Decision Checklist

Use this checklist to select a pattern:

1. **Do I need tools/external data?**
   - Yes → Consider ReAct, LLM Compiler, REWOO, LATS
   - No → Consider Reflection, Plan & Solve, Self-Discovery, STORM

2. **What's my primary goal?**
   - Speed → ReAct, LLM Compiler, REWOO
   - Quality → Reflection, Reflexion, LATS, STORM
   - Cost → REWOO, ReAct (low iterations)
   - Coverage → STORM, LATS

3. **What's the task structure?**
   - Clear steps → Plan & Solve
   - Exploratory → ReAct, Self-Discovery
   - Multiple solutions → LATS
   - Research-oriented → STORM

4. **What's my budget?**
   - Low → REWOO, ReAct (3 iterations)
   - Medium → ReAct, Reflection, Plan & Solve
   - High → Reflexion, LLM Compiler, Self-Discovery
   - Very High → LATS, STORM

5. **Can I evaluate success programmatically?**
   - Yes → Reflexion
   - No → Other patterns

6. **Do tools run independently?**
   - Yes → LLM Compiler
   - No → ReAct, REWOO

---

## Common Mistakes

### Using LATS for Simple Tasks
**Problem**: LATS is expensive and complex
**Solution**: Use ReAct or Reflection instead

### Using ReAct When REWOO Would Work
**Problem**: More LLM calls than needed
**Solution**: If tool needs predictable, use REWOO

### Not Using Reflection for Quality Content
**Problem**: Settling for first-draft quality
**Solution**: Use Reflection with 1-2 cycles

### Using Plan & Solve Without Clear Steps
**Problem**: Forcing structure on unstructured task
**Solution**: Use ReAct or Self-Discovery instead

### Underestimating STORM Costs
**Problem**: Surprise API bills
**Solution**: Test with small topics first

---

## Still Unsure?

1. **Start Simple**: Begin with ReAct or Reflection
2. **Prototype**: Build quick POC with easiest pattern
3. **Measure**: Track cost, speed, quality
4. **Iterate**: Switch patterns based on metrics
5. **Ask**: Post in [GitHub Discussions](https://github.com/osok/agent-patterns/discussions)

---

## Further Reading

- [Pattern API Reference](../api/patterns.md) - Detailed pattern documentation
- [Examples](../examples/index.md) - See patterns in action
- [FAQ](../faq.md) - Common questions
- [Architecture](../concepts/architecture.md) - How patterns work
