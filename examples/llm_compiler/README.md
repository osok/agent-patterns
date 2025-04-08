# LLM Compiler Pattern Examples

This directory contains examples demonstrating the LLM Compiler pattern, a parallel task execution framework that efficiently orchestrates multiple function calls.

## What is the LLM Compiler Pattern?

The LLM Compiler pattern optimizes agent workflows by:

1. **Generating a Directed Acyclic Graph (DAG)** of tasks
2. **Executing tasks in parallel** when they don't depend on each other
3. **Streaming results** as soon as they're available
4. **Reducing token usage** by minimizing redundant LLM calls

Unlike sequential patterns (like ReAct), the LLM Compiler identifies which tasks can be executed concurrently and which require dependencies, leading to better performance.

## Example Files

### 1. Basic Example (`llm_compiler_example.py`)

A simple introduction to using the LLM Compiler agent with:
- Basic setup and configuration
- Multiple example queries
- Streaming output demonstration

Run with:
```bash
python examples/llm_compiler/llm_compiler_example.py
```

### 2. Performance Comparison (`parallel_vs_sequential_example.py`)

Directly compares the LLM Compiler pattern against sequential execution:
- Uses simulated tool latency to demonstrate parallel execution benefits
- Shows quantitative performance improvements
- Explains when the pattern is most beneficial

Run with:
```bash
python examples/llm_compiler/parallel_vs_sequential_example.py
```

### 3. DAG Visualization (`llm_compiler_dag_example.py`)

Visualizes the directed acyclic graph (DAG) of tasks:
- Shows a complex workflow with interdependent tasks
- Demonstrates how task dependencies are managed
- Provides ASCII art visualization of the task graph

Run with:
```bash
python examples/llm_compiler/llm_compiler_dag_example.py
```

## Use Cases

The LLM Compiler pattern is particularly valuable when:

1. **You have multiple independent tasks** - They can be executed in parallel for better performance
2. **Tasks have complex dependencies** - The pattern automatically manages execution order
3. **Response time is critical** - Parallel execution reduces overall latency
4. **You want to reduce token usage** - The pattern minimizes redundant LLM calls

## Requirements

To run these examples, you'll need:
- Python 3.8+
- OpenAI API key (set in your .env file)
- Required packages (`langchain`, `langgraph`, etc.)

## Modifying the Examples

You can customize these examples by:
- Adding your own tools
- Changing the LLM models
- Modifying the query complexity
- Adding visualization features

## Further Reading

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LLMCompiler Paper](https://arxiv.org/abs/2312.04511) - "An LLM Compiler for Parallel Function Calling" 