# Prompt Customization Guide

This guide explains the three flexible methods for customizing prompts in Agent Patterns.

## Overview

Agent Patterns provides a powerful, flexible system for customizing prompts without modifying the library code. This allows you to:

- Add domain-specific expertise
- Enforce compliance requirements
- Adjust tone, style, and complexity
- A/B test different prompts
- Create specialized pattern variants

## Three Customization Methods

### 1. File-Based Customization (prompt_dir)

**What it does:** Loads prompts from markdown files in a custom directory structure

**When to use:**
- You want to maintain prompts in version control
- You're making extensive changes to many prompts
- You need to share prompt templates across teams
- You want to revert to previous prompt versions

**Example:**

```python
from agent_patterns.patterns import ReActAgent

agent = ReActAgent(
    llm_configs=llm_configs,
    prompt_dir="/path/to/my_prompts"  # Custom prompt directory
)
```

**Directory structure:**
```
my_prompts/
└── ReActAgent/
    └── ThoughtStep/
        ├── system.md    # System prompt
        └── user.md      # User prompt template
```

**Pros:**
- Version controllable
- Easy to review and collaborate on
- Can be templated with standard formats

**Cons:**
- Requires file system access
- Less flexible for runtime customization
- Must maintain directory structure

---

### 2. Custom Instructions (custom_instructions)

**What it does:** Appends domain-specific instructions to ALL system prompts in the workflow

**When to use:**
- Adding domain expertise (medical, legal, financial)
- Enforcing compliance/regulatory requirements
- Setting consistent tone/style across all steps
- Specifying target audience level
- Adding ethical guidelines

**Example:**

```python
from agent_patterns.patterns import SelfDiscoveryAgent

medical_instructions = """
You are providing information in the MEDICAL domain. Guidelines:

1. ACCURACY: Always prioritize medical accuracy
2. DISCLAIMERS: Include appropriate medical disclaimers
3. TERMINOLOGY: Use proper medical terminology but explain complex terms
4. ETHICS: Consider ethical implications and patient privacy
5. RECOMMENDATION: Always recommend consulting healthcare professionals
"""

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=medical_instructions
)
```

**How it works:**
Custom instructions are appended to the system prompt at EVERY step in the workflow:

```
[Original System Prompt]

## Custom Instructions

[Your custom instructions]
```

**Pros:**
- Simple to use
- Applies consistently across all workflow steps
- No file system management needed
- Easy to programmatically generate

**Cons:**
- Less granular control (affects all steps)
- Can't override existing prompts, only append
- Adds to token count for every LLM call

**Use Cases:**

1. **Domain Expertise:**
```python
legal_instructions = """
LEGAL domain - include disclaimers, cite precedents, note jurisdiction
"""
```

2. **Compliance:**
```python
compliance_instructions = """
FINANCIAL COMPLIANCE:
- Include all required disclosures
- Discuss relevant risks
- Avoid promotional language
- This is not financial advice
"""
```

3. **Tone/Style:**
```python
style_instructions = """
COMMUNICATION STYLE:
- Use concise bullet points
- Avoid jargon
- Target audience: non-technical business users
"""
```

4. **Cultural Sensitivity:**
```python
cultural_instructions = """
CULTURAL AWARENESS:
- Respect diverse perspectives
- Use inclusive language
- Avoid cultural assumptions
"""
```

See [examples/custom_instructions_example.py](../examples/custom_instructions_example.py) for comprehensive examples.

---

### 3. Prompt Overrides (prompt_overrides)

**What it does:** Programmatically replaces specific prompts with complete control

**When to use:**
- A/B testing different prompts
- Experimenting with prompt engineering
- Creating specialized pattern variants
- Dynamic prompt generation based on runtime conditions
- Fine-tuning specific workflow steps

**Example:**

```python
from agent_patterns.patterns import SelfDiscoveryAgent

overrides = {
    "DiscoverModules": {
        "system": "You are an expert at selecting reasoning strategies. Be concise.",
        "user": """Task: {task}

Available modules:
{modules}

Select the {max_modules} MOST relevant modules.

Format:
SELECTED: module_name
"""
    },
    "SynthesizeOutput": {
        "system": "You synthesize reasoning steps into clear, actionable answers.",
        "user": "Task: {task}\n\nReasoning:\n{reasoning_steps}\n\nFinal answer:"
    }
}

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=overrides
)
```

**How it works:**
When loading a prompt for a step (e.g., "DiscoverModules"):
1. Check `prompt_overrides` first - if found, use it (complete replacement)
2. Otherwise, load from file system
3. Finally, append `custom_instructions` if provided

