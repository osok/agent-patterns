# Plan & Solve Agent Pattern

The **Plan & Solve** pattern separates planning from execution by first creating a comprehensive multi-step plan, then systematically executing each step to solve complex problems.

## Overview

**Best For**: Tasks that can be decomposed into clear, sequential steps

**Complexity**: ⭐⭐ Moderate (Simple two-phase approach)

**Cost**: $$ Medium (Planning + execution calls)

## When to Use Plan & Solve

### Ideal Use Cases

✅ **Structured problem solving**
- Agent creates detailed plan upfront
- Executes steps sequentially
- Each step builds on previous results

✅ **Multi-step workflows**
- Clear dependency between steps
- Benefits from upfront planning
- Systematic execution required

✅ **Complex calculations**
- Multi-stage mathematical problems
- Data processing pipelines
- Algorithm implementation

✅ **Research and analysis tasks**
- Information gathering workflows
- Systematic investigation
- Sequential reasoning chains

### When NOT to Use Plan & Solve

❌ **Dynamic environments** → Use ReAct for adaptive planning
❌ **Tool-based workflows** → Use ReAct or REWOO
❌ **Learning from failures** → Use Reflexion
❌ **One-step tasks** → Direct LLM call sufficient

## How Plan & Solve Works

### The Two-Phase Workflow

```
┌─────────────────────────────────────────┐
│                                         │
│  PHASE 1: PLANNING                      │
│                                         │
│  Task: "Create a marketing strategy"   │
│  ↓                                      │
│  Plan:                                  │
│  1. Analyze target market               │
│  2. Identify key messaging              │
│  3. Select marketing channels           │
│  4. Create content calendar             │
│  5. Define success metrics              │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  PHASE 2: EXECUTION                     │
│                                         │
│  Execute Step 1:                        │
│  "Target market: millennials interested │
│   in sustainable products..."           │
│  ↓                                      │
│  Execute Step 2:                        │
│  "Key messaging: eco-friendly,          │
│   affordable luxury..."                 │
│  ↓                                      │
│  Execute Step 3...                      │
│  Execute Step 4...                      │
│  Execute Step 5...                      │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  AGGREGATION                            │
│                                         │
│  Combine all step results into          │
│  comprehensive final answer             │
│                                         │
└─────────────────────────────────────────┘
```

### Theoretical Foundation

The Plan & Solve pattern is based on problem decomposition and structured execution principles:

1. **Planning reduces errors**: Thinking ahead prevents missteps
2. **Sequential execution**: Complex problems broken into manageable parts
3. **Accumulative progress**: Each step builds on previous work
4. **Clear structure**: Explicit plan makes process transparent

### Algorithm

```python
def plan_and_solve(task):
    """Simplified Plan & Solve algorithm"""

    # Phase 1: Planning
    plan = llm_create_plan(task)
    # plan = [step1, step2, step3, ...]

    # Phase 2: Execution
    step_results = []
    for step in plan:
        result = llm_execute_step(
            task=task,
            step=step,
            previous_results=step_results
        )
        step_results.append(result)

    # Aggregation
    final_answer = llm_aggregate(
        task=task,
        plan=plan,
        results=step_results
    )

    return final_answer
```

## API Reference

### Class: `PlanAndSolveAgent`

```python
from agent_patterns.patterns import PlanAndSolveAgent

agent = PlanAndSolveAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configs for "planning", "execution", and "documentation" roles |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict` | No | Override specific prompts programmatically |

#### LLM Roles

- **planning**: Used for creating the multi-step plan
- **execution**: Used for executing each step
- **documentation**: Used for aggregating results into final answer

#### Methods

**`run(input_data: str) -> str`**

Executes the Plan & Solve pattern on the given input.

- **Parameters**:
  - `input_data` (str): The task or problem to solve
- **Returns**: str - The final aggregated result
- **Raises**: ValueError if graph not built

**`build_graph() -> None`**

Builds the LangGraph state graph. Called automatically during initialization.

## Complete Examples

### Basic Usage

