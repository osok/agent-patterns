# Agent Patterns Examples

This directory contains examples for each implemented agent pattern in the Agent Patterns library. Each pattern has its own directory with specific examples demonstrating different use cases and features.

## Available Pattern Examples

### [ReAct Agent](./react/)
Implementation of the Reasoning + Acting pattern for tool use:
- [Simple Example](./react/simple_example.py) - Basic tool usage with weather and calculator tools
- [Complex Reasoning Example](./react/complex_reasoning_example.py) - Multi-step reasoning with specialized AI concept tools

### [Plan & Solve Agent](./plan_and_solve/)
Implementation of the Plan & Solve pattern for planning and execution:
- [Simple Example](./plan_and_solve/simple_example.py) - Creating a Python learning curriculum
- [Trip Planner Example](./plan_and_solve/trip_planner_example.py) - Detailed Tokyo travel itinerary with constraints

### [Reflection Agent](./reflection/)
Implementation of the Reflection pattern for self-critique and refinement:
- [Simple Example](./reflection/simple_example.py) - Explaining relativity theory with self-critique
- [Code Review Example](./reflection/code_review_example.py) - Code analysis with bug detection and improvements

### [Reflexion Agent](./reflexion/)
Implementation of the Reflexion pattern for multi-trial learning with reflection memory:
- [Simple Example](./reflexion/simple_example.py) - Fibonacci function implementation with iterative improvement
- [Chess Analysis Example](./reflexion/chess_analysis_example.py) - Chess position analysis with progressive refinement

## Running the Examples

Each example can be run directly using Python. Make sure you have set up your environment variables first:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-api-key-here
```

Then run any example:

```bash
python examples/PATTERN_DIRECTORY/EXAMPLE_FILE.py
```

For instance:

```bash
python examples/reflection/simple_example.py
```