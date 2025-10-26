"""
Multi-agent base class for coordinating multiple sub-agents.

This module provides the abstract base class for multi-agent patterns where multiple
specialized agents work together to accomplish complex tasks.
"""

import abc
from typing import Any, Dict

from agent_patterns.core.base_agent import BaseAgent


class MultiAgentBase(BaseAgent, abc.ABC):
    """
    Abstract base class for multi-agent patterns.

    This class extends BaseAgent to support coordination between multiple sub-agents.
    Each sub-agent can be a specialized pattern (e.g., researcher, coder, reviewer)
    that contributes to solving different aspects of the overall task.

    Attributes:
        sub_agents (Dict[str, BaseAgent]): Mapping of role names to agent instances
        llm_configs (Dict[str, Dict[str, Any]]): Configuration for LLM roles
        prompt_dir (str): Directory containing prompt templates
    """

    def __init__(
        self,
        sub_agents: Dict[str, BaseAgent],
        llm_configs: Dict[str, Dict[str, Any]],
        **kwargs: Any
    ):
        """
        Initialize the multi-agent coordinator.

        Args:
            sub_agents: Dictionary mapping role names to initialized agent instances.
                       Example: {"researcher": ResearchAgent(...), "coder": CoderAgent(...)}
            llm_configs: Configuration for the coordinator's LLM (if needed)
            **kwargs: Additional arguments passed to BaseAgent.__init__()
        """
        self.sub_agents = sub_agents
        super().__init__(llm_configs=llm_configs, **kwargs)

    @abc.abstractmethod
    def coordinate(self, task: str) -> str:
        """
        High-level method for distributing a task among sub-agents.

        This method defines the coordination strategy for the multi-agent system.
        It determines which agents to invoke, in what order, and how to combine
        their results.

        Args:
            task: The high-level task or problem to solve

        Returns:
            Unified final result from coordinating all sub-agents

        Example:
            def coordinate(self, task: str) -> str:
                # Break down task
                subtasks = self._decompose_task(task)

                # Distribute to agents
                results = {}
                for role, subtask in subtasks.items():
                    if role in self.sub_agents:
                        results[role] = self.sub_agents[role].run(subtask)

                # Synthesize results
                return self._synthesize_results(results)
        """
        pass

    def add_agent(self, role: str, agent: BaseAgent) -> None:
        """
        Add a new sub-agent to the coordinator.

        Args:
            role: The role or name for this agent
            agent: An initialized BaseAgent instance
        """
        self.sub_agents[role] = agent

    def remove_agent(self, role: str) -> None:
        """
        Remove a sub-agent from the coordinator.

        Args:
            role: The role or name of the agent to remove

        Raises:
            KeyError: If the role doesn't exist
        """
        del self.sub_agents[role]

    def get_agent(self, role: str) -> BaseAgent:
        """
        Get a sub-agent by role.

        Args:
            role: The role or name of the agent

        Returns:
            The agent instance for that role

        Raises:
            KeyError: If the role doesn't exist
        """
        return self.sub_agents[role]

    def list_agents(self) -> list[str]:
        """
        Get a list of all sub-agent roles.

        Returns:
            List of role names
        """
        return list(self.sub_agents.keys())
