# Reflexion Agent Examples

This directory contains examples demonstrating the Reflexion agent pattern implementation.

## Examples

### 1. Simple Example (`simple_example.py`)

A basic example showing how to initialize and run a Reflexion agent to solve a Fibonacci implementation task. This demonstrates the core reflexion workflow of learning from past attempts through multiple trials with a persistent reflection memory.

**Features demonstrated:**
- Setting up a Reflexion agent with multiple LLM roles
- Multi-trial problem-solving approach
- Memory-based learning from past attempts
- Evaluation and reflection on each trial

### 2. Chess Analysis Example (`chess_analysis_example.py`)

An advanced example showing how to use the Reflexion agent for chess position analysis. This demonstrates the pattern's ability to improve complex reasoning through reflection and iteration.

**Features demonstrated:**
- Complex position analysis in a specialized domain
- Improving analysis quality through reflection
- Learning from specific analytical mistakes
- Building on successful reasoning patterns

## Running the Examples

Make sure you have set up your environment variables first:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-api-key-here
```

To run an example:

```bash
# For simple example
python examples/reflexion/simple_example.py

# For chess analysis example
python examples/reflexion/chess_analysis_example.py
```