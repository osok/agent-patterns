# Changelog

All notable changes to Agent Patterns will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-XX

### Major Rewrite - Breaking Changes

Version 0.2.0 is a complete architectural rewrite of Agent Patterns. The previous 0.1.x version used asyncio extensively, which caused significant reliability issues. Version 0.2.0 eliminates async/await entirely in favor of a synchronous-only architecture.

**This is a breaking change. Code written for v0.1.x will not work with v0.2.0 without modifications.**

### Added

#### Core Features
- **Synchronous Architecture**: Complete elimination of async/await for simplicity and debuggability
- **9 Production-Ready Patterns**: ReAct, Reflection, Plan & Solve, Reflexion, LLM Compiler, REWOO, LATS, Self-Discovery, STORM
- **Three-Layer Prompt Customization System**:
  - File-based prompts from directory structure
  - Custom instructions appended to all system prompts
  - Programmatic prompt overrides for specific steps
- **Lifecycle Hooks**: `on_start()`, `on_finish()`, `on_error()` for monitoring and logging
- **LLM Caching**: Automatic caching of initialized LLM instances
- **Type Hints**: Comprehensive type annotations throughout codebase
- **Multi-Provider Support**: OpenAI and Anthropic providers out of the box

#### Patterns Implemented
- **ReAct** (`ReActAgent`): Reason + Act with tool use
- **Reflection** (`ReflectionAgent`): Generate-Reflect-Refine cycle
- **Plan & Solve** (`PlanAndSolveAgent`): Planning then sequential execution
- **Reflexion** (`ReflexionAgent`): Multi-trial learning with reflection memory
- **LLM Compiler** (`LLMCompilerAgent`): DAG-based parallel tool execution
- **REWOO** (`REWOOAgent`): Planner-Worker-Solver pattern
- **LATS** (`LATSAgent`): Language Agent Tree Search
- **Self-Discovery** (`SelfDiscoveryAgent`): Dynamic reasoning strategy selection
- **STORM** (`STORMAgent`): Multi-perspective research synthesis

#### Documentation
- Comprehensive user documentation in `usr-docs/`
- API reference for all patterns and base classes
- Architecture guide explaining internal design
- Quick start tutorial and examples
- FAQ and troubleshooting guides
- Pattern selection guide

#### Testing
- Unit tests for all patterns
- Test coverage >80%
- Pytest configuration and fixtures
- Mock LLM support for testing

#### Development Tools
- Black code formatting configuration
- Ruff linting configuration
- mypy type checking configuration
- GitHub Actions CI/CD workflows
- Pre-commit hooks

### Changed

#### Breaking Changes
- **No async/await**: All methods are now synchronous
  - **Old**: `async def run()` / `await agent.run()`
  - **New**: `def run()` / `agent.run()`
- **New import paths**: Patterns moved to `agent_patterns.patterns`
  - **Old**: `from agent_patterns import ReActAgent`
  - **New**: `from agent_patterns.patterns import ReActAgent`
- **New configuration format**: `llm_configs` dictionary structure
  ```python
  # Old (v0.1.x)
  agent = ReActAgent(model="gpt-4")

  # New (v0.2.0)
  agent = ReActAgent(
      llm_configs={
          "thinking": {
              "provider": "openai",
              "model_name": "gpt-4-turbo"
          }
      }
  )
  ```
- **Prompt system overhaul**: New three-layer customization system
- **BaseAgent API changes**: New abstract methods and signatures

#### Improvements
- **Reliability**: Synchronous design eliminates async race conditions and complexity
- **Debuggability**: Simple call stacks, easy to trace execution
- **Performance**: Removed async overhead
- **Maintainability**: Cleaner codebase, better separation of concerns

### Removed
- **Async support**: All asyncio code removed
- **Old v0.1.x patterns**: Complete rewrite, not backward compatible
- **Legacy configuration**: Old configuration formats no longer supported

### Fixed
- Async reliability issues that plagued v0.1.x
- Race conditions in multi-step workflows
- Complex debugging challenges
- Inconsistent error handling

