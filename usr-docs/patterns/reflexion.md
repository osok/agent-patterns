# Reflexion Agent Pattern

The **Reflexion** pattern enables agents to learn from failures across multiple trials by maintaining a persistent reflection memory. Unlike simple reflection, Reflexion performs multiple attempts, stores insights from each trial, and uses accumulated knowledge to improve subsequent attempts.

## Overview

**Best For**: Tasks requiring learning from failures and iterative improvement

**Complexity**: ⭐⭐⭐ Advanced (Multi-trial learning with memory)

**Cost**: $$$$ Very High (Multiple trials × multiple LLM calls per trial)

## When to Use Reflexion

### Ideal Use Cases

✅ **Problem-solving with trial and error**
- Agent attempts solution
- Evaluates success/failure
- Learns from mistakes
- Tries again with improved approach

✅ **Optimization tasks**
- Multiple attempts to find best solution
- Each trial provides learning
- Memory guides future strategies
- Converges toward optimal approach

✅ **Complex puzzles and challenges**
- Initial attempts may fail
- Insights from failures inform next try
- Persistent memory tracks what doesn't work
- Gradual refinement leads to solution

✅ **Adaptive strategy development**
- Explores different approaches
- Learns which strategies succeed
- Builds knowledge base over trials
- Applies lessons to new attempts

### When NOT to Use Reflexion

❌ **One-shot tasks** → Use Reflection or direct LLM
❌ **No clear success/failure criteria** → Hard to evaluate trials
❌ **Cost-sensitive applications** → Many trials = high cost
❌ **Time-critical tasks** → Multiple trials take time

## How Reflexion Works

### The Multi-Trial Learning Cycle

```
┌─────────────────────────────────────────┐
│  TRIAL 1                                │
│                                         │
│  1. PLAN: Create initial approach       │
│     (no prior memory)                   │
│  2. EXECUTE: Try the approach           │
│  3. EVALUATE: Failed                    │
│  4. REFLECT: "Approach X didn't work    │
│              because Y. Try Z instead"  │
│  5. UPDATE MEMORY: Store insight        │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  TRIAL 2                                │
│                                         │
│  1. PLAN: Using memory from Trial 1     │
│     "Avoid approach X, try Z instead"   │
│  2. EXECUTE: Try improved approach      │
│  3. EVALUATE: Failed (but closer)       │
│  4. REFLECT: "Z was better than X, but  │
│              needs adjustment W"        │
│  5. UPDATE MEMORY: Add new insight      │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  TRIAL 3                                │
│                                         │
│  1. PLAN: Using memory from Trials 1-2  │
│     "Apply Z with adjustment W"         │
│  2. EXECUTE: Try refined approach       │
│  3. EVALUATE: Success!                  │
│  4. RETURN: Successful solution         │
│                                         │
└─────────────────────────────────────────┘
```

### Theoretical Foundation

