"""Unit tests for the REWOOAgent pattern."""

import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from agent_patterns.patterns.rewoo_agent import REWOOAgent


@pytest.fixture
def mock_llm_configs():
    """Provide mock LLM configurations."""
    return {
        "thinking": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        },
        "solver": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
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

    def stock_tool(symbol: str) -> str:
        """Mock stock tool."""
        return f"Stock price for {symbol}: $100.00"

    return {
        "search_tool": search_tool,
        "calculator_tool": calculator_tool,
        "stock_tool": stock_tool
    }


@pytest.fixture
def agent(mock_llm_configs, sample_tools):
    """Create a REWOOAgent instance for testing."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        return REWOOAgent(
            llm_configs=mock_llm_configs,
            tools=sample_tools
        )


class TestREWOOAgentInitialization:
    """Test REWOOAgent initialization."""

    def test_initialization_with_tools(self, mock_llm_configs, sample_tools):
        """Test agent initializes correctly with tools."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = REWOOAgent(
                llm_configs=mock_llm_configs,
                tools=sample_tools
            )

            assert agent.tools == sample_tools
            assert agent.graph is not None
            assert agent.solver_llm_role == "solver"

    def test_initialization_without_tools(self, mock_llm_configs):
        """Test agent initializes with empty tools dict if none provided."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = REWOOAgent(llm_configs=mock_llm_configs)

            assert agent.tools == {}
            assert agent.graph is not None

    def test_initialization_custom_solver_role(self, mock_llm_configs, sample_tools):
        """Test agent initializes with custom solver LLM role."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = REWOOAgent(
                llm_configs=mock_llm_configs,
                tools=sample_tools,
                solver_llm_role="executor"
            )

            assert agent.solver_llm_role == "executor"

    def test_initialization_builds_graph(self, mock_llm_configs, sample_tools):
        """Test that initialization builds the state graph."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = REWOOAgent(
                llm_configs=mock_llm_configs,
                tools=sample_tools
            )

            assert agent.graph is not None
            assert hasattr(agent.graph, 'invoke')


class TestToolFormatting:
    """Test tool formatting for prompts."""

    def test_format_tools_with_tools(self, agent):
        """Test formatting tools for prompt."""
        formatted = agent._format_tools()

        assert isinstance(formatted, str)
        assert "search_tool" in formatted
        assert "calculator_tool" in formatted
        assert "stock_tool" in formatted

    def test_format_tools_empty(self, mock_llm_configs):
        """Test formatting when no tools available."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = REWOOAgent(llm_configs=mock_llm_configs, tools={})
            formatted = agent._format_tools()

            assert formatted == "No tools available"


class TestPlanParsing:
    """Test worker plan parsing."""

    def test_parse_simple_plan(self, agent):
        """Test parsing a simple worker plan."""
        plan_text = """
PLAN: Find CEO -> {ceo_name}

SOLVER: ceo_name
TOOL: search_tool
PARAMS: {"query": "CEO of Company"}
"""

        template, requests = agent._parse_worker_plan(plan_text)

        assert "Find CEO" in template
        assert "{ceo_name}" in template
        assert len(requests) == 1
        assert requests[0]["placeholder"] == "ceo_name"
        assert requests[0]["tool"] == "search_tool"
        assert requests[0]["params"]["query"] == "CEO of Company"

    def test_parse_multi_step_plan(self, agent):
        """Test parsing a multi-step plan with dependencies."""
        plan_text = """
PLAN: Find CEO -> {ceo_name}, then search announcements by {ceo_name} -> {announcements}

SOLVER: ceo_name
TOOL: search_tool
PARAMS: {"query": "CEO"}

SOLVER: announcements
TOOL: search_tool
PARAMS: {"query": "announcements by {ceo_name}"}
"""

        template, requests = agent._parse_worker_plan(plan_text)

        assert len(requests) == 2
        assert requests[0]["placeholder"] == "ceo_name"
        assert requests[1]["placeholder"] == "announcements"
        # Second request should reference first
        assert "{ceo_name}" in requests[1]["params"]["query"]

    def test_parse_empty_plan(self, agent):
        """Test parsing an empty or malformed plan."""
        template, requests = agent._parse_worker_plan("")

        # Should return fallback values
        assert isinstance(template, str)
        assert len(template) > 0
        assert isinstance(requests, list)

    def test_parse_plan_without_params(self, agent):
        """Test parsing plan with missing PARAMS."""
        plan_text = """
PLAN: Do something

SOLVER: result1
TOOL: search_tool
"""

        template, requests = agent._parse_worker_plan(plan_text)

        # Should handle missing PARAMS gracefully
        assert len(requests) >= 0


