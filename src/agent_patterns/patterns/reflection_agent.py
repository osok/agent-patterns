"""Reflection agent pattern implementation."""

import operator
from typing import Any, Dict, List, Optional, Union, TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import logging
from pathlib import Path
import re

from agent_patterns.core.base_agent import BaseAgent

# Define the state according to LangGraph best practices
class ReflectionState(TypedDict):
    """Represents the state of the Reflection agent.

    Attributes:
        input: The initial user input/query.
        chat_history: The history of messages.
        initial_output: The first generated response.
        reflection: The critique of the initial output.
        refined_output: The improved response after reflection.
        needs_refinement: Flag indicating if refinement is needed.
        final_answer: The final output to return to the user.
    """
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    initial_output: Optional[str]
    reflection: Optional[str]
    refined_output: Optional[str]
    needs_refinement: bool
    final_answer: Optional[str]


class ReflectionAgent(BaseAgent):
    """Reflection pattern implementation using LangGraph.
    
    This agent follows a three-phase approach:
    1. Generate an initial response to the user's query
    2. Reflect on and critique the initial response
    3. Refine the response based on the critique if needed
    
    The primary benefit of this approach is improved quality through
    self-critique and refinement.
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict],
        prompt_dir: str = "src/agent_patterns/prompts",
        tool_provider: Optional[Any] = None,
        memory: Optional[Any] = None,
        memory_config: Optional[Dict[str, bool]] = None,
        log_level: int = logging.INFO
    ):
        """Initialize the Reflection agent.
        
        Args:
            llm_configs: Configuration for LLM roles (e.g., {'generator': {...}, 'critic': {...}}).
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
        
        # Initialize the LLMs for generation and criticism
        try:
            self.generator_llm = self._get_llm('generator')
            self.critic_llm = self._get_llm('critic')
        except ValueError as e:
            self.logger.error("Failed to initialize LLMs: %s", e)
            raise ValueError("LLM initialization failed. Make sure 'generator' and 'critic' roles are defined in llm_configs.") from e

        self.logger.info("Initialized Reflection agent")

    def build_graph(self) -> None:
        """Build the LangGraph state graph for the Reflection agent.
        
        Nodes:
        - generate_initial: Creates an initial response.
        - reflect: Critiques the initial response.
        - check_refine: Determines if refinement is needed.
        - refine: Improves the response based on reflection.
        - final_output: Prepares the final answer.
        
        Edges:
        - Conditional edges based on whether refinement is needed.
        """
        # Create the graph with our state type
        reflection_graph = StateGraph(ReflectionState)

        # Define nodes
        reflection_graph.add_node("generate_initial", self._generate_initial_output)
        reflection_graph.add_node("reflect", self._reflect_on_output)
        reflection_graph.add_node("check_refine", self._check_refinement_needed)
        reflection_graph.add_node("refine", self._refine_output)
        reflection_graph.add_node("final_output", self._prepare_final_output)

        # Define edges
        reflection_graph.set_entry_point("generate_initial")
        reflection_graph.add_edge("generate_initial", "reflect")
        reflection_graph.add_edge("reflect", "check_refine")
        
        # Conditional edges from check_refine
        reflection_graph.add_conditional_edges(
            "check_refine",
            self._should_refine,
            {
                True: "refine",  # If refinement needed, go to refine
                False: "final_output"  # If no refinement needed, go to final output
            }
        )
        
        # Final edges
        reflection_graph.add_edge("refine", "final_output")
        reflection_graph.add_edge("final_output", END)
        
        # Compile the graph
        try:
            self.graph = reflection_graph.compile()
            self.logger.info("Reflection agent graph compiled successfully.")
        except Exception as e:
            self.logger.error("Failed to compile Reflection agent graph: %s", e)
            raise RuntimeError("Graph compilation failed") from e

    def _generate_initial_output(self, state: ReflectionState) -> Dict[str, Union[str, Sequence[BaseMessage]]]:
        """Generate an initial response to the user's query.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with an initial output.
        """
        self.logger.debug("Generating initial output for: %s", state["input"])
        
        try:
            # Retrieve relevant memories if memory is enabled
            memories = self.sync_retrieve_memories(state["input"])
            memory_context = ""
            
            # Format memories for inclusion in the prompt
            if memories:
                memory_sections = []
                for memory_type, items in memories.items():
                    if items:
                        items_text = "\n- ".join([str(item) for item in items])
                        memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                
                if memory_sections:
                    memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                    self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for initial output")
            
            # Get available tools if tool_provider is present
            tools_description = ""
            if self.tool_provider:
                tools = self.tool_provider.list_tools()
                if tools:
                    tool_descriptions = []
                    for tool in tools:
                        tool_descriptions.append(f"- {tool['name']}: {tool['description']}")
                    tools_description = "Available tools:\n" + "\n".join(tool_descriptions) + "\n\n"
                    tools_description += "To use a tool, include the following format in your response:\n"
                    tools_description += "USE_TOOL: tool_name(param1=value1, param2=value2)\n\n"
                    self.logger.info(f"Found {len(tools)} available tools for initial output")
            
            # Load the generation prompt template
            prompt = self._load_prompt_template("Generate")
            
            # Format the prompt with the user's input, memory context, and tools
            formatted_prompt = prompt.invoke({
                "input": state["input"],
                "memory_context": memory_context,
                "tools_description": tools_description
            })
            
            # Get the generation response
            generation_response = self.generator_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the content from the response
            initial_output = generation_response.content
            
            # Check if the response contains a tool call
            # Simple pattern matching for tool calls in the format: "USE_TOOL: tool_name(param1=value1, param2=value2)"
            tool_call_pattern = r"USE_TOOL:\s+(\w+)\(([^)]*)\)"
            tool_call_match = re.search(tool_call_pattern, initial_output)
            
            # If a tool call is detected and tool_provider is available
            if tool_call_match and self.tool_provider:
                tool_name = tool_call_match.group(1)
                tool_params_str = tool_call_match.group(2)
                
                # Parse parameters
                params = {}
                param_matches = re.finditer(r"(\w+)\s*=\s*([^,]+)(?:,|$)", tool_params_str)
                for match in param_matches:
                    param_name = match.group(1)
                    param_value = match.group(2).strip().strip('"\'')
                    params[param_name] = param_value
                
                try:
                    # Execute the tool
                    self.logger.info(f"Executing tool: {tool_name} with params {params}")
                    tool_result = self.tool_provider.execute_tool(tool_name, params)
                    
                    # Append tool result to the initial output
                    initial_output += f"\n\nTool Result: {tool_result}"
                except Exception as e:
                    error_msg = f"\n\nError executing tool {tool_name}: {str(e)}"
                    initial_output += error_msg
                    self.logger.error(f"Tool execution error: {str(e)}")
            
            # Update chat history with the generation interaction
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content=state["input"])
            ai_message = AIMessage(content=initial_output)
            new_history = chat_history + [human_message, ai_message]
            
            self.logger.debug("Generated initial output: %s", initial_output[:100] + "..." if len(initial_output) > 100 else initial_output)
            
            return {
                "initial_output": initial_output,
                "chat_history": new_history
            }
            
        except Exception as e:
            self.logger.error("Error generating initial output: %s", e)
            # Return a simple fallback response
            return {
                "initial_output": f"I apologize, but I encountered an error while generating a response to your query: {str(e)}",
                "chat_history": state.get("chat_history", [])
            }

    def _reflect_on_output(self, state: ReflectionState) -> Dict[str, Union[str, Sequence[BaseMessage]]]:
        """Reflect on and critique the initial output.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with reflection.
        """
        self.logger.debug("Reflecting on initial output")
        
        try:
            # Load the reflection prompt template
            prompt = self._load_prompt_template("Reflect")
            
            # Format the prompt with the initial output and input
            formatted_prompt = prompt.invoke({
                "input": state["input"],
                "initial_output": state["initial_output"]
            })
            
            # Get the reflection response
            reflection_response = self.critic_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the content from the response
            reflection = reflection_response.content
            
            # Update chat history with the reflection interaction
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content=f"Please critique the response to: {state['input']}")
            ai_message = AIMessage(content=reflection)
            new_history = chat_history + [human_message, ai_message]
            
            # Save the reflection to episodic memory
            if self.memory:
                self.sync_save_memory(
                    memory_type="episodic",
                    item={
                        "event_type": "reflection",
                        "query": state["input"],
                        "initial_output": state["initial_output"],
                        "reflection": reflection
                    },
                    query=state["input"]
                )
                self.logger.debug("Saved reflection to episodic memory")
            
            self.logger.debug("Generated reflection: %s", reflection[:100] + "..." if len(reflection) > 100 else reflection)
            
            return {
                "reflection": reflection,
                "chat_history": new_history
            }
            
        except Exception as e:
            self.logger.error("Error generating reflection: %s", e)
            # Return a simple fallback reflection
            return {
                "reflection": "Upon review, the initial response appears to address the query, but could benefit from additional detail and clarification.",
                "chat_history": state.get("chat_history", [])
            }

    def _check_refinement_needed(self, state: ReflectionState) -> Dict[str, bool]:
        """Determine if refinement is needed based on the reflection.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with needs_refinement flag.
        """
        # Simple heuristic: check if reflection contains indicators that refinement is needed
        # This could be made more sophisticated with actual NLP analysis
        reflection_text = state.get("reflection", "").lower()
        
        # Words that suggest refinement is needed
        refinement_indicators = [
            "improve", "missing", "lacks", "could be better", "should include",
            "incomplete", "error", "incorrect", "inaccurate", "unclear",
            "confusing", "should add", "needs more", "omitted", "overlooked"
        ]
        
        needs_refinement = any(indicator in reflection_text for indicator in refinement_indicators)
        
        self.logger.debug("Refinement needed: %s", needs_refinement)
        
        return {"needs_refinement": needs_refinement}

    def _should_refine(self, state: ReflectionState) -> bool:
        """Determine if the agent should proceed to the refinement step.
        
        Args:
            state: The current graph state.
            
        Returns:
            True if refinement is needed, False otherwise.
        """
        return state["needs_refinement"]

    def _refine_output(self, state: ReflectionState) -> Dict[str, Union[str, Sequence[BaseMessage]]]:
        """Refine the initial output based on the reflection.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with refined output.
        """
        self.logger.debug("Refining output based on reflection")
        
        try:
            # Load the refinement prompt template
            prompt = self._load_prompt_template("Refine")
            
            # Format the prompt with the initial output, reflection, and input
            formatted_prompt = prompt.invoke({
                "input": state["input"],
                "initial_output": state["initial_output"],
                "reflection": state["reflection"]
            })
            
            # Get the refinement response
            refinement_response = self.generator_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the content from the response
            refined_output = refinement_response.content
            
            # Update chat history with the refinement interaction
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content=f"Please improve your response based on this feedback: {state['reflection']}")
            ai_message = AIMessage(content=refined_output)
            new_history = chat_history + [human_message, ai_message]
            
            # Save the refinement to episodic memory
            if self.memory:
                self.sync_save_memory(
                    memory_type="episodic",
                    item={
                        "event_type": "refinement",
                        "query": state["input"],
                        "initial_output": state["initial_output"],
                        "reflection": state["reflection"],
                        "refined_output": refined_output
                    },
                    query=state["input"]
                )
                
                # Also save to semantic memory for future reference
                self.sync_save_memory(
                    memory_type="semantic",
                    item={
                        "query_type": state["input"].split()[0:5],  # Use first few words as query type
                        "query": state["input"],
                        "answer": refined_output,
                        "reflection_improved": True
                    },
                    query=state["input"]
                )
                
                self.logger.debug("Saved refinement to memory")
            
            self.logger.debug("Generated refined output: %s", refined_output[:100] + "..." if len(refined_output) > 100 else refined_output)
            
            return {
                "refined_output": refined_output,
                "chat_history": new_history,
                "final_answer": refined_output  # Set final answer to the refined output
            }
            
        except Exception as e:
            self.logger.error("Error refining output: %s", e)
            # Return the initial output as a fallback
            return {
                "refined_output": state["initial_output"],
                "final_answer": state["initial_output"],
                "chat_history": state.get("chat_history", [])
            }

    def _prepare_final_output(self, state: ReflectionState) -> Dict[str, Union[str, Sequence[BaseMessage]]]:
        """Prepare the final output to return to the user.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with final answer.
        """
        # If refinement was not needed, use the initial output as the final answer
        if not state["needs_refinement"]:
            self.logger.debug("Using initial output as final answer (no refinement needed)")
            
            # Save the initial output to semantic memory if no refinement was needed
            if self.memory:
                self.sync_save_memory(
                    memory_type="semantic",
                    item={
                        "query_type": state["input"].split()[0:5],  # Use first few words as query type
                        "query": state["input"],
                        "answer": state["initial_output"],
                        "reflection_improved": False
                    },
                    query=state["input"]
                )
                self.logger.debug("Saved initial output to semantic memory")
            
            return {"final_answer": state["initial_output"]}
        
        # If we get here, refinement was done and final_answer should already be set
        # This is just a safeguard in case final_answer wasn't set
        if state.get("final_answer") is None:
            self.logger.debug("Using refined output as final answer")
            return {"final_answer": state["refined_output"]}
        
        # Otherwise, keep the existing final_answer
        return {}

    def run(self, input_text: str) -> Dict[str, Any]:
        """Run the Reflection agent on the given input.
        
        Args:
            input_text: The input query to process
            
        Returns:
            Dict containing the final result.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        # Initialize state
        initial_state: ReflectionState = {
            "input": input_text,
            "chat_history": [],
            "initial_output": None,
            "reflection": None,
            "refined_output": None,
            "needs_refinement": False,
            "final_answer": None
        }
        
        try:
            self.on_start()
            self.logger.info("Running Reflection agent with input: %s", input_text)
            
            # Prepare input for graph
            inputs_for_graph = {
                "input": input_text,
                "chat_history": []
            }
            
            # Run the graph
            final_state = self.graph.invoke(inputs_for_graph)
            
            # Extract the final result
            result = final_state.get("final_answer", "No final answer generated.")
            
            self.logger.info("Reflection agent completed successfully")
            return {"output": result}
            
        except Exception as e:
            self.logger.error("Reflection agent execution failed: %s", e, exc_info=True)
            return {"error": str(e)}
        finally:
            self.on_finish()

    def stream(self, input_text: str) -> Any:
        """Stream the Reflection agent execution.
        
        Args:
            input_text: The input query to process
            
        Yields:
            State updates at each step of execution.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        # Initialize state
        initial_state: ReflectionState = {
            "input": input_text,
            "chat_history": [],
            "initial_output": None,
            "reflection": None,
            "refined_output": None,
            "needs_refinement": False,
            "final_answer": None
        }
        
        try:
            self.on_start()
            self.logger.info("Streaming Reflection agent with input: %s", input_text)
            
            # Prepare input for graph
            inputs_for_graph = {
                "input": input_text,
                "chat_history": []
            }
            
            # Stream the graph execution
            for step_output in self.graph.stream(inputs_for_graph):
                yield step_output
                
        except Exception as e:
            self.logger.error("Reflection agent streaming failed: %s", e, exc_info=True)
            yield {"error": str(e)}
        finally:
            self.on_finish()