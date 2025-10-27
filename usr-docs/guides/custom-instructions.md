# Custom Instructions Deep Dive

Comprehensive guide to using the `custom_instructions` parameter to add domain-specific expertise, constraints, and guidelines to any agent pattern.

## Overview

Custom instructions are a powerful yet simple way to inject domain-specific knowledge, ethical guidelines, compliance requirements, or stylistic preferences into your agents **without modifying prompt files or code**.

### Key Characteristics

- **Appended to all system prompts** throughout the workflow
- **Pattern-agnostic**: Works with any agent pattern
- **Persistent**: Applied to every reasoning step automatically
- **Simple**: Just a string parameter
- **Composable**: Can be generated dynamically

## How Custom Instructions Work

### Under the Hood

When you provide `custom_instructions`, they are automatically appended to every system prompt:

```python
# Your code
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions="You are a medical expert. Always cite sources."
)

# What the LLM actually receives (v0.2.0 with comprehensive prompts)
system_prompt = """
# Role and Identity
You are the Module Discovery Specialist in a Self-Discovery workflow...
[~150-300 lines of comprehensive prompt with 9 sections]

## Custom Instructions

You are a medical expert. Always cite sources.
"""
```

**New in v0.2.0**: Custom instructions are now appended to **enterprise-grade comprehensive prompts** (150-300+ lines) instead of basic prompts (~32 lines). This means your domain-specific instructions build on top of a much more robust foundation, providing both comprehensive guidance AND your specialized context.

This happens for **every step** in the agent's workflow:
- Discovery steps
- Adaptation steps
- Planning steps
- Execution steps
- Synthesis steps

### Example Flow

```python
from agent_patterns.patterns import SelfDiscoveryAgent

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions="DOMAIN: Medical. Always cite sources."
)

# When agent runs:
# 1. DiscoverModules step → system prompt includes "DOMAIN: Medical..."
# 2. AdaptModules step → system prompt includes "DOMAIN: Medical..."
# 3. PlanReasoning step → system prompt includes "DOMAIN: Medical..."
# 4. ExecuteStep step → system prompt includes "DOMAIN: Medical..."
# 5. SynthesizeOutput step → system prompt includes "DOMAIN: Medical..."
```

## Domain-Specific Examples

### Medical Domain

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
    custom_instructions=medical_instructions,
    max_selected_modules=3
)

result = agent.run("What are the key considerations for diagnosing Type 2 Diabetes?")
```

**Expected Behavior**:
- Uses proper medical terminology
- Includes disclaimers about consulting healthcare professionals
- Cites evidence-based guidelines
- Acknowledges AI limitations in medical diagnosis

### Legal Domain

```python
from agent_patterns.patterns import STORMAgent

legal_instructions = """
You are providing information in the LEGAL domain. Follow these guidelines:

1. JURISDICTION: Be clear about which jurisdiction's laws you're discussing
2. DISCLAIMERS: Include appropriate legal disclaimers (not legal advice)
3. CITATIONS: Reference specific laws, regulations, or case precedents when possible
4. NEUTRALITY: Present balanced views when discussing legal interpretations
5. UPDATES: Note that laws change and information may become outdated
6. RECOMMENDATION: Always recommend consulting licensed attorneys for legal advice
"""

def mock_search(query: str) -> str:
    # Your actual search implementation
    return f"Legal information about: {query}"

agent = STORMAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model": "gpt-4"},
        "documentation": {"provider": "openai", "model": "gpt-4"}
    },
    retrieval_tools={"search": mock_search},
    custom_instructions=legal_instructions
)

result = agent.run("Overview of intellectual property rights for software")
```

**Expected Behavior**:
- Specifies jurisdiction (e.g., "Under U.S. law...")
- Includes disclaimers ("This is not legal advice")
- References specific laws or regulations
- Recommends consulting attorneys for specific cases

### Financial Compliance

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
    llm_configs={
        "thinking": {"provider": "openai", "model": "gpt-4"},
        "execution": {"provider": "openai", "model": "gpt-4"}
    },
    custom_instructions=compliance_instructions,
    max_selected_modules=4
)

result = agent.run("Explain the pros and cons of index funds versus actively managed funds")
```

