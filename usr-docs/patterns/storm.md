# STORM Agent Pattern

The **STORM** (Synthesis of Topic Outlines through Retrieval and Multi-perspective question asking) pattern creates comprehensive, well-researched reports by exploring topics from multiple perspectives, retrieving information systematically, and synthesizing it into structured documents.

## Overview

**Best For**: Creating comprehensive multi-perspective research reports and articles

**Complexity**: ⭐⭐⭐ Advanced (Multi-stage research workflow)

**Cost**: $$$$ Very High (Many LLM calls + retrieval operations)

## When to Use STORM

### Ideal Use Cases

✅ **Research report generation**
- Generates structured outlines
- Explores multiple viewpoints
- Retrieves comprehensive information
- Synthesizes into coherent reports

✅ **Wikipedia-style articles**
- Systematic topic coverage
- Multiple expert perspectives
- Well-cited, comprehensive content
- Structured sections and subsections

✅ **Technical documentation**
- Multi-perspective analysis (architect, developer, operator)
- Comprehensive topic coverage
- Research-backed content
- Organized presentation

✅ **Market research reports**
- Analyst, customer, competitor perspectives
- Data-driven insights
- Structured findings
- Synthesized recommendations

### When NOT to Use STORM

❌ **Simple queries** → Use direct LLM or ReAct
❌ **No retrieval needed** → Use Reflection or Plan & Solve
❌ **Single perspective sufficient** → Use simpler patterns
❌ **Time-sensitive tasks** → Too many stages and calls

## How STORM Works

### The Multi-Stage Research Workflow

```
┌─────────────────────────────────────────┐
│                                         │
│  1. GENERATE OUTLINE                    │
│     Topic: "Quantum Computing"          │
│     Sections: Introduction, History,    │
│               Applications, Challenges   │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  2. GENERATE PERSPECTIVES               │
│     - Researcher perspective            │
│     - Practitioner perspective          │
│     - Industry expert perspective       │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  3. GENERATE QUESTIONS                  │
│     For each section × each perspective │
│     Researcher + Introduction:          │
│       "What are the theoretical         │
│        foundations?"                    │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  4. EXECUTE SEARCHES                    │
│     Run retrieval for all questions     │
│     Gather information from sources     │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  5. SYNTHESIZE SECTIONS                 │
│     Combine multi-perspective info      │
│     into each section                   │
│                                         │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│                                         │
│  6. COMPILE REPORT                      │
│     Assemble all sections into          │
│     final coherent document             │
│                                         │
└─────────────────────────────────────────┘
```

### Theoretical Foundation

