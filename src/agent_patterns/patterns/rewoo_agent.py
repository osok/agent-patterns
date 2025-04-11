"""
REWOO Agent Pattern Implementation

This module implements the Reasoning Without Observation (REWOO) agent pattern,
which decouples planning from execution to improve efficiency and performance.

The pattern consists of two main components:
1. Planner/Worker: Generates a plan without executing tools
2. Solver/Executor: Executes the plan by following the steps

Key advantages:
- Reduces token consumption by separating reasoning from observation
- Improves performance through specialized roles
- Enables using different LLMs for planning vs. execution
"""

from typing import Any, Dict, List, Optional, TypedDict, Annotated, Sequence
import operator
import logging
from agent_patterns.core.base_agent import BaseAgent
from langgraph.graph import StateGraph, END
import re

logger = logging.getLogger(__name__)

# Define the state schema using TypedDict
class REWOOState(TypedDict):
    """
    Represents the state of the REWOO agent.
    
    Attributes:
        input: The initial user input.
        plan: List of steps in the execution plan.
        current_step_index: Index of the current step being executed.
        execution_results: List of results from executing steps.
        iteration_count: Number of iterations performed.
        execution_complete: Whether execution is complete.
        final_answer: The final synthesized answer.
    """
    input: str
    plan: List[Dict[str, Any]]
    current_step_index: int
    execution_results: List[Dict[str, Any]]
    iteration_count: int
    execution_complete: bool
    final_answer: Optional[str]

