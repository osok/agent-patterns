# Testing Strategies for Agent Patterns

Complete guide to testing agent systems including unit tests, integration tests, mocking strategies, and quality assurance.

## Overview

Testing AI agents presents unique challenges:
- Non-deterministic outputs from LLMs
- Complex multi-step workflows
- External API dependencies
- Cost of running real LLM calls

This guide provides strategies for comprehensive, cost-effective testing.

## Testing Levels

### Unit Tests

Test individual agent components in isolation.

```python
import pytest
from unittest.mock import MagicMock, patch
from agent_patterns.patterns import ReflectionAgent

@pytest.fixture
def llm_configs():
    """Fixture for test LLM configurations."""
    return {
        "documentation": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        },
        "reflection": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.5
        }
    }

def test_agent_initialization(llm_configs):
    """Test agent initializes correctly."""
    agent = ReflectionAgent(
        llm_configs=llm_configs,
        max_reflection_cycles=2
    )

    assert agent.max_reflection_cycles == 2
    assert agent.graph is not None

def test_check_refinement_needed():
    """Test refinement check logic."""
    agent = ReflectionAgent(llm_configs={})

    # Negative indicators should trigger refinement
    state = {
        "reflection": "The response is incomplete and needs improvement"
    }
    result = agent._check_refinement_needed(state)
    assert result["needs_refinement"] is True

    # Positive indicators should not trigger refinement
    state = {
        "reflection": "Excellent and comprehensive response"
    }
    result = agent._check_refinement_needed(state)
    assert result["needs_refinement"] is False
```

### Integration Tests

Test complete agent workflows.

```python
@patch.object(ReflectionAgent, "_get_llm")
@patch.object(ReflectionAgent, "_load_prompt")
def test_full_reflection_workflow(mock_load, mock_get_llm, llm_configs):
    """Test complete reflection workflow."""

    # Mock prompts
    mock_load.return_value = {
        "system": "System prompt",
        "user": "Task: {task}"
    }

    # Mock LLM responses
    mock_llm = MagicMock()
    responses = [
        MagicMock(content="Initial output"),  # Generate
        MagicMock(content="This is incomplete"),  # Reflect
        MagicMock(content="Improved output")  # Refine
    ]
    mock_llm.invoke.side_effect = responses
    mock_get_llm.return_value = mock_llm

    agent = ReflectionAgent(llm_configs=llm_configs)
    result = agent.run("Test task")

    # Verify workflow completed
    assert "output" in result.lower()
```

### End-to-End Tests

Test agents with real LLM calls (expensive, run sparingly).

```python
@pytest.mark.slow
@pytest.mark.integration
def test_agent_e2e_real_llm():
    """End-to-end test with real LLM (slow, costs money)."""

    llm_configs = {
        "documentation": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",  # Use cheaper model for testing
            "temperature": 0.0  # Deterministic
        },
        "reflection": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.0
        }
    }

    agent = ReflectionAgent(llm_configs=llm_configs, max_reflection_cycles=1)

    result = agent.run("Explain what 2+2 equals in one sentence")

    # Verify result
    assert result is not None
    assert len(result) > 0
    assert "4" in result or "four" in result.lower()
```

## Mocking Strategies

### Mocking LLM Responses

```python
from unittest.mock import Mock

def create_mock_llm(responses):
    """Create mock LLM with predefined responses."""
    mock_llm = Mock()

    if isinstance(responses, list):
        # Multiple responses
        mock_responses = [Mock(content=r) for r in responses]
        mock_llm.invoke.side_effect = mock_responses
    else:
        # Single response
        mock_llm.invoke.return_value = Mock(content=responses)

    return mock_llm

# Usage
mock_llm = create_mock_llm(["Response 1", "Response 2", "Response 3"])
```

### Mocking Tools

```python
def test_react_with_mock_tools():
    """Test ReAct agent with mocked tools."""

    # Create mock tools
    mock_search = Mock(return_value="Search results: Python is a programming language")
    mock_calc = Mock(return_value="42")

    tools = {
        "search": mock_search,
        "calculate": mock_calc
    }

    # Mock LLM to call tools
    with patch.object(ReActAgent, "_get_llm") as mock_get_llm:
        mock_llm = create_mock_llm([
            "Thought: I'll search\nAction: search\nAction Input: Python",
            "Thought: Done\nAction: FINISH\nAction Input: Python is a language"
        ])
        mock_get_llm.return_value = mock_llm

        agent = ReActAgent(llm_configs={}, tools=tools, max_iterations=2)
        result = agent.run("What is Python?")

        # Verify tool was called
        mock_search.assert_called()
```

### Mocking Prompts

```python
@patch.object(ReflectionAgent, "_load_prompt")
def test_with_mock_prompts(mock_load_prompt, llm_configs):
    """Test with mocked prompt loading."""

    # Mock prompt loading
    mock_load_prompt.return_value = {
        "system": "Test system prompt",
        "user": "Test user prompt: {task}"
    }

    agent = ReflectionAgent(llm_configs=llm_configs)

    # Verify prompt was loaded
    prompt = agent._load_prompt("Generate")
    assert prompt["system"] == "Test system prompt"
```

