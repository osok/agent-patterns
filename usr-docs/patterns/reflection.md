# Reflection Agent Pattern

The **Reflection** pattern implements a generate-critique-refine cycle where an agent creates an initial response, reflects on its quality, and iteratively improves it based on self-critique.

## Overview

**Best For**: Tasks requiring high-quality outputs where iterative refinement adds value

**Complexity**: ⭐⭐ Moderate (Good balance of simplicity and power)

**Cost**: $$$ Higher (Multiple LLM calls per cycle)

## When to Use Reflection

### Ideal Use Cases

✅ **Content generation and editing**
- Agent generates draft content
- Critiques quality, clarity, and completeness
- Refines output to meet high standards

✅ **Code review and improvement**
- Generates initial code solution
- Identifies bugs, inefficiencies, or style issues
- Produces improved version

✅ **Creative writing**
- Creates initial draft
- Evaluates narrative flow, character development
- Refines story elements

✅ **Document preparation**
- Generates reports or proposals
- Critiques structure, argumentation, evidence
- Polishes final version

### When NOT to Use Reflection

❌ **Time-sensitive tasks** → Use ReAct for faster results
❌ **Tasks requiring external tools** → Use ReAct with tool access
❌ **Learning from multiple trials** → Use Reflexion for memory-based learning
❌ **Simple queries** → Direct LLM call sufficient

## How Reflection Works

### The Generate-Reflect-Refine Cycle

```
┌─────────────────────────────────────────┐
│                                         │
│  1. GENERATE: Create initial output    │
│     "Draft blog post about AI ethics"   │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  2. REFLECT: Critique the output        │
│     "Missing concrete examples, too     │
│      abstract, could improve structure" │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  3. CHECK: Needs refinement?            │
│     Analyze critique for improvement    │
│     opportunities                       │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  4. REFINE: Improve based on critique   │
│     Add examples, restructure, clarify  │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
              [Repeat up to max_reflection_cycles]
```

### Theoretical Foundation

The Reflection pattern is inspired by metacognitive learning and self-regulated problem solving. Key principles:

1. **Self-evaluation**: The agent assesses its own work objectively
2. **Iterative improvement**: Multiple refinement cycles lead to better outcomes
3. **Quality awareness**: Explicit critique makes quality criteria transparent
4. **Adaptive refinement**: Agent learns what aspects need improvement

### Algorithm

```python
def reflection_loop(task, max_cycles=1):
    """Simplified Reflection algorithm"""

    # Generate initial output
    output = llm_generate(task)

    for cycle in range(max_cycles):
        # Reflect on current output
        reflection = llm_reflect(task, output)

        # Check if refinement is needed
        needs_refinement = evaluate_reflection(reflection)

        if not needs_refinement:
            return output

        # Refine based on critique
        output = llm_refine(task, output, reflection)

    return output
```

## API Reference

### Class: `ReflectionAgent`

```python
from agent_patterns.patterns import ReflectionAgent

agent = ReflectionAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    max_reflection_cycles: int = 1,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configs for "documentation" and "reflection" roles |
| `max_reflection_cycles` | `int` | No | Maximum number of refine iterations (default: 1) |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict` | No | Override specific prompts programmatically |

#### LLM Roles

- **documentation**: Used for generating initial output and refinements
- **reflection**: Used for critiquing the output

#### Methods

**`run(input_data: str) -> str`**

Executes the Reflection pattern on the given input.

- **Parameters**:
  - `input_data` (str): The task or content request
- **Returns**: str - The final refined output
- **Raises**: ValueError if graph not built

**`build_graph() -> None`**

Builds the LangGraph state graph. Called automatically during initialization.

## Complete Examples

### Basic Usage

```python
from agent_patterns.patterns import ReflectionAgent

# Configure LLMs
llm_configs = {
    "documentation": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
    },
    "reflection": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,  # Lower temp for more consistent critique
    }
}

# Create agent
agent = ReflectionAgent(
    llm_configs=llm_configs,
    max_reflection_cycles=1
)

# Generate and refine content
result = agent.run("""
Write a technical blog post about the benefits of microservices architecture.
Target audience: Senior developers and tech leads.
""")

print(result)
# Output will be a refined blog post that has been self-critiqued and improved
```

### With Custom Instructions

```python
# Add domain-specific quality criteria
writing_guidelines = """
You are a technical writer. Follow these quality standards:

GENERATION:
- Use clear, concrete examples
- Avoid jargon without explanation
- Structure with clear headings
- Include code snippets where relevant

REFLECTION:
- Check for technical accuracy
- Verify examples are practical
- Ensure logical flow
- Identify areas lacking clarity

REFINEMENT:
- Address all critique points
- Maintain the original intent
- Improve without over-complicating
"""

agent = ReflectionAgent(
    llm_configs=llm_configs,
    max_reflection_cycles=2,  # Allow 2 refinement cycles
    custom_instructions=writing_guidelines
)

result = agent.run("Explain database indexing to junior developers")
```

