# Prompt Overrides Deep Dive

Complete guide to using `prompt_overrides` for programmatic, runtime control over agent prompts. Perfect for A/B testing, dynamic generation, and creating specialized pattern variants.

## Overview

Prompt overrides provide **complete, programmatic control** over individual prompts in an agent's workflow. Unlike custom instructions (which append to prompts) or file-based prompts (which require file changes), overrides **completely replace** specific prompts at runtime.

### Key Characteristics

- **Complete replacement**: Overrides replace prompts entirely
- **Surgical precision**: Override only the steps you need
- **Runtime flexibility**: Generate prompts dynamically based on conditions
- **No file changes**: Everything in code
- **Highest priority**: Overrides trump all other customization methods

## How Prompt Overrides Work

### Structure

Prompt overrides are a dictionary mapping step names to prompt dictionaries:

```python
prompt_overrides = {
    "StepName": {
        "system": "Custom system prompt",
        "user": "Custom user prompt with {variables}"
    }
}
```

### Important Note About v0.2.0 Comprehensive Prompts

When you use prompt overrides in v0.2.0, you're **replacing enterprise-grade comprehensive prompts** (150-300+ lines with 9 sections) with your custom prompt.

**Two approaches**:
1. **Simple override**: Replace with a concise custom prompt (quick but loses comprehensive structure)
2. **Comprehensive override**: Maintain the 9-section structure in your override (recommended for production)

### Example: Simple Override

```python
from agent_patterns.patterns import SelfDiscoveryAgent

# Simple override (concise but loses comprehensive structure)
simple_overrides = {
    "DiscoverModules": {
        "system": "You are an expert at selecting reasoning strategies.",
        "user": "Task: {task}\n\nModules:\n{modules}\n\nSelect {max_modules}:"
    }
}

agent = SelfDiscoveryAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model": "gpt-4"},
        "execution": {"provider": "openai", "model": "gpt-4"}
    },
    prompt_overrides=simple_overrides
)
```

### Example: Comprehensive Override (Recommended)

```python
# Comprehensive override (maintains enterprise-grade structure)
comprehensive_overrides = {
    "DiscoverModules": {
        "system": """# Role and Identity
You are the Module Selection Specialist with expertise in matching reasoning strategies to tasks.

# Core Capabilities
**What You CAN Do:**
- Analyze task requirements systematically
- Evaluate reasoning module applicability
- Select optimal module combinations
- Justify module selections clearly

**What You CANNOT Do:**
- Select more modules than max_modules allows
- Create new modules not in the provided list
- Make arbitrary selections without reasoning
- Skip the selection process

# Process
1. Analyze the task thoroughly
2. Review available modules
3. Match task needs to module strengths
4. Select best-fit modules
5. Verify selection meets requirements

# Output Format
Output each selected module on its own line:
SELECTED: module_name

# Quality Standards
Excellent selections are:
- Well-matched to task requirements
- Diverse and complementary
- Justified by task characteristics
- Within the specified limit

# Examples
[2-3 examples of task -> module selection]

# Critical Reminders
- Respect the max_modules limit
- Only select from provided modules
- One SELECTED line per module""",
        "user": "Task: {task}\n\nModules:\n{modules}\n\nSelect {max_modules}:"
    }
}
```

**Recommendation**: For production use, maintain the comprehensive structure to preserve reliability and robustness benefits.

### What Gets Replaced

When you provide an override:

```python
overrides = {
    "Generate": {
        "system": "You are a concise writer.",
        "user": "Task: {task}\n\nRespond briefly:"
    }
}
```

The agent uses:
- **System prompt**: "You are a concise writer." (override completely replaces file/default)
- **User prompt**: "Task: {task}\n\nRespond briefly:" (override completely replaces file/default)

Custom instructions are **still appended** to the overridden system prompt:

```python
agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions="DOMAIN: Medical",
    prompt_overrides=overrides
)

# Final system prompt: "You are a concise writer.\n\n## Custom Instructions\n\nDOMAIN: Medical"
```

## Use Cases

### 1. A/B Testing Prompts

Compare different prompt variations to optimize performance:

