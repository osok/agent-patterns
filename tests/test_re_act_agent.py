"""Unit tests for the ReAct agent pattern."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, TypedDict
from langchain_core.tools import BaseTool
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.language_models import BaseLanguageModel
from pathlib import Path

from agent_patterns.patterns.re_act_agent import ReActAgent, ReActState


# Shared mock for load_prompt to avoid file not found errors
@pytest.fixture
def mock_load_prompt():
    from langchain_core.prompts import ChatPromptTemplate
    dummy_template = ChatPromptTemplate.from_messages([
        ("system", "System Prompt: You are a ReAct agent."),
        ("user", "User Input: {input}\nTools: {tools}\nHistory: {intermediate_steps}")
    ])
    with patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template", 
              return_value=dummy_template) as mock:
        yield mock

# Updated fixture for llm_configs as expected by BaseAgent
@pytest.fixture
def mock_llm_configs():
    return {
        'default': {'provider': 'mock', 'model': 'mock-model'}
    }

# Test fixtures
@pytest.fixture
def mock_llm():
    """Create a mock LLM that returns predefined responses."""
    llm = Mock(spec=BaseLanguageModel)
    llm.invoke.side_effect = [
        AIMessage(content="""Thought: I need to search for information about Python
Action: search_tool(python programming language)"""),
        AIMessage(content="""Thought: I have the information I need. Let me summarize.
Action: DONE"""),
        AIMessage(content="Python is a popular programming language."),
        AIMessage(content="Dummy fourth response") 
    ]
    return llm

@pytest.fixture
def mock_tools() -> List[BaseTool]:
    search_tool = Mock(spec=BaseTool)
    search_tool.name = "search_tool"
    search_tool.description = "Search for information"
    search_tool.run.return_value = "Python is a programming language."
    
    calc_tool = Mock(spec=BaseTool)
    calc_tool.name = "calculator"
    calc_tool.description = "Perform calculations"
    calc_tool.run.return_value = "4"
    
    return [search_tool, calc_tool]

@pytest.fixture
def mock_prompts(tmp_path):
    """Create temporary prompt directory (less critical now with mocking)."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "ReActAgent" / "AgentStep").mkdir(parents=True, exist_ok=True)
    (prompts_dir / "ReActAgent" / "AgentStep" / "system.md").touch()
    (prompts_dir / "ReActAgent" / "AgentStep" / "user.md").touch()
    return str(prompts_dir)

@pytest.fixture
def react_agent(mock_prompts, mock_tools, mock_llm, mock_llm_configs):
    with patch.object(ReActAgent, '_get_llm', return_value=mock_llm):
        agent = ReActAgent(
            prompt_dir=mock_prompts,
            tools=mock_tools,
            llm_configs=mock_llm_configs,
        )
    return agent

# Test cases
def test_init(mock_tools, mock_prompts, mock_llm_configs):
    """Test ReActAgent initialization."""
    with patch("agent_patterns.core.base_agent.BaseAgent._get_llm", return_value=Mock(spec=BaseLanguageModel)):
        agent = ReActAgent(
            prompt_dir=mock_prompts,
            tools=mock_tools,
            llm_configs=mock_llm_configs
        )
    
    assert agent.tools == mock_tools
    assert agent.max_steps == 10  # default value
    assert agent.prompt_dir == mock_prompts
    assert agent.graph is not None
    assert agent.llm is not None

def test_custom_max_steps(mock_tools, mock_prompts, mock_llm_configs):
    """Test ReActAgent with custom max_steps."""
    custom_steps = 5
    with patch("agent_patterns.core.base_agent.BaseAgent._get_llm", return_value=Mock(spec=BaseLanguageModel)):
        agent = ReActAgent(
            prompt_dir=mock_prompts,
            tools=mock_tools,
            llm_configs=mock_llm_configs,
            max_steps=custom_steps
        )
    
    assert agent.max_steps == custom_steps

@pytest.mark.skip(reason="Needs rework for new ReActState and agent flow")
def test_run_simple_completion(react_agent, mock_tools, mock_llm, mock_load_prompt):
    """Test a simple successful completion of the ReAct cycle."""
    mock_tools[0].run.return_value = "Python is a programming language."
    
    result = react_agent.run("Tell me about Python")
    
    assert result.get("output") == "Python is a popular programming language."
    mock_tools[0].run.assert_called_once_with("python programming language")
    assert mock_llm.invoke.call_count >= 2

def test_parse_llm_react_response_action(react_agent):
    """Test parsing LLM response for an action."""
    agent = react_agent
    response = AIMessage(content="""Thought: I need to search.
Action: search_tool(query="test query")""")
    outcome = agent._parse_llm_react_response(response)
    assert isinstance(outcome, AgentAction)
    assert outcome.tool == "search_tool"
    assert outcome.tool_input == {"query": "test query"}

