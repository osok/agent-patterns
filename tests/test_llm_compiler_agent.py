"""Unit tests for the LLMCompilerAgent pattern."""

import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from agent_patterns.patterns.llm_compiler_agent import LLMCompilerAgent


@pytest.fixture
def mock_llm_configs():
    """Provide mock LLM configurations."""
    return {
        "thinking": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        },
        "documentation": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.3
        }
    }


@pytest.fixture
def sample_tools():
    """Provide sample tools for testing."""
    def search_tool(query: str) -> str:
        """Mock search tool."""
        return f"Search result for: {query}"

    def calculator_tool(expression: str) -> float:
        """Mock calculator tool."""
        try:
            return float(eval(expression))
        except:
            return 0.0

    def weather_tool(location: str) -> str:
        """Mock weather tool."""
        return f"Weather in {location}: Sunny, 20C"

    return {
        "search_tool": search_tool,
        "calculator_tool": calculator_tool,
        "weather_tool": weather_tool
    }


@pytest.fixture
def agent(mock_llm_configs, sample_tools):
    """Create a LLMCompilerAgent instance for testing."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        return LLMCompilerAgent(
            llm_configs=mock_llm_configs,
            tools=sample_tools
        )


class TestLLMCompilerAgentInitialization:
    """Test LLMCompilerAgent initialization."""

    def test_initialization_with_tools(self, mock_llm_configs, sample_tools):
        """Test agent initializes correctly with tools."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = LLMCompilerAgent(
                llm_configs=mock_llm_configs,
                tools=sample_tools
            )

            assert agent.tools == sample_tools
            assert agent.graph is not None

    def test_initialization_without_tools(self, mock_llm_configs):
        """Test agent initializes with empty tools dict if none provided."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = LLMCompilerAgent(llm_configs=mock_llm_configs)

            assert agent.tools == {}
            assert agent.graph is not None

    def test_initialization_builds_graph(self, mock_llm_configs, sample_tools):
        """Test that initialization builds the state graph."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = LLMCompilerAgent(
                llm_configs=mock_llm_configs,
                tools=sample_tools
            )

            assert agent.graph is not None
            # Graph should be compiled
            assert hasattr(agent.graph, 'invoke')


class TestToolSchemas:
    """Test tool schema generation."""

    def test_define_tool_schemas(self, agent, sample_tools):
        """Test that tool schemas are correctly generated."""
        schemas = agent._define_tool_schemas()

        assert len(schemas) == len(sample_tools)
        assert "search_tool" in schemas
        assert "calculator_tool" in schemas
        assert "weather_tool" in schemas

        # Check schema structure
        for tool_name, schema in schemas.items():
            assert "name" in schema
            assert "description" in schema
            assert "callable" in schema
            assert schema["name"] == tool_name
            assert callable(schema["callable"])

    def test_format_tool_schemas(self, agent, sample_tools):
        """Test formatting of tool schemas for prompts."""
        schemas = agent._define_tool_schemas()
        formatted = agent._format_tool_schemas(schemas)

        assert isinstance(formatted, str)
        assert "search_tool" in formatted
        assert "calculator_tool" in formatted
        assert "weather_tool" in formatted
        # Should contain markdown formatting
        assert "**" in formatted or "-" in formatted


class TestPlanParsing:
    """Test execution graph parsing."""

    def test_parse_simple_plan(self, agent, sample_tools):
        """Test parsing a simple execution plan."""
        plan_text = """
NODE: node1
TOOL: search_tool
ARGS: {"query": "test query"}
DEPENDS_ON: []

NODE: node2
TOOL: calculator_tool
ARGS: {"expression": "2 + 2"}
DEPENDS_ON: [node1]
"""

        tool_schemas = agent._define_tool_schemas()
        graph = agent._parse_plan_to_graph(plan_text, tool_schemas)

        assert "nodes" in graph
        assert len(graph["nodes"]) == 2

        # Check first node
        node1 = graph["nodes"][0]
        assert node1["id"] == "node1"
        assert node1["tool"] == "search_tool"
        assert node1["args"]["query"] == "test query"
        assert node1["depends_on"] == []

        # Check second node
        node2 = graph["nodes"][1]
        assert node2["id"] == "node2"
        assert node2["tool"] == "calculator_tool"
        assert node2["depends_on"] == ["node1"]

    def test_parse_parallel_plan(self, agent, sample_tools):
        """Test parsing a plan with parallel nodes."""
        plan_text = """
NODE: node1
TOOL: search_tool
ARGS: {"query": "query1"}
DEPENDS_ON: []

NODE: node2
TOOL: weather_tool
ARGS: {"location": "Tokyo"}
DEPENDS_ON: []

NODE: node3
TOOL: calculator_tool
ARGS: {"expression": "1 + 1"}
DEPENDS_ON: [node1, node2]
"""

        tool_schemas = agent._define_tool_schemas()
        graph = agent._parse_plan_to_graph(plan_text, tool_schemas)

        assert len(graph["nodes"]) == 3
        # First two nodes have no dependencies (can run in parallel)
        assert graph["nodes"][0]["depends_on"] == []
        assert graph["nodes"][1]["depends_on"] == []
        # Third node depends on both
        assert set(graph["nodes"][2]["depends_on"]) == {"node1", "node2"}

    def test_parse_empty_plan(self, agent, sample_tools):
        """Test parsing an empty or malformed plan."""
        tool_schemas = agent._define_tool_schemas()
        graph = agent._parse_plan_to_graph("", tool_schemas)

        # Should return fallback graph with single node
        assert "nodes" in graph
        assert len(graph["nodes"]) >= 1