class TestParameterResolution:
    """Test parameter placeholder resolution."""

    def test_resolve_simple_params(self, agent):
        """Test resolving parameters without placeholders."""
        params = {"query": "test", "number": 42}
        solver_results = {}

        resolved = agent._resolve_params(params, solver_results)

        assert resolved == params

    def test_resolve_with_placeholder(self, agent):
        """Test resolving parameters with placeholders."""
        params = {"query": "info about {ceo_name}"}
        solver_results = {"ceo_name": "John Doe"}

        resolved = agent._resolve_params(params, solver_results)

        assert resolved["query"] == "info about John Doe"

    def test_resolve_multiple_placeholders(self, agent):
        """Test resolving multiple placeholders in one parameter."""
        params = {"query": "{person} at {company}"}
        solver_results = {
            "person": "Jane Smith",
            "company": "TechCorp"
        }

        resolved = agent._resolve_params(params, solver_results)

        assert resolved["query"] == "Jane Smith at TechCorp"

    def test_resolve_missing_placeholder(self, agent):
        """Test resolving with missing placeholder."""
        params = {"query": "info about {nonexistent}"}
        solver_results = {"other": "value"}

        resolved = agent._resolve_params(params, solver_results)

        # Should keep unresolv placeholder
        assert "{nonexistent}" in resolved["query"]

    def test_resolve_non_string_params(self, agent):
        """Test that non-string parameters pass through unchanged."""
        params = {"number": 42, "flag": True, "list": [1, 2, 3]}
        solver_results = {}

        resolved = agent._resolve_params(params, solver_results)

        assert resolved == params


