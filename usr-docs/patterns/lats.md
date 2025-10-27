# LATS Agent Pattern

The **LATS** (Language Agent Tree Search) pattern performs Monte Carlo Tree Search-inspired exploration over possible reasoning paths. Instead of following a single solution chain, LATS explores multiple paths simultaneously, evaluates them, and uses tree search techniques to find the best solution.

## Overview

**Best For**: Complex reasoning tasks with multiple possible solution paths

**Complexity**: ⭐⭐⭐⭐ Very Advanced (Tree search with backpropagation)

**Cost**: $$$$ Very High (Explores many paths with evaluations)

## When to Use LATS

### Ideal Use Cases

✅ **Complex problems with multiple approaches**
- Agent explores different solution strategies
- Evaluates promise of each approach
- Selects best path through tree search
- Finds optimal solution through exploration

✅ **Game-playing and strategic tasks**
- Multiple moves possible at each step
- Need to evaluate future consequences
- Explore different strategies
- Select best action sequence

✅ **Algorithm design and optimization**
- Multiple algorithmic approaches possible
- Trade-offs between approaches
- Need to evaluate which path leads to best solution
- Systematic exploration beneficial

✅ **Planning under uncertainty**
- Multiple valid plans
- Each has different properties
- Need to explore and compare
- Select most promising approach

### When NOT to Use LATS

❌ **Simple, single-path problems** → Use Plan & Solve
❌ **Known optimal approach** → Don't need exploration
❌ **Cost-sensitive applications** → Very expensive pattern
❌ **Time-critical tasks** → Exploration takes time
❌ **Linear workflows** → Overkill for sequential tasks

## How LATS Works

### The Tree Search Process

```
                    ROOT (Initial State)
                    /      |      \
                   /       |       \
         Approach A   Approach B   Approach C
         (visits: 5)  (visits: 8)  (visits: 3)
         (value: 0.6) (value: 0.7) (value: 0.4)
               /  \         |           \
              /    \        |            \
        Step A1  Step A2  Step B1     Step C1
        (v:3)    (v:2)    (v:8)       (v:3)
        (val:0.5)(val:0.7)(val:0.8)   (val:0.3)

Selection: UCB chooses most promising node to explore
Expansion: Generate possible next steps from selected node
Evaluation: Score each new node's promise
Backpropagation: Update values up the tree
Repeat: Continue until budget exhausted
Best Path: Follow highest-value path from root to leaf
```

### Key Concepts

**Upper Confidence Bound (UCB)**:
```
UCB(node) = exploitation + exploration
          = (wins/visits) + c × √(ln(parent_visits)/visits)

Exploitation: Favor nodes with high average value
Exploration: Favor nodes visited less often
```

**Tree Search Cycle**:
1. **Select**: Choose promising node using UCB
2. **Expand**: Generate child nodes (possible next steps)
3. **Evaluate**: Score each child's promise
4. **Backpropagate**: Update ancestor values
5. **Repeat**: Until iteration budget exhausted
6. **Extract**: Follow best path to solution

### Theoretical Foundation

