"""Self-Discovery agent pattern implementation."""

import json
import operator
from typing import Any, Dict, List, Optional, Union, TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import logging
from pathlib import Path

from agent_patterns.core.base_agent import BaseAgent

# Define the state according to LangGraph best practices
class SelfDiscoveryState(TypedDict):
    """Represents the state of the Self-Discovery agent.

    Attributes:
        input: The task or problem to solve.
        chat_history: The history of messages in the conversation.
        reasoning_modules: The collection of atomic reasoning modules.
        selected_modules: The modules selected for this specific task.
        adapted_modules: The selected modules adapted to the task.
        reasoning_structure: The composed reasoning structure to follow.
        execution_result: The result of executing the reasoning structure.
        final_answer: The final answer to the task.
    """
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    reasoning_modules: List[Dict[str, str]]
    selected_modules: Optional[List[str]]
    adapted_modules: Optional[List[str]]
    reasoning_structure: Optional[Dict[str, Any]]
    execution_result: Optional[str]
    final_answer: Optional[str]


class SelfDiscoveryAgent(BaseAgent):
    """Self-Discovery pattern implementation using LangGraph.
    
    This agent follows a two-stage approach:
    1. Discovery Stage: Self-discover a reasoning structure for the task
       - SELECT relevant reasoning modules
       - ADAPT modules to be task-specific
       - IMPLEMENT structure with adapted modules
    2. Execution Stage: Solve the task by following the composed structure
    
    The primary benefit of this approach is improved problem-solving for complex tasks
    by composing multiple reasoning approaches tailored to the specific task.
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict],
        reasoning_modules_path: Optional[str] = None,
        prompt_dir: str = "src/agent_patterns/prompts",
        tool_provider: Optional[Any] = None,
        memory: Optional[Any] = None,
        memory_config: Optional[Dict[str, bool]] = None,
        log_level: int = logging.INFO
    ):
        """Initialize the Self-Discovery agent.
        
        Args:
            llm_configs: Configuration for LLM roles (e.g., {'discovery': {...}, 'execution': {...}}).
            reasoning_modules_path: Path to JSON file containing reasoning modules (optional).
            prompt_dir: Directory containing prompt templates (relative to project root).
            tool_provider: Optional provider for tools the agent can use.
            memory: Optional composite memory instance.
            memory_config: Configuration for which memory types to use.
            log_level: Logging level.
        """
        # Call BaseAgent init
        super().__init__(
            llm_configs=llm_configs, 
            prompt_dir=prompt_dir, 
            tool_provider=tool_provider,
            memory=memory,
            memory_config=memory_config,
            log_level=log_level
        )
        
        # Initialize the LLMs for discovery and execution
        try:
            self.discovery_llm = self._get_llm('discovery')
            self.execution_llm = self._get_llm('execution')
        except ValueError as e:
            self.logger.error("Failed to initialize LLMs: %s", e)
            raise ValueError("LLM initialization failed. Make sure 'discovery' and 'execution' roles are defined in llm_configs.") from e

        # Load reasoning modules
        self.reasoning_modules = self._load_reasoning_modules(reasoning_modules_path)
        
        self.logger.info("Initialized Self-Discovery agent with %d reasoning modules", len(self.reasoning_modules))

    def _load_reasoning_modules(self, custom_path=None) -> List[Dict[str, str]]:
        """Load reasoning modules from a JSON file.
        
        Args:
            custom_path: Optional custom path to the reasoning modules JSON file.
            
        Returns:
            List of reasoning module dictionaries.
        """
        try:
            # Default path in the prompts directory
            default_path = Path(self.prompt_dir) / "SelfDiscoveryAgent" / "reasoning_modules.json"
            
            # Use custom path if provided
            if custom_path:
                path = Path(custom_path)
            else:
                path = default_path
                
            # Create default modules if file doesn't exist
            if not path.exists():
                self.logger.warning("Reasoning modules file not found at %s, using default modules", path)
                return self._get_default_reasoning_modules()
                
            # Load modules from file
            with open(path, 'r', encoding='utf-8') as f:
                modules = json.load(f)
                
            self.logger.info("Loaded %d reasoning modules from %s", len(modules), path)
            return modules
            
        except Exception as e:
            self.logger.error("Error loading reasoning modules: %s", e)
            self.logger.info("Falling back to default reasoning modules")
            return self._get_default_reasoning_modules()
    
    def _get_default_reasoning_modules(self) -> List[Dict[str, str]]:
        """Get a default set of reasoning modules if the file is not available.
        
        Returns:
            List of reasoning module dictionaries.
        """
        return [
            {
                "name": "Critical Thinking",
                "description": "This style involves analyzing the problem from different perspectives, questioning assumptions, and evaluating the evidence or information available."
            },
            {
                "name": "Step by Step Thinking",
                "description": "Let's think step by step to break down the problem into manageable parts and solve each part in sequence."
            },
            {
                "name": "Decomposition",
                "description": "Break down complex problems into smaller, more manageable sub-problems."
            },
            {
                "name": "Analogical Reasoning",
                "description": "Draw parallels between the current problem and similar problems encountered in the past."
            },
            {
                "name": "First Principles Thinking",
                "description": "Break down complex problems into their most basic elements and reassemble them from the ground up."
            },
            {
                "name": "Counterfactual Reasoning",
                "description": "Consider alternative scenarios or outcomes by changing certain factors."
            },
            {
                "name": "Reflective Thinking",
                "description": "Step back from the problem, take the time for introspection and self-reflection."
            },
            {
                "name": "Logical Analysis",
                "description": "Apply formal logic rules to analyze the problem methodically."
            }
        ]

    def build_graph(self) -> None:
        """Build the LangGraph state graph for the Self-Discovery agent.
        
        The graph consists of two main stages:
        1. Discovery Stage: Select, adapt, and implement a reasoning structure
        2. Execution Stage: Execute the structure and format the final answer
        """
        # Create the graph with our state type
        self_discovery_graph = StateGraph(SelfDiscoveryState)

        # Define nodes for Discovery Stage
        self_discovery_graph.add_node("select_modules", self._select_reasoning_modules)
        self_discovery_graph.add_node("adapt_modules", self._adapt_reasoning_modules)
        self_discovery_graph.add_node("implement_structure", self._implement_reasoning_structure)
        
        # Define nodes for Execution Stage
        self_discovery_graph.add_node("execute_structure", self._execute_reasoning_structure)
        self_discovery_graph.add_node("format_final_answer", self._format_final_answer)

        # Define edges
        self_discovery_graph.set_entry_point("select_modules")
        self_discovery_graph.add_edge("select_modules", "adapt_modules")
        self_discovery_graph.add_edge("adapt_modules", "implement_structure")
        self_discovery_graph.add_edge("implement_structure", "execute_structure")
        self_discovery_graph.add_edge("execute_structure", "format_final_answer")
        self_discovery_graph.add_edge("format_final_answer", END)
        
        # Compile the graph
        try:
            self.graph = self_discovery_graph.compile()
            self.logger.info("Self-Discovery agent graph compiled successfully.")
        except Exception as e:
            self.logger.error("Failed to compile Self-Discovery agent graph: %s", e)
            raise RuntimeError("Graph compilation failed") from e

    def _select_reasoning_modules(self, state: SelfDiscoveryState) -> Dict[str, Union[List[str], Sequence[BaseMessage]]]:
        """Select relevant reasoning modules for the given task.
        
        This is the first step of the discovery stage, where the agent selects
        which reasoning modules are most appropriate for the task.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with selected reasoning modules.
        """
        self.logger.debug("Selecting reasoning modules for task: %s", state["input"])
        
        try:
            # Retrieve relevant memories if memory is enabled
            memory_context = ""
            if self.memory:
                memories = self.sync_retrieve_memories(state["input"])
                
                # Format memories for inclusion in the prompt
                if memories:
                    memory_sections = []
                    for memory_type, items in memories.items():
                        if items:
                            items_text = "\n- ".join([str(item) for item in items])
                            memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                    
                    if memory_sections:
                        memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                        self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for module selection")
            
            # Load the selection prompt template
            prompt = self._load_prompt_template("Select")
            
            # Format modules as a numbered list for the prompt
            modules_text = "\n".join([f"{i+1}. {module['name']}: {module['description']}" 
                                    for i, module in enumerate(state["reasoning_modules"])])
            
            # Format the prompt with the task and available modules
            formatted_prompt = prompt.invoke({
                "task": state["input"],
                "reasoning_modules": modules_text,
                "memory_context": memory_context
            })
            
            # Get the selection response
            selection_response = self.discovery_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the content from the response
            selection_text = selection_response.content
            
            # Parse the selected modules from the response text
            # This assumes the LLM will output a list of selected modules
            selected_modules = self._parse_selected_modules(selection_text)
            
            # Update chat history
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content=f"Select reasoning modules for task: {state['input']}")
            ai_message = AIMessage(content=selection_text)
            new_history = chat_history + [human_message, ai_message]
            
            self.logger.debug("Selected %d reasoning modules", len(selected_modules))
            
            return {
                "selected_modules": selected_modules,
                "chat_history": new_history
            }
            
        except Exception as e:
            self.logger.error("Error selecting reasoning modules: %s", e)
            # Fallback to a subset of default modules
            fallback_modules = [
                "Step by Step Thinking",
                "Critical Thinking",
                "Decomposition"
            ]
            return {
                "selected_modules": fallback_modules,
                "chat_history": state.get("chat_history", [])
            }
    
    def _parse_selected_modules(self, selection_text: str) -> List[str]:
        """Parse the selected modules from the LLM response.
        
        Args:
            selection_text: The raw text from the LLM.
            
        Returns:
            List of selected module names.
        """
        # This is a simple parsing implementation that extracts module names
        # A more robust implementation might use regex patterns or structured output parsing
        lines = selection_text.split('\n')
        selected_modules = []
        
        for line in lines:
            line = line.strip()
            # Look for lines with module names (often with numbers, bullet points, or quotes)
            for module in [m["name"] for m in self.reasoning_modules]:
                if module in line:
                    selected_modules.append(module)
                    break
        
        # If parsing failed, include some default modules
        if not selected_modules:
            self.logger.warning("Failed to parse selected modules, using default subset")
            selected_modules = ["Critical Thinking", "Step by Step Thinking"]
            
        return selected_modules

    def _adapt_reasoning_modules(self, state: SelfDiscoveryState) -> Dict[str, Union[List[str], Sequence[BaseMessage]]]:
        """Adapt the selected reasoning modules to the specific task.
        
        This is the second step of the discovery stage, where the agent adapts
        the selected reasoning modules to make them specific to the task.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with adapted reasoning modules.
        """
        self.logger.debug("Adapting reasoning modules to task")
        
        try:
            # Retrieve relevant memories if memory is enabled
            memory_context = ""
            if self.memory:
                memories = self.sync_retrieve_memories(state["input"])
                
                # Format memories for inclusion in the prompt
                if memories:
                    memory_sections = []
                    for memory_type, items in memories.items():
                        if items:
                            items_text = "\n- ".join([str(item) for item in items])
                            memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                    
                    if memory_sections:
                        memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                        self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for module adaptation")
            
            # Load the adaptation prompt template
            prompt = self._load_prompt_template("Adapt")
            
            # Format selected modules as a list for the prompt
            selected_modules_text = "\n".join([f"- {module}" for module in state["selected_modules"]])
            
            # Format the prompt
            formatted_prompt = prompt.invoke({
                "task": state["input"],
                "selected_modules": selected_modules_text,
                "memory_context": memory_context
            })
            
            # Get the adaptation response
            adaptation_response = self.discovery_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the content from the response
            adaptation_text = adaptation_response.content
            
            # The adaptation text contains the adapted descriptions
            # We'll store it as is for use in the next step
            adapted_modules = [adaptation_text]
            
            # Update chat history
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content=f"Adapt selected reasoning modules to the task")
            ai_message = AIMessage(content=adaptation_text)
            new_history = chat_history + [human_message, ai_message]
            
            self.logger.debug("Adapted reasoning modules for the task")
            
            return {
                "adapted_modules": adapted_modules,
                "chat_history": new_history
            }
            
        except Exception as e:
            self.logger.error("Error adapting reasoning modules: %s", e)
            # Fallback with generic adaptations
            fallback_adaptation = f"Apply the selected reasoning methods to solve '{state['input']}'"
            return {
                "adapted_modules": [fallback_adaptation],
                "chat_history": state.get("chat_history", [])
            }

    def _implement_reasoning_structure(self, state: SelfDiscoveryState) -> Dict[str, Union[Dict[str, Any], Sequence[BaseMessage]]]:
        """Implement the reasoning structure based on adapted modules.
        
        This is the third step of the discovery stage, where the agent creates
        a structured actionable plan for solving the task.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with implemented reasoning structure.
        """
        self.logger.debug("Implementing reasoning structure")
        
        try:
            # Retrieve relevant memories if memory is enabled
            memory_context = ""
            if self.memory:
                memories = self.sync_retrieve_memories(state["input"])
                
                # Format memories for inclusion in the prompt
                if memories:
                    memory_sections = []
                    for memory_type, items in memories.items():
                        if items:
                            items_text = "\n- ".join([str(item) for item in items])
                            memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                    
                    if memory_sections:
                        memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                        self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for structure implementation")
            
            # Get available tools information if tool_provider is available
            tools_context = ""
            if self.tool_provider:
                try:
                    provider_tools = self.tool_provider.list_tools()
                    if provider_tools:
                        tool_descriptions = []
                        for tool in provider_tools:
                            tool_name = tool.get("name", "")
                            tool_desc = tool.get("description", "")
                            tool_params = tool.get("parameters", {})
                            tool_descriptions.append(f"- {tool_name}: {tool_desc}")
                            if tool_params:
                                param_desc = str(tool_params).replace("{", "").replace("}", "")
                                tool_descriptions.append(f"  Parameters: {param_desc}")
                        
                        if tool_descriptions:
                            tools_context = "Available tools that you can use:\n" + "\n".join(tool_descriptions) + "\n\n"
                            tools_context += "To use these tools, clearly indicate in your response when you want to use a tool. Format your tool calls like this:\n"
                            tools_context += "TOOL: tool_name\nparam1: value1\nparam2: value2\n\n"
                            self.logger.info(f"Added {len(provider_tools)} tools from tool provider")
                except Exception as e:
                    self.logger.warning(f"Error retrieving tools from tool_provider: {str(e)}")
            
            # Load the implementation prompt template
            prompt = self._load_prompt_template("Implement")
            
            # Format the prompt with the task and adapted modules
            formatted_prompt = prompt.invoke({
                "task": state["input"],
                "adapted_modules": state["adapted_modules"][0] if state["adapted_modules"] else "",
                "memory_context": memory_context,
                "tools_context": tools_context
            })
            
            # Get the implementation response
            implementation_response = self.discovery_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the content from the response
            implementation_text = implementation_response.content
            
            # The implementation should be structured, ideally as a JSON-like structure
            # We'll parse it if it looks like JSON, otherwise treat it as text
            reasoning_structure = self._parse_reasoning_structure(implementation_text)
            
            # Update chat history
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content=f"Implement a reasoning structure for the task")
            ai_message = AIMessage(content=implementation_text)
            new_history = chat_history + [human_message, ai_message]
            
            self.logger.debug("Implemented reasoning structure")
            
            return {
                "reasoning_structure": reasoning_structure,
                "chat_history": new_history
            }
            
        except Exception as e:
            self.logger.error("Error implementing reasoning structure: %s", e)
            # Fallback with a simple structure
            fallback_structure = {
                "steps": [
                    "Break down the problem",
                    "Analyze each part critically",
                    "Solve step by step",
                    "Verify the solution"
                ]
            }
            return {
                "reasoning_structure": fallback_structure,
                "chat_history": state.get("chat_history", [])
            }
    
    def _parse_reasoning_structure(self, implementation_text: str) -> Dict[str, Any]:
        """Parse the reasoning structure from the LLM response.
        
        Args:
            implementation_text: The raw text from the LLM.
            
        Returns:
            Structured representation of the reasoning approach.
        """
        # Try to find and parse JSON content
        try:
            # Look for patterns that might indicate JSON content
            start_idx = implementation_text.find('{')
            end_idx = implementation_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = implementation_text[start_idx:end_idx+1]
                structure = json.loads(json_str)
                return structure
        except:
            # If JSON parsing fails, create a structure from the text
            pass
        
        # Fallback to a text-based structure
        lines = implementation_text.split('\n')
        steps = []
        
        # Extract numbered steps or bullet points
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                # Remove leading numbers, bullets, or dashes
                cleaned_line = line
                while cleaned_line and not cleaned_line[0].isalpha():
                    cleaned_line = cleaned_line[1:].strip()
                if cleaned_line:
                    steps.append(cleaned_line)
        
        # If we couldn't extract steps, use the whole text
        if not steps:
            return {"plan": implementation_text}
            
        return {"steps": steps}

    def _execute_reasoning_structure(self, state: SelfDiscoveryState) -> Dict[str, Union[str, Sequence[BaseMessage]]]:
        """Execute the reasoning structure to solve the task.
        
        This is the main step of the execution stage, where the agent follows
        the self-discovered reasoning structure to solve the problem.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with execution result.
        """
        self.logger.debug("Executing reasoning structure")
        
        try:
            # Retrieve relevant memories if memory is enabled
            memory_context = ""
            if self.memory:
                memories = self.sync_retrieve_memories(state["input"])
                
                # Format memories for inclusion in the prompt
                if memories:
                    memory_sections = []
                    for memory_type, items in memories.items():
                        if items:
                            items_text = "\n- ".join([str(item) for item in items])
                            memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                    
                    if memory_sections:
                        memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                        self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for execution")
            
            # Get available tools information if tool_provider is available
            tools_context = ""
            if self.tool_provider:
                try:
                    provider_tools = self.tool_provider.list_tools()
                    if provider_tools:
                        tool_descriptions = []
                        for tool in provider_tools:
                            tool_name = tool.get("name", "")
                            tool_desc = tool.get("description", "")
                            tool_params = tool.get("parameters", {})
                            tool_descriptions.append(f"- {tool_name}: {tool_desc}")
                            if tool_params:
                                param_desc = str(tool_params).replace("{", "").replace("}", "")
                                tool_descriptions.append(f"  Parameters: {param_desc}")
                        
                        if tool_descriptions:
                            tools_context = "Available tools that you can use:\n" + "\n".join(tool_descriptions) + "\n\n"
                            tools_context += "To use these tools, clearly indicate in your response when you want to use a tool. Format your tool calls like this:\n"
                            tools_context += "TOOL: tool_name\nparam1: value1\nparam2: value2\n\n"
                            self.logger.info(f"Added {len(provider_tools)} tools from tool provider")
                except Exception as e:
                    self.logger.warning(f"Error retrieving tools from tool_provider: {str(e)}")
            
            # Load the execution prompt template
            prompt = self._load_prompt_template("Execute")
            
            # Format the reasoning structure for the prompt
            structure_text = json.dumps(state["reasoning_structure"], indent=2)
            
            # Format the prompt
            formatted_prompt = prompt.invoke({
                "task": state["input"],
                "reasoning_structure": structure_text,
                "memory_context": memory_context,
                "tools_context": tools_context
            })
            
            # Get the execution response
            execution_response = self.execution_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the content from the response
            execution_result_raw = execution_response.content
            
            # Process the response to handle any tool calls
            execution_result = execution_result_raw
            
            # Check if the response contains tool calls and the tool_provider is available
            if self.tool_provider and "TOOL:" in execution_result_raw:
                # Extract and execute tool calls
                execution_result = self._process_tool_calls(execution_result_raw)
            
            # Update chat history
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content=f"Solve the task following the reasoning structure")
            ai_message = AIMessage(content=execution_result)
            new_history = chat_history + [human_message, ai_message]
            
            # Save the execution to memory if enabled
            if self.memory:
                self.sync_save_memory(
                    memory_type="episodic",
                    item={
                        "event_type": "execution",
                        "task": state["input"],
                        "reasoning_structure": state["reasoning_structure"],
                        "result": execution_result
                    },
                    query=state["input"]
                )
            
            self.logger.debug("Executed reasoning structure")
            
            return {
                "execution_result": execution_result,
                "chat_history": new_history
            }
            
        except Exception as e:
            self.logger.error("Error executing reasoning structure: %s", e)
            # Fallback with a simple attempt to solve
            fallback_result = f"I attempted to solve the task '{state['input']}' but encountered an error: {str(e)}"
            return {
                "execution_result": fallback_result,
                "chat_history": state.get("chat_history", [])
            }
    
    def _process_tool_calls(self, text: str) -> str:
        """Process any tool calls in the execution response.
        
        Args:
            text: The raw text from the LLM with possible tool calls.
            
        Returns:
            Updated text with tool call results integrated.
        """
        if not self.tool_provider or "TOOL:" not in text:
            return text
        
        result_parts = []
        lines = text.split("\n")
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith("TOOL:") or line.startswith("Tool:") or line.startswith("tool:"):
                # Extract tool name
                parts = line.split(":", 1)
                if len(parts) > 1:
                    tool_name = parts[1].strip()
                    tool_args = {}
                    i += 1
                    
                    # Extract parameters
                    while i < len(lines) and ":" in lines[i] and not (
                        lines[i].startswith("TOOL:") or 
                        lines[i].startswith("Tool:") or 
                        lines[i].startswith("tool:")
                    ):
                        param_parts = lines[i].split(":", 1)
                        if len(param_parts) > 1:
                            param_name = param_parts[0].strip()
                            param_value = param_parts[1].strip()
                            tool_args[param_name] = param_value
                        i += 1
                    
                    # Execute the tool
                    try:
                        self.logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                        tool_result = self.tool_provider.execute_tool(tool_name, tool_args)
                        
                        # Add the tool call and result to the output
                        result_parts.append(f"TOOL CALL: {tool_name}")
                        for param, value in tool_args.items():
                            result_parts.append(f"{param}: {value}")
                        
                        result_parts.append("\nTOOL RESULT:")
                        result_parts.append(str(tool_result))
                        result_parts.append("")
                    except Exception as e:
                        self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
                        result_parts.append(f"TOOL CALL ERROR: {tool_name} - {str(e)}")
                    
                    continue  # Skip the increment at the end to account for the modified i
            
            # For non-tool lines, just add them to the result
            result_parts.append(lines[i])
            i += 1
        
        return "\n".join(result_parts)

    def _format_final_answer(self, state: SelfDiscoveryState) -> Dict[str, Union[str, Sequence[BaseMessage]]]:
        """Format the final answer based on the execution result.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with final answer.
        """
        self.logger.debug("Formatting final answer")
        
        execution_result = state.get("execution_result", "")
        
        # Extract the final answer from the execution result
        # This could be more sophisticated, looking for specific patterns
        # or using another LLM call to extract the answer
        
        # Simple approach: Use the execution result as the final answer
        final_answer = execution_result
        
        # Save the final answer to memory if enabled
        if self.memory:
            # Save to episodic memory
            self.sync_save_memory(
                memory_type="episodic",
                item={
                    "event_type": "final_answer",
                    "task": state["input"],
                    "reasoning_structure": state.get("reasoning_structure", {}),
                    "answer": final_answer
                },
                query=state["input"]
            )
            
            # Save to semantic memory
            self.sync_save_memory(
                memory_type="semantic",
                item={
                    "task_type": " ".join(state["input"].split()[:5]),  # Use first few words as task type
                    "solution": final_answer
                },
                query=state["input"]
            )
        
        self.logger.debug("Formatted final answer")
        
        return {"final_answer": final_answer}

    def run(self, input_text: str) -> Dict[str, Any]:
        """Run the Self-Discovery agent on the given input.
        
        Args:
            input_text: The task or problem to solve
            
        Returns:
            Dict containing the result of the execution.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        try:
            self.on_start()
            self.logger.info("Running Self-Discovery agent with input: %s", input_text)
            
            # Initialize state
            initial_state = {
                "input": input_text,
                "chat_history": [],
                "reasoning_modules": self.reasoning_modules,
                "selected_modules": None,
                "adapted_modules": None,
                "reasoning_structure": None,
                "execution_result": None,
                "final_answer": None
            }
            
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Extract the final result
            result = final_state.get("final_answer", "No final answer generated.")
            
            # Create a detailed result with the reasoning structure for transparency
            detailed_result = {
                "output": result,
                "reasoning_structure": final_state.get("reasoning_structure", {})
            }
            
            self.logger.info("Self-Discovery agent completed successfully")
            return detailed_result
            
        except Exception as e:
            self.logger.error("Self-Discovery agent execution failed: %s", e, exc_info=True)
            return {"error": str(e)}
        finally:
            self.on_finish()

    def stream(self, input_text: str) -> Any:
        """Stream the Self-Discovery agent execution.
        
        Args:
            input_text: The task or problem to solve
            
        Yields:
            State updates at each step of execution.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        try:
            self.on_start()
            self.logger.info("Streaming Self-Discovery agent with input: %s", input_text)
            
            # Initialize state
            initial_state = {
                "input": input_text,
                "chat_history": [],
                "reasoning_modules": self.reasoning_modules,
                "selected_modules": None,
                "adapted_modules": None,
                "reasoning_structure": None,
                "execution_result": None,
                "final_answer": None
            }
            
            # Stream the graph execution
            for state in self.graph.stream(initial_state):
                yield state
                
        except Exception as e:
            self.logger.error("Self-Discovery agent streaming failed: %s", e, exc_info=True)
            yield {"error": str(e)}
        finally:
            self.on_finish() 