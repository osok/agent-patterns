"""
Comprehensive tests for ReflexionAgent - matching actual implementation.
"""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage

from agent_patterns.patterns.reflexion_agent import ReflexionAgent


@pytest.fixture
def llm_configs():
    """Standard LLM configurations for testing."""
    return {
        "thinking": {"provider": "openai", "model_name": "gpt-4", "temperature": 0.7},
        "execution": {"provider": "openai", "model_name": "gpt-3.5-turbo", "temperature": 0.5},
        "reflection": {"provider": "openai", "model_name": "gpt-4", "temperature": 0.3},
        "documentation": {"provider": "openai", "model_name": "gpt-3.5-turbo", "temperature": 0.5},
    }


class TestReflexionAgentInitialization:
    """Tests for ReflexionAgent initialization."""

    def test_initialization_with_custom_max_trials(self, llm_configs):
        """Test initialization with custom max_trials."""
        agent = ReflexionAgent(llm_configs=llm_configs, max_trials=5)
        assert agent.max_trials == 5
        assert agent.graph is not None

    def test_initialization_default_max_trials(self, llm_configs):
        """Test default max_trials value."""
        agent = ReflexionAgent(llm_configs=llm_configs)
        assert agent.max_trials == 3

    def test_build_graph_structure(self, llm_configs):
        """Test that build_graph creates proper structure."""
        agent = ReflexionAgent(llm_configs=llm_configs)
        assert agent.graph is not None


class TestPlanActionWithMemory:
    """Tests for _plan_action_with_memory method."""

    def test_plan_increments_trial_count(self, llm_configs):
        """Test that trial_count is incremented."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Try new approach X"
        mock_llm.invoke.return_value = mock_response
        agent._llm_cache["thinking"] = mock_llm

        state = {
            "input_task": "Solve puzzle",
            "reflection_memory": [],
            "trial_count": 0,
            "max_trials": 3,
        }

        result = agent._plan_action_with_memory(state)
        assert result["trial_count"] == 1
        assert "current_plan" in result

    def test_plan_with_memory(self, llm_configs):
        """Test planning with existing reflection memory."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Based on previous failures, try Y"
        mock_llm.invoke.return_value = mock_response
        agent._llm_cache["thinking"] = mock_llm

        state = {
            "input_task": "Solve puzzle",
            "reflection_memory": ["Trial 1: Failed because X"],
            "trial_count": 1,
            "max_trials": 3,
        }

        result = agent._plan_action_with_memory(state)
        assert "current_plan" in result
        assert len(result["current_plan"]) > 0


class TestExecuteAction:
    """Tests for _execute_action method."""

    def test_execute_action_basic(self, llm_configs):
        """Test basic action execution."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "My solution attempt"
        mock_llm.invoke.return_value = mock_response
        agent._llm_cache["execution"] = mock_llm

        state = {
            "input_task": "Solve puzzle",
            "current_plan": "Try approach X",
        }

        result = agent._execute_action(state)
        assert "outcome" in result
        assert result["outcome"] == "My solution attempt"


class TestEvaluateOutcome:
    """Tests for _evaluate_outcome method."""

    def test_evaluate_success(self, llm_configs):
        """Test evaluation marking success."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "SUCCESS: This solution is correct and complete."
        mock_llm.invoke.return_value = mock_response
        agent._llm_cache["reflection"] = mock_llm

        state = {
            "input_task": "Solve puzzle",
            "outcome": "Answer: 42",
        }

        result = agent._evaluate_outcome(state)
        assert result["evaluation"] == "success"

    def test_evaluate_failure(self, llm_configs):
        """Test evaluation marking failure."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "FAILURE: This approach doesn't work."
        mock_llm.invoke.return_value = mock_response
        agent._llm_cache["reflection"] = mock_llm

        state = {
            "input_task": "Solve puzzle",
            "outcome": "Wrong answer",
        }

        result = agent._evaluate_outcome(state)
        assert result["evaluation"] == "failure"


class TestReflectOnTrial:
    """Tests for _reflect_on_trial method."""

    def test_reflect_on_trial(self, llm_configs):
        """Test reflection generation."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "The approach failed because we didn't consider X"
        mock_llm.invoke.return_value = mock_response
        agent._llm_cache["reflection"] = mock_llm

        state = {
            "input_task": "Solve puzzle",
            "current_plan": "Try X",
            "outcome": "Failed",
            "evaluation": "failure",
        }

        result = agent._reflect_on_trial(state)
        assert "trial_reflection" in result
        assert len(result["trial_reflection"]) > 0


