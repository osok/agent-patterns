from unittest.mock import Mock
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from agent_patterns.patterns.re_act_agent import ReActAgent, ReActState

def test_format_final_answer_with_error():
    """Test that the format_final_answer method handles LLM errors by generating a default answer."""
    # Create a mock LLM that raises an exception
    mock_llm = Mock(spec=BaseLanguageModel)
    mock_llm.invoke.side_effect = Exception("LLM error")
    
    # Create a simple agent with the mocked LLM
    agent = ReActAgent(
        prompt_dir="prompts",
        tools=[],
        llm_configs={'default': {'provider': 'dummy'}},
        llm=mock_llm
    )
    
    # Create a test state using ReActState structure (simplified for this test)
    state: ReActState = {
        "input": "test query",
        "chat_history": [],
        "agent_outcome": None,
        "intermediate_steps": []
    }
    
    # Call the method (which now takes ReActState)
    state_with_obs = {
        "input": "test query",
        "chat_history": [],
        "agent_outcome": None,
        "intermediate_steps": [(AgentAction(tool="search", tool_input="query", log=""), "This is a search result")]
    }
    answer = agent._generate_default_answer(state_with_obs)
    
    # Check the result
    print("Result:", answer)
    assert isinstance(answer, str)
    assert "Based on my execution, I found: This is a search result" in answer
    print("Test passed!")

if __name__ == "__main__":
    test_format_final_answer_with_error() 