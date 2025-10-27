# Contributing to Agent Patterns

Thank you for your interest in contributing to Agent Patterns! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Types of Contributions](#types-of-contributions)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in Agent Patterns a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Report unacceptable behavior to [osok@users.noreply.github.com](mailto:osok@users.noreply.github.com). All complaints will be reviewed and investigated promptly and fairly.

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- GitHub account
- OpenAI or Anthropic API key (for testing)

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
```bash
git clone https://github.com/YOUR-USERNAME/agent-patterns.git
cd agent-patterns
```

3. **Add upstream remote**:
```bash
git remote add upstream https://github.com/osok/agent-patterns.git
```

---

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- Agent Patterns in editable mode
- pytest, pytest-cov, pytest-mock
- black, ruff, mypy
- All core dependencies

### 3. Set Up Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Verify Setup

```bash
# Run tests
pytest

# Check formatting
black --check agent_patterns tests examples

# Check linting
ruff check agent_patterns tests examples

# Check types
mypy agent_patterns
```

All checks should pass.

---

## Making Changes

### Branch Strategy

1. **Keep main branch synced**:
```bash
git checkout main
git pull upstream main
```

2. **Create feature branch**:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

Branch naming:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### Making Code Changes

1. **Edit code** in your feature branch
2. **Add tests** for new functionality
3. **Update documentation** if needed
4. **Run tests** frequently:
```bash
pytest tests/test_your_changes.py -v
```

### Commit Messages

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "Add STORM pattern implementation"
git commit -m "Fix ReAct infinite loop on empty tool results"
git commit -m "Update README with new pattern examples"

# Bad
git commit -m "fix bug"
git commit -m "updates"
git commit -m "WIP"
```

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting (no code change)
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance

**Example:**
```
feat: Add LATS pattern implementation

Implements Language Agent Tree Search pattern with:
- Tree node expansion
- Evaluation and backpropagation
- Best path extraction

Closes #123
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_base_agent.py

# Run specific test
pytest tests/test_base_agent.py::test_init

# Run with coverage
pytest --cov=agent_patterns --cov-report=html

# Run verbose
pytest -v

# Run with output
pytest -s
```

### Writing Tests

Create tests in `tests/` directory:

```python
"""Test module for MyNewPattern."""

import pytest
from unittest.mock import Mock
from agent_patterns.patterns import MyNewPattern


class TestMyNewPattern:
    """Test cases for MyNewPattern."""

    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM."""
        llm = Mock()
        llm.invoke.return_value.content = "Test response"
        return llm

    @pytest.fixture
    def agent(self, mock_llm):
        """Create test agent."""
        agent = MyNewPattern(
            llm_configs={
                "thinking": {
                    "provider": "openai",
                    "model_name": "gpt-4-turbo"
                }
            }
        )
        agent._llm_cache["thinking"] = mock_llm
        return agent

    def test_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.graph is not None

    def test_run_basic(self, agent):
        """Test basic run functionality."""
        result = agent.run("test input")
        assert result is not None
        assert isinstance(result, str)

    def test_run_with_tools(self, agent):
        """Test run with tools."""
        def test_tool(input: str) -> str:
            return f"Tool result: {input}"

        agent.add_tool("test_tool", test_tool)
        result = agent.run("test with tool")
        assert "Tool result" in result or "test with tool" in result
```

**Test Guidelines:**
- Test both success and failure cases
- Use fixtures for common setup
- Mock LLMs to avoid API calls
- Test edge cases
- Aim for >80% coverage

---

## Code Style

### Formatting

We use **Black** for code formatting:

```bash
# Format code
black agent_patterns tests examples

# Check formatting
black --check agent_patterns tests examples
```

**Configuration**: See `pyproject.toml`

### Linting

We use **Ruff** for linting:

```bash
# Run linter
ruff check agent_patterns tests examples

# Fix auto-fixable issues
ruff check --fix agent_patterns tests examples
```

**Configuration**: See `pyproject.toml`

### Type Checking

We use **mypy** for type checking:

```bash
# Type check
mypy agent_patterns
```

**Guidelines:**
- Add type hints to all functions
- Use `Optional` for nullable values
- Use `Dict`, `List`, `Tuple` from `typing`
- Document complex types

**Example:**

```python
from typing import Dict, List, Optional, Any

def process_data(
    input_data: str,
    config: Dict[str, Any],
    options: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Process input data with configuration.

    Args:
        input_data: The input string to process
        config: Configuration dictionary
        options: Optional list of processing options

    Returns:
        Dictionary containing processed results
    """
    results: Dict[str, Any] = {"input": input_data}
    # ... process ...
    return results
```

### Documentation

**Docstrings**: Use Google style:

```python
def my_function(param1: str, param2: int) -> bool:
    """One-line summary.

    More detailed description if needed.
    Can span multiple lines.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is negative

    Example:
        >>> my_function("test", 5)
        True
    """
    pass
```

**Comments**: Use sparingly, prefer clear code:

```python
# Good: Clear code, no comment needed
user_count = len(active_users)

# Bad: Obvious comment
i = i + 1  # Increment i

# Good: Explains WHY
# Use batch size of 100 to avoid API rate limits
batch_size = 100
```

---

## Submitting Changes

### Pre-Submission Checklist

Before submitting, ensure:

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black --check`)
- [ ] Linting passes (`ruff check`)
- [ ] Type checking passes (`mypy agent_patterns`)
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] Commit messages are clear
- [ ] No sensitive information (API keys, etc.) committed

