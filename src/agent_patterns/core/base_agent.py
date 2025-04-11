"""Base agent class for implementing reusable agent patterns."""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Generator, Union, List, Tuple
import abc # Use abc for abstract base class
import importlib.util
import asyncio

from langgraph.graph import StateGraph
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate # For prompt handling

class BaseAgent(abc.ABC): # Inherit from abc.ABC
    """Abstract base class for implementing reusable agent patterns.
    
    Attributes:
        prompt_dir (str): Directory containing prompt templates relative to project root.
        graph (Optional[Any]): The compiled LangGraph state graph. Type set to Any after compile().
        logger (logging.Logger): Logger instance for this agent.
        llm_configs (Dict[str, Dict]): Configuration for different LLM roles.
        _llm_cache (Dict[str, BaseLanguageModel]): Cache for instantiated LLMs.
        tool_provider (Optional[Any]): Provider for tools the agent can use.
        memory (Optional[Any]): Memory system for the agent.
        memory_config (Dict[str, bool]): Configuration of which memory types to use.
    """

    def __init__(
        self, 
        llm_configs: Dict[str, Any],
        prompt_dir: str = "src/agent_patterns/prompts",
        tool_provider: Optional[Any] = None,
        memory: Optional[Any] = None,
        memory_config: Optional[Dict[str, bool]] = None,
        log_level: int = logging.INFO
    ):
        """
        Initialize the base agent.
        
        Args:
            llm_configs: Dictionary mapping role names to LLM configurations.
                Each config can be either a direct LLM instance or a
                dictionary with configurations to create an LLM.
            prompt_dir: Directory containing prompt templates.
            tool_provider: Optional provider for tools the agent can use.
            memory: Optional composite memory instance.
            memory_config: Configuration for which memory types to use.
            log_level: Logging level.
        """
        # Configure logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        
        # Ensure handler exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
        # Store configurations
        self.llm_configs = llm_configs
        self.prompt_dir = prompt_dir
        self.tool_provider = tool_provider
        self.memory = memory
        self.memory_config = memory_config or {
            "semantic": True,
            "episodic": True,
            "procedural": False  # Off by default as it's more experimental
        }
        
        # Initialize LLM cache
        self._llm_cache = {}
        
        # Log initialization
        self.logger.info(f"Initializing agent with prompt directory: {prompt_dir}")
        if tool_provider:
            self.logger.info(f"Agent using tool provider: {tool_provider.__class__.__name__}")
        if memory:
            memory_types = ", ".join(memory.memories.keys())
            self.logger.info(f"Agent using memory types: {memory_types}")
            self.logger.info(f"Memory configuration: {self.memory_config}")
        
        # Build the graph
        self.graph = None
        self.build_graph()
        
        # Verify the graph was built
        if self.graph is None:
            raise ValueError("build_graph() must set self.graph. The graph cannot be None.")
        
        self.logger.info("Agent initialization complete")

    @abc.abstractmethod # Mark as abstract
    def build_graph(self) -> None:
        """Build and compile the LangGraph state graph for this agent.
        
        This method must be implemented by subclasses.
        The implementation *must* set `self.graph` to a `CompiledGraph` instance.
        """
        pass

    # Keep run and stream as placeholders for now, subclasses define actual logic
    @abc.abstractmethod
    def run(self, input_data: Any) -> Any:
        """Run the agent to completion with the given input.
        
        Args:
            input_data: The user query or initial state.
            
        Returns:
            The final output or answer.
        """
        pass

    def stream(self, input_data: Any) -> Generator[Any, None, None]:
        """Optional streaming interface. Subclasses can override."""
        self.logger.info("Streaming not explicitly implemented for %s, falling back to run()", self.__class__.__name__)
        yield self.run(input_data) # Default fallback

    def _get_llm(self, role: str = "default") -> Any:
        """
        Get the LLM for the specified role.
        
        Args:
            role: The role name to get the LLM for.
            
        Returns:
            The initialized LLM.
            
        Raises:
            ValueError: If the role is not configured or LLM initialization fails.
        """
        # Check if the LLM is already cached
        if role in self._llm_cache:
            return self._llm_cache[role]
            
        if role not in self.llm_configs:
            available_roles = ", ".join(self.llm_configs.keys())
            if "default" in self.llm_configs:
                self.logger.warning(f"Role '{role}' not found. Using 'default' role instead. Available roles: {available_roles}")
                role = "default"
            else:
                raise ValueError(f"Role '{role}' not found in llm_configs and no default fallback. Available roles: {available_roles}")
        
        # Get the LLM configuration
        config = self.llm_configs[role]
        
        # If config is already an LLM instance, just return it
        if hasattr(config, "invoke") or hasattr(config, "__call__"):
            self._llm_cache[role] = config
            return config
            
        # Otherwise, assume it's a config dict that needs to be used to create an LLM
        if not isinstance(config, dict):
            raise ValueError(f"LLM config for role '{role}' must be an LLM instance or a dict, got {type(config)}")
            
        config = config.copy()  # Make a copy to avoid modifying the original
        
        # Get the LLM provider and model
        provider = config.pop("provider", "openai").lower()
        model = config.pop("model_name", config.pop("model", "gpt-4o"))
        
        # Import the appropriate module for the provider
        if provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model=model, **config)
                self._llm_cache[role] = llm
                return llm
            except ImportError:
                raise ImportError("langchain-openai not installed. Please install it with: pip install langchain-openai")
        elif provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
                llm = ChatAnthropic(model=model, **config)
                self._llm_cache[role] = llm
                return llm
            except ImportError:
                raise ImportError("langchain-anthropic not installed. Please install it with: pip install langchain-anthropic")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _load_prompt_template(self, name: str) -> Any:
        """
        Load a prompt template for the specified name.
        
        First tries to load from files in the prompt directory structure:
        - {prompt_dir}/{class_name}/{name}/system.md
        - {prompt_dir}/{class_name}/{name}/user.md
        
        If files don't exist, falls back to built-in templates.
        
        Args:
            name: Name of the prompt template.
            
        Returns:
            A prompt template suitable for the LLM.
            
        Raises:
            FileNotFoundError: If prompt files don't exist and no fallback is available.
        """
        from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
        
        class_name = self.__class__.__name__
        
        # Try to load from files first
        if self.prompt_dir:
            # Construct paths to system and user prompt files
            class_prompt_dir = os.path.join(self.prompt_dir, class_name, name)
            system_path = os.path.join(class_prompt_dir, "system.md")
            user_path = os.path.join(class_prompt_dir, "user.md")
            
            # Check if both files exist
            if os.path.exists(system_path) and os.path.exists(user_path):
                # Load system prompt
                with open(system_path, "r") as f:
                    system_content = f.read()
                
                # Load user prompt
                with open(user_path, "r") as f:
                    user_content = f.read()
                
                # Create template from loaded content
                return ChatPromptTemplate.from_messages([
                    SystemMessagePromptTemplate.from_template(system_content),
                    HumanMessagePromptTemplate.from_template(user_content)
                ])
        
        # For nonexistent steps that aren't covered by fallbacks, raise an error
        if name not in ["PlannerPrompt", "SolverPrompt", "FinalAnswerPrompt"]:
            raise FileNotFoundError(
                f"Prompt template '{name}' not found for {class_name}. "
                f"Expected files at {self.prompt_dir}/{class_name}/{name}/system.md and "
                f"{self.prompt_dir}/{class_name}/{name}/user.md"
            )
        
        # Fallback for common templates
        if name == "PlannerPrompt":
            return ChatPromptTemplate.from_messages([
                {"role": "system", "content": f"You are a planning agent responsible for creating a step-by-step plan to answer the user's query. Do not execute the plan or use tools directly - just create the plan."},
                {"role": "user", "content": "Create a detailed plan to answer this query:\n\n{input}\n\nFormat your response as numbered steps."}
            ])
        elif name == "SolverPrompt":
            return ChatPromptTemplate.from_messages([
                {"role": "system", "content": f"You are an execution agent responsible for completing individual steps of a plan."},
                {"role": "user", "content": "Execute this step:\n\n{step_description}\n\nAdditional details: {step_details}\n\nPrevious context: {context}"}
            ])
        elif name == "FinalAnswerPrompt":
            return ChatPromptTemplate.from_messages([
                {"role": "system", "content": f"You are a final answer agent responsible for synthesizing the results of all steps into a coherent response."},
                {"role": "user", "content": "Using the following execution steps, provide a comprehensive answer to the original query:\n\nOriginal query: {input}\n\nExecution summary:\n{execution_summary}"}
            ])
        else:
            # Should never get here because of the earlier check, but just in case
            raise FileNotFoundError(f"Prompt template '{name}' not found and no fallback available.")

    async def _retrieve_memories(self, query: str) -> Dict[str, List[Any]]:
        """
        Retrieve relevant memories for a query.
        
        Args:
            query: The input query or context
            
        Returns:
            Dictionary mapping memory types to retrieved items
        """
        if not self.memory:
            return {}
            
        # Filter enabled memory types
        enabled_memories = {
            k: v for k, v in self.memory.memories.items()
            if self.memory_config.get(k, False)
        }
        
        if not enabled_memories:
            return {}
            
        # Create a filtered composite memory
        from .memory import CompositeMemory
        filtered_memory = CompositeMemory(enabled_memories)
        
        # Retrieve from all enabled memories
        return await filtered_memory.retrieve_all(query)
    
    def sync_retrieve_memories(self, query: str) -> Dict[str, List[Any]]:
        """Synchronous wrapper for _retrieve_memories."""
        return asyncio.run(self._retrieve_memories(query))
    
    async def _save_memory(self, memory_type: str, item: Any, **metadata) -> Optional[str]:
        """
        Save an item to a specific memory type if enabled.
        
        Args:
            memory_type: Which memory to save to
            item: The item to save
            **metadata: Additional metadata
            
        Returns:
            A unique identifier for the saved item, or None if memory type is disabled
        """
        if not self.memory or not self.memory_config.get(memory_type, False):
            return None
            
        return await self.memory.save_to(memory_type, item, **metadata)
    
    def sync_save_memory(self, memory_type: str, item: Any, **metadata) -> Optional[str]:
        """Synchronous wrapper for _save_memory."""
        return asyncio.run(self._save_memory(memory_type, item, **metadata))

    # --- Lifecycle Hooks (as per design doc) ---

    def on_start(self) -> None:
        """Optional lifecycle hook called before agent execution starts."""
        self.logger.debug("Agent execution starting")

    def on_finish(self) -> None:
        """Optional lifecycle hook called after agent execution finishes."""
        self.logger.debug("Agent execution finished")