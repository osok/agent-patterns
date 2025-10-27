# Prompt Customization Guide

Complete guide to customizing prompts in Agent Patterns using three powerful methods: file-based prompts, custom instructions, and prompt overrides.

## Overview

Agent Patterns provides three complementary ways to customize how your agents communicate with LLMs:

1. **File-Based Prompts**: Traditional approach using markdown template files
2. **Custom Instructions**: Add domain-specific context to all system prompts
3. **Prompt Overrides**: Programmatically replace specific prompts at runtime

Each method serves different use cases, and they can be combined for maximum flexibility.

## Priority System

When multiple customization methods are used together, they follow this priority order:

```
┌─────────────────────────────────────────────────────┐
│  1. Prompt Overrides (Highest Priority)             │
│     → Completely replaces prompts programmatically  │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  2. File-Based Prompts                              │
│     → Loaded from prompt_dir                        │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  3. Custom Instructions (Lowest Priority)           │
│     → Appended to system prompts                    │
└─────────────────────────────────────────────────────┘
```

This design allows you to:
- Start with base templates (file-based)
- Add domain context (custom instructions)
- Override specific steps as needed (prompt overrides)

## Method 1: File-Based Prompts

### Structure

Prompts are organized by pattern and step name:

```
prompts/
├── ReActAgent/
│   └── ThoughtStep/
│       ├── system.md    # System prompt
│       └── user.md      # User prompt template
├── ReflectionAgent/
│   ├── Generate/
│   │   ├── system.md
│   │   └── user.md
│   ├── Reflect/
│   │   ├── system.md
│   │   └── user.md
│   └── Refine/
│       ├── system.md
│       └── user.md
└── SelfDiscoveryAgent/
    ├── DiscoverModules/
    ├── AdaptModules/
    ├── PlanReasoning/
    ├── ExecuteStep/
    └── SynthesizeOutput/
```

### Creating Custom Prompt Directory

1. **Create the directory structure:**

```bash
mkdir -p my_prompts/ReActAgent/ThoughtStep
```

2. **Write system.md:**

```markdown
You are an intelligent research assistant with access to specialized tools.

Your goal is to provide accurate, well-researched answers by:
1. Carefully analyzing the question
2. Selecting appropriate tools
3. Synthesizing information into clear answers

Available tools:
{tool_descriptions}

Format your response as:
Thought: [Your reasoning about what to do next]
Action: [tool_name or FINISH]
Action Input: [parameters for the tool]
```

3. **Write user.md:**

```markdown
Task: {input}

Previous steps:
{history}

What should you do next?
```

4. **Use custom directory:**

```python
from agent_patterns.patterns import ReActAgent

agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    prompt_dir="my_prompts"  # Use custom prompts
)
```

### Template Variables

Each pattern's prompts support specific template variables:

**ReActAgent**:
- `{input}` - The user's task
- `{history}` - Previous thoughts and observations
- `{tool_descriptions}` - Formatted list of available tools

**ReflectionAgent**:
- `{task}` - The user's task
- `{output}` - Current output to reflect on
- `{reflection}` - Critique/feedback

**SelfDiscoveryAgent**:
- `{task}` - The user's task
- `{modules}` - Available reasoning modules
- `{max_modules}` - Maximum modules to select
- `{reasoning_steps}` - Accumulated reasoning results

**See individual pattern documentation for complete variable lists.**

### Example: Custom ReAct Prompts

**my_prompts/ReActAgent/ThoughtStep/system.md:**
```markdown
You are a technical support agent helping developers debug issues.

When analyzing problems:
1. Gather all relevant information first
2. Form hypotheses about the root cause
3. Test hypotheses systematically
4. Provide clear, actionable solutions

Available diagnostic tools:
{tool_descriptions}

Always use this format:
Thought: [Your analysis of the situation]
Action: [tool_name or FINISH]
Action Input: [tool parameters]
```

**my_prompts/ReActAgent/ThoughtStep/user.md:**
```markdown
Support Ticket: {input}

Investigation History:
{history}

What's your next diagnostic step?
```

