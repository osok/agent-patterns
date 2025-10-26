"""
Base agent class for all agent patterns.

This module provides the abstract base class that all agent patterns must inherit from.
It defines the core interface and common functionality for agent workflows.
"""

import abc
import os
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph


class BaseAgent(abc.ABC):
    """
    Abstract base class for all agent patterns.

    This class provides the foundation for implementing AI agent workflows using LangGraph.
    Subclasses must implement build_graph() and run() methods to define their specific
    pattern logic.

    The BaseAgent handles:
    - LLM initialization for different roles (thinking, reflection, etc.)
    - Prompt template loading from external files
    - Graph compilation for state transitions
    - Optional lifecycle hooks for logging and monitoring

    Attributes:
        llm_configs (Dict[str, Dict[str, Any]]): Configuration for LLM roles
        prompt_dir (str): Directory containing prompt templates
        custom_instructions (Optional[str]): Custom instructions appended to all prompts
        prompt_overrides (Dict[str, Dict[str, str]]): Direct prompt overrides by step name
        graph (Optional[CompiledGraph]): Compiled LangGraph state graph
        _llm_cache (Dict[str, BaseChatModel]): Cache of initialized LLM instances
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """
        Initialize the base agent.

        Args:
            llm_configs: Dictionary mapping role names to LLM configuration.
                        Example: {"thinking": {"provider": "openai", "model_name": "gpt-4"}}
            prompt_dir: Path to directory containing prompt templates
            custom_instructions: Optional custom instructions to append to all system prompts.
                               Useful for adding domain-specific context or constraints.
                               Example: "You are a medical expert. Always cite sources."
            prompt_overrides: Optional dictionary to programmatically override specific prompts.
                            Format: {"StepName": {"system": "custom system prompt", "user": "custom user prompt"}}
                            Example: {"ThoughtStep": {"system": "Think like a scientist"}}
        """
        self.llm_configs = llm_configs
        self.prompt_dir = prompt_dir
        self.custom_instructions = custom_instructions
        self.prompt_overrides = prompt_overrides or {}
        self.graph: Optional[CompiledStateGraph] = None
        self._llm_cache: Dict[str, BaseChatModel] = {}

        # Build the graph after initialization
        self.build_graph()

    @abc.abstractmethod
    def build_graph(self) -> None:
        """
        Construct or compile the LangGraph used by this agent pattern.

        This method must be implemented by subclasses to define the specific
        state graph structure for their pattern. The graph should be stored
        in self.graph after compilation.

        Example:
            def build_graph(self) -> None:
                sg = StateGraph()
                sg.add_node("step1", func=self._step1)
                sg.add_node("step2", func=self._step2)
                sg.add_edge("step1", "step2")
                self.graph = sg.compile()
        """
        pass

    @abc.abstractmethod
    def run(self, input_data: Any) -> Any:
        """
        Run the agent to completion with the given input.

        This is the main entry point for executing the agent pattern. Subclasses
        must implement this method to define how the graph is invoked and how
        the final result is extracted.

        Args:
            input_data: The user query, problem statement, or initial state

        Returns:
            The final output or answer from the agent execution

        Example:
            def run(self, input_data: str) -> str:
                initial_state = {"input": input_data, "output": None}
                final_state = self.graph.invoke(initial_state)
                return final_state["output"]
        """
        pass

    def stream(self, input_data: Any) -> Iterator[Any]:
        """
        Optional streaming interface for incremental results.

        Default implementation just yields the final result from run().
        Subclasses can override this to provide true streaming behavior.

        Args:
            input_data: The user query or initial state

        Yields:
            Incremental results or final result
        """
        yield self.run(input_data)

    def _get_llm(self, role: str) -> BaseChatModel:
        """
        Get or create an LLM instance for the specified role.

        This method manages LLM initialization and caching. It supports multiple
        providers (OpenAI, Anthropic) and can be extended for others.

        Args:
            role: The role name (e.g., "thinking", "reflection", "documentation")

        Returns:
            An initialized LangChain chat model

        Raises:
            ValueError: If the role is not configured or provider is unsupported
            KeyError: If required configuration keys are missing
        """
        # Return cached instance if available
        if role in self._llm_cache:
            return self._llm_cache[role]

        # Get configuration for this role
        if role not in self.llm_configs:
            raise ValueError(
                f"No configuration found for role '{role}'. "
                f"Available roles: {list(self.llm_configs.keys())}"
            )

        config = self.llm_configs[role]
        provider = config.get("provider", "").lower()
        model_name = config.get("model_name")

        if not model_name:
            raise KeyError(f"'model_name' is required in configuration for role '{role}'")

        # Extract optional parameters
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 2000)

        # Initialize LLM based on provider
        llm: BaseChatModel

        if provider == "openai":
            llm = ChatOpenAI(
                model=model_name, temperature=temperature, max_tokens=max_tokens
            )
        elif provider == "anthropic":
            llm = ChatAnthropic(
                model=model_name, temperature=temperature, max_tokens=max_tokens
            )
        else:
            raise ValueError(
                f"Unsupported provider '{provider}' for role '{role}'. "
                f"Supported providers: openai, anthropic"
            )

        # Cache and return
        self._llm_cache[role] = llm
        return llm

    def _load_prompt(self, step_name: str) -> Dict[str, str]:
        """
        Load prompt templates for a specific step from the prompts directory.

        Checks for programmatic overrides first, then falls back to file system.
        Appends custom_instructions to system prompts if provided.

        Looks for system.md and user.md files in the pattern-specific subdirectory.
        Pattern structure: prompts/{ClassName}/{StepName}/system.md

        Args:
            step_name: Name of the step (e.g., "ThoughtStep", "Generate", "Reflect")

        Returns:
            Dictionary with 'system' and 'user' keys containing prompt text.
            Returns empty strings if files don't exist and no overrides provided.

        Example:
            prompts = self._load_prompt("ThoughtStep")
            system_prompt = prompts["system"]
            user_prompt = prompts["user"]
        """
        system_prompt = ""
        user_prompt = ""

        # Priority 1: Check for programmatic overrides
        if step_name in self.prompt_overrides:
            override = self.prompt_overrides[step_name]
            system_prompt = override.get("system", "")
            user_prompt = override.get("user", "")
        else:
            # Priority 2: Load from file system (existing behavior)
            class_name = self.__class__.__name__
            prompt_path = Path(self.prompt_dir) / class_name / step_name

            # Load system prompt
            system_file = prompt_path / "system.md"
            if system_file.exists():
                system_prompt = system_file.read_text(encoding="utf-8").strip()

            # Load user prompt
            user_file = prompt_path / "user.md"
            if user_file.exists():
                user_prompt = user_file.read_text(encoding="utf-8").strip()

        # Append custom instructions to system prompt if provided
        if self.custom_instructions and system_prompt:
            system_prompt = f"{system_prompt}\n\n## Custom Instructions\n\n{self.custom_instructions}"

        return {"system": system_prompt, "user": user_prompt}

    def on_start(self, input_data: Any) -> None:
        """
        Lifecycle hook called before agent execution starts.

        Subclasses can override this for logging, monitoring, or setup tasks.

        Args:
            input_data: The initial input to the agent
        """
        pass

    def on_finish(self, result: Any) -> None:
        """
        Lifecycle hook called after agent execution completes.

        Subclasses can override this for logging, cleanup, or post-processing.

        Args:
            result: The final result from the agent
        """
        pass

    def on_error(self, error: Exception) -> None:
        """
        Lifecycle hook called when an error occurs during execution.

        Subclasses can override this for error logging or recovery.

        Args:
            error: The exception that was raised
        """
        pass
