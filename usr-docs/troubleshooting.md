# Troubleshooting Guide

Solutions to common problems and error messages when using Agent Patterns.

## Quick Diagnostic Checklist

Before diving into specific issues, verify:

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Agent Patterns installed (`pip show agent-patterns`)
- [ ] API keys set (in `.env` or environment)
- [ ] Dependencies installed (`pip list | grep lang`)
- [ ] Code imports successfully

---

## Installation Issues

### Problem: `pip: command not found`

**Cause**: pip not installed or not in PATH

**Solutions**:

```bash
# Use Python's pip module
python -m pip install agent-patterns

# Or install pip
python -m ensurepip --default-pip

# macOS with brew
brew install python@3.10
```

### Problem: `Permission denied` during installation

**Cause**: Trying to install system-wide without permissions

**Solutions**:

```bash
# Install to user directory
pip install --user agent-patterns

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install agent-patterns
```

### Problem: `No module named 'agent_patterns'`

**Cause**: Package not installed or wrong environment

**Solutions**:

```bash
# Verify installation
pip show agent-patterns

# Reinstall
pip install --force-reinstall agent-patterns

# Check you're in correct virtual environment
which python  # Should point to your venv

# If installed from source, use editable install
pip install -e .
```

### Problem: Dependency conflicts

**Cause**: Incompatible versions of LangChain/LangGraph

**Solutions**:

```bash
# Create fresh virtual environment
python -m venv fresh_venv
source fresh_venv/bin/activate
pip install agent-patterns

# Or specify compatible versions
pip install langgraph==0.2.0 langchain==0.3.0 agent-patterns
```

---

## Configuration Issues

### Problem: `No API key found`

**Error**: `openai.error.AuthenticationError: No API key provided`

**Cause**: API key not set or not loaded

**Solutions**:

1. **Create .env file**:
```bash
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your-key-here
```

2. **Load environment variables**:
```python
from dotenv import load_dotenv
load_dotenv()  # Add this before creating agent
```

3. **Set manually**:
```python
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"
```

4. **Verify key is loaded**:
```python
import os
print(os.getenv("OPENAI_API_KEY"))  # Should not be None
```

### Problem: `Invalid API key`

**Error**: `openai.error.AuthenticationError: Incorrect API key`

**Cause**: Wrong API key or key for wrong provider

**Solutions**:

1. **Verify key**:
   - OpenAI keys start with `sk-`
   - Anthropic keys start with `sk-ant-`

2. **Check provider matches key**:
```python
# If using OpenAI key, use openai provider
llm_configs = {
    "thinking": {
        "provider": "openai",  # Match your key
        "model_name": "gpt-4-turbo"
    }
}
```

3. **Test key directly**:
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo")
llm.invoke("test")  # Should work if key is valid
```

### Problem: `No configuration found for role 'X'`

**Error**: `ValueError: No configuration found for role 'thinking'`

**Cause**: Missing required LLM role in configuration

**Solutions**:

Check pattern requirements:

```python
# ReAct requires "thinking"
agent = ReActAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"}
    }
)

# Reflection requires "documentation" and "reflection"
agent = ReflectionAgent(
    llm_configs={
        "documentation": {...},
        "reflection": {...}
    }
)
```

See [Pattern API Reference](api/patterns.md) for each pattern's required roles.

### Problem: `Unsupported provider 'X'`

**Error**: `ValueError: Unsupported provider 'claude'`

**Cause**: Provider name incorrect

**Solutions**:

Use correct provider names:

```python
# Correct
"provider": "openai"      # For GPT models
"provider": "anthropic"   # For Claude models

# Incorrect
"provider": "claude"      # Wrong! Use "anthropic"
"provider": "gpt"         # Wrong! Use "openai"
```

---

## Runtime Issues

### Problem: Agent gives nonsensical responses

**Symptoms**: Output doesn't match input, hallucinations, incorrect answers

**Causes & Solutions**:

1. **Temperature too high**:
```python
# Lower temperature for more deterministic output
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.3  # Lower = more focused
    }
}
```

2. **Wrong model**:
```python
# Use more capable model
"model_name": "gpt-4-turbo"  # Instead of gpt-3.5-turbo
```

3. **Poor prompts**:
```python
# Add domain context
agent = ReActAgent(
    llm_configs={...},
    custom_instructions="""
    You are an expert in {domain}.
    Always provide accurate, well-reasoned answers.
    """
)
```

4. **Insufficient iterations**:
```python
# Increase iterations for complex tasks
agent = ReActAgent(max_iterations=10)  # Default is 5
```

### Problem: Agent loops indefinitely

**Symptoms**: Never reaches final answer, hits max iterations every time

**Causes & Solutions**:

1. **Check termination logic**:
```python
# Ensure agent can detect completion
# For ReAct, tool should return "FINAL_ANSWER" when done