## Method 2: Custom Instructions

### What Are Custom Instructions?

Custom instructions are domain-specific guidelines, constraints, or context that get appended to **all system prompts** throughout the agent's workflow. They don't replace prompts—they enhance them.

### When to Use Custom Instructions

Use custom instructions when you need to:
- Add domain expertise (medical, legal, financial, etc.)
- Enforce compliance or regulatory requirements
- Set consistent tone and style across all steps
- Specify target audience
- Add ethical guidelines or constraints

### Basic Usage

```python
from agent_patterns.patterns import SelfDiscoveryAgent

medical_instructions = """
You are providing information in the MEDICAL domain. Follow these guidelines:

1. ACCURACY: Always prioritize medical accuracy and cite evidence-based sources
2. DISCLAIMERS: Include appropriate medical disclaimers where necessary
3. TERMINOLOGY: Use proper medical terminology but explain complex terms
4. ETHICS: Consider ethical implications and patient privacy
5. LIMITATIONS: Acknowledge the limitations of AI in medical contexts
6. RECOMMENDATION: Always recommend consulting healthcare professionals for medical decisions
"""

agent = SelfDiscoveryAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model": "gpt-4"},
        "execution": {"provider": "openai", "model": "gpt-4"}
    },
    custom_instructions=medical_instructions  # Applied to ALL system prompts
)

result = agent.run("What are the key considerations for diagnosing Type 2 Diabetes?")
```

### Domain-Specific Examples

#### Legal Domain

```python
legal_instructions = """
You are providing information in the LEGAL domain. Follow these guidelines:

1. JURISDICTION: Be clear about which jurisdiction's laws you're discussing
2. DISCLAIMERS: Include appropriate legal disclaimers (not legal advice)
3. CITATIONS: Reference specific laws, regulations, or case precedents when possible
4. NEUTRALITY: Present balanced views when discussing legal interpretations
5. UPDATES: Note that laws change and information may become outdated
6. RECOMMENDATION: Always recommend consulting licensed attorneys for legal advice
"""

agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_function},
    custom_instructions=legal_instructions
)
```

#### Financial Compliance

```python
compliance_instructions = """
You are operating under FINANCIAL REGULATORY COMPLIANCE requirements:

1. DISCLOSURES: Include all required regulatory disclosures
2. ACCURACY: Financial information must be verifiable and accurate
3. RISKS: Always discuss relevant risks associated with financial decisions
4. OBJECTIVITY: Avoid promotional or biased language
5. ACCESSIBILITY: Explain financial concepts in clear, accessible language
6. SUITABILITY: Consider the suitability of financial products for different investors
7. DISCLAIMER: This is not financial advice - consult licensed financial advisors

PROHIBITED:
- Making specific investment recommendations
- Guaranteeing returns or outcomes
- Omitting material risks
"""

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=compliance_instructions
)
```

#### Educational Content

```python
educational_instructions = """
You are creating EDUCATIONAL CONTENT. Follow these principles:

1. SCAFFOLDING: Build concepts progressively from simple to complex
2. EXAMPLES: Provide concrete examples for abstract concepts
3. ENGAGEMENT: Use questions and prompts to encourage active learning
4. CLARITY: Use clear, grade-appropriate language
5. FEEDBACK: Explain not just "what" but "why" and "how"
6. ERRORS: Treat misconceptions as learning opportunities
7. ASSESSMENT: Include ways for learners to check their understanding

TARGET AUDIENCE: High school students (ages 14-18)
"""

agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions=educational_instructions
)
```

#### Cultural Sensitivity