```python
def test_prompt_variations(task: str):
    """A/B test different prompt strategies."""

    # Variation A: Detailed prompting
    overrides_a = {
        "Generate": {
            "system": """You are a thorough assistant. For each response:
1. Consider multiple perspectives
2. Provide detailed explanations
3. Include relevant examples
4. Cite sources when applicable""",
            "user": "Task: {task}\n\nProvide a comprehensive response:"
        }
    }

    # Variation B: Concise prompting
    overrides_b = {
        "Generate": {
            "system": "You are a concise assistant. Be brief and direct.",
            "user": "Task: {task}\n\nBrief response:"
        }
    }

    agent_a = ReflectionAgent(llm_configs=llm_configs, prompt_overrides=overrides_a)
    agent_b = ReflectionAgent(llm_configs=llm_configs, prompt_overrides=overrides_b)

    result_a = agent_a.run(task)
    result_b = agent_b.run(task)

    # Compare results
    print(f"Variation A (Detailed):\n{result_a}\n")
    print(f"Variation B (Concise):\n{result_b}\n")

    return {
        "a_length": len(result_a),
        "b_length": len(result_b),
        "a_result": result_a,
        "b_result": result_b
    }
```

### 2. Dynamic Prompt Generation

Generate prompts based on runtime conditions:

```python
def create_overrides_for_task(task: str) -> dict:
    """Dynamically create overrides based on task characteristics."""

    # Detect task type
    if any(word in task.lower() for word in ["calculate", "solve", "equation", "math"]):
        # Mathematical tasks: emphasize step-by-step calculation
        return {
            "ExecuteStep": {
                "system": "You are a mathematical problem solver. Show all work step-by-step.",
                "user": "Step: {step_description}\n\nSolve this step, showing all calculations:"
            }
        }

    elif any(word in task.lower() for word in ["design", "create", "write", "story"]):
        # Creative tasks: emphasize exploration
        return {
            "ExecuteStep": {
                "system": "You are a creative thinker. Explore multiple possibilities.",
                "user": "Step: {step_description}\n\nApproach this creatively with multiple ideas:"
            }
        }

    elif any(word in task.lower() for word in ["analyze", "compare", "evaluate"]):
        # Analytical tasks: emphasize systematic analysis
        return {
            "ExecuteStep": {
                "system": "You are an analytical problem solver. Use logic and evidence.",
                "user": "Step: {step_description}\n\nAnalyze this systematically:"
            }
        }

    else:
        # Default: balanced approach
        return {}

# Use dynamic overrides
task1 = "Calculate the compound interest on $10,000 at 5% for 10 years"
agent1 = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=create_overrides_for_task(task1)
)
result1 = agent1.run(task1)

task2 = "Design a logo for a sustainable tech startup"
agent2 = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=create_overrides_for_task(task2)
)
result2 = agent2.run(task2)
```

### 3. Style Customization

Create different communication styles:

#### Concise Style

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
    prompt_overrides=concise_overrides,
    max_reflection_cycles=1
)
```

#### Socratic Method

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
    prompt_overrides=socratic_overrides,
    max_reflection_cycles=1
)

result = agent.run("Why is the sky blue?")
```

#### Expert vs Beginner Level

```python
# Expert-level prompts
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

# Beginner-level prompts
beginner_overrides = {
    "Generate": {
        "system": """You are teaching complete beginners.
- Define all technical terms
- Use simple analogies and examples
- Break down complex concepts step-by-step
- Check for understanding
- Be patient and encouraging""",
        "user": "Task: {task}\n\nExplain this for someone with no background knowledge:"
    }
}

# Use based on audience
expert_agent = ReflectionAgent(llm_configs=llm_configs, prompt_overrides=expert_overrides)
beginner_agent = ReflectionAgent(llm_configs=llm_configs, prompt_overrides=beginner_overrides)
```

### 4. Debugging and Development

Override prompts to add debugging information:

```python
debugging_overrides = {
    "ExecuteStep": {
        "system": """You are executing a reasoning step. Be explicit about your process:
1. Restate what you're being asked to do
2. Explain your approach
3. Execute the step
4. Verify your result
5. Note any assumptions or limitations""",
        "user": """Step: {step_description}

Previous results:
{previous_results}

Execute this step with explicit reasoning:"""
    }
}

debug_agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=debugging_overrides
)
```

### 5. Specialized Variants

Create specialized versions of patterns:

