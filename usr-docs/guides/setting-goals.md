# Setting Agent Goals

Complete guide to configuring agent objectives through task descriptions, custom instructions, and prompt overrides to achieve desired outcomes.

## Overview

Agent goals determine what your agent is trying to achieve and how it approaches tasks. Agent Patterns provides multiple complementary methods for setting and refining agent goals:

1. **Task Descriptions**: Direct, explicit goals via the input
2. **Custom Instructions**: Persistent goals across all tasks
3. **Prompt Overrides**: Fine-tuned goal setting per workflow step
4. **Configuration Parameters**: Pattern-specific goal constraints

## Goal-Setting Methods

### 1. Via Task Description (Primary Method)

The most direct way to set a goal is through the task description passed to `agent.run()`.

#### Explicit Goals

```python
from agent_patterns.patterns import ReActAgent

agent = ReActAgent(llm_configs=llm_configs, tools=tools)

# Explicit, specific goal
result = agent.run("Find the current stock price of AAPL and calculate its P/E ratio")

# Multi-part goal
result = agent.run("""
Goal: Create a comprehensive market analysis report

Requirements:
1. Find current stock prices for AAPL, GOOGL, and MSFT
2. Calculate year-over-year growth for each
3. Compare P/E ratios
4. Provide investment insights
""")
```

#### Goal Clarity Spectrum

```python
# Vague goal (may produce inconsistent results)
agent.run("Tell me about Python")

# Better: More specific
agent.run("Explain Python's main use cases and why it's popular")

# Best: Clear, measurable goal
agent.run("""
Explain Python programming language:
1. Top 3 use cases with examples
2. Key advantages over other languages
3. Major companies using Python
4. Recommended learning resources

Target audience: Beginners with no programming experience
""")
```

#### Success Criteria in Task Description

```python
# Include success criteria
agent.run("""
Task: Research electric vehicle market trends

Success criteria:
- Cover top 5 manufacturers
- Include 2023-2024 sales data
- Identify 3 key trends
- Cite all sources
- Provide executive summary (max 200 words)
""")
```

### 2. Via Custom Instructions (Persistent Goals)

Use custom instructions to set goals that apply to **all** tasks the agent handles.

#### Persistent Quality Goals

```python
from agent_patterns.patterns import ReflectionAgent

quality_goals = """
QUALITY GOALS:
1. ACCURACY: All facts must be verifiable and cited
2. CLARITY: Use simple language (8th grade reading level)
3. COMPLETENESS: Address all aspects of the question
4. CONCISENESS: No unnecessary verbosity
5. EXAMPLES: Include concrete examples for abstract concepts

SUCCESS CRITERIA:
- Every claim has a source
- No jargon without definitions
- Answers the "what", "why", and "how"
"""

agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions=quality_goals
)

# These goals apply to every task
result1 = agent.run("Explain quantum computing")
result2 = agent.run("How do vaccines work?")
# Both will follow the quality goals
```

#### Domain-Specific Goals

```python
# Medical domain goals
medical_goals = """
PRIMARY GOAL: Provide accurate, evidence-based medical information

Sub-goals:
1. Prioritize patient safety in all responses
2. Cite medical literature and guidelines
3. Acknowledge limitations and uncertainties
4. Recommend professional consultation
5. Use patient-friendly language while maintaining accuracy

CONSTRAINTS:
- Never diagnose specific conditions
- Never recommend specific medications or dosages
- Always include medical disclaimers
"""

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=medical_goals
)
```

#### Performance Goals

```python
# Efficiency goals
efficiency_goals = """
PERFORMANCE GOALS:
1. SPEED: Minimize number of reasoning steps
2. COST: Use cheaper models when possible
3. RELIABILITY: Verify information from multiple sources
4. DETERMINISM: Produce consistent results for same inputs

OPTIMIZATION PRIORITIES:
- Accuracy > Speed > Cost
- Fail gracefully with clear error messages
- Cache repeated computations when possible
"""

agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    custom_instructions=efficiency_goals,
    max_iterations=3  # Enforces speed goal
)
```

