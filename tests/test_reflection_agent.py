"""
Unit tests for the ReflectionAgent class.
"""

from unittest.mock import MagicMock, patch

import pytest

from agent_patterns.patterns import ReflectionAgent


@pytest.fixture
def llm_configs():
    """Fixture for LLM configurations."""
    return {
        "documentation": {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
        },
        "reflection": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.5,
        },
    }


def test_reflection_agent_initialization(llm_configs):
    """Test ReflectionAgent initialization."""
    agent = ReflectionAgent(
        llm_configs=llm_configs, max_reflection_cycles=2
    )

    assert agent.max_reflection_cycles == 2
    assert agent.graph is not None


def test_reflection_agent_default_max_cycles(llm_configs):
    """Test default max_reflection_cycles."""
    agent = ReflectionAgent(llm_configs=llm_configs)

    assert agent.max_reflection_cycles == 1


def test_reflection_agent_build_graph_structure(llm_configs):
    """Test that build_graph creates correct graph structure."""
    agent = ReflectionAgent(llm_configs=llm_configs)

    assert agent.graph is not None


def test_check_refinement_needed_negative_indicators():
    """Test refinement check with negative indicators."""
    agent = ReflectionAgent(llm_configs={})

    state = {
        "reflection": "The response is incomplete and missing important details. It could be improved."
    }

    result_state = agent._check_refinement_needed(state)

    assert result_state["needs_refinement"] is True


def test_check_refinement_needed_positive_indicators():
    """Test refinement check with positive indicators."""
    agent = ReflectionAgent(llm_configs={})

    state = {
        "reflection": "This response is excellent and comprehensive. The answer is thorough and accurate."
    }

    result_state = agent._check_refinement_needed(state)

    assert result_state["needs_refinement"] is False


def test_check_refinement_needed_mixed_indicators():
    """Test refinement check with mixed indicators."""
    agent = ReflectionAgent(llm_configs={})

    # More negative than positive
    state = {
        "reflection": "The response is good but incomplete and could be improved with more details."
    }

    result_state = agent._check_refinement_needed(state)

    assert result_state["needs_refinement"] is True


def test_check_refinement_needed_empty_reflection():
    """Test refinement check with empty reflection."""
    agent = ReflectionAgent(llm_configs={})

    state = {"reflection": ""}

    result_state = agent._check_refinement_needed(state)

    # With no indicators, defaults to False (no refinement needed)
    assert result_state["needs_refinement"] is False


def test_check_cycle_limit_not_reached():
    """Test cycle limit check when not reached."""
    agent = ReflectionAgent(llm_configs={})

    state = {
        "reflection_cycle": 1,
        "max_reflection_cycles": 3,
    }

    result_state = agent._check_cycle_limit(state)

    assert result_state["continue_reflection"] is True


def test_check_cycle_limit_reached():
    """Test cycle limit check when reached."""
    agent = ReflectionAgent(llm_configs={})

    state = {
        "reflection_cycle": 3,
        "max_reflection_cycles": 3,
    }

    result_state = agent._check_cycle_limit(state)

    assert result_state["continue_reflection"] is False


def test_check_cycle_limit_exceeded():
    """Test cycle limit check when exceeded."""
    agent = ReflectionAgent(llm_configs={})

    state = {
        "reflection_cycle": 5,
        "max_reflection_cycles": 3,
    }

    result_state = agent._check_cycle_limit(state)

    assert result_state["continue_reflection"] is False


@patch("agent_patterns.patterns.reflection_agent.SystemMessage")
@patch("agent_patterns.patterns.reflection_agent.HumanMessage")
@patch.object(ReflectionAgent, "_get_llm")
@patch.object(ReflectionAgent, "_load_prompt")
def test_generate_initial_output(mock_load, mock_get_llm, mock_human, mock_system, llm_configs):
    """Test generating initial output."""
    # Setup mocks
    mock_load.return_value = {
        "system_prompt": "System prompt",
        "user_prompt": "Task: {task}\nRespond.",
    }

    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Generated initial output"
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    agent = ReflectionAgent(llm_configs=llm_configs)

    state = {"input_task": "Write a story"}

    result_state = agent._generate_initial_output(state)

    assert result_state["initial_output"] == "Generated initial output"
    mock_get_llm.assert_called_with("documentation")
    mock_load.assert_called_with("Generate")


