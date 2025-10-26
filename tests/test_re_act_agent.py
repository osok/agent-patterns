"""
Unit tests for the ReActAgent class.
"""

from unittest.mock import MagicMock, patch

import pytest

from agent_patterns.patterns import ReActAgent


def mock_search_tool(query: str) -> str:
    """Mock search tool for testing."""
    return f"Search results for: {query}"


def mock_calculator_tool(expression: str) -> str:
    """Mock calculator tool for testing."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception:
        return "Error in calculation"


@pytest.fixture
def llm_configs():
    """Fixture for LLM configurations."""
    return {
        "thinking": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.7,
        }
    }


@pytest.fixture
def tools():
    """Fixture for test tools."""
    return {
        "search": mock_search_tool,
        "calculator": mock_calculator_tool,
    }


def test_react_agent_initialization(llm_configs, tools):
    """Test ReActAgent initialization."""
    agent = ReActAgent(
        llm_configs=llm_configs, tools=tools, max_iterations=3
    )

    assert agent.tools == tools
    assert agent.max_iterations == 3
    assert agent.graph is not None


def test_react_agent_initialization_no_tools(llm_configs):
    """Test ReActAgent initialization without tools."""
    agent = ReActAgent(llm_configs=llm_configs)

    assert agent.tools == {}
    assert agent.max_iterations == 5  # default


def test_react_agent_build_graph_structure(llm_configs, tools):
    """Test that build_graph creates correct graph structure."""
    agent = ReActAgent(llm_configs=llm_configs, tools=tools)

    assert agent.graph is not None
    # Graph should be compiled and ready to run


def test_parse_llm_response_standard_format():
    """Test parsing LLM response in standard format."""
    agent = ReActAgent(llm_configs={}, tools={})

    response = """
    Thought: I need to search for information
    Action: search
    Action Input: test query
    """

    thought, action = agent._parse_llm_response(response)

    assert "search for information" in thought
    assert action["tool_name"] == "search"
    assert action["tool_input"] == "test query"


def test_parse_llm_response_multiline():
    """Test parsing LLM response with multiline content."""
    agent = ReActAgent(llm_configs={}, tools={})

    response = """
    Thought: I need to search for information
    because the user asked about it
    Action: search
    Action Input: test query
    with multiple lines
    """

    thought, action = agent._parse_llm_response(response)

    assert "search for information" in thought
    assert "because the user asked" in thought
    assert action["tool_name"] == "search"
    assert "test query" in action["tool_input"]


def test_parse_llm_response_final_answer():
    """Test parsing LLM response with final answer."""
    agent = ReActAgent(llm_configs={}, tools={})

    response = """
    Thought: I have enough information to answer
    Action: Final Answer
    Action Input: The answer is 42
    """

    thought, action = agent._parse_llm_response(response)

    assert "enough information" in thought
    assert action["tool_name"] == "Final Answer"
    assert action["tool_input"] == "The answer is 42"


def test_format_history_empty():
    """Test formatting empty history."""
    agent = ReActAgent(llm_configs={}, tools={})

    history = agent._format_history([])

    assert "No previous steps" in history


def test_format_history_with_steps():
    """Test formatting history with steps."""
    agent = ReActAgent(llm_configs={}, tools={})

    steps = [
        ("First thought", {"tool_name": "search", "tool_input": "query1"}, "result1"),
        ("Second thought", {"tool_name": "calculator", "tool_input": "2+2"}, "4"),
    ]

    history = agent._format_history(steps)

    assert "Step 1" in history
    assert "Step 2" in history
    assert "First thought" in history
    assert "Second thought" in history
    assert "search" in history
    assert "calculator" in history


def test_execute_action_with_valid_tool(tools):
    """Test executing action with a valid tool."""
    agent = ReActAgent(llm_configs={}, tools=tools)

    state = {
        "action": {"tool_name": "search", "tool_input": "test query"}
    }

    result_state = agent._execute_action(state)

    assert "observation" in result_state
    assert "Search results for: test query" in result_state["observation"]


def test_execute_action_with_invalid_tool():
    """Test executing action with an invalid tool."""
    agent = ReActAgent(llm_configs={}, tools={})

    state = {
        "action": {"tool_name": "nonexistent", "tool_input": "test"}
    }

    result_state = agent._execute_action(state)

    assert "not found" in result_state["observation"]


def test_execute_action_with_final_answer():
    """Test executing action when it's a final answer."""
    agent = ReActAgent(llm_configs={}, tools={})

    state = {
        "action": {"tool_name": "Final Answer", "tool_input": "The answer is 42"}
    }

    result_state = agent._execute_action(state)

    assert result_state["observation"] == "FINAL_ANSWER"
    assert result_state["final_answer"] == "The answer is 42"


def test_execute_action_tool_error():
    """Test executing action when tool raises an error."""

    def error_tool(input):
        raise ValueError("Tool error")

    agent = ReActAgent(llm_configs={}, tools={"error_tool": error_tool})

    state = {
        "action": {"tool_name": "error_tool", "tool_input": "test"}
    }

    result_state = agent._execute_action(state)

    assert "Error" in result_state["observation"]
    assert "Tool error" in result_state["observation"]


