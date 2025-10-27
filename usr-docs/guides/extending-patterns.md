# Extending Agent Patterns

Complete guide to creating custom agent patterns by extending BaseAgent, implementing new workflows, and composing existing patterns.

## Overview

Agent Patterns is designed for extensibility. You can:
- Create entirely new agent patterns
- Extend existing patterns
- Compose multiple patterns together
- Add new workflow steps
- Customize state management

## Understanding BaseAgent

All patterns inherit from `BaseAgent`:

```python
from agent_patterns.core.base_agent import BaseAgent

class BaseAgent(abc.ABC):
    """Base class for all agent patterns."""

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        # Initialization logic

    @abc.abstractmethod
    def build_graph(self) -> None:
        """Build the LangGraph state graph."""
        pass

    @abc.abstractmethod
    def run(self, input_data: Any) -> Any:
        """Execute the agent workflow."""
        pass
```

### Key Methods to Override

1. **`build_graph()`**: Define workflow structure
2. **`run()`**: Execute the workflow
3. **`on_start()`, `on_finish()`, `on_error()`**: Lifecycle hooks (optional)

## Creating a Simple Custom Pattern

### Step 1: Define the Pattern Class

```python
from agent_patterns.core.base_agent import BaseAgent
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

class SimpleReasonerAgent(BaseAgent):
    """Simple custom agent that thinks then acts."""

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        max_reasoning_steps: int = 3,
        **kwargs
    ):
        self.max_reasoning_steps = max_reasoning_steps
        super().__init__(llm_configs=llm_configs, **kwargs)

    def build_graph(self) -> None:
        """Build the state graph."""
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("think", self._think)
        workflow.add_node("act", self._act)
        workflow.add_node("check", self._check_completion)

        # Set entry point
        workflow.set_entry_point("think")

        # Add edges
        workflow.add_edge("think", "act")
        workflow.add_edge("act", "check")

        # Conditional routing
        workflow.add_conditional_edges(
            "check",
            self._route_after_check,
            {
                "continue": "think",
                "finish": END
            }
        )

        self.graph = workflow.compile()

    def run(self, input_data: Any) -> Any:
        """Execute the agent."""
        self.on_start(input_data)

        try:
            initial_state = {
                "input": input_data,
                "thoughts": [],
                "actions": [],
                "current_step": 0,
                "done": False,
                "result": None
            }

            final_state = self.graph.invoke(initial_state)

            result = final_state.get("result", "No result")
            self.on_finish(result)
            return result

        except Exception as e:
            self.on_error(e)
            raise

    def _think(self, state: Dict) -> Dict:
        """Reasoning step."""
        prompts = self._load_prompt("Think")
        llm = self._get_llm("thinking")

        messages = [
            SystemMessage(content=prompts["system"]),
            HumanMessage(content=prompts["user"].format(
                input=state["input"],
                previous_thoughts="\n".join(state["thoughts"])
            ))
        ]

        response = llm.invoke(messages)
        state["thoughts"].append(response.content)

        return state

    def _act(self, state: Dict) -> Dict:
        """Action step."""
        prompts = self._load_prompt("Act")
        llm = self._get_llm("execution")

        messages = [
            SystemMessage(content=prompts["system"]),
            HumanMessage(content=prompts["user"].format(
                input=state["input"],
                thought=state["thoughts"][-1]
            ))
        ]

        response = llm.invoke(messages)
        state["actions"].append(response.content)
        state["current_step"] += 1

        return state

    def _check_completion(self, state: Dict) -> Dict:
        """Check if workflow should continue."""
        state["done"] = (
            state["current_step"] >= self.max_reasoning_steps or
            "FINISH" in state["actions"][-1].upper()
        )

        if state["done"]:
            state["result"] = state["actions"][-1]

        return state

    def _route_after_check(self, state: Dict) -> str:
        """Route based on completion check."""
        return "finish" if state["done"] else "continue"
```