**Expected Behavior**:
- Discusses both benefits and risks
- Uses balanced, objective language
- Includes financial disclaimers
- Explains concepts clearly for non-experts
- Avoids specific investment recommendations

### Educational Content

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

agent = SelfDiscoveryAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model": "gpt-4"},
        "execution": {"provider": "openai", "model": "gpt-4"}
    },
    custom_instructions=educational_instructions
)

result = agent.run("Explain how photosynthesis works")
```

**Expected Behavior**:
- Starts with simple concepts, builds to complex
- Uses age-appropriate language and examples
- Includes questions to promote engagement
- Explains the "why" behind processes
- May include self-check questions

### Technical Documentation

```python
technical_docs_instructions = """
You are creating TECHNICAL DOCUMENTATION. Follow these standards:

1. PRECISION: Use precise technical terminology correctly
2. COMPLETENESS: Cover all necessary details including edge cases
3. EXAMPLES: Provide code examples and usage patterns
4. STRUCTURE: Use clear headings, sections, and formatting
5. AUDIENCE: Write for developers with intermediate to advanced skills
6. CONTEXT: Explain the "why" behind design decisions
7. WARNINGS: Highlight potential pitfalls and gotchas

FORMAT:
- Use code blocks for code examples
- Use tables for comparing options
- Use bullet points for lists
- Include both conceptual explanations and practical examples
"""

agent = ReflectionAgent(
    llm_configs={
        "documentation": {"provider": "openai", "model": "gpt-4"},
        "reflection": {"provider": "openai", "model": "gpt-4"}
    },
    custom_instructions=technical_docs_instructions
)

result = agent.run("Document the authentication flow for our REST API")
```

### Cultural Sensitivity

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

def search_cross_cultural(query: str) -> str:
    # Your search implementation
    return f"Cross-cultural information about: {query}"

agent = STORMAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model": "gpt-4"},
        "documentation": {"provider": "openai", "model": "gpt-4"}
    },
    retrieval_tools={"search": search_cross_cultural},
    custom_instructions=cultural_instructions
)

result = agent.run("Communication styles in business settings")
```

### Accessibility Guidelines

```python
accessibility_instructions = """
You are creating ACCESSIBLE CONTENT. Follow WCAG 2.1 AA guidelines:

1. CLARITY: Use simple, clear language (aim for 8th grade reading level)
2. STRUCTURE: Use proper heading hierarchy and semantic structure
3. ALTERNATIVES: Describe images, charts, and visual content in text
4. CONTRAST: When discussing design, mention color contrast requirements
5. KEYBOARD: Consider keyboard-only navigation in UI descriptions
6. SCREEN READERS: Think about how content sounds when read aloud
7. INCLUSIVITY: Use person-first or identity-first language appropriately

AVOID:
- Idioms or cultural references without explanation
- Color-only information ("click the red button" → "click the Submit button (red)")
- Complex jargon without definitions
"""

agent = ReflectionAgent(
    llm_configs={
        "documentation": {"provider": "openai", "model": "gpt-4"},
        "reflection": {"provider": "openai", "model": "gpt-4"}
    },
    custom_instructions=accessibility_instructions
)

result = agent.run("Create a user guide for our mobile app")
```

### Scientific Research