### Create Pull Request

1. **Push your branch**:
```bash
git push origin feature/your-feature-name
```

2. **Create PR on GitHub**:
   - Go to your fork on GitHub
   - Click "Compare & pull request"
   - Fill in the PR template

3. **PR Title**: Clear and descriptive
```
Add STORM pattern implementation
Fix ReAct infinite loop issue
Update documentation for prompt customization
```

4. **PR Description**: Include:
   - What changed and why
   - Related issue numbers (`Closes #123`)
   - Testing performed
   - Screenshots (if UI changes)

**PR Template:**

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
Describe testing performed.

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Linting passes
- [ ] Documentation updated
- [ ] Commit messages clear

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**: CI runs tests, linting, type checking
2. **Code Review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: Maintainer merges to main

**During Review:**
- Respond to feedback promptly
- Make requested changes
- Push updates to same branch
- Be open to suggestions
- Ask questions if unclear

---

## Types of Contributions

### Bug Fixes

1. **Find or create issue** describing bug
2. **Create branch**: `fix/issue-123-description`
3. **Write test** that reproduces bug
4. **Fix the bug**
5. **Verify test passes**
6. **Submit PR**

### New Features

1. **Discuss in issue** first (for large features)
2. **Create branch**: `feature/feature-name`
3. **Implement feature**
4. **Add comprehensive tests**
5. **Update documentation**
6. **Submit PR**

### New Patterns

Adding a new agent pattern:

1. **Create pattern file**: `agent_patterns/patterns/my_pattern_agent.py`
2. **Implement pattern**:
```python
from agent_patterns.core import BaseAgent

class MyPatternAgent(BaseAgent):
    def build_graph(self):
        # Build state graph
        pass

    def run(self, input_data):
        # Execute pattern
        pass
```

3. **Add prompts**: `agent_patterns/prompts/MyPatternAgent/`
4. **Create tests**: `tests/test_my_pattern_agent.py`
5. **Add example**: `examples/my_pattern_example.py`
6. **Update**:
   - `agent_patterns/patterns/__init__.py` (export)
   - `usr-docs/api/patterns.md` (documentation)
   - `README.md` (mention pattern)

### Documentation

1. **Update existing docs** in `usr-docs/`
2. **Add new guides** for new features
3. **Improve examples**
4. **Fix typos and errors**
5. **Add docstrings** to code

### Tests

1. **Increase coverage** for untested code
2. **Add edge case tests**
3. **Improve test quality**
4. **Add integration tests**

---

## Development Tips

### Run Pre-commit Checks

Before committing, run:

```bash
# Format
black agent_patterns tests examples

# Lint
ruff check agent_patterns tests examples

# Type check
mypy agent_patterns

# Test
pytest
```

### Faster Testing

```bash
# Run only fast tests
pytest -m "not slow"

# Run failed tests first
pytest --failed-first

# Run tests in parallel
pytest -n auto
```

### Debug Tests

```bash
# Run with debugger on failure
pytest --pdb

# Print output
pytest -s

# Verbose
pytest -vv
```

### Keep Fork Updated

```bash
# Fetch upstream
git fetch upstream

# Update main
git checkout main
git merge upstream/main

# Rebase feature branch (if needed)
git checkout feature/your-feature
git rebase main
```

---

## Getting Help

- **Questions**: Open [GitHub Discussion](https://github.com/osok/agent-patterns/discussions)
- **Bugs**: Open [GitHub Issue](https://github.com/osok/agent-patterns/issues)
- **Slack/Discord**: Coming soon
- **Email**: [osok@users.noreply.github.com](mailto:osok@users.noreply.github.com)

---

## Recognition

Contributors are recognized in:
- **README.md**: Contributors section
- **Release notes**: Mentioned in changelog
- **GitHub**: Automatically tracked

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Agent Patterns!**