```python
# Code review variant of Reflection
code_review_overrides = {
    "Reflect": {
        "system": """You are an expert code reviewer. Evaluate code for:
1. CORRECTNESS: Does it work as intended?
2. PERFORMANCE: Are there efficiency issues?
3. SECURITY: Are there security vulnerabilities?
4. MAINTAINABILITY: Is it clean and well-documented?
5. BEST PRACTICES: Does it follow language idioms?

Provide specific, actionable feedback with code examples.""",
        "user": """Code to review:
{output}

Provide a thorough code review:"""
    }
}

code_reviewer = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=code_review_overrides
)

# Mathematical proof variant of Reflexion
proof_checking_overrides = {
    "Reflect": {
        "system": """You are checking a mathematical proof. Examine:
1. LOGIC: Are the logical steps valid?
2. ASSUMPTIONS: Are all assumptions stated and justified?
3. COMPLETENESS: Are all cases covered?
4. RIGOR: Is the proof rigorous enough?
5. CLARITY: Is the argument clear?

Identify gaps, errors, or areas needing clarification.""",
        "user": """Proof attempt:
{previous_attempt}

Evaluate this proof:"""
    }
}

proof_checker = ReflexionAgent(
    llm_configs=llm_configs,
    prompt_overrides=proof_checking_overrides
)
```

## Pattern-Specific Examples

### ReAct Pattern

```python
from agent_patterns.patterns import ReActAgent

# Override thought process to be more methodical
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
    prompt_overrides=react_overrides
)
```

### Self-Discovery Pattern

```python
from agent_patterns.patterns import SelfDiscoveryAgent

# Override multiple steps for a specialized variant
discovery_overrides = {
    "DiscoverModules": {
        "system": "You select reasoning strategies efficiently. Prefer proven methods.",
        "user": "Task: {task}\n\nModules:\n{modules}\n\nSelect top {max_modules}:"
    },
    "AdaptModules": {
        "system": "You adapt strategies to specific contexts.",
        "user": "Task: {task}\n\nModule: {module_name}\n\nHow to apply it here:"
    },
    "SynthesizeOutput": {
        "system": "You create clear, actionable final answers.",
        "user": "Task: {task}\n\nReasoning:\n{reasoning_steps}\n\nFinal answer:"
    }
}

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=discovery_overrides,
    max_selected_modules=3
)
```

### Reflection Pattern

```python
from agent_patterns.patterns import ReflectionAgent

# Override to create a technical writing editor
tech_writing_overrides = {
    "Generate": {
        "system": "You are a technical writer creating clear documentation.",
        "user": "Topic: {task}\n\nWrite clear technical documentation:"
    },
    "Reflect": {
        "system": """You are an editor reviewing technical documentation for:
- Clarity: Is it easy to understand?
- Accuracy: Is it technically correct?
- Completeness: Does it cover all necessary details?
- Examples: Are there helpful code examples?
- Structure: Is it well-organized?""",
        "user": "Documentation:\n{output}\n\nReview and provide feedback:"
    },
    "Refine": {
        "system": "You improve technical documentation based on editor feedback.",
        "user": "Topic: {task}\n\nDraft:\n{output}\n\nFeedback:\n{reflection}\n\nImproved version:"
    }
}

tech_writer = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=tech_writing_overrides
)
```

### Reflexion Pattern

```python
from agent_patterns.patterns import ReflexionAgent

# Override for systematic debugging
debugging_overrides = {
    "Reflect": {
        "system": """You are a debugging expert. Analyze failed attempts systematically:
1. What was the approach?
2. Where exactly did it fail?
3. What assumptions were incorrect?
4. What edge cases weren't considered?
5. What should be tried next?

Be specific and technical.""",
        "user": """Task: {task}

Attempt #{attempt_number}:
{previous_attempt}

Result: FAILED
Error/Issue: {failure_reason}

Analyze what went wrong and suggest corrections:"""
    }
}

debugger = ReflexionAgent(
    llm_configs=llm_configs,
    prompt_overrides=debugging_overrides,
    max_trials=3
)
```

## Advanced Techniques

### Conditional Overrides