### Dependencies
- `langgraph>=0.2.0` - State graph management
- `langchain>=0.3.0` - LLM abstractions
- `langchain-core>=0.3.0` - Core functionality
- `langchain-openai>=0.2.0` - OpenAI integration
- `langchain-anthropic>=0.2.0` - Anthropic integration
- `python-dotenv>=1.0.0` - Environment variable management

### Migration Guide

#### Step 1: Update Imports
```python
# Old
from agent_patterns import ReActAgent, ReflectionAgent

# New
from agent_patterns.patterns import ReActAgent, ReflectionAgent
```

#### Step 2: Remove Async/Await
```python
# Old
async def main():
    agent = ReActAgent(...)
    result = await agent.run(query)

# New
def main():
    agent = ReActAgent(...)
    result = agent.run(query)
```

#### Step 3: Update Configuration
```python
# Old
agent = ReActAgent(
    model="gpt-4",
    api_key="...",
    temperature=0.7
)

# New
agent = ReActAgent(
    llm_configs={
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4-turbo",
            "temperature": 0.7
        }
    }
)
```

#### Step 4: Update Tool Definitions
```python
# Old (async)
async def my_tool(input: str) -> str:
    return await some_async_call(input)

# New (sync)
def my_tool(input: str) -> str:
    return some_sync_call(input)
```

#### Step 5: Test Thoroughly
- Run your test suite
- Verify all functionality works
- Check for any edge cases

### Known Issues
- None at release

### Contributors
- osok (primary developer)

---

## [0.1.0] - 2024-XX-XX (Deprecated)

**Note**: Version 0.1.x is deprecated due to async reliability issues. Please upgrade to 0.2.0.

### Added
- Initial release with async architecture
- Basic ReAct, Reflection, and Plan & Solve patterns
- Async/await throughout

### Known Issues
- Async reliability problems
- Race conditions in workflows
- Difficult debugging
- Complex error handling

**Status**: Deprecated. Do not use for new projects.

---

## Future Releases

### Planned Features

#### v0.3.0 (Target: Q2 2025)
- **Streaming Support**: True streaming for incremental results
- **Multi-Agent Patterns**: Patterns coordinating multiple sub-agents
- **Tool Registry**: Built-in tool library
- **Enhanced Monitoring**: Metrics and observability
- **Pattern Composition**: Combine patterns in workflows
- **LangSmith Integration**: Deep tracing integration

#### v0.4.0 (Target: Q3 2025)
- **Custom Provider Support**: Easy plugin system for new LLM providers
- **Advanced Caching**: Semantic caching for LLM calls
- **Prompt Optimization**: A/B testing framework
- **Pattern Templates**: Pre-built configurations for common use cases
- **Web UI**: Visual workflow builder and monitor

#### Under Consideration
- **Async Option**: Optional async support for those who need it
- **Distributed Execution**: Run patterns across multiple machines
- **Pattern Marketplace**: Share custom patterns with community
- **AutoGen Integration**: Compatibility with Microsoft AutoGen
- **LlamaIndex Integration**: RAG pattern integration

### Backward Compatibility Promise

Starting with v0.2.0, we commit to:
- **Semantic Versioning**: Major.Minor.Patch format
- **No Breaking Changes in Minor Versions**: 0.2.x will remain compatible
- **Deprecation Warnings**: 1 minor version notice before removal
- **Migration Guides**: Clear upgrade paths for major versions
- **LTS Support**: Long-term support for major versions

### Version Support Policy

| Version | Status | Support Until | Notes |
|---------|--------|---------------|-------|
| 0.2.x | Current | TBD | Active development |
| 0.1.x | Deprecated | 2025-03-31 | Security fixes only |

---

## Contributing

See [CONTRIBUTING.md](contributing.md) for guidelines on submitting changes.

## Reporting Issues

Found a bug? [Create an issue](https://github.com/osok/agent-patterns/issues/new)

## Release Notes Distribution

- **GitHub Releases**: Full release notes
- **PyPI**: Version numbers and links
- **Documentation**: This changelog
- **Twitter/X**: Major release announcements

---

**Note**: Dates in "Unreleased" and future versions are tentative and subject to change.
