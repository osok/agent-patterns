# LATS Agent Examples

This directory contains examples demonstrating the Language Agent Tree Search (LATS) pattern implementation in the Agent Patterns library.

## Description

The LATS agent pattern implements a Monte Carlo Tree Search (MCTS) approach to solving complex reasoning problems. It explores multiple reasoning paths simultaneously and evaluates their potential, focusing computational effort on the most promising directions.

Key features:
- Tree-based exploration of reasoning paths
- UCB1 selection for balancing exploration vs. exploitation
- Multiple LLM roles: thinking (expansion) and evaluation
- Configurable search parameters (depth, iterations, branching factor)

## Examples

- [Simple Example](./simple_example.py) - Demonstrates basic usage for developing a strategy to increase user engagement on a social media platform.
- [Engineering Problem Example](./engineering_problem_example.py) - Explores multiple approaches to design a sustainable urban transportation system with specific constraints.
- [Medical Diagnosis Example](./medical_diagnosis_example.py) - Demonstrates clinical reasoning by exploring multiple diagnostic hypotheses and treatment options for a complex medical case.

## Running the Examples

To run any of the LATS agent examples:

```bash
python examples/lats/simple_example.py
python examples/lats/engineering_problem_example.py
python examples/lats/medical_diagnosis_example.py
```

Make sure you have set up your environment variables first, including your OpenAI API key. 