# Installation Guide

This guide covers all the ways to install Agent Patterns and get your environment set up for development or production use.

## Quick Install

### From PyPI (Recommended)

The easiest way to install Agent Patterns is via pip from PyPI:

```bash
pip install agent-patterns
```

This installs the latest stable version with all required dependencies.

### Upgrade to Latest Version

```bash
pip install --upgrade agent-patterns
```

## Installation from Source

### Standard Installation

Clone the repository and install:

```bash
# Clone the repository
git clone https://github.com/osok/agent-patterns.git
cd agent-patterns

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Development Installation

If you plan to contribute or modify the library, install with development dependencies:

```bash
# Clone and navigate to repository
git clone https://github.com/osok/agent-patterns.git
cd agent-patterns

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

The development installation includes:
- `pytest` - Testing framework
- `pytest-cov` - Code coverage reporting
- `pytest-mock` - Mocking utilities
- `black` - Code formatter
- `ruff` - Fast Python linter
- `mypy` - Static type checker

## Requirements

### System Requirements

- **Python**: 3.10 or higher (3.10, 3.11, 3.12 supported)
- **Operating System**: Linux, macOS, Windows
- **Memory**: Minimum 2GB RAM (4GB+ recommended)

### Core Dependencies

Agent Patterns automatically installs these required dependencies:

```
langgraph>=0.2.0          # State graph management
langchain>=0.3.0          # LLM abstractions
langchain-core>=0.3.0     # Core LangChain functionality
langchain-openai>=0.2.0   # OpenAI integration
langchain-anthropic>=0.2.0 # Anthropic integration
python-dotenv>=1.0.0      # Environment variable management
```

## Environment Setup

### 1. Create Configuration File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Add API Keys

Edit `.env` and add your API keys:

```bash
# Required: At least one API key
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Model configuration
THINKING_MODEL_PROVIDER=openai
THINKING_MODEL_NAME=gpt-4-turbo
THINKING_TEMPERATURE=0.7
```

### 3. Verify Installation

Test your installation:

```python
from agent_patterns.patterns import ReActAgent

# Should import without errors
print("Agent Patterns installed successfully!")
```

## Installation Options

### Minimal Installation (Core Only)

If you only need specific providers:

```bash
# OpenAI only
pip install agent-patterns langchain-openai

# Anthropic only
pip install agent-patterns langchain-anthropic
```

### Specific Version

Install a specific version:

```bash
pip install agent-patterns==0.2.0
```

### From GitHub Branch

Install from a specific branch (for testing unreleased features):

```bash
pip install git+https://github.com/osok/agent-patterns.git@main
```

## Virtual Environment Setup

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Install Agent Patterns
pip install agent-patterns

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n agent-patterns python=3.10

# Activate environment
conda activate agent-patterns

# Install Agent Patterns
pip install agent-patterns

# Deactivate when done
conda deactivate
```

### Using poetry

```bash
# Initialize poetry project
poetry init

# Add Agent Patterns
poetry add agent-patterns

# Install dependencies
poetry install

# Run commands in poetry environment
poetry run python your_script.py
```

## Verification and Testing

### Quick Verification

Create a test script `test_install.py`:

```python
#!/usr/bin/env python3
"""Quick installation verification script."""

import sys

def verify_installation():
    """Verify Agent Patterns installation."""
    try:
        # Import core modules
        from agent_patterns.core import BaseAgent
        from agent_patterns.patterns import (
            ReActAgent,
            ReflectionAgent,
            PlanAndSolveAgent,
            ReflexionAgent,
            LLMCompilerAgent,
            REWOOAgent,
            LATSAgent,
            SelfDiscoveryAgent,
            STORMAgent,
        )

        print("✓ All pattern imports successful")

        # Check version
        import agent_patterns
        print(f"✓ Agent Patterns version: {agent_patterns.__version__}")

        # Check dependencies
        import langgraph
        import langchain
        print("✓ Core dependencies available")

        return True

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)
```

Run the verification:

```bash
python test_install.py
```

### Run Unit Tests

If you installed from source:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=agent_patterns --cov-report=html

# Run specific test file
pytest tests/test_base_agent.py

# Run with verbose output
pytest -v
```

## Troubleshooting Installation

### Common Issues

#### Issue: `pip: command not found`

**Solution**: Install pip or use python's pip module:
```bash
python -m ensurepip --default-pip
# or
python -m pip install agent-patterns
```

#### Issue: Permission denied

**Solution**: Install to user directory or use virtual environment:
```bash
pip install --user agent-patterns
# or create virtual environment (recommended)
python -m venv venv && source venv/bin/activate
```

#### Issue: SSL certificate verification failed

**Solution**: Update certificates or use trusted host:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org agent-patterns
```

#### Issue: Incompatible Python version

**Solution**: Check Python version and upgrade if needed:
```bash
python --version  # Should be 3.10+

# Install specific Python version (macOS with brew)
brew install python@3.10

# Install specific Python version (Ubuntu)
sudo apt install python3.10
```

#### Issue: Dependency conflicts

**Solution**: Use virtual environment and upgrade pip:
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install agent-patterns
```

#### Issue: LangChain/LangGraph version conflicts

**Solution**: Install specific compatible versions:
```bash
pip install langgraph==0.2.0 langchain==0.3.0 agent-patterns
```

### Getting Help

If you encounter installation issues:

1. **Check requirements**: Ensure Python 3.10+
2. **Update pip**: `pip install --upgrade pip`
3. **Use virtual environment**: Isolate dependencies
4. **Check GitHub Issues**: [agent-patterns/issues](https://github.com/osok/agent-patterns/issues)
5. **Ask for help**: Create a new issue with:
   - Python version (`python --version`)
   - OS and version
   - Full error message
   - Installation command used

## IDE Setup

### VS Code

Recommended extensions:
- Python (Microsoft)
- Pylance
- Python Docstring Generator

Settings (`.vscode/settings.json`):
```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.analysis.typeCheckingMode": "basic"
}
```

### PyCharm

1. Open Settings > Project > Python Interpreter
2. Add new virtual environment or select existing
3. Install agent-patterns in selected interpreter
4. Enable type checking: Settings > Editor > Inspections > Python

## Next Steps

After successful installation:

1. Read the [Quick Start Guide](quickstart.md) for a 5-minute tutorial
2. Review [Core Concepts](concepts/what-are-patterns.md) to understand patterns
3. Explore [Pattern API Reference](api/patterns.md) for detailed documentation
4. Check out [Examples](examples/index.md) for real-world usage

## Upgrading from v0.1.x

If you're upgrading from version 0.1.x, be aware of breaking changes:

**Major Changes in v0.2.0:**
- Complete rewrite to synchronous architecture (no async/await)
- New prompt customization system (file-based, instructions, overrides)
- Updated API for all patterns
- New patterns: Reflexion, LLM Compiler, REWOO, LATS, Self-Discovery, STORM

**Migration Steps:**

1. Review the [changelog](changelog.md) for all changes
2. Remove all `async`/`await` keywords from your code
3. Update agent initialization to use new configuration format
4. Update prompt customization approach if using custom prompts
5. Test thoroughly with new synchronous API

Example migration:

```python
# Old (v0.1.x) - Async
async def main():
    agent = ReActAgent(...)
    result = await agent.run(query)

# New (v0.2.0) - Synchronous
def main():
    agent = ReActAgent(...)
    result = agent.run(query)
```
