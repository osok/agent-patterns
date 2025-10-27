# Pattern Comparison Matrix

This comprehensive matrix helps you choose the right agent pattern for your use case.

## Quick Decision Matrix

| Use Case | Primary Pattern | Alternative | Rationale |
|----------|----------------|-------------|-----------|
| **API/Tool Integration** | ReAct ⭐⭐⭐ | REWOO ⭐⭐ | ReAct excels at interactive tool use |
| **Content Writing** | Reflection ⭐⭐⭐ | STORM ⭐⭐ | Reflection for quality, STORM for research |
| **Mathematical Problems** | Self-Discovery ⭐⭐⭐ | Plan & Solve ⭐⭐ | Self-Discovery adapts reasoning strategies |
| **Code Generation** | Reflexion ⭐⭐⭐ | ReAct ⭐⭐ | Reflexion learns from compilation errors |
| **Research Reports** | STORM ⭐⭐⭐ | Plan & Solve ⭐⭐ | STORM designed for multi-perspective research |
| **Data Analysis** | Self-Discovery ⭐⭐⭐ | LLM Compiler ⭐⭐ | Self-Discovery for complex reasoning |
| **Multi-Step Workflows** | Plan & Solve ⭐⭐⭐ | LLM Compiler ⭐⭐ | Plan & Solve for sequential, Compiler for parallel |
| **Cost-Sensitive Tasks** | REWOO ⭐⭐⭐ | ReAct ⭐⭐ | REWOO minimizes LLM calls |
| **Exploratory Problems** | LATS ⭐⭐⭐ | Self-Discovery ⭐⭐ | LATS explores multiple solution paths |
| **Debugging/Troubleshooting** | Reflexion ⭐⭐⭐ | ReAct ⭐⭐ | Reflexion excels at trial-and-error |
| **Question Answering** | ReAct ⭐⭐⭐ | Reflection ⭐ | ReAct for fact-based, Reflection for thoughtful |
| **Creative Writing** | Reflection ⭐⭐⭐ | Self-Discovery ⭐⭐ | Reflection for quality iteration |
| **Planning Complex Projects** | Plan & Solve ⭐⭐⭐ | Self-Discovery ⭐⭐ | Plan & Solve excels at decomposition |
| **Web Research** | STORM ⭐⭐⭐ | ReAct ⭐⭐ | STORM for comprehensive synthesis |
| **Optimization Problems** | LATS ⭐⭐⭐ | Self-Discovery ⭐⭐ | LATS explores solution space systematically |

**Legend**: ⭐⭐⭐ Best Choice | ⭐⭐ Good Alternative | ⭐ Possible but not ideal

## Detailed Use Case Analysis

### Content Creation & Writing

#### Blog Posts & Articles
**Primary**: Reflection ⭐⭐⭐
- **Why**: Iterative refinement produces high-quality content
- **Alternative**: STORM ⭐⭐ (if research-heavy)
- **When to use Reflection**: Quality matters more than speed
- **When to use STORM**: Need comprehensive research from multiple angles

```python
# Reflection for blog posts
agent = ReflectionAgent(
    llm_configs={"documentation": {...}, "reflection": {...}},
    custom_instructions="Write engaging, SEO-friendly blog content"
)
```

#### Technical Documentation
**Primary**: Plan & Solve ⭐⭐⭐
- **Why**: Structured approach ensures completeness
- **Alternative**: Reflection ⭐⭐ (for polish)
- **When to use Plan & Solve**: Need comprehensive, organized documentation
- **When to use Reflection**: Focus on clarity and readability

#### Research Papers/Reports
**Primary**: STORM ⭐⭐⭐
- **Why**: Multi-perspective research with source synthesis
- **Alternative**: Plan & Solve ⭐⭐ (for structured reports)
- **When to use STORM**: Need diverse viewpoints and comprehensive coverage
- **When to use Plan & Solve**: Have clear outline, need execution

#### Creative Fiction
**Primary**: Reflection ⭐⭐⭐
- **Why**: Iterative refinement improves narrative quality
- **Alternative**: Self-Discovery ⭐ (for complex plots)
- **When to use Reflection**: Focus on prose quality and coherence
- **When to use Self-Discovery**: Complex story structure requires adaptive reasoning

### Problem Solving