### Step 2: Create Prompt Templates

```bash
mkdir -p prompts/SimpleReasonerAgent/Think
mkdir -p prompts/SimpleReasonerAgent/Act
```

**prompts/SimpleReasonerAgent/Think/system.md**:
```markdown
You are a thoughtful reasoning agent. Analyze the problem step-by-step.
```

**prompts/SimpleReasonerAgent/Think/user.md**:
```markdown
Problem: {input}

Previous thoughts:
{previous_thoughts}

What's your next thought?
```

**prompts/SimpleReasonerAgent/Act/system.md**:
```markdown
You take actions based on reasoning. Be clear and specific.
```

**prompts/SimpleReasonerAgent/Act/user.md**:
```markdown
Problem: {input}

Thought: {thought}

What action should you take? (Say "FINISH: [answer]" when done)
```

### Step 3: Use the Custom Pattern

```python
# Create agent
agent = SimpleReasonerAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model": "gpt-4"},
        "execution": {"provider": "openai", "model": "gpt-4"}
    },
    max_reasoning_steps=3
)

# Run agent
result = agent.run("What is 15% of 80?")
print(result)
```

## Extending Existing Patterns

### Adding Custom Behavior

```python
from agent_patterns.patterns import ReflectionAgent

class CustomReflectionAgent(ReflectionAgent):
    """Reflection agent with custom validation."""

    def _generate_initial_output(self, state: Dict) -> Dict:
        """Override to add validation."""

        # Call parent implementation
        state = super()._generate_initial_output(state)

        # Add custom validation
        output = state["initial_output"]
        if not self._validate_output(output):
            state["initial_output"] = "Please provide more detail: " + output

        return state

    def _validate_output(self, output: str) -> bool:
        """Custom validation logic."""
        return len(output) > 100 and "example" in output.lower()
```

### Adding New Steps

```python
from agent_patterns.patterns import SelfDiscoveryAgent
from langgraph.graph import StateGraph

class ExtendedSelfDiscoveryAgent(SelfDiscoveryAgent):
    """Self-Discovery with additional verification step."""

    def build_graph(self) -> None:
        """Build graph with additional verification step."""

        # Call parent to set up base graph
        workflow = StateGraph(dict)

        # Add all original nodes
        workflow.add_node("discover_modules", self._discover_modules)
        workflow.add_node("adapt_modules", self._adapt_modules)
        workflow.add_node("plan_reasoning", self._plan_reasoning)
        workflow.add_node("execute_step", self._execute_step)
        workflow.add_node("check_completion", self._check_completion)
        workflow.add_node("verify_result", self._verify_result)  # NEW
        workflow.add_node("synthesize_output", self._synthesize_output)

        # Set entry point
        workflow.set_entry_point("discover_modules")

        # Add edges
        workflow.add_edge("discover_modules", "adapt_modules")
        workflow.add_edge("adapt_modules", "plan_reasoning")
        workflow.add_edge("plan_reasoning", "execute_step")
        workflow.add_edge("execute_step", "check_completion")

        workflow.add_conditional_edges(
            "check_completion",
            self._route_after_check,
            {
                "continue": "execute_step",
                "finish": "verify_result"  # NEW: verify before synthesize
            }
        )

        workflow.add_edge("verify_result", "synthesize_output")
        workflow.add_edge("synthesize_output", "__end__")

        self.graph = workflow.compile()

    def _verify_result(self, state: Dict) -> Dict:
        """NEW: Verify result before final synthesis."""

        prompts = self._load_prompt("VerifyResult")
        llm = self._get_llm("thinking")

        # Verification logic
        messages = [
            SystemMessage(content=prompts["system"]),
            HumanMessage(content=prompts["user"].format(
                task=state["input_task"],
                results="\n".join(state["step_results"])
            ))
        ]

        response = llm.invoke(messages)

        state["verification"] = response.content

        # If verification finds issues, flag for user
        if "issue" in response.content.lower():
            state["verification_issues"] = True

        return state
```