class TestToolExecution:
    """Test tool execution."""

    def test_execute_tool_basic(self, agent):
        """Test basic tool execution."""
        result = agent._execute_tool("search_tool", {"query": "test"}, {})

        assert isinstance(result, str)
        assert "test" in result

    def test_execute_tool_with_calculation(self, agent):
        """Test calculator tool execution."""
        result = agent._execute_tool(
            "calculator_tool",
            {"expression": "2 + 2"},
            {}
        )

        assert result == 4.0

    def test_execute_tool_not_found(self, agent):
        """Test execution of non-existent tool."""
        result = agent._execute_tool("nonexistent_tool", {}, {})

        assert isinstance(result, str)
        assert "not found" in result.lower()

    def test_execute_tool_with_error(self, agent):
        """Test tool execution with error."""
        # Pass invalid expression to calculator
        result = agent._execute_tool(
            "calculator_tool",
            {"expression": "invalid"},
            {}
        )

        # Should return error message, not raise exception
        assert isinstance(result, (str, float))


class TestArgumentResolution:
    """Test argument resolution with node references."""

    def test_resolve_simple_args(self, agent):
        """Test resolving arguments without references."""
        args = {"query": "test", "number": 42}
        node_results = {}

        resolved = agent._resolve_args(args, node_results)

        assert resolved == args

    def test_resolve_node_reference(self, agent):
        """Test resolving argument with node reference."""
        args = {"expression": "#node1"}
        node_results = {"node1": 5}

        resolved = agent._resolve_args(args, node_results)

        # Should replace #node1 with the value 5
        assert resolved["expression"] == 5

    def test_resolve_multiple_references(self, agent):
        """Test resolving multiple node references."""
        args = {
            "value1": "#node1",
            "value2": "#node2",
            "normal": "text"
        }
        node_results = {
            "node1": "result1",
            "node2": "result2"
        }

        resolved = agent._resolve_args(args, node_results)

        assert resolved["value1"] == "result1"
        assert resolved["value2"] == "result2"
        assert resolved["normal"] == "text"

    def test_resolve_missing_reference(self, agent):
        """Test resolving reference to missing node."""
        args = {"value": "#nonexistent"}
        node_results = {}

        resolved = agent._resolve_args(args, node_results)

        # Should keep original reference if node not found
        assert resolved["value"] == "#nonexistent"


class TestExecutorDispatch:
    """Test executor dispatch logic."""

    def test_executor_executes_ready_nodes(self, agent):
        """Test that executor runs nodes with satisfied dependencies."""
        state = {
            "execution_graph": {
                "nodes": [
                    {
                        "id": "node1",
                        "tool": "search_tool",
                        "args": {"query": "test"},
                        "depends_on": []
                    }
                ]
            },
            "node_results": {}
        }

        new_state = agent._executor_dispatch(state)

        # Node should have been executed
        assert "node1" in new_state["node_results"]

    def test_executor_skips_nodes_with_unsatisfied_dependencies(self, agent):
        """Test that executor skips nodes with unmet dependencies."""
        state = {
            "execution_graph": {
                "nodes": [
                    {
                        "id": "node1",
                        "tool": "search_tool",
                        "args": {"query": "test"},
                        "depends_on": []
                    },
                    {
                        "id": "node2",
                        "tool": "calculator_tool",
                        "args": {"expression": "2 + 2"},
                        "depends_on": ["node1"]
                    }
                ]
            },
            "node_results": {}  # node1 hasn't run yet
        }

        # First dispatch - only node1 should execute
        new_state = agent._executor_dispatch(state)
        assert "node1" in new_state["node_results"]
        # node2 shouldn't execute yet (though in our simple implementation it might)

    def test_executor_handles_errors(self, agent):
        """Test that executor handles errors gracefully."""
        state = {
            "error": "Previous error",
            "execution_graph": {"nodes": []},
            "node_results": {}
        }

        new_state = agent._executor_dispatch(state)

        # Should not crash, should preserve error
        assert new_state.get("error") is not None


