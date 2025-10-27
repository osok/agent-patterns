# Frequently Asked Questions (FAQ)

Common questions and answers about Agent Patterns.

## General Questions

### What is Agent Patterns?

Agent Patterns is a Python library providing reusable workflow patterns for AI agents. It implements 9 research-backed patterns using LangGraph and LangChain, making it easy to build reliable, structured agent applications.

### Why use patterns instead of custom code?

Patterns provide:
- **Reliability**: Consistent, predictable behavior
- **Reusability**: Apply same pattern across different domains
- **Best Practices**: Research-backed approaches
- **Debuggability**: Clear, inspectable workflow stages
- **Maintainability**: Modular, well-tested code

See [What Are Patterns?](concepts/what-are-patterns.md) for details.

### Which pattern should I use?

It depends on your task:
- **Tool-based Q&A**: ReAct
- **High-quality content**: Reflection
- **Multi-step tasks**: Plan & Solve
- **Comprehensive research**: STORM
- **Novel problems**: Self-Discovery

See [Choosing a Pattern](patterns/choosing-a-pattern.md) for detailed guidance.

### Is Agent Patterns production-ready?

Yes. Version 0.2.0 is stable and tested. It uses:
- Synchronous design (no async complexity)
- Comprehensive test coverage (>80%)
- Well-documented API
- Battle-tested patterns from research papers

### What's the license?

MIT License. Free for commercial and personal use.

---

## Installation & Setup

### How do I install Agent Patterns?

```bash
pip install agent-patterns
```

See [Installation Guide](installation.md) for details.

### What Python version is required?

Python 3.10 or higher. We support Python 3.10, 3.11, and 3.12.

### Do I need API keys?

Yes, you need at least one:
- OpenAI API key for GPT models
- Anthropic API key for Claude models

Set them in `.env` file or environment variables.

### Can I use local/open-source models?

Currently, Agent Patterns supports OpenAI and Anthropic via LangChain. For other models, you'll need to:
1. Check if LangChain supports the model
2. Extend `BaseAgent._get_llm()` to handle the provider
3. Configure accordingly

### How do I set up multiple API keys?

In `.env`:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Use different providers in `llm_configs`:

```python
llm_configs = {
    "thinking": {"provider": "anthropic", "model_name": "claude-3-5-sonnet-20241022"},
    "documentation": {"provider": "openai", "model_name": "gpt-3.5-turbo"}
}
```

---

## Usage Questions

### How do I create a simple agent?

```python
from agent_patterns.patterns import ReActAgent
from dotenv import load_dotenv

load_dotenv()

agent = ReActAgent(
    llm_configs={
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4-turbo"
        }
    }
)

result = agent.run("Your question here")
```

See [Quick Start](quickstart.md) for more.

### How do I add tools to an agent?

```python
def my_tool(input: str) -> str:
    """Tool description."""
    return f"Result for {input}"

agent = ReActAgent(
    llm_configs={...},
    tools={"my_tool": my_tool}
)
```

Tools are simple Python functions taking string input and returning string output.

### Can I use async functions?

No. Agent Patterns v0.2.0+ is **synchronous only**. This was a deliberate design decision for simplicity and debuggability.

If you have async tools, wrap them:

```python
import asyncio

def sync_wrapper(input: str) -> str:
    async def async_tool(input: str) -> str:
        # Your async code
        pass

    return asyncio.run(async_tool(input))

agent = ReActAgent(tools={"tool": sync_wrapper})
```

### How do I handle errors?

```python
try:
    result = agent.run(input_data)
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Runtime error: {e}")
```

Or use lifecycle hooks:

```python
class MyAgent(ReActAgent):
    def on_error(self, error):
        logger.error(f"Agent failed: {error}")
        # Send alert, etc.
```

### How do I log agent activity?

Override lifecycle hooks:

```python
class LoggedAgent(ReActAgent):
    def on_start(self, input_data):
        print(f"Starting: {input_data}")

    def on_finish(self, result):
        print(f"Finished: {result}")
```

Or integrate with logging framework:

```python
import logging

class LoggedAgent(ReActAgent):
    def on_start(self, input_data):
        logging.info(f"Agent started", extra={"input": input_data})
```

---

## Customization Questions

### How do I customize prompts?

Three ways:

1. **File-based**: Put prompts in `prompts/` directory
2. **Custom instructions**: Add domain context
3. **Prompt overrides**: Programmatically replace prompts

```python
agent = ReActAgent(
    llm_configs={...},
    prompt_dir="my_prompts",
    custom_instructions="You are a medical expert.",
    prompt_overrides={
        "ThoughtStep": {
            "system": "Custom system prompt"
        }
    }
)
```