**Pros:**
- Complete control over specific prompts
- Can be generated dynamically at runtime
- Perfect for experimentation
- No file system required

**Cons:**
- More verbose than custom_instructions
- Must maintain prompt templates in code
- Can diverge from base prompts

**Use Cases:**

1. **Style Customization:**
```python
concise_overrides = {
    "Generate": {
        "system": "Be extremely concise. Use bullet points. Max 3 sentences per point.",
        "user": "Task: {task}\n\nProvide a concise, bulleted response."
    }
}
```

2. **Socratic Method:**
```python
socratic_overrides = {
    "Reflect": {
        "system": "Use Socratic questioning to improve thinking. Ask probing questions.",
        "user": "Task: {task}\nResponse: {output}\n\nAsk 3-5 questions to improve this:"
    }
}
```

3. **Expert Level:**
```python
expert_overrides = {
    "Generate": {
        "system": "Address PhD-level experts. Use advanced terminology without explanation.",
        "user": "Task: {task}\n\nProvide expert-level technical response."
    }
}
```

4. **Dynamic Overrides:**
```python
def create_overrides_for_task(task: str) -> dict:
    if "calculate" in task.lower():
        return {
            "ExecuteStep": {
                "system": "Show all mathematical work step-by-step.",
                "user": "Step: {step_description}\n\nSolve with calculations:"
            }
        }
    elif "design" in task.lower():
        return {
            "ExecuteStep": {
                "system": "Think creatively. Explore multiple possibilities.",
                "user": "Step: {step_description}\n\nApproach creatively:"
            }
        }
    # ... more conditions

overrides = create_overrides_for_task(user_task)
agent = SelfDiscoveryAgent(llm_configs=llm_configs, prompt_overrides=overrides)
```

See [examples/prompt_overrides_example.py](../examples/prompt_overrides_example.py) for comprehensive examples.

---

## Combining Methods

You can use all three methods together for maximum flexibility:

```python
from agent_patterns.patterns import ReflectionAgent

# Method 1: Custom prompt directory (base templates)
prompt_dir = "my_company_prompts"

# Method 2: Add domain context (applies to all steps)
domain_instructions = """
You are providing SOFTWARE ARCHITECTURE guidance:
- Focus on scalability and maintainability
- Consider trade-offs explicitly
- Include code examples where helpful
- Target audience: Senior engineers
"""

# Method 3: Override specific steps (fine-tuning)
overrides = {
    "Generate": {
        "system": "You create well-structured technical documentation.",
        "user": "Task: {task}\n\nCreate structured documentation with clear sections."
    }
}

agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_dir=prompt_dir,              # 1. Base templates
    custom_instructions=domain_instructions,  # 2. Domain context
    prompt_overrides=overrides          # 3. Specific overrides
)
```

### Priority Order

When a prompt is loaded, the system checks in this order:

1. **`prompt_overrides`** (highest priority)
   - If step name exists in overrides, use it completely (no file loading)

2. **File system (`prompt_dir`)**
   - Load `{prompt_dir}/{ClassName}/{StepName}/system.md`
   - Load `{prompt_dir}/{ClassName}/{StepName}/user.md`

3. **`custom_instructions`** (lowest priority)
   - Appended to system prompt with header: `## Custom Instructions`

**Example flow for "DiscoverModules" step:**

```python
# If overrides provided:
if "DiscoverModules" in prompt_overrides:
    system_prompt = prompt_overrides["DiscoverModules"]["system"]
    user_prompt = prompt_overrides["DiscoverModules"]["user"]
else:
    # Load from files
    system_prompt = read_file("prompts/SelfDiscoveryAgent/DiscoverModules/system.md")
    user_prompt = read_file("prompts/SelfDiscoveryAgent/DiscoverModules/user.md")

# Always append custom instructions if provided
if custom_instructions:
    system_prompt += f"\n\n## Custom Instructions\n\n{custom_instructions}"
```

---

## Decision Guide

**Use `custom_instructions` when:**
- ✅ You want consistent behavior across ALL workflow steps
- ✅ Adding domain expertise, compliance, or ethical guidelines
- ✅ Setting tone/style/audience for entire workflow
- ✅ You want something simple and easy to maintain

**Use `prompt_overrides` when:**
- ✅ You need fine-grained control over specific steps
- ✅ A/B testing or experimenting with prompts
- ✅ Creating specialized variants of patterns
- ✅ Generating prompts dynamically at runtime
- ✅ You want to completely replace specific prompts

