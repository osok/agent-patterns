# Library Architecture

This document explains the internal architecture of Agent Patterns, how patterns work, and how they integrate with LangGraph and LangChain.

## Overview

Agent Patterns is built on three foundational components:

1. **LangChain**: Provides LLM abstractions and integrations
2. **LangGraph**: Manages state graphs and workflow execution
3. **Agent Patterns**: Implements reusable agent workflow patterns

```
┌─────────────────────────────────────┐
│      Your Application               │
├─────────────────────────────────────┤
│      Agent Patterns Library         │
│   ┌─────────────┬─────────────┐    │
│   │ Pattern     │  Pattern    │    │
│   │ Library     │  Base       │    │
│   │             │  Classes    │    │
│   └─────────────┴─────────────┘    │
├─────────────────────────────────────┤
│         LangGraph                   │
│   (State Graph Management)          │
├─────────────────────────────────────┤
│         LangChain                   │
│   (LLM Integrations)                │
└─────────────────────────────────────┘
```

## Core Architecture

### Component Hierarchy

```
BaseAgent (Abstract)
├── Single-Agent Patterns
│   ├── ReActAgent
│   ├── ReflectionAgent
│   ├── PlanAndSolveAgent
│   ├── ReflexionAgent
│   ├── LLMCompilerAgent
│   ├── REWOOAgent
│   ├── LATSAgent
│   ├── SelfDiscoveryAgent
│   └── STORMAgent
└── MultiAgentBase (Abstract)
    └── (Future multi-agent patterns)
```

### BaseAgent Class

All patterns inherit from `BaseAgent`, which provides:

```python
class BaseAgent(abc.ABC):
    """Abstract base for all patterns."""

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        # LLM configuration and caching
        self.llm_configs = llm_configs
        self._llm_cache: Dict[str, BaseChatModel] = {}

        # Prompt customization
        self.prompt_dir = prompt_dir
        self.custom_instructions = custom_instructions
        self.prompt_overrides = prompt_overrides or {}

        # State graph
        self.graph: Optional[CompiledStateGraph] = None

        # Build the pattern's graph
        self.build_graph()

    @abc.abstractmethod
    def build_graph(self) -> None:
        """Build the LangGraph state graph."""
        pass

    @abc.abstractmethod
    def run(self, input_data: Any) -> Any:
        """Execute the pattern."""
        pass
```

**Key Features:**

1. **LLM Management**: Initializes and caches LLM instances
2. **Prompt Loading**: Loads prompts from files with customization support
3. **Graph Building**: Constructs the pattern's state machine
4. **Lifecycle Hooks**: Provides extension points for logging/monitoring

## State Graph Architecture

Every pattern is a **state graph** managed by LangGraph.

### Graph Components

```
┌─────────────┐
│  Entry Node │  ← Starting point
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Node 1     │  ← Processing step
└──────┬──────┘
       │
       ▼
   ┌───┴───┐
   │ Edge  │  ← Transition logic
   └───┬───┘
       │
       ▼
┌─────────────┐
│  Node 2     │  ← Another step
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  END Node   │  ← Terminal state
└─────────────┘
```

### Example: ReAct Pattern Graph

```python
def build_graph(self):
    workflow = StateGraph(dict)

    # Add nodes (processing steps)
    workflow.add_node("thought_step", self._generate_thought_and_action)
    workflow.add_node("action_step", self._execute_action)
    workflow.add_node("observation_step", self._observation_handler)
    workflow.add_node("final_answer", self._format_final_answer)

    # Set entry point
    workflow.set_entry_point("thought_step")

    # Add edges (transitions)
    workflow.add_edge("thought_step", "action_step")
    workflow.add_edge("action_step", "observation_step")

    # Conditional edge (routing logic)
    workflow.add_conditional_edges(
        "observation_step",
        self._should_continue,  # Decision function
        {
            "continue": "thought_step",  # Loop back
            "finish": "final_answer",    # Exit loop
        },
    )

    workflow.add_edge("final_answer", END)

    # Compile to executable graph
    self.graph = workflow.compile()
```

**Graph Execution:**

```python
# Initialize state
initial_state = {
    "input": "What is 2+2?",
    "thought": "",
    "action": {},
    "observation": None,
    "final_answer": None,
}

# Execute graph
final_state = self.graph.invoke(initial_state)

# Extract result
result = final_state["final_answer"]
```

## State Management

### State Dictionary

Each pattern defines its state schema:

```python
# ReAct Pattern State
state = {
    "input": str,              # User query
    "thought": str,            # Current reasoning
    "action": Dict,            # Tool to call
    "observation": Any,        # Tool result
    "intermediate_steps": List,# History
    "final_answer": str,       # Result
    "iteration_count": int,    # Loop counter
    "max_iterations": int,     # Loop limit
}
```

### State Flow

State flows through the graph:

```
┌──────────────────────────────────────┐
│ Initial State                        │
│ {"input": "query", ...}              │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Node updates state                   │
│ state["thought"] = "I should..."     │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ State passed to next node            │
│ state = next_node(state)             │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Final State                          │
│ {"input": "query", "final_answer":..}│
└──────────────────────────────────────┘
```

