"""
Unit tests for the BaseAgent class.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent_patterns.core import BaseAgent


# Concrete implementation for testing
class TestAgent(BaseAgent):
    """Concrete test implementation of BaseAgent."""

    def build_graph(self) -> None:
        """Build a simple test graph."""
        self.graph = MagicMock()

    def run(self, input_data: str) -> str:
        """Simple run implementation."""
        return f"Processed: {input_data}"


def test_base_agent_initialization():
    """Test BaseAgent initialization."""
    llm_configs = {
        "thinking": {"provider": "openai", "model_name": "gpt-4"}
    }

    agent = TestAgent(llm_configs=llm_configs, prompt_dir="prompts")

    assert agent.llm_configs == llm_configs
    assert agent.prompt_dir == "prompts"
    assert agent.graph is not None
    assert len(agent._llm_cache) == 0


def test_base_agent_build_graph_called():
    """Test that build_graph is called during initialization."""
    llm_configs = {"thinking": {"provider": "openai", "model_name": "gpt-4"}}

    with patch.object(TestAgent, "build_graph") as mock_build:
        agent = TestAgent(llm_configs=llm_configs)
        mock_build.assert_called_once()


@patch("agent_patterns.core.base_agent.ChatOpenAI")
def test_get_llm_openai(mock_chat_openai):
    """Test _get_llm with OpenAI provider."""
    llm_configs = {
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.5,
            "max_tokens": 1000,
        }
    }

    agent = TestAgent(llm_configs=llm_configs)
    llm = agent._get_llm("thinking")

    # Verify ChatOpenAI was called with correct parameters
    mock_chat_openai.assert_called_once_with(
        model="gpt-4", temperature=0.5, max_tokens=1000
    )

    # Verify caching
    assert "thinking" in agent._llm_cache
    llm2 = agent._get_llm("thinking")
    assert llm is llm2  # Should return cached instance


@patch("agent_patterns.core.base_agent.ChatAnthropic")
def test_get_llm_anthropic(mock_chat_anthropic):
    """Test _get_llm with Anthropic provider."""
    llm_configs = {
        "reflection": {
            "provider": "anthropic",
            "model_name": "claude-3-5-sonnet-20241022",
            "temperature": 0.7,
        }
    }

    agent = TestAgent(llm_configs=llm_configs)
    llm = agent._get_llm("reflection")

    # Verify ChatAnthropic was called
    mock_chat_anthropic.assert_called_once()
    assert "reflection" in agent._llm_cache


def test_get_llm_missing_role():
    """Test _get_llm with missing role raises ValueError."""
    llm_configs = {"thinking": {"provider": "openai", "model_name": "gpt-4"}}

    agent = TestAgent(llm_configs=llm_configs)

    with pytest.raises(ValueError, match="No configuration found for role"):
        agent._get_llm("nonexistent_role")


def test_get_llm_missing_model_name():
    """Test _get_llm with missing model_name raises KeyError."""
    llm_configs = {
        "thinking": {"provider": "openai"}  # Missing model_name
    }

    agent = TestAgent(llm_configs=llm_configs)

    with pytest.raises(KeyError, match="model_name"):
        agent._get_llm("thinking")


def test_get_llm_unsupported_provider():
    """Test _get_llm with unsupported provider raises ValueError."""
    llm_configs = {
        "thinking": {"provider": "unsupported", "model_name": "model"}
    }

    agent = TestAgent(llm_configs=llm_configs)

    with pytest.raises(ValueError, match="Unsupported provider"):
        agent._get_llm("thinking")


def test_load_prompt_with_files():
    """Test _load_prompt when files exist."""
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt_dir = Path(tmpdir)
        agent_dir = prompt_dir / "TestAgent" / "TestStep"
        agent_dir.mkdir(parents=True)

        # Create prompt files
        (agent_dir / "system.md").write_text("System prompt content")
        (agent_dir / "user.md").write_text("User prompt template: {input}")

        # Test loading
        agent = TestAgent(llm_configs={}, prompt_dir=str(prompt_dir))
        prompts = agent._load_prompt("TestStep")

        assert prompts["system_prompt"] == "System prompt content"
        assert prompts["user_prompt"] == "User prompt template: {input}"


def test_load_prompt_missing_files():
    """Test _load_prompt when files don't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = TestAgent(llm_configs={}, prompt_dir=tmpdir)
        prompts = agent._load_prompt("NonexistentStep")

        assert prompts["system_prompt"] == ""
        assert prompts["user_prompt"] == ""


def test_load_prompt_partial_files():
    """Test _load_prompt when only some files exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt_dir = Path(tmpdir)
        agent_dir = prompt_dir / "TestAgent" / "PartialStep"
        agent_dir.mkdir(parents=True)

        # Only create system.md
        (agent_dir / "system.md").write_text("System only")

        agent = TestAgent(llm_configs={}, prompt_dir=str(prompt_dir))
        prompts = agent._load_prompt("PartialStep")

        assert prompts["system_prompt"] == "System only"
        assert prompts["user_prompt"] == ""


def test_stream_default_implementation():
    """Test default stream implementation."""
    llm_configs = {"thinking": {"provider": "openai", "model_name": "gpt-4"}}
    agent = TestAgent(llm_configs=llm_configs)

    input_data = "test input"
    results = list(agent.stream(input_data))

    assert len(results) == 1
    assert results[0] == f"Processed: {input_data}"


def test_lifecycle_hooks():
    """Test lifecycle hook methods."""
    llm_configs = {"thinking": {"provider": "openai", "model_name": "gpt-4"}}
    agent = TestAgent(llm_configs=llm_configs)

    # These should not raise errors
    agent.on_start("input")
    agent.on_finish("output")
    agent.on_error(Exception("test"))


def test_lifecycle_hooks_can_be_overridden():
    """Test that lifecycle hooks can be overridden."""

    class CustomAgent(TestAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_called = False
            self.finish_called = False
            self.error_called = False

        def on_start(self, input_data):
            self.start_called = True

        def on_finish(self, result):
            self.finish_called = True

        def on_error(self, error):
            self.error_called = True

    agent = CustomAgent(llm_configs={})

    agent.on_start("test")
    agent.on_finish("result")
    agent.on_error(Exception())

    assert agent.start_called
    assert agent.finish_called
    assert agent.error_called


def test_abstract_methods_must_be_implemented():
    """Test that abstract methods must be implemented."""

    # This should raise TypeError because build_graph and run are not implemented
    with pytest.raises(TypeError):

        class IncompleteAgent(BaseAgent):
            pass

        IncompleteAgent(llm_configs={})


def test_default_temperature_and_max_tokens():
    """Test that default temperature and max_tokens are used when not specified."""
    llm_configs = {
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4",
            # No temperature or max_tokens specified
        }
    }

    with patch("agent_patterns.core.base_agent.ChatOpenAI") as mock_chat_openai:
        agent = TestAgent(llm_configs=llm_configs)
        agent._get_llm("thinking")

        # Verify defaults are used
        mock_chat_openai.assert_called_once_with(
            model="gpt-4", temperature=0.7, max_tokens=2000
        )