```python
def get_overrides_for_context(
    audience: str,
    task_type: str,
    urgency: str
) -> dict:
    """Generate overrides based on multiple factors."""

    overrides = {}

    # Adjust based on audience
    if audience == "technical":
        system_base = "You are addressing technical experts. Use precise terminology."
    elif audience == "business":
        system_base = "You are addressing business stakeholders. Focus on value and ROI."
    else:
        system_base = "You are addressing a general audience. Use clear, accessible language."

    # Adjust based on task type
    if task_type == "analysis":
        system_base += " Provide thorough analysis with evidence."
    elif task_type == "summary":
        system_base += " Be concise and focus on key points."
    elif task_type == "recommendation":
        system_base += " Provide clear recommendations with justification."

    # Adjust based on urgency
    if urgency == "high":
        system_base += " Prioritize speed and clarity."
        user_template = "Task: {task}\n\nQuick response needed:"
    else:
        system_base += " Be thorough and comprehensive."
        user_template = "Task: {task}\n\nDetailed response:"

    overrides["Generate"] = {
        "system": system_base,
        "user": user_template
    }

    return overrides

# Use conditional overrides
context = {
    "audience": "technical",
    "task_type": "analysis",
    "urgency": "high"
}

agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=get_overrides_for_context(**context)
)
```

### Template-Based Overrides

```python
class PromptTemplates:
    """Reusable prompt templates."""

    CONCISE_SYSTEM = "You are concise. Maximum {max_sentences} sentences."
    DETAILED_SYSTEM = "You are thorough. Provide comprehensive analysis."
    STRUCTURED_SYSTEM = "You provide structured responses with clear sections."

    BEGINNER_USER = "Task: {task}\n\nExplain for beginners:"
    EXPERT_USER = "Task: {task}\n\nExpert-level response:"
    QUICK_USER = "Task: {task}\n\nBrief answer:"

    @classmethod
    def concise_variant(cls, max_sentences: int = 3) -> dict:
        """Create concise prompts."""
        return {
            "Generate": {
                "system": cls.CONCISE_SYSTEM.format(max_sentences=max_sentences),
                "user": cls.QUICK_USER
            }
        }

    @classmethod
    def beginner_variant(cls) -> dict:
        """Create beginner-friendly prompts."""
        return {
            "Generate": {
                "system": "You teach beginners. Define all terms. Use simple examples.",
                "user": cls.BEGINNER_USER
            }
        }

    @classmethod
    def expert_variant(cls) -> dict:
        """Create expert-level prompts."""
        return {
            "Generate": {
                "system": "You address experts. Use advanced terminology. Discuss nuances.",
                "user": cls.EXPERT_USER
            }
        }

# Use template-based overrides
agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=PromptTemplates.concise_variant(max_sentences=5)
)
```

### Inheritance and Composition

```python
class OverrideBuilder:
    """Build overrides through composition."""

    BASE_OVERRIDES = {
        "Generate": {
            "system": "You are a helpful assistant.",
            "user": "Task: {task}\n\nRespond:"
        }
    }

    @classmethod
    def with_tone(cls, tone: str) -> dict:
        """Add tone to base overrides."""
        overrides = cls.BASE_OVERRIDES.copy()
        overrides["Generate"]["system"] += f" Tone: {tone}."
        return overrides

    @classmethod
    def with_format(cls, format_type: str) -> dict:
        """Add format requirements."""
        overrides = cls.BASE_OVERRIDES.copy()
        format_instructions = {
            "bullets": " Use bullet points for all lists.",
            "numbered": " Use numbered lists for sequential items.",
            "structured": " Use clear headings and sections."
        }
        overrides["Generate"]["system"] += format_instructions.get(format_type, "")
        return overrides

    @classmethod
    def with_constraints(cls, max_length: int) -> dict:
        """Add length constraints."""
        overrides = cls.BASE_OVERRIDES.copy()
        overrides["Generate"]["system"] += f" Maximum {max_length} words."
        return overrides

    @classmethod
    def build(cls, tone: str = None, format_type: str = None, max_length: int = None) -> dict:
        """Build overrides with multiple features."""
        overrides = cls.BASE_OVERRIDES.copy()

        if tone:
            overrides = cls.with_tone(tone)
        if format_type:
            current = overrides["Generate"]["system"]
            overrides["Generate"]["system"] = current + cls.with_format(format_type)["Generate"]["system"].split(".", 1)[1]
        if max_length:
            current = overrides["Generate"]["system"]
            overrides["Generate"]["system"] = current + f" Maximum {max_length} words."

        return overrides

# Use composed overrides
agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=OverrideBuilder.build(
        tone="professional",
        format_type="structured",
        max_length=500
    )
)
```