### With Prompt Overrides

```python
# Customize the reflection prompt for code review
overrides = {
    "Reflect": {
        "system": """You are an expert code reviewer. Provide constructive critique focusing on:
- Code correctness and edge cases
- Performance and efficiency
- Readability and maintainability
- Best practices and design patterns
- Security considerations
""",
        "user": """Original task: {task}

Current code:
{output}

Provide a detailed code review. For each issue, explain:
1. What the problem is
2. Why it matters
3. How to fix it

Your critique:"""
    },
    "Refine": {
        "system": "You are an expert programmer. Improve the code based on the review feedback.",
        "user": """Task: {task}

Current code:
{output}

Code review feedback:
{reflection}

Produce improved code that addresses all feedback while maintaining functionality."""
    }
}

agent = ReflectionAgent(
    llm_configs=llm_configs,
    max_reflection_cycles=1,
    prompt_overrides=overrides
)

result = agent.run("""
Write a Python function to find the longest common substring
between two strings. Include error handling.
""")
```

## Customizing Prompts

### Understanding the System Prompt Structure

Version 0.2.0 introduces **enterprise-grade prompts** with a comprehensive 9-section structure. Each system prompt is now 150-300+ lines (compared to ~32 lines previously), providing significantly better guidance to the LLM.

#### The 9-Section Comprehensive Structure

All Reflection system prompts now follow this proven architecture:

1. **Role and Identity** - Clear definition of the agent's purpose and capabilities
2. **Core Capabilities** - Explicit CAN/CANNOT boundaries to prevent hallucination
3. **Process** - Step-by-step workflow guidance for consistent execution
4. **Output Format** - Precise specifications for structured responses
5. **Decision-Making Guidelines** - Context-specific rules and best practices
6. **Quality Standards** - Clear criteria for excellent vs. poor outputs
7. **Edge Cases** - Built-in error handling and special situation guidance
8. **Examples** - 2-3 concrete examples demonstrating expected behavior
9. **Critical Reminders** - Key points emphasized for reliability

**Benefits**: Increased reliability, better transparency, improved robustness, and backward compatibility. No code changes required to benefit from enhanced prompts.

### Understanding Reflection Prompts

The Reflection pattern uses three prompt templates (all now with comprehensive 9-section structure):

**Generate/system.md & user.md**: Initial content generation
- Now includes all 9 sections for better generation quality
- Sets the agent's role, capabilities, and boundaries
- Produces first draft with clear quality standards

**Reflect/system.md & user.md**: Critique generation
- Comprehensive guidance on analyzing outputs
- Identifies strengths and weaknesses systematically
- Suggests improvements with examples

**Refine/system.md & user.md**: Improvement generation
- Detailed process for addressing feedback
- Takes original output and critique
- Produces improved version with quality checks

### Method 1: Custom Instructions

Add guidelines without changing core prompts:

```python
agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions="""
    QUALITY CRITERIA:
    - Accuracy: All facts must be verifiable
    - Clarity: Use simple language where possible
    - Completeness: Address all aspects of the task
    - Conciseness: Avoid unnecessary verbosity

    When refining, prioritize clarity and accuracy over length.
    """
)
```

### Method 2: Prompt Overrides

Replace prompts entirely:

```python
overrides = {
    "Generate": {
        "system": "You are a creative writer specializing in short stories.",
        "user": "Write a short story based on: {task}\n\nYour story:"
    },
    "Reflect": {
        "system": "You are a literary critic. Evaluate stories for narrative quality.",
        "user": """Story prompt: {task}

Current story:
{output}

Critique this story's:
1. Character development
2. Plot structure
3. Pacing and tension
4. Dialogue quality
5. Descriptive language

Your critique:"""
    },
    "Refine": {
        "system": "You are a skilled editor. Improve stories based on feedback.",
        "user": """Story prompt: {task}

Current story:
{output}

Editorial feedback:
{reflection}

Rewrite the story addressing all feedback points:"""
    }
}

agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=overrides,
    max_reflection_cycles=2
)
```

### Method 3: Custom Prompt Directory

For extensive customization:

```bash
my_prompts/
└── ReflectionAgent/
    ├── Generate/
    │   ├── system.md
    │   └── user.md
    ├── Reflect/
    │   ├── system.md
    │   └── user.md
    └── Refine/
        ├── system.md
        └── user.md
```

