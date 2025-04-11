# Contributing to Agent Patterns

Thank you for your interest in contributing to Agent Patterns! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install the package in development mode:
```bash
pip install -e .
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write docstrings for all public functions and classes
- Include unit tests for new features

## Import Paths

We maintain compatibility with both development mode and installed package mode. When writing code:

### For Development

When developing locally, the package structure includes the `src` directory:
```python
from src.agent_patterns.patterns import ReActAgent
```

### For Installation

When the package is installed via pip, imports should not include the `src` prefix:
```python
from agent_patterns.patterns import ReActAgent
```

To support both modes in examples and tests, consider using the following pattern:
```python
try:
    from agent_patterns.patterns import ReActAgent  # For installed package
except ImportError:
    from src.agent_patterns.patterns import ReActAgent  # For development
```

## Prompt Directory Paths

When referencing prompt directories, ensure compatibility with both development and installed structures:

```python
# Get the project root directory
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent

# Try both development and installed paths
src_prompt_dir = project_root / "src" / "agent_patterns" / "prompts"
pkg_prompt_dir = project_root / "agent_patterns" / "prompts"

if src_prompt_dir.exists():
    prompt_dir = str(src_prompt_dir)
else:
    prompt_dir = str(pkg_prompt_dir)
```

## Adding New Agent Patterns

When adding new agent patterns:

1. Create your agent class in the appropriate directory
2. Update the relevant `__init__.py` files to include your agent
3. Add tests for your agent
4. Create example files demonstrating usage
5. Update documentation to include your agent

## Making Fixes to Existing Code

Before creating a pull request, run our import path checker:
```bash
python tools/fix_imports.py
```

This tool will automatically fix common import and prompt directory path issues in examples and tests.

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Create a pull request with a clear description of the changes

Thank you for contributing to Agent Patterns! 