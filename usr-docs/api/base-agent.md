# BaseAgent API Reference

Complete reference for the `BaseAgent` abstract base class that all patterns inherit from.

## Overview

`BaseAgent` provides the foundation for all agent patterns in the library. It handles:

- LLM initialization and caching
- Prompt template loading and customization
- State graph compilation
- Lifecycle hooks for monitoring

## Class Definition

```python
from agent_patterns.core import BaseAgent

class BaseAgent(abc.ABC):
    """Abstract base class for all agent patterns."""
```

**Location**: `agent_patterns/core/base_agent.py`

## Constructor

### `__init__(llm_configs, prompt_dir='prompts', custom_instructions=None, prompt_overrides=None)`

Initialize the base agent with configuration.

**Parameters:**

- **llm_configs** (`Dict[str, Dict[str, Any]]`) - Configuration for LLM roles
  ```python
  {
      "thinking": {
          "provider": "openai",      # "openai" or "anthropic"
          "model_name": "gpt-4-turbo",  # Model identifier
          "temperature": 0.7,        # Optional: 0.0-1.0
          "max_tokens": 2000,        # Optional: max response length
      }
  }
  ```

- **prompt_dir** (`str`, default=`"prompts"`) - Directory containing prompt templates
  - Relative or absolute path
  - Pattern looks for `{prompt_dir}/{ClassName}/{StepName}/system.md` and `user.md`

- **custom_instructions** (`Optional[str]`, default=`None`) - Custom instructions appended to all system prompts
  - Useful for domain-specific context
  - Applied after base prompts loaded
  - Example: `"You are an expert in medical diagnosis..."`

- **prompt_overrides** (`Optional[Dict[str, Dict[str, str]]]`, default=`None`) - Programmatic prompt overrides
  ```python
  {
      "StepName": {
          "system": "Custom system prompt",
          "user": "Custom user prompt template"
      }
  }
  ```
  - Highest priority in prompt resolution
  - Completely replaces file-based prompts

**Example:**

```python
from agent_patterns.patterns import ReActAgent

agent = ReActAgent(
    llm_configs={
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4-turbo",
            "temperature": 0.7,
        }
    },
    prompt_dir="custom_prompts",
    custom_instructions="You are a helpful medical assistant.",
    prompt_overrides={
        "ThoughtStep": {
            "system": "Think carefully about medical implications."
        }
    }
)
```

## Abstract Methods

Subclasses must implement these methods.

### `build_graph() -> None`

Construct the LangGraph state graph for this pattern.

**Description:**
- Called automatically during `__init__()`
- Should create nodes, edges, and compile the graph
- Must set `self.graph` to the compiled graph

**Example Implementation:**

```python
def build_graph(self) -> None:
    from langgraph.graph import StateGraph, END

    workflow = StateGraph(dict)

    # Add nodes
    workflow.add_node("step1", self._step1)
    workflow.add_node("step2", self._step2)

    # Define flow
    workflow.set_entry_point("step1")
    workflow.add_edge("step1", "step2")
    workflow.add_edge("step2", END)

    # Compile and store
    self.graph = workflow.compile()
```

### `run(input_data: Any) -> Any`

Execute the agent pattern on the given input.

**Parameters:**
- **input_data** (`Any`) - The input query, task, or problem

**Returns:**
- `Any` - The final result from pattern execution

**Description:**
- Main entry point for using the agent
- Should invoke `self.graph.invoke(initial_state)`
- Should call lifecycle hooks (`on_start`, `on_finish`, `on_error`)
- Should extract and return the final result

**Example Implementation:**

```python
def run(self, input_data: str) -> str:
    if self.graph is None:
        raise ValueError("Graph not built")

    initial_state = {
        "input": input_data,
        "output": None
    }

    self.on_start(input_data)

    try:
        final_state = self.graph.invoke(initial_state)
        result = final_state["output"]
        self.on_finish(result)
        return result
    except Exception as e:
        self.on_error(e)
        raise
```

## Public Methods

### `stream(input_data: Any) -> Iterator[Any]`

Optional streaming interface for incremental results.

**Parameters:**
- **input_data** (`Any`) - The input query or task

**Yields:**
- `Any` - Incremental results or state updates

**Default Implementation:**
```python
def stream(self, input_data: Any) -> Iterator[Any]:
    yield self.run(input_data)
```

**Note:** Most patterns use the default implementation. Override for true streaming.

## Protected Methods

These methods are available to subclasses.