```python
agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_dir="my_prompts"
)
```

## Setting Agent Goals

### Via Task Description

The most direct way to set goals:

```python
# Specific quality requirements
agent.run("""
Write a product description for wireless headphones that:
1. Highlights key features (battery life, sound quality, comfort)
2. Uses persuasive but honest language
3. Is 150-200 words
4. Targets audiophile consumers
""")

# Technical requirements
agent.run("""
Create a Python class for a binary search tree with:
- Insert, delete, and search methods
- In-order traversal
- Comprehensive docstrings
- Type hints
- Unit test examples
""")
```

### Via Custom Instructions

Set persistent quality standards:

```python
agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions="""
    GOAL: Produce publication-ready technical documentation

    GENERATION STANDARDS:
    - Use active voice
    - Include concrete examples
    - Structure with clear hierarchy
    - Add code snippets for technical concepts

    REFLECTION FOCUS:
    - Verify technical accuracy
    - Check completeness of examples
    - Ensure proper formatting
    - Validate code snippets

    REFINEMENT PRIORITIES:
    1. Correctness
    2. Clarity
    3. Completeness
    4. Consistency
    """
)
```

### Via System Prompt Override

Set goals at the system level for each phase:

```python
overrides = {
    "Generate": {
        "system": """You are a technical documentation writer. Your goal is to create
clear, accurate, and comprehensive documentation that helps developers understand
complex concepts quickly. Always include practical examples."""
    },
    "Reflect": {
        "system": """You are a senior technical reviewer. Your goal is to ensure
documentation meets enterprise standards for accuracy, completeness, and clarity.
Be thorough but constructive in your critique."""
    },
    "Refine": {
        "system": """You are an expert technical editor. Your goal is to transform
good documentation into excellent documentation by addressing all feedback while
maintaining readability and practical value."""
    }
}
```

## Advanced Usage

### Multiple Reflection Cycles

```python
# For complex tasks requiring multiple iterations
agent = ReflectionAgent(
    llm_configs=llm_configs,
    max_reflection_cycles=3
)

# Each cycle provides another opportunity for improvement
result = agent.run("""
Write a comprehensive research paper introduction about quantum computing,
including background, significance, and research questions.
""")
```

### Role-Specific LLM Configurations

```python
# Use different models for different roles
llm_configs = {
    "documentation": {
        "provider": "openai",
        "model": "gpt-4",  # Stronger model for generation
        "temperature": 0.8,  # Higher creativity
    },
    "reflection": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper model for critique
        "temperature": 0.2,  # More focused critique
    }
}

agent = ReflectionAgent(llm_configs=llm_configs)
```

### Combining with External Validation

```python
# Use custom logic to decide if refinement is needed
class CustomReflectionAgent(ReflectionAgent):
    def _check_refinement_needed(self, state):
        """Override with custom validation logic"""
        reflection = state.get("reflection", "")
        output = state.get("initial_output") or state.get("refined_output", "")

        # Custom checks
        needs_refinement = (
            len(output) < 500 or  # Too short
            "incomplete" in reflection.lower() or
            "error" in reflection.lower() or
            not self._has_code_examples(output)
        )

        state["needs_refinement"] = needs_refinement
        return state

    def _has_code_examples(self, text):
        """Check if output contains code blocks"""
        return "```" in text or "    " in text

agent = CustomReflectionAgent(llm_configs=llm_configs)
```

## Performance Considerations

### Cost Optimization

Reflection makes multiple LLM calls (generate + reflect + refine) × cycles:

```python
# Minimize cycles for routine tasks
agent = ReflectionAgent(
    llm_configs=llm_configs,
    max_reflection_cycles=1  # Just one improvement pass
)

# Use cheaper model for reflection
llm_configs = {
    "documentation": {
        "provider": "openai",
        "model": "gpt-4",
    },
    "reflection": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper for critique
    }
}
```

**Cost per task**:
- 1 cycle: 3 LLM calls (generate + reflect + refine)
- 2 cycles: 5 LLM calls (generate + reflect + refine + reflect + refine)
- 3 cycles: 7 LLM calls

### Quality vs Cost Tradeoff

```python
# High-quality output (expensive)
premium_agent = ReflectionAgent(
    llm_configs={"documentation": {...}, "reflection": {...}},
    max_reflection_cycles=3
)

# Balanced (moderate cost)
standard_agent = ReflectionAgent(
    llm_configs={"documentation": {...}, "reflection": {...}},
    max_reflection_cycles=1
)