### 3. Via Prompt Overrides (Step-Specific Goals)

Use prompt overrides to set different goals for different workflow steps.

#### Goal-Oriented Overrides

```python
from agent_patterns.patterns import SelfDiscoveryAgent

# Different goals for different steps
goal_overrides = {
    "DiscoverModules": {
        "system": """Your goal: Select reasoning modules that maximize solution quality.

Prioritize modules that:
1. Are proven effective for this problem type
2. Provide complementary perspectives
3. Lead to verifiable conclusions""",
        "user": "Task: {task}\n\nModules:\n{modules}\n\nSelect the {max_modules} best modules:"
    },
    "ExecuteStep": {
        "system": """Your goal: Execute this reasoning step thoroughly and accurately.

Sub-goals:
1. Show your work step-by-step
2. Verify intermediate results
3. Note any assumptions
4. Identify potential errors""",
        "user": "Step: {step_description}\n\nExecute with full reasoning:"
    },
    "SynthesizeOutput": {
        "system": """Your goal: Create a clear, actionable final answer.

Success criteria:
1. Directly answers the original question
2. Is well-structured and easy to follow
3. Highlights key insights
4. Acknowledges any limitations""",
        "user": "Task: {task}\n\nReasoning:\n{reasoning_steps}\n\nSynthesize final answer:"
    }
}

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    prompt_overrides=goal_overrides
)
```

#### Outcome-Focused Overrides

```python
# Focus on specific outcome
outcome_overrides = {
    "Generate": {
        "system": """Your goal: Produce actionable recommendations.

Every response must include:
1. Specific actions to take
2. Expected outcomes
3. Potential risks
4. Success metrics

Not theoretical - practical and implementable.""",
        "user": "Situation: {task}\n\nProvide actionable recommendations:"
    }
}

agent = ReflectionAgent(
    llm_configs=llm_configs,
    prompt_overrides=outcome_overrides
)
```

### 4. Via Configuration Parameters

Use pattern-specific parameters to constrain goals.

```python
from agent_patterns.patterns import ReActAgent, ReflectionAgent, SelfDiscoveryAgent

# Limit iterations = goal to be efficient
react_agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    max_iterations=3  # Goal: Solve in max 3 steps
)

# Multiple reflection cycles = goal for high quality
reflection_agent = ReflectionAgent(
    llm_configs=llm_configs,
    max_reflection_cycles=3  # Goal: Refine up to 3 times
)

# Module selection = goal focus
discovery_agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    max_selected_modules=2,  # Goal: Use focused approach
    reasoning_modules=domain_specific_modules  # Goal: Use domain expertise
)
```

## Goal Types and Examples

### Informational Goals

Goals focused on gathering and presenting information.

```python
# Research goal
agent.run("""
Research goal: Create comprehensive overview of renewable energy

Information requirements:
- Solar, wind, hydro, geothermal technologies
- Current adoption rates globally
- Cost trends over past decade
- Future projections to 2030
- Environmental impact comparison

Format: Executive summary + detailed sections
""")

# Comparison goal
agent.run("""
Compare electric vehicles vs gasoline vehicles across:
1. Total cost of ownership (5 years)
2. Environmental impact
3. Convenience and infrastructure
4. Performance metrics

Goal: Help consumers make informed decisions
""")
```

### Analytical Goals

Goals focused on analysis and insights.

```python
# Root cause analysis goal
agent.run("""
Analyze declining user engagement:

Data provided:
- Daily active users down 25% in Q3
- Session duration decreased from 12min to 8min
- Feature adoption rates unchanged

Goal: Identify top 3 root causes with evidence
""")

# Trend analysis goal
agent.run("""
Analyze cryptocurrency market trends:

Goal: Identify and explain 3 major trends in 2023-2024
- Use quantitative data where possible
- Explain causal factors
- Project implications for 2025
""")
```

### Creative Goals

Goals focused on generation and ideation.

