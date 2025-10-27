# Self-Discovery Agent Pattern

The **Self-Discovery** pattern enables agents to dynamically select and adapt reasoning strategies from a library of problem-solving heuristics, creating customized reasoning plans for each unique task.

## Overview

**Best For**: Complex reasoning tasks requiring multiple problem-solving approaches

**Complexity**: ⭐⭐⭐ Advanced (Sophisticated meta-reasoning)

**Cost**: $$$ Higher (Multiple LLM calls for discovery, adaptation, and execution)

## When to Use Self-Discovery

### Ideal Use Cases

✅ **Multi-faceted problems**
- Agent discovers relevant reasoning approaches
- Adapts general strategies to specific context
- Combines multiple perspectives for comprehensive solutions

✅ **Novel problem domains**
- No predetermined approach exists
- Agent selects appropriate reasoning modules
- Customizes strategy based on task characteristics

✅ **Complex analytical tasks**
- Requires diverse reasoning methods (analogical, first principles, etc.)
- Benefits from structured reasoning plan
- Needs systematic approach to decomposition

✅ **Strategic planning**
- Analyzes problem from multiple angles
- Selects relevant planning heuristics
- Executes customized reasoning workflow

### When NOT to Use Self-Discovery

❌ **Simple queries** → Use direct LLM or ReAct
❌ **Tasks with known solutions** → Use Plan & Solve
❌ **Tool-based workflows** → Use ReAct or REWOO
❌ **Speed-critical tasks** → Meta-reasoning adds overhead

## How Self-Discovery Works

### The Discovery-Adaptation-Execution Cycle

```
┌─────────────────────────────────────────┐
│                                         │
│  1. DISCOVER: Select relevant modules   │
│     Library: [break_down, analogical,   │
│              first_principles, ...]     │
│     Selected: [break_down,              │
│                first_principles]        │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  2. ADAPT: Customize for task           │
│     break_down → "Decompose the system  │
│     into: UI, API, Database layers"     │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  3. PLAN: Create reasoning sequence     │
│     Step 1: Apply break_down strategy   │
│     Step 2: Apply first_principles      │
│     Step 3: Synthesize insights         │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  4. EXECUTE: Run each reasoning step    │
│     Execute step 1... execute step 2... │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  5. SYNTHESIZE: Combine results         │
│     Integrate all reasoning outputs     │
│     into coherent final answer          │
│                                         │
└─────────────────────────────────────────┘
```

### Theoretical Foundation

