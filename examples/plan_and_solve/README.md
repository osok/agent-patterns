# Plan & Solve Agent Examples

This directory contains examples demonstrating the Plan & Solve agent pattern implementation.

## Examples

### 1. Simple Example (`simple_example.py`)

A basic example showing how to initialize and run a Plan & Solve agent to create a learning plan. This demonstrates the core planning and execution workflow of the pattern.

**Features demonstrated:**
- Setting up a Plan & Solve agent with different models for planning and execution
- Generating a structured plan
- Executing the plan steps
- Aggregating the results

### 2. Trip Planner Example (`trip_planner_example.py`)

An advanced example showing how to use the Plan & Solve agent to create a detailed travel itinerary. This demonstrates the pattern's ability to handle complex planning with multiple constraints and requirements.

**Features demonstrated:**
- Detailed planning with sequential dependencies
- Handling complex specifications and constraints
- Structured output generation
- Cost estimation and logistics planning

## Running the Examples

Make sure you have set up your environment variables first:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-api-key-here
```

To run an example:

```bash
# For simple example
python examples/plan_and_solve/simple_example.py

# For trip planner example
python examples/plan_and_solve/trip_planner_example.py
```