```python
# Content creation goal
agent.run("""
Create a technical blog post about microservices:

Goals:
- Explain benefits and challenges
- Include code examples
- Target audience: intermediate developers
- Length: 1500-2000 words
- Engaging and practical, not theoretical
""")

# Design goal
agent.run("""
Design a loyalty program for coffee shop:

Goals:
- Increase customer retention by 30%
- Appeal to students and professionals
- Low operational overhead
- Mobile-first experience
- Unique/differentiated from competitors

Deliverables:
- Program structure
- Reward tiers
- Implementation plan
""")
```

### Decision Support Goals

Goals focused on recommendations and choices.

```python
# Recommendation goal
agent.run("""
Recommend database technology for new project:

Context:
- E-commerce platform
- 100K+ products
- 10M+ users expected
- Complex search requirements
- Need for scalability

Goal: Recommend top 3 options with:
- Pros/cons for our use case
- Estimated costs
- Implementation complexity
- Risk assessment
""")

# Evaluation goal
agent.run("""
Evaluate A/B test results:

Test: New checkout flow vs current
- Variant A: 5.2% conversion (current)
- Variant B: 5.7% conversion (new)
- 10,000 users per variant
- 2 week test period

Goals:
1. Determine statistical significance
2. Recommend whether to ship
3. Identify next tests to run
""")
```

### Problem-Solving Goals

Goals focused on finding solutions.

```python
# Debugging goal
agent.run("""
Debug authentication failure:

Symptoms:
- Users can't login via OAuth
- Password login works fine
- Started after deployment yesterday
- Affects ~30% of OAuth users

Goal:
1. Identify root cause
2. Provide fix
3. Suggest prevention measures
""")

# Optimization goal
agent.run("""
Optimize database query performance:

Current: Query takes 5.2 seconds
Target: Under 500ms
Query: Complex join across 4 tables with aggregation

Goals:
1. Analyze query execution plan
2. Identify bottlenecks
3. Propose optimizations (indexes, query rewrite, etc.)
4. Estimate expected improvement
""")
```

## Combining Goal-Setting Methods

The real power comes from combining multiple methods:

### Example 1: Research Agent

```python
from agent_patterns.patterns import STORMAgent

# 1. Persistent research goals via custom instructions
research_goals = """
RESEARCH QUALITY GOALS:
1. Multiple perspectives: Seek diverse viewpoints
2. Source credibility: Prioritize authoritative sources
3. Recency: Prefer recent information (last 2 years)
4. Objectivity: Present balanced analysis
5. Depth: Go beyond surface-level information

CITATION REQUIREMENTS:
- Cite all factual claims
- Note publication date
- Assess source credibility
"""

# 2. Step-specific goals via overrides
research_overrides = {
    "GenerateQuestions": {
        "system": "Goal: Generate questions that uncover multiple perspectives and deep insights.",
        "user": "Topic: {topic}\n\nGenerate research questions:"
    }
}

# 3. Create agent
agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_function},
    custom_instructions=research_goals,
    prompt_overrides=research_overrides
)

# 4. Specific task goal
result = agent.run("""
Research topic: Impact of AI on employment

Specific goals:
- Historical perspective (past impacts of automation)
- Current trends and data
- Future projections from credible sources
- Both optimistic and pessimistic viewpoints
- Policy implications

Deliverable: 3000-word balanced analysis
""")
```

### Example 2: Customer Service Agent