### `_get_llm(role: str) -> BaseChatModel`

Get or create an LLM instance for the specified role.

**Parameters:**
- **role** (`str`) - Role name (e.g., "thinking", "reflection")

**Returns:**
- `BaseChatModel` - Initialized and cached LLM instance

**Raises:**
- `ValueError` - If role not configured or provider unsupported
- `KeyError` - If required config keys missing

**Supported Providers:**
- `openai` - OpenAI models (GPT-3.5, GPT-4, etc.)
- `anthropic` - Anthropic models (Claude)

**Example:**

```python
def _my_step(self, state: Dict) -> Dict:
    # Get LLM for thinking role
    llm = self._get_llm("thinking")

    # Use it
    messages = [
        SystemMessage(content="You are helpful."),
        HumanMessage(content="Hello!")
    ]
    response = llm.invoke(messages)

    return state
```

**Caching:**
- LLMs are initialized once per role
- Subsequent calls return cached instance
- Cache stored in `self._llm_cache`

### `_load_prompt(step_name: str) -> Dict[str, str]`

Load prompt templates for a specific step.

**Parameters:**
- **step_name** (`str`) - Name of the step (e.g., "ThoughtStep", "Generate")

**Returns:**
- `Dict[str, str]` - Dictionary with "system" and "user" keys

**Prompt Resolution Order:**
1. Check `prompt_overrides` (highest priority)
2. Load from file system (`{prompt_dir}/{ClassName}/{StepName}/`)
3. Append `custom_instructions` to system prompt

**File Structure:**
```
prompts/
└── ReActAgent/
    └── ThoughtStep/
        ├── system.md
        └── user.md
```

**Example:**

```python
def _generate_output(self, state: Dict) -> Dict:
    # Load prompts for this step
    prompts = self._load_prompt("Generate")

    system_prompt = prompts.get("system", "Default system prompt")
    user_template = prompts.get("user", "Task: {task}")

    # Format user prompt
    user_prompt = user_template.format(task=state["input"])

    # Use with LLM
    llm = self._get_llm("documentation")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    response = llm.invoke(messages)

    state["output"] = response.content
    return state
```

**Custom Instructions:**
- If `self.custom_instructions` is set, automatically appended to system prompts
- Format: `{system_prompt}\n\n## Custom Instructions\n\n{custom_instructions}`

## Lifecycle Hooks

Override these methods for logging, monitoring, or custom behavior.

### `on_start(input_data: Any) -> None`

Called before agent execution starts.

**Parameters:**
- **input_data** (`Any`) - The input being processed

**Default:** Does nothing (pass)

**Example:**

```python
class MonitoredAgent(ReActAgent):
    def on_start(self, input_data):
        print(f"Starting: {input_data}")
        self.start_time = time.time()
```

### `on_finish(result: Any) -> None`

Called after agent execution completes successfully.

**Parameters:**
- **result** (`Any`) - The final result

**Default:** Does nothing (pass)

**Example:**

```python
def on_finish(self, result):
    duration = time.time() - self.start_time
    print(f"Completed in {duration:.2f}s")
    logger.info(f"Result: {result}")
```

### `on_error(error: Exception) -> None`

Called when an error occurs during execution.

**Parameters:**
- **error** (`Exception`) - The exception raised

**Default:** Does nothing (pass)

**Example:**

```python
def on_error(self, error):
    print(f"Error: {error}")
    logger.error(f"Agent failed", exc_info=error)
    # Send to monitoring system
    metrics.record_error(type(error).__name__)
```

## Attributes

### Public Attributes

- **llm_configs** (`Dict[str, Dict[str, Any]]`) - LLM configuration dictionary
- **prompt_dir** (`str`) - Path to prompts directory
- **custom_instructions** (`Optional[str]`) - Custom instructions string
- **prompt_overrides** (`Dict[str, Dict[str, str]]`) - Prompt override dictionary
- **graph** (`Optional[CompiledStateGraph]`) - Compiled LangGraph state graph

### Private Attributes

- **_llm_cache** (`Dict[str, BaseChatModel]`) - Cache of initialized LLM instances

## Complete Example