```python
cultural_instructions = """
You are operating with CULTURAL SENSITIVITY AND AWARENESS:

1. RESPECT: Show respect for diverse cultural perspectives and practices
2. INCLUSIVITY: Use inclusive language that doesn't assume a specific cultural context
3. AWARENESS: Be mindful of cultural differences in communication styles and values
4. NEUTRALITY: Avoid imposing one culture's values as universal
5. REPRESENTATION: Acknowledge and represent diverse viewpoints
6. SENSITIVITY: Be aware of potentially sensitive cultural or historical topics
7. LEARNING: Approach cultural differences with curiosity and openness

CONTEXT: Creating content for a global, multicultural audience
"""

agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_function},
    custom_instructions=cultural_instructions
)
```

### Best Practices for Custom Instructions

1. **Be Specific**: Vague instructions like "be helpful" are less effective than specific guidelines
2. **Use Numbered Lists**: Makes instructions clear and easy to follow
3. **Include Examples**: When possible, show what you mean
4. **Set Boundaries**: Explicitly state what the agent should NOT do
5. **Keep It Focused**: Too many instructions can be counterproductive
6. **Test Thoroughly**: Verify instructions have the desired effect

### Complete Example from examples/custom_instructions_example.py

```python
from agent_patterns.patterns.self_discovery_agent import SelfDiscoveryAgent

def example_medical_domain():
    """Example: Using custom instructions for medical domain expertise."""

    # Define medical domain instructions
    medical_instructions = """
    You are providing information in the MEDICAL domain. Follow these guidelines:

    1. ACCURACY: Always prioritize medical accuracy and cite evidence-based sources
    2. DISCLAIMERS: Include appropriate medical disclaimers where necessary
    3. TERMINOLOGY: Use proper medical terminology but explain complex terms
    4. ETHICS: Consider ethical implications and patient privacy
    5. LIMITATIONS: Acknowledge the limitations of AI in medical contexts
    6. RECOMMENDATION: Always recommend consulting healthcare professionals for medical decisions
    """

    # Create SelfDiscovery agent with medical instructions
    agent = SelfDiscoveryAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model": "gpt-4"},
            "execution": {"provider": "openai", "model": "gpt-4"}
        },
        custom_instructions=medical_instructions,
        max_selected_modules=3
    )

    # The custom instructions will be appended to ALL system prompts in the workflow
    result = agent.run("What are the key considerations for diagnosing Type 2 Diabetes?")
    return result
```

## Method 3: Prompt Overrides

### What Are Prompt Overrides?

Prompt overrides allow you to **completely replace** specific prompts programmatically at runtime, without modifying any files. This provides maximum control and flexibility.

### When to Use Prompt Overrides

Use prompt overrides when you need to:
- A/B test different prompt variations
- Generate prompts dynamically based on runtime conditions
- Create specialized variants of patterns
- Experiment with prompt engineering
- Adjust complexity levels (beginner vs expert)
- Implement different interaction styles (Socratic, concise, etc.)

### Basic Usage

```python
from agent_patterns.patterns import SelfDiscoveryAgent

# Override the DiscoverModules step
overrides = {
    "DiscoverModules": {
        "system": "You are an expert at selecting reasoning strategies. Be concise.",
        "user": """
Task: {task}

Available reasoning modules:
{modules}

Select the {max_modules} MOST relevant modules for this specific task.

Output format (one per line):
SELECTED: module_name
"""
    }
}

agent = SelfDiscoveryAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model": "gpt-4"},
        "execution": {"provider": "openai", "model": "gpt-4"}
    },
    prompt_overrides=overrides
)
```

### Multiple Overrides

You can override multiple steps independently:

```python
overrides = {
    "DiscoverModules": {
        "system": "You are a strategic reasoning expert. Select wisely.",
        "user": "Task: {task}\n\nModules:\n{modules}\n\nSelect {max_modules} best modules:\nSELECTED: module_name"
    },
    "AdaptModules": {
        "system": "You adapt generic reasoning strategies to specific problems.",
        "user": "Task: {task}\n\nModule: {module_name}\nDescription: {module_description}\n\nAdapt this to the task:"
    },
    "SynthesizeOutput": {
        "system": "You synthesize reasoning steps into a clear, final answer.",
        "user": "Task: {task}\n\nReasoning:\n{reasoning_steps}\n\nProvide the final answer:"
    }
}

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=overrides,
    max_selected_modules=2
)
```