```python
from agent_patterns.patterns import ReActAgent

# 1. Service quality goals
service_goals = """
CUSTOMER SERVICE GOALS:
1. RESOLUTION: Solve customer issues completely
2. EFFICIENCY: Minimize resolution time
3. SATISFACTION: Ensure positive experience
4. ACCURACY: Provide correct information
5. EMPATHY: Show understanding and care

SERVICE STANDARDS:
- First response within 1 minute
- Full resolution within 24 hours
- Customer satisfaction score > 4.5/5
- No escalations unless absolutely necessary
"""

# 2. Interaction style override
service_overrides = {
    "ThoughtStep": {
        "system": """Goal: Provide excellent customer service.

For each interaction:
1. Acknowledge the customer's issue
2. Gather necessary information
3. Provide clear solution
4. Confirm customer satisfaction

Be empathetic, clear, and efficient.""",
        "user": "Customer: {input}\n\nHistory: {history}\n\nHow to help:"
    }
}

# 3. Create agent
agent = ReActAgent(
    llm_configs=llm_configs,
    tools=customer_service_tools,
    custom_instructions=service_goals,
    prompt_overrides=service_overrides,
    max_iterations=5  # Efficiency goal
)

# 4. Handle customer issue
result = agent.run("""
Customer Issue: Order #12345 hasn't arrived, tracking shows delivered but customer didn't receive it

Customer info: Premium member, first issue ever
Goal: Resolve immediately and maintain satisfaction
""")
```

### Example 3: Code Review Agent

```python
from agent_patterns.patterns import ReflectionAgent

# 1. Code quality goals
quality_goals = """
CODE REVIEW GOALS:
1. CORRECTNESS: Code works as intended
2. SECURITY: No vulnerabilities
3. PERFORMANCE: No obvious inefficiencies
4. MAINTAINABILITY: Clean, well-documented
5. BEST PRACTICES: Follows language idioms

REVIEW STANDARDS:
- Every finding must include specific line reference
- Provide code examples for suggested improvements
- Categorize issues: Critical, Important, Minor, Nitpick
- Acknowledge good practices
"""

# 2. Review process overrides
review_overrides = {
    "Reflect": {
        "system": """Goal: Provide thorough, constructive code review.

Review checklist:
1. Functionality: Does it work correctly?
2. Security: Any vulnerabilities?
3. Performance: Any bottlenecks?
4. Readability: Is it clear?
5. Tests: Adequate coverage?

Be specific, constructive, and educational.""",
        "user": "Code to review:\n{output}\n\nProvide detailed code review:"
    }
}

# 3. Create agent
agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions=quality_goals,
    prompt_overrides=review_overrides,
    max_reflection_cycles=2  # Thorough review
)

# 4. Review code
result = agent.run("""
Review this authentication function:

def authenticate(username, password):
    user = db.query(f"SELECT * FROM users WHERE username='{username}'")
    if user and user.password == password:
        return create_session(user)
    return None

Goals:
- Identify security issues
- Suggest improvements
- Provide corrected version
""")
```

## Goal Measurement and Validation

### Defining Measurable Goals

```python
# Measurable goals in task description
agent.run("""
Task: Optimize checkout flow

Measurable goals:
- Reduce steps from 5 to 3
- Decrease avg time from 2min to 1min
- Increase conversion rate by 15%
- Maintain form completion accuracy > 95%

Success criteria:
- All goals met in A/B test
- No increase in support tickets
- Positive user feedback (NPS > 70)
""")
```

### Validating Goal Achievement

```python
def validate_agent_goals(agent, task, expected_criteria):
    """Validate that agent output meets specified goals."""
    result = agent.run(task)

    validation_results = {}

    # Check for required elements
    if "citations" in expected_criteria:
        has_citations = bool(re.findall(r'\[\d+\]|\[.*?\]', result))
        validation_results["has_citations"] = has_citations

    # Check length goals
    if "max_words" in expected_criteria:
        word_count = len(result.split())
        validation_results["within_length"] = word_count <= expected_criteria["max_words"]

    # Check for required sections
    if "required_sections" in expected_criteria:
        validation_results["has_sections"] = all(
            section.lower() in result.lower()
            for section in expected_criteria["required_sections"]
        )

    # Check for prohibited content
    if "prohibited_terms" in expected_criteria:
        has_prohibited = any(
            term.lower() in result.lower()
            for term in expected_criteria["prohibited_terms"]
        )
        validation_results["no_prohibited_content"] = not has_prohibited

    return validation_results

# Example usage
criteria = {
    "max_words": 500,
    "required_sections": ["Summary", "Details", "Recommendations"],
    "prohibited_terms": ["I think", "maybe", "probably"]
}

validation = validate_agent_goals(agent, task, criteria)
print(f"Goal achievement: {validation}")
```

