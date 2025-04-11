"""Agent patterns for different use cases.

This package contains implementations of various agent patterns to solve different
types of problems and implement different reasoning strategies."""

from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.patterns.reflection_agent import ReflectionAgent
from agent_patterns.patterns.plan_and_solve_agent import PlanAndSolveAgent
from agent_patterns.patterns.reflection_and_refinement_agent import ReflectionAndRefinementAgent
from agent_patterns.patterns.factory import (
    create_plan_and_solve_agent,
    create_react_agent,
    create_reflection_agent,
    create_reflection_and_refinement_agent
)

__all__ = [
    "ReActAgent",
    "ReflectionAgent",
    "PlanAndSolveAgent",
    "ReflectionAndRefinementAgent",
    "create_plan_and_solve_agent",
    "create_react_agent",
    "create_reflection_agent",
    "create_reflection_and_refinement_agent"
]