### Style Customization

Create different interaction styles:

**Concise Style:**
```python
concise_overrides = {
    "Generate": {
        "system": """You are a concise assistant. Follow these rules:
- Use bullet points instead of paragraphs
- Maximum 3 sentences per point
- No fluff or filler words
- Get straight to the point""",
        "user": "Task: {task}\n\nProvide a concise, bulleted response."
    },
    "Refine": {
        "system": """You are a ruthless editor. Make responses MORE concise:
- Cut unnecessary words
- Use shorter sentences
- Remove redundancy
- Keep only essential information""",
        "user": "Task: {task}\n\nCurrent response:\n{output}\n\nCritique:\n{reflection}\n\nMake it more concise:"
    }
}

agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=concise_overrides
)
```

**Socratic Method:**
```python
socratic_overrides = {
    "Reflect": {
        "system": """You are a Socratic teacher who improves thinking through questions.
Instead of telling what's wrong, ask probing questions that guide toward better answers:
- What assumptions are being made?
- What evidence supports this?
- What alternative explanations exist?
- What are the implications?
- How would you test this?""",
        "user": """Original task: {task}

Current response:
{output}

Ask 3-5 Socratic questions that would improve this response:"""
    }
}

agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=socratic_overrides
)
```

**Expert Level:**
```python
expert_overrides = {
    "Generate": {
        "system": """You are addressing PhD-level experts in the field.
- Use advanced technical terminology without explanation
- Reference current research and state-of-the-art methods
- Discuss nuances, edge cases, and open research questions
- Assume deep domain knowledge
- Focus on cutting-edge developments""",
        "user": "Task: {task}\n\nProvide an expert-level technical response."
    }
}

agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=expert_overrides
)
```

### Dynamic Overrides

Generate prompts dynamically based on task characteristics:

```python
def create_overrides_for_task(task: str) -> dict:
    """Dynamically create overrides based on task."""

    # Detect if task is mathematical
    if any(word in task.lower() for word in ["calculate", "solve", "equation", "math"]):
        return {
            "ExecuteStep": {
                "system": "You are a mathematical problem solver. Show all work step-by-step.",
                "user": "Step: {step_description}\n\nSolve this step, showing all calculations:"
            }
        }

    # Detect if task is creative
    elif any(word in task.lower() for word in ["design", "create", "write", "story"]):
        return {
            "ExecuteStep": {
                "system": "You are a creative thinker. Explore multiple possibilities.",
                "user": "Step: {step_description}\n\nApproach this creatively with multiple ideas:"
            }
        }

    # Default analytical approach
    else:
        return {
            "ExecuteStep": {
                "system": "You are an analytical problem solver. Use logic and evidence.",
                "user": "Step: {step_description}\n\nAnalyze this systematically:"
            }
        }

# Use dynamic overrides
task = "Calculate the compound interest on $10,000 at 5% for 10 years"
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=create_overrides_for_task(task)
)
result = agent.run(task)
```

### Complete Example from examples/prompt_overrides_example.py

```python
from agent_patterns.patterns import ReflectionAgent

def example_style_customization():
    """Example: Customize the style/tone of responses."""

    # Create a variant that produces more concise outputs
    concise_overrides = {
        "Generate": {
            "system": """You are a concise assistant. Follow these rules:
- Use bullet points instead of paragraphs
- Maximum 3 sentences per point
- No fluff or filler words
- Get straight to the point""",
            "user": "Task: {task}\n\nProvide a concise, bulleted response."
        },
        "Refine": {
            "system": """You are a ruthless editor. Make responses MORE concise:
- Cut unnecessary words
- Use shorter sentences
- Remove redundancy
- Keep only essential information""",
            "user": "Task: {task}\n\nCurrent response:\n{output}\n\nCritique:\n{reflection}\n\nMake it more concise:"
        }
    }

    agent = ReflectionAgent(
        llm_configs={
            "documentation": {"provider": "openai", "model": "gpt-4"},
            "reflection": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=concise_overrides,
        max_reflection_cycles=1
    )

    result = agent.run("Explain machine learning")
    return result
```

