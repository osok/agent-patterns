"""Plan and Solve agent pattern implementation."""

import operator
import re
from typing import Any, Dict, List, Optional, Union, TypedDict, Annotated, Sequence, cast
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import logging
from pathlib import Path

from agent_patterns.core.base_agent import BaseAgent

# Define the state according to LangGraph best practices
class PlanAndSolveState(TypedDict):
    """Represents the state of the Plan and Solve agent.

    Attributes:
        input: The initial user input/task.
        chat_history: The history of messages.
        plan: List of steps generated from the planning phase.
        current_step_index: Index of the current step being executed.
        step_results: Results from each executed step.
        plan_done: Flag indicating if the plan execution is complete.
        final_result: The final aggregated result.
    """
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    plan: List[str]
    current_step_index: int
    step_results: List[str]
    plan_done: bool
    final_result: Optional[str]


class PlanAndSolveAgent(BaseAgent):
    """Plan and Solve pattern implementation using LangGraph.
    
    This agent follows a two-phase approach:
    1. Planning Phase: Generate a multi-step plan to solve the task
    2. Execution Phase: Execute each step of the plan sequentially
    
    The advantage of this approach is that it separates the planning from execution,
    allowing for more structured and focused handling of complex tasks.
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
        """Initialize the Plan and Solve agent.
        
        Args:
            llm_configs: Configuration for LLM roles (e.g., {'planner': {...}, 'executor': {...}}).
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
        
        # Initialize the LLMs for planning and execution
        try:
            self.planning_llm = self._get_llm('planner')
            self.execution_llm = self._get_llm('executor')
        except ValueError as e:
            self.logger.error("Failed to initialize LLMs: %s", e)
            raise ValueError("LLM initialization failed. Make sure 'planner' and 'executor' roles are defined in llm_configs.") from e

        self.logger.info("Initialized Plan and Solve agent")

    def build_graph(self) -> None:
        """Build the LangGraph state graph for the Plan and Solve agent.
        
        Nodes:
        - generate_plan: Creates a plan with multiple steps.
        - execute_step: Executes the current step in the plan.
        - check_completion: Checks if all steps have been executed.
        - aggregate_results: Combines step results into a final answer.
        
        Edges:
        - Conditional edges based on plan completion status.
        """
        # Create the graph with our state type
        plan_solve_graph = StateGraph(PlanAndSolveState)

        # Define nodes
        plan_solve_graph.add_node("generate_plan", self._generate_plan)
        plan_solve_graph.add_node("execute_step", self._execute_plan_step)
        plan_solve_graph.add_node("check_completion", self._check_plan_completion)
        plan_solve_graph.add_node("aggregate_results", self._aggregate_results)

        # Define edges
        plan_solve_graph.set_entry_point("generate_plan")
        plan_solve_graph.add_edge("generate_plan", "execute_step")
        plan_solve_graph.add_edge("execute_step", "check_completion")
        
        # Conditional edges from check_completion
        plan_solve_graph.add_conditional_edges(
            "check_completion",
            self._should_continue_execution,
            {
                True: "execute_step",  # If not done, continue executing steps
                False: "aggregate_results"  # If done, move to aggregation
            }
        )
        
        # Final edge
        plan_solve_graph.add_edge("aggregate_results", END)
        
        # Compile the graph
        try:
            self.graph = plan_solve_graph.compile()
            self.logger.info("Plan and Solve agent graph compiled successfully.")
        except Exception as e:
            self.logger.error("Failed to compile Plan and Solve agent graph: %s", e)
            raise RuntimeError("Graph compilation failed") from e

    def _generate_plan(self, state: PlanAndSolveState) -> Dict[str, Union[List[str], Sequence[BaseMessage]]]:
        """Generate a multi-step plan for solving the task.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with a plan.
        """
        self.logger.debug("Generating plan for task: %s", state["input"])
        
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
                    self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for planning")
            
            # Load the planning prompt template
            prompt = self._load_prompt_template("PlanStep")
            
            # Format the prompt with the task and memory context
            formatted_prompt = prompt.invoke({
                "input": state["input"],
                "memory_context": memory_context
            })
            
            # Get the planning response
            planning_response = self.planning_llm.invoke(formatted_prompt.to_messages())
            
            # Parse the plan into a list of steps
            plan_text = planning_response.content
            
            # Extract numbered steps using regex
            steps = []
            # This pattern matches numbered items like "1. Do something" or "Step 1: Do something"
            step_pattern = r'(?:\d+\.|\bStep\s+\d+:?)\s*(.*?)(?=(?:\d+\.|\bStep\s+\d+:?)|$)'
            matches = re.finditer(step_pattern, plan_text, re.DOTALL)
            
            for match in matches:
                step_text = match.group(1).strip()
                if step_text:  # Ensure non-empty step
                    steps.append(step_text)
            
            # If regex didn't work, fall back to splitting by newlines and filtering
            if not steps:
                # Simple fallback - split by newlines and look for lines starting with numbers
                lines = plan_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if re.match(r'^\d+\.', line):
                        # Extract the text after the number and period
                        step_text = re.sub(r'^\d+\.\s*', '', line).strip()
                        if step_text:
                            steps.append(step_text)
            
            # If we still don't have steps, use the whole response
            if not steps:
                self.logger.warning("Could not parse steps from plan, using whole response")
                steps = [plan_text]
            
            # Update chat history with the planning interaction
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content=f"I need to plan how to: {state['input']}")
            ai_message = AIMessage(content=f"Here's a plan to solve this task:\n\n{plan_text}")
            new_history = chat_history + [human_message, ai_message]
            
            # Save the plan to episodic memory if memory is enabled
            if self.memory:
                self.sync_save_memory(
                    memory_type="episodic",
                    item={
                        "event_type": "plan_generation",
                        "task": state["input"],
                        "plan": steps
                    },
                    task=state["input"]
                )
            
            self.logger.info("Generated plan with %d steps", len(steps))
            return {
                "plan": steps,
                "chat_history": new_history,
                "current_step_index": 0,
                "step_results": []
            }
            
        except Exception as e:
            self.logger.error("Error generating plan: %s", e)
            # Return a simple fallback plan
            return {
                "plan": ["Analyze the task", "Gather information", "Provide a solution"],
                "chat_history": state.get("chat_history", []),
                "current_step_index": 0,
                "step_results": []
            }

    def _execute_plan_step(self, state: PlanAndSolveState) -> Dict[str, Union[int, List[str], Sequence[BaseMessage]]]:
        """Execute the current step in the plan.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with the result of the executed step.
        """
        current_index = state["current_step_index"]
        
        if current_index >= len(state["plan"]):
            self.logger.warning("Attempted to execute step beyond plan length")
            return {
                "current_step_index": current_index,
                "step_results": state["step_results"]
            }
        
        current_step = state["plan"][current_index]
        previous_results = state["step_results"]
        
        self.logger.info("Executing step %d: %s", current_index + 1, current_step)
        
        try:
            # Retrieve relevant memories for this step
            step_query = f"{state['input']} - {current_step}"
            memories = self.sync_retrieve_memories(step_query)
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
                    self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for step execution")
            
            # Get available tools if tool_provider is present
            tools_description = ""
            if self.tool_provider:
                tools = self.tool_provider.list_tools()
                if tools:
                    tool_descriptions = []
                    for tool in tools:
                        tool_descriptions.append(f"- {tool['name']}: {tool['description']}")
                    tools_description = "Available tools:\n" + "\n".join(tool_descriptions) + "\n\n"
                    self.logger.info(f"Found {len(tools)} available tools for step execution")
            
            # Load the execution prompt template
            prompt = self._load_prompt_template("ExecuteStep")
            
            # Format previous results as context
            previous_context = "\n".join([
                f"Step {i+1} Result: {result}" 
                for i, result in enumerate(previous_results)
            ])
            
            # Format the prompt with the current step
            formatted_prompt = prompt.invoke({
                "input": state["input"],
                "current_step": current_step,
                "previous_results": previous_context,
                "memory_context": memory_context,
                "tools_description": tools_description
            })
            
            # Get the execution response
            execution_response = self.execution_llm.invoke(formatted_prompt.to_messages())
            step_result = execution_response.content
            
            # Check if the response contains a tool call
            # Simple pattern matching for tool calls in the format: "USE_TOOL: tool_name(param1=value1, param2=value2)"
            tool_call_pattern = r"USE_TOOL:\s+(\w+)\(([^)]*)\)"
            tool_call_match = re.search(tool_call_pattern, step_result)
            
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
                    
                    # Append tool result to the step result
                    step_result += f"\n\nTool Result: {tool_result}"
                except Exception as e:
                    error_msg = f"\n\nError executing tool {tool_name}: {str(e)}"
                    step_result += error_msg
                    self.logger.error(f"Tool execution error: {str(e)}")
            
            # Update chat history with the execution interaction
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content=f"Execute step {current_index + 1}: {current_step}")
            ai_message = AIMessage(content=step_result)
            new_history = chat_history + [human_message, ai_message]
            
            # Save the step execution result to episodic memory
            if self.memory:
                self.sync_save_memory(
                    memory_type="episodic",
                    item={
                        "event_type": "step_execution",
                        "task": state["input"],
                        "step": current_step,
                        "step_index": current_index,
                        "result": step_result
                    },
                    task=state["input"]
                )
            
            # Update step results
            new_results = list(state["step_results"])
            new_results.append(step_result)
            
            self.logger.debug("Step %d executed with result: %s", current_index + 1, step_result[:100] + "..." if len(step_result) > 100 else step_result)
            
            # Return updated state
            return {
                "current_step_index": current_index + 1,
                "step_results": new_results,
                "chat_history": new_history
            }
            
        except Exception as e:
            self.logger.error("Error executing step %d: %s", current_index + 1, e)
            # Return error as step result
            error_result = f"Error executing step: {str(e)}"
            new_results = list(state["step_results"])
            new_results.append(error_result)
            
            return {
                "current_step_index": current_index + 1,
                "step_results": new_results
            }

    def _check_plan_completion(self, state: PlanAndSolveState) -> Dict[str, bool]:
        """Check if all steps in the plan have been executed.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with plan_done flag.
        """
        is_done = state["current_step_index"] >= len(state["plan"])
        self.logger.debug("Plan completion check: %s (%d/%d steps completed)", 
                         "Complete" if is_done else "Incomplete",
                         state["current_step_index"],
                         len(state["plan"]))
        
        return {"plan_done": is_done}

    def _should_continue_execution(self, state: PlanAndSolveState) -> bool:
        """Determine if execution should continue to the next step.
        
        Args:
            state: The current graph state.
            
        Returns:
            True if there are more steps to execute, False otherwise.
        """
        return not state["plan_done"]

    def _aggregate_results(self, state: PlanAndSolveState) -> Dict[str, Union[str, Sequence[BaseMessage]]]:
        """Aggregate the results from all executed steps into a final result.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with the final result.
        """
        self.logger.info("Aggregating results from %d steps", len(state["step_results"]))
        
        # Combine the step results
        steps_with_results = []
        for i, (step, result) in enumerate(zip(state["plan"], state["step_results"])):
            steps_with_results.append(f"Step {i+1}: {step}\nResult: {result}")
        
        execution_summary = "\n\n".join(steps_with_results)
        
        try:
            # Retrieve relevant memories for final synthesis
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
                    self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for final synthesis")
            
            # Use the planning LLM to summarize the results
            system_prompt = "You are a helpful assistant that creates clear, concise summaries."
            human_prompt = f"""
            Based on the executed steps below, provide a comprehensive final answer to the original task.

            Original Task: {state['input']}

            {memory_context}

            Execution Steps:
            {execution_summary}

            Please provide a well-structured final answer that directly addresses the original task.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": human_prompt}
            ]
            
            # Get the final response
            final_response = self.planning_llm.invoke(messages)
            final_result = final_response.content
            
            # Update chat history with the final result
            chat_history = list(state.get("chat_history", []))
            human_message = HumanMessage(content="Please provide the final answer to my task")
            ai_message = AIMessage(content=final_result)
            new_history = chat_history + [human_message, ai_message]
            
            # Save the final result to memory (both semantic and episodic)
            if self.memory:
                # Save to episodic memory
                self.sync_save_memory(
                    memory_type="episodic",
                    item={
                        "event_type": "final_result",
                        "task": state["input"],
                        "plan": state["plan"],
                        "result": final_result
                    },
                    task=state["input"]
                )
                
                # Save to semantic memory
                self.sync_save_memory(
                    memory_type="semantic",
                    item={
                        "task_type": state["input"].split()[0:5],  # Use first few words as task type
                        "solution": final_result,
                        "successful": True
                    },
                    task=state["input"]
                )
            
            self.logger.debug("Generated final result: %s", final_result[:100] + "..." if len(final_result) > 100 else final_result)
            
            return {
                "final_result": final_result,
                "chat_history": new_history
            }
            
        except Exception as e:
            self.logger.error("Error aggregating results: %s", e)
            # Fallback to a simple concatenation of results
            fallback_result = f"Task: {state['input']}\n\n{execution_summary}"
            return {"final_result": fallback_result}

    def run(self, input_text: str) -> Dict[str, Any]:
        """Run the Plan and Solve agent on the given input.
        
        Args:
            input_text: The input task to process
            
        Returns:
            Dict containing the final result.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        # Initialize state
        initial_state: PlanAndSolveState = {
            "input": input_text,
            "chat_history": [],
            "plan": [],
            "current_step_index": 0,
            "step_results": [],
            "plan_done": False,
            "final_result": None
        }
        
        try:
            self.on_start()
            self.logger.info("Running Plan and Solve agent with input: %s", input_text)
            
            # Prepare input for graph
            inputs_for_graph = {
                "input": input_text,
                "chat_history": []
            }
            
            # Run the graph
            final_state = self.graph.invoke(inputs_for_graph)
            
            # Extract the final result
            result = final_state.get("final_result", "No final result generated.")
            
            self.logger.info("Plan and Solve agent completed successfully")
            return {"output": result}
            
        except Exception as e:
            self.logger.error("Plan and Solve agent execution failed: %s", e, exc_info=True)
            return {"error": str(e)}
        finally:
            self.on_finish()

    def stream(self, input_text: str) -> Any:
        """Stream the Plan and Solve agent execution.
        
        Args:
            input_text: The input task to process
            
        Yields:
            State updates at each step of execution.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        # Initialize state
        initial_state: PlanAndSolveState = {
            "input": input_text,
            "chat_history": [],
            "plan": [],
            "current_step_index": 0,
            "step_results": [],
            "plan_done": False,
            "final_result": None
        }
        
        try:
            self.on_start()
            self.logger.info("Streaming Plan and Solve agent with input: %s", input_text)
            
            # Prepare input for graph
            inputs_for_graph = {
                "input": input_text,
                "chat_history": []
            }
            
            # Stream the graph execution
            for step_output in self.graph.stream(inputs_for_graph):
                yield step_output
                
        except Exception as e:
            self.logger.error("Plan and Solve agent streaming failed: %s", e, exc_info=True)
            yield {"error": str(e)}
        finally:
            self.on_finish()