# Fast and cheap (skip reflection entirely - use direct LLM)
# Don't use Reflection pattern for simple tasks
```

### When to Skip Reflection

Not all tasks benefit from reflection:

```python
# Good for Reflection: Complex, high-stakes content
agent.run("Write a legal disclaimer for software liability")  # ✅

# Overkill for Reflection: Simple queries
agent.run("What is 2+2?")  # ❌ Too simple, use direct LLM
agent.run("List Python's built-in data types")  # ❌ Factual, no refinement needed
```

## Comparison with Other Patterns

| Aspect | Reflection | Reflexion | Self-Discovery |
|--------|-----------|-----------|----------------|
| **Approach** | Single-task iteration | Multi-trial learning | Reasoning module selection |
| **Memory** | Within-task only | Across trials | No memory |
| **Best For** | Quality refinement | Learning from failures | Complex reasoning |
| **Cost** | Medium-High | High | Medium-High |
| **Iterations** | 1-3 cycles | 3-10 trials | Single pass |
| **Strengths** | Polished output | Adaptive learning | Diverse perspectives |

## Common Pitfalls

### 1. Insufficient Reflection Cycles

❌ **Bad**: Using 1 cycle for complex tasks
```python
agent = ReflectionAgent(llm_configs=llm_configs, max_reflection_cycles=1)
agent.run("Write a comprehensive 50-page technical specification")
```

✅ **Good**: Allocate cycles based on task complexity
```python
agent = ReflectionAgent(llm_configs=llm_configs, max_reflection_cycles=3)
agent.run("Write a comprehensive technical specification with examples")
```

### 2. Vague Reflection Criteria

❌ **Bad**: Generic reflection instructions
```python
custom_instructions = "Make it better"
```

✅ **Good**: Specific quality criteria
```python
custom_instructions = """
REFLECTION CRITERIA:
- Technical accuracy: Are all facts correct?
- Completeness: Are all required sections present?
- Clarity: Can the target audience understand it?
- Examples: Are there sufficient practical examples?
"""
```

### 3. Over-Refinement

❌ **Bad**: Too many cycles can lead to over-editing
```python
agent = ReflectionAgent(llm_configs=llm_configs, max_reflection_cycles=10)
```

✅ **Good**: Use appropriate cycle count
```python
# Most tasks: 1-2 cycles
agent = ReflectionAgent(llm_configs=llm_configs, max_reflection_cycles=2)

# Complex tasks: 2-3 cycles
agent = ReflectionAgent(llm_configs=llm_configs, max_reflection_cycles=3)
```

### 4. Same Temperature for All Roles

❌ **Bad**: Same settings for generation and critique
```python
llm_configs = {
    "documentation": {"provider": "openai", "model": "gpt-4", "temperature": 0.7},
    "reflection": {"provider": "openai", "model": "gpt-4", "temperature": 0.7}
}
```

✅ **Good**: Lower temperature for consistent critique
```python
llm_configs = {
    "documentation": {"provider": "openai", "model": "gpt-4", "temperature": 0.8},
    "reflection": {"provider": "openai", "model": "gpt-4", "temperature": 0.2}
}
```

## Troubleshooting

### Refinement Not Triggered

**Symptom**: Agent returns initial output without refining

**Causes & Solutions**:
- Reflection too positive → Adjust `_check_refinement_needed` heuristics
- Not enough negative indicators detected → Customize reflection prompt to be more critical
- Override the check method to always refine:

```python
class AlwaysRefineAgent(ReflectionAgent):
    def _check_refinement_needed(self, state):
        state["needs_refinement"] = True  # Always refine
        return state
```

### Poor Quality Refinements

**Symptom**: Refined output isn't better than original

**Causes & Solutions**:
- Weak reflection critique → Use stronger LLM for reflection role
- Generic feedback → Add specific criteria in custom_instructions
- Refine prompt too generic → Override Refine prompts with detailed instructions

### Infinite Refinement Loop

**Symptom**: Agent keeps refining without improvement

**Causes & Solutions**:
- max_reflection_cycles too high → Reduce to 2-3
- Reflection always negative → Adjust criteria to recognize good output
- Add cycle tracking in custom instructions

## Next Steps

- Try the [complete examples](../examples/reflection-examples.md)
- Learn about [Reflexion](reflexion.md) for multi-trial learning with memory
- Explore [Self-Discovery](self-discovery.md) for complex reasoning
- Read about [prompt customization](../guides/prompt-customization.md)

## References

- Pattern based on self-critique and metacognitive learning principles
- Related: [Constitutional AI](https://arxiv.org/abs/2212.08073) and self-refinement techniques
- [Reflexion paper](https://arxiv.org/abs/2303.11366) (multi-trial variant)