## Combining All Three Methods

The real power comes from combining all three approaches:

```python
from agent_patterns.patterns import ReflectionAgent

# 1. Start with custom prompts directory
# 2. Add domain-specific instructions
domain_instructions = """
DOMAIN: Software Architecture
AUDIENCE: Senior engineers
FORMAT: Include diagrams (described in text), code examples, and trade-offs
"""

# 3. Override specific steps for fine-tuning
overrides = {
    "Generate": {
        "system": "You create structured, well-organized responses.",
        "user": "Task: {task}\n\nCreate a structured response with clear sections."
    }
}

# Combine all three
agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_dir="my_custom_prompts",      # 1. Custom directory
    custom_instructions=domain_instructions,  # 2. Add domain context
    prompt_overrides=overrides            # 3. Override specific steps
)

result = agent.run("Design a microservices architecture for an e-commerce platform")
```

### Resolution Order

When all three methods are used:

1. **System Prompt**:
   - If override exists: Use override's system prompt
   - Else: Load from file system
   - Then: Append custom_instructions to system prompt

2. **User Prompt**:
   - If override exists: Use override's user prompt
   - Else: Load from file system

Example flow:
```python
# Step: Generate
# 1. Check overrides → Found! Use override system prompt: "You create structured responses"
# 2. Append custom_instructions → "You create structured responses\n\nDOMAIN: Software Architecture..."
# 3. Check overrides → Found! Use override user prompt
# Final: Use overridden prompts + custom instructions
```

## Pattern-Specific Examples

### ReAct Pattern

```python
from agent_patterns.patterns import ReActAgent

# Custom instructions for customer support
support_instructions = """
You are a customer support agent:
- Be polite and empathetic
- Gather all necessary information before taking action
- Confirm actions with the user when possible
- Provide clear explanations of what you're doing
"""

# Override for more structured thinking
react_overrides = {
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
    custom_instructions=support_instructions,
    prompt_overrides=react_overrides
)
```

### Self-Discovery Pattern

```python
from agent_patterns.patterns import SelfDiscoveryAgent

# Instructions for scientific reasoning
science_instructions = """
Apply rigorous scientific methodology:
1. Form clear hypotheses
2. Consider alternative explanations
3. Evaluate evidence objectively
4. Acknowledge limitations and uncertainty
5. Draw conclusions proportional to evidence strength
"""

# Override for concise module selection
discovery_overrides = {
    "DiscoverModules": {
        "system": "Select reasoning modules efficiently. Prefer proven strategies.",
        "user": "Task: {task}\n\nModules:\n{modules}\n\nSelect top {max_modules}:"
    }
}

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=science_instructions,
    prompt_overrides=discovery_overrides,
    max_selected_modules=3
)
```

### STORM Pattern

```python
from agent_patterns.patterns import STORMAgent

# Instructions for balanced research
research_instructions = """
Conduct balanced, multi-perspective research:
1. Seek diverse viewpoints and sources
2. Identify potential biases in sources
3. Present evidence for different perspectives
4. Distinguish facts from opinions
5. Acknowledge areas of uncertainty or debate
"""

agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_function},
    custom_instructions=research_instructions
)
```

## Testing Your Customizations

### Unit Testing Prompts

