"""
Agent Patterns Library.

A collection of reusable AI agent workflow patterns implemented using LangGraph and LangChain.
All patterns are synchronous and follow consistent architectural principles.
"""

__version__ = "0.1.0"

from agent_patterns.core import BaseAgent, MultiAgentBase

__all__ = ["BaseAgent", "MultiAgentBase", "__version__"]