## Composing Multiple Patterns

### Sequential Composition

```python
class SequentialAgent:
    """Run multiple agents in sequence."""

    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run(self, input_data: Any) -> Any:
        """Run agents sequentially, passing output to next input."""

        result = input_data

        for i, agent in enumerate(self.agents):
            print(f"Running agent {i+1}/{len(self.agents)}: {type(agent).__name__}")
            result = agent.run(result)

        return result

# Usage
planner = PlanAndSolveAgent(llm_configs=configs)
executor = ReActAgent(llm_configs=configs, tools=tools)
reviewer = ReflectionAgent(llm_configs=configs)

pipeline = SequentialAgent([planner, executor, reviewer])
result = pipeline.run("Build a web scraper for news articles")
```

### Parallel Composition

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

class ParallelAgent:
    """Run multiple agents in parallel and combine results."""

    def __init__(self, agents: List[BaseAgent], combiner_llm):
        self.agents = agents
        self.combiner_llm = combiner_llm

    def run(self, input_data: Any) -> Any:
        """Run agents in parallel and combine results."""

        results = []

        with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            futures = {
                executor.submit(agent.run, input_data): agent
                for agent in self.agents
            }

            for future in as_completed(futures):
                agent = futures[future]
                try:
                    result = future.result()
                    results.append({
                        "agent": type(agent).__name__,
                        "result": result
                    })
                except Exception as e:
                    print(f"Agent {type(agent).__name__} failed: {e}")

        # Combine results
        combined = self._combine_results(results)
        return combined

    def _combine_results(self, results: List[Dict]) -> str:
        """Combine multiple agent results."""

        results_text = "\n\n".join([
            f"Agent {r['agent']}:\n{r['result']}"
            for r in results
        ])

        prompt = f"""
        Multiple agents have analyzed the task. Synthesize their insights into a single coherent answer.

        Results:
        {results_text}

        Synthesized answer:
        """

        response = self.combiner_llm.invoke(prompt)
        return response.content

# Usage
agent1 = SelfDiscoveryAgent(llm_configs=configs)
agent2 = ReflectionAgent(llm_configs=configs)
agent3 = STORMAgent(llm_configs=configs, retrieval_tools={"search": search})

parallel = ParallelAgent(
    agents=[agent1, agent2, agent3],
    combiner_llm=ChatOpenAI(model="gpt-4")
)

