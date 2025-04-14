# REWOO Agent Pattern Examples

This directory contains examples of the Reasoning Without Observation (REWOO) agent pattern. The REWOO pattern separates the planning and execution phases of problem-solving, allowing for better strategic thinking without being influenced by partial execution results.

## Available Examples

### Simple Example

A basic implementation of the REWOO pattern conducting a climate change research task with a structured approach, memory integration, and tool usage.

**Run from project root:**
```bash
python examples/rewoo/simple_example.py
```

**What it demonstrates:**
- Separation of planning and execution phases
- Integration with semantic, episodic, and procedural memory
- Custom tool provider implementation with search and calculator tools
- Mock mode for testing without API keys

### Web Research Example

A more advanced example showing how the REWOO pattern can be used for comprehensive web research tasks with information extraction and structured reporting.

**Run from project root:**
```bash
python examples/rewoo/web_research_example.py
```

**What it demonstrates:**
- Structured information gathering from simulated web sources
- Advanced planning capabilities for research tasks
- Information synthesis into a comprehensive report
- Memory retention of research findings

### Math Solver Example

Shows how the REWOO pattern can break down and solve complex mathematical word problems step by step.

**Run from project root:**
```bash
python examples/rewoo/math_solver_example.py
```

**What it demonstrates:**
- Mathematical problem decomposition
- Step-by-step solution planning
- Tool usage for calculations
- Formal solution presentation with clear reasoning

### Travel Planner Example

A complex example showing how REWOO can plan and execute a detailed travel itinerary with multiple constraints.

**Run from project root:**
```bash
python examples/rewoo/travel_planner_example.py
```

**What it demonstrates:**
- Complex planning with multiple constraints
- Itinerary creation with flights, accommodations, and attractions
- Consideration of budget, time, and preference constraints
- Structuring complex information into a usable travel plan

## Environment Setup

Make sure you have set your OpenAI API key:

```bash
# Set your OpenAI API key in the .env file or as an environment variable
export OPENAI_API_KEY=your-api-key-here
```

All examples have a mock mode that will run without an API key, providing pre-scripted responses for testing purposes.

## Memory Integration

The REWOO examples demonstrate how to use different memory types:
- **Semantic Memory**: Stores factual information (e.g., climate change definitions)
- **Episodic Memory**: Records experiences and interactions
- **Procedural Memory**: Maintains patterns and methodologies (e.g., research methodology)

## Tool Integration

The examples show how to create custom tool providers that can be used with the REWOO agent, including:
- Search tools for information retrieval
- Calculator tools for mathematical operations
- Simulated web research tools 