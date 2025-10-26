# Agent-Patterns Project: Implementation Notes

**Date Created:** October 26, 2025
**Last Updated:** October 26, 2025

---

## Project Overview

The agent-patterns library provides reusable AI agent workflow patterns implemented using LangGraph and LangChain. All patterns are synchronous (no async/await) and follow a consistent architecture based on abstract base classes.

---

## Key Architectural Decisions

### 1. Synchronous-Only Implementation
**Decision:** No async code anywhere in the codebase
**Rationale:** Simplifies implementation, debugging, and integration. Avoids event loop complexity.
**Impact:** All LLM calls, tool executions, and state transitions are synchronous.

### 2. LangGraph for State Management
**Decision:** Use LangGraph's StateGraph for all pattern implementations
**Rationale:** Provides clear DAG structure, explicit state transitions, and debuggability.
**Implementation:** Each pattern builds a StateGraph in `build_graph()` method.

### 3. Externalized Prompts
**Decision:** Store all prompts as markdown files in prompts/ directory
**Rationale:** Enables easy modification without code changes, version control of prompts.
**Structure:** `prompts/{PatternClassName}/{StepName}/system.md` and `user.md`

### 4. Role-Based LLM Configuration
**Decision:** Support multiple LLM roles (thinking, reflection, documentation, etc.)
**Rationale:** Different tasks benefit from different models (e.g., expensive for planning, cheap for execution).
**Implementation:** `_get_llm(role)` method in BaseAgent.

### 5. Abstract Base Classes
**Decision:** Two base classes - BaseAgent and MultiAgentBase
**Rationale:** Enforces consistency, provides reusable infrastructure, clear contracts.
**Key Methods:** `build_graph()`, `run()`, `_get_llm()`, `_load_prompt()`

---

## Pattern Implementation Guide

### Pattern Development Checklist

For each new pattern:

1. **Design Phase**
   - [ ] Identify the pattern's workflow stages
   - [ ] Define state dictionary structure
   - [ ] Map nodes and edges in StateGraph
   - [ ] Identify LLM roles needed

2. **Implementation Phase**
   - [ ] Subclass BaseAgent (or MultiAgentBase)
   - [ ] Implement `build_graph()` with all nodes and edges
   - [ ] Implement `run()` method
   - [ ] Implement all node handler methods (e.g., `_generate_plan()`)
   - [ ] Add type hints to all methods
   - [ ] Add comprehensive docstrings

3. **Prompt Phase**
   - [ ] Create directory: `prompts/{PatternName}/`
   - [ ] For each LLM step, create system.md and user.md
   - [ ] Include placeholder documentation in prompts

4. **Testing Phase**
   - [ ] Create test file: `tests/test_{pattern_name}.py`
   - [ ] Test with mocked LLMs
   - [ ] Test state transitions
   - [ ] Test edge cases (empty state, max iterations, etc.)

5. **Documentation Phase**
   - [ ] Create example: `examples/{pattern_name}_example.py`
   - [ ] Document in README.md
   - [ ] Add usage notes

---

## State Dictionary Conventions

### Common State Keys

All patterns should use consistent naming:

- `input_task` or `input_data`: Initial user query/request
- `final_answer` or `final_result`: Final output
- `intermediate_steps`: List of (action, result) tuples
- `iteration_count` or `trial_count`: Loop counter
- `max_iterations` or `max_trials`: Loop limit

### Pattern-Specific State Keys

Document pattern-specific keys in the pattern's docstring:

```python
class MyAgent(BaseAgent):
    """
    My Agent Pattern.

    State Keys:
        - input_task (str): User's query
        - custom_state (dict): Pattern-specific data
        - final_answer (str): Final output
    """
```

---

## LLM Integration Notes

### Supported Providers

Target providers (configured via .env):
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Other LangChain-supported providers

### LLM Role Definitions

Standard roles across patterns:
- **thinking**: Primary reasoning model (e.g., GPT-4)
- **reflection**: Self-critique model (can be same or different)
- **documentation**: Output generation (can be cheaper model)
- **planning**: Planning and decomposition (typically expensive model)
- **execution**: Task execution (can be cheaper model)

### Prompt Template Structure

Each prompt directory contains:
- `system.md`: System prompt defining role and behavior
- `user.md`: User prompt template with {placeholders}

Example:
```
prompts/
└── ReActAgent/
    ├── ThoughtStep/
    │   ├── system.md
    │   └── user.md
    └── ActionStep/
        ├── system.md
        └── user.md
```

---

## Testing Strategy

### Unit Testing Approach

1. **Mock LLM Calls**: Use `unittest.mock.patch` to mock `_get_llm()`
2. **Test State Transitions**: Verify state dict changes through graph
3. **Test Edge Cases**: Empty inputs, max iterations, error conditions
4. **Test Tool Registry**: Mock tool calls for patterns that use tools

### Example Test Structure

```python
def test_pattern_basic():
    agent = MyAgent(llm_configs={}, prompt_dir="prompts")
    with patch.object(agent, "_get_llm", return_value=mock_llm):
        result = agent.run("test input")
        assert result is not None
```

---

## Known Limitations and Future Enhancements

### Current Limitations