```python
import pytest
from agent_patterns.patterns import ReflectionAgent

def test_custom_instructions_applied():
    """Test that custom instructions are included in prompts."""
    instructions = "DOMAIN: Medical\nAUDIENCE: Patients"

    agent = ReflectionAgent(
        llm_configs=llm_configs,
        custom_instructions=instructions
    )

    # Load a prompt and verify instructions are appended
    prompt_data = agent._load_prompt("Generate")
    assert "DOMAIN: Medical" in prompt_data["system"]
    assert "AUDIENCE: Patients" in prompt_data["system"]

def test_prompt_overrides():
    """Test that overrides completely replace prompts."""
    overrides = {
        "Generate": {
            "system": "Custom system prompt",
            "user": "Custom user prompt with {task}"
        }
    }

    agent = ReflectionAgent(
        llm_configs=llm_configs,
        prompt_overrides=overrides
    )

    prompt_data = agent._load_prompt("Generate")
    assert prompt_data["system"] == "Custom system prompt"
    assert prompt_data["user"] == "Custom user prompt with {task}"
```

### A/B Testing Prompts

```python
def compare_prompt_variations(task: str):
    """A/B test different prompt variations."""

    # Version A: Standard prompts
    agent_a = ReflectionAgent(llm_configs=llm_configs)
    result_a = agent_a.run(task)

    # Version B: Concise prompts
    concise_overrides = {
        "Generate": {
            "system": "Be extremely concise. Use bullet points.",
            "user": "Task: {task}\n\nBrief response:"
        }
    }
    agent_b = ReflectionAgent(
        llm_configs=llm_configs,
        prompt_overrides=concise_overrides
    )
    result_b = agent_b.run(task)

    # Compare results
    print(f"Version A length: {len(result_a)}")
    print(f"Version B length: {len(result_b)}")

    return result_a, result_b
```

## Common Pitfalls

### 1. Missing Template Variables

❌ **Bad**: Using undefined variables
```python
overrides = {
    "Generate": {
        "user": "Task: {unknown_variable}\n\nRespond:"  # KeyError!
    }
}
```

✅ **Good**: Check pattern documentation for valid variables
```python
# ReflectionAgent Generate step uses {task}
overrides = {
    "Generate": {
        "user": "Task: {task}\n\nRespond:"
    }
}
```

### 2. Too Many Instructions

❌ **Bad**: Overloading with instructions
```python
custom_instructions = """
[50 lines of detailed instructions]
"""
# LLM may ignore or poorly follow overly complex instructions
```

✅ **Good**: Keep it focused
```python
custom_instructions = """
1. Use simple language
2. Provide examples
3. Be concise
"""
```

### 3. Conflicting Instructions

❌ **Bad**: Instructions conflict with pattern behavior
```python
# ReAct needs to call tools, but instructions say don't
custom_instructions = "Never use external tools or APIs"
```

✅ **Good**: Align with pattern design
```python
custom_instructions = "Use tools efficiently and explain your tool choices"
```

### 4. Forgetting to Test

Always test customizations with representative tasks before production use.

## Next Steps

- Learn more about [Custom Instructions](custom-instructions.md) in detail
- Explore [Prompt Overrides](prompt-overrides.md) advanced techniques
- See [Setting Agent Goals](setting-goals.md) for objective configuration
- Review [Best Practices](best-practices.md) for production usage

## Reference

### Customization Methods Summary

| Method | Use Case | Priority | Scope | Dynamic |
|--------|----------|----------|-------|---------|
| **File-Based** | Base templates | Medium | All instances | No |
| **Custom Instructions** | Domain context | Low (appended) | All prompts | Yes |
| **Prompt Overrides** | Fine-grained control | High (replaces) | Specific steps | Yes |

### All Template Variables by Pattern

**ReActAgent**:
- `{input}`, `{history}`, `{tool_descriptions}`

**ReflectionAgent**:
- `{task}`, `{output}`, `{reflection}`

**SelfDiscoveryAgent**:
- `{task}`, `{modules}`, `{max_modules}`, `{module_name}`, `{module_description}`, `{module_template}`, `{adapted_modules}`, `{step_description}`, `{previous_results}`, `{reasoning_steps}`

**PlanAndSolveAgent**:
- `{task}`, `{plan}`, `{step}`, `{results}`

**ReflexionAgent**:
- `{task}`, `{attempt}`, `{previous_attempts}`, `{reflection}`

**See individual pattern API documentation for complete lists.**