@patch("agent_patterns.patterns.reflection_agent.SystemMessage")
@patch("agent_patterns.patterns.reflection_agent.HumanMessage")
@patch.object(ReflectionAgent, "_get_llm")
@patch.object(ReflectionAgent, "_load_prompt")
def test_reflect_on_output(mock_load, mock_get_llm, mock_human, mock_system, llm_configs):
    """Test reflecting on output."""
    # Setup mocks
    mock_load.return_value = {
        "system_prompt": "Critique system prompt",
        "user_prompt": "Task: {task}\nOutput: {output}\nCritique.",
    }

    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Critical feedback here"
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    agent = ReflectionAgent(llm_configs=llm_configs)

    state = {
        "input_task": "Write a story",
        "initial_output": "Once upon a time...",
        "reflection_cycle": 0,
    }

    result_state = agent._reflect_on_output(state)

    assert result_state["reflection"] == "Critical feedback here"
    assert result_state["reflection_cycle"] == 1
    mock_get_llm.assert_called_with("reflection")
    mock_load.assert_called_with("Reflect")


@patch("agent_patterns.patterns.reflection_agent.SystemMessage")
@patch("agent_patterns.patterns.reflection_agent.HumanMessage")
@patch.object(ReflectionAgent, "_get_llm")
@patch.object(ReflectionAgent, "_load_prompt")
def test_reflect_on_refined_output(mock_load, mock_get_llm, mock_human, mock_system, llm_configs):
    """Test reflecting on refined output in subsequent cycles."""
    # Setup mocks
    mock_load.return_value = {
        "system_prompt": "Critique system prompt",
        "user_prompt": "Task: {task}\nOutput: {output}\nCritique.",
    }

    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Second critique"
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    agent = ReflectionAgent(llm_configs=llm_configs)

    state = {
        "input_task": "Write a story",
        "initial_output": "Once upon a time...",
        "refined_output": "Once upon a time, in a land far away...",
        "reflection_cycle": 1,
    }

    result_state = agent._reflect_on_output(state)

    # Should reflect on refined output, not initial
    assert result_state["reflection"] == "Second critique"
    assert result_state["reflection_cycle"] == 2


@patch("agent_patterns.patterns.reflection_agent.SystemMessage")
@patch("agent_patterns.patterns.reflection_agent.HumanMessage")
@patch.object(ReflectionAgent, "_get_llm")
@patch.object(ReflectionAgent, "_load_prompt")
def test_refine_output(mock_load, mock_get_llm, mock_human, mock_system, llm_configs):
    """Test refining output."""
    # Setup mocks
    mock_load.return_value = {
        "system_prompt": "Refine system prompt",
        "user_prompt": "Task: {task}\nOutput: {output}\nCritique: {reflection}\nRefine.",
    }

    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Refined output with improvements"
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    agent = ReflectionAgent(llm_configs=llm_configs)

    state = {
        "input_task": "Write a story",
        "initial_output": "Once upon a time...",
        "reflection": "Add more details",
    }

    result_state = agent._refine_output(state)

    assert result_state["refined_output"] == "Refined output with improvements"
    assert result_state["final_answer"] == "Refined output with improvements"
    mock_get_llm.assert_called_with("documentation")
    mock_load.assert_called_with("Refine")


def test_run_requires_built_graph(llm_configs):
    """Test that run raises error if graph not built."""
    agent = ReflectionAgent(llm_configs=llm_configs)
    agent.graph = None

    with pytest.raises(ValueError, match="Graph has not been built"):
        agent.run("test input")