Based on the paper ["Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models"](https://arxiv.org/abs/2402.14207). Key principles:

1. **Multi-perspective inquiry**: Different viewpoints reveal different insights
2. **Systematic coverage**: Structured outline ensures completeness
3. **Research-backed**: Retrieval grounds content in actual information
4. **Hierarchical synthesis**: Build from questions → sections → final report

### Algorithm

```python
def storm_workflow(topic, perspectives, retrieval_tool):
    """Simplified STORM algorithm"""

    # Stage 1: Plan structure
    outline = llm_generate_outline(topic)

    # Stage 2: Identify perspectives
    active_perspectives = select_perspectives(topic, perspectives)

    # Stage 3: Generate questions
    questions = {}
    for section in outline:
        for perspective in active_perspectives:
            qs = llm_generate_questions(topic, section, perspective)
            questions[section][perspective] = qs

    # Stage 4: Retrieve information
    search_results = {}
    for section, persp_qs in questions.items():
        for perspective, qs in persp_qs.items():
            for q in qs:
                info = retrieval_tool(q)
                search_results[section][perspective].append(info)

    # Stage 5: Synthesize sections
    synthesized_sections = {}
    for section, persp_results in search_results.items():
        section_content = llm_synthesize_section(
            topic, section, persp_results
        )
        synthesized_sections[section] = section_content

    # Stage 6: Compile final report
    final_report = llm_compile_report(topic, synthesized_sections)

    return final_report
```

## API Reference

### Class: `STORMAgent`

```python
from agent_patterns.patterns import STORMAgent

agent = STORMAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    retrieval_tools: Optional[Dict[str, Callable]] = None,
    perspectives: Optional[List[Dict[str, str]]] = None,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configs for "thinking" and "documentation" roles |
| `retrieval_tools` | `Dict[str, Callable]` | No | Dictionary mapping tool names to retrieval functions |
| `perspectives` | `List[Dict]` | No | Custom perspective definitions (uses defaults if None) |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict` | No | Override specific prompts programmatically |

#### Default Perspectives

The agent includes 4 default perspectives:

1. **expert**: Technical expert with deep domain knowledge
2. **practitioner**: Professional practitioner applying concepts
3. **researcher**: Academic researcher studying the topic
4. **critic**: Critical analyst examining limitations and challenges

#### LLM Roles

- **thinking**: Used for outline, perspectives, questions, and planning
- **documentation**: Used for section synthesis and report compilation

#### Methods

**`run(input_data: str) -> str`**

Executes the STORM pattern on the given topic.

- **Parameters**:
  - `input_data` (str): The topic for the research report
- **Returns**: str - The final compiled report
- **Raises**: ValueError if graph not built

**`build_graph() -> None`**

Builds the LangGraph state graph. Called automatically during initialization.

## Complete Examples

### Basic Usage

```python
from agent_patterns.patterns import STORMAgent

# Define retrieval tool
def search_web(query: str) -> str:
    """Search the web and return relevant information"""
    # Use actual search API in production
    import requests
    response = requests.get(f"https://api.search.com/search?q={query}")
    return response.json()["snippet"]

# Configure LLMs
llm_configs = {
    "thinking": {
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
agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_web}
)

# Generate comprehensive report
report = agent.run("Artificial Intelligence in Healthcare")

print(report)
# Output: Multi-section report with:
# - Introduction from multiple perspectives
# - Applications (expert, practitioner views)
# - Challenges and limitations (critic view)
# - Research directions (researcher view)
# - Conclusion synthesizing all perspectives
```

### With Custom Perspectives

```python
# Define domain-specific perspectives
healthcare_perspectives = [
    {
        "name": "physician",
        "description": "Medical doctor focused on clinical applications"
    },
    {
        "name": "patient_advocate",
        "description": "Patient representative concerned with access and safety"
    },
    {
        "name": "health_economist",
        "description": "Economist analyzing cost-effectiveness and policy"
    },
    {
        "name": "medical_researcher",
        "description": "Clinical researcher studying evidence and outcomes"
    },
    {
        "name": "tech_implementer",
        "description": "IT professional implementing health technology"
    }
]

agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_web},
    perspectives=healthcare_perspectives
)

report = agent.run("Telemedicine Adoption Post-Pandemic")
```

### With Multiple Retrieval Tools

```python
def search_academic(query: str) -> str:
    """Search academic databases"""
    # Integration with PubMed, arxiv, etc.
    return f"Academic research about: {query}"

def search_news(query: str) -> str:
    """Search news articles"""
    # Integration with news APIs
    return f"Recent news about: {query}"

def search_patents(query: str) -> str:
    """Search patent databases"""
    # Integration with patent databases
    return f"Patents related to: {query}"

# Agent will use 'search' tool by default, but you can customize
retrieval_tools = {
    "search": search_academic,
    "news_search": search_news,
    "patent_search": search_patents
}

agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools=retrieval_tools
)

# Modify agent to use different tools for different sections
# (requires custom prompt overrides or subclassing)
```

### With Custom Instructions

```python
research_guidelines = """
You are generating high-quality research reports. Follow these guidelines:

OUTLINE GENERATION:
- Create 5-7 main sections
- Each section should have 2-4 subsections
- Structure should tell a complete story

QUESTION GENERATION:
- Ask specific, answerable questions
- Focus on factual information
- Avoid yes/no questions
- Target 3-5 questions per section/perspective

SECTION SYNTHESIS:
- Integrate perspectives smoothly
- Cite different viewpoints explicitly
- Resolve contradictions when possible
- Maintain objectivity

REPORT COMPILATION:
- Ensure smooth transitions between sections
- Create compelling introduction and conclusion
- Maintain consistent tone throughout
- Format with clear headings and structure
"""

agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_web},
    custom_instructions=research_guidelines
)

report = agent.run("Blockchain Technology in Supply Chain Management")
```

## Retrieval Tool Guidelines

### Tool Function Signature

```python
def retrieval_tool(query: str) -> str:
    """
    Retrieve information for a query.

    Args:
        query: The search query or question

    Returns:
        Retrieved information as a string
    """
    # Retrieval implementation
    return result_string
```

### Tool Best Practices

1. **Return comprehensive info**: Include enough context for synthesis
2. **Handle errors gracefully**: Return informative error messages
3. **Be consistent**: Always return strings
4. **Add source attribution**: Include sources in retrieved content when possible

### Example Retrieval Tools

```python
def wiki_search(query: str) -> str:
    """Search Wikipedia for information"""
    try:
        import wikipedia
        results = wikipedia.summary(query, sentences=5)
        return results
    except Exception as e:
        return f"Wikipedia search error: {str(e)}"

def arxiv_search(query: str) -> str:
    """Search arXiv for academic papers"""
    try:
        import arxiv
        search = arxiv.Search(query=query, max_results=3)
        summaries = []
        for result in search.results():
            summaries.append(f"{result.title}: {result.summary[:200]}")
        return "\n\n".join(summaries)
    except Exception as e:
        return f"arXiv search error: {str(e)}"

def google_search(query: str) -> str:
    """Search Google and return snippets"""
    try:
        from googlesearch import search
        results = []
        for url in search(query, num_results=5):
            # Fetch and extract snippet
            results.append(f"Source: {url}")
        return "\n".join(results)
    except Exception as e:
        return f"Search error: {str(e)}"
```

## Customizing Prompts

### Understanding the System Prompt Structure

Version 0.2.0 introduces **enterprise-grade prompts** with a comprehensive 9-section structure. Each system prompt is now 150-300+ lines (compared to ~32 lines previously), providing significantly better guidance to the LLM.

**The 9-Section Comprehensive Structure**: All STORM system prompts now include Role and Identity, Core Capabilities (CAN/CANNOT boundaries), Process, Output Format, Decision-Making Guidelines, Quality Standards, Edge Cases, Examples, and Critical Reminders.

**Benefits**: Increased reliability, better transparency, improved robustness, and backward compatibility.

### Understanding STORM Prompts

STORM uses six prompt templates for different stages (all now with comprehensive 9-section structure):

1. **GenerateOutline**: Creates hierarchical document structure with detailed quality standards
2. **GeneratePerspectives**: Selects relevant viewpoints using systematic process guidance
3. **GenerateQuestions**: Creates questions from each perspective with examples
4. **SynthesizeSection**: Combines multi-perspective info with edge case handling
5. **CompileReport**: Assembles final document with quality criteria

### Method 1: Custom Instructions

```python
agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_web},
    custom_instructions="""
    Target audience: Business executives and decision-makers
    Tone: Professional, authoritative, accessible
    Format: Executive summary + detailed sections + recommendations
    Citation style: Inline references to perspectives
    """
)
```

### Method 2: Prompt Overrides

```python
overrides = {
    "GenerateOutline": {
        "system": "You create well-structured research outlines for business reports.",
        "user": """Topic: {topic}

Create a comprehensive outline with:
1. Executive Summary
2. Background and Context
3. Current State Analysis
4. Key Challenges
5. Opportunities
6. Recommendations
7. Conclusion

For sections 2-6, include 3-4 subsections.

Your outline:"""
    },
    "GenerateQuestions": {
        "system": "You generate insightful research questions.",
        "user": """Topic: {topic}
Section: {section}
Subsections: {subsections}

Perspective: {perspective_name} - {perspective_description}

Generate 4-5 specific research questions from this perspective that will help
create comprehensive content for this section. Make questions actionable and
focused on gathering concrete information.

Your questions (one per line, numbered):"""
    }
}

agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_web},
    prompt_overrides=overrides
)
```

### Method 3: Custom Prompt Directory

```bash
my_prompts/
└── STORMAgent/
    ├── GenerateOutline/
    │   ├── system.md
    │   └── user.md
    ├── GeneratePerspectives/
    │   ├── system.md
    │   └── user.md
    ├── GenerateQuestions/
    │   ├── system.md
    │   └── user.md
    ├── SynthesizeSection/
    │   ├── system.md
    │   └── user.md
    └── CompileReport/
        ├── system.md
        └── user.md
```

## Setting Agent Goals

### Via Topic Description

Provide detailed topic with requirements:

```python
agent.run("""
Topic: Remote Work Technology Trends 2024-2025

Scope:
- Focus on collaboration tools
- Include security considerations
- Cover hybrid work models
- Address productivity metrics

Audience: IT decision-makers and HR leaders

Desired length: Comprehensive (8-10 sections)
""")
```

### Via Custom Instructions

```python
agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_web},
    custom_instructions="""
    GOAL: Create authoritative, well-researched industry reports

    PERSPECTIVE SELECTION:
    - Always include industry expert and practitioner
    - Add researcher for academic topics
    - Add critic for balanced analysis

    QUESTION QUALITY:
    - Target specific, verifiable facts
    - Include "how" and "why" questions
    - Avoid vague or open-ended questions

    SYNTHESIS QUALITY:
    - Integrate all perspectives smoothly
    - Highlight areas of agreement and disagreement
    - Support claims with retrieved information
    - Maintain objectivity

    OUTPUT FORMAT:
    - Clear section headings
    - Smooth paragraph flow
    - Professional tone
    - Logical progression of ideas
    """
)
```

## Advanced Usage

### Custom Perspective Selection

```python
# Industry-specific perspectives
fintech_perspectives = [
    {"name": "regulator", "description": "Financial regulatory expert"},
    {"name": "security_expert", "description": "Cybersecurity specialist"},
    {"name": "customer", "description": "End-user perspective"},
    {"name": "developer", "description": "Platform developer"}
]

agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_web},
    perspectives=fintech_perspectives
)
```

### Caching Retrieval Results

```python
class CachedSTORMAgent(STORMAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retrieval_cache = {}

    def _retrieve_information(self, query: str) -> str:
        """Override to add caching"""
        if query in self.retrieval_cache:
            return self.retrieval_cache[query]

        result = super()._retrieve_information(query)
        self.retrieval_cache[query] = result
        return result

agent = CachedSTORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_web}
)
```

## Performance Considerations

### Cost Analysis

STORM is expensive due to many stages:

**Per report cost**:
- Generate outline: 1 LLM call
- Generate perspectives: 1 LLM call
- Generate questions: S × P calls (S=sections, P=perspectives)
- Synthesize sections: S calls
- Compile report: 1 call
- **Total LLM calls**: ~15-30 for typical report
- **Retrieval calls**: Q × S × P (Q=questions per section/perspective)
  - Example: 4 questions × 6 sections × 3 perspectives = 72 retrievals

**Optimization strategies**:

```python
# 1. Limit perspectives
focused_perspectives = [
    {"name": "expert", "description": "Domain expert"},
    {"name": "practitioner", "description": "Hands-on practitioner"}
]  # Just 2 instead of 4

# 2. Use cheaper model for synthesis
llm_configs = {
    "thinking": {"provider": "openai", "model": "gpt-4"},
    "documentation": {"provider": "openai", "model": "gpt-3.5-turbo"}
}

# 3. Reduce questions per section
# Override GenerateQuestions to request 2-3 questions instead of 4-5

# 4. Cache retrieval results (see Advanced Usage)
```

### When to Use STORM

| Use Case | STORM? | Alternative |
|----------|--------|-------------|
| Wikipedia-style article | ✅ Yes | - |
| Comprehensive research report | ✅ Yes | - |
| Quick summary | ❌ No | Direct LLM |
| No retrieval needed | ❌ No | Reflection, Plan & Solve |
| Single perspective sufficient | ❌ No | ReAct with tools |
| Cost-sensitive | ❌ No | Simpler patterns |

## Comparison with Other Patterns

| Aspect | STORM | ReAct | Self-Discovery |
|--------|-------|-------|----------------|
| **Purpose** | Comprehensive reports | Dynamic tool use | Complex reasoning |
| **Retrieval** | Core feature | Via tools | Not supported |
| **Perspectives** | Multi-viewpoint | Single agent | Module-based |
| **Structure** | Hierarchical outline | Adaptive | Reasoning plan |
| **Cost** | Very High | Medium | High |
| **Best For** | Research reports | Interactive tasks | Novel problems |

## Common Pitfalls

### 1. Insufficient Retrieval

❌ **Bad**: No retrieval tools configured
```python
agent = STORMAgent(llm_configs=llm_configs)  # No tools!
```

✅ **Good**: Provide effective retrieval
```python
agent = STORMAgent(
    llm_configs=llm_configs,
    retrieval_tools={"search": search_web}
)
```

### 2. Too Many Perspectives

❌ **Bad**: Overwhelming number of viewpoints
```python
perspectives = [/* 8+ perspectives */]  # Too many!
```

✅ **Good**: 2-4 complementary perspectives
```python
perspectives = [
    {"name": "expert", "description": "..."},
    {"name": "practitioner", "description": "..."},
    {"name": "critic", "description": "..."}
]
```

### 3. Vague Topics

❌ **Bad**: Overly broad or vague
```python
agent.run("Technology")  # Way too broad
```

✅ **Good**: Specific, scoped topics
```python
agent.run("""
Cloud-Native Application Development:
Focus on containerization, microservices, and DevOps practices
""")
```

### 4. Poor Question Generation

❌ **Bad**: Allowing yes/no or vague questions

✅ **Good**: Override to ensure quality questions
```python
overrides = {
    "GenerateQuestions": {
        "user": """...
Generate 3-4 specific questions that:
- Start with "What", "How", or "Why"
- Target factual, verifiable information
- Are specific to this section and perspective

Your questions:"""
    }
}
```

## Troubleshooting

### Shallow or Generic Content

**Symptom**: Report lacks depth despite retrieval

**Solutions**:
```python
# 1. Improve question quality via prompts
# 2. Use better retrieval tools
# 3. Add more specific perspectives
# 4. Override synthesis to emphasize depth

custom_instructions = """
SYNTHESIS REQUIREMENTS:
- Include specific examples and data
- Cite information from multiple perspectives
- Provide detailed explanations
- Support claims with retrieved evidence
"""
```

### Disjointed Sections

**Symptom**: Sections don't flow well together

**Solutions**:
```python
# Override CompileReport for better integration
overrides = {
    "CompileReport": {
        "user": """Topic: {topic}

Sections:
{sections}

Compile these into a cohesive report with:
1. Smooth transitions between sections
2. Consistent narrative arc
3. Clear introduction setting context
4. Strong conclusion tying everything together

Your compiled report:"""
    }
}
```

### Retrieval Failures

**Symptom**: Many retrieval errors or poor results

**Solutions**:
```python
def robust_search(query: str) -> str:
    """Search with fallback strategies"""
    try:
        # Primary search
        return primary_search_api(query)
    except:
        try:
            # Fallback search
            return fallback_search_api(query)
        except:
            # Last resort: reformulate and try again
            reformulated = f"information about {query}"
            return basic_search(reformulated)
```

## Next Steps

- Try the [complete examples](../examples/storm-examples.md)
- Learn about [ReAct](react.md) for simpler tool-based workflows
- Explore [Self-Discovery](self-discovery.md) for reasoning without retrieval
- Read the [original paper](https://arxiv.org/abs/2402.14207)

## References

- Original paper: [Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models](https://arxiv.org/abs/2402.14207)
- Stanford STORM project: [https://storm.genie.stanford.edu/](https://storm.genie.stanford.edu/)
- Related: Multi-document synthesis and question generation research
