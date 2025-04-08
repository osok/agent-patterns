"""Base agent class for implementing reusable agent patterns."""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Generator

from langgraph.graph import StateGraph


class BaseAgent:
    """Abstract base class for implementing reusable agent patterns.
    
    Attributes:
        llm_configs (Dict[str, Dict[str, Any]]): Dictionary mapping role names to LLM configurations.
            Example: {"default": {"provider": "openai", "model": "gpt-4"}}
        prompt_dir (str): Directory containing prompt templates.
        graph (Optional[StateGraph]): The LangGraph state graph for this agent.
    """

    def __init__(self, llm_configs: Dict[str, Dict[str, Any]], prompt_dir: str):
        """Initialize the base agent.
        
        Args:
            llm_configs: Dictionary mapping role names to LLM configurations.
            prompt_dir: Directory containing prompt templates.
        """
        self.llm_configs = llm_configs
        self.prompt_dir = prompt_dir
        self._llm_cache: Dict[str, Any] = {}
        self.graph: Optional[StateGraph] = None
        self.build_graph()
        if self.graph is None:
            raise ValueError("build_graph() must set self.graph")

    def build_graph(self) -> None:
        """Build and set the LangGraph state graph for this agent.
        
        This method must be implemented by subclasses to define the agent's workflow.
        The implementation must set self.graph to a compiled StateGraph.
        """
        raise NotImplementedError("Subclasses must implement build_graph()")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent on the given input data.
        
        Args:
            input_data: Input data for the agent.
            
        Returns:
            The agent's output.
            
        Raises:
            RuntimeError: If graph is not built before calling run.
        """
        if self.graph is None:
            raise RuntimeError("Must call build_graph() before run()")
        return self.graph.run(input_data)

    def stream(self, input_data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """Stream results from the agent's execution.
        
        Args:
            input_data: Input data for the agent.
            
        Yields:
            Intermediate results from the agent's execution.
            
        Raises:
            RuntimeError: If graph is not built before calling stream.
        """
        if self.graph is None:
            raise RuntimeError("Must call build_graph() before stream()")
        yield from self.graph.stream(input_data)

    def _get_llm(self, role: str = "default") -> Any:
        """Get a configured LLM instance for the given role.
        
        Args:
            role: The role to get the LLM for.
            
        Returns:
            The configured LLM instance.
            
        Raises:
            ValueError: If the role or provider is not supported.
        """
        if role not in self.llm_configs:
            raise ValueError(f"Role {role} not found in llm_configs")

        if role in self._llm_cache:
            return self._llm_cache[role]

        config = self.llm_configs[role]
        provider = config.get("provider", "openai").lower()

        if provider == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(**config)
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(**config)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        self._llm_cache[role] = llm
        return llm

    def _load_prompt(self, template_name: str) -> Dict[str, str]:
        """Load prompt templates from the prompt directory.
        
        Args:
            template_name: Name of the template.
            
        Returns:
            Dictionary containing 'system' and 'user' prompts.
            
        Raises:
            FileNotFoundError: If any template file does not exist.
        """
        prompts = {}
        template_dir = Path(self.prompt_dir) / self.__class__.__name__ / template_name
        
        for prompt_type in ["system", "user"]:
            prompt_path = template_dir / f"{prompt_type}.md"
            if not prompt_path.exists():
                raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
            prompts[prompt_type] = prompt_path.read_text().strip()
        
        return prompts

    def on_start(self) -> None:
        """Optional lifecycle hook called before agent execution starts."""
        pass

    def on_finish(self) -> None:
        """Optional lifecycle hook called after agent execution finishes."""
        pass