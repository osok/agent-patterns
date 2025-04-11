"""Factory module for creating agent instances."""

from typing import Dict, List, Any, Optional, Type
from langchain_core.language_models import BaseLanguageModel

from agent_patterns.core.base_agent import BaseAgent
from agent_patterns.core.memory.provider import MemoryProvider
from agent_patterns.core.tools.provider import DefaultToolProvider
from agent_patterns.patterns.reflection_and_refinement_agent import ReflectionAndRefinementAgent
from agent_patterns.patterns.plan_and_solve_agent import PlanAndSolveAgent
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.patterns.reflection_agent import ReflectionAgent


def create_reflection_and_refinement_agent(
    llm: BaseLanguageModel,
    memory_provider: Optional[MemoryProvider] = None,
    tool_provider: Optional[DefaultToolProvider] = None,
    **kwargs: Any
) -> BaseAgent:
    """Create a Reflection and Refinement agent.

    Args:
        llm: The language model to use
        memory_provider: Optional memory provider to use with the agent
        tool_provider: Optional tool provider to use with the agent
        **kwargs: Additional keyword arguments to pass to the agent constructor

    Returns:
        A configured ReflectionAndRefinementAgent instance
    """
    return ReflectionAndRefinementAgent(
        llm=llm,
        memory_provider=memory_provider,
        tool_provider=tool_provider,
        **kwargs
    )


def create_plan_and_solve_agent(
    llm: BaseLanguageModel,
    memory_provider: Optional[MemoryProvider] = None,
    tool_provider: Optional[DefaultToolProvider] = None,
    **kwargs: Any
) -> BaseAgent:
    """Create a Plan and Solve agent.

    Args:
        llm: The language model to use
        memory_provider: Optional memory provider to use with the agent
        tool_provider: Optional tool provider to use with the agent
        **kwargs: Additional keyword arguments to pass to the agent constructor

    Returns:
        A configured PlanAndSolveAgent instance
    """
    return PlanAndSolveAgent(
        llm=llm,
        memory_provider=memory_provider,
        tool_provider=tool_provider,
        **kwargs
    )


def create_react_agent(
    llm: BaseLanguageModel,
    memory_provider: Optional[MemoryProvider] = None,
    tool_provider: Optional[DefaultToolProvider] = None,
    **kwargs: Any
) -> BaseAgent:
    """Create a ReAct agent.

    Args:
        llm: The language model to use
        memory_provider: Optional memory provider to use with the agent
        tool_provider: Optional tool provider to use with the agent
        **kwargs: Additional keyword arguments to pass to the agent constructor

    Returns:
        A configured ReActAgent instance
    """
    return ReActAgent(
        llm=llm,
        memory_provider=memory_provider,
        tool_provider=tool_provider,
        **kwargs
    )


def create_reflection_agent(
    llm: BaseLanguageModel,
    memory_provider: Optional[MemoryProvider] = None,
    tool_provider: Optional[DefaultToolProvider] = None,
    **kwargs: Any
) -> BaseAgent:
    """Create a Reflection agent.

    Args:
        llm: The language model to use
        memory_provider: Optional memory provider to use with the agent
        tool_provider: Optional tool provider to use with the agent
        **kwargs: Additional keyword arguments to pass to the agent constructor

    Returns:
        A configured ReflectionAgent instance
    """
    return ReflectionAgent(
        llm=llm,
        memory_provider=memory_provider,
        tool_provider=tool_provider,
        **kwargs
    )