```python
scientific_instructions = """
You are conducting SCIENTIFIC RESEARCH. Follow the scientific method:

1. RIGOR: Apply rigorous scientific methodology and critical thinking
2. EVIDENCE: Base conclusions on empirical evidence, not assumptions
3. CITATIONS: Reference peer-reviewed sources and studies
4. METHODOLOGY: Clearly describe methods and reasoning
5. UNCERTAINTY: Acknowledge limitations, uncertainties, and confidence levels
6. OBJECTIVITY: Minimize bias and consider alternative explanations
7. REPRODUCIBILITY: Provide enough detail for others to verify findings
8. PEER REVIEW: Consider how findings would hold up to peer review

STRUCTURE:
- State hypotheses clearly
- Describe methodology
- Present findings objectively
- Discuss limitations
- Draw appropriate conclusions
"""

agent = SelfDiscoveryAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model": "gpt-4"},
        "execution": {"provider": "openai", "model": "gpt-4"}
    },
    custom_instructions=scientific_instructions
)

result = agent.run("Analyze the relationship between exercise and cognitive function")
```

### Customer Service

```python
customer_service_instructions = """
You are a CUSTOMER SERVICE AGENT. Follow these principles:

1. EMPATHY: Show genuine empathy and understanding
2. CLARITY: Communicate clearly and avoid jargon
3. EFFICIENCY: Resolve issues quickly without sacrificing quality
4. ESCALATION: Know when to escalate to human agents
5. DOCUMENTATION: Keep clear records of interactions
6. FOLLOW-UP: Ensure customer satisfaction before closing
7. BOUNDARIES: Stay within your capabilities and authority

TONE:
- Professional yet friendly
- Patient and non-judgmental
- Positive and solution-focused
- Apologetic when appropriate

PROHIBITED:
- Making promises outside your authority
- Sharing confidential customer information
- Being defensive or argumentative
"""

agent = ReActAgent(
    llm_configs={"thinking": {"provider": "openai", "model": "gpt-4"}},
    tools=customer_service_tools,
    custom_instructions=customer_service_instructions
)

result = agent.run("Customer says their order hasn't arrived")
```

## Advanced Patterns

### Multi-Concern Instructions

Combine multiple concerns in a single set of instructions:

```python
multi_concern_instructions = """
DOMAIN: Healthcare Technology
AUDIENCE: Medical professionals and IT administrators
COMPLIANCE: HIPAA, GDPR

Guidelines:
1. TECHNICAL ACCURACY: Use correct medical and technical terminology
2. PRIVACY: Never discuss or request patient-identifiable information
3. SECURITY: Emphasize security best practices for healthcare data
4. INTEROPERABILITY: Consider HL7, FHIR, and other healthcare standards
5. USABILITY: Balance technical depth with clinical usability
6. DISCLAIMERS: Include appropriate medical and technical disclaimers

PROHIBITED:
- Discussing specific patient cases
- Making clinical recommendations
- Bypassing security measures
- Sharing sensitive configuration details
"""

agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions=multi_concern_instructions
)
```

### Dynamic Instructions

Generate instructions based on runtime context:

```python
def create_instructions_for_user(user_role: str, user_expertise: str) -> str:
    """Generate custom instructions based on user profile."""

    base = "You are a helpful assistant.\n\n"

    # Adjust based on role
    if user_role == "developer":
        base += "AUDIENCE: Software developers\n"
        base += "- Provide code examples\n"
        base += "- Use technical terminology\n"
        base += "- Discuss implementation details\n\n"
    elif user_role == "manager":
        base += "AUDIENCE: Business managers\n"
        base += "- Focus on business value and ROI\n"
        base += "- Minimize technical jargon\n"
        base += "- Emphasize strategic implications\n\n"
    elif user_role == "student":
        base += "AUDIENCE: Students learning the topic\n"
        base += "- Explain concepts from first principles\n"
        base += "- Provide educational examples\n"
        base += "- Include learning resources\n\n"

    # Adjust based on expertise
    if user_expertise == "beginner":
        base += "EXPERTISE LEVEL: Beginner\n"
        base += "- Define all technical terms\n"
        base += "- Use simple analogies\n"
        base += "- Provide step-by-step guidance\n"
    elif user_expertise == "expert":
        base += "EXPERTISE LEVEL: Expert\n"
        base += "- Use advanced terminology without definition\n"
        base += "- Focus on nuances and edge cases\n"
        base += "- Reference state-of-the-art approaches\n"

    return base

# Use dynamic instructions
user_profile = {"role": "developer", "expertise": "expert"}
instructions = create_instructions_for_user(
    user_role=user_profile["role"],
    user_expertise=user_profile["expertise"]
)

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=instructions
)
```

