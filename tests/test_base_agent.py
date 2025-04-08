"""Tests for the BaseAgent class."""

import os
import pytest
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

from agent_patterns.core.base_agent import BaseAgent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate


class SimpleTestAgent(BaseAgent):
    """A simple agent implementation for testing."""
    
    def __init__(self, prompt_dir: str, llm_configs: Dict[str, Any], log_level: int = logging.INFO):
        """Initialize the test agent, passing llm_configs to BaseAgent."""
        # Pass llm_configs directly to super().__init__
        super().__init__(prompt_dir=prompt_dir, llm_configs=llm_configs, log_level=log_level)
        # self._llm_configs = llm_configs # No longer needed, handled by BaseAgent
        # self.graph = None # Handled by BaseAgent
        # self.build_graph() # Called by BaseAgent __init__
    
    def build_graph(self) -> None:
        """Build a simple mock graph (Needs to be a CompiledGraph)."""
        # For testing BaseAgent, we just need to set self.graph to something.
        # A Mock that mimics CompiledGraph might be needed for run/stream tests.
        # For init tests, a simple Mock might suffice if run/stream aren't called.
        self.graph = Mock(name="MockCompiledGraph") 
    
    def run(self, input_data: Any) -> Any:
        """Run the agent (Placeholder for testing)."""
        # If tests call run, this might need actual graph invocation simulation
        return {"result": "test result"}

    # Override _get_llm if specific mock behavior is needed for these tests,
    # otherwise, rely on the BaseAgent._get_llm implementation.
    # For now, let's remove the override to test the BaseAgent logic.
    # def _get_llm(self, role: str = "default"):
    #     ...


@pytest.fixture
def test_prompts_dir(tmp_path):
    """Create a temp directory with test prompts in the expected structure."""
    prompts_root = tmp_path / "prompts"
    # Create structure: <prompt_dir>/<ClassName>/<step_name>/
    step_dir = prompts_root / "SimpleTestAgent" / "sample"
    step_dir.mkdir(parents=True)
    
    # Create sample prompt files
    (step_dir / "system.md").write_text("System prompt for sample step.")
    (step_dir / "user.md").write_text("User prompt for {variable}.")
    
    return str(prompts_root) # Return the root prompts directory


@pytest.fixture
def llm_configs():
    """Sample LLM configs for testing."""
    return {
        "thinking": {
            "model_name": "gpt-4-turbo",
            "provider": "openai"
        },
        "reflection": {
            "model_name": "claude-3",
            "provider": "anthropic"
        }
    }


def test_base_agent_initialization(llm_configs, test_prompts_dir):
    """Test basic agent initialization."""
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
    assert agent.prompt_dir == str(test_prompts_dir)
    assert agent.graph is not None


def test_get_llm_openai(llm_configs, test_prompts_dir):
    """Test getting an OpenAI LLM."""
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
    
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        agent._get_llm("thinking")
        mock_openai.assert_called_once()


def test_get_llm_anthropic(llm_configs, test_prompts_dir):
    """Test getting an Anthropic LLM."""
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
    
    with patch("langchain_anthropic.ChatAnthropic") as mock_anthropic:
        agent._get_llm("reflection")
        mock_anthropic.assert_called_once()


def test_get_llm_caching(llm_configs, test_prompts_dir):
    """Test that LLMs are properly cached."""
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
    
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        # First call should create a new LLM
        agent._get_llm("thinking")
        assert mock_openai.call_count == 1
        
        # Second call should use cached instance
        agent._get_llm("thinking")
        assert mock_openai.call_count == 1


def test_get_llm_invalid_role(llm_configs, test_prompts_dir):
    """Test error handling for invalid role."""
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
    
    with pytest.raises(ValueError) as excinfo:
        agent._get_llm("invalid_role")
    assert "Role 'invalid_role' not found in llm_configs" in str(excinfo.value)


def test_get_llm_invalid_provider(llm_configs, test_prompts_dir):
    """Test error handling for invalid provider."""
    invalid_configs = {
        "test": {
            "provider": "invalid",
            "model_name": "test"
        }
    }
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=invalid_configs)
    
    with pytest.raises(ValueError) as excinfo:
        agent._get_llm("test")
    assert "Unsupported LLM provider" in str(excinfo.value)


def test_load_prompt(llm_configs, test_prompts_dir):
    """Test prompt loading using _load_prompt_template."""
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
    # Call with step_name, expects it to find SimpleTestAgent/sample/{system|user}.md
    prompt_template = agent._load_prompt_template("sample") 
    assert isinstance(prompt_template, ChatPromptTemplate)
    # Check content or structure if necessary
    assert len(prompt_template.messages) == 2
    assert "System prompt" in prompt_template.messages[0].prompt.template
    assert "User prompt for {variable}" in prompt_template.messages[1].prompt.template


def test_load_prompt_missing_files(llm_configs, test_prompts_dir):
    """Test error handling for missing prompt files."""
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
    
    with pytest.raises(FileNotFoundError):
        # Try loading a step that doesn't exist
        agent._load_prompt_template("nonexistent_step") 


def test_stream_interface(llm_configs, test_prompts_dir):
    """Test the streaming interface."""
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
    
    # Should have a method to handle streaming
    assert hasattr(agent, "stream")
    assert callable(agent.stream)


def test_lifecycle_hooks(llm_configs, test_prompts_dir):
    """Test that lifecycle hooks exist and can be called."""
    agent = SimpleTestAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
    
    # Test hooks exist (as defined in BaseAgent)
    assert hasattr(agent, "on_start")
    assert hasattr(agent, "on_finish") # Check for on_finish
    
    # Test they can be called without error
    agent.on_start()
    agent.on_finish()


def test_missing_graph_build(test_prompts_dir, llm_configs):
    """Test error handling when build_graph doesn't set the graph."""
    class BadAgent(BaseAgent):
        def build_graph(self) -> None:
            pass  # Doesn't set self.graph
        def run(self, input_data: Any) -> Any:
            pass
    
    with pytest.raises(ValueError):
        BadAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)