```python
from agent_patterns.patterns import PlanAndSolveAgent

# Configure LLMs
llm_configs = {
    "planning": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,  # Lower temp for consistent planning
    },
    "execution": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
    },
    "documentation": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
    }
}

# Create agent
agent = PlanAndSolveAgent(llm_configs=llm_configs)

# Solve multi-step problem
result = agent.run("""
Calculate the ROI for a software development project with:
- Initial investment: $500,000
- Development time: 12 months
- Expected revenue: $100,000/month after launch
- Operating costs: $30,000/month
- 3-year evaluation period

Provide detailed ROI calculation with explanation.
""")

print(result)
# Agent will:
# 1. Plan: Break down into steps (calculate costs, revenue, profit, ROI)
# 2. Execute: Run each calculation step
# 3. Aggregate: Combine into comprehensive ROI analysis
```

### With Custom Instructions

```python
# Add domain-specific planning guidance
research_guidelines = """
You are a research analyst. Follow these principles:

PLANNING:
- Break complex questions into researchable sub-questions
- Ensure logical dependency between steps
- Plan for both data gathering and analysis

EXECUTION:
- Be thorough and specific in each step
- Show your work and reasoning
- Build on results from previous steps
- Cite sources when applicable

AGGREGATION:
- Synthesize findings coherently
- Address the original question directly
- Highlight key insights
- Note limitations or uncertainties
"""

agent = PlanAndSolveAgent(
    llm_configs=llm_configs,
    custom_instructions=research_guidelines
)

result = agent.run("""
Research question: What factors contributed to the success of
remote work adoption during 2020-2023, and what are the long-term
implications for office real estate?
""")
```

### With Prompt Overrides

```python
# Customize planning and execution prompts
overrides = {
    "PlanStep": {
        "system_prompt": """You are an expert planner who creates detailed,
actionable steps for complex problems. Each step should be:
- Specific and actionable
- Dependent on previous steps where appropriate
- Achievable with available information
- Contributing to the final solution""",
        "user_prompt": """Task: {task}

Create a detailed step-by-step plan. Number each step clearly.
Make sure steps are in logical order and build on each other.

Your plan:"""
    },
    "ExecuteStep": {
        "system_prompt": "You are a meticulous executor who completes tasks thoroughly.",
        "user_prompt": """Original task: {task}

Current step: {step}

Results from previous steps:
{previous_results}

Execute this step with detail and precision. Show your work.

Your result:"""
    },
    "AggregateStep": {
        "system_prompt": "You synthesize information into clear, comprehensive answers.",
        "user_prompt": """Task: {task}

All step results:
{results}

Combine these results into a well-structured final answer that fully
addresses the original task. Organize logically and highlight key points.

Your final answer:"""
    }
}

agent = PlanAndSolveAgent(
    llm_configs=llm_configs,
    prompt_overrides=overrides
)

result = agent.run("""
Design a database schema for an e-commerce platform that supports:
- User accounts and authentication
- Product catalog with categories
- Shopping cart and checkout
- Order history and tracking
- Reviews and ratings
""")
```

## Customizing Prompts

### Understanding Plan & Solve Prompts

The pattern uses three prompt templates:

1. **PlanStep**: Creates the multi-step plan
   - Analyzes the task
   - Breaks it into sequential steps
   - Ensures logical flow

2. **ExecuteStep**: Executes individual steps
   - Takes current step description
   - Has access to previous step results
   - Produces detailed step output

3. **AggregateStep**: Combines results
   - Reviews all step outputs
   - Synthesizes coherent final answer
   - Addresses original task

### Method 1: Custom Instructions

```python
agent = PlanAndSolveAgent(
    llm_configs=llm_configs,
    custom_instructions="""
    PLANNING STYLE: Create 4-7 clear, actionable steps
    EXECUTION STYLE: Be thorough and show reasoning
    AGGREGATION STYLE: Create executive summary + detailed findings
    """
)
```

### Method 2: Prompt Overrides

```python
# Customize for code generation
code_overrides = {
    "PlanStep": {
        "user_prompt": """Task: {task}

Create a coding plan with these steps:
1. Define data structures/classes
2. Implement core functionality
3. Add error handling
4. Write tests
5. Add documentation

Your detailed plan:"""
    },
    "ExecuteStep": {
        "user_prompt": """Coding task: {task}

Step: {step}

Previous code:
{previous_results}

Write the code for this step with:
- Clear comments
- Proper error handling
- Type hints (if applicable)

Your code:"""
    }
}

agent = PlanAndSolveAgent(
    llm_configs=llm_configs,
    prompt_overrides=code_overrides
)
```