#### Mathematical Proofs
**Primary**: Self-Discovery ⭐⭐⭐
- **Why**: Selects appropriate mathematical reasoning strategies
- **Alternative**: Plan & Solve ⭐⭐
- **When to use Self-Discovery**: Complex, multi-step proofs
- **When to use Plan & Solve**: Straightforward problems with clear steps

#### Logic Puzzles
**Primary**: LATS ⭐⭐⭐
- **Why**: Tree search explores solution space systematically
- **Alternative**: Self-Discovery ⭐⭐
- **When to use LATS**: Multiple possible approaches need exploration
- **When to use Self-Discovery**: Need to select best reasoning strategy

#### Code Debugging
**Primary**: Reflexion ⭐⭐⭐
- **Why**: Learns from test failures and refines approach
- **Alternative**: ReAct ⭐⭐ (with debugging tools)
- **When to use Reflexion**: Can run tests and get error feedback
- **When to use ReAct**: Need to use debugger or inspection tools

#### Optimization Problems
**Primary**: LATS ⭐⭐⭐
- **Why**: Explores and evaluates multiple solutions
- **Alternative**: Self-Discovery ⭐⭐
- **When to use LATS**: Need to find optimal solution among many candidates
- **When to use Self-Discovery**: Need adaptive strategy for complex constraints

#### Algorithm Design
**Primary**: Self-Discovery ⭐⭐⭐
- **Why**: Selects appropriate algorithmic reasoning approaches
- **Alternative**: Plan & Solve ⭐⭐
- **When to use Self-Discovery**: Complex algorithms requiring multiple techniques
- **When to use Plan & Solve**: Clear algorithmic structure

### Task Automation

#### API Orchestration
**Primary**: ReAct ⭐⭐⭐
- **Why**: Interactive reasoning about API calls and responses
- **Alternative**: REWOO ⭐⭐ (for cost efficiency)
- **When to use ReAct**: Need dynamic decision-making based on API responses
- **When to use REWOO**: Predictable API workflow, cost-sensitive

#### Web Scraping & Data Collection
**Primary**: ReAct ⭐⭐⭐
- **Why**: Adaptive navigation and data extraction
- **Alternative**: Plan & Solve ⭐⭐ (for structured sites)
- **When to use ReAct**: Dynamic websites requiring adaptive scraping
- **When to use Plan & Solve**: Well-structured sites with predictable layout

#### ETL Pipelines
**Primary**: LLM Compiler ⭐⭐⭐
- **Why**: Parallel execution of independent transformations
- **Alternative**: Plan & Solve ⭐⭐
- **When to use LLM Compiler**: Independent data transformations can run in parallel
- **When to use Plan & Solve**: Sequential dependencies between steps

#### Workflow Automation
**Primary**: Plan & Solve ⭐⭐⭐
- **Why**: Clear decomposition of multi-step workflows
- **Alternative**: LLM Compiler ⭐⭐ (if parallelizable)
- **When to use Plan & Solve**: Sequential workflow with dependencies
- **When to use LLM Compiler**: Independent tasks can run concurrently

#### Database Queries
**Primary**: REWOO ⭐⭐⭐
- **Why**: Efficient planning minimizes expensive database calls
- **Alternative**: ReAct ⭐⭐
- **When to use REWOO**: Cost of queries is high, can plan ahead
- **When to use ReAct**: Need dynamic query adjustment based on results

### Research & Analysis

#### Market Research
**Primary**: STORM ⭐⭐⭐
- **Why**: Multi-perspective analysis from diverse sources
- **Alternative**: Plan & Solve ⭐⭐
- **When to use STORM**: Need comprehensive view of market landscape
- **When to use Plan & Solve**: Structured research with clear objectives

#### Competitive Analysis
**Primary**: STORM ⭐⭐⭐
- **Why**: Synthesizes information from multiple competitors
- **Alternative**: Self-Discovery ⭐⭐
- **When to use STORM**: Need balanced view across competitors
- **When to use Self-Discovery**: Complex comparative reasoning required

#### Literature Review
**Primary**: STORM ⭐⭐⭐
- **Why**: Designed for multi-source research synthesis
- **Alternative**: Plan & Solve ⭐⭐
- **When to use STORM**: Need to synthesize diverse academic sources
- **When to use Plan & Solve**: Structured review of specific topics