def my_tool(input: str) -> str:
    if condition_met:
        return "FINAL_ANSWER: Result here"
    return "Continue with more data"
```

2. **Lower max iterations**:
```python
agent = ReActAgent(max_iterations=3)  # Force early termination
```

3. **Improve tool responses**:
```python
# Tools should return clear, useful information
def search_tool(query: str) -> str:
    results = search(query)
    if not results:
        return "No results found. Try different query."
    return results
```

### Problem: Tools not being called

**Symptoms**: Agent doesn't use available tools, tries to answer without them

**Causes & Solutions**:

1. **Tools not registered**:
```python
# Make sure tools are in the dict
agent = ReActAgent(
    llm_configs={...},
    tools={"search": search_func}  # Must be here!
)
```

2. **Missing tool docstrings**:
```python
# Bad - no docstring
def search(query: str) -> str:
    return results

# Good - clear docstring
def search(query: str) -> str:
    """Search the web for information about the query."""
    return results
```

3. **Prompt doesn't mention tools**:
```python
# Check prompts mention available tools
# Custom prompt should reference tools:
prompt_overrides = {
    "ThoughtStep": {
        "user": "Available tools: {available_tools}\nUse tools when needed."
    }
}
```

### Problem: `KeyError: 'output'` or similar

**Cause**: State key doesn't exist

**Solutions**:

1. **Check state initialization**:
```python
def run(self, input_data):
    initial_state = {
        "input": input_data,
        "output": None,  # Initialize all keys!
        "intermediate": []
    }
    final_state = self.graph.invoke(initial_state)
```

2. **Check node returns**:
```python
def _my_node(self, state: Dict) -> Dict:
    state["new_key"] = "value"
    return state  # Must return state!
```

### Problem: `Graph has not been built`

**Error**: `ValueError: Graph has not been built`

**Cause**: `build_graph()` not called or failed

**Solutions**:

```python
# Ensure build_graph() is called
class MyAgent(BaseAgent):
    def __init__(self, ...):
        super().__init__(...)  # This calls build_graph()

# Check for errors in build_graph()
def build_graph(self):
    try:
        workflow = StateGraph(dict)
        # ... build graph ...
        self.graph = workflow.compile()
    except Exception as e:
        print(f"Graph build failed: {e}")
        raise
```

---

## Performance Issues

### Problem: Slow execution

**Symptoms**: Takes too long to complete

**Causes & Solutions**:

1. **Too many iterations**:
```python
# Reduce iterations
agent = ReActAgent(max_iterations=3)
```

2. **Using slow models**:
```python
# Use faster models for simple roles
llm_configs = {
    "thinking": {"model_name": "gpt-4-turbo"},
    "documentation": {"model_name": "gpt-3.5-turbo"}  # Faster
}
```

3. **Large max_tokens**:
```python
# Reduce max tokens
llm_configs = {
    "thinking": {
        "model_name": "gpt-4-turbo",
        "max_tokens": 500  # Instead of 2000
    }
}
```

4. **Enable caching**:
```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())
```

### Problem: High API costs

**Symptoms**: Unexpectedly expensive

**Solutions**:

1. **Use cheaper models**:
```python
# GPT-3.5 is ~10x cheaper than GPT-4
"model_name": "gpt-3.5-turbo"
```

2. **Reduce iterations/cycles**:
```python
agent = ReActAgent(max_iterations=3)  # Instead of 10
agent = ReflectionAgent(max_reflection_cycles=1)  # Instead of 3
```

3. **Use REWOO instead of ReAct**:
```python
# REWOO makes fewer LLM calls
agent = REWOOAgent(...)  # More efficient than ReActAgent
```

4. **Cache common queries**:
```python
# Cache results in database/Redis
cached_result = cache.get(query)
if cached_result:
    return cached_result

result = agent.run(query)
cache.set(query, result)
```

### Problem: Memory usage high

**Causes & Solutions**:

1. **Large state history**:
```python
# Limit history size
def _my_node(self, state):
    # Keep only last N steps
    if len(state["history"]) > 10:
        state["history"] = state["history"][-10:]
    return state
