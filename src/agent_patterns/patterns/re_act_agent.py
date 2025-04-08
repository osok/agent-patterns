"""ReAct (Reason + Act) pattern implementation."""

import operator
import json # Import json at the top level
from typing import Any, Dict, List, Optional, Tuple, Union, TypedDict, Annotated, Sequence
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, FunctionMessage # Import necessary message types
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages # Use add_messages for chat history
import logging
import re
from pathlib import Path

from agent_patterns.core.base_agent import BaseAgent
# Removed load_prompt as BaseAgent now handles prompt loading via _load_prompt_template

# Define the state according to LangChain/LangGraph best practices
class ReActState(TypedDict):
    """Represents the state of the ReAct agent.

    Attributes:
        input: The initial user input.
        chat_history: The history of messages (Human, AI, Tool).
        agent_outcome: The outcome of the last agent step (AgentAction or AgentFinish).
        intermediate_steps: Accumulated list of (AgentAction, str observation) tuples.
        # Removed tools, max_steps, step_count - these are agent instance properties, not state
    """
    input: str
    # Use Annotated list with add_messages reducer for history
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    agent_outcome: Optional[Union[AgentAction, AgentFinish]]
    # Use Annotated list with operator.add reducer for intermediate steps
    intermediate_steps: Annotated[List[Tuple[AgentAction, str]], operator.add]

# --- Agent Implementation ---

