# Type Reference

Type definitions, data structures, and type hints used in Agent Patterns.

## Core Types

### LLM Configuration Types

#### `LLMConfig`

```python
from typing import TypedDict, Literal

class LLMConfig(TypedDict, total=False):
    """Configuration for a single LLM role."""
    provider: Literal["openai", "anthropic"]
    model_name: str
    temperature: float      # Optional, default: 0.7
    max_tokens: int        # Optional, default: 2000
```

**Example:**

```python
llm_config: LLMConfig = {
    "provider": "openai",
    "model_name": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 2000,
}
```

#### `LLMConfigs`

```python
from typing import Dict, Any

LLMConfigs = Dict[str, Dict[str, Any]]
```

**Example:**

```python
llm_configs: LLMConfigs = {
    "thinking": {
        "provider": "openai",
        "model_name": "gpt-4-turbo",
    },
    "reflection": {
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-20241022",
    },
}
```

### Prompt Types

#### `PromptDict`

```python
from typing import TypedDict

class PromptDict(TypedDict):
    """Prompt templates for a step."""
    system: str
    user: str
```

**Example:**

```python
prompt: PromptDict = {
    "system": "You are a helpful assistant.",
    "user": "Task: {task}\n\nPlease help."
}
```

#### `PromptOverrides`

```python
from typing import Dict

PromptOverrides = Dict[str, PromptDict]
```

**Example:**

```python
overrides: PromptOverrides = {
    "ThoughtStep": {
        "system": "Think carefully.",
        "user": "Question: {input}"
    },
    "ActionStep": {
        "system": "Execute precisely.",
        "user": "Action: {action}"
    }
}
```

### Tool Types

#### `ToolFunction`

```python
from typing import Callable

ToolFunction = Callable[[str], str]
```

**Example:**

```python
def search_tool(query: str) -> str:
    return f"Results for: {query}"

my_tool: ToolFunction = search_tool
```

#### `ToolDict`

```python
from typing import Dict, Callable

ToolDict = Dict[str, Callable]
```

**Example:**

```python
tools: ToolDict = {
    "search": search_tool,
    "calculator": calc_tool,
    "database": db_tool,
}
```

### State Types

#### `State`

Generic state dictionary:

```python
from typing import Dict, Any

State = Dict[str, Any]
```

**Example:**

```python
state: State = {
    "input": "user query",
    "output": None,
    "iteration": 0,
}
```

#### Pattern-Specific State Types

**ReActState:**

```python
from typing import TypedDict, List, Tuple, Optional

class ReActState(TypedDict):
    input: str
    thought: str
    action: Dict[str, str]
    observation: Any
    intermediate_steps: List[Tuple[str, Dict, Any]]
    final_answer: Optional[str]
    iteration_count: int
    max_iterations: int
```

**ReflectionState:**

```python
class ReflectionState(TypedDict):
    input_task: str
    initial_output: Optional[str]
    reflection: Optional[str]
    refined_output: Optional[str]
    needs_refinement: bool
    final_answer: Optional[str]
    reflection_cycle: int
    max_reflection_cycles: int
    continue_reflection: bool
```

**PlanAndSolveState:**

```python
class PlanAndSolveState(TypedDict):
    input_task: str
    plan: List[Dict[str, str]]
    current_step_index: int
    step_results: List[str]
    plan_done: bool
    final_result: Optional[str]
```

### Action Types

#### `Action`

```python
from typing import TypedDict

class Action(TypedDict):
    """Tool invocation specification."""
    tool_name: str
    tool_input: str
```

**Example:**

```python
action: Action = {
    "tool_name": "search",
    "tool_input": "Python programming"
}
```

### Result Types

#### `AgentResult`

```python
from typing import Union

AgentResult = Union[str, Dict[str, Any]]
```

Most patterns return strings, but some may return structured data.

## Pattern-Specific Types

### ReAct Pattern

```python
from typing import List, Tuple, Dict, Any, Optional

# Intermediate step: (thought, action, observation)
IntermediateStep = Tuple[str, Dict[str, str], Any]

class ReActConfig(TypedDict, total=False):
    llm_configs: Dict[str, Dict[str, Any]]
    tools: Dict[str, Callable[[str], str]]
    max_iterations: int
    prompt_dir: str
    custom_instructions: Optional[str]
    prompt_overrides: Optional[Dict[str, Dict[str, str]]]
```

### Reflection Pattern

```python
class ReflectionConfig(TypedDict, total=False):
    llm_configs: Dict[str, Dict[str, Any]]
    max_reflection_cycles: int
    prompt_dir: str
    custom_instructions: Optional[str]
    prompt_overrides: Optional[Dict[str, Dict[str, str]]]
```

### Self-Discovery Pattern

```python
from typing import List, Dict

class ReasoningModule(TypedDict):
    """Reasoning strategy definition."""
    name: str
    description: str
    template: str

class SelfDiscoveryConfig(TypedDict, total=False):
    llm_configs: Dict[str, Dict[str, Any]]
    reasoning_modules: Optional[List[ReasoningModule]]
    max_selected_modules: int
    prompt_dir: str
    custom_instructions: Optional[str]
    prompt_overrides: Optional[Dict[str, Dict[str, str]]]
```

### STORM Pattern

```python
class Perspective(TypedDict):
    """Viewpoint for multi-perspective analysis."""
    name: str
    description: str

class STORMConfig(TypedDict, total=False):
    llm_configs: Dict[str, Dict[str, Any]]
    retrieval_tools: Optional[Dict[str, Callable]]
    perspectives: Optional[List[Perspective]]
    prompt_dir: str
    custom_instructions: Optional[str]
    prompt_overrides: Optional[Dict[str, Dict[str, str]]]
```

## LangChain/LangGraph Types