**Important**: Each node receives the state, modifies it, and returns the updated state.

## LLM Integration

### LLM Configuration

Patterns use role-based LLM configuration:

```python
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "temperature": 0.7,
        "max_tokens": 2000,
    },
    "reflection": {
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-20241022",
        "temperature": 0.5,
        "max_tokens": 1000,
    },
}
```

### LLM Initialization and Caching

```python
def _get_llm(self, role: str) -> BaseChatModel:
    """Get or create LLM for role."""
    # Check cache
    if role in self._llm_cache:
        return self._llm_cache[role]

    # Get config
    config = self.llm_configs[role]
    provider = config["provider"]
    model_name = config["model_name"]

    # Initialize LLM
    if provider == "openai":
        llm = ChatOpenAI(
            model=model_name,
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000)
        )
    elif provider == "anthropic":
        llm = ChatAnthropic(
            model=model_name,
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000)
        )

    # Cache and return
    self._llm_cache[role] = llm
    return llm
```

**Benefits:**
- LLMs initialized once and reused
- Different models for different roles
- Easy to swap providers/models

### LLM Invocation

```python
# Get LLM for role
llm = self._get_llm("thinking")

# Prepare messages
messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=user_prompt),
]

# Invoke LLM
response = llm.invoke(messages)
result = response.content
```

## Prompt Management

### Three-Layer Prompt System

```
1. Base Prompts (Files)
   ↓
2. Custom Instructions (Appended)
   ↓
3. Prompt Overrides (Replacement)
```

### File-Based Prompts

```
prompts/
└── ReActAgent/
    └── ThoughtStep/
        ├── system.md    # System prompt
        └── user.md      # User prompt template
```

Loading:

```python
def _load_prompt(self, step_name: str) -> Dict[str, str]:
    """Load prompts for a step."""
    # Get class name for directory
    class_name = self.__class__.__name__

    # Build path
    prompt_path = Path(self.prompt_dir) / class_name / step_name

    # Load files
    system_prompt = (prompt_path / "system.md").read_text()
    user_prompt = (prompt_path / "user.md").read_text()

    return {
        "system": system_prompt,
        "user": user_prompt
    }
```

### Custom Instructions

Appended to all system prompts:

```python
agent = ReActAgent(
    llm_configs=configs,
    custom_instructions="""
    You are an expert in the medical domain.
    Always cite sources and include disclaimers.
    """
)

# System prompt becomes:
# <original system prompt>
#
# ## Custom Instructions
#
# <custom instructions>
```

### Prompt Overrides

Complete replacement for specific steps:

```python
overrides = {
    "ThoughtStep": {
        "system": "You are a cautious reasoner...",
        "user": "Task: {input}\n\nWhat should I do?"
    }
}

agent = ReActAgent(
    llm_configs=configs,
    prompt_overrides=overrides
)
```

**Priority**: Overrides > File System > Custom Instructions

## Pattern Execution Flow

### Complete Execution Lifecycle

```
1. Initialization
   ├─ Load LLM configs
   ├─ Load/override prompts
   └─ Build state graph

2. Invocation (run method)
   ├─ Create initial state
   ├─ Call on_start() hook
   └─ Invoke graph

3. Graph Execution
   ├─ Enter first node
   ├─ Process state
   ├─ Invoke LLM if needed
   ├─ Update state
   ├─ Transition to next node
   ├─ Repeat until END
   └─ Return final state

4. Completion
   ├─ Extract result from state
   ├─ Call on_finish() hook
   └─ Return result
```

### Example: ReAct Execution

```python
# 1. User creates agent
agent = ReActAgent(
    llm_configs={"thinking": {...}},
    tools={"search": search_fn},
    max_iterations=5
)
# → build_graph() called automatically

# 2. User invokes agent
result = agent.run("What is the weather in Paris?")

# 3. Internal execution:
initial_state = {
    "input": "What is the weather in Paris?",
    "thought": "",
    "action": {},
    "observation": None,
    "intermediate_steps": [],
    "final_answer": None,
    "iteration_count": 0,
    "max_iterations": 5,
}

# Graph executes:
# thought_step → action_step → observation_step → decision
#                                    ↑                  ↓
#                                    └──────────────────┘
#                                      (loop if continue)

# 4. Result extracted
result = final_state["final_answer"]
# → "The weather in Paris is..."
```

## Tool Integration

### Tool Definition

Tools are simple Python functions:

```python
def search_tool(query: str) -> str:
    """Search the web for information."""
    # Implementation
    results = api.search(query)
    return results
```

### Tool Registration

```python
agent = ReActAgent(
    llm_configs=configs,
    tools={
        "search": search_tool,
        "calculator": calc_tool,
        "database": db_tool,
    }
)
```

### Tool Execution

Within a pattern node:

```python
def _execute_action(self, state: Dict) -> Dict:
    """Execute tool specified in action."""
    action = state["action"]
    tool_name = action["tool_name"]
    tool_input = action["tool_input"]

    # Get tool function
    if tool_name in self.tools:
        try:
            # Execute tool
            observation = self.tools[tool_name](tool_input)
        except Exception as e:
            observation = f"Error: {str(e)}"
    else:
        observation = f"Tool {tool_name} not found"

    # Update state
    state["observation"] = observation
    return state
```