result = parallel.run("Analyze climate change impacts")
```

### Hierarchical Composition

```python
class HierarchicalAgent(BaseAgent):
    """Agent that delegates to sub-agents."""

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        sub_agents: Dict[str, BaseAgent],
        **kwargs
    ):
        self.sub_agents = sub_agents
        super().__init__(llm_configs=llm_configs, **kwargs)

    def build_graph(self) -> None:
        """Build coordination graph."""
        workflow = StateGraph(dict)

        workflow.add_node("coordinate", self._coordinate)
        workflow.add_node("delegate", self._delegate)
        workflow.add_node("synthesize", self._synthesize)

        workflow.set_entry_point("coordinate")
        workflow.add_edge("coordinate", "delegate")
        workflow.add_edge("delegate", "synthesize")
        workflow.add_edge("synthesize", END)

        self.graph = workflow.compile()

    def run(self, input_data: Any) -> Any:
        """Run hierarchical workflow."""
        initial_state = {
            "input": input_data,
            "sub_tasks": [],
            "sub_results": {},
            "final_result": None
        }

        final_state = self.graph.invoke(initial_state)
        return final_state["final_result"]

    def _coordinate(self, state: Dict) -> Dict:
        """Determine which sub-agents to use."""

        prompts = self._load_prompt("Coordinate")
        llm = self._get_llm("coordination")

        # Determine sub-tasks
        messages = [
            SystemMessage(content=prompts["system"]),
            HumanMessage(content=prompts["user"].format(
                task=state["input"],
                available_agents=list(self.sub_agents.keys())
            ))
        ]

        response = llm.invoke(messages)

        # Parse sub-tasks (simplified)
        sub_tasks = [
            line.strip()
            for line in response.content.split("\n")
            if line.strip().startswith("SUBTASK:")
        ]

        state["sub_tasks"] = sub_tasks
        return state

    def _delegate(self, state: Dict) -> Dict:
        """Delegate to sub-agents."""

        for sub_task in state["sub_tasks"]:
            # Determine which agent to use
            agent_name = self._select_agent(sub_task)

            if agent_name in self.sub_agents:
                agent = self.sub_agents[agent_name]
                result = agent.run(sub_task)
                state["sub_results"][sub_task] = result

        return state

    def _synthesize(self, state: Dict) -> Dict:
        """Synthesize sub-results."""

        prompts = self._load_prompt("Synthesize")
        llm = self._get_llm("synthesis")

        results_text = "\n\n".join([
            f"Subtask: {task}\nResult: {result}"
            for task, result in state["sub_results"].items()
        ])

        messages = [
            SystemMessage(content=prompts["system"]),
            HumanMessage(content=prompts["user"].format(
                original_task=state["input"],
                sub_results=results_text
            ))
        ]

        response = llm.invoke(messages)
        state["final_result"] = response.content

        return state

    def _select_agent(self, sub_task: str) -> str:
        """Select appropriate sub-agent for task."""
        # Simple keyword matching (could use LLM for better selection)
        if "research" in sub_task.lower():
            return "storm"
        elif "code" in sub_task.lower():
            return "react"
        else:
            return "reflection"
```

## Advanced Customization

### Custom State Management

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class CustomState(TypedDict):
    """Custom state with typed fields."""

    messages: Annotated[list, add_messages]
    input: str
    output: str
    metadata: dict
    iteration: int

class TypedAgent(BaseAgent):
    """Agent with custom typed state."""

    def build_graph(self) -> None:
        workflow = StateGraph(CustomState)

        # Add nodes
        workflow.add_node("process", self._process)

        # Build graph
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)

        self.graph = workflow.compile()

    def _process(self, state: CustomState) -> CustomState:
        """Process with typed state."""
        # Type-safe state access
        input_text = state["input"]
        iteration = state["iteration"]

        # Update state
        state["output"] = f"Processed: {input_text}"
        state["iteration"] = iteration + 1

        return state
```

### Adding Tools to Patterns

```python
class ToolEnabledSelfDiscovery(SelfDiscoveryAgent):
    """Self-Discovery with tool support."""

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        tools: Dict[str, Callable],
        **kwargs
    ):
        self.tools = tools
        super().__init__(llm_configs=llm_configs, **kwargs)

    def _execute_step(self, state: Dict) -> Dict:
        """Execute step with tool support."""

        # Call parent
        state = super()._execute_step(state)

        # Check if step requires tool use
        step_result = state["step_results"][-1]

        if "USE_TOOL:" in step_result:
            # Extract tool call
            tool_name, tool_input = self._parse_tool_call(step_result)

            if tool_name in self.tools:
                # Execute tool
                tool_result = self.tools[tool_name](tool_input)

                # Update result
                state["step_results"][-1] = f"{step_result}\nTool Result: {tool_result}"

        return state

    def _parse_tool_call(self, text: str) -> tuple:
        """Parse tool call from text."""
        # Simple parsing logic
        lines = text.split("\n")
        for line in lines:
            if line.startswith("USE_TOOL:"):
                parts = line.split(":", 2)
                return parts[1].strip(), parts[2].strip()
        return None, None
```

## Testing Custom Patterns

