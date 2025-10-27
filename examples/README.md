# Agent Patterns Examples

This directory contains example scripts demonstrating how to use the various agent patterns and customization features.

## Prerequisites

Before running any examples, you need to:

1. **Set up your environment**:
   ```bash
   # Copy the example .env file
   cp .env.example .env

   # Edit .env and add your API keys
   # At minimum, you need either OPENAI_API_KEY or ANTHROPIC_API_KEY
   ```

2. **Install the package** (if not already installed):
   ```bash
   pip install agent-patterns
   # OR for development:
   pip install -e .
   ```

## Running the Examples

⚠️ **Important**: All examples must be run from the **project root directory**, not from the `examples/` folder.

```bash
# Run from the project root (where .env is located)
python examples/react_example.py
python examples/reflection_example.py
# etc.
```

Running from the wrong directory will cause the `.env` file not to be found, resulting in API key errors.

## Available Examples

### Pattern Examples

These examples demonstrate individual agent patterns:

#### 1. ReAct Agent (`react_example.py`)
Demonstrates the ReAct (Reason + Act) pattern for answering questions that require tool use and reasoning.

- **What it shows**: Tool integration, reasoning loops, observation handling
- **Use case**: Question answering with external tools (search, calculation, etc.)
- **Run**: `python examples/react_example.py`

#### 2. Reflection Agent (`reflection_example.py`)
Demonstrates the Reflection pattern for generating and refining high-quality outputs through self-critique.

- **What it shows**: Generate → Critique → Refine workflow
- **Use case**: High-quality content generation (stories, essays, documentation)
- **Run**: `python examples/reflection_example.py`

#### 3. LLM Compiler Agent (`llm_compiler_example.py`)
Demonstrates the LLM Compiler pattern for executing complex multi-tool workflows using DAG-based execution.

- **What it shows**: Parallel tool execution, dependency management, optimized workflows
- **Use case**: Complex tasks requiring multiple tools with dependencies
- **Run**: `python examples/llm_compiler_example.py`

#### 4. REWOO Agent (`rewoo_example.py`)
Demonstrates the REWOO (Reason Without Observation) pattern that separates planning from execution for cost-effective multi-tool workflows.

- **What it shows**: Worker-Solver pattern, plan-then-execute, reduced LLM calls
- **Use case**: Efficient reasoning when LLM calls are expensive
- **Run**: `python examples/rewoo_example.py`

### Customization Examples

These examples demonstrate how to customize agent behavior:

#### 5. Custom Instructions (`custom_instructions_example.py`)
Shows how to use `custom_instructions` parameter to inject domain-specific context into any agent pattern without modifying prompt templates.

- **What it shows**: Adding domain knowledge, constraints, and guidelines
- **Use case**: Adapting patterns to specific domains (medical, legal, technical, etc.)
- **Run**: `python examples/custom_instructions_example.py`

#### 6. Prompt Overrides (`prompt_overrides_example.py`)
Shows how to use `prompt_overrides` parameter to programmatically replace specific prompt templates at runtime.

- **What it shows**: Complete prompt replacement, A/B testing, dynamic prompts
- **Use case**: Experimenting with different prompts, creating specialized variants
- **Run**: `python examples/prompt_overrides_example.py`

## Example Output

Most examples will output:
- Initialization messages
- Step-by-step execution traces (depending on the pattern)
- Final results
- Any errors encountered

If you see an error about missing API keys, make sure:
1. You created a `.env` file in the project root
2. You added your API keys to the `.env` file
3. You're running the example from the project root directory

## Modifying Examples

Feel free to modify these examples to experiment with:
- Different models (change in `.env`)
- Different tasks/prompts
- Different tools
- Different configuration parameters
- Custom instructions and prompt overrides

## Need More Examples?

Currently, we have examples for 4 out of 9 patterns. Missing examples:
- Plan & Solve
- Reflexion
- LATS
- Self-Discovery
- STORM

Contributions welcome! See our [contribution guide](https://agent-patterns.readthedocs.io/en/latest/) for details.

## Documentation

For more detailed documentation, see:
- **[Full Documentation](https://agent-patterns.readthedocs.io/en/latest/)** - Complete guides and API reference
- **[Main README](../README.md)** - Project overview and quick start
- **[.env.example](../.env.example)** - Configuration options

## Support

- **Issues**: [GitHub Issues](https://github.com/osok/agent-patterns/issues)
- **Discussions**: [GitHub Discussions](https://github.com/osok/agent-patterns/discussions)
- **Documentation**: [Read the Docs](https://agent-patterns.readthedocs.io/en/latest/)