```

2. **LLM cache growing**:
```python
# Clear cache periodically
agent._llm_cache.clear()
```

---

## Testing & Development Issues

### Problem: Tests failing

**Solutions**:

1. **Install test dependencies**:
```bash
pip install -e ".[dev]"
```

2. **Run specific test**:
```bash
pytest tests/test_base_agent.py -v
```

3. **Mock LLMs in tests**:
```python
from unittest.mock import Mock

def test_agent():
    mock_llm = Mock()
    mock_llm.invoke.return_value.content = "Test response"

    agent = ReActAgent(llm_configs={...})
    agent._llm_cache["thinking"] = mock_llm

    result = agent.run("test")
    assert "Test response" in result
```

### Problem: Type checking errors with mypy

**Solutions**:

```bash
# Check mypy version
mypy --version

# Update mypy
pip install --upgrade mypy

# Run with less strict settings
mypy --ignore-missing-imports agent_patterns/
```

### Problem: Import errors in development

**Cause**: Package not installed in editable mode

**Solutions**:

```bash
# Install in editable mode
pip install -e .

# Verify
python -c "import agent_patterns; print(agent_patterns.__file__)"
```

---

## Debugging Techniques

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agent_patterns")
logger.setLevel(logging.DEBUG)
```

### Inspect State

```python
class DebugAgent(ReActAgent):
    def _generate_thought_and_action(self, state):
        print(f"State before thought: {state}")
        state = super()._generate_thought_and_action(state)
        print(f"State after thought: {state}")
        return state
```

### Test Individual Nodes

```python
# Test a single node in isolation
agent = ReActAgent(...)
test_state = {"input": "test", ...}

result_state = agent._generate_thought_and_action(test_state)
print(result_state)
```

### Use Breakpoints

```python
def _my_node(self, state):
    import pdb; pdb.set_trace()  # Debugger breakpoint
    # Step through code
    return state
```

### Check LLM Responses

```python
def _my_node(self, state):
    llm = self._get_llm("thinking")
    messages = [...]
    response = llm.invoke(messages)

    print(f"LLM Response: {response.content}")  # Debug output

    return state
```

---

## Error Messages Reference

### Common Errors and Meanings

| Error | Meaning | Solution |
|-------|---------|----------|
| `AuthenticationError` | Invalid/missing API key | Check `.env` file |
| `RateLimitError` | Too many API requests | Add delays, use rate limiting |
| `InvalidRequestError` | Bad request to API | Check model name, parameters |
| `ValueError: Graph not built` | build_graph() failed | Check build_graph() implementation |
| `KeyError` | Missing state key | Initialize all state keys |
| `TypeError: X is not callable` | Tool not a function | Ensure tools are functions |
| `ImportError` | Missing dependency | Run `pip install agent-patterns` |

---

## Still Having Issues?

### Before Asking for Help

1. **Check FAQ**: [FAQ](faq.md)
2. **Search Issues**: [GitHub Issues](https://github.com/osok/agent-patterns/issues)
3. **Read docs**: Review relevant documentation pages
4. **Try minimal example**: Reproduce with simplest possible code

### When Creating an Issue

Include:

1. **Environment**:
   - Python version (`python --version`)
   - Agent Patterns version (`pip show agent-patterns`)
   - OS and version

2. **Minimal reproducible example**:
```python
# Shortest code that demonstrates the issue
from agent_patterns.patterns import ReActAgent

agent = ReActAgent(llm_configs={...})
result = agent.run("test")  # Fails here
```

3. **Full error message**:
```
Traceback (most recent call last):
  File ...
  ...full traceback...
```

4. **What you expected** vs **what happened**

### Get Help

- **GitHub Issues**: [Report bugs](https://github.com/osok/agent-patterns/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/osok/agent-patterns/discussions)
- **Documentation**: [Read the docs](index.md)

---

## Prevention Tips

1. **Use virtual environments**: Isolate dependencies
2. **Pin versions**: Specify exact versions in requirements.txt
3. **Test changes**: Run tests before deploying
4. **Monitor logs**: Watch for warnings and errors
5. **Start simple**: Begin with basic examples, add complexity gradually
6. **Read error messages**: They often explain the problem clearly
7. **Check documentation**: API reference has details on parameters
8. **Use type hints**: Catch errors during development