### Iterative Goal Refinement

```python
def refine_goals_based_on_results(initial_task, initial_result, feedback):
    """Refine goals based on previous attempt."""

    refined_task = f"""
Previous attempt: {initial_task}

Previous result issues:
{feedback}

Refined goals:
{initial_task}

Additional requirements based on feedback:
- Address the issues noted above
- Maintain quality in other areas
"""
    return refined_task

# Example usage
task_v1 = "Explain machine learning"
result_v1 = agent.run(task_v1)

feedback = """
Issues:
- Too technical for beginners
- Lacks concrete examples
- No practical applications mentioned
"""

task_v2 = refine_goals_based_on_results(task_v1, result_v1, feedback)
result_v2 = agent.run(task_v2)
```

## Advanced Goal Patterns

### Hierarchical Goals

```python
hierarchical_goals = """
PRIMARY GOAL: Create actionable business recommendations

SECONDARY GOALS:
1. Data-driven: Base recommendations on quantitative analysis
2. Risk-aware: Identify and quantify risks
3. Practical: Focus on implementable solutions
4. Prioritized: Rank by impact and feasibility

TERTIARY GOALS:
1. Clear communication: Executive summary + details
2. Comprehensive: Cover all major aspects
3. Time-bound: Include implementation timeline
"""

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=hierarchical_goals
)
```

### Conditional Goals

```python
def get_goals_for_user_type(user_type, task_urgency):
    """Generate goals based on context."""

    if user_type == "executive":
        base_goal = "Provide strategic, high-level insights"
        detail_level = "Executive summary with key takeaways"
    elif user_type == "analyst":
        base_goal = "Provide detailed analysis with data"
        detail_level = "Comprehensive with methodology"
    else:
        base_goal = "Provide balanced overview"
        detail_level = "Moderate detail with examples"

    if task_urgency == "high":
        speed_goal = "Prioritize speed: Quick, actionable answer"
    else:
        speed_goal = "Prioritize thoroughness: Comprehensive analysis"

    return f"""
{base_goal}
Detail level: {detail_level}
Approach: {speed_goal}
"""

# Use conditional goals
goals = get_goals_for_user_type(user_type="executive", task_urgency="high")
agent = ReflectionAgent(
    llm_configs=llm_configs,
    custom_instructions=goals
)
```

### Competing Goals and Trade-offs

```python
tradeoff_goals = """
PRIMARY GOALS (in priority order):
1. ACCURACY: Correct information (non-negotiable)
2. SPEED: Fast response (target < 30 seconds)
3. DETAIL: Comprehensive coverage (target 500+ words)
4. SIMPLICITY: Easy to understand (8th grade level)

TRADE-OFF GUIDANCE:
- Never sacrifice accuracy for speed
- If speed conflicts with detail, prefer speed with option to elaborate
- If detail conflicts with simplicity, provide layered information (simple summary + detailed sections)

When goals conflict, explicitly state the trade-off made and why.
"""

agent = SelfDiscoveryAgent(
    llm_configs=llm_configs,
    custom_instructions=tradeoff_goals
)
```

## Common Pitfalls

### 1. Vague Goals

❌ **Bad**: Unclear objectives
```python
agent.run("Tell me about climate change")
```

✅ **Good**: Specific, measurable goals
```python
agent.run("""
Explain climate change for high school students:
- What it is and what causes it (2-3 paragraphs)
- 3 major impacts with examples
- 3 actions individuals can take
- Use simple analogies for complex concepts
- Include credible sources
""")
```

### 2. Conflicting Goals

❌ **Bad**: Goals that contradict each other
```python
custom_instructions = """
- Be extremely brief (max 50 words)
- Provide comprehensive, detailed analysis
- Include multiple examples
"""
```

