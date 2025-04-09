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

### [LLM Compiler Agent](./llm_compiler/)
Implementation of the LLM Compiler pattern for parallel function calling and task orchestration:
- [Basic Example](./llm_compiler/llm_compiler_example.py) - Demonstrates basic usage with multiple tools
- [Performance Comparison](./llm_compiler/parallel_vs_sequential_example.py) - Compares parallel vs sequential execution
- [DAG Visualization](./llm_compiler/llm_compiler_dag_example.py) - Visualizes task dependencies with ASCII art

### [REWOO Agent](./rewoo/)
Implementation of the Reasoning Without Observation pattern for decoupled planning and execution:
- [Simple Example](./rewoo/simple_example.py) - Research task using separate planning and execution components
- [Web Research Example](./rewoo/web_research_example.py) - Comprehensive research report with structured information extraction
- [Math Solver Example](./rewoo/math_solver_example.py) - Step-by-step solution to mathematical word problems
- [Travel Planner Example](./rewoo/travel_planner_example.py) - Detailed travel itinerary with flights, accommodations, and attractions

### [LATS Agent](./lats/)
Implementation of the Language Agent Tree Search pattern for exploring multiple reasoning paths:
- [Simple Example](./lats/simple_example.py) - Strategy development using Monte Carlo Tree Search approach
- [Engineering Problem Example](./lats/engineering_problem_example.py) - Sustainable urban transportation system design
- [Medical Diagnosis Example](./lats/medical_diagnosis_example.py) - Clinical reasoning with diagnostic hypotheses exploration

### [STORM Agent](./storm/)
Implementation of the Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking pattern for article generation:
- [Basic Article Generation](./storm/basic_article_generation.py) - Complete article generation with structured outline
- [Streaming Article Generation](./storm/streaming_article_generation.py) - Real-time updates during article generation process

### [Self-Discovery Agent](./self_discovery/)
Implementation of the Self-Discovery pattern for dynamic reasoning structure composition:
- [Basic Reasoning](./self_discovery/basic_reasoning.py) - Complex problem solving with self-discovered reasoning strategies
- [Simulated Streaming](./self_discovery/basic_reasoning.py) - Step-by-step view of the self-discovery and execution process

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

Or for REWOO:

```bash
python examples/rewoo/simple_example.py
```