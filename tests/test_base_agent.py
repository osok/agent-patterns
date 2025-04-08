"""Tests for the BaseAgent class."""

import os
import pytest
from pathlib import Path
from typing import Any, Dict

from agent_patterns.core.base_agent import BaseAgent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


class SimpleTestAgent(BaseAgent):
    """A simple agent implementation for testing."""
    
    def build_graph(self) -> None:
        """Simple graph with a single node."""
        from langgraph.graph import StateGraph
        
        sg = StateGraph(input=str, output=str)
        sg.add_node("test_node", lambda x: x)
        self.graph = sg.compile()
    
    def run(self, input_data: Any) -> Any:
        """Simple pass-through implementation."""
        return input_data


@pytest.fixture
def test_prompts_dir(tmp_path):
    """Create a temporary prompts directory with test files."""
    prompts_dir = tmp_path / "prompts" / "SimpleTestAgent" / "TestStep"
    prompts_dir.mkdir(parents=True)
    
    # Create test prompt files
    (prompts_dir / "system.md").write_text("Test system prompt")
    (prompts_dir / "user.md").write_text("Test user prompt")
    
    return tmp_path / "prompts"


@pytest.fixture
def llm_configs():
    """Sample LLM configurations."""
    return {
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4-turbo"
        },
        "reflection": {
            "provider": "anthropic",
            "model_name": "claude-3"
        }
    }


def test_base_agent_initialization(llm_configs, test_prompts_dir):
    """Test basic agent initialization."""
    agent = SimpleTestAgent(llm_configs, prompt_dir=str(test_prompts_dir))
    assert agent.llm_configs == llm_configs
    assert agent.prompt_dir == str(test_prompts_dir)
    assert agent.graph is not None


def test_get_llm_openai(llm_configs, test_prompts_dir):
    """Test getting an OpenAI LLM."""
    agent = SimpleTestAgent(llm_configs, prompt_dir=str(test_prompts_dir))
    llm = agent._get_llm("thinking")
    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "gpt-4-turbo"


def test_get_llm_anthropic(llm_configs, test_prompts_dir):
    """Test getting an Anthropic LLM."""
    agent = SimpleTestAgent(llm_configs, prompt_dir=str(test_prompts_dir))
    llm = agent._get_llm("reflection")
    assert isinstance(llm, ChatAnthropic)
    assert llm.model == "claude-3"


def test_get_llm_caching(llm_configs, test_prompts_dir):
    """Test that LLMs are properly cached."""
    agent = SimpleTestAgent(llm_configs, prompt_dir=str(test_prompts_dir))
    llm1 = agent._get_llm("thinking")
    llm2 = agent._get_llm("thinking")
    assert llm1 is llm2  # Same instance


def test_get_llm_invalid_role(llm_configs, test_prompts_dir):
    """Test error handling for invalid role."""
    agent = SimpleTestAgent(llm_configs, prompt_dir=str(test_prompts_dir))
    with pytest.raises(ValueError):
        agent._get_llm("nonexistent_role")


def test_get_llm_invalid_provider(llm_configs, test_prompts_dir):
    """Test error handling for invalid provider."""
    invalid_configs = {
        "test": {
            "provider": "invalid",
            "model_name": "test"
        }
    }
    agent = SimpleTestAgent(invalid_configs, prompt_dir=str(test_prompts_dir))
    with pytest.raises(ValueError):
        agent._get_llm("test")


def test_load_prompt(llm_configs, test_prompts_dir):
    """Test prompt loading."""
    agent = SimpleTestAgent(llm_configs, prompt_dir=str(test_prompts_dir))
    prompts = agent._load_prompt("TestStep")
    assert prompts["system"] == "Test system prompt"
    assert prompts["user"] == "Test user prompt"


def test_load_prompt_missing_files(llm_configs, test_prompts_dir):
    """Test error handling for missing prompt files."""
    agent = SimpleTestAgent(llm_configs, prompt_dir=str(test_prompts_dir))
    with pytest.raises(FileNotFoundError):
        agent._load_prompt("NonexistentStep")


def test_stream_interface(llm_configs, test_prompts_dir):
    """Test the streaming interface."""
    agent = SimpleTestAgent(llm_configs, prompt_dir=str(test_prompts_dir))
    test_input = "test"
    stream = agent.stream(test_input)
    assert next(stream) == test_input


def test_lifecycle_hooks(llm_configs, test_prompts_dir):
    """Test that lifecycle hooks exist and can be called."""
    agent = SimpleTestAgent(llm_configs, prompt_dir=str(test_prompts_dir))
    # These should not raise any errors
    agent.on_start()
    agent.on_finish()


def test_missing_graph_build(llm_configs, test_prompts_dir):
    """Test error handling when build_graph doesn't set the graph."""
    class BadAgent(BaseAgent):
        def build_graph(self) -> None:
            pass  # Doesn't set self.graph
        def run(self, input_data: Any) -> Any:
            pass
    
    with pytest.raises(ValueError):
        BadAgent(llm_configs, prompt_dir=str(test_prompts_dir))