class TestUpdateReflectionMemory:
    """Tests for _update_reflection_memory method."""

    def test_update_memory_adds_reflection(self, llm_configs):
        """Test that reflection is added to memory."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        state = {
            "reflection_memory": [],
            "trial_reflection": "Learned lesson X",
            "trial_count": 1,
        }

        result = agent._update_reflection_memory(state)
        assert len(result["reflection_memory"]) == 1
        assert "Trial 1" in result["reflection_memory"][0]

    def test_update_memory_accumulates(self, llm_configs):
        """Test that memory accumulates over trials."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        state = {
            "reflection_memory": ["Trial 1: Old lesson"],
            "trial_reflection": "New lesson",
            "trial_count": 2,
        }

        result = agent._update_reflection_memory(state)
        assert len(result["reflection_memory"]) == 2


class TestCheckContinue:
    """Tests for _check_continue method."""

    def test_check_continue_on_success(self, llm_configs):
        """Test that success triggers finish."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        state = {
            "evaluation": "success",
            "outcome": "Correct answer",
            "trial_count": 2,
            "max_trials": 3,
        }

        result = agent._check_continue(state)
        assert result == "finish"
        assert state["final_answer"] == "Correct answer"

    def test_check_continue_max_trials_reached(self, llm_configs):
        """Test that max trials triggers finish."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Best attempt summary"
        mock_llm.invoke.return_value = mock_response
        agent._llm_cache["documentation"] = mock_llm

        state = {
            "evaluation": "failure",
            "outcome": "Latest attempt",
            "trial_count": 3,
            "max_trials": 3,
            "input_task": "Task",
            "reflection_memory": [],
        }

        result = agent._check_continue(state)
        assert result == "finish"
        assert "final_answer" in state

    def test_check_continue_returns_continue(self, llm_configs):
        """Test that incomplete trials return continue."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        state = {
            "evaluation": "failure",
            "trial_count": 1,
            "max_trials": 3,
        }

        result = agent._check_continue(state)
        assert result == "continue"


class TestRun:
    """Tests for run method."""

    def test_run_requires_built_graph(self, llm_configs):
        """Test that run raises error if graph not built."""
        agent = ReflexionAgent(llm_configs=llm_configs)
        agent.graph = None

        with pytest.raises(ValueError, match="Graph has not been built"):
            agent.run("test task")

    def test_run_success(self, llm_configs):
        """Test successful run."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"final_answer": "Success!"}
        agent.graph = mock_graph

        result = agent.run("Solve this")
        assert result == "Success!"

    def test_run_with_no_answer_fallback(self, llm_configs):
        """Test run with missing final_answer."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {}
        agent.graph = mock_graph

        result = agent.run("Solve this")
        assert result == "No answer generated"

    @patch.object(ReflexionAgent, "on_start")
    @patch.object(ReflexionAgent, "on_finish")
    def test_run_calls_lifecycle_hooks(self, mock_finish, mock_start, llm_configs):
        """Test that run calls lifecycle hooks."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"final_answer": "Result"}
        agent.graph = mock_graph

        agent.run("test task")

        mock_start.assert_called_once_with("test task")
        mock_finish.assert_called_once_with("Result")


class TestHelperMethods:
    """Tests for helper methods."""

    def test_format_memory_empty(self, llm_configs):
        """Test format_memory with empty list."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        formatted = agent._format_memory([])
        assert "No previous trials" in formatted

    def test_format_memory_with_entries(self, llm_configs):
        """Test format_memory with entries."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        memory = ["Trial 1: Lesson A", "Trial 2: Lesson B"]
        formatted = agent._format_memory(memory)

        assert "Trial 1" in formatted
        assert "Lesson A" in formatted
        assert "Trial 2" in formatted

    def test_generate_final_answer(self, llm_configs):
        """Test _generate_final_answer method."""
        agent = ReflexionAgent(llm_configs=llm_configs)

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Best possible answer based on attempts"
        mock_llm.invoke.return_value = mock_response
        agent._llm_cache["documentation"] = mock_llm

        state = {
            "input_task": "Solve puzzle",
            "reflection_memory": ["Trial 1: X", "Trial 2: Y"],
            "outcome": "Last attempt result",
        }

        result = agent._generate_final_answer(state)
        assert len(result) > 0