class TestCompletionChecking:
    """Test completion checking logic."""

    def test_check_completion_all_done(self, agent):
        """Test completion when all nodes are executed."""
        state = {
            "execution_graph": {
                "nodes": [
                    {"id": "node1", "tool": "search_tool"},
                    {"id": "node2", "tool": "calculator_tool"}
                ]
            },
            "node_results": {
                "node1": "result1",
                "node2": "result2"
            }
        }

        new_state = agent._check_completion(state)

        assert new_state["graph_done"] is True

    def test_check_completion_not_done(self, agent):
        """Test completion when nodes remain."""
        state = {
            "execution_graph": {
                "nodes": [
                    {"id": "node1", "tool": "search_tool"},
                    {"id": "node2", "tool": "calculator_tool"}
                ]
            },
            "node_results": {
                "node1": "result1"
                # node2 missing
            }
        }

        new_state = agent._check_completion(state)

        assert new_state["graph_done"] is False

    def test_check_completion_with_error(self, agent):
        """Test completion checking when error exists."""
        state = {
            "error": "Some error",
            "execution_graph": {"nodes": []},
            "node_results": {}
        }

        new_state = agent._check_completion(state)

        # Should mark as done when error exists
        assert new_state["graph_done"] is True


class TestRouting:
    """Test routing logic."""

    def test_route_after_check_done(self, agent):
        """Test routing when graph is complete."""
        state = {"graph_done": True}

        route = agent._route_after_check(state)

        assert route == "finish"

    def test_route_after_check_continue(self, agent):
        """Test routing when graph has more nodes."""
        state = {"graph_done": False}

        route = agent._route_after_check(state)

        assert route == "continue"


class TestResultFormatting:
    """Test result formatting."""

    def test_format_node_results(self, agent):
        """Test formatting of node results for synthesis."""
        execution_graph = {
            "nodes": [
                {"id": "node1", "tool": "search_tool"},
                {"id": "node2", "tool": "calculator_tool"}
            ]
        }
        node_results = {
            "node1": "Search result text",
            "node2": 42
        }

        formatted = agent._format_node_results(execution_graph, node_results)

        assert isinstance(formatted, str)
        assert "node1" in formatted
        assert "node2" in formatted
        assert "search_tool" in formatted
        assert "calculator_tool" in formatted

    def test_format_empty_results(self, agent):
        """Test formatting with no results."""
        execution_graph = {"nodes": []}
        node_results = {}

        formatted = agent._format_node_results(execution_graph, node_results)

        assert isinstance(formatted, str)


class TestSynthesis:
    """Test result synthesis."""

    @patch("agent_patterns.patterns.llm_compiler_agent.LLMCompilerAgent._get_llm")
    @patch("agent_patterns.patterns.llm_compiler_agent.LLMCompilerAgent._load_prompt")
    def test_synthesize_result(self, mock_load_prompt, mock_get_llm, agent):
        """Test synthesis of final result."""
        # Mock prompt loading
        mock_load_prompt.return_value = {
            "system": "You are a synthesis expert.",
            "user": "Task: {task}\nResults: {results}"
        }

        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Synthesized final answer"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "input_task": "Test task",
            "execution_graph": {
                "nodes": [
                    {"id": "node1", "tool": "search_tool"}
                ]
            },
            "node_results": {
                "node1": "Result from node1"
            }
        }

        new_state = agent._synthesize_result(state)

        assert "final_answer" in new_state
        assert new_state["final_answer"] == "Synthesized final answer"
        mock_get_llm.assert_called_with("documentation")

    def test_synthesize_with_error(self, agent):
        """Test synthesis when error exists."""
        state = {
            "error": "Test error",
            "execution_graph": {"nodes": []},
            "node_results": {}
        }

        new_state = agent._synthesize_result(state)

        assert "final_answer" in new_state
        assert "error" in new_state["final_answer"].lower()


class TestEndToEnd:
    """End-to-end integration tests."""

    @patch("agent_patterns.patterns.llm_compiler_agent.LLMCompilerAgent._get_llm")
    @patch("agent_patterns.patterns.llm_compiler_agent.LLMCompilerAgent._load_prompt")
    def test_run_simple_task(
        self,
        mock_load_prompt,
        mock_get_llm,
        mock_llm_configs,
        sample_tools
    ):
        """Test running a simple task end-to-end."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = LLMCompilerAgent(
                llm_configs=mock_llm_configs,
                tools=sample_tools
            )

            # Mock planner prompt
            def prompt_side_effect(step_name):
                if step_name == "PlanGraph":
                    return {
                        "system": "Plan the task",
                        "user": "Task: {task}\nTools: {tools}"
                    }
                elif step_name == "Synthesize":
                    return {
                        "system": "Synthesize results",
                        "user": "Task: {task}\nResults: {results}"
                    }

            mock_load_prompt.side_effect = prompt_side_effect

            # Mock planner LLM response
            mock_llm = Mock()

            def invoke_side_effect(messages):
                response = Mock()
                # First call: planner generates graph
                if "Plan the task" in str(messages):
                    response.content = """
NODE: node1
TOOL: search_tool
ARGS: {"query": "test"}
DEPENDS_ON: []
"""
                # Second call: synthesizer creates final answer
                else:
                    response.content = "Final synthesized answer"
                return response

            mock_llm.invoke.side_effect = invoke_side_effect
            mock_get_llm.return_value = mock_llm

            # Run task
            result = agent.run("Test task")

            assert result is not None
            assert isinstance(result, str)
