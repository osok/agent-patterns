"""
Tests for PlanAndSolveAgent.
"""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage

from agent_patterns.patterns.plan_and_solve_agent import PlanAndSolveAgent


@pytest.fixture
def llm_configs():
    """Standard LLM configurations for testing."""
    return {
        "planning": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.7,
        },
        "execution": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.5,
        },
        "documentation": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.3,
        },
    }


def test_plan_and_solve_agent_initialization(llm_configs):
    """Test PlanAndSolveAgent initialization."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    assert agent.llm_configs == llm_configs
    assert agent.graph is not None


def test_plan_and_solve_agent_build_graph_structure(llm_configs):
    """Test that build_graph creates proper structure."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    # Graph should be built
    assert agent.graph is not None


def test_generate_plan(llm_configs):
    """Test _generate_plan method."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    # Mock the LLM
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = """Step 1: Research renewable energy sources
Step 2: Analyze current trends
Step 3: Write conclusion"""
    mock_llm.invoke.return_value = mock_response

    agent._llm_cache["planning"] = mock_llm

    state = {
        "input_task": "Write about renewable energy",
        "plan": None,
    }

    result_state = agent._generate_plan(state)

    assert "plan" in result_state
    assert len(result_state["plan"]) == 3
    assert result_state["current_step_index"] == 0


def test_execute_plan_step(llm_configs):
    """Test _execute_plan_step method."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    # Mock the LLM
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Solar and wind are major renewable energy sources."
    mock_llm.invoke.return_value = mock_response

    agent._llm_cache["execution"] = mock_llm

    state = {
        "input_task": "Write about renewable energy",
        "plan": [
            {"step_number": 1, "description": "Research renewable energy sources"},
            {"step_number": 2, "description": "Analyze trends"},
        ],
        "current_step_index": 0,
        "step_results": [],
    }

    result_state = agent._execute_plan_step(state)

    assert len(result_state["step_results"]) == 1
    assert result_state["current_step_index"] == 1


def test_check_plan_completion_not_done(llm_configs):
    """Test _check_plan_completion when not done."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    state = {
        "plan": [{"step_number": 1}, {"step_number": 2}],
        "current_step_index": 1,
    }

    result_state = agent._check_plan_completion(state)

    assert result_state["plan_done"] is False


def test_check_plan_completion_done(llm_configs):
    """Test _check_plan_completion when done."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    state = {
        "plan": [{"step_number": 1}, {"step_number": 2}],
        "current_step_index": 2,
    }

    result_state = agent._check_plan_completion(state)

    assert result_state["plan_done"] is True


def test_aggregate_results(llm_configs):
    """Test _aggregate_results method."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    # Mock the LLM
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Renewable energy is growing rapidly worldwide."
    mock_llm.invoke.return_value = mock_response

    agent._llm_cache["documentation"] = mock_llm

    state = {
        "input_task": "Write about renewable energy",
        "plan": [
            {"step_number": 1, "description": "Research"},
            {"step_number": 2, "description": "Analyze"},
        ],
        "step_results": [
            "Solar and wind are major sources.",
            "Growth rate is 10% annually.",
        ],
    }

    result_state = agent._aggregate_results(state)

    assert "final_result" in result_state
    assert len(result_state["final_result"]) > 0


def test_run_requires_built_graph(llm_configs):
    """Test that run raises error if graph not built."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)
    agent.graph = None

    with pytest.raises(ValueError, match="Graph has not been built"):
        agent.run("test task")


def test_run_success_flow(llm_configs):
    """Test successful run flow."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    # Mock the graph
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "final_result": "Renewable energy is the future."
    }
    agent.graph = mock_graph

    result = agent.run("Write about renewable energy")

    assert result == "Renewable energy is the future."
    mock_graph.invoke.assert_called_once()


@patch.object(PlanAndSolveAgent, "on_start")
@patch.object(PlanAndSolveAgent, "on_finish")
def test_run_calls_lifecycle_hooks(mock_finish, mock_start, llm_configs):
    """Test that run calls lifecycle hooks."""
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    # Mock the graph
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "final_result": "Result"
    }
    agent.graph = mock_graph

    agent.run("test task")

    mock_start.assert_called_once_with("test task")
    mock_finish.assert_called_once_with("Result")