Based on the paper ["Self-Discover: Large Language Models Self-Compose Reasoning Structures"](https://arxiv.org/abs/2402.03620). Key insights:

1. **Meta-reasoning**: Agent reasons about which reasoning approaches to use
2. **Adaptive strategy**: Different tasks benefit from different heuristics
3. **Structured thinking**: Explicit reasoning plan improves outcomes
4. **Composability**: Combines multiple reasoning modules effectively

### Algorithm

```python
def self_discovery(task, module_library, max_modules=3):
    """Simplified Self-Discovery algorithm"""

    # Stage 1: Discover relevant modules
    selected_modules = llm_select_modules(
        task=task,
        modules=module_library,
        max_select=max_modules
    )

    # Stage 2: Adapt modules to task
    adapted_modules = []
    for module in selected_modules:
        adapted = llm_adapt_module(
            task=task,
            module=module
        )
        adapted_modules.append(adapted)

    # Stage 3: Create reasoning plan
    reasoning_plan = llm_create_plan(
        task=task,
        adapted_modules=adapted_modules
    )

    # Stage 4: Execute plan steps
    step_results = []
    for step in reasoning_plan:
        result = llm_execute_step(
            task=task,
            step=step,
            previous_results=step_results
        )
        step_results.append(result)

    # Stage 5: Synthesize final answer
    final_answer = llm_synthesize(
        task=task,
        reasoning_steps=step_results
    )

    return final_answer
```

## API Reference

### Class: `SelfDiscoveryAgent`

```python
from agent_patterns.patterns import SelfDiscoveryAgent

agent = SelfDiscoveryAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    reasoning_modules: Optional[List[Dict[str, str]]] = None,
    max_selected_modules: int = 3,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configs for "thinking" and "execution" roles |
| `reasoning_modules` | `List[Dict]` | No | Custom reasoning module library (uses defaults if None) |
| `max_selected_modules` | `int` | No | Max modules to select per task (default: 3) |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict` | No | Override specific prompts programmatically |

#### Default Reasoning Modules

The agent includes 10 default reasoning modules:

1. **break_down_problem**: Decompose into sub-problems
2. **identify_constraints**: Analyze requirements and limitations
3. **analogical_reasoning**: Find similar problems and apply lessons
4. **first_principles**: Reason from fundamental truths
5. **step_by_step**: Proceed systematically through the problem
6. **pros_and_cons**: Evaluate different approaches
7. **critical_analysis**: Examine assumptions and evidence
8. **pattern_recognition**: Identify patterns and trends
9. **hypothesis_testing**: Form and test hypotheses
10. **visualization**: Create mental models or diagrams

#### LLM Roles

- **thinking**: Used for discovery, adaptation, planning, and synthesis
- **execution**: Used for executing each reasoning step

#### Methods

**`run(input_data: str) -> str`**

Executes the Self-Discovery pattern on the given input.

- **Parameters**:
  - `input_data` (str): The task or problem to solve
- **Returns**: str - The synthesized final answer
- **Raises**: ValueError if graph not built

**`build_graph() -> None`**

Builds the LangGraph state graph. Called automatically during initialization.

## Complete Examples

### Basic Usage

```python
from agent_patterns.patterns import SelfDiscoveryAgent

# Configure LLMs
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
    },
    "execution": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
    }
}

# Create agent with default reasoning modules
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    max_selected_modules=3
)

# Solve complex reasoning problem
result = agent.run("""
Design a sustainable urban transportation system for a city of 2 million people.
Consider environmental impact, cost, efficiency, and user experience.
""")

print(result)
# Agent will:
# 1. Select relevant modules (e.g., break_down, constraints, pros_and_cons)
# 2. Adapt them to urban transportation context
# 3. Create reasoning plan
# 4. Execute each step
# 5. Synthesize comprehensive solution
```

### With Custom Reasoning Modules

```python
# Define domain-specific reasoning modules
custom_modules = [
    {
        "name": "stakeholder_analysis",
        "description": "Identify all stakeholders and their interests",
        "template": "For '{task}', identify key stakeholders and analyze their needs and constraints"
    },
    {
        "name": "risk_assessment",
        "description": "Evaluate potential risks and mitigation strategies",
        "template": "Identify risks in '{task}' and develop mitigation approaches"
    },
    {
        "name": "resource_optimization",
        "description": "Optimize resource allocation and utilization",
        "template": "Analyze resource constraints for '{task}' and propose optimal allocation"
    },
    {
        "name": "scalability_analysis",
        "description": "Assess how solution scales with growth",
        "template": "Evaluate scalability of '{task}' under different growth scenarios"
    },
    {
        "name": "competitive_analysis",
        "description": "Compare with alternative approaches",
        "template": "Compare different approaches to '{task}' and identify best option"
    }
]

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    reasoning_modules=custom_modules,
    max_selected_modules=3
)

result = agent.run("""
Develop a go-to-market strategy for a B2B SaaS product
targeting enterprise customers in the healthcare industry.
""")
```

### With Custom Instructions

```python
# Add guidance for reasoning selection and execution
business_strategy_instructions = """
You are a business strategy consultant. When selecting reasoning modules:
- Prioritize data-driven approaches
- Consider both qualitative and quantitative factors
- Balance short-term feasibility with long-term vision

When executing reasoning steps:
- Use concrete examples from real companies
- Provide actionable recommendations
- Consider both opportunities and risks
- Reference industry best practices

When synthesizing:
- Create a structured action plan
- Identify key metrics for success
- Highlight critical dependencies
"""

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    max_selected_modules=4,
    custom_instructions=business_strategy_instructions
)

result = agent.run("""
Create a digital transformation roadmap for a traditional
retail company facing competition from e-commerce.
""")
```

### With Prompt Overrides

```python
# Customize how modules are discovered and adapted
overrides = {
    "DiscoverModules": {
        "system": """You are an expert in selecting problem-solving strategies.
Analyze the task deeply and choose the most relevant reasoning approaches.""",
        "user": """Task: {task}

Available reasoning modules:
{modules}

Select up to {max_modules} modules that are MOST relevant for this specific task.
Focus on modules that will provide unique, valuable perspectives.

For each selected module, output:
SELECTED: <module_name>

Your selections:"""
    },
    "AdaptModules": {
        "system": "You specialize in customizing general strategies for specific contexts.",
        "user": """Task: {task}

Module: {module_name}
Description: {module_description}
Template: {module_template}

Adapt this module specifically for the task. Be concrete and specific.
How would you apply this reasoning approach to this exact problem?

Adapted strategy:"""
    }
}

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=overrides,
    max_selected_modules=3
)
```

## Customizing Reasoning Modules

### Creating Domain-Specific Modules

```python
# Scientific research modules
research_modules = [
    {
        "name": "literature_review",
        "description": "Survey existing research and identify gaps",
        "template": "Review relevant literature for '{task}' and identify research gaps"
    },
    {
        "name": "hypothesis_formation",
        "description": "Formulate testable hypotheses",
        "template": "Generate testable hypotheses for '{task}'"
    },
    {
        "name": "experimental_design",
        "description": "Design experiments to test hypotheses",
        "template": "Design experiments to investigate '{task}'"
    },
    {
        "name": "data_analysis",
        "description": "Analyze data and draw conclusions",
        "template": "Analyze data patterns in '{task}' and draw evidence-based conclusions"
    }
]

# Engineering design modules
engineering_modules = [
    {
        "name": "requirements_analysis",
        "description": "Define functional and non-functional requirements",
        "template": "Specify detailed requirements for '{task}'"
    },
    {
        "name": "architecture_design",
        "description": "Design system architecture and components",
        "template": "Design system architecture for '{task}'"
    },
    {
        "name": "trade_off_analysis",
        "description": "Evaluate engineering trade-offs",
        "template": "Analyze trade-offs between different design choices for '{task}'"
    }
]

# Choose based on domain
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    reasoning_modules=research_modules  # or engineering_modules
)
```

### Module Structure

Each module requires three fields:

```python
module = {
    "name": "unique_identifier",  # Used in selection output
    "description": "What this reasoning approach does",  # Helps agent select
    "template": "How to apply it to '{task}'"  # Gets filled with actual task
}
```

## Setting Agent Goals

### Via Task Description

Provide clear problem statement:

```python
# Well-defined task
agent.run("""
Problem: Our mobile app has 40% user churn in the first week.

Context:
- 100K downloads/month
- Average session: 3 minutes
- Main competitors: AppA (15% churn), AppB (20% churn)

Goal: Reduce churn to under 25% within 3 months

Constraints:
- Limited development resources (2 engineers)
- $50K marketing budget
- Must maintain current feature set

Question: What strategy should we implement?
""")
```

### Via Custom Instructions

Set persistent reasoning guidelines:

```python
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions="""
    GOAL: Provide comprehensive, actionable strategic recommendations

    REASONING APPROACH:
    - Select modules that complement each other
    - Ensure both analytical and creative perspectives
    - Ground reasoning in practical constraints

    OUTPUT REQUIREMENTS:
    - Specific, measurable recommendations
    - Timeline and resource estimates
    - Risk factors and mitigation strategies
    - Success metrics
    """
)
```

### Via System Prompt Override

Configure each stage:

```python
overrides = {
    "DiscoverModules": {
        "system": """You select reasoning strategies to maximize solution quality.
Goal: Choose modules that provide diverse, complementary perspectives."""
    },
    "ExecuteStep": {
        "system": """You execute reasoning steps with rigor and depth.
Goal: Generate insights that are specific, actionable, and evidence-based."""
    },
    "SynthesizeOutput": {
        "system": """You synthesize insights into coherent strategic recommendations.
Goal: Create an actionable plan with clear priorities and success metrics."""
    }
}
```

## Advanced Usage

### Adjusting Module Selection

```python
# Select more modules for complex tasks
comprehensive_agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    max_selected_modules=5  # More diverse perspectives
)

# Select fewer for focused analysis
focused_agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    max_selected_modules=2  # Streamlined reasoning
)
```

### Combining Default and Custom Modules

```python
from agent_patterns.patterns.self_discovery_agent import DEFAULT_REASONING_MODULES

# Add custom modules to defaults
all_modules = DEFAULT_REASONING_MODULES + [
    {
        "name": "ethical_analysis",
        "description": "Evaluate ethical implications and considerations",
        "template": "Analyze ethical dimensions of '{task}'"
    },
    {
        "name": "sustainability_check",
        "description": "Assess environmental and social sustainability",
        "template": "Evaluate sustainability aspects of '{task}'"
    }
]

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    reasoning_modules=all_modules,
    max_selected_modules=4
)
```

### Role-Specific LLM Configurations

```python
# Use stronger model for meta-reasoning, standard for execution
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4",  # Stronger for discovery/planning
        "temperature": 0.7,
    },
    "execution": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper for execution steps
        "temperature": 0.7,
    }
}
```

## Performance Considerations

### Cost Optimization

Self-Discovery makes many LLM calls:

**Per task cost**:
- Discover modules: 1 call
- Adapt modules: N calls (where N = selected modules)
- Plan reasoning: 1 call
- Execute steps: M calls (where M = steps in plan)
- Synthesize: 1 call
- **Total**: ~7-12 LLM calls for typical task

**Optimization strategies**:

```python
# 1. Reduce max_selected_modules
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    max_selected_modules=2  # Fewer modules = fewer calls
)

# 2. Use cheaper model for execution
llm_configs = {
    "thinking": {"provider": "openai", "model": "gpt-4"},
    "execution": {"provider": "openai", "model": "gpt-3.5-turbo"}
}

# 3. Create focused module libraries (fewer options to consider)
focused_modules = [
    # Only 4-5 most relevant modules for your domain
]
```

### When to Use vs Other Patterns

| Task Type | Best Pattern | Reason |
|-----------|-------------|---------|
| Complex reasoning, no tools | Self-Discovery | ✅ Leverages diverse reasoning |
| Simple reasoning | Direct LLM | ❌ Self-Discovery overhead unnecessary |
| Tool-based workflows | ReAct, REWOO | ❌ Modules don't replace tools |
| Learning from failures | Reflexion | ❌ Self-Discovery doesn't maintain memory |
| Predetermined steps | Plan & Solve | ❌ Self-Discovery for novel problems |

## Comparison with Other Patterns

| Aspect | Self-Discovery | Plan & Solve | ReAct |
|--------|---------------|--------------|-------|
| **Planning** | Dynamic module selection | Fixed planning phase | Adaptive per iteration |
| **Reasoning** | Multi-strategy | Linear steps | Thought-action |
| **Tools** | Not supported | Not supported | Core feature |
| **Best For** | Complex reasoning | Structured tasks | Dynamic tool use |
| **Cost** | High | Medium | Medium |
| **Flexibility** | Very high | Medium | High |

## Common Pitfalls

### 1. Too Many Modules

❌ **Bad**: Overwhelming the agent with too many options
```python
huge_library = [/* 20+ modules */]
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    reasoning_modules=huge_library,
    max_selected_modules=8  # Too many
)
```

✅ **Good**: Curated, relevant module library
```python
focused_library = [/* 6-8 most relevant modules */]
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    reasoning_modules=focused_library,
    max_selected_modules=3
)
```

### 2. Generic Module Descriptions

❌ **Bad**: Vague descriptions
```python
{
    "name": "analyze",
    "description": "Analyze the problem",
    "template": "Analyze '{task}'"
}
```

✅ **Good**: Specific, actionable descriptions
```python
{
    "name": "stakeholder_analysis",
    "description": "Identify stakeholders, their goals, and potential conflicts",
    "template": "For '{task}', list key stakeholders, their objectives, and areas of alignment/conflict"
}
```

### 3. Using for Simple Tasks

❌ **Bad**: Over-engineering simple queries
```python
agent.run("What is the capital of France?")  # Overkill!
```

✅ **Good**: Use for genuinely complex reasoning
```python
agent.run("""
Design a comprehensive climate change mitigation strategy
for a mid-sized industrial city, balancing economic growth
with environmental sustainability.
""")
```

### 4. Ignoring Module Adaptation

❌ **Bad**: Skipping adaptation in custom implementation
```python
# Directly using generic modules without task-specific customization
```

✅ **Good**: Let agent adapt modules to context
```python
# Trust the adaptation phase - it makes generic modules task-specific
agent = SelfDiscoveryAgent(llm_configs=llm_configs)  # Uses adaptation
```

## Troubleshooting

### Poor Module Selection

**Symptom**: Agent selects irrelevant modules

**Solutions**:
```python
# 1. Improve module descriptions
modules = [
    {
        "name": "financial_analysis",
        "description": "Evaluate financial viability, ROI, and cost-benefit. Use for business/financial decisions.",
        "template": "..."
    }
]

# 2. Add custom selection instructions
custom_instructions = """
When selecting modules, prioritize those that:
1. Directly address the core problem
2. Provide complementary perspectives
3. Are specific to the task domain
"""

# 3. Override DiscoverModules prompt for better selection
```

### Weak Reasoning Steps

**Symptom**: Execution steps are shallow or generic

**Solutions**:
```python
# 1. Add execution guidance
custom_instructions = """
When executing reasoning steps:
- Provide specific examples and evidence
- Show detailed work and calculations
- Reference concrete data points
- Explain reasoning clearly
"""

# 2. Use stronger LLM for execution
llm_configs = {
    "thinking": {"provider": "openai", "model": "gpt-4"},
    "execution": {"provider": "openai", "model": "gpt-4"}  # Not 3.5
}
```

### Synthesis Doesn't Integrate Well

**Symptom**: Final answer doesn't coherently combine step results

**Solutions**:
```python
# Override synthesis prompt
overrides = {
    "SynthesizeOutput": {
        "system": "You are an expert synthesizer. Create cohesive answers that integrate all reasoning.",
        "user": """Task: {task}

Reasoning steps and results:
{reasoning_steps}

Synthesize these into a comprehensive, well-structured answer that:
1. Integrates insights from all steps
2. Resolves any contradictions
3. Provides actionable recommendations
4. Includes supporting evidence

Your synthesis:"""
    }
}
```

## Next Steps

- Try the [complete examples](../examples/self-discovery-examples.md)
- Learn about [Plan & Solve](plan-and-solve.md) for simpler structured reasoning
- Explore [Reflexion](reflexion.md) for learning from multiple trials
- Read the [original paper](https://arxiv.org/abs/2402.03620)

## References

- Original paper: [Self-Discover: Large Language Models Self-Compose Reasoning Structures](https://arxiv.org/abs/2402.03620)
- Related work on [Chain-of-Thought prompting](https://arxiv.org/abs/2201.11903)
- [Reasoning strategies in cognitive science](https://en.wikipedia.org/wiki/Problem_solving#Techniques)