### Method 3: Custom Prompt Directory

```bash
my_prompts/
└── PlanAndSolveAgent/
    ├── PlanStep/
    │   ├── system_prompt.md
    │   └── user_prompt.md
    ├── ExecuteStep/
    │   ├── system_prompt.md
    │   └── user_prompt.md
    └── AggregateStep/
        ├── system_prompt.md
        └── user_prompt.md
```

## Setting Agent Goals

### Via Task Description

Provide clear, structured task:

```python
# Well-defined requirements
agent.run("""
Project: Customer Churn Prediction System

Requirements:
1. Analyze customer behavior data
2. Identify key churn indicators
3. Propose ML model approach
4. Define evaluation metrics
5. Create implementation roadmap

Deliverable: Technical specification document
""")
```

### Via Custom Instructions

```python
agent = PlanAndSolveAgent(
    llm_configs=llm_configs,
    custom_instructions="""
    GOAL: Produce actionable, implementation-ready solutions

    PLANNING REQUIREMENTS:
    - 5-8 concrete steps
    - Clear dependencies
    - Realistic scope per step

    EXECUTION REQUIREMENTS:
    - Specific, not generic
    - Include examples where relevant
    - Reference previous steps

    FINAL OUTPUT REQUIREMENTS:
    - Start with executive summary
    - Organize into logical sections
    - Include next steps/recommendations
    """
)
```

## Advanced Usage

### Role-Specific Models

```python
# Use different models for different phases
llm_configs = {
    "planning": {
        "provider": "openai",
        "model": "gpt-4",  # Strong model for planning
        "temperature": 0.2,  # Low temp for consistent plans
    },
    "execution": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper for execution
        "temperature": 0.7,
    },
    "documentation": {
        "provider": "openai",
        "model": "gpt-4",  # Strong model for synthesis
        "temperature": 0.7,
    }
}

agent = PlanAndSolveAgent(llm_configs=llm_configs)
```

### Custom Step Execution Logic

```python
class CustomPlanAndSolveAgent(PlanAndSolveAgent):
    def _run_single_step(self, step, state):
        """Override to add custom execution logic"""
        step_description = step.get("step_description", "")

        # Add custom preprocessing
        if "calculate" in step_description.lower():
            # Use specialized calculation handling
            return self._execute_calculation_step(step, state)
        elif "research" in step_description.lower():
            # Use research-specific approach
            return self._execute_research_step(step, state)
        else:
            # Default execution
            return super()._run_single_step(step, state)

    def _execute_calculation_step(self, step, state):
        """Custom logic for calculation steps"""
        # Implementation here
        pass

agent = CustomPlanAndSolveAgent(llm_configs=llm_configs)
```

### Plan Validation

```python
class ValidatedPlanAndSolveAgent(PlanAndSolveAgent):
    def _generate_plan(self, state):
        """Override to validate plan before execution"""
        state = super()._generate_plan(state)

        plan = state.get("plan", [])

        # Validate plan quality
        if len(plan) < 2:
            # Plan too short, regenerate
            return super()._generate_plan(state)

        if len(plan) > 15:
            # Plan too long, might be too granular
            # Could prompt for consolidation
            pass

        return state

agent = ValidatedPlanAndSolveAgent(llm_configs=llm_configs)
```

## Performance Considerations

### Cost Optimization

Plan & Solve cost calculation:
- Planning: 1 LLM call
- Execution: N calls (N = number of steps)
- Aggregation: 1 call
- **Total**: N + 2 calls

**Typical**: 6-8 LLM calls for average task

```python
# Optimize by using cheaper models for execution
llm_configs = {
    "planning": {"provider": "openai", "model": "gpt-4"},
    "execution": {"provider": "openai", "model": "gpt-3.5-turbo"},  # Cheaper
    "documentation": {"provider": "openai", "model": "gpt-4"}
}

# Encourage concise plans via custom instructions
custom_instructions = """
PLANNING: Create 4-6 high-level steps (avoid over-granularity)
"""
```

### Speed Optimization