## Testing Custom Instructions

```python
def test_custom_instructions_applied():
    """Test that custom instructions are appended to system prompts."""

    instructions = "DOMAIN: Medical\nAUDIENCE: Patients"

    agent = ReflectionAgent(
        llm_configs=llm_configs,
        custom_instructions=instructions
    )

    # Load prompt and verify instructions appended
    prompt = agent._load_prompt("Generate")

    assert "DOMAIN: Medical" in prompt["system"]
    assert "AUDIENCE: Patients" in prompt["system"]

def test_custom_instructions_in_all_steps():
    """Verify custom instructions applied to all workflow steps."""

    instructions = "TEST_INSTRUCTION"

    agent = SelfDiscoveryAgent(
        llm_configs=llm_configs,
        custom_instructions=instructions
    )

    # Check multiple steps
    steps = ["DiscoverModules", "AdaptModules", "ExecuteStep", "SynthesizeOutput"]

    for step in steps:
        prompt = agent._load_prompt(step)
        assert "TEST_INSTRUCTION" in prompt["system"], f"Instructions missing in {step}"
```

## Testing Prompt Overrides

```python
def test_prompt_overrides_replace_prompts():
    """Test that overrides completely replace prompts."""

    overrides = {
        "Generate": {
            "system": "OVERRIDE_SYSTEM",
            "user": "OVERRIDE_USER {task}"
        }
    }

    agent = ReflectionAgent(
        llm_configs=llm_configs,
        prompt_overrides=overrides
    )

    prompt = agent._load_prompt("Generate")

    assert prompt["system"] == "OVERRIDE_SYSTEM"
    assert prompt["user"] == "OVERRIDE_USER {task}"

def test_override_priority_over_custom_instructions():
    """Test that overrides take priority but instructions still append."""

    instructions = "CUSTOM_INSTRUCTION"
    overrides = {
        "Generate": {
            "system": "OVERRIDE_SYSTEM",
            "user": "OVERRIDE_USER"
        }
    }

    agent = ReflectionAgent(
        llm_configs=llm_configs,
        custom_instructions=instructions,
        prompt_overrides=overrides
    )

    prompt = agent._load_prompt("Generate")

    # System should have override + instructions
    assert "OVERRIDE_SYSTEM" in prompt["system"]
    assert "CUSTOM_INSTRUCTION" in prompt["system"]

    # User should be just the override
    assert prompt["user"] == "OVERRIDE_USER"
```

## Testing Configuration

```python
def test_valid_config():
    """Test agent with valid configuration."""
    config = {
        "thinking": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        }
    }

    agent = ReActAgent(llm_configs=config, tools={})
    assert agent is not None

def test_invalid_provider():
    """Test that invalid provider raises error."""
    config = {
        "thinking": {
            "provider": "invalid_provider",
            "model": "some-model"
        }
    }

    with pytest.raises(ValueError, match="Unsupported provider"):
        agent = ReActAgent(llm_configs=config, tools={})
        agent.run("test")  # May error on first LLM access

def test_missing_role_config():
    """Test that missing role configuration raises error."""
    config = {}  # Missing required role

    agent = ReActAgent(llm_configs=config, tools={})

    with pytest.raises(ValueError, match="No configuration found"):
        agent._get_llm("thinking")
```

## Testing Pattern-Specific Behavior

### Testing ReAct

```python
def test_react_max_iterations():
    """Test that ReAct respects max_iterations."""

    with patch.object(ReActAgent, "_get_llm") as mock_get_llm:
        # Mock LLM to never finish
        mock_llm = create_mock_llm("Thought: Continue\nAction: search\nAction Input: test")
        mock_get_llm.return_value = mock_llm

        agent = ReActAgent(
            llm_configs={},
            tools={"search": lambda x: "result"},
            max_iterations=3
        )

        # Should stop after 3 iterations
        # Implementation depends on pattern's max iteration handling
```

### Testing Reflection

```python
def test_reflection_cycles():
    """Test reflection cycle limit."""

    agent = ReflectionAgent(
        llm_configs={},
        max_reflection_cycles=2
    )

    state = {
        "reflection_cycle": 2,
        "max_reflection_cycles": 2
    }

    result = agent._check_cycle_limit(state)

    # Should not continue after reaching limit
    assert result["continue_reflection"] is False
```

### Testing Self-Discovery

```python
def test_self_discovery_module_selection():
    """Test module selection logic."""

    agent = SelfDiscoveryAgent(
        llm_configs={},
        max_selected_modules=3
    )

    # Test module parsing
    selection_text = """
    SELECTED: break_down_problem
    SELECTED: first_principles
    SELECTED: step_by_step
    """

    modules = agent._parse_module_selection(
        selection_text,
        DEFAULT_REASONING_MODULES
    )

    assert len(modules) == 3
    assert modules[0]["name"] == "break_down_problem"
```