@patch.object(ReflectionAgent, "_generate_initial_output")
@patch.object(ReflectionAgent, "_reflect_on_output")
@patch.object(ReflectionAgent, "_check_refinement_needed")
@patch.object(ReflectionAgent, "_refine_output")
@patch.object(ReflectionAgent, "_check_cycle_limit")
def test_run_success_no_refinement(
    mock_cycle,
    mock_refine,
    mock_check,
    mock_reflect,
    mock_generate,
    llm_configs,
):
    """Test successful run without needing refinement."""
    # Configure mocks for no refinement path
    mock_generate.return_value = {"initial_output": "Great output"}
    mock_reflect.return_value = {"reflection": "Excellent work"}
    mock_check.return_value = {"needs_refinement": False}

    agent = ReflectionAgent(llm_configs=llm_configs)

    # Mock the graph
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "initial_output": "Great output",
        "refined_output": None,
        "final_answer": None,
    }
    agent.graph = mock_graph

    result = agent.run("test task")

    # Should return initial output since no refinement
    assert result == "Great output"


@patch.object(ReflectionAgent, "_generate_initial_output")
@patch.object(ReflectionAgent, "_reflect_on_output")
@patch.object(ReflectionAgent, "_check_refinement_needed")
@patch.object(ReflectionAgent, "_refine_output")
def test_run_success_with_refinement(
    mock_refine,
    mock_check,
    mock_reflect,
    mock_generate,
    llm_configs,
):
    """Test successful run with refinement."""
    # Configure mocks for refinement path
    mock_generate.return_value = {"initial_output": "Initial output"}
    mock_reflect.return_value = {"reflection": "Needs improvement"}
    mock_check.return_value = {"needs_refinement": True}
    mock_refine.return_value = {
        "refined_output": "Improved output",
        "final_answer": "Improved output",
    }

    agent = ReflectionAgent(llm_configs=llm_configs)

    # Mock the graph
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "initial_output": "Initial output",
        "refined_output": "Improved output",
        "final_answer": "Improved output",
    }
    agent.graph = mock_graph

    result = agent.run("test task")

    assert result == "Improved output"


def test_run_fallback_to_initial(llm_configs):
    """Test run falls back to initial output if no final answer set."""
    agent = ReflectionAgent(llm_configs=llm_configs)

    # Mock the graph to return state without final_answer or refined_output
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "initial_output": "Fallback output",
        "refined_output": None,
        "final_answer": None,
    }
    agent.graph = mock_graph

    result = agent.run("test task")

    assert result == "Fallback output"


def test_run_fallback_to_default_message(llm_configs):
    """Test run fallback when no output at all."""
    agent = ReflectionAgent(llm_configs=llm_configs)

    # Mock the graph to return empty state
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "initial_output": None,
        "refined_output": None,
        "final_answer": None,
    }
    agent.graph = mock_graph

    result = agent.run("test task")

    assert result == "No output generated"


@patch.object(ReflectionAgent, "on_start")
@patch.object(ReflectionAgent, "on_finish")
def test_run_calls_lifecycle_hooks(mock_finish, mock_start, llm_configs):
    """Test that run calls lifecycle hooks."""
    agent = ReflectionAgent(llm_configs=llm_configs)

    # Mock the graph
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"final_answer": "Result"}
    agent.graph = mock_graph

    agent.run("test input")

    mock_start.assert_called_once_with("test input")
    mock_finish.assert_called_once_with("Result")


@patch.object(ReflectionAgent, "on_error")
def test_run_calls_error_hook_on_exception(mock_error, llm_configs):
    """Test that run calls on_error hook when exception occurs."""
    agent = ReflectionAgent(llm_configs=llm_configs)

    # Mock the graph to raise an exception
    mock_graph = MagicMock()
    test_exception = ValueError("Test error")
    mock_graph.invoke.side_effect = test_exception
    agent.graph = mock_graph

    with pytest.raises(ValueError):
        agent.run("test input")

    mock_error.assert_called_once()
