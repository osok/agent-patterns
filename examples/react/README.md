# ReAct Agent Examples

This directory contains examples demonstrating the ReAct (Reasoning + Acting) agent pattern implementation.

## Examples

### 1. Simple Example (`simple_example.py`)

A basic example showing how to initialize and run a ReAct agent with simple tools (search, calculator, and weather). This demonstrates the core tool-use functionality of the ReAct pattern.

**Features demonstrated:**
- Setting up a ReAct agent with multiple tools
- Basic tool integration
- Simple question answering with tool use

### 2. Complex Reasoning Example (`complex_reasoning_example.py`)

An advanced example showing how to use ReAct for multi-step reasoning tasks that require coordination between specialized tools. This demonstrates more sophisticated information retrieval and synthesis capabilities.

**Features demonstrated:**
- Custom tool implementation (encyclopedia, concept extraction, concept comparison)
- Multi-step reasoning flow
- Complex task decomposition
- Debugging with reasoning trace visualization

## Running the Examples

Make sure you have set up your environment variables first:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-api-key-here
```

To run an example:

```bash
# For simple example
python examples/react/simple_example.py

# For complex reasoning example
python examples/react/complex_reasoning_example.py
```