### Context-Aware Instructions

Adjust instructions based on the task:

```python
def get_instructions_for_task(task: str) -> str:
    """Generate instructions based on task type."""

    # Detect task type
    if "debug" in task.lower() or "error" in task.lower():
        return """
TASK TYPE: Debugging

Approach:
1. Reproduce the error systematically
2. Isolate the root cause
3. Propose minimal fixes
4. Test the solution
5. Explain what went wrong and why

Be methodical and evidence-based.
"""

    elif "design" in task.lower() or "architecture" in task.lower():
        return """
TASK TYPE: System Design

Approach:
1. Clarify requirements and constraints
2. Consider multiple design alternatives
3. Evaluate trade-offs
4. Recommend approach with justification
5. Identify potential risks and mitigations

Think holistically about the system.
"""

    elif "optimize" in task.lower() or "performance" in task.lower():
        return """
TASK TYPE: Optimization

Approach:
1. Measure current performance baseline
2. Identify bottlenecks through profiling
3. Consider algorithmic and implementation optimizations
4. Evaluate trade-offs (speed vs memory, complexity vs maintainability)
5. Verify improvements with benchmarks

Focus on measurable improvements.
"""

    else:
        return """
TASK TYPE: General

Approach:
1. Understand the problem thoroughly
2. Break down into manageable steps
3. Execute systematically
4. Verify results
5. Explain your reasoning

Be clear and thorough.
"""

# Use context-aware instructions
task = "Debug the authentication error in the login flow"
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=get_instructions_for_task(task)
)
result = agent.run(task)
```

### Composable Instructions

Build instructions from reusable components:

```python
class InstructionBuilder:
    """Build custom instructions from reusable components."""

    @staticmethod
    def domain(name: str) -> str:
        domains = {
            "medical": "DOMAIN: Medical. Cite evidence-based sources. Include disclaimers.",
            "legal": "DOMAIN: Legal. Specify jurisdiction. This is not legal advice.",
            "financial": "DOMAIN: Financial. Discuss risks. This is not financial advice.",
            "technical": "DOMAIN: Technical. Use precise terminology. Provide examples."
        }
        return domains.get(name, "")

    @staticmethod
    def audience(level: str) -> str:
        audiences = {
            "beginner": "AUDIENCE: Beginners. Define all terms. Use simple analogies.",
            "intermediate": "AUDIENCE: Intermediate. Balance depth with clarity.",
            "expert": "AUDIENCE: Experts. Use advanced terminology. Focus on nuances."
        }
        return audiences.get(level, "")

    @staticmethod
    def tone(style: str) -> str:
        tones = {
            "formal": "TONE: Formal, professional, objective.",
            "casual": "TONE: Casual, friendly, conversational.",
            "academic": "TONE: Academic, rigorous, well-cited.",
            "empathetic": "TONE: Empathetic, supportive, patient."
        }
        return tones.get(style, "")

    @staticmethod
    def format(structure: str) -> str:
        formats = {
            "structured": "FORMAT: Use clear headings, sections, and bullet points.",
            "narrative": "FORMAT: Use narrative, storytelling style with flow.",
            "technical": "FORMAT: Use code blocks, tables, and technical diagrams."
        }
        return formats.get(structure, "")

    @classmethod
    def build(cls, domain: str = None, audience: str = None,
              tone: str = None, format: str = None, extra: str = None) -> str:
        """Build instructions from components."""
        parts = []

        if domain:
            parts.append(cls.domain(domain))
        if audience:
            parts.append(cls.audience(audience))
        if tone:
            parts.append(cls.tone(tone))
        if format:
            parts.append(cls.format(format))
        if extra:
            parts.append(extra)

        return "\n\n".join(filter(None, parts))

# Use composable instructions
instructions = InstructionBuilder.build(
    domain="medical",
    audience="intermediate",
    tone="empathetic",
    format="structured",
    extra="Always recommend consulting healthcare professionals."
)

agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions=instructions
)
```

