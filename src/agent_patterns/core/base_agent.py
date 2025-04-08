"""Base agent class for implementing reusable agent patterns."""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Generator, Union, List, Tuple
import abc # Use abc for abstract base class

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
    """

    def __init__(
        self, 
        prompt_dir: str, 
        llm_configs: Dict[str, Dict], # Expect llm_configs dict
        log_level: int = logging.INFO
    ):
        """Initialize the base agent.
        
        Args:
            prompt_dir: Directory containing prompt templates (relative to project root).
            llm_configs: Dictionary specifying provider, model, and roles. 
                         Example: {'default': {'provider': 'openai', 'model': 'gpt-4o-mini'}}
            log_level: Logging level (default: logging.INFO)
        """
        self.prompt_dir = prompt_dir
        self.llm_configs = llm_configs
        self.graph: Optional[Any] = None # Use Any type hint for compiled graph for simplicity
        self._llm_cache: Dict[str, BaseLanguageModel] = {} # Initialize LLM cache
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__) # Use class name for logger
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.info("Initializing agent with prompt directory: %s", self.prompt_dir)
        self.build_graph() # Call build_graph during init as per design
        if self.graph is None: # Check if graph was set after build_graph
            self.logger.error("build_graph() failed to set self.graph")
            raise ValueError("build_graph() must set self.graph to a compiled StateGraph")
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

    def _get_llm(self, role: str = "default") -> BaseLanguageModel:
        """Get or create a configured LLM instance for the given role based on llm_configs.
        
        Args:
            role: The role name (key in llm_configs) to get the LLM for.
            
        Returns:
            The configured LLM instance.
            
        Raises:
            ValueError: If the role is not found or provider is not supported.
            ImportError: If required LLM provider packages are not installed.
        """
        if role not in self.llm_configs:
            self.logger.error("Requested unknown LLM role: '%s'. Available roles: %s", role, list(self.llm_configs.keys()))
            raise ValueError(f"Role '{role}' not found in llm_configs")

        if role in self._llm_cache:
            self.logger.debug("Retrieved cached LLM for role: %s", role)
            return self._llm_cache[role]

        self.logger.debug("Configuring new LLM for role: %s", role)
        config = self.llm_configs[role].copy()
        provider = config.pop("provider", "openai").lower()
        model_name = config.pop("model", None) # 'model' is often the main arg
        if not model_name:
             model_name = config.pop("model_name", None) # Fallback to model_name
             if not model_name:
                 raise ValueError(f"Missing 'model' or 'model_name' in llm_configs for role '{role}'")

        # Remaining items in config are passed as kwargs (e.g., temperature)
        model_kwargs = config 

        try:
            llm: BaseLanguageModel
            if provider == "openai":
                from langchain_openai import ChatOpenAI
                # Ensure API key is set (example, could use env vars or other methods)
                if "OPENAI_API_KEY" not in os.environ:
                     self.logger.warning("OPENAI_API_KEY environment variable not set.")
                     # raise ValueError("OPENAI_API_KEY must be set for OpenAI provider")
                llm = ChatOpenAI(model=model_name, **model_kwargs)
            elif provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                 # Ensure API key is set
                if "ANTHROPIC_API_KEY" not in os.environ:
                    self.logger.warning("ANTHROPIC_API_KEY environment variable not set.")
                    # raise ValueError("ANTHROPIC_API_KEY must be set for Anthropic provider")
                llm = ChatAnthropic(model=model_name, **model_kwargs)
            # Add other providers as needed (e.g., Google VertexAI, HuggingFace)
            # elif provider == "google":
            #     from langchain_google_vertexai import ChatVertexAI
            #     llm = ChatVertexAI(model_name=model_name, **model_kwargs)
            else:
                self.logger.error("Unsupported LLM provider: %s", provider)
                raise ValueError(f"Unsupported LLM provider: {provider}")
            
            self._llm_cache[role] = llm
            self.logger.debug("Successfully configured LLM '%s' (%s) for role: %s", model_name, provider, role)
            return llm
            
        except ImportError as e:
            self.logger.error("Failed to import package for LLM provider '%s'. Please install it. Error: %s", provider, e)
            raise ImportError(f"Package for LLM provider '{provider}' not found. Please install the required package (e.g., pip install langchain-openai).") from e
        except Exception as e:
            self.logger.error("Failed to configure LLM for role '%s' with provider '%s': %s", role, provider, str(e))
            raise ValueError(f"Failed to configure LLM for role '{role}': {str(e)}") from e


    def _load_prompt_template(self, step_name: str) -> ChatPromptTemplate:
        """Loads system and user prompts for a step and returns a ChatPromptTemplate.
        
        Expects prompts in: <prompt_dir>/<ClassName>/<step_name>/{system.md, user.md}
        
        Args:
            step_name: Name of the step (sub-directory name).
            
        Returns:
            A ChatPromptTemplate instance.
            
        Raises:
            FileNotFoundError: If expected prompt files are missing.
        """
        self.logger.debug("Loading prompt template for step: %s", step_name)
        class_name = self.__class__.__name__
        template_dir = Path(self.prompt_dir) / class_name / step_name
        
        system_path = template_dir / "system.md"
        user_path = template_dir / "user.md"
        
        if not system_path.exists():
            self.logger.error("Missing system prompt template: %s", system_path)
            raise FileNotFoundError(f"System prompt template not found: {system_path}")
        if not user_path.exists():
             self.logger.error("Missing user prompt template: %s", user_path)
             raise FileNotFoundError(f"User prompt template not found: {user_path}")
            
        try:
            system_prompt = system_path.read_text().strip()
            user_prompt = user_path.read_text().strip()
            self.logger.debug("Loaded prompts from: %s", template_dir)
            
            # Create ChatPromptTemplate
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", user_prompt) # Assumes user prompt contains placeholders like {input}, {history} etc.
            ])
            return prompt_template

        except Exception as e:
            self.logger.error("Failed to load or parse prompts from %s: %s", template_dir, str(e))
            raise ValueError(f"Error loading prompts for step '{step_name}': {e}") from e


    # --- Lifecycle Hooks (as per design doc) ---

    def on_start(self) -> None:
        """Optional lifecycle hook called before agent execution starts."""
        self.logger.debug("Agent execution starting")

    def on_finish(self) -> None:
        """Optional lifecycle hook called after agent execution finishes."""
        self.logger.debug("Agent execution finished")