Based on the paper ["LATS: Language Agent Tree Search"](https://arxiv.org/abs/2310.04406). Inspired by Monte Carlo Tree Search (MCTS) used in game-playing AI like AlphaGo.

Key principles:
1. **Exploration vs Exploitation**: Balance trying new paths vs following promising ones
2. **Value estimation**: Score paths based on promise, not just final outcome
3. **Backpropagation**: Learn from outcomes throughout tree
4. **Best path extraction**: Select path with strongest support

### Algorithm

```python
def lats_search(task, max_iterations=10):
    """Simplified LATS algorithm"""

    # Initialize tree
    root = TreeNode(initial_state=task)

    for _ in range(max_iterations):
        # 1. Select most promising leaf using UCB
        node = select_best_leaf(root)

        # 2. Expand: generate possible next steps
        children = llm_expand(node, num_children=3)
        node.children = children

        # 3. Evaluate each child
        for child in children:
            score = llm_evaluate(child)
            child.value = score
            child.visits = 1

        # 4. Backpropagate values up tree
        for child in children:
            backpropagate(child, child.value)

    # Extract best path
    best_path = get_best_path(root)

    # Generate final answer from best path
    final_answer = llm_synthesize(best_path)

    return final_answer

def select_best_leaf(node):
    """Recursively select using UCB"""
    if not node.children:
        return node

    # Choose child with highest UCB score
    best_child = max(node.children, key=lambda c: c.ucb_score())

    return select_best_leaf(best_child)

def backpropagate(node, value):
    """Update values up to root"""
    current = node.parent
    while current:
        current.visits += 1
        current.value += value
        current = current.parent
```

## API Reference

### Class: `LATSAgent`

```python
from agent_patterns.patterns import LATSAgent

agent = LATSAgent(
    llm_configs: Dict[str, Dict[str, Any]],
    tools: Optional[Dict[str, Callable]] = None,
    max_iterations: int = 10,
    exploration_weight: float = 1.41,
    num_expansions: int = 3,
    prompt_dir: str = "prompts",
    custom_instructions: Optional[str] = None,
    prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
)
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `llm_configs` | `Dict[str, Dict[str, Any]]` | Yes | LLM configs for "thinking" and "evaluation" roles |
| `tools` | `Dict[str, Callable]` | No | Dictionary mapping tool names to functions (optional) |
| `max_iterations` | `int` | No | Maximum search iterations (default: 10) |
| `exploration_weight` | `float` | No | UCB exploration parameter (default: 1.41, √2) |
| `num_expansions` | `int` | No | Children to generate per expansion (default: 3) |
| `prompt_dir` | `str` | No | Custom prompt directory (default: "prompts") |
| `custom_instructions` | `str` | No | Instructions appended to system prompts |
| `prompt_overrides` | `Dict` | No | Override specific prompts programmatically |

#### LLM Roles

- **thinking**: Used for node expansion and final output generation
- **evaluation**: Used for scoring node promise

#### Methods

**`run(input_data: str) -> str`**

Executes the LATS tree search on the given input.

- **Parameters**:
  - `input_data` (str): The task or problem to solve
- **Returns**: str - The final answer from the best path
- **Raises**: ValueError if graph not built

**`build_graph() -> None`**

Builds the LangGraph state graph. Called automatically during initialization.

## Complete Examples

### Basic Usage

```python
from agent_patterns.patterns import LATSAgent

# Configure LLMs
llm_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
    },
    "evaluation": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,  # More consistent evaluation
    }
}

# Create agent
agent = LATSAgent(
    llm_configs=llm_configs,
    max_iterations=15,  # More iterations for thorough exploration
    num_expansions=3    # Generate 3 children per expansion
)

# Solve complex reasoning problem
result = agent.run("""
You have 8 coins that look identical. One coin is counterfeit and
weighs slightly different (either heavier or lighter, but you don't
know which). Using a balance scale exactly 2 times, can you:
1. Identify the counterfeit coin
2. Determine if it's heavier or lighter

Provide the complete strategy.
""")

print(result)
# Agent will:
# - Explore different weighing strategies
# - Evaluate which approaches are most promising
# - Backpropagate values through tree
# - Select best strategy
# - Generate detailed solution
```

### With Custom Instructions

```python
problem_solving_instructions = """
You are solving complex problems through systematic exploration.

NODE EXPANSION:
- Generate diverse approaches (don't just vary small details)
- Each child should represent meaningfully different strategy
- Be creative but logical in generating alternatives

NODE EVALUATION:
- Score based on:
  * Logical soundness (0.4 weight)
  * Completeness of approach (0.3 weight)
  * Efficiency (0.2 weight)
  * Clarity (0.1 weight)
- Use scale 0.0 to 1.0
- Be discriminating (don't give everything 0.5)

FINAL OUTPUT:
- Present the winning strategy clearly
- Explain why this approach is optimal
- Address potential objections
"""

agent = LATSAgent(
    llm_configs=llm_configs,
    max_iterations=20,
    num_expansions=4,
    custom_instructions=problem_solving_instructions
)

result = agent.run("""
Design an algorithm to find the median of two sorted arrays
of different lengths in O(log(min(m,n))) time complexity.
Explain the approach and prove the time complexity.
""")
```

### With Prompt Overrides

```python
# Customize expansion and evaluation
overrides = {
    "Expand": {
        "system": """You generate diverse solution approaches for complex problems.
Each approach should be significantly different from the others.""",
        "user": """Task: {task}

Current state: {current_state}

Path so far:
{path}

Generate {num_expansions} different next steps or approaches.
Make them meaningfully different (not just minor variations).

For each expansion, output:
EXPANSION N:
ACTION: <describe the action/approach>
STATE: <describe the resulting state>

Your expansions:"""
    },
    "Evaluate": {
        "system": """You evaluate the promise of solution approaches.
Score from 0.0 (unpromising) to 1.0 (very promising).""",
        "user": """Task: {task}

Current path:
{path}

Current state: {current_state}

Evaluate how promising this path is for solving the task.
Consider:
- Logical soundness
- Progress toward solution
- Likelihood of success
- Efficiency

Output format:
SCORE: <number between 0.0 and 1.0>
REASONING: <brief explanation>

Your evaluation:"""
    }
}