```python
from agent_patterns.core import BaseAgent
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Any, Dict

class SimpleQAAgent(BaseAgent):
    """Simple Q&A agent that generates and verifies answers."""

    def __init__(self, llm_configs: Dict[str, Dict[str, Any]], **kwargs):
        super().__init__(llm_configs=llm_configs, **kwargs)

    def build_graph(self) -> None:
        """Build a simple generate -> verify -> finalize graph."""
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("generate", self._generate_answer)
        workflow.add_node("verify", self._verify_answer)
        workflow.add_node("finalize", self._finalize)

        # Set flow
        workflow.set_entry_point("generate")
        workflow.add_edge("generate", "verify")
        workflow.add_conditional_edges(
            "verify",
            lambda s: "regenerate" if not s["verified"] else "done",
            {
                "regenerate": "generate",
                "done": "finalize"
            }
        )
        workflow.add_edge("finalize", END)

        self.graph = workflow.compile()

    def run(self, input_data: str) -> str:
        """Execute the Q&A workflow."""
        if self.graph is None:
            raise ValueError("Graph not built")

        initial_state = {
            "question": input_data,
            "answer": None,
            "verified": False,
            "attempts": 0,
            "max_attempts": 3
        }

        self.on_start(input_data)

        try:
            final_state = self.graph.invoke(initial_state)
            result = final_state["answer"]
            self.on_finish(result)
            return result
        except Exception as e:
            self.on_error(e)
            raise

    def _generate_answer(self, state: Dict) -> Dict:
        """Generate answer to question."""
        # Load prompts
        prompts = self._load_prompt("Generate")

        # Format prompts
        system_prompt = prompts.get("system", "You answer questions accurately.")
        user_prompt = prompts.get("user", "Q: {question}\nA:").format(
            question=state["question"]
        )

        # Get LLM and generate
        llm = self._get_llm("thinking")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)

        # Update state
        state["answer"] = response.content
        state["attempts"] += 1

        return state

    def _verify_answer(self, state: Dict) -> Dict:
        """Verify answer quality."""
        # Load prompts
        prompts = self._load_prompt("Verify")

        # Format
        system_prompt = prompts.get("system", "Verify answer accuracy.")
        user_prompt = prompts.get("user", "Q: {question}\nA: {answer}\nIs this accurate?").format(
            question=state["question"],
            answer=state["answer"]
        )

        # Verify
        llm = self._get_llm("reflection")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)

        # Check result
        verified = "yes" in response.content.lower()

        # Update state
        state["verified"] = verified or state["attempts"] >= state["max_attempts"]

        return state

    def _finalize(self, state: Dict) -> Dict:
        """Finalize the answer."""
        # Could add formatting, disclaimers, etc.
        return state

    # Lifecycle hooks
    def on_start(self, input_data):
        print(f"[START] Processing question: {input_data}")

    def on_finish(self, result):
        print(f"[FINISH] Generated answer")

    def on_error(self, error):
        print(f"[ERROR] {error}")


# Usage
agent = SimpleQAAgent(
    llm_configs={
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4-turbo"
        },
        "reflection": {
            "provider": "openai",
            "model_name": "gpt-4-turbo"
        }
    },
    custom_instructions="Provide concise, factual answers."
)

result = agent.run("What is the capital of France?")
print(result)
```

## Best Practices

### 1. Always Call Parent `__init__()`

```python
def __init__(self, llm_configs, **kwargs):
    # Custom initialization
    self.custom_attr = "value"

    # ALWAYS call parent
    super().__init__(llm_configs=llm_configs, **kwargs)
```

### 2. Handle Errors in `run()`

```python
def run(self, input_data):
    self.on_start(input_data)

    try:
        result = self.graph.invoke(...)
        self.on_finish(result)
        return result
    except Exception as e:
        self.on_error(e)
        raise  # Re-raise after logging
```

### 3. Use Descriptive Step Names

```python
# Good
prompts = self._load_prompt("GenerateInitialDraft")
prompts = self._load_prompt("ReflectOnQuality")

# Less clear
prompts = self._load_prompt("Step1")
prompts = self._load_prompt("Step2")
```

### 4. Cache LLMs

```python
# Good - cached automatically
llm = self._get_llm("thinking")

# Bad - don't create directly
llm = ChatOpenAI(model="gpt-4")  # No caching
```

### 5. Validate State

```python
def _my_step(self, state: Dict) -> Dict:
    # Validate required keys
    if "input" not in state:
        raise ValueError("State missing 'input' key")

    # Process...

    return state
```

## See Also

- [Pattern API Reference](patterns.md) - All implemented patterns
- [Architecture Guide](../concepts/architecture.md) - How patterns work internally
- [Type Reference](types.md) - Type definitions and hints
- [Examples](../examples/index.md) - Real-world usage examples