## Best Practices

### 1. Preserve Template Variables

Always use the correct template variables for each step:

❌ **Bad**: Wrong variables
```python
overrides = {
    "Generate": {
        "user": "Question: {input}\n\nAnswer:"  # Wrong! Should be {task}
    }
}
```

✅ **Good**: Correct variables
```python
overrides = {
    "Generate": {
        "user": "Task: {task}\n\nAnswer:"  # Correct variable for ReflectionAgent
    }
}
```

Check pattern documentation for valid variables for each step.

### 2. Override Only What You Need

Don't override everything—only the steps you want to change:

❌ **Bad**: Overriding all steps unnecessarily
```python
overrides = {
    "Generate": {...},
    "Reflect": {...},
    "Refine": {...},
    "CheckCycle": {...},  # Unnecessary
    # ... etc
}
```

✅ **Good**: Override only what needs changing
```python
overrides = {
    "Generate": {
        "system": "Be concise.",
        "user": "Task: {task}\n\nBrief response:"
    }
    # Other steps use default prompts
}
```

### 3. Test Overrides Thoroughly

```python
def test_prompt_override():
    """Test that overrides are applied correctly."""
    overrides = {
        "Generate": {
            "system": "TEST_SYSTEM_PROMPT",
            "user": "TEST_USER_PROMPT {task}"
        }
    }

    agent = ReflectionAgent(
        llm_configs=llm_configs,
        prompt_overrides=overrides
    )

    # Verify override is loaded
    prompt_data = agent._load_prompt("Generate")
    assert "TEST_SYSTEM_PROMPT" in prompt_data["system"]
    assert "TEST_USER_PROMPT" in prompt_data["user"]
```

### 4. Document Your Overrides

```python
class PromptOverrides:
    """Centralized prompt overrides with documentation."""

    CONCISE_REFLECTION = {
        """
        Concise variant of Reflection pattern.
        Use for quick iterations where brevity is important.

        Changes:
        - Generate: Emphasizes brevity
        - Refine: Focuses on making responses even shorter

        Best for: Quick answers, summaries, bullet points
        """
        "Generate": {
            "system": "Be extremely concise. Use bullet points.",
            "user": "Task: {task}\n\nBrief response:"
        },
        "Refine": {
            "system": "Make this even more concise.",
            "user": "Current: {output}\n\nFeedback: {reflection}\n\nShorter version:"
        }
    }

    SOCRATIC_REFLECTION = {
        """
        Socratic variant of Reflection pattern.
        Uses questions to guide thinking instead of direct critique.

        Changes:
        - Reflect: Asks probing questions instead of providing critique

        Best for: Educational contexts, developing critical thinking
        """
        "Reflect": {
            "system": "Ask Socratic questions to improve thinking.",
            "user": "Task: {task}\n\nResponse: {output}\n\nQuestions:"
        }
    }
```

### 5. Version Control Overrides

```python
# overrides_v1.py
CONCISE_V1 = {
    "Generate": {
        "system": "Be brief.",
        "user": "Task: {task}\n\nShort answer:"
    }
}

# overrides_v2.py
CONCISE_V2 = {
    "Generate": {
        "system": "Be brief. Use bullet points. Maximum 3 sentences per point.",
        "user": "Task: {task}\n\nConcise, bulleted response:"
    }
}

# Use versioned overrides
from overrides_v2 import CONCISE_V2

agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=CONCISE_V2
)
```

### 6. Combine with Custom Instructions

Overrides and custom instructions work together:

```python
# Overrides: Change specific prompts
overrides = {
    "Generate": {
        "system": "You create structured responses.",
        "user": "Task: {task}\n\nStructured response:"
    }
}

# Custom instructions: Add domain context
instructions = "DOMAIN: Medical. Always cite sources."

# Both are applied
agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions=instructions,  # Appended to ALL system prompts
    prompt_overrides=overrides  # Replaces specific prompts
)

# Final Generate system prompt:
# "You create structured responses.\n\n## Custom Instructions\n\nDOMAIN: Medical. Always cite sources."
```