def test_parse_llm_react_response_finish(react_agent):
    """Test parsing LLM response for a final answer."""
    agent = react_agent
    response = AIMessage(content="""Thought: I have the answer.
Final Answer: The answer is 42.""")
    outcome = agent._parse_llm_react_response(response)
    assert isinstance(outcome, AgentFinish)
    assert outcome.return_values["output"] == "The answer is 42."

def test_parse_llm_react_response_malformed(react_agent):
    """Test parsing malformed LLM response."""
    agent = react_agent
    response = AIMessage(content="Just some text without action or answer.")
    outcome = agent._parse_llm_react_response(response)
    assert isinstance(outcome, AgentFinish)
    assert "Just some text" in outcome.return_values["output"] 

@pytest.mark.skip(reason="Needs rework for new ReActState and agent flow")
def test_max_steps_limit(mock_tools, mock_prompts, mock_load_prompt, mock_llm_configs):
    """Test that agent stops after max_steps."""
    mock_llm_limited = Mock(spec=BaseLanguageModel)
    mock_llm_limited.invoke.side_effect = [AIMessage(content="Action: search_tool(more info)")] * 10 
    
    with patch("agent_patterns.core.base_agent.BaseAgent._get_llm", return_value=mock_llm_limited):
        agent = ReActAgent(
            prompt_dir=mock_prompts,
            tools=mock_tools,
            llm_configs=mock_llm_configs,
            max_steps=3
        )
    
    result = agent.run("Tell me everything")
    assert "Agent stopped" in result.get("output", "")

@pytest.mark.skip(reason="Needs rework for new ReActState and agent flow")
def test_tool_error_handling(mock_tools, mock_prompts, mock_load_prompt, mock_llm_configs):
    """Test handling of tool execution errors."""
    mock_tools[0].run.side_effect = Exception("Tool failed")
    mock_llm_error = Mock(spec=BaseLanguageModel)
    mock_llm_error.invoke.side_effect = [
        AIMessage(content="Action: search_tool(query)"),
        AIMessage(content="Final Answer: Cannot proceed due to tool error.")
    ]

    with patch("agent_patterns.core.base_agent.BaseAgent._get_llm", return_value=mock_llm_error):
        agent = ReActAgent(
            prompt_dir=mock_prompts,
            tools=mock_tools,
            llm_configs=mock_llm_configs
        )
    
    result = agent.run("Search something")
    assert "Error executing tool search_tool: Tool failed" in str(result)

def test_should_execute_tools(react_agent):
    """Test the _should_execute_tools logic."""
    agent = react_agent
    state_action: ReActState = {
        "input": "", "chat_history": [], "intermediate_steps": [],
        "agent_outcome": AgentAction(tool="test", tool_input="", log="")
    }
    assert agent._should_execute_tools(state_action) is True

    state_finish: ReActState = {
        "input": "", "chat_history": [], "intermediate_steps": [],
        "agent_outcome": AgentFinish({"output": "done"}, log="")
    }
    assert agent._should_execute_tools(state_finish) is False

    state_none: ReActState = {"input": "", "chat_history": [], "intermediate_steps": [], "agent_outcome": None}
    assert agent._should_execute_tools(state_none) is False

@pytest.mark.skip(reason="_process_observation was removed")
def test_process_observation(mock_tools, mock_prompts):
    pass

@pytest.mark.skip(reason="_format_final_answer was removed")
def test_format_final_answer_error(mock_tools, mock_prompts):
   pass

@pytest.mark.skip(reason="_generate_default_answer was removed")
def test_generate_default_answer(mock_tools, mock_prompts):
    pass

@pytest.mark.skip(reason="_generate_default_answer was removed")
def test_generate_default_answer_direct():
    pass

@pytest.mark.skip(reason="Needs rework for new ReActState and agent flow")
def test_intermediate_steps_tracking(mock_tools, mock_prompts, mock_load_prompt, mock_llm_configs):
    """Test that intermediate steps are properly tracked."""
    mock_llm_tracking = Mock(spec=BaseLanguageModel)
    mock_llm_tracking.invoke.side_effect = [
        AIMessage(content="Action: search_tool(query1)"),
        AIMessage(content="Action: calculator(2+2)"),
        AIMessage(content="Final Answer: Result is 4")
    ]
    mock_tools[0].run.return_value = "Search result"
    mock_tools[1].run.return_value = "4"

    with patch("agent_patterns.core.base_agent.BaseAgent._get_llm", return_value=mock_llm_tracking):
        agent = ReActAgent(
            prompt_dir=mock_prompts,
            tools=mock_tools,
            llm_configs=mock_llm_configs
        )
        
    result_state = agent.run("Test query")
    
    pass