agent = LATSAgent(
    llm_configs=llm_configs,
    prompt_overrides=overrides,
    max_iterations=15
)
```

## Customizing Search Parameters

### Understanding the System Prompt Structure

Version 0.2.0 introduces **enterprise-grade prompts** with a comprehensive 9-section structure (150-300+ lines vs ~32 lines).

**The 9-Section Structure**: All LATS prompts now include Role and Identity, Core Capabilities, Process, Output Format, Decision-Making Guidelines, Quality Standards, Edge Cases, Examples, and Critical Reminders.

**Benefits**: LATS steps for tree generation, evaluation, and selection all benefit from comprehensive prompts with increased reliability and better transparency. No code changes required.

### Exploration vs Exploitation

```python
# More exploration (try diverse paths)
exploratory_agent = LATSAgent(
    llm_configs=llm_configs,
    exploration_weight=2.0,  # Higher = more exploration
    max_iterations=20
)

# More exploitation (follow promising paths)
focused_agent = LATSAgent(
    llm_configs=llm_configs,
    exploration_weight=0.5,  # Lower = more exploitation
    max_iterations=15
)
```

### Search Breadth and Depth

```python
# Wide search (more children per node)
wide_agent = LATSAgent(
    llm_configs=llm_configs,
    num_expansions=5,  # More alternatives
    max_iterations=25  # Need more iterations for wide tree
)

# Deep search (fewer children, more iterations)
deep_agent = LATSAgent(
    llm_configs=llm_configs,
    num_expansions=2,  # Fewer alternatives
    max_iterations=30  # Go deeper into promising paths
)
```

### Iteration Budget

```python
# Quick exploration
quick_agent = LATSAgent(
    llm_configs=llm_configs,
    max_iterations=8,
    num_expansions=2
)

# Thorough exploration
thorough_agent = LATSAgent(
    llm_configs=llm_configs,
    max_iterations=50,
    num_expansions=4
)
```

## Advanced Usage

### Custom Tree Node Logic

```python
class CustomLATSAgent(LATSAgent):
    def _select_best_leaf(self, node):
        """Override with custom selection logic"""
        if not node.children:
            return node

        # Custom UCB calculation
        best_child = None
        best_score = float('-inf')

        for child in node.children:
            # Add domain-specific factors
            custom_score = child.ucb_score(self.exploration_weight)

            # Bonus for depth (encourage deeper exploration)
            depth_bonus = self._get_depth(child) * 0.1

            total_score = custom_score + depth_bonus

            if total_score > best_score:
                best_score = total_score
                best_child = child

        return self._select_best_leaf(best_child)

    def _get_depth(self, node):
        """Calculate node depth"""
        depth = 0
        current = node
        while current.parent:
            depth += 1
            current = current.parent
        return depth

agent = CustomLATSAgent(llm_configs=llm_configs)
```

### Pruning Unpromising Branches

```python
class PruningLATSAgent(LATSAgent):
    def _evaluate_node(self, state):
        """Override to add pruning"""
        state = super()._evaluate_node(state)

        # Prune nodes with very low scores
        expanded_children = state["expanded_children"]
        pruned_children = [
            child for child in expanded_children
            if child.value > 0.2  # Prune if score < 0.2
        ]

        # Remove pruned children from parent
        if pruned_children:
            state["current_node"].children = pruned_children
            state["expanded_children"] = pruned_children

        return state

agent = PruningLATSAgent(
    llm_configs=llm_configs,
    max_iterations=15
)
```

## Performance Considerations

### Cost Analysis

LATS is very expensive:

**Per iteration**:
- Select: No LLM call (tree traversal)
- Expand: 1 LLM call
- Evaluate: N LLM calls (N = num_expansions)
- Backpropagate: No LLM call
- **= 1 + N calls per iteration**

**Total cost**:
- Iterations × (1 + num_expansions) + 1 final generation
- 10 iterations × 4 calls = 40 calls
- 20 iterations × 4 calls = 80 calls

**Optimization strategies**:

```python
# 1. Reduce iterations
agent = LATSAgent(llm_configs=llm_configs, max_iterations=8)

# 2. Reduce expansions per node
agent = LATSAgent(llm_configs=llm_configs, num_expansions=2)

# 3. Use cheaper model for evaluation
llm_configs = {
    "thinking": {"provider": "openai", "model": "gpt-4"},
    "evaluation": {"provider": "openai", "model": "gpt-3.5-turbo"}
}