## Finding Step Names

To use overrides, you need to know the step names for each pattern. Here's how to find them:

### Method 1: Check Pattern Source Code

```python
# Look at pattern implementation
from agent_patterns.patterns import ReflectionAgent
import inspect

# Get the source code
source = inspect.getsource(ReflectionAgent)
print(source)

# Look for _load_prompt() calls
# Example: self._load_prompt("Generate") → step name is "Generate"
```

### Method 2: Check Prompt Directory

```bash
# List step directories
ls agent_patterns/prompts/ReflectionAgent/
# Output: Generate/ Reflect/ Refine/
```

### Method 3: Pattern Documentation

Each pattern's documentation lists all step names and their purposes.

### Common Step Names by Pattern

**ReActAgent**:
- `ThoughtStep`

**ReflectionAgent**:
- `Generate`
- `Reflect`
- `Refine`

**SelfDiscoveryAgent**:
- `DiscoverModules`
- `AdaptModules`
- `PlanReasoning`
- `ExecuteStep`
- `SynthesizeOutput`

**PlanAndSolveAgent**:
- `Plan`
- `Execute`
- `Document`

**ReflexionAgent**:
- `Execute`
- `Reflect`

## Common Pitfalls

### 1. Typos in Step Names

❌ **Bad**: Typo in step name
```python
overrides = {
    "Generrate": {...}  # Typo! Should be "Generate"
}
# Override silently ignored
```

✅ **Good**: Correct step name
```python
overrides = {
    "Generate": {...}
}
```

### 2. Missing Required Variables

❌ **Bad**: Missing required template variable
```python
overrides = {
    "Generate": {
        "user": "Provide an answer"  # Missing {task} variable!
    }
}
# Will cause KeyError at runtime
```

✅ **Good**: All required variables present
```python
overrides = {
    "Generate": {
        "user": "Task: {task}\n\nProvide an answer"
    }
}
```

### 3. Overriding Both System and User When Only One Needed

```python
# If you only want to change the user prompt, don't override system
overrides = {
    "Generate": {
        "user": "Task: {task}\n\nCustom format:"
        # System prompt will use default/file
    }
}
```

### 4. Forgetting About Custom Instructions

Remember that custom instructions are appended to overridden system prompts too:

```python
overrides = {"Generate": {"system": "Short prompt"}}
instructions = "Long detailed instructions..."

# Final system: "Short prompt\n\n## Custom Instructions\n\nLong detailed instructions..."
# Might conflict with intention of short prompt!
```

## Troubleshooting

### Override Not Applied

**Problem**: Override doesn't seem to take effect

**Solutions**:
1. Verify step name is correct (check source code or docs)
2. Ensure override dictionary structure is correct
3. Check for typos in step name
4. Verify you're testing the right step

### Template Variable Error

**Problem**: KeyError for missing variable

**Solutions**:
1. Check pattern documentation for required variables
2. Include all variables used in original prompt
3. Test with simple prompts first

### Conflicts with Custom Instructions

**Problem**: Override and custom instructions conflict

**Solutions**:
1. Remember instructions are appended to system prompt
2. Design overrides with instructions in mind
3. Keep overrides and instructions aligned

## Next Steps

- Review [Custom Instructions](custom-instructions.md) for complementary approach
- Learn about [Setting Agent Goals](setting-goals.md)
- See [Prompt Customization](prompt-customization.md) for overview
- Explore [Best Practices](best-practices.md) for production usage

## Reference

### Complete Example from Repository

See `/ai/work/claude-code/agent-patterns/examples/prompt_overrides_example.py` for:
- Basic override example
- Multiple overrides example
- Style customization (concise, Socratic, expert)
- Debugging-focused variant
- Combining with custom instructions
- Dynamic override generation
- And more...

### Key Takeaways

1. Overrides **completely replace** specific prompts
2. They have **highest priority** over file-based and custom instructions
3. Perfect for **A/B testing** and **experimentation**
4. Can be **generated dynamically** at runtime
5. Work on **individual steps** independently
6. Custom instructions are **still appended** to overridden system prompts
7. Must use **correct step names** and **template variables**
8. Great for creating **specialized pattern variants**