✅ **Good**: Aligned, prioritized goals
```python
custom_instructions = """
- Provide comprehensive analysis
- Use layered approach: brief summary (50 words) + detailed sections
- Include 2-3 examples per major point
"""
```

### 3. Unmeasurable Goals

❌ **Bad**: Can't verify achievement
```python
agent.run("Make the answer good")
```

✅ **Good**: Measurable criteria
```python
agent.run("""
Goals (measurable):
- Include exactly 3 main points
- Each point supported by data/example
- Total length: 300-500 words
- Reading level: 10th grade
- At least 2 credible sources cited
""")
```

### 4. Too Many Goals

❌ **Bad**: Overwhelming number of objectives
```python
custom_instructions = """
[30 different goals listed]
"""
```

✅ **Good**: Focused, prioritized goals
```python
custom_instructions = """
TOP 5 GOALS (in priority order):
1. Accuracy: All facts verified
2. Clarity: 8th grade reading level
3. Completeness: Address all aspects
4. Conciseness: No unnecessary verbosity
5. Citations: Cite all sources
"""
```

## Best Practices

### 1. Start with Clear Task Goals

Every task should have explicit goals:

```python
template = """
Task: {task_description}

Goals:
1. {primary_goal}
2. {secondary_goal}
3. {tertiary_goal}

Success criteria:
- {criterion_1}
- {criterion_2}
- {criterion_3}

Target audience: {audience}
Format: {format_preference}
"""
```

### 2. Use Hierarchical Goal Structure

```python
goals = """
PRIMARY: {most_important}
SECONDARY: {important}
TERTIARY: {nice_to_have}

If goals conflict, prioritize in this order.
"""
```

### 3. Make Goals Measurable

```python
measurable_goals = """
Goals:
1. Response length: 500-750 words
2. Reading level: 8th grade (Flesch-Kincaid score 8-10)
3. Citations: Minimum 3 credible sources
4. Examples: 2-3 concrete examples
5. Structure: Intro + 3 sections + conclusion
"""
```

### 4. Provide Context

```python
contextual_goals = """
Goal: Explain blockchain technology

Context:
- Audience: Business executives (non-technical)
- Purpose: Evaluate if blockchain fits our use case
- Current knowledge: Familiar with databases, basic web tech
- Time constraint: 10-minute read

Output goals:
- No technical jargon without explanation
- Focus on business value and trade-offs
- Include real-world examples from Fortune 500
- Clear recommendation on applicability
"""
```

### 5. Test Goal Achievement

```python
def test_goal_achievement():
    """Test that agent achieves specified goals."""
    task = """
    Explain photosynthesis.

    Goals:
    - Target: 10th grade students
    - Length: 200-300 words
    - Include: Process diagram description
    - Cite: At least one educational source
    """

    result = agent.run(task)

    # Validate
    word_count = len(result.split())
    assert 200 <= word_count <= 300, f"Length goal not met: {word_count} words"
    assert "source:" in result.lower() or "reference:" in result.lower(), "Citation goal not met"
    # More validations...
```

## Next Steps

- Learn about [Prompt Customization](prompt-customization.md) methods
- Review [Configuration Guide](configuration.md) for parameter tuning
- See [Best Practices](best-practices.md) for production usage
- Explore individual pattern docs for pattern-specific goals

## Reference

### Goal-Setting Method Comparison

| Method | Scope | Priority | Best For |
|--------|-------|----------|----------|
| **Task Description** | Single task | Highest | Specific, one-off goals |
| **Custom Instructions** | All tasks | Medium | Persistent quality standards |
| **Prompt Overrides** | Workflow steps | Highest | Fine-grained control |
| **Config Parameters** | Pattern behavior | System | Constraints and limits |

### Example Goal Templates

See `/ai/work/claude-code/agent-patterns/examples/` for:
- Research goals (STORM pattern)
- Quality goals (Reflection pattern)
- Efficiency goals (ReAct pattern)
- Multi-objective goals (Self-Discovery pattern)