### LLM Types

```python
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Base type for all chat models
LLMType = BaseChatModel

# Specific implementations
OpenAIModel = ChatOpenAI
AnthropicModel = ChatAnthropic
```

### Message Types

```python
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)

MessageType = BaseMessage
Messages = List[BaseMessage]
```

**Example:**

```python
messages: Messages = [
    SystemMessage(content="You are helpful."),
    HumanMessage(content="Hello!"),
    AIMessage(content="Hi there!"),
]
```

### Graph Types

```python
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph

Graph = CompiledStateGraph
GraphBuilder = StateGraph
```

## Utility Types

### Optional and Union

```python
from typing import Optional, Union

# Optional value (can be None)
MaybeString = Optional[str]
MaybeConfig = Optional[Dict[str, Any]]

# Union of types
StringOrDict = Union[str, Dict[str, Any]]
IntOrFloat = Union[int, float]
```

### Callable Types

```python
from typing import Callable, Any

# Function signatures
EvaluatorFunction = Callable[[Any], bool]
ToolFunction = Callable[[str], str]
ProcessorFunction = Callable[[Dict], Dict]
```

**Examples:**

```python
def my_evaluator(result: Any) -> bool:
    return len(result) > 0

def my_tool(input: str) -> str:
    return f"Processed: {input}"

def my_processor(state: Dict) -> Dict:
    state["processed"] = True
    return state

evaluator: EvaluatorFunction = my_evaluator
tool: ToolFunction = my_tool
processor: ProcessorFunction = my_processor
```

### Generic Types

```python
from typing import TypeVar, Generic, List, Dict

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Generic list
GenericList = List[T]

# Generic dict
GenericDict = Dict[K, V]
```

## Type Checking

### Runtime Type Checking

```python
from typing import get_type_hints

def validate_config(config: LLMConfig) -> bool:
    """Validate LLM configuration."""
    required = {"provider", "model_name"}
    return all(key in config for key in required)
```

### Type Guards

```python
from typing import TypeGuard

def is_llm_config(obj: Any) -> TypeGuard[LLMConfig]:
    """Check if object is valid LLM config."""
    return (
        isinstance(obj, dict) and
        "provider" in obj and
        "model_name" in obj
    )
```

## Type Hints in Practice

### Function Signatures

```python
from typing import Dict, List, Optional, Any

def create_agent(
    llm_configs: LLMConfigs,
    tools: Optional[ToolDict] = None,
    max_iterations: int = 5
) -> BaseAgent:
    """Create agent with type hints."""
    pass

def process_state(
    state: State,
    llm: BaseChatModel
) -> State:
    """Process state with LLM."""
    pass

def format_messages(
    system_prompt: str,
    user_prompt: str
) -> List[BaseMessage]:
    """Format prompts into messages."""
    pass
```

### Class Type Hints

```python
from typing import Dict, Optional, Any

class MyAgent(BaseAgent):
    """Agent with proper type hints."""

    def __init__(
        self,
        llm_configs: LLMConfigs,
        custom_param: Optional[str] = None
    ) -> None:
        self.custom_param: Optional[str] = custom_param
        super().__init__(llm_configs=llm_configs)

    def build_graph(self) -> None:
        """Build graph (no return value)."""
        pass

    def run(self, input_data: str) -> str:
        """Run agent (returns string)."""
        return "result"

    def _helper(
        self,
        state: State,
        param: Optional[int] = None
    ) -> State:
        """Helper method with types."""
        return state
```

## Type Aliases

Create readable aliases:

```python
from typing import Dict, List, Tuple, Callable

# Configuration aliases
AgentConfig = Dict[str, Any]
ModelConfig = Dict[str, Any]

# State aliases
AgentState = Dict[str, Any]
WorkflowState = Dict[str, Any]

# Function aliases
StateProcessor = Callable[[AgentState], AgentState]
Evaluator = Callable[[Any], bool]
ToolCall = Callable[[str], str]

# Complex types
StepHistory = List[Tuple[str, Dict, Any]]
PlanSteps = List[Dict[str, str]]
```

**Usage:**

```python
def process_workflow(
    state: WorkflowState,
    config: AgentConfig,
    processor: StateProcessor
) -> WorkflowState:
    """Process workflow with typed parameters."""
    return processor(state)
```

## mypy Configuration

For type checking with mypy:

```ini
# mypy.ini or pyproject.toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true
ignore_missing_imports = true
```

Run type checking:

```bash
mypy agent_patterns/
```

## Type Stubs

For third-party libraries without types:

```python
# stubs/external_lib.pyi
from typing import Any, Dict

def external_function(param: str) -> Dict[str, Any]: ...

class ExternalClass:
    def __init__(self, config: Dict[str, Any]) -> None: ...
    def process(self, data: str) -> str: ...
```

## Best Practices

### 1. Always Use Type Hints

```python
# Good
def process(data: str, config: Dict[str, Any]) -> str:
    return data.upper()

# Bad
def process(data, config):
    return data.upper()
```

### 2. Use Optional for Nullable Values

```python
# Good
def get_value(key: str) -> Optional[str]:
    return cache.get(key)

# Bad
def get_value(key: str) -> str:
    return cache.get(key)  # Could return None!
```

### 3. Use TypedDict for Structured Dicts

```python
# Good
class Config(TypedDict):
    name: str
    value: int

# Bad
Config = Dict[str, Any]
```

### 4. Document Complex Types

```python
from typing import Dict, List, Tuple

# Document meaning
StepHistory = List[Tuple[
    str,         # thought
    Dict,        # action
    Any          # observation
]]
```

## See Also

- [BaseAgent API](base-agent.md) - Base class methods
- [Pattern API](patterns.md) - Pattern-specific types
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