## Lifecycle Hooks

Patterns provide hooks for monitoring and logging:

```python
class BaseAgent:
    def on_start(self, input_data: Any) -> None:
        """Called before execution starts."""
        pass

    def on_finish(self, result: Any) -> None:
        """Called after execution completes."""
        pass

    def on_error(self, error: Exception) -> None:
        """Called when an error occurs."""
        pass
```

### Custom Hook Implementation

```python
class MonitoredReActAgent(ReActAgent):
    def on_start(self, input_data):
        print(f"[START] Query: {input_data}")
        self.start_time = time.time()

    def on_finish(self, result):
        duration = time.time() - self.start_time
        print(f"[FINISH] Duration: {duration:.2f}s")
        print(f"[RESULT] {result[:100]}...")

    def on_error(self, error):
        print(f"[ERROR] {type(error).__name__}: {error}")
        # Log to monitoring system
        logger.error(f"Agent error: {error}")
```

## Extending Patterns

### Creating Custom Patterns

Inherit from `BaseAgent`:

```python
from agent_patterns.core import BaseAgent
from langgraph.graph import StateGraph, END

class MyCustomPattern(BaseAgent):
    def __init__(self, llm_configs, **kwargs):
        super().__init__(llm_configs, **kwargs)

    def build_graph(self):
        """Define your workflow."""
        workflow = StateGraph(dict)

        # Add your nodes
        workflow.add_node("step1", self._step1)
        workflow.add_node("step2", self._step2)

        # Define flow
        workflow.set_entry_point("step1")
        workflow.add_edge("step1", "step2")
        workflow.add_edge("step2", END)

        # Compile
        self.graph = workflow.compile()

    def run(self, input_data):
        """Execute your pattern."""
        initial_state = {
            "input": input_data,
            "output": None,
        }

        final_state = self.graph.invoke(initial_state)
        return final_state["output"]

    def _step1(self, state):
        """First processing step."""
        # Use LLM
        llm = self._get_llm("thinking")
        # Load prompts
        prompts = self._load_prompt("Step1")
        # Process
        # ...
        return state

    def _step2(self, state):
        """Second processing step."""
        # ...
        return state
```

### Extending Existing Patterns

Override specific methods:

```python
class EnhancedReActAgent(ReActAgent):
    def _generate_thought_and_action(self, state):
        """Override thought generation with custom logic."""
        # Add logging
        print(f"Iteration {state['iteration_count']}")

        # Call parent implementation
        state = super()._generate_thought_and_action(state)

        # Add custom processing
        # ...

        return state
```

## Design Principles

### 1. Synchronous Execution

All patterns are synchronous - no async/await:

```python
# Synchronous
result = agent.run(input)

# NOT async
# result = await agent.run(input)
```

**Why**: Simplicity, debuggability, and sufficient for most use cases.

### 2. Immutable by Default

State updates create new state:

```python
def _update_state(self, state):
    # Return updated state
    return {**state, "new_field": value}

    # NOT in-place modification
    # state["new_field"] = value
    # return state
```

### 3. Explicit Over Implicit

Everything is explicit:
- State is a visible dictionary
- LLM calls are clear
- Tool execution is traceable
- No hidden magic

### 4. Composition Over Inheritance

Prefer composition:

```python
# Good: Compose with tools
agent = ReActAgent(tools={"search": search_fn})

# Less good: Inherit for simple customization
class SearchReActAgent(ReActAgent):
    def __init__(self):
        super().__init__(tools={"search": search_fn})
```

## Performance Considerations

### LLM Caching

LLMs are initialized once and cached:

```python
# First call: initializes LLM
llm = self._get_llm("thinking")

# Subsequent calls: returns cached instance
llm = self._get_llm("thinking")  # Instant
```

### State Graph Compilation

Graphs are compiled once during initialization:

```python
def __init__(self, ...):
    # ...
    self.build_graph()  # Compiled once
    # graph.invoke() is fast

# Each run() reuses compiled graph
result1 = agent.run(input1)  # Uses compiled graph
result2 = agent.run(input2)  # Uses compiled graph
```

### Prompt Loading

Prompts are loaded on-demand and could be cached:

```python
# Loaded when needed
prompts = self._load_prompt("Step1")

# For optimization, cache in subclass:
def __init__(self, ...):
    super().__init__(...)
    self._prompt_cache = {}

def _load_prompt(self, step_name):
    if step_name not in self._prompt_cache:
        self._prompt_cache[step_name] = super()._load_prompt(step_name)
    return self._prompt_cache[step_name]
```

## Next Steps

- **API Reference**: See [BaseAgent API](../api/base-agent.md) for complete method documentation
- **Pattern Details**: Learn about each [pattern's implementation](../api/patterns.md)
- **Examples**: Study [real implementations](../examples/index.md)
- **Type Reference**: Review [type definitions](../api/types.md)
