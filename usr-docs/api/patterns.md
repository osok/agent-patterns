# Pattern API Reference

Complete API reference for all 9 agent patterns in the library.

## Pattern Overview

| Pattern | Purpose | Complexity | Cost | Best For |
|---------|---------|------------|------|----------|
| [ReAct](#react-pattern) | Reason + Act with tools | Low | Medium | Q&A with external data |
| [Reflection](#reflection-pattern) | Generate, critique, refine | Low | Medium | High-quality content |
| [Plan & Solve](#plan--solve-pattern) | Plan then execute steps | Medium | Medium | Multi-step tasks |
| [Reflexion](#reflexion-pattern) | Learn from failures | Medium | High | Complex problem-solving |
| [LLM Compiler](#llm-compiler-pattern) | Parallel tool execution | High | High | Multi-source data gathering |
| [REWOO](#rewoo-pattern) | Plan-Execute-Solve | Medium | Low | Cost-efficient workflows |
| [LATS](#lats-pattern) | Tree search reasoning | High | Very High | Exploring solution spaces |
| [Self-Discovery](#self-discovery-pattern) | Adaptive reasoning | Medium | Medium | Novel problems |
| [STORM](#storm-pattern) | Multi-perspective research | High | High | Comprehensive reports |

---

## ReAct Pattern

**Reason + Act**: Iteratively reasons about a problem and takes actions (tool calls) until finding an answer.

### Constructor

```python
from agent_patterns.patterns import ReActAgent

ReActAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    tools: Optional[Dict[str, Callable]] = None,
    max_iterations: int = 5,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

**Parameters:**
- **llm_configs**: LLM configuration (requires `"thinking"` role)
- **tools**: Dictionary mapping tool names to callable functions
- **max_iterations**: Maximum reasoning cycles (default: 5)
- **prompt_dir, custom_instructions, prompt_overrides**: See [BaseAgent](base-agent.md)

### State Schema

```python
{
    "input": str,                    # User query
    "thought": str,                  # Current reasoning
    "action": Dict,                  # {"tool_name": str, "tool_input": Any}
    "observation": Any,              # Tool result
    "intermediate_steps": List[Tuple], # History
    "final_answer": str,             # Result
    "iteration_count": int,          # Current iteration
    "max_iterations": int            # Loop limit
}
```

### Methods

#### `run(input_data: str) -> str`
Execute the ReAct loop on the given query.

#### `add_tool(name: str, func: Callable) -> None`
Add a tool to the agent's toolbox.

#### `remove_tool(name: str) -> None`
Remove a tool from the agent.

#### `list_tools() -> List[str]`
Get list of available tool names.

### Example

```python
def search(query: str) -> str:
    return f"Search results for: {query}"

def calculator(expression: str) -> str:
    return str(eval(expression))

agent = ReActAgent(
    llm_configs={
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4-turbo",
            "temperature": 0.7,
        }
    },
    tools={"search": search, "calculator": calculator},
    max_iterations=5
)

result = agent.run("What is the population of Tokyo times 2?")
```

### Workflow

```
1. Thought: Reason about what to do
2. Action: Choose and execute tool
3. Observation: Receive tool result
4. Decision: Continue or provide final answer
5. Repeat steps 1-4 until done or max iterations
```

---

## Reflection Pattern

**Generate-Reflect-Refine**: Creates content, critiques it, and refines based on feedback.

### Constructor

```python
from agent_patterns.patterns import ReflectionAgent

ReflectionAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    max_reflection_cycles: int = 1,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

**Parameters:**
- **llm_configs**: Requires `"documentation"` and `"reflection"` roles
- **max_reflection_cycles**: Number of refinement iterations (default: 1)

### State Schema

```python
{
    "input_task": str,           # User's task
    "initial_output": str,       # First attempt
    "reflection": str,           # Critique
    "refined_output": str,       # Improved version
    "needs_refinement": bool,    # Whether to refine
    "final_answer": str,         # Result
    "reflection_cycle": int,     # Current cycle
    "max_reflection_cycles": int # Cycle limit
}
```

### Example

```python
agent = ReflectionAgent(
    llm_configs={
        "documentation": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
        },
        "reflection": {
            "provider": "openai",
            "model_name": "gpt-4-turbo",
        }
    },
    max_reflection_cycles=2
)

result = agent.run("Write a product description for smart water bottle")
```

### Workflow

```
1. Generate: Create initial content
2. Reflect: Critique the output
3. Check: Determine if refinement needed
4. Refine: Improve based on critique (if needed)
5. Repeat steps 2-4 up to max_reflection_cycles
```

---

## Plan & Solve Pattern

**Planning then Execution**: Separates planning from execution with sequential step processing.

### Constructor

```python
from agent_patterns.patterns import PlanAndSolveAgent

PlanAndSolveAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

**Parameters:**
- **llm_configs**: Requires `"planning"`, `"execution"`, and `"documentation"` roles

### State Schema

```python
{
    "input_task": str,              # User's task
    "plan": List[Dict],             # List of step descriptions
    "current_step_index": int,      # Current step being executed
    "step_results": List[str],      # Results from completed steps
    "plan_done": bool,              # Whether all steps complete
    "final_result": str             # Aggregated result
}
```

### Example

```python
agent = PlanAndSolveAgent(
    llm_configs={
        "planning": {
            "provider": "openai",
            "model_name": "gpt-4-turbo",
        },
        "execution": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
        },
        "documentation": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
        }
    }
)

result = agent.run("Create a marketing strategy for AI language learning app")
```

### Workflow

```
1. Plan: Generate multi-step plan
2. Execute: Process each step sequentially
3. Check: Verify all steps complete
4. Aggregate: Synthesize results into final answer
```

---

## Reflexion Pattern

**Multi-trial Learning**: Learns from previous failures through reflective memory across trials.

### Constructor

```python
from agent_patterns.patterns import ReflexionAgent

ReflexionAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    tools: Optional[Dict[str, Callable]] = None,
    evaluator: Optional[Callable] = None,
    max_trials: int = 3,
    max_iterations_per_trial: int = 5,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

**Parameters:**
- **llm_configs**: Requires `"thinking"` and `"reflection"` roles
- **tools**: Tools for task execution
- **evaluator**: Function to evaluate trial success (returns bool or score)
- **max_trials**: Maximum number of attempts (default: 3)
- **max_iterations_per_trial**: Iterations per trial (default: 5)

### State Schema

```python
{
    "task": str,                    # User's task
    "current_trial": int,           # Trial number
    "max_trials": int,              # Trial limit
    "solution": str,                # Current attempt
    "evaluation": Any,              # Evaluation result
    "reflection_memory": List[str], # Lessons from failures
    "success": bool,                # Whether task solved
    "final_answer": str             # Result
}
```

### Example

```python
def evaluate_code(code: str) -> bool:
    """Evaluate if code is correct."""
    try:
        exec(code)
        return True
    except:
        return False

agent = ReflexionAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "reflection": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    evaluator=evaluate_code,
    max_trials=3
)

result = agent.run("Write a function to calculate fibonacci numbers")
```

### Workflow

```
For each trial:
  1. Generate: Attempt solution
  2. Evaluate: Check if solution succeeds
  3. If success: Return solution
  4. Reflect: Analyze failure and create memory
  5. Next trial: Use memory to improve
```

---

## LLM Compiler Pattern

**DAG-based Parallel Execution**: Plans tool execution as DAG and runs independent tools in parallel.

### Constructor

```python
from agent_patterns.patterns import LLMCompilerAgent

LLMCompilerAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    tools: Optional[Dict[str, Callable]] = None,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

**Parameters:**
- **llm_configs**: Requires `"planning"` and `"synthesis"` roles
- **tools**: Tools for task execution

### State Schema

```python
{
    "task": str,                     # User's task
    "execution_plan": List[Dict],    # DAG of tool calls
    "tool_results": Dict[str, Any],  # Results keyed by task ID
    "dependencies_met": Dict[str, bool], # Dependency tracking
    "final_answer": str              # Synthesized result
}
```

### Example

```python
agent = LLMCompilerAgent(
    llm_configs={
        "planning": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "synthesis": {"provider": "openai", "model_name": "gpt-3.5-turbo"}
    },
    tools={
        "search": search_tool,
        "weather": weather_tool,
        "calculator": calc_tool
    }
)

result = agent.run("Compare weather in Paris and Tokyo, calculate difference")
```

### Workflow

```
1. Plan: Create DAG of tool dependencies
2. Execute: Run independent tools in parallel
3. Wait: For dependencies before executing dependent tasks
4. Synthesize: Combine all results into answer
```

---

## REWOO Pattern

**Planner-Worker-Solver**: Separates planning, execution, and solving for efficiency.

### Constructor

```python
from agent_patterns.patterns import REWOOAgent

REWOOAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    tools: Optional[Dict[str, Callable]] = None,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

**Parameters:**
- **llm_configs**: Requires `"planning"`, `"worker"`, and `"solver"` roles
- **tools**: Tools for information gathering

### State Schema

```python
{
    "task": str,                  # User's task
    "plan": List[Dict],           # Sequence of tool calls
    "observations": List[str],    # Tool results
    "evidence": str,              # Compiled observations
    "final_answer": str           # Solver's answer
}
```

### Example

```python
agent = REWOOAgent(
    llm_configs={
        "planning": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "worker": {"provider": "openai", "model_name": "gpt-3.5-turbo"},
        "solver": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    tools={"search": search, "wiki": wikipedia}
)

result = agent.run("Who won the 2020 Nobel Prize in Physics?")
```

### Workflow

```
1. Plan: Create complete tool execution plan upfront
2. Execute: Worker executes all planned tools
3. Solve: Solver uses gathered evidence to answer
```

---

## LATS Pattern

**Language Agent Tree Search**: Explores multiple reasoning paths using tree search with backtracking.

### Constructor

```python
from agent_patterns.patterns import LATSAgent

LATSAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    tools: Optional[Dict[str, Callable]] = None,
    max_expansions: int = 10,
    max_depth: int = 5,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

**Parameters:**
- **llm_configs**: Requires `"thinking"` and `"evaluation"` roles
- **tools**: Tools for actions
- **max_expansions**: Maximum nodes to explore (default: 10)
- **max_depth**: Maximum tree depth (default: 5)

### State Schema

```python
{
    "task": str,                    # User's task
    "tree": Dict,                   # Search tree structure
    "current_node": str,            # Current node ID
    "best_path": List[Dict],        # Best solution path
    "final_answer": str             # Result from best path
}
```

### Example

```python
agent = LATSAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "evaluation": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    max_expansions=10,
    max_depth=5
)

result = agent.run("Design an efficient algorithm for task scheduling")
```

### Workflow

```
1. Initialize: Create root node
2. Select: Choose promising node to expand
3. Expand: Generate child nodes (actions/thoughts)
4. Evaluate: Score each child
5. Backtrack: Update parent scores
6. Repeat: Until max expansions or solution found
7. Extract: Return best path as solution
```

---

## Self-Discovery Pattern

**Adaptive Reasoning**: Dynamically selects and adapts reasoning strategies from a module library.

### Constructor

```python
from agent_patterns.patterns import SelfDiscoveryAgent

SelfDiscoveryAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    reasoning_modules: Optional[List[Dict[str, str]]] = None,
    max_selected_modules: int = 3,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

**Parameters:**
- **llm_configs**: Requires `"thinking"` and `"execution"` roles
- **reasoning_modules**: Custom reasoning module library (uses defaults if None)
- **max_selected_modules**: Maximum modules to select (default: 3)

### Default Reasoning Modules

```python
- break_down_problem: Decompose into sub-problems
- identify_constraints: Analyze requirements and limitations
- analogical_reasoning: Find similar problems
- first_principles: Reason from fundamentals
- step_by_step: Systematic progression
- pros_and_cons: Evaluate approaches
- critical_analysis: Examine assumptions
- pattern_recognition: Identify patterns
- hypothesis_testing: Form and test hypotheses
- visualization: Create mental models
```

### State Schema

```python
{
    "task": str,                       # User's task
    "selected_modules": List[Dict],    # Chosen reasoning strategies
    "adapted_modules": List[Dict],     # Task-specific adaptations
    "reasoning_plan": List[str],       # Execution sequence
    "reasoning_results": List[str],    # Results from each step
    "current_step": int,               # Current execution step
    "final_answer": str                # Synthesized result
}
```

### Example

```python
agent = SelfDiscoveryAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "execution": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    max_selected_modules=3
)

result = agent.run("How can we reduce traffic congestion in major cities?")
```

### Workflow

```
1. Discover: Select relevant reasoning modules
2. Adapt: Customize modules for specific task
3. Plan: Create reasoning execution plan
4. Execute: Apply each reasoning step
5. Synthesize: Combine results into answer
```

---

## STORM Pattern

**Multi-Perspective Research**: Creates comprehensive reports by synthesizing multiple viewpoints.

### Constructor

```python
from agent_patterns.patterns import STORMAgent

STORMAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    retrieval_tools: Optional[Dict[str, Callable]] = None,
    perspectives: Optional[List[Dict[str, str]]] = None,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

**Parameters:**
- **llm_configs**: Requires `"thinking"` and `"documentation"` roles
- **retrieval_tools**: Tools for information retrieval
- **perspectives**: Custom perspective definitions (uses defaults if None)

### Default Perspectives

```python
- expert: Technical expert with deep domain knowledge
- practitioner: Professional practitioner applying concepts
- researcher: Academic researcher studying the topic
- critic: Critical analyst examining limitations
```

### State Schema

```python
{
    "topic": str,                     # Report topic
    "outline": List[Dict],            # Document structure
    "perspectives": List[Dict],       # Viewpoints to explore
    "questions": List[Dict],          # Questions per perspective
    "retrieved_info": Dict,           # Information gathered
    "section_content": Dict,          # Content per section
    "final_report": str               # Compiled document
}
```

### Example

```python
def search_tool(query: str) -> str:
    return f"Research data for: {query}"

agent = STORMAgent(
    llm_configs={
        "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"},
        "documentation": {"provider": "openai", "model_name": "gpt-4-turbo"}
    },
    retrieval_tools={"search": search_tool}
)

report = agent.run("Artificial Intelligence in Healthcare")
```

### Workflow

```
1. Generate Outline: Create document structure
2. Generate Perspectives: Identify relevant viewpoints
3. Generate Questions: Create questions per perspective per section
4. Retrieve Information: Gather data for each question
5. Synthesize Sections: Write each section from gathered info
6. Compile Report: Assemble final document
```

---

## Common Parameters

All patterns inherit from `BaseAgent` and support:

### LLM Roles

Patterns use different role names based on their needs:

| Pattern | Required Roles |
|---------|---------------|
| ReAct | thinking |
| Reflection | documentation, reflection |
| Plan & Solve | planning, execution, documentation |
| Reflexion | thinking, reflection |
| LLM Compiler | planning, synthesis |
| REWOO | planning, worker, solver |
| LATS | thinking, evaluation |
| Self-Discovery | thinking, execution |
| STORM | thinking, documentation |

### Prompt Customization

All patterns support three levels of customization:

```python
agent = PatternAgent(
    llm_configs=...,
    prompt_dir="custom_prompts",          # File-based
    custom_instructions="Domain context", # Instructions
    prompt_overrides={...}                # Programmatic
)
```

See [BaseAgent](base-agent.md) for details.

### Lifecycle Hooks

All patterns support:

```python
class CustomAgent(PatternAgent):
    def on_start(self, input_data):
        # Called before execution
        pass

    def on_finish(self, result):
        # Called after success
        pass

    def on_error(self, error):
        # Called on error
        pass
```

---

## Pattern Selection Guide

See [Choosing a Pattern](../patterns/choosing-a-pattern.md) for detailed guidance.

## Further Reading

- [BaseAgent API](base-agent.md) - Base class reference
- [Type Reference](types.md) - Type definitions
- [Examples](../examples/index.md) - Real-world usage
- [Architecture](../concepts/architecture.md) - How patterns work internally