## Test Fixtures and Utilities

### Shared Fixtures

```python
# conftest.py
import pytest

@pytest.fixture
def openai_configs():
    """Standard OpenAI configuration."""
    return {
        "thinking": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        }
    }

@pytest.fixture
def anthropic_configs():
    """Standard Anthropic configuration."""
    return {
        "thinking": {
            "provider": "anthropic",
            "model": "claude-3-opus-20240229",
            "temperature": 0.7
        }
    }

@pytest.fixture
def mock_tools():
    """Standard mock tools for testing."""
    return {
        "search": Mock(return_value="search results"),
        "calculate": Mock(return_value="42"),
        "get_weather": Mock(return_value="sunny")
    }
```

### Test Helpers

```python
def assert_valid_llm_output(output: str):
    """Assert that output looks like valid LLM output."""
    assert output is not None
    assert len(output) > 0
    assert not output.startswith("Error")

def create_test_agent(pattern_class, **kwargs):
    """Create agent with test configuration."""
    test_configs = {
        "thinking": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.0  # Deterministic
        }
    }

    return pattern_class(llm_configs=test_configs, **kwargs)
```

## Performance Testing

```python
import time

def test_agent_performance():
    """Test agent performance metrics."""

    agent = create_test_agent(ReflectionAgent)

    start_time = time.time()
    result = agent.run("Quick test task")
    duration = time.time() - start_time

    # Performance assertions
    assert duration < 10.0  # Should complete in < 10 seconds
    assert len(result) > 0

@pytest.mark.benchmark
def test_agent_throughput(benchmark):
    """Benchmark agent throughput."""

    agent = create_test_agent(ReActAgent, tools={"test": lambda x: x})

    result = benchmark(agent.run, "test task")

    assert result is not None
```

## Test Organization

### Test Structure

```
tests/
├── unit/
│   ├── test_base_agent.py
│   ├── test_react_agent.py
│   ├── test_reflection_agent.py
│   └── test_self_discovery_agent.py
├── integration/
│   ├── test_react_workflow.py
│   └── test_reflection_workflow.py
├── e2e/
│   ├── test_real_llm_calls.py
│   └── test_complete_workflows.py
├── fixtures/
│   ├── conftest.py
│   └── mock_data.py
└── helpers/
    ├── assertions.py
    └── factories.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run with coverage
pytest --cov=agent_patterns --cov-report=html

# Run only fast tests (exclude slow e2e)
pytest -m "not slow"

# Run specific test file
pytest tests/unit/test_reflection_agent.py

# Run specific test
pytest tests/unit/test_reflection_agent.py::test_agent_initialization

# Run with verbose output
pytest -v

# Run with output  capture disabled (see prints)
pytest -s
```

## Best Practices

### 1. Mock Expensive Operations

```python
# Always mock LLM calls in unit tests
@patch.object(Agent, "_get_llm")
def test_something(mock_get_llm):
    mock_get_llm.return_value = create_mock_llm("response")
    # Test code
```

### 2. Use Deterministic Settings for Tests

```python
# Use temperature=0 for deterministic tests
test_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.0  # Deterministic
    }
}
```

### 3. Test Error Cases

```python
def test_handles_llm_error():
    """Test agent handles LLM errors gracefully."""

    with patch.object(Agent, "_get_llm") as mock_llm:
        mock_llm.side_effect = APIError("API error")

        agent = create_test_agent(ReActAgent, tools={})

        with pytest.raises(APIError):
            agent.run("test")
```

### 4. Use Fixtures for Common Setup

```python
@pytest.fixture
def configured_agent():
    """Fixture providing pre-configured agent."""
    return ReflectionAgent(
        llm_configs=test_configs,
        max_reflection_cycles=1
    )

def test_with_fixture(configured_agent):
    """Test using fixture."""
    assert configured_agent.max_reflection_cycles == 1
```

### 5. Mark Expensive Tests

```python
@pytest.mark.slow
@pytest.mark.integration
def test_expensive_operation():
    """Expensive test marked appropriately."""
    # Test code
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"

    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=agent_patterns

    - name: Run integration tests
      run: |
        pytest tests/integration/ -v

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Next Steps

- Review [Error Handling](error-handling.md) for testing error scenarios
- See [Deployment](deployment.md) for production testing
- Explore [Best Practices](best-practices.md) for testing strategies

## Reference

### Pytest Markers

```python
# pytest.ini
[pytest]
markers =
    slow: Marks tests as slow (deselect with '-m "not slow"')
    integration: Integration tests
    e2e: End-to-end tests with real LLMs
    benchmark: Performance benchmark tests
```

### Test Coverage Goals

- **Unit Tests**: > 80% coverage
- **Integration Tests**: All major workflows
- **E2E Tests**: Critical user journeys
- **Performance Tests**: Key operations benchmarked