class ReActAgent(BaseAgent):
    """ReAct pattern implementation using LangGraph.
    
    Follows the cycle: LLM decides action -> Execute action -> LLM decides next action...
    
    Uses a state dictionary adhering to LangGraph conventions.
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict], # Inherited from BaseAgent
        tools: List[BaseTool],
        prompt_dir: str = "prompts", # Default prompt directory
        max_steps: int = 10, # Keep max_steps as instance property
        log_level: int = logging.INFO
    ):
        """Initialize the ReAct agent.
        
        Args:
            llm_configs: Configuration for LLM roles (e.g., {'default': {...}}).
            tools: List of tools available to the agent.
            prompt_dir: Directory containing prompt templates (relative to project root).
            max_steps: Maximum number of agent steps before stopping.
            log_level: Logging level.
        """
        self.tools = tools
        self.max_steps = max_steps
        self.tool_map = {tool.name: tool for tool in tools} # Map tool names for easy lookup
        self.llm = None # Will be initialized via _get_llm
        
        # Call BaseAgent init *after* setting agent-specific properties
        super().__init__(llm_configs=llm_configs, prompt_dir=prompt_dir, log_level=log_level)
        
        # Initialize the LLM using the base class method
        try:
            self.llm = self._get_llm('default') # Assume a 'default' role for the main LLM
        except ValueError as e:
            self.logger.error("Failed to initialize LLM: %s", e)
            raise # Re-raise if LLM init fails

        self.logger.info("Initialized ReAct agent with %d tools and max_steps=%d", len(self.tools), self.max_steps)

    def build_graph(self) -> None:
        """Build the LangGraph state graph for the ReAct agent.
        
        Nodes:
        - agent: Decides the next action or finishes.
        - execute_tools: Executes the chosen tool.
        
        Edges:
        - Conditional edge from agent based on AgentAction vs AgentFinish.
        """
        agent_graph = StateGraph(ReActState) # Use the ReActState TypedDict

        # Define nodes
        agent_graph.add_node("agent", self._run_agent_llm)
        agent_graph.add_node("execute_tools", self._execute_tools)

        # Define edges
        agent_graph.set_entry_point("agent")
        agent_graph.add_conditional_edges(
            "agent",
            self._should_execute_tools,
            {
                True: "execute_tools", # If AgentAction, execute tools
                False: END # If AgentFinish, end the graph
            }
        )
        agent_graph.add_edge("execute_tools", "agent") # Loop back to agent after tool execution

        # Compile the graph
        try:
            self.graph = agent_graph.compile()
            self.logger.info("ReAct agent graph compiled successfully.")
        except Exception as e:
            self.logger.error("Failed to compile agent graph: %s", e)
            raise RuntimeError("Graph compilation failed") from e

    def _get_agent_prompt(self) -> Any:
         """Load and return the main agent prompt template."""
         # Uses the method from BaseAgent, expecting prompts in <prompt_dir>/ReActAgent/ThoughtStep/
         try:
             return self._load_prompt_template("ThoughtStep")
         except (FileNotFoundError, ValueError) as e:
             self.logger.error("Failed to load ReAct agent prompt: %s", e)
             # Provide a fallback or raise a more specific error if needed
             raise ValueError("Could not load required prompt template for ReAct agent.") from e

    def _run_agent_llm(self, state: ReActState) -> Dict[str, Union[AgentAction, AgentFinish, List[Tuple[AgentAction, str]]]]:
        """Runs the agent LLM to decide the next step (action or finish).
        
        Args:
            state: The current graph state.

        Returns:
            A dictionary containing the agent_outcome (AgentAction or AgentFinish)
            and potentially updated intermediate_steps.
        """
        self.logger.debug("Running agent LLM step.")
        prompt = self._get_agent_prompt()
        
        # Format the prompt with current state
        # Ensure tools are formatted correctly for the prompt
        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
        
        # Prepare messages for the LLM call - include history if available
        messages = state.get("chat_history", [])
        if not messages:
             # If no history, start with the initial input
             messages = [HumanMessage(content=state["input"])]

        try:
            # Use LCEL to bind tools and invoke
            # Note: Depending on the specific LLM and how it expects tools, 
            # you might use .bind_tools() or include descriptions in the prompt.
            # For simplicity here, we assume prompt includes tool descriptions.
            # llm_with_tools = self.llm.bind_tools(self.tools) # If using native tool calling LLM
            
            formatted_prompt = prompt.invoke({
                "input": state["input"], 
                "intermediate_steps": state.get("intermediate_steps", []) # Pass intermediate steps
                # "chat_history": messages # Pass history if prompt expects it
                # "tools": tool_descriptions # Pass tool descriptions if prompt expects it
            })
            
            response: BaseMessage = self.llm.invoke(formatted_prompt.to_messages())
            
            # Parse the AIMessage response into AgentAction or AgentFinish
            # This logic depends heavily on the prompt format and LLM output structure.
            # For a ReAct prompt, we expect Thought/Action or Final Answer. 
            agent_outcome = self._parse_llm_react_response(response) 
            
            self.logger.debug("LLM outcome: %s", agent_outcome)
            return {"agent_outcome": agent_outcome}

        except Exception as e:
            self.logger.error("Error in agent LLM step: %s", e)
            # Handle LLM error, perhaps by returning a finish state with error
            return {"agent_outcome": AgentFinish({"output": f"Agent LLM failed: {e}"}, log=f"Agent LLM failed: {e}")}


    def _execute_tools(self, state: ReActState) -> Dict[str, List[Tuple[AgentAction, str]]]:
        """Executes the tool specified in the agent_outcome.
        
        Args:
            state: The current graph state.

        Returns:
            A dictionary containing the new intermediate_steps.
        """
        agent_action = state.get('agent_outcome')
        if not isinstance(agent_action, AgentAction):
            self.logger.error("execute_tools called without AgentAction in state.")
            # This case should ideally not be reached due to graph logic
            return {"intermediate_steps": []} 

        self.logger.info("Executing tool: %s with args %s", agent_action.tool, agent_action.tool_input)
        tool = self.tool_map.get(agent_action.tool)
        if tool is None:
            self.logger.warning("Tool '%s' not found.", agent_action.tool)
            observation = f"Error: Tool '{agent_action.tool}' not found."
        else:
            try:
                # Use the _execute_tool helper for consistent execution/error handling
                observation = self._execute_tool(tool, agent_action.tool_input)
            except Exception as e:
                # Should not happen if _execute_tool catches exceptions, but as a safeguard
                self.logger.error("Unexpected error during tool execution: %s", e)
                observation = f"Error: Failed to execute tool '{agent_action.tool}'. {e}"
        
        self.logger.debug("Tool observation: %s", observation)
        # Return the observation to be added to intermediate_steps
        # The operator.add reducer on intermediate_steps will append this tuple
        return {"intermediate_steps": [(agent_action, observation)]} 

    def _should_execute_tools(self, state: ReActState) -> bool:
        """Determines if the agent decided to use a tool."""
        agent_outcome = state.get('agent_outcome')
        should_exec = isinstance(agent_outcome, AgentAction)
        self.logger.debug("Checking if tools should execute: %s", should_exec)
        return should_exec

    def _parse_llm_react_response(self, response: BaseMessage) -> Union[AgentAction, AgentFinish]:
        """Parses LLM response (expected ReAct format) into AgentAction or AgentFinish.
        
        Example ReAct format:
        Thought: I need to use a tool.
        Action: tool_name(tool_input)
        
        Or for final answer:
        Thought: I have the final answer.
        Final Answer: The answer is 42.
        """
        if not isinstance(response, AIMessage):
             self.logger.warning("Unexpected response type from LLM: %s", type(response))
             return AgentFinish({"output": f"LLM returned unexpected type: {type(response)}"}, log=f"LLM returned unexpected type: {type(response)}")
             
        text = response.content
        self.logger.debug("Parsing LLM response: %s", text[:100] + "..." if len(text) > 100 else text)

        final_answer_match = re.search(r"Final Answer:(.*)", text, re.DOTALL | re.IGNORECASE)
        if final_answer_match:
            final_answer = final_answer_match.group(1).strip()
            self.logger.info("LLM provided Final Answer: %s", final_answer)
            return AgentFinish({"output": final_answer}, log=text)

        action_match = re.search(r"Action:(.*?)(?:\n|$)", text, re.DOTALL | re.IGNORECASE)
        if action_match:
            action_text = action_match.group(1).strip()
            tool_match = re.match(r"(\w+)\s*\((.*)\)", action_text)
            if tool_match:
                tool_name = tool_match.group(1)
                tool_input_content = tool_match.group(2).strip()
                tool_input: Any = tool_input_content # Default

                # Determine potential type
                is_dict_like = tool_input_content.startswith("{") and tool_input_content.endswith("}")
                is_list_like = tool_input_content.startswith("[") and tool_input_content.endswith("]")
                is_simple_kv = '=' in tool_input_content and not (is_dict_like or is_list_like)
                is_quoted_string = (tool_input_content.startswith("'") and tool_input_content.endswith("'")) or \
                                 (tool_input_content.startswith('"') and tool_input_content.endswith('"'))

                # Outer try block for overall parsing logic
                try: 
                    if is_dict_like:
                        try: 
                            tool_input = json.loads(tool_input_content)
                        except json.JSONDecodeError as e:
                            self.logger.warning("JSON dict parsing failed for '%s': %s. Using raw string.", tool_input_content, e)
                            # Fallback handled by initial default
                    elif is_list_like:
                        try: 
                            tool_input = json.loads(tool_input_content)
                        except json.JSONDecodeError as e:
                            self.logger.warning("JSON list parsing failed for '%s': %s. Using raw string.", tool_input_content, e)
                            # Fallback handled by initial default
                    elif is_simple_kv:
                        parsed_args = {}
                        kv_pairs = re.findall(r'(\w+)\s*=\s*(?:"(.*?)"|\'(.*?)\'|([^,\s]+))', tool_input_content)
                        for key, quoted_val1, quoted_val2, plain_val in kv_pairs:
                            value = quoted_val1 if quoted_val1 else quoted_val2 if quoted_val2 else plain_val
                            parsed_args[key] = value
                        if parsed_args:
                            tool_input = parsed_args
                            self.logger.debug("Parsed key-value tool input: %s", parsed_args)
                        # else: keep raw string if parsing fails
                    elif is_quoted_string:
                        tool_input = tool_input_content[1:-1]
                    # else: Keep default raw string if no format matches
                        
                except Exception as e:
                    self.logger.warning("Unexpected error during tool input parsing for '%s': %s. Using raw string.", tool_input_content, e)
                    tool_input = tool_input_content # Ensure fallback on any parsing error

                self.logger.info("LLM requested Action: %s(%s)", tool_name, repr(tool_input))
                return AgentAction(tool=tool_name, tool_input=tool_input, log=text)

            else:
                self.logger.warning("Could not parse action text format: %s", action_text)
                return AgentFinish({"output": f"Could not parse action: {action_text}"}, log=text)

        self.logger.warning("LLM response did not contain Final Answer or parsable Action.")
        return AgentFinish({"output": text}, log=text)


    def _execute_tool(self, tool: BaseTool, tool_input: Any) -> str:
        """Executes a tool and returns the string output or error message."""
        try:
            # Tools expect string input generally, but handle dicts if possible
            input_str = str(tool_input) if not isinstance(tool_input, str) else tool_input
            result = tool.run(input_str) # Pass input_str or tool_input based on tool needs
            return str(result)
        except Exception as e:
            error_msg = f"Error executing tool {tool.name}: {str(e)}"
            self.logger.error("Tool execution failed for %s: %s", tool.name, str(e))
            return error_msg

    # Override the run method from BaseAgent to handle initial state setup for ReAct
    def run(self, input_text: str) -> Dict[str, Any]:
        """Run the ReAct agent on the given input.
        
        Args:
            input_text: The input text/query to process
            
        Returns:
            Dict containing the final agent outcome.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        # Initialize state according to ReActState definition
        initial_state: ReActState = {
            "input": input_text,
            "chat_history": [], # Start with empty history
            "agent_outcome": None, 
            "intermediate_steps": [] 
        }
        
        final_state = {} 
        # Use streaming to get the final state, handling potential errors
        try:
            self.on_start()
            self.logger.info("Running ReAct agent graph with input: %s", input_text)
            # LangGraph expects inputs as a dictionary matching the state keys
            inputs_for_graph = {"input": input_text, "chat_history": [], "intermediate_steps": []}
            for step_output in self.graph.stream(inputs_for_graph):
                # The final state is the last value yielded before END
                # We just need the last snapshot
                final_state = step_output 
            
            # Extract the relevant final output from the last state
            # The structure depends on how the graph is built and what END returns
            # Assuming the last node before END updates the state correctly.
            # Let's get the last value for the 'agent' node if available
            last_agent_state = final_state.get("agent", {})
            agent_outcome = last_agent_state.get("agent_outcome")

            if isinstance(agent_outcome, AgentFinish):
                self.logger.info("Agent finished successfully.")
                return {"output": agent_outcome.return_values["output"]}
            else:
                # Handle cases where the graph ends unexpectedly (e.g., max iterations)
                self.logger.warning("Agent graph finished without explicit AgentFinish.")
                # Try to get the last observation or input as fallback
                if final_state.get("intermediate_steps"):
                    last_action, last_obs = final_state["intermediate_steps"][-1]
                    return {"output": f"Agent stopped. Last observation: {last_obs}"}
                else:
                    return {"output": f"Agent stopped. No clear output found."}

        except Exception as e:
            self.logger.error("Agent execution failed during run: %s", e, exc_info=True)
            # Return an error dictionary or re-raise
            return {"error": str(e)}
        finally:
            self.on_finish()

    # Remove methods that are no longer needed or refactored:
    # _process_observation - Logic moved into LLM seeing history
    # _format_final_answer - Final answer generated by _run_agent_llm returning AgentFinish
    # _generate_default_answer - Error handling produces ToolMessage or AgentFinish with error
    # _should_continue - Replaced by _should_execute_tools
    # _parse_action - Incorporated into _parse_llm_react_response
    # _is_done - Logic now handled by _should_execute_tools checking for AgentFinish
    # merge_states - Not needed when using Annotated state correctly