Based on the paper ["Reflexion: Language Agents with Verbal Reinforcement Learning"](https://arxiv.org/abs/2303.11366). Key concepts:

1. **Verbal reinforcement learning**: Learn from natural language feedback
2. **Persistent memory**: Insights accumulate across trials
3. **Self-evaluation**: Agent judges its own success/failure
4. **Iterative refinement**: Each trial improves on previous attempts

### Algorithm

```python
def reflexion_loop(task, max_trials=3):
    """Simplified Reflexion algorithm"""
    reflection_memory = []

    for trial in range(max_trials):
        # 1. Plan using accumulated memory
        plan = llm_plan_with_memory(task, reflection_memory)

        # 2. Execute the plan
        outcome = llm_execute(task, plan)

        # 3. Evaluate success/failure
        evaluation = llm_evaluate(task, outcome)

        if evaluation == "success":
            return outcome

        # 4. Reflect on what went wrong
        reflection = llm_reflect(task, plan, outcome, evaluation)

        # 5. Add to memory for next trial
        reflection_memory.append(reflection)

    # Max trials reached, return best attempt
    return generate_final_answer(task, reflection_memory, outcome)
```

## API Reference

### Class: `ReflexionAgent`

```python
from agent_patterns.patterns import ReflexionAgent

agent = ReflexionAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    max_trials: int = 3,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configs for "thinking", "reflection", "execution", and "documentation" roles |
| `max_trials` | `int` | No | Maximum number of trial attempts (default: 3) |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict` | No | Override specific prompts programmatically |

#### LLM Roles

- **thinking**: Used for planning with memory
- **execution**: Used for executing each trial
- **reflection**: Used for evaluating outcomes and generating insights
- **documentation**: Used for generating final answer when trials exhausted

#### Methods

**`run(input_data: str) -> str`**

Executes the Reflexion pattern on the given input.

- **Parameters**:
  - `input_data` (str): The task or problem to solve
- **Returns**: str - The final answer (successful outcome or best attempt)
- **Raises**: ValueError if graph not built

**`build_graph() -> None`**

Builds the LangGraph state graph. Called automatically during initialization.

## Complete Examples

### Basic Usage

```python
from agent_patterns.patterns import ReflexionAgent

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
    },
    "reflection": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,  # Lower temp for consistent evaluation
    },
    "documentation": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
    }
}

# Create agent
agent = ReflexionAgent(
    llm_configs=llm_configs,
    max_trials=3
)

# Solve challenging problem
result = agent.run("""
Puzzle: You have 12 coins that look identical. One is counterfeit
and weighs slightly different (either heavier or lighter).
Using a balance scale only 3 times, identify the counterfeit coin
AND determine if it's heavier or lighter.

Provide step-by-step solution.
""")

print(result)
# Agent will:
# Trial 1: Attempt a solution, likely fail or have gaps
# Trial 2: Learn from Trial 1 mistakes, try improved approach
# Trial 3: Apply accumulated insights, find correct solution
```

### With Custom Instructions

```python
# Add domain-specific learning guidance
debugging_instructions = """
You are debugging code by trial and error. Follow these principles:

PLANNING WITH MEMORY:
- Review what you've tried before
- Don't repeat failed approaches
- Build on partial successes
- Try systematic variations

EXECUTION:
- Be precise in implementing the plan
- Document what you're testing

EVALUATION:
- Check if code runs without errors
- Verify output matches expected results
- Identify specific failure points

REFLECTION:
- Analyze why the approach failed
- Identify what worked and what didn't
- Generate specific, actionable insights
- Propose concrete changes for next trial
"""

agent = ReflexionAgent(
    llm_configs=llm_configs,
    max_trials=5,  # Allow more trials for complex debugging
    custom_instructions=debugging_instructions
)

result = agent.run("""
Debug this Python function that should find the longest palindromic substring:

def longest_palindrome(s):
    result = ""
    for i in range(len(s)):
        for j in range(i, len(s)):
            if s[i:j] == s[i:j][::-1]:
                result = max(result, s[i:j])
    return result

Test cases:
- longest_palindrome("babad") should return "bab" or "aba"
- longest_palindrome("cbbd") should return "bb"

The function has bugs. Fix them.
""")
```

### With Prompt Overrides

```python
# Customize evaluation criteria
overrides = {
    "Evaluate": {
        "system_prompt": """You are a strict evaluator. Determine if the task
was completed successfully. Be rigorous - partial solutions are failures.
Respond with SUCCESS or FAILURE and explain why.""",
        "user_prompt": """Task: {task}

Attempted solution:
{outcome}

Did this FULLY complete the task with no errors or gaps?
Respond with SUCCESS or FAILURE and detailed explanation.

Your evaluation:"""
    },
    "ReflectOnTrial": {
        "system_prompt": """You are a learning agent analyzing failures.
Generate actionable insights about what went wrong and how to improve.""",
        "user_prompt": """Task: {task}

Your plan: {plan}

What happened: {outcome}

Evaluation: {evaluation}

Analyze this trial deeply:
1. What specific aspect failed?
2. Why did it fail?
3. What should be different in the next attempt?
4. What (if anything) worked well and should be kept?

Your insights:"""
    }
}

agent = ReflexionAgent(
    llm_configs=llm_configs,
    max_trials=3,
    prompt_overrides=overrides
)
```

## Customizing Prompts

### Understanding Reflexion Prompts

Reflexion uses five prompt templates:

1. **PlanWithMemory**: Creates plan using reflection memory from previous trials
2. **Execute**: Executes the current plan
3. **Evaluate**: Judges success or failure
4. **ReflectOnTrial**: Generates insights from the trial
5. **GenerateFinal**: Creates final answer when trials exhausted

### Method 1: Custom Instructions

```python
agent = ReflexionAgent(
    llm_configs=llm_configs,
    custom_instructions="""
    LEARNING APPROACH:
    - Each trial should explore meaningfully different approaches
    - Extract specific, actionable lessons
    - Build systematically on previous insights
    - Avoid repeating mistakes

    SUCCESS CRITERIA:
    - Solution must be complete
    - All requirements satisfied
    - No errors or edge cases missed
    """
)
```

### Method 2: Prompt Overrides

```python
# Customize planning with memory
overrides = {
    "PlanWithMemory": {
        "system_prompt": """You learn from past attempts. Use insights from
previous trials to create better plans.""",
        "user_prompt": """Task: {task}

Trial: {trial_count}/{max_trials}

Lessons learned from previous trials:
{memory}

Plan your next approach, incorporating what you've learned.
Be specific about how you're adapting based on past failures.

Your plan:"""
    }
}
```

### Method 3: Custom Prompt Directory

```bash
my_prompts/
└── ReflexionAgent/
    ├── PlanWithMemory/
    │   ├── system_prompt.md
    │   └── user_prompt.md
    ├── Execute/
    │   ├── system_prompt.md
    │   └── user_prompt.md
    ├── Evaluate/
    │   ├── system_prompt.md
    │   └── user_prompt.md
    ├── ReflectOnTrial/
    │   ├── system_prompt.md
    │   └── user_prompt.md
    └── GenerateFinal/
        ├── system_prompt.md
        └── user_prompt.md
```

## Setting Agent Goals

### Via Task Description

Provide clear success criteria:

```python
# Well-defined success criteria
agent.run("""
Task: Optimize this SQL query to run in under 2 seconds

Current query:
SELECT * FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date > '2023-01-01'
ORDER BY o.total DESC

Database info:
- orders table: 1M rows
- customers table: 100K rows
- No current indexes except primary keys

Success criteria:
- Query returns same results
- Execution time < 2 seconds
- Explain your optimization strategy
""")
```

### Via Custom Instructions

```python
agent = ReflexionAgent(
    llm_configs=llm_configs,
    custom_instructions="""
    GOAL: Find working, optimal solutions through iterative learning

    TRIAL SUCCESS DEFINITION:
    - Solution is correct (passes all test cases)
    - Solution is efficient (meets performance requirements)
    - Solution is complete (handles edge cases)

    REFLECTION QUALITY:
    - Identify root causes of failures
    - Generate specific, testable hypotheses
    - Propose concrete alternative approaches

    LEARNING EFFICIENCY:
    - Don't repeat the same mistakes
    - Build incrementally on partial successes
    - Try meaningfully different approaches if stuck
    """
)
```

## Advanced Usage

### Adjusting Trial Budget

```python
# Quick tasks: fewer trials
quick_agent = ReflexionAgent(
    llm_configs=llm_configs,
    max_trials=2
)

# Complex tasks: more trials
thorough_agent = ReflexionAgent(
    llm_configs=llm_configs,
    max_trials=5
)

# Very challenging tasks: extended trials
research_agent = ReflexionAgent(
    llm_configs=llm_configs,
    max_trials=10
)
```

### Custom Evaluation Logic

```python
class CustomReflexionAgent(ReflexionAgent):
    def _evaluate_outcome(self, state):
        """Override with domain-specific evaluation"""
        task = state["input_task"]
        outcome = state["outcome"]

        # Custom evaluation logic
        if "code" in task.lower():
            # Code-specific checks
            evaluation = self._evaluate_code(outcome)
        elif "math" in task.lower():
            # Math-specific checks
            evaluation = self._evaluate_math(outcome)
        else:
            # Default LLM evaluation
            return super()._evaluate_outcome(state)

        state["evaluation"] = evaluation
        state["evaluation_detail"] = f"Custom evaluation: {evaluation}"
        return state

    def _evaluate_code(self, code):
        """Evaluate code outcome"""
        try:
            # Try to execute code
            exec(code)
            return "success"
        except:
            return "failure"

    def _evaluate_math(self, answer):
        """Evaluate mathematical answer"""
        # Custom math validation logic
        pass

agent = CustomReflexionAgent(llm_configs=llm_configs)
```

### Memory Analysis

```python
class AnalyzingReflexionAgent(ReflexionAgent):
    def run(self, input_data):
        """Override to analyze memory after completion"""
        result = super().run(input_data)

        # Access reflection memory for analysis
        # (Would need to store in instance variable during execution)
        print("\n=== Learning Summary ===")
        print(f"Trials completed: {self.trial_count}")
        print("\nKey insights:")
        for i, insight in enumerate(self.memory_log, 1):
            print(f"{i}. {insight}")

        return result

agent = AnalyzingReflexionAgent(llm_configs=llm_configs)
```

## Performance Considerations

### Cost Analysis

Reflexion is expensive due to multiple trials:

**Per trial cost**:
- Plan: 1 LLM call
- Execute: 1 LLM call
- Evaluate: 1 LLM call
- Reflect: 1 LLM call
- **= 4 calls per trial**

**Total cost**:
- 3 trials: ~12 LLM calls
- 5 trials: ~20 LLM calls
- 10 trials: ~40 LLM calls

**Optimization strategies**:

```python
# 1. Limit trials
agent = ReflexionAgent(llm_configs=llm_configs, max_trials=3)

# 2. Use cheaper models for some roles
llm_configs = {
    "thinking": {"provider": "openai", "model": "gpt-4"},
    "execution": {"provider": "openai", "model": "gpt-3.5-turbo"},  # Cheaper
    "reflection": {"provider": "openai", "model": "gpt-4"},
    "documentation": {"provider": "openai", "model": "gpt-3.5-turbo"}  # Cheaper
}

# 3. Early stopping with custom evaluation
# (Stop as soon as success is detected)
```

### When to Use Reflexion vs Other Patterns

| Task Type | Best Pattern | Reason |
|-----------|-------------|---------|
| One-shot quality improvement | Reflection | ✅ No need for trials |
| Learning from failures | Reflexion | ✅ Designed for this |
| Simple tasks | Direct LLM | ❌ Reflexion overkill |
| Tool-based workflows | ReAct | ❌ Reflexion doesn't use tools |
| Cost-sensitive | Reflection, Plan & Solve | ❌ Reflexion expensive |

## Comparison with Other Patterns

| Aspect | Reflexion | Reflection | ReAct |
|--------|-----------|-----------|--------|
| **Trials** | Multiple | Single task | Single task |
| **Memory** | Persistent across trials | Within-task only | No memory |
| **Learning** | Trial-and-error | Self-critique | Adaptive action |
| **Cost** | Very High | Medium-High | Medium |
| **Best For** | Learning from failures | Quality improvement | Tool interaction |

## Common Pitfalls

### 1. Insufficient Trials

❌ **Bad**: Too few trials for complex problems
```python
agent = ReflexionAgent(llm_configs=llm_configs, max_trials=1)
# This is just expensive execution, no learning benefit
```

✅ **Good**: Appropriate trial budget
```python
agent = ReflexionAgent(llm_configs=llm_configs, max_trials=3-5)
```

### 2. Vague Evaluation Criteria

❌ **Bad**: Unclear success definition
```python
agent.run("Make this better")  # What is "better"?
```

✅ **Good**: Specific, measurable criteria
```python
agent.run("""
Optimize this function to:
1. Run in O(n log n) time or better
2. Use O(n) space or less
3. Pass all test cases
4. Handle edge cases (empty input, single element, etc.)
""")
```

### 3. Weak Reflections

❌ **Bad**: Generic or non-actionable insights

✅ **Good**: Ensure reflections are specific
```python
overrides = {
    "ReflectOnTrial": {
        "user_prompt": """...
Your reflection must include:
1. SPECIFIC failure point (not "it didn't work")
2. ROOT CAUSE analysis (why it failed)
3. CONCRETE alternative approach (exactly what to try next)

Your detailed reflection:"""
    }
}
```

### 4. Repeating Mistakes

❌ **Bad**: Agent ignores previous learnings

✅ **Good**: Emphasize memory usage in planning
```python
overrides = {
    "PlanWithMemory": {
        "user_prompt": """...
Lessons from previous trials:
{memory}

Your plan MUST:
- Avoid approaches that already failed
- Build on what worked
- Try something meaningfully different if previous approaches all failed

Your plan:"""
    }
}
```

## Troubleshooting

### All Trials Failing

**Symptom**: Agent doesn't find solution within max_trials

**Solutions**:
```python
# 1. Increase trial budget
agent = ReflexionAgent(llm_configs=llm_configs, max_trials=7)

# 2. Provide more guidance
custom_instructions = """
APPROACH DIVERSITY:
If first 2 trials fail, try radically different approaches in subsequent trials.
Don't keep varying the same failed strategy.
"""

# 3. Check if task is solvable
# Verify task has clear solution and criteria
```

### Weak Learning Between Trials

**Symptom**: Later trials don't improve on earlier ones

**Solutions**:
```python
# Strengthen reflection prompts
overrides = {
    "ReflectOnTrial": {
        "user_prompt": """...
Analyze deeply:
- What EXACTLY went wrong at which step?
- What assumption was incorrect?
- What approach should be abandoned entirely?
- What aspect should be kept for next trial?
- What SPECIFIC change should trial {trial_count + 1} make?

Your analysis:"""
    }
}
```

### Premature Success Evaluation

**Symptom**: Agent declares success on partial solutions

**Solutions**:
```python
# Make evaluation more rigorous
overrides = {
    "Evaluate": {
        "system_prompt": """You are a strict evaluator. Only declare SUCCESS
if the solution is 100% complete and correct. Partial solutions are FAILURE.""",
        "user_prompt": """...
Check every requirement:
{requirements_checklist}

All must be satisfied for SUCCESS.

Your evaluation:"""
    }
}
```

## Next Steps

- Try the [complete examples](../examples/reflexion-examples.md)
- Learn about [Reflection](reflection.md) for single-task refinement
- Explore [LATS](lats.md) for tree-search based exploration
- Read the [original paper](https://arxiv.org/abs/2303.11366)

## References

- Original paper: [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- Related: [Self-Refine](https://arxiv.org/abs/2303.17651) and iterative improvement techniques
- Reinforcement learning concepts applied to language agents