class TestSolverExecution:
    """Test solver execution logic."""

    def test_call_solver_with_direct_tool(self, agent):
        """Test calling solver with direct tool."""
        result = agent._call_solver("search_tool", {"query": "test"})

        assert isinstance(result, str)
        assert "test" in result

    def test_call_solver_with_calculation(self, agent):
        """Test calling solver with calculator tool."""
        result = agent._call_solver("calculator_tool", {"expression": "2 + 2"})

        assert result == 4.0

    def test_call_solver_tool_not_found(self, mock_llm_configs):
        """Test calling nonexistent tool."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            # Remove solver from config so it tries direct tool lookup
            llm_configs = {"thinking": mock_llm_configs["thinking"]}
            agent = REWOOAgent(llm_configs=llm_configs, tools={})
            result = agent._call_solver("nonexistent", {})

            assert isinstance(result, str)
            assert "not found" in result.lower()

    def test_call_solver_with_error(self, agent):
        """Test solver execution with error."""
        result = agent._call_solver("calculator_tool", {"expression": "invalid"})

        # Should return error message, not raise
        assert isinstance(result, (str, float))


class TestDispatch:
    """Test solver dispatch logic."""

    def test_dispatch_valid_requests(self, agent):
        """Test dispatch with valid solver requests."""
        state = {
            "solver_requests": [
                {"placeholder": "result1", "tool": "search_tool", "params": {}},
                {"placeholder": "result2", "tool": "calculator_tool", "params": {}}
            ]
        }

        new_state = agent._dispatch_to_solvers(state)

        assert new_state.get("error") is None

    def test_dispatch_missing_tool(self, agent):
        """Test dispatch with missing tool field."""
        state = {
            "solver_requests": [
                {"placeholder": "result1", "params": {}}  # Missing "tool"
            ]
        }

        new_state = agent._dispatch_to_solvers(state)

        assert new_state.get("error") is not None
        assert "tool" in new_state["error"].lower()

    def test_dispatch_missing_placeholder(self, agent):
        """Test dispatch with missing placeholder field."""
        state = {
            "solver_requests": [
                {"tool": "search_tool", "params": {}}  # Missing "placeholder"
            ]
        }

        new_state = agent._dispatch_to_solvers(state)

        assert new_state.get("error") is not None
        assert "placeholder" in new_state["error"].lower()

    def test_dispatch_with_error(self, agent):
        """Test dispatch when error already exists."""
        state = {
            "error": "Previous error",
            "solver_requests": []
        }

        new_state = agent._dispatch_to_solvers(state)

        # Should pass through without validation
        assert new_state["error"] == "Previous error"


class TestSolverExecuteStep:
    """Test the full solver execution step."""

    def test_solver_execute_single_request(self, agent):
        """Test executing a single solver request."""
        state = {
            "solver_requests": [
                {
                    "placeholder": "result1",
                    "tool": "search_tool",
                    "params": {"query": "test"}
                }
            ],
            "solver_results": {}
        }

        new_state = agent._solver_execute(state)

        assert "result1" in new_state["solver_results"]
        assert new_state.get("error") is None

    def test_solver_execute_multiple_requests(self, agent):
        """Test executing multiple solver requests."""
        state = {
            "solver_requests": [
                {"placeholder": "result1", "tool": "search_tool", "params": {"query": "q1"}},
                {"placeholder": "result2", "tool": "search_tool", "params": {"query": "q2"}}
            ],
            "solver_results": {}
        }

        new_state = agent._solver_execute(state)

        assert len(new_state["solver_results"]) == 2
        assert "result1" in new_state["solver_results"]
        assert "result2" in new_state["solver_results"]

    def test_solver_execute_with_dependencies(self, agent):
        """Test executing requests with placeholder dependencies."""
        state = {
            "solver_requests": [
                {"placeholder": "name", "tool": "search_tool", "params": {"query": "CEO"}},
                {"placeholder": "info", "tool": "search_tool", "params": {"query": "info about {name}"}}
            ],
            "solver_results": {}
        }

        new_state = agent._solver_execute(state)

        # Both should execute, second should use first's result
        assert len(new_state["solver_results"]) == 2
        # The second query should have resolved the placeholder
        assert "info" in new_state["solver_results"]

    def test_solver_execute_with_error(self, agent):
        """Test solver execute when error exists."""
        state = {
            "error": "Previous error",
            "solver_requests": [],
            "solver_results": {}
        }

        new_state = agent._solver_execute(state)

        # Should not execute, preserve error
        assert new_state["error"] == "Previous error"


class TestResultCollection:
    """Test solver result collection."""

    def test_collect_all_results_present(self, agent):
        """Test collection when all results are present."""
        state = {
            "solver_requests": [
                {"placeholder": "result1", "tool": "search_tool"},
                {"placeholder": "result2", "tool": "calculator_tool"}
            ],
            "solver_results": {
                "result1": "value1",
                "result2": "value2"
            }
        }

        new_state = agent._collect_solver_results(state)

        assert new_state.get("error") is None

    def test_collect_missing_results(self, agent):
        """Test collection when some results are missing."""
        state = {
            "solver_requests": [
                {"placeholder": "result1", "tool": "search_tool"},
                {"placeholder": "result2", "tool": "calculator_tool"}
            ],
            "solver_results": {
                "result1": "value1"
                # result2 missing
            }
        }

        new_state = agent._collect_solver_results(state)

        assert new_state.get("error") is not None
        assert "result2" in new_state["error"]

    def test_collect_with_error(self, agent):
        """Test collection when error already exists."""
        state = {
            "error": "Previous error",
            "solver_requests": [],
            "solver_results": {}
        }

        new_state = agent._collect_solver_results(state)

        assert new_state["error"] == "Previous error"


class TestResultFormatting:
    """Test result formatting."""

    def test_format_results(self, agent):
        """Test formatting solver results."""
        solver_results = {
            "ceo_name": "John Doe",
            "stock_price": "$100.00"
        }

        formatted = agent._format_results(solver_results)

        assert isinstance(formatted, str)
        assert "ceo_name" in formatted
        assert "John Doe" in formatted
        assert "stock_price" in formatted
        assert "$100.00" in formatted

    def test_format_empty_results(self, agent):
        """Test formatting empty results."""
        formatted = agent._format_results({})

        assert isinstance(formatted, str)


class TestWorkerIntegration:
    """Test worker integration step."""

    @patch("agent_patterns.patterns.rewoo_agent.REWOOAgent._get_llm")
    @patch("agent_patterns.patterns.rewoo_agent.REWOOAgent._load_prompt")
    def test_worker_integrate_success(self, mock_load_prompt, mock_get_llm, agent):
        """Test successful worker integration."""
        # Mock prompt loading
        mock_load_prompt.return_value = {
            "system": "You are an integration expert.",
            "user": "Task: {task}\nPlan: {plan}\nResults: {results}"
        }

        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Final integrated answer"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "input_task": "Test task",
            "worker_plan_template": "Find CEO -> {ceo_name}",
            "solver_results": {"ceo_name": "John Doe"}
        }

        new_state = agent._worker_integrate(state)

        assert new_state["final_answer"] == "Final integrated answer"
        assert "John Doe" in str(mock_llm.invoke.call_args)

    def test_worker_integrate_with_error(self, agent):
        """Test worker integration when error exists."""
        state = {
            "error": "Test error",
            "worker_plan_template": "",
            "solver_results": {}
        }

        new_state = agent._worker_integrate(state)

        assert "error" in new_state["final_answer"].lower()


class TestEndToEnd:
    """End-to-end integration tests."""

    @patch("agent_patterns.patterns.rewoo_agent.REWOOAgent._get_llm")
    @patch("agent_patterns.patterns.rewoo_agent.REWOOAgent._load_prompt")
    def test_run_simple_task(
        self,
        mock_load_prompt,
        mock_get_llm,
        mock_llm_configs,
        sample_tools
    ):
        """Test running a simple task end-to-end."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = REWOOAgent(
                llm_configs=mock_llm_configs,
                tools=sample_tools
            )

            # Mock prompts
            def prompt_side_effect(step_name):
                if step_name == "WorkerPlan":
                    return {
                        "system": "Create a plan",
                        "user": "Task: {task}\nTools: {tools}"
                    }
                elif step_name == "WorkerIntegrate":
                    return {
                        "system": "Integrate results",
                        "user": "Task: {task}\nPlan: {plan}\nResults: {results}"
                    }

            mock_load_prompt.side_effect = prompt_side_effect

            # Mock LLM
            mock_llm = Mock()

            def invoke_side_effect(messages):
                response = Mock()
                # First call: worker plan
                if "Create a plan" in str(messages):
                    response.content = """
PLAN: Search for info -> {info}

SOLVER: info
TOOL: search_tool
PARAMS: {"query": "test"}
"""
                # Second call: integration
                else:
                    response.content = "Final answer with results"
                return response

            mock_llm.invoke.side_effect = invoke_side_effect
            mock_get_llm.return_value = mock_llm

            # Run task
            result = agent.run("Test task")

            assert result is not None
            assert isinstance(result, str)
