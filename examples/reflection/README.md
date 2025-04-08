# Reflection Agent Examples

This directory contains examples demonstrating the Reflection agent pattern implementation.

## Examples

### 1. Simple Example (`simple_example.py`)

A basic example showing how to initialize and run a Reflection agent to improve text generation. This demonstrates the core reflection workflow of generating an initial response, critiquing it, and then refining it based on the critique.

**Features demonstrated:**
- Setting up a Reflection agent with separate generator and critic models
- Initial response generation
- Critical evaluation and refinement
- Quality improvement through reflection

### 2. Code Review Example (`code_review_example.py`)

An advanced example showing how to use the Reflection agent for code review and improvement suggestions. This demonstrates the pattern's ability to analyze code for bugs, inefficiencies, and best practices.

**Features demonstrated:**
- Code analysis and critique
- Identifying bugs and edge cases
- Suggesting performance improvements
- Providing specific recommendations and code examples

## Running the Examples

Make sure you have set up your environment variables first:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-api-key-here
```

To run an example:

```bash
# For simple example
python examples/reflection/simple_example.py

# For code review example
python examples/reflection/code_review_example.py
```