```python
import pytest
from unittest.mock import Mock, patch

def test_simple_reasoner_initialization():
    """Test custom pattern initializes."""

    agent = SimpleReasonerAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model": "gpt-4"},
            "execution": {"provider": "openai", "model": "gpt-4"}
        },
        max_reasoning_steps=3
    )

    assert agent.max_reasoning_steps == 3
    assert agent.graph is not None

@patch.object(SimpleReasonerAgent, "_get_llm")
def test_simple_reasoner_workflow(mock_get_llm):
    """Test custom pattern workflow."""

    # Mock LLM
    mock_llm = Mock()
    mock_responses = [
        Mock(content="Thought 1"),
        Mock(content="Action 1"),
        Mock(content="Thought 2"),
        Mock(content="FINISH: Final answer")
    ]
    mock_llm.invoke.side_effect = mock_responses
    mock_get_llm.return_value = mock_llm

    agent = SimpleReasonerAgent(
        llm_configs={"thinking": {}, "execution": {}},
        max_reasoning_steps=2
    )

    result = agent.run("Test task")

    assert "Final answer" in result
```

## Best Practices

### 1. Follow BaseAgent Contract

Always implement required abstract methods:
- `build_graph()`
- `run()`

### 2. Use Lifecycle Hooks

```python
class LoggingAgent(BaseAgent):
    def on_start(self, input_data):
        logger.info(f"Starting: {input_data[:100]}")

    def on_finish(self, result):
        logger.info(f"Finished: {len(result)} chars")

    def on_error(self, error):
        logger.error(f"Error: {error}", exc_info=True)
```

### 3. Make Patterns Configurable

```python
class FlexibleAgent(BaseAgent):
    def __init__(
        self,
        llm_configs,
        max_iterations=5,
        enable_caching=True,
        custom_validator=None,
        **kwargs
    ):
        self.max_iterations = max_iterations
        self.enable_caching = enable_caching
        self.validator = custom_validator or default_validator

        super().__init__(llm_configs=llm_configs, **kwargs)
```

### 4. Document Your Pattern

```python
class MyCustomAgent(BaseAgent):
    """Custom agent pattern for [specific use case].

    This pattern implements [workflow description].

    Workflow:
        1. [Step 1 description]
        2. [Step 2 description]
        3. [Step 3 description]

    Args:
        llm_configs: LLM configuration dictionary
        custom_param: Description of custom parameter

    Example:
        >>> agent = MyCustomAgent(
        ...     llm_configs=configs,
        ...     custom_param=value
        ... )
        >>> result = agent.run("task description")
    """
```

### 5. Reuse Existing Components

Don't reinvent the wheel - leverage existing patterns:

```python
from agent_patterns.patterns import ReflectionAgent

class MyAgent(BaseAgent):
    def __init__(self, llm_configs, **kwargs):
        super().__init__(llm_configs=llm_configs, **kwargs)

        # Reuse Reflection as a sub-component
        self.refiner = ReflectionAgent(
            llm_configs=llm_configs,
            max_reflection_cycles=1
        )

    def _refine_output(self, output: str) -> str:
        """Use Reflection pattern for refinement."""
        return self.refiner.run(output)
```

## Next Steps

- Review [Testing Guide](testing.md) for testing custom patterns
- See [Best Practices](best-practices.md) for optimization
- Explore existing patterns for inspiration

## Reference

### BaseAgent API

- `__init__(llm_configs, prompt_dir, custom_instructions, prompt_overrides)`
- `build_graph()`: Abstract - must implement
- `run(input_data)`: Abstract - must implement
- `_get_llm(role)`: Get LLM for role
- `_load_prompt(step_name)`: Load prompts
- `on_start(input_data)`: Lifecycle hook
- `on_finish(result)`: Lifecycle hook
- `on_error(error)`: Lifecycle hook

### State Graph Components

- `StateGraph(state_type)`: Create graph
- `add_node(name, func)`: Add node
- `add_edge(from, to)`: Add edge
- `add_conditional_edges(node, router, mapping)`: Conditional routing
- `set_entry_point(node)`: Set entry
- `compile()`: Compile graph