class REWOOAgent(BaseAgent):
    """
    Implementation of the REWOO (Reasoning Without Observation) agent pattern.
    
    This pattern separates reasoning (planning) from observations (execution)
    to improve efficiency and performance. It consists of a planner component
    that creates a structured plan, and an executor component that follows
    the plan and uses tools to complete tasks.
    """
    
    def __init__(
        self, 
        llm_configs: dict, 
        tool_registry: Optional[Dict[str, Any]] = None,
        prompt_dir: str = "src/agent_patterns/prompts",
        tool_provider: Optional[Any] = None,
        memory: Optional[Any] = None,
        memory_config: Optional[Dict[str, bool]] = None,
        max_iterations: int = 5,
        **kwargs
    ):
        """
        Initialize the REWOO agent.
        
        Args:
            llm_configs: Dictionary of LLM configurations for different roles
            tool_registry: Dictionary of tools available to the agent
            prompt_dir: Directory containing prompt templates
            tool_provider: Optional provider for tools the agent can use
            memory: Optional composite memory instance
            memory_config: Configuration for which memory types to use
            max_iterations: Maximum number of execution iterations
        """
        self.tool_registry = tool_registry or {}
        self.max_iterations = max_iterations
        super().__init__(
            llm_configs=llm_configs, 
            prompt_dir=prompt_dir, 
            tool_provider=tool_provider,
            memory=memory,
            memory_config=memory_config,
            **kwargs
        )
    
    def build_graph(self) -> None:
        """
        Construct the LangGraph for the REWOO pattern.
        
        The graph consists of these main nodes:
        1. plan_steps: Generate a structured plan
        2. execute_step: Execute a single step of the plan
        3. check_completion: Check if execution is complete
        4. format_final_answer: Format the final answer
        """
        # Create the graph with our state type
        sg = StateGraph(REWOOState)
        
        # Define nodes
        sg.add_node("plan_steps", self._plan_steps)
        sg.add_node("execute_step", self._execute_step)
        sg.add_node("check_completion", self._check_completion)
        sg.add_node("format_final_answer", self._format_final_answer)
        
        # Define edges
        sg.set_entry_point("plan_steps")
        sg.add_edge("plan_steps", "execute_step")
        sg.add_edge("execute_step", "check_completion")
        
        # Add conditional edges based on execution completion
        sg.add_conditional_edges(
            "check_completion",
            self._should_continue_execution,
            {
                True: "execute_step",  # If not complete, continue executing
                False: "format_final_answer"  # If complete, format final answer
            }
        )
        
        # Add edge from format_final_answer to END
        sg.add_edge("format_final_answer", END)
        
        self.graph = sg.compile()
    
    def _should_continue_execution(self, state: REWOOState) -> bool:
        """
        Check if execution should continue.
        
        Args:
            state: Current agent state
            
        Returns:
            True if execution should continue, False if complete
        """
        return not state["execution_complete"]
    
    def run(self, input_data: Any, config: Optional[Dict[str, Any]] = None) -> Any:
        """
        Run the REWOO agent on the given input.
        
        Args:
            input_data: User query or task description
            config: Optional configuration parameters like recursion_limit
            
        Returns:
            Final response after execution
            
        Raises:
            Exception: If an error occurs during execution
        """
        initial_state: REWOOState = {
            "input": input_data,
            "plan": [],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        logger.info(f"Starting REWOO agent with input: {input_data}")
        # Don't catch exceptions here to allow them to propagate
        final_state = self.graph.invoke(initial_state, config=config)
        logger.info("REWOO agent execution completed")
        
        return final_state["final_answer"]
    
    def stream(self, input_data: Any, config: Optional[Dict[str, Any]] = None):
        """
        Stream the execution of the REWOO agent.
        
        Args:
            input_data: User query or task description
            config: Optional configuration parameters like recursion_limit
            
        Yields:
            Intermediate results during execution
        """
        initial_state: REWOOState = {
            "input": input_data,
            "plan": [],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        # Use try/except to gracefully handle any streaming issues
        try:
            for event in self.graph.stream(initial_state, config=config):
                if "state" in event and "final_answer" in event["state"] and event["state"]["final_answer"]:
                    yield event["state"]["final_answer"]
                elif "state" in event and "current_step_index" in event["state"]:
                    current_step = event["state"].get("current_step_index", 0)
                    plan_length = len(event["state"].get("plan", []))
                    if plan_length > 0:
                        yield f"Executing step {current_step + 1} of {plan_length}..."
        except Exception as e:
            # Log the error and fall back to non-streaming
            logger.warning(f"Error during streaming: {str(e)}. Falling back to non-streaming.")
            # Fall back to non-streaming in case of any error
            result = self.run(input_data, config=config)
            yield result
            
    def _plan_steps(self, state: REWOOState) -> Dict:
        """
        Generate a structured plan without executing tools.
        
        This function uses the planner LLM to create a detailed plan
        with steps that will be executed separately.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with plan
        """
        planner_llm = self._get_llm("planner")
        prompt_template = self._load_prompt_template("PlannerPrompt")
        
        # Generate plan using the planner LLM
        logger.info(f"Generating plan for input: {state['input']}")
        
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
                    logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for planning")
        
        # Format the prompt with the input and memory context
        prompt_args = {
            "input": state["input"],
            "memory_context": memory_context
        }
        
        # Get formatted messages
        messages = prompt_template.format_messages(**prompt_args)
        
        # Call the LLM
        planning_response = planner_llm.invoke(messages)
        
        # Parse the planning response into structured steps
        # Handle different response formats (string, dict with content, AIMessage)
        if isinstance(planning_response, str):
            plan_text = planning_response
        elif isinstance(planning_response, dict) and "content" in planning_response:
            plan_text = planning_response["content"]
        elif hasattr(planning_response, "content"):
            plan_text = planning_response.content
        else:
            logger.warning(f"Unexpected planning response format: {type(planning_response)}")
            plan_text = str(planning_response)
        
        # Parse plan text into structured steps using more robust parsing
        plan_lines = plan_text.strip().split("\n")
        structured_plan = []
        
        # Regular expressions for step detection
        step_patterns = [
            r'^Step\s+(\d+)[\s:.)-]*(.*)$',  # Step 1: Do something
            r'^(\d+)[\s:.)-]+(.*)$',         # 1. Do something
            r'^(\d+)\)\s+(.*)$',              # 1) Do something 
            r'^\*\s+Step\s+(\d+)[\s:.)-]*(.*)$',  # * Step 1: Do something
            r'^\*\s+(\d+)[\s:.)-]+(.*)$'     # * 1. Do something
        ]
        
        current_step = None
        step_content = []
        
        def process_current_step():
            """Helper function to process and add the current step to the structured plan."""
            if current_step and step_content:
                # Join all content lines for the step
                details = "\n".join(step_content).strip()
                current_step["details"] = details
                
                # Try to identify tool mentions in the details
                if details:
                    # Look for tools from the tool registry
                    for tool in self.tool_registry.keys():
                        if tool.lower() in details.lower() and tool not in current_step["tools"]:
                            current_step["tools"].append(tool)
                    
                    # Look for tools from the tool provider, if available
                    if self.tool_provider:
                        try:
                            provider_tools = self.tool_provider.list_tools()
                            for tool_info in provider_tools:
                                tool_name = tool_info.get("name", "")
                                if tool_name.lower() in details.lower() and tool_name not in current_step["tools"]:
                                    current_step["tools"].append(tool_name)
                        except Exception as e:
                            logger.warning(f"Error retrieving tools from tool_provider: {str(e)}")
                
                structured_plan.append(current_step)
        
        for line in plan_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts a new step
            is_new_step = False
            step_num = len(structured_plan) + 1
            step_desc = line
            
            for pattern in step_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    is_new_step = True
                    try:
                        step_num = int(match.group(1))
                    except (IndexError, ValueError):
                        step_num = len(structured_plan) + 1
                    
                    # Get the step description from the matched group
                    step_desc = match.group(2).strip() if match.group(2) else line
                    break
            
            if is_new_step:
                # Process the previous step if it exists
                process_current_step()
                
                # Start a new step
                current_step = {
                    "step_id": step_num,
                    "description": step_desc,
                    "details": "",
                    "tools": [],
                    "depends_on": []
                }
                step_content = []
            elif current_step:
                # Add line to current step's content
                step_content.append(line)
        
        # Process the last step
        process_current_step()
            
        # If no structured plan was created, create a simple default plan
        if not structured_plan:
            structured_plan = [{
                "step_id": 1,
                "description": f"Complete the task: {state['input']}",
                "details": plan_text,
                "tools": [],
                "depends_on": []
            }]
        
        # Ensure step_ids are unique and sequential if needed
        if len(structured_plan) > 0:
            # Sort by step_id first to preserve any intentional ordering
            structured_plan.sort(key=lambda x: x["step_id"])
            
            # Then reassign ids sequentially starting from 1
            for i, step in enumerate(structured_plan, 1):
                step["step_id"] = i
        
        # Save the plan to episodic memory if memory is enabled
        if self.memory:
            self.sync_save_memory(
                memory_type="episodic",
                item={
                    "event_type": "plan_generation",
                    "task": state["input"],
                    "plan": [step["description"] for step in structured_plan]
                },
                task=state["input"]
            )
            
        logger.info(f"Generated plan with {len(structured_plan)} steps")
        return {"plan": structured_plan}
    
    def _execute_step(self, state: REWOOState) -> Dict:
        """
        Execute the current step in the plan.
        
        This function takes the current step from the plan and executes it
        using the solver LLM and available tools.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with execution results
        """
        # Increment iteration count
        iteration_count = state.get("iteration_count", 0) + 1
        
        # Ensure the state has a plan
        if "plan" not in state or not state["plan"]:
            logger.warning("No plan found in state. Cannot execute step.")
            return {"execution_complete": True, "iteration_count": iteration_count}
        
        # Get current step
        current_step_index = state["current_step_index"]
        if current_step_index >= len(state["plan"]):
            # No more steps to execute
            return {"execution_complete": True, "iteration_count": iteration_count}
            
        # Check if we've exceeded the max iterations
        if iteration_count > self.max_iterations:
            logger.warning(f"Reached maximum iterations ({self.max_iterations}). Stopping execution.")
            return {"execution_complete": True, "iteration_count": iteration_count}
            
        current_step = state["plan"][current_step_index]
        logger.info(f"Executing step {current_step_index + 1}: {current_step['description']}")
        
        # Prepare context from previous execution results
        context = ""
        for result in state.get("execution_results", []):
            step_id = result["step_id"]
            context += f"Step {step_id} result: {result['result']}\n"
        
        # Retrieve relevant memories for this step
        memory_context = ""
        if self.memory:
            step_query = f"{state['input']} - {current_step['description']}"
            memories = self.sync_retrieve_memories(step_query)
            
            # Format memories for inclusion in the prompt
            if memories:
                memory_sections = []
                for memory_type, items in memories.items():
                    if items:
                        items_text = "\n- ".join([str(item) for item in items])
                        memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                
                if memory_sections:
                    memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                    logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for step execution")
        
        # Get available tools information
        tools_description = ""
        
        # First add tools from tool_registry
        if self.tool_registry:
            tool_descriptions = []
            for tool_name in self.tool_registry.keys():
                tool_descriptions.append(f"- {tool_name}")
            if tool_descriptions:
                tools_description += "Available tools from registry:\n" + "\n".join(tool_descriptions) + "\n\n"
        
        # Then add tools from tool_provider if available
        if self.tool_provider:
            try:
                provider_tools = self.tool_provider.list_tools()
                if provider_tools:
                    provider_tool_descriptions = []
                    for tool_info in provider_tools:
                        tool_name = tool_info.get("name", "")
                        tool_desc = tool_info.get("description", "")
                        provider_tool_descriptions.append(f"- {tool_name}: {tool_desc}")
                    if provider_tool_descriptions:
                        tools_description += "Available tools from provider:\n" + "\n".join(provider_tool_descriptions) + "\n\n"
            except Exception as e:
                logger.warning(f"Error retrieving tools from tool_provider: {str(e)}")
        
        # Get solver LLM and prompt
        solver_llm = self._get_llm("solver")
        prompt_template = self._load_prompt_template("SolverPrompt")
        
        # Format the prompt with the step information
        prompt_args = {
            "step_description": current_step["description"],
            "step_details": current_step.get("details", ""),
            "context": context,
            "memory_context": memory_context,
            "tools_description": tools_description
        }
        
        # Get formatted messages
        messages = prompt_template.format_messages(**prompt_args)
        
        # Execute step using solver LLM
        execution_response = solver_llm.invoke(messages)
        
        # Extract execution result
        # Handle different response formats (string, dict with content, AIMessage)
        if isinstance(execution_response, str):
            execution_result = execution_response
        elif isinstance(execution_response, dict) and "content" in execution_response:
            execution_result = execution_response["content"]
        elif hasattr(execution_response, "content"):
            execution_result = execution_response.content
        else:
            logger.warning(f"Unexpected execution response format: {type(execution_response)}")
            execution_result = str(execution_response)
        
        # Check if any tools need to be called based on LLM output
        tool_calls = self._extract_tool_calls(execution_result)
        tool_outputs = []
        
        # Execute tool calls if any
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            
            # Try to use the tool_provider first if available
            if self.tool_provider and tool_name:
                try:
                    logger.info(f"Attempting to execute tool '{tool_name}' via tool_provider")
                    result = self.tool_provider.execute_tool(tool_name, tool_args)
                    tool_outputs.append({
                        "tool": tool_name,
                        "output": result
                    })
                    continue  # Skip to next tool call if successful
                except Exception as e:
                    logger.warning(f"Tool provider failed to execute '{tool_name}': {e}")
                    # Fall back to tool_registry
            
            # Try using the tool_registry if the tool exists there
            if tool_name in self.tool_registry:
                try:
                    logger.info(f"Calling tool from registry: {tool_name} with args: {tool_args}")
                    tool_result = self.tool_registry[tool_name](**tool_args)
                    tool_outputs.append({
                        "tool": tool_name,
                        "output": tool_result
                    })
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error executing tool {tool_name}: {error_msg}")
                    # Include both output and error keys for better compatibility
                    tool_outputs.append({
                        "tool": tool_name,
                        "output": {"error": error_msg},
                        "error": error_msg
                    })
            else:
                error_msg = "Tool not available"
                logger.warning(f"Tool not found: {tool_name}")
                tool_outputs.append({
                    "tool": tool_name, 
                    "output": {"error": error_msg},
                    "error": error_msg
                })
        
        # Build the execution result
        new_result = {
            "step_id": current_step["step_id"],
            "result": execution_result,
            "tool_outputs": tool_outputs,
            "success": True  # Assume success for now - could be determined by additional logic
        }
        
        # Get a copy of the existing execution results and append the new result
        execution_results = state.get("execution_results", []).copy()
        execution_results.append(new_result)
        
        # Save the step execution to episodic memory if enabled
        if self.memory:
            self.sync_save_memory(
                memory_type="episodic",
                item={
                    "event_type": "step_execution",
                    "task": state["input"],
                    "step": current_step["description"],
                    "step_index": current_step_index,
                    "result": execution_result,
                    "tool_outputs": [f"{output['tool']}: {output['output']}" for output in tool_outputs]
                },
                task=state["input"]
            )
        
        # Move to next step and update state
        return {
            "plan": state["plan"],  # Preserve the plan
            "execution_results": execution_results,
            "current_step_index": current_step_index + 1,
            "iteration_count": iteration_count
        }
    
    def _check_completion(self, state: REWOOState) -> Dict:
        """
        Check if all steps have been executed.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with completion status
        """
        if state["current_step_index"] >= len(state["plan"]):
            logger.info("All steps have been executed. Execution complete.")
            return {"execution_complete": True}
        else:
            logger.info(f"Execution continuing. {state['current_step_index']}/{len(state['plan'])} steps complete.")
            return {"execution_complete": False}
    
    def _format_final_answer(self, state: REWOOState) -> Dict:
        """
        Format the final answer based on execution results.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with final answer
        """
        # Retrieve relevant memories for final synthesis
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
                    logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for final synthesis")
        
        # Get final answer LLM (can be same as solver)
        final_llm = self._get_llm("solver")
        prompt_template = self._load_prompt_template("FinalAnswerPrompt")
        
        # Format the execution results for the LLM
        execution_summary = ""
        
        # Ensure execution_results exists in state
        execution_results = state.get("execution_results", [])
        plan = state.get("plan", [])
        
        # If execution_results is missing but execution_complete is True,
        # provide a default empty list but still continue
        if not execution_results and state.get("execution_complete", False):
            logger.warning("Execution is marked as complete but no execution_results found in state")
            execution_results = []
        
        for i, result in enumerate(execution_results):
            step_id = result["step_id"]
            step_desc = next((s["description"] for s in plan if s["step_id"] == step_id), f"Step {step_id}")
            execution_summary += f"Step {step_id}: {step_desc}\nResult: {result['result']}\n\n"
            
            # Include tool outputs
            tool_outputs = result.get("tool_outputs", [])
            if tool_outputs:
                execution_summary += "Tool outputs:\n"
                for output in tool_outputs:
                    tool_name = output.get("tool", "unknown")
                    if "output" in output:
                        execution_summary += f"- {tool_name}: {output['output']}\n"
                    else:
                        execution_summary += f"- {tool_name}: Error - {output.get('error', 'unknown error')}\n"
                execution_summary += "\n"
        
        # If no execution results, provide a generic summary
        if not execution_summary:
            execution_summary = "No detailed execution results available."
        
        # Format the prompt with the input and execution summary
        prompt_args = {
            "input": state.get("input", "No input provided"),
            "execution_summary": execution_summary,
            "memory_context": memory_context
        }
        
        # Get formatted messages
        messages = prompt_template.format_messages(**prompt_args)
        
        # Generate final answer
        logger.info("Generating final answer")
        final_response = final_llm.invoke(messages)
        
        # Handle different response formats (string, dict with content, AIMessage)
        if isinstance(final_response, str):
            final_answer = final_response
        elif isinstance(final_response, dict) and "content" in final_response:
            final_answer = final_response["content"]
        elif hasattr(final_response, "content"):
            final_answer = final_response.content
        else:
            logger.warning(f"Unexpected final response format: {type(final_response)}")
            final_answer = str(final_response)
            
        logger.info("Final answer generated")
        
        # Save the final result to memory (both semantic and episodic)
        if self.memory:
            # Save to episodic memory
            self.sync_save_memory(
                memory_type="episodic",
                item={
                    "event_type": "final_result",
                    "task": state["input"],
                    "plan": [step["description"] for step in state["plan"]],
                    "result": final_answer
                },
                task=state["input"]
            )
            
            # Save to semantic memory
            self.sync_save_memory(
                memory_type="semantic",
                item={
                    "task_type": " ".join(state["input"].split()[:5]),  # Use first few words as task type
                    "solution": final_answer,
                    "successful": True
                },
                task=state["input"]
            )
        
        return {"final_answer": final_answer}
    
    def _extract_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract tool calls from LLM output.
        
        This is a simplified implementation. In a production environment,
        you'd want more robust parsing, possibly using structured outputs
        from the LLM.
        
        Args:
            text: LLM output text
            
        Returns:
            List of tool call dictionaries
        """
        tool_calls = []
        
        # Check for common tool call formats
        if "TOOL:" in text or "Tool:" in text or "tool:" in text:
            lines = text.split("\n")
            current_tool = None
            current_args = {}
            
            for line in lines:
                line = line.strip()
                
                # Look for tool markers
                if line.upper().startswith("TOOL:") or line.startswith("Tool:") or line.startswith("tool:"):
                    # Save previous tool if exists
                    if current_tool:
                        tool_calls.append({"name": current_tool, "args": current_args})
                    
                    # Start new tool
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current_tool = parts[1].strip()
                        current_args = {}
                
                # Look for arguments
                elif ":" in line and current_tool:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        current_args[key] = value
            
            # Add the final tool if it exists
            if current_tool:
                tool_calls.append({"name": current_tool, "args": current_args})
        
        return tool_calls 