# 4. Early stopping when confident
# (Custom implementation to stop when best path is clear)
```

### When to Use LATS

✅ **Complex reasoning**: Multiple valid approaches to explore
✅ **High-value tasks**: Quality matters more than cost
✅ **Uncertain paths**: Don't know best approach upfront
✅ **Need robustness**: Want to find truly best solution

❌ **Simple tasks**: Overkill and wasteful
❌ **Known solutions**: Don't need to explore
❌ **Cost-sensitive**: Too expensive
❌ **Time-critical**: Too slow

## Comparison with Other Patterns

| Aspect | LATS | Reflexion | ReAct |
|--------|------|-----------|-------|
| **Exploration** | Tree search | Sequential trials | Single path |
| **Evaluation** | Many nodes | Per trial | Per action |
| **Best For** | Multiple solution paths | Learning from failures | Tool use |
| **Cost** | Very High | High | Medium |
| **Complexity** | Very Advanced | Advanced | Moderate |
| **Output Quality** | Highest (with budget) | High | Medium |

## Common Pitfalls

### 1. Insufficient Iteration Budget

❌ **Bad**: Too few iterations for meaningful exploration
```python
agent = LATSAgent(llm_configs=llm_configs, max_iterations=3)
# Can't explore tree meaningfully
```

✅ **Good**: Adequate budget for task complexity
```python
# Simple tasks: 8-12 iterations
# Complex tasks: 15-25 iterations
# Very complex: 30-50 iterations
agent = LATSAgent(llm_configs=llm_configs, max_iterations=20)
```

### 2. Poor Evaluation Scoring

❌ **Bad**: All nodes get similar scores (0.5)

✅ **Good**: Discriminating evaluation
```python
overrides = {
    "Evaluate": {
        "user": """...
Be discriminating in your scoring:
- 0.0-0.3: Poor approach with fundamental issues
- 0.3-0.5: Mediocre approach with significant gaps
- 0.5-0.7: Decent approach with minor issues
- 0.7-0.9: Strong approach with small refinements needed
- 0.9-1.0: Excellent approach likely to succeed

Avoid giving everything 0.5!

Your score:"""
    }
}
```

### 3. Non-Diverse Expansions

❌ **Bad**: Children are minor variations

✅ **Good**: Meaningfully different approaches
```python
custom_instructions = """
NODE EXPANSION:
Generate substantially different approaches:
- Different algorithmic strategies
- Different problem decompositions
- Different orderings or priorities
NOT just small parameter changes!
"""
```

### 4. Wrong Exploration Weight

❌ **Bad**: Not tuning for problem type

✅ **Good**: Adjust based on needs
```python
# Many viable paths? More exploration
agent = LATSAgent(llm_configs=llm_configs, exploration_weight=2.0)

# Clear best path? More exploitation
agent = LATSAgent(llm_configs=llm_configs, exploration_weight=0.7)
```

## Troubleshooting

### Search Not Exploring Diverse Paths

**Symptom**: Tree grows in one direction only

**Solutions**:
```python
# Increase exploration weight
agent = LATSAgent(
    llm_configs=llm_configs,
    exploration_weight=2.0,  # More exploration
    max_iterations=20
)

# Emphasize diversity in expansion prompt
custom_instructions = """
EXPANSION: Generate RADICALLY different approaches.
Each child must explore a fundamentally different strategy.
"""
```

### Low-Quality Final Solution

**Symptom**: Best path doesn't actually solve problem well

**Solutions**:
```python
# More iterations to explore better
agent = LATSAgent(llm_configs=llm_configs, max_iterations=30)

# Stronger evaluation model
llm_configs = {
    "thinking": {"provider": "openai", "model": "gpt-4"},
    "evaluation": {"provider": "openai", "model": "gpt-4"}  # Not 3.5
}

# Better evaluation criteria
# (Override Evaluate prompt with specific rubric)
```

### Search Takes Too Long

**Symptom**: Unacceptable execution time

**Solutions**:
```python
# Reduce iteration budget
agent = LATSAgent(llm_configs=llm_configs, max_iterations=10)

# Reduce expansions per node
agent = LATSAgent(llm_configs=llm_configs, num_expansions=2)

# Consider if LATS is the right pattern
# For simpler tasks, use Plan & Solve or Reflexion
```

## Next Steps

- Try the [complete examples](../examples/lats-examples.md)
- Learn about [Reflexion](reflexion.md) for simpler multi-trial learning
- Explore [Self-Discovery](self-discovery.md) for structured reasoning
- Read the [original paper](https://arxiv.org/abs/2310.04406)

## References

- Original paper: [Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models](https://arxiv.org/abs/2310.04406)
- Monte Carlo Tree Search: Classic AI technique for game-playing
- UCB algorithm: [Upper Confidence Bounds](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)
- Related: AlphaGo and tree search in reinforcement learning