**Use `prompt_dir` when:**
- ✅ Making extensive changes to many prompts
- ✅ You want version control for prompts
- ✅ Sharing prompt templates across teams
- ✅ You need to maintain multiple prompt sets

**Combine approaches when:**
- ✅ You need both broad guidelines AND specific customizations
- ✅ Building production systems with multiple requirements
- ✅ Maximum flexibility is required

---

## Best Practices

### 1. Start Simple
Begin with `custom_instructions` for broad guidelines, then add `prompt_overrides` only where needed.

### 2. Test Iteratively
Test your customizations with representative inputs before deploying to production.

### 3. Document Your Prompts
Add comments explaining WHY you customized prompts, not just WHAT you changed.

### 4. Version Control Everything
Store your `custom_instructions` and `prompt_overrides` in version control.

### 5. Monitor Token Usage
Remember that `custom_instructions` are added to EVERY system prompt, affecting costs.

### 6. Use Placeholder Variables
Ensure you use the correct placeholder variables (e.g., `{task}`, `{modules}`) in your overrides.

### 7. Maintain Consistency
If you override multiple steps, ensure they work together coherently.

### 8. Consider Fallbacks
When using dynamic overrides, always have fallback prompts.

---

## Examples Repository

The `examples/` directory contains comprehensive demonstrations:

- **[custom_instructions_example.py](../examples/custom_instructions_example.py)**
  - Medical domain expertise
  - Legal domain compliance
  - Financial regulatory requirements
  - Educational content guidelines
  - Cultural sensitivity

- **[prompt_overrides_example.py](../examples/prompt_overrides_example.py)**
  - Basic single override
  - Multiple step overrides
  - Style customization (concise)
  - Socratic method
  - Expert level content
  - Debugging focus
  - Dynamic runtime overrides
  - Combining with custom_instructions

---

## Technical Implementation

### BaseAgent Changes

The `BaseAgent` class now supports:

```python
class BaseAgent(ABC):
    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        self.prompt_dir = prompt_dir
        self.custom_instructions = custom_instructions
        self.prompt_overrides = prompt_overrides or {}
        # ...
```

### _load_prompt Method

```python
def _load_prompt(self, step_name: str) -> Dict[str, str]:
    system_prompt = ""
    user_prompt = ""

    # Priority 1: Check programmatic overrides
    if step_name in self.prompt_overrides:
        override = self.prompt_overrides[step_name]
        system_prompt = override.get("system", "")
        user_prompt = override.get("user", "")
    else:
        # Priority 2: Load from file system
        class_name = self.__class__.__name__
        prompt_path = Path(self.prompt_dir) / class_name / step_name

        system_file = prompt_path / "system.md"
        if system_file.exists():
            system_prompt = system_file.read_text(encoding="utf-8").strip()

        user_file = prompt_path / "user.md"
        if user_file.exists():
            user_prompt = user_file.read_text(encoding="utf-8").strip()

    # Append custom instructions if provided
    if self.custom_instructions and system_prompt:
        system_prompt = f"{system_prompt}\n\n## Custom Instructions\n\n{self.custom_instructions}"

    return {"system": system_prompt, "user": user_prompt}
```

### Pattern Updates

All patterns now use the consistent keys:
- `prompts["system"]` instead of `prompts["system_prompt"]`
- `prompts["user"]` instead of `prompts["user_prompt"]`

This ensures compatibility with the updated `_load_prompt` method.

---

## FAQ

**Q: Can I use custom_instructions and prompt_overrides together?**
A: Yes! They work together. Overrides replace specific prompts completely, while custom_instructions are still appended to any system prompts (including overridden ones).

**Q: Will custom_instructions affect token costs?**
A: Yes, they're added to every system prompt throughout the workflow, so they affect token usage for every LLM call.

**Q: Can I override just the system prompt or just the user prompt?**
A: Yes, you can provide either or both in your overrides dictionary.

**Q: What happens if I provide an invalid step name in prompt_overrides?**
A: It will be ignored. The agent will fall back to loading from files or using defaults.

**Q: Can I change prompts between runs of the same agent?**
A: Create a new agent instance with different parameters. Agents are designed to be immutable after initialization.

**Q: Do I need to maintain the same placeholder variables in my overrides?**
A: Yes, ensure your overrides use the correct placeholders (like `{task}`, `{modules}`) that the pattern expects.

**Q: Can I use markdown formatting in custom_instructions?**
A: Yes, custom_instructions support markdown formatting.

---

## Support

For questions or issues:
- Open an issue on GitHub
- See examples in `examples/` directory
- Check the main [README.md](../README.md)