#### Data Analysis & Insights
**Primary**: Self-Discovery ⭐⭐⭐
- **Why**: Adapts analytical approach based on data characteristics
- **Alternative**: Plan & Solve ⭐⭐
- **When to use Self-Discovery**: Exploratory analysis, unclear best approach
- **When to use Plan & Solve**: Standard analytical workflow

#### Trend Analysis
**Primary**: STORM ⭐⭐⭐
- **Why**: Synthesizes trends from multiple data sources
- **Alternative**: Self-Discovery ⭐⭐
- **When to use STORM**: Need comprehensive trend synthesis
- **When to use Self-Discovery**: Complex pattern recognition in trends

### Software Development

#### Code Generation
**Primary**: Reflexion ⭐⭐⭐
- **Why**: Learns from test failures and compilation errors
- **Alternative**: Plan & Solve ⭐⭐
- **When to use Reflexion**: Can run tests and iterate on failures
- **When to use Plan & Solve**: Clear specification, straightforward implementation

#### Code Review
**Primary**: Reflection ⭐⭐⭐
- **Why**: Multiple review passes improve quality
- **Alternative**: Self-Discovery ⭐⭐
- **When to use Reflection**: Focus on code quality and best practices
- **When to use Self-Discovery**: Complex code requiring different review strategies

#### Test Generation
**Primary**: Plan & Solve ⭐⭐⭐
- **Why**: Systematic decomposition of test scenarios
- **Alternative**: Self-Discovery ⭐⭐
- **When to use Plan & Solve**: Clear testing requirements
- **When to use Self-Discovery**: Need creative test case generation

#### Refactoring
**Primary**: Reflexion ⭐⭐⭐
- **Why**: Iterates until tests pass with improved code
- **Alternative**: Reflection ⭐⭐
- **When to use Reflexion**: Have tests to validate refactoring
- **When to use Reflection**: Focus on code clarity and design

#### Architecture Design
**Primary**: Self-Discovery ⭐⭐⭐
- **Why**: Selects appropriate architectural reasoning approaches
- **Alternative**: LATS ⭐⭐ (to explore options)
- **When to use Self-Discovery**: Complex system requiring multiple design considerations
- **When to use LATS**: Need to evaluate multiple architectural options

### Decision Making

#### Strategic Planning
**Primary**: LATS ⭐⭐⭐
- **Why**: Explores and evaluates multiple strategic options
- **Alternative**: Self-Discovery ⭐⭐
- **When to use LATS**: Need to explore multiple paths and outcomes
- **When to use Self-Discovery**: Need adaptive strategic reasoning

#### Risk Assessment
**Primary**: Self-Discovery ⭐⭐⭐
- **Why**: Adapts risk analysis approach to situation
- **Alternative**: Plan & Solve ⭐⭐
- **When to use Self-Discovery**: Complex, multifaceted risks
- **When to use Plan & Solve**: Standard risk assessment framework

#### Resource Allocation
**Primary**: LLM Compiler ⭐⭐⭐
- **Why**: Evaluates resource allocation scenarios in parallel
- **Alternative**: Self-Discovery ⭐⭐
- **When to use LLM Compiler**: Independent resource allocation decisions
- **When to use Self-Discovery**: Complex interdependencies

#### Scenario Planning
**Primary**: LATS ⭐⭐⭐
- **Why**: Explores multiple future scenarios systematically
- **Alternative**: Self-Discovery ⭐⭐
- **When to use LATS**: Need to evaluate diverse future scenarios
- **When to use Self-Discovery**: Need adaptive scenario generation

### Customer Support

#### Troubleshooting
**Primary**: Reflexion ⭐⭐⭐
- **Why**: Learns from failed solutions, tries alternatives
- **Alternative**: ReAct ⭐⭐ (with diagnostic tools)
- **When to use Reflexion**: Can test solutions and get feedback
- **When to use ReAct**: Need to use diagnostic tools interactively

#### FAQ Generation
**Primary**: STORM ⭐⭐⭐
- **Why**: Synthesizes FAQs from multiple customer interactions
- **Alternative**: Plan & Solve ⭐⭐
- **When to use STORM**: Need comprehensive FAQ from diverse sources
- **When to use Plan & Solve**: Structured FAQ based on known topics