## Best Practices

### 1. Be Specific and Actionable

❌ **Bad**: Vague instructions
```python
custom_instructions = "Be helpful and accurate."
```

✅ **Good**: Specific, actionable guidelines
```python
custom_instructions = """
1. Cite sources for all factual claims
2. Use bullet points for lists of 3+ items
3. Define technical terms on first use
4. Include examples for abstract concepts
"""
```

### 2. Use Structured Formatting

❌ **Bad**: Wall of text
```python
custom_instructions = "You should always cite sources and be accurate and explain things clearly and use examples and be thorough but concise..."
```

✅ **Good**: Numbered or bulleted lists
```python
custom_instructions = """
Guidelines:
1. Cite all sources
2. Provide concrete examples
3. Balance thoroughness with conciseness
4. Define technical terms
"""
```

### 3. Prioritize Key Guidelines

Put the most important instructions first:

```python
custom_instructions = """
CRITICAL:
1. Never share personally identifiable information
2. Always include safety disclaimers for medical content

IMPORTANT:
3. Cite evidence-based sources
4. Acknowledge limitations and uncertainties

PREFERRED:
5. Use clear, accessible language
6. Provide practical examples
"""
```

### 4. Set Clear Boundaries

Explicitly state what NOT to do:

```python
custom_instructions = """
Guidelines:
1. Provide educational information about medications
2. Explain how drugs work in the body
3. Discuss common side effects

PROHIBITED:
- Diagnosing medical conditions
- Recommending specific medications
- Advising on dosages
- Replacing professional medical advice
"""
```

### 5. Keep It Concise

Aim for 5-15 well-crafted guidelines rather than 50 vague ones:

❌ **Bad**: Too many instructions
```python
custom_instructions = """
[100 lines of guidelines]
"""
# LLM may not follow all of them
```

✅ **Good**: Focused, essential guidelines
```python
custom_instructions = """
Top 5 Guidelines:
1. [Most important]
2. [Second most important]
3. [Third most important]
4. [Fourth most important]
5. [Fifth most important]
"""
```

### 6. Test Thoroughly

Always test that instructions have the desired effect:

```python
def test_medical_instructions():
    """Test that medical instructions are followed."""
    medical_instructions = """
    DOMAIN: Medical
    Always recommend consulting healthcare professionals.
    """

    agent = SelfDiscoveryAgent(
        llm_configs=llm_configs,
        custom_instructions=medical_instructions
    )

    result = agent.run("What should I do about my headache?")

    # Verify disclaimer is included
    assert "consult" in result.lower() or "healthcare professional" in result.lower()
    assert "doctor" in result.lower() or "physician" in result.lower()
```

### 7. Version Your Instructions

Track changes to instructions:

```python
# instructions_v1.py
MEDICAL_INSTRUCTIONS_V1 = """
Basic medical guidelines...
"""

# instructions_v2.py
MEDICAL_INSTRUCTIONS_V2 = """
Enhanced medical guidelines with better disclaimers...
"""

# Use versioned instructions
from instructions_v2 import MEDICAL_INSTRUCTIONS_V2

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=MEDICAL_INSTRUCTIONS_V2
)
```

### 8. Document Your Instructions

```python
class DomainInstructions:
    """Centralized repository of domain-specific instructions."""

    MEDICAL = """
    Medical domain instructions for healthcare content.

    Version: 2.1
    Last Updated: 2024-01-15
    Owner: Medical Content Team

    Guidelines:
    1. Prioritize medical accuracy
    2. Include appropriate disclaimers
    3. Use evidence-based sources
    4. Recommend professional consultation
    """

    LEGAL = """
    Legal domain instructions for legal content.

    Version: 1.3
    Last Updated: 2024-01-10
    Owner: Legal Content Team

    Guidelines:
    1. Specify jurisdiction
    2. Include legal disclaimers
    3. Cite laws and regulations
    4. Recommend attorney consultation
    """

# Use documented instructions
agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=DomainInstructions.MEDICAL
)
```