See [README Customization](../README.md#customizing-prompts) for details.

### What's the difference between custom_instructions and prompt_overrides?

- **custom_instructions**: Appended to ALL system prompts (adds context)
- **prompt_overrides**: Completely replaces specific prompts (fine-grained control)

Use custom_instructions for domain expertise, prompt_overrides for experiments.

### Can I use different models for different roles?

Yes! Mix and match:

```python
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model_name": "gpt-4-turbo"
    },
    "reflection": {
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-20241022"
    },
    "documentation": {
        "provider": "openai",
        "model_name": "gpt-3.5-turbo"  # Cheaper for simple tasks
    }
}
```

### How do I adjust temperature and other parameters?

In `llm_configs`:

```python
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.3,      # Lower = more deterministic
        "max_tokens": 1500,      # Response length limit
    }
}
```

---

## Pattern-Specific Questions

### ReAct: How many iterations should I use?

Start with 5. Adjust based on task complexity:
- Simple Q&A: 3-5
- Complex research: 7-10
- Very complex: 10-15

```python
agent = ReActAgent(max_iterations=7)
```

### Reflection: How many reflection cycles?

Usually 1-2 is sufficient:
- 1 cycle: Good for most content
- 2 cycles: High-quality requirements
- 3+ cycles: Diminishing returns, higher cost

```python
agent = ReflectionAgent(max_reflection_cycles=2)
```

### Plan & Solve: Can I provide an existing plan?

Not directly, but you can guide it via custom instructions:

```python
agent = PlanAndSolveAgent(
    llm_configs={...},
    custom_instructions="""
    Use this structure:
    1. Research phase
    2. Analysis phase
    3. Synthesis phase
    """
)
```

### STORM: How do I add custom perspectives?

```python
perspectives = [
    {"name": "engineer", "description": "Software engineer implementing solutions"},
    {"name": "manager", "description": "Project manager considering resources"},
    {"name": "user", "description": "End user of the product"}
]

agent = STORMAgent(
    llm_configs={...},
    perspectives=perspectives
)
```

### Self-Discovery: Can I add custom reasoning modules?

Yes:

```python
custom_modules = [
    {
        "name": "cost_benefit",
        "description": "Analyze costs and benefits",
        "template": "For '{task}', identify costs and benefits"
    },
    {
        "name": "risk_analysis",
        "description": "Assess risks and mitigation strategies",
        "template": "Identify risks for '{task}' and how to mitigate them"
    }
]

agent = SelfDiscoveryAgent(
    llm_configs={...},
    reasoning_modules=custom_modules
)
```

---

## Technical Questions

### How does state management work?

Each pattern uses a state dictionary that flows through the graph:

```python
state = {
    "input": "user query",
    "intermediate_data": [...],
    "output": "result"
}

# Nodes receive and return state
def my_node(state: Dict) -> Dict:
    state["new_field"] = "value"
    return state
```

See [Architecture](concepts/architecture.md) for details.

### What is LangGraph?

LangGraph is a library for building stateful, multi-actor applications with LLMs. It manages the state graph execution for Agent Patterns.

Learn more: [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

### Can I inspect intermediate steps?

Yes, access the state during execution. For ReAct:

```python
# After execution, inspect
result_state = agent.graph.invoke(initial_state)
history = result_state["intermediate_steps"]

for thought, action, observation in history:
    print(f"Thought: {thought}")
    print(f"Action: {action}")
    print(f"Result: {observation}")
```

### Can I stream results?

Default `stream()` implementation just yields final result. For true streaming, override in subclass:

```python
class StreamingAgent(ReActAgent):
    def stream(self, input_data):
        state = {"input": input_data, ...}

        for chunk in self.graph.stream(state):
            yield chunk
```

LangGraph supports streaming - see [LangGraph streaming docs](https://langchain-ai.github.io/langgraph/how-tos/stream-values/).

### How do I test my agent?

```python
import pytest
from unittest.mock import Mock

def test_agent():
    # Mock LLM
    mock_llm = Mock()
    mock_llm.invoke.return_value.content = "Test response"

    # Create agent
    agent = ReActAgent(llm_configs={...})
    agent._llm_cache["thinking"] = mock_llm

    # Test
    result = agent.run("test query")
    assert "Test response" in result
```

See test files in `tests/` directory for examples.

---

## Performance & Cost Questions

### How much do API calls cost?

Depends on:
- Model used (GPT-4 > GPT-3.5)
- Number of iterations/cycles
- Token counts

Example ReAct with GPT-4 (5 iterations):
- ~2,000 tokens per iteration
- 10,000 total tokens
- ~$0.30 per query

Use cheaper models for less critical roles:

```python
llm_configs = {
    "thinking": {"model_name": "gpt-4-turbo"},  # Expensive but good
    "documentation": {"model_name": "gpt-3.5-turbo"}  # Cheap for simple tasks
}
```

### How can I reduce costs?

1. **Use cheaper models** for simple roles
2. **Reduce iterations/cycles**
3. **Lower max_tokens**
4. **Cache results** when possible
5. **Use REWOO** instead of ReAct (fewer LLM calls)

### How fast are the patterns?

Depends on:
- Number of LLM calls
- Model speed
- Network latency

Approximate times (GPT-4):
- ReAct (5 iter): 10-15 seconds
- Reflection (2 cycles): 15-20 seconds
- Plan & Solve: 20-30 seconds
- STORM: 60-120 seconds

### Can I cache LLM responses?

Yes, use LangChain caching:

```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())

# Now LLM calls are cached
agent = ReActAgent(...)
```

---

## Troubleshooting Questions

### I get "Module not found" errors

Install dependencies:

```bash
pip install agent-patterns
```

Or if installed from source:

```bash
pip install -e .
```

### I get "API key not found" errors

Set API key in `.env`:

```bash
OPENAI_API_KEY=your-key-here
```

Or environment:

```bash
export OPENAI_API_KEY=your-key-here
```

Load in code:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Agent gives nonsensical responses

Check:
1. **Prompts**: Are they clear and well-structured?
2. **Temperature**: Try lowering (0.3-0.5)
3. **Model**: Try more capable model (GPT-4 instead of GPT-3.5)
4. **Instructions**: Add domain context via custom_instructions

### Agent loops infinitely

Check:
1. **max_iterations**: Set appropriate limit
2. **Termination logic**: Ensure pattern can detect completion
3. **Tool results**: Make sure tools return useful information

### Tools aren't being called

Check:
1. **Tool registration**: Tools in `tools` dict?
2. **Tool docstrings**: Clear description?
3. **Prompts**: Do they mention available tools?
4. **LLM capability**: Some models better at tool use than others

See [Troubleshooting Guide](troubleshooting.md) for more.

---

## Advanced Questions

### Can I create my own pattern?

Yes! Inherit from `BaseAgent`:

```python
from agent_patterns.core import BaseAgent
from langgraph.graph import StateGraph, END

class MyPattern(BaseAgent):
    def build_graph(self):
        workflow = StateGraph(dict)
        # Define your nodes and edges
        workflow.add_node("step1", self._step1)
        workflow.add_edge("step1", END)
        self.graph = workflow.compile()

    def run(self, input_data):
        state = {"input": input_data}
        final_state = self.graph.invoke(state)
        return final_state["output"]

    def _step1(self, state):
        # Your logic
        return state
```

See [BaseAgent API](api/base-agent.md) for details.

### Can I combine multiple patterns?

Yes, but requires custom implementation. You could:

1. **Sequential**: Run one pattern, feed output to another
2. **Parallel**: Run multiple patterns, combine results
3. **Hierarchical**: Use one pattern to coordinate others

Future versions may include multi-agent patterns.

### How do I deploy to production?

1. **Containerize**: Use Docker
2. **API wrapper**: FastAPI or Flask
3. **Monitoring**: Add logging and metrics
4. **Error handling**: Robust try/catch
5. **Rate limiting**: Manage API costs
6. **Caching**: Cache common queries

Example FastAPI wrapper:

```python
from fastapi import FastAPI
from agent_patterns.patterns import ReActAgent

app = FastAPI()
agent = ReActAgent(llm_configs={...})

@app.post("/query")
def query(question: str):
    try:
        result = agent.run(question)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}, 500
```

### Can I use Agent Patterns with LangChain Expression Language (LCEL)?

Agent Patterns uses LangGraph, which is compatible with LCEL. You can integrate LCEL chains as tools:

```python
from langchain_core.runnables import RunnableLambda

def lcel_tool_wrapper(chain):
    """Wrap LCEL chain as tool."""
    def tool(input: str) -> str:
        return chain.invoke({"input": input})
    return tool

my_chain = prompt | llm | output_parser
agent = ReActAgent(
    llm_configs={...},
    tools={"my_chain": lcel_tool_wrapper(my_chain)}
)
```

---

## Migration Questions

### How do I migrate from v0.1.x to v0.2.0?

v0.2.0 is a complete rewrite. Key changes:

1. **Remove async/await**: All code is now synchronous
2. **Update imports**: Patterns moved to `agent_patterns.patterns`
3. **New configuration**: Use new `llm_configs` format
4. **Prompt system**: Update to new 3-layer system

See [Changelog](changelog.md) for details.

### Can I still use v0.1.x?

Yes, but not recommended. v0.1.x had async reliability issues. v0.2.0 is much more stable.

---

## Community & Support

### Where can I get help?

- **Documentation**: Start here
- **GitHub Issues**: [Report bugs](https://github.com/osok/agent-patterns/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/osok/agent-patterns/discussions)

### How can I contribute?

See [Contributing Guide](contributing.md).

### Is there a Discord/Slack?

Not yet. Use GitHub Discussions for community interaction.

### Where can I find more examples?

- [Examples directory](examples/index.md)
- [GitHub examples](https://github.com/osok/agent-patterns/tree/main/examples)

---

## Didn't find your answer?

- Check [Troubleshooting Guide](troubleshooting.md)
- Search [GitHub Issues](https://github.com/osok/agent-patterns/issues)
- Ask in [GitHub Discussions](https://github.com/osok/agent-patterns/discussions)
- Create a [new issue](https://github.com/osok/agent-patterns/issues/new)