def test_observation_handler():
    """Test observation handler updates intermediate steps."""
    agent = ReActAgent(llm_configs={}, tools={})

    state = {
        "thought": "Test thought",
        "action": {"tool_name": "search", "tool_input": "query"},
        "observation": "Test observation",
        "intermediate_steps": [],
    }

    result_state = agent._observation_handler(state)

    assert len(result_state["intermediate_steps"]) == 1
    step = result_state["intermediate_steps"][0]
    assert step[0] == "Test thought"
    assert step[1]["tool_name"] == "search"
    assert step[2] == "Test observation"


def test_should_continue_with_final_answer():
    """Test should_continue when we have a final answer."""
    agent = ReActAgent(llm_configs={}, tools={})

    state = {
        "observation": "FINAL_ANSWER",
        "iteration_count": 1,
        "max_iterations": 5,
    }

    result = agent._should_continue(state)

    assert result == "finish"


def test_should_continue_max_iterations_reached():
    """Test should_continue when max iterations is reached."""
    agent = ReActAgent(llm_configs={}, tools={})

    state = {
        "observation": "Some observation",
        "iteration_count": 5,
        "max_iterations": 5,
        "input": "test question",
    }

    result = agent._should_continue(state)

    assert result == "finish"
    assert "final_answer" in state


def test_should_continue_normal():
    """Test should_continue in normal conditions."""
    agent = ReActAgent(llm_configs={}, tools={})

    state = {
        "observation": "Some observation",
        "thought": "I need to investigate more",
        "iteration_count": 2,
        "max_iterations": 5,
    }

    result = agent._should_continue(state)

    assert result == "continue"


def test_should_continue_with_final_answer_in_thought():
    """Test should_continue when thought indicates completion."""
    agent = ReActAgent(llm_configs={}, tools={})

    state = {
        "observation": "Some observation",
        "thought": "I can now provide a final answer",
        "iteration_count": 2,
        "max_iterations": 5,
    }

    result = agent._should_continue(state)

    assert result == "finish"


def test_generate_fallback_answer_with_observation():
    """Test fallback answer generation with observation."""
    agent = ReActAgent(llm_configs={}, tools={})

    state = {
        "input": "test question",
        "intermediate_steps": [
            ("thought", {"tool_name": "search"}, "Last observation here")
        ],
    }

    answer = agent._generate_fallback_answer(state)

    assert "Last observation here" in answer


def test_generate_fallback_answer_without_observation():
    """Test fallback answer generation without observation."""
    agent = ReActAgent(llm_configs={}, tools={})

    state = {
        "input": "test question",
        "intermediate_steps": [],
    }

    answer = agent._generate_fallback_answer(state)

    assert "unable to find" in answer
    assert "test question" in answer


def test_add_tool():
    """Test adding a tool to the agent."""
    agent = ReActAgent(llm_configs={}, tools={})

    def new_tool(input):
        return "new tool result"

    agent.add_tool("new_tool", new_tool)

    assert "new_tool" in agent.tools
    assert agent.tools["new_tool"]("test") == "new tool result"


def test_remove_tool(tools):
    """Test removing a tool from the agent."""
    agent = ReActAgent(llm_configs={}, tools=tools.copy())

    agent.remove_tool("search")

    assert "search" not in agent.tools
    assert "calculator" in agent.tools  # Other tools remain


def test_remove_nonexistent_tool():
    """Test removing a nonexistent tool raises KeyError."""
    agent = ReActAgent(llm_configs={}, tools={})

    with pytest.raises(KeyError):
        agent.remove_tool("nonexistent")


def test_list_tools(tools):
    """Test listing available tools."""
    agent = ReActAgent(llm_configs={}, tools=tools)

    tool_list = agent.list_tools()

    assert "search" in tool_list
    assert "calculator" in tool_list
    assert len(tool_list) == 2


def test_run_requires_built_graph(llm_configs, tools):
    """Test that run raises error if graph not built."""
    agent = ReActAgent(llm_configs=llm_configs, tools=tools)
    agent.graph = None

    with pytest.raises(ValueError, match="Graph has not been built"):
        agent.run("test input")


@patch.object(ReActAgent, "_generate_thought_and_action")
@patch.object(ReActAgent, "_execute_action")
@patch.object(ReActAgent, "_observation_handler")
@patch.object(ReActAgent, "_should_continue")
@patch.object(ReActAgent, "_format_final_answer")
def test_run_success_flow(
    mock_format,
    mock_should_continue,
    mock_observation,
    mock_execute,
    mock_generate,
    llm_configs,
    tools,
):
    """Test successful run flow."""
    # Configure mocks to simulate one iteration then finish
    mock_generate.return_value = {
        "thought": "test thought",
        "action": {"tool_name": "Final Answer", "tool_input": "answer"},
        "iteration_count": 1,
    }
    mock_execute.return_value = {
        "observation": "FINAL_ANSWER",
        "final_answer": "answer",
    }
    mock_observation.return_value = {"observation": "FINAL_ANSWER"}
    mock_should_continue.return_value = "finish"
    mock_format.return_value = {"final_answer": "Formatted answer"}

    agent = ReActAgent(llm_configs=llm_configs, tools=tools)

    # Mock the graph to return our mocked state
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"final_answer": "Final result"}
    agent.graph = mock_graph

    result = agent.run("test input")

    assert result == "Final result"