## Combining with Other Customization Methods

Custom instructions work seamlessly with other customization methods:

### With Prompt Overrides

```python
# Custom instructions: Add domain context
medical_instructions = "DOMAIN: Medical. Always cite sources."

# Prompt overrides: Fine-tune specific steps
overrides = {
    "SynthesizeOutput": {
        "system": "Create a well-structured final answer.",
        "user": "Task: {task}\n\nReasoning:\n{reasoning_steps}\n\nFinal answer:"
    }
}

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=medical_instructions,  # Applied to ALL prompts
    prompt_overrides=overrides  # Override specific steps
)
```

### With Custom Prompt Directory

```python
agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_dir="my_custom_prompts",  # Base templates
    custom_instructions=medical_instructions  # Add domain context
)
```

## Common Pitfalls

### 1. Instructions Too Generic

❌ **Bad**:
```python
custom_instructions = "Be helpful and professional."
```

✅ **Good**:
```python
custom_instructions = """
1. Respond within 3 business hours
2. Address customer by name
3. Provide order numbers for reference
4. Escalate to supervisor if unresolved after 2 interactions
"""
```

### 2. Conflicting Instructions

❌ **Bad**: Instructions conflict with pattern design
```python
# ReAct needs to use tools, but instructions say not to
custom_instructions = "Never use external tools or APIs."
```

✅ **Good**: Instructions align with pattern
```python
custom_instructions = "Use tools efficiently. Explain tool choices."
```

### 3. Instructions Lost in Noise

❌ **Bad**: Important instructions buried
```python
custom_instructions = """
[50 lines]
48. Never share API keys  # Critical but buried
[more lines]
"""
```

✅ **Good**: Critical instructions prominent
```python
custom_instructions = """
CRITICAL SECURITY:
1. Never share API keys, passwords, or credentials

Other Guidelines:
2. Use clear language
3. Provide examples
...
"""
```

## Troubleshooting

### Instructions Not Being Followed

**Problem**: Agent ignores custom instructions

**Solutions**:
1. Make instructions more specific and actionable
2. Put most important instructions first
3. Reduce number of instructions (focus on key ones)
4. Test with simpler tasks first
5. Increase LLM capability (e.g., gpt-4 vs gpt-3.5)

### Instructions Conflict with Pattern Behavior

**Problem**: Instructions interfere with pattern's core function

**Solutions**:
1. Understand pattern's design and workflow
2. Align instructions with pattern's approach
3. Use prompt overrides for deeper changes
4. Consider a different pattern

### Too Many Instructions

**Problem**: Agent performs poorly with many instructions

**Solutions**:
1. Prioritize top 5-10 most important guidelines
2. Group related instructions
3. Use tiered importance (Critical, Important, Preferred)
4. Split complex instructions into separate agents

## Next Steps

- Explore [Prompt Overrides](prompt-overrides.md) for finer control
- Learn about [Setting Agent Goals](setting-goals.md)
- Review [Best Practices](best-practices.md) for production usage
- See [Prompt Customization](prompt-customization.md) for overview

## Reference

### Key Takeaways

1. Custom instructions are appended to **all system prompts**
2. They work with **any agent pattern**
3. They're perfect for **domain expertise** and **constraints**
4. They **don't replace** prompts, they **enhance** them
5. Keep them **focused** and **actionable**
6. **Test thoroughly** to ensure desired behavior
7. Can be **generated dynamically** based on context
8. Work **seamlessly** with other customization methods

### Complete Example from Repository

See `/ai/work/claude-code/agent-patterns/examples/custom_instructions_example.py` for:
- Medical domain example
- Legal domain example
- Financial compliance example
- Educational content example
- Cultural sensitivity example