```python
# Faster models for time-sensitive tasks
llm_configs = {
    "planning": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Faster planning
        "temperature": 0.3,
    },
    "execution": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
    },
    "documentation": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
    }
}
```

## Comparison with Other Patterns

| Aspect | Plan & Solve | ReAct | Self-Discovery |
|--------|--------------|-------|----------------|
| **Planning** | Upfront, complete | Adaptive per step | Dynamic module selection |
| **Execution** | Sequential steps | Tool-based actions | Reasoning strategies |
| **Flexibility** | Fixed plan | Highly adaptive | Moderate |
| **Tools** | Not supported | Core feature | Not supported |
| **Best For** | Known workflows | Dynamic problems | Complex reasoning |
| **Cost** | Medium | Medium | High |

## Common Pitfalls

### 1. Too Granular Plans

❌ **Bad**: Plan with 20+ tiny steps
```python
# Results in excessive LLM calls and fragmented execution
```

✅ **Good**: 4-8 meaningful steps
```python
custom_instructions = """
Create 4-8 substantial steps. Each step should accomplish something meaningful.
Avoid breaking tasks into trivial micro-steps.
"""
```

### 2. Steps Without Dependencies

❌ **Bad**: Independent steps that don't build on each other
```python
# Plan:
# 1. Research topic A
# 2. Research topic B (unrelated)
# 3. Research topic C (unrelated)
# → Should use parallel execution, not Plan & Solve
```

✅ **Good**: Sequential, dependent steps
```python
# Plan:
# 1. Define requirements
# 2. Design architecture (based on requirements)
# 3. Identify implementation challenges (based on architecture)
# 4. Propose solutions (based on challenges)
```

### 3. Vague Step Descriptions

❌ **Bad**: Generic step descriptions
```python
# Step 1: Analyze
# Step 2: Decide
# Step 3: Implement
```

✅ **Good**: Specific, actionable steps
```python
overrides = {
    "PlanStep": {
        "user_prompt": """Task: {task}

Create specific, actionable steps. Each step should clearly state:
- What will be done
- What output is expected

Your detailed plan:"""
    }
}
```

### 4. Ignoring Previous Results

❌ **Bad**: Steps don't use previous outputs

✅ **Good**: Ensure execution accesses context
```python
# ExecuteStep prompt already includes {previous_results}
# Make sure your custom prompts do too if overriding
```

## Troubleshooting

### Plans Are Too Short

**Symptom**: Agent creates 1-2 step plans for complex tasks

**Solutions**:
```python
# Add guidance in custom instructions
custom_instructions = """
PLANNING: Create comprehensive plans with 5-8 steps for complex tasks.
Break down the problem thoroughly.
"""

# Or override PlanStep prompt
overrides = {
    "PlanStep": {
        "user_prompt": """Task: {task}

This is a complex task. Create a detailed plan with 6-10 specific steps.

Your plan:"""
    }
}
```

### Steps Don't Build on Each Other

**Symptom**: Execution ignores previous results

**Solutions**:
```python
# Emphasize continuity in ExecuteStep
overrides = {
    "ExecuteStep": {
        "user_prompt": """Task: {task}
Step: {step}

Previous results:
{previous_results}

Execute this step, explicitly building on and referencing previous results where relevant.

Your result:"""
    }
}
```

### Poor Final Synthesis

**Symptom**: Aggregation doesn't coherently combine results

**Solutions**:
```python
# Improve AggregateStep prompt
overrides = {
    "AggregateStep": {
        "user_prompt": """Task: {task}

Step-by-step results:
{results}

Create a comprehensive final answer that:
1. Synthesizes all step results into a coherent narrative
2. Directly addresses the original task
3. Highlights key findings
4. Provides clear structure (use headings if appropriate)

Your final answer:"""
    }
}
```

## Next Steps

- Try the [complete examples](../examples/plan-and-solve-examples.md)
- Learn about [ReAct](react.md) for adaptive planning with tools
- Explore [Self-Discovery](self-discovery.md) for complex reasoning
- Read about [prompt customization](../guides/prompt-customization.md)

## References

- Related to classic problem decomposition in computer science
- Inspired by hierarchical planning in AI systems
- Similar to [Chain-of-Thought](https://arxiv.org/abs/2201.11903) with explicit planning phase