#### Knowledge Base Search
**Primary**: ReAct ⭐⭐⭐
- **Why**: Interactive search and refinement
- **Alternative**: REWOO ⭐ (for efficiency)
- **When to use ReAct**: Need adaptive search based on results
- **When to use REWOO**: Predictable search patterns

## Pattern Characteristics Comparison

### Computational Cost

| Pattern | LLM Calls | Cost | Best For |
|---------|-----------|------|----------|
| ReAct | High (iterative) | $$ | Quality interactions |
| Reflection | Medium-High | $$ | Quality content |
| Plan & Solve | Medium | $ | Balanced efficiency |
| Self-Discovery | High | $$$ | Complex reasoning |
| Reflexion | Very High | $$$ | Learning from failures |
| REWOO | Low | $ | Cost-sensitive tasks |
| LATS | Very High | $$$$ | Exploration |
| LLM Compiler | Medium | $$ | Parallel efficiency |
| STORM | High | $$$ | Comprehensive research |

**Legend**: $ Low | $$ Medium | $$$ High | $$$$ Very High

### Complexity & Learning Curve

| Pattern | Complexity | Setup Time | When to Start With |
|---------|------------|------------|-------------------|
| ReAct | ⭐ Simple | Quick | First pattern to learn |
| Reflection | ⭐ Simple | Quick | Great starter pattern |
| Plan & Solve | ⭐⭐ Medium | Moderate | After mastering basics |
| REWOO | ⭐⭐ Medium | Moderate | When cost matters |
| Self-Discovery | ⭐⭐⭐ Complex | Longer | For advanced users |
| Reflexion | ⭐⭐⭐ Complex | Longer | When you understand Reflection |
| LLM Compiler | ⭐⭐⭐⭐ Very Complex | Significant | For expert users |
| LATS | ⭐⭐⭐⭐ Very Complex | Significant | For expert users |
| STORM | ⭐⭐⭐ Complex | Longer | When you need research |

### Output Quality vs Speed

```
Quality ↑
|
| Reflexion (learns)     LATS (explores)
|
| Self-Discovery        STORM (comprehensive)
| (adaptive)
|
| Reflection (iterates)
|
| Plan & Solve (structured)    LLM Compiler (parallel)
|
| ReAct (interactive)
|
| REWOO (efficient)
|
└────────────────────────────────────────→ Speed
```

### Recommended Learning Path

1. **Start**: ReAct → Learn tool use and iterative reasoning
2. **Next**: Reflection → Understand quality improvement through iteration
3. **Then**: Plan & Solve → Learn structured decomposition
4. **Intermediate**: REWOO, Self-Discovery → Efficiency and adaptation
5. **Advanced**: Reflexion, STORM → Learning and research
6. **Expert**: LATS, LLM Compiler → Exploration and parallelism

## Decision Flowchart

```
Do you need to use external tools/APIs?
├─ Yes → ReAct (or REWOO if cost-sensitive)
└─ No → Continue

Is quality iteration important?
├─ Yes → Do you learn from failures?
│   ├─ Yes → Reflexion
│   └─ No → Reflection
└─ No → Continue

Is it a planning/decomposition task?
├─ Yes → Are subtasks independent?
│   ├─ Yes → LLM Compiler
│   └─ No → Plan & Solve
└─ No → Continue

Do you need comprehensive research?
├─ Yes → STORM
└─ No → Continue

Do you need to explore multiple solutions?
├─ Yes → LATS
└─ No → Self-Discovery (for adaptive reasoning)
```

## Pattern Combination Strategies

Some tasks benefit from combining patterns:

### Sequential Combinations

**STORM → Reflection**: Research then polish
- Use STORM for comprehensive research
- Use Reflection to refine and polish the final report

**Self-Discovery → Reflexion**: Strategy then learning
- Use Self-Discovery to select initial approach
- Use Reflexion to learn and improve through trials

**Plan & Solve → ReAct**: Plan then execute
- Use Plan & Solve to create detailed plan
- Use ReAct to execute steps with tool interaction

### Parallel Combinations

**Multiple ReAct agents**: Parallel tool usage
- Different agents handle different tool domains
- Combine results for comprehensive answer

## Next Steps

- Choose a pattern from the matrix above
- Read the detailed [pattern documentation](react.md)
- Try the [examples](../examples/index.md)
- Learn about [customization](../guides/prompt-customization.md)