1. **No Streaming**: Current implementation doesn't support streaming responses
2. **No Async**: Deliberately excluded for simplicity
3. **Limited Tool Registry**: Basic tool integration, extensible by users
4. **No Persistence**: State not persisted between runs (by design)

### Future Enhancement Ideas

1. **Tool Registry Module**: Comprehensive tool management system
2. **State Persistence**: Optional state saving/loading
3. **Observability Hooks**: Structured logging and tracing
4. **Parallel Execution**: Where patterns support it (without async)
5. **Prompt Versioning**: Version control for prompt templates
6. **Pattern Composition**: Combining patterns hierarchically

---

## Development Environment

### Required Tools

- Python 3.10+
- Virtual environment (venv)
- pip for dependency management
- pytest for testing

### Setup Commands

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
pytest tests/
```

### Environment Variables

Required in .env:
```
OPENAI_API_KEY=your-key-here
THINKING_MODEL_PROVIDER=openai
THINKING_MODEL_NAME=gpt-4-turbo
REFLECTION_MODEL_PROVIDER=openai
REFLECTION_MODEL_NAME=gpt-4-turbo
DOCUMENTATION_MODEL_PROVIDER=openai
DOCUMENTATION_MODEL_NAME=gpt-3.5-turbo
```

---

## Design Pattern Notes

### ReAct Pattern
- Iterative thought → action → observation loop
- Requires tool registry for action execution
- Stop condition: explicit "FINAL ANSWER" marker or max steps

### Plan & Solve Pattern
- Two-phase: planning then execution
- Plan is a list of structured steps
- Execution can be sequential or parallel (future enhancement)

### Reflection Pattern
- Generate → Critique → Refine cycle
- Single refinement pass (can be extended to multiple)
- Uses separate LLM roles for generation and critique

### Reflexion Pattern
- Multiple trial attempts with memory
- Each trial: plan → execute → evaluate → reflect → store
- Memory accumulates across trials within a session

### LLM Compiler Pattern
- Plan execution as DAG
- Topological execution order
- Supports parallel tool execution (conceptually)

### REWOO Pattern
- Separates planning (Worker) from execution (Solver)
- Uses placeholders in plan template
- Cost-efficient: expensive model only for planning and integration

### LATS Pattern
- Tree search over reasoning paths
- Monte Carlo-inspired selection and backpropagation
- Computationally intensive, best for complex problems

### Self-Discovery Pattern
- Dynamic module selection from library
- Adaptation phase customizes modules to task
- Useful when task type varies significantly

### STORM Pattern
- Multi-perspective research and synthesis
- Outline → Perspectives → Questions → Retrieval → Synthesis
- Best for long-form content generation

---

## Common Pitfalls and Solutions

### Pitfall 1: Forgetting State Returns
**Problem:** Node functions must return the state dict
**Solution:** Always `return state` at end of node functions

### Pitfall 2: Async Contamination
**Problem:** Accidentally importing async LangChain components
**Solution:** Review imports, use synchronous variants

### Pitfall 3: Hard-coded Prompts
**Problem:** Prompts embedded in code
**Solution:** Always use `_load_prompt(step_name)`

### Pitfall 4: Missing Type Hints
**Problem:** Unclear parameter and return types
**Solution:** Add type hints to all public and private methods

### Pitfall 5: Infinite Loops
**Problem:** Patterns with loops don't have stop conditions
**Solution:** Always include max_iterations counter and check

---

## Code Review Checklist

Before merging pattern implementations:

- [ ] No async/await keywords anywhere
- [ ] All methods have type hints
- [ ] All public methods have docstrings
- [ ] Prompts externalized to prompts/ directory
- [ ] No hard-coded API keys or model names
- [ ] State keys documented in class docstring
- [ ] Max iterations or stop condition implemented
- [ ] Unit tests exist and pass
- [ ] Example script exists and runs
- [ ] No breaking changes to base classes

---

## Performance Considerations

### LLM Call Optimization
- Minimize number of LLM calls in critical paths
- Use cheaper models for simple tasks
- Cache prompt templates (loaded once)

### State Management
- Keep state dictionaries lean
- Avoid storing large objects in state
- Clean up intermediate results when possible

### Testing Performance
- Mock LLM calls in tests (never call real APIs in tests)
- Keep test execution time under 30 seconds total

---

## Versioning Strategy

### Version Numbers
- Use semantic versioning: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes to base classes or pattern interfaces
- MINOR: New patterns or significant features
- PATCH: Bug fixes, documentation updates

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Git tag created

---

## Questions and Decisions Log

### Q1: Should we support async?
**Decision:** No, synchronous only
**Date:** 2025-10-26
**Rationale:** Simplicity, easier debugging, design document requirement

### Q2: How to handle tool registry?
**Decision:** Defer to pattern implementations, provide example in ReAct
**Date:** 2025-10-26
**Rationale:** Different patterns need different tool capabilities

### Q3: Should prompts be validated?
**Decision:** Basic validation (file exists), not content validation
**Date:** 2025-10-26
**Rationale:** Allow maximum flexibility for prompt experimentation

---

## Contact and Contribution

For questions or suggestions:
- Review Design.md for architectural guidance
- Check task_list.md for current development status
- Follow coding conventions outlined in this document
