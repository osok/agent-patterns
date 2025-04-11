"""LLM Compiler agent pattern implementation."""

import operator
import re
import asyncio
from typing import Any, Dict, List, Optional, Union, TypedDict, Annotated, Sequence, cast, Set, Tuple
import logging
from pathlib import Path

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END

from agent_patterns.core.base_agent import BaseAgent

# Define a simple ToolExecutor instead of importing from langgraph.prebuilt
class ToolExecutor:
    """Simple executor for LangChain tools."""
    
    def __init__(self, tools: List[BaseTool]):
        """Initialize with a list of tools."""
        self.tools = {tool.name: tool for tool in tools}
    
    def execute(self, tool_invocation: Dict[str, Any]) -> Any:
        """Execute a tool given a tool invocation."""
        tool_name = tool_invocation["tool_name"]
        tool_input = tool_invocation["tool_input"]
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tools[tool_name]
        return tool.invoke(tool_input)

# Define the state according to LangGraph best practices
class LLMCompilerState(TypedDict):
    """Represents the state of the LLM Compiler agent.

    Attributes:
        input_query: The original user query.
        available_tools: List of available tools for the agent to use.
        task_graph: Dictionary representing the directed acyclic graph of tasks.
        tasks_pending: List of tasks that are ready to be executed.
        tasks_in_progress: List of tasks currently being executed.
        tasks_completed: List of tasks that have been completed.
        task_results: Dictionary mapping task IDs to their results.
        needs_replanning: Whether additional planning is needed.
        final_answer: The final answer to return to the user.
    """
    input_query: str
    available_tools: List[Dict[str, Any]]
    task_graph: Dict[str, Any]
    tasks_pending: List[Dict[str, Any]]
    tasks_in_progress: List[Dict[str, Any]]
    tasks_completed: List[Dict[str, Any]]
    task_results: Dict[str, Any]
    needs_replanning: bool
    final_answer: Optional[str]


class LLMCompilerAgent(BaseAgent):
    """LLM Compiler pattern implementation using LangGraph.
    
    This agent implements a parallel task execution approach that:
    1. Plans a directed acyclic graph (DAG) of tasks
    2. Executes tasks in parallel when dependencies are satisfied
    3. Synthesizes results into a final answer
    
    The primary benefits are improved performance through parallel execution
    and reduced token usage by minimizing redundant LLM calls.
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict],
        tools: List[BaseTool] = None,
        prompt_dir: str = "src/agent_patterns/prompts",
        tool_provider: Optional[Any] = None,
        memory: Optional[Any] = None,
        memory_config: Optional[Dict[str, bool]] = None,
        log_level: int = logging.INFO
    ):
        """Initialize the LLM Compiler agent.
        
        Args:
            llm_configs: Configuration for LLM roles (e.g., {'planner': {...}, 'executor': {...}, 'joiner': {...}}).
            tools: List of LangChain tools available to the agent.
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
        
        # Initialize the LLMs for different roles
        try:
            self.planner_llm = self._get_llm('planner')
            self.executor_llm = self._get_llm('executor')
            self.joiner_llm = self._get_llm('joiner')
        except ValueError as e:
            self.logger.error("Failed to initialize LLMs: %s", e)
            raise ValueError("LLM initialization failed. Make sure required roles are defined in llm_configs.") from e

        # Initialize tools
        self.tools = tools if tools is not None else []
        self.tool_executor = ToolExecutor(self.tools) if self.tools else None
        
        # Prepare tool descriptions for the agent
        self.tool_descriptions = [
            {
                "name": tool.name,
                "description": tool.description,
                "args_schema": str(tool.args)
            }
            for tool in self.tools
        ] if self.tools else []
        
        # If tool_provider is available, add its tools to the descriptions
        if self.tool_provider:
            provider_tools = self.tool_provider.list_tools()
            if provider_tools:
                self.tool_descriptions.extend(provider_tools)
                self.logger.info(f"Added {len(provider_tools)} tools from tool provider")
        
        self.logger.info("Initialized LLM Compiler agent with %d tools", len(self.tool_descriptions))

    def build_graph(self) -> None:
        """Build the LangGraph state graph for the LLM Compiler agent.
        
        The graph consists of:
        1. Planning stage: Generate a directed acyclic graph (DAG) of tasks
        2. Task scheduling: Identify which tasks can be executed based on dependencies
        3. Task execution: Execute tasks in parallel
        4. Joining: Synthesize results into a final answer or replan if needed
        """
        # Create the graph with our state type
        compiler_graph = StateGraph(LLMCompilerState)

        # Define nodes
        compiler_graph.add_node("plan_tasks", self._plan_tasks)
        compiler_graph.add_node("schedule_tasks", self._schedule_tasks)
        compiler_graph.add_node("execute_tasks", self._execute_tasks)
        compiler_graph.add_node("update_task_status", self._update_task_status)
        compiler_graph.add_node("synthesize_results", self._synthesize_results)

        # Define edges
        compiler_graph.set_entry_point("plan_tasks")
        compiler_graph.add_edge("plan_tasks", "schedule_tasks")
        compiler_graph.add_edge("schedule_tasks", "execute_tasks")
        compiler_graph.add_edge("execute_tasks", "update_task_status")
        
        # Conditional edges from update_task_status
        compiler_graph.add_conditional_edges(
            "update_task_status",
            self._should_continue_execution,
            {
                True: "schedule_tasks",  # Continue executing tasks
                False: "synthesize_results"  # All tasks completed, synthesize results
            }
        )
        
        # Conditional edges from synthesize_results
        compiler_graph.add_conditional_edges(
            "synthesize_results",
            self._needs_replanning,
            {
                True: "plan_tasks",  # Need additional planning
                False: END  # Final answer ready
            }
        )
        
        # Compile the graph
        try:
            self.graph = compiler_graph.compile()
            self.logger.info("LLM Compiler agent graph compiled successfully.")
        except Exception as e:
            self.logger.error("Failed to compile LLM Compiler agent graph: %s", e)
            raise RuntimeError("Graph compilation failed") from e

    def _plan_tasks(self, state: LLMCompilerState) -> Dict[str, Any]:
        """Generate a plan as a directed acyclic graph (DAG) of tasks.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with task graph.
        """
        self.logger.debug("Planning tasks for query: %s", state["input_query"])
        
        try:
            # Retrieve relevant memories if memory is enabled
            memories = self.sync_retrieve_memories(state["input_query"])
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
            prompt = self._load_prompt_template("PlannerStep")
            
            # Format the prompt with all relevant information
            formatted_prompt = prompt.invoke({
                "input_query": state["input_query"],
                "available_tools": "\n".join([
                    f"- {tool['name']}: {tool['description']}" 
                    for tool in state["available_tools"]
                ]),
                "memory_context": memory_context
            })
            
            # Get the planner response
            planner_response = self.planner_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the plan from the response
            plan_text = planner_response.content
            
            # Parse the plan into a task graph structure
            task_graph = self._parse_task_plan(plan_text)
            
            self.logger.debug("Generated plan with %d tasks", len(task_graph))
            
            # Initialize task lists
            tasks_pending = []
            
            # Find root tasks (no dependencies)
            for task_id, task in task_graph.items():
                if not task.get("depends_on", []):
                    tasks_pending.append({
                        "id": task_id,
                        "tool": task["tool"],
                        "inputs": task["inputs"]
                    })
            
            return {
                "task_graph": task_graph,
                "tasks_pending": tasks_pending,
                "tasks_in_progress": [],
                "tasks_completed": [],
                "task_results": {}
            }
            
        except Exception as e:
            self.logger.error("Error generating task plan: %s", e, exc_info=True)
            # Return a minimal fallback plan
            return {
                "task_graph": {"1": {"tool": "simple_task", "inputs": {"query": state["input_query"]}}},
                "tasks_pending": [{"id": "1", "tool": "simple_task", "inputs": {"query": state["input_query"]}}],
                "tasks_in_progress": [],
                "tasks_completed": [],
                "task_results": {}
            }

    def _parse_task_plan(self, plan_text: str) -> Dict[str, Any]:
        """Parse the task plan from the planner's response.
        
        Args:
            plan_text: The raw plan text from the planner.
            
        Returns:
            A dictionary representing the task graph.
        """
        task_graph = {}
        
        # Use regex to extract tasks
        task_pattern = r'(\d+)\.\s+(?:task_\d+)?\(tool="([^"]+)",\s+inputs=(\{[^}]+\})(?:,\s+depends_on=\[([^\]]*)\])?\)'
        
        for match in re.finditer(task_pattern, plan_text):
            task_id, tool_name, inputs_str, depends_str = match.groups()
            
            # Process inputs: convert string representation to dict
            # This is a simplified approach - in a real implementation you would use a safer parsing method
            try:
                # Replace single quotes with double quotes
                inputs_str = inputs_str.replace("'", "\"")
                
                # Handle nested quotes by temporarily replacing them
                inputs_str = re.sub(r':\s*"([^"]*)"', lambda m: f': "TEMP_QUOTE_START{m.group(1)}TEMP_QUOTE_END"', inputs_str)
                inputs_str = inputs_str.replace('\\"', 'ESCAPED_QUOTE')
                
                # Parse JSON
                import json
                inputs = json.loads(inputs_str)
                
                # Restore quotes in values
                for key, value in inputs.items():
                    if isinstance(value, str):
                        value = value.replace('TEMP_QUOTE_START', '')
                        value = value.replace('TEMP_QUOTE_END', '')
                        value = value.replace('ESCAPED_QUOTE', '"')
                        inputs[key] = value
                
            except Exception as e:
                self.logger.warning("Error parsing inputs JSON: %s. Input string: %s", e, inputs_str)
                # Fallback if parsing fails
                inputs = {"raw_input": inputs_str}
            
            # Process dependencies
            depends_on = []
            if depends_str:
                depends_on = [d.strip() for d in depends_str.split(',')]
            
            task_graph[task_id] = {
                "tool": tool_name,
                "inputs": inputs,
                "depends_on": depends_on
            }
        
        return task_graph

    def _schedule_tasks(self, state: LLMCompilerState) -> Dict[str, List[Dict[str, Any]]]:
        """Schedule tasks for execution based on their dependencies.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with scheduled tasks.
        """
        self.logger.debug("Scheduling tasks")
        
        # Check for new tasks that can be scheduled
        new_pending_tasks = []
        
        # For each task in the graph, check if all dependencies are met
        for task_id, task in state["task_graph"].items():
            # Skip tasks that are already in progress, completed, or pending
            if any(t["id"] == task_id for t in state["tasks_in_progress"]) or \
               any(t["id"] == task_id for t in state["tasks_completed"]) or \
               any(t["id"] == task_id for t in state["tasks_pending"]):
                continue
            
            # Check if all dependencies are completed
            dependencies_met = True
            for dep_id in task.get("depends_on", []):
                if not any(t["id"] == dep_id for t in state["tasks_completed"]):
                    dependencies_met = False
                    break
            
            # If all dependencies are met, add to pending tasks
            if dependencies_met:
                # Prepare inputs with results from dependencies
                processed_inputs = {}
                for key, value in task["inputs"].items():
                    # Check if the value refers to a task result
                    if isinstance(value, str) and value.startswith("task_result:"):
                        # Extract the task ID from the reference
                        ref_task_id = value.split("task_result:")[1].strip()
                        if ref_task_id in state["task_results"]:
                            processed_inputs[key] = state["task_results"][ref_task_id]
                        else:
                            # Use the original value if the reference can't be resolved
                            processed_inputs[key] = value
                    else:
                        processed_inputs[key] = value
                
                new_pending_tasks.append({
                    "id": task_id,
                    "tool": task["tool"],
                    "inputs": processed_inputs
                })
        
        # Move tasks from pending to in-progress
        in_progress = state["tasks_in_progress"].copy()
        in_progress.extend(state["tasks_pending"])
        
        return {
            "tasks_pending": new_pending_tasks,
            "tasks_in_progress": in_progress
        }

    def _execute_tasks(self, state: LLMCompilerState) -> Dict[str, Any]:
        """Execute tasks in parallel using the tool executor.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with task results.
        """
        self.logger.debug("Executing %d tasks", len(state["tasks_in_progress"]))
        
        if not state["tasks_in_progress"]:
            return {}  # No tasks to execute
        
        # In a real implementation, we would execute tasks in parallel
        # For simplicity, we'll execute one task at a time in this example
        task = state["tasks_in_progress"][0]
        
        try:
            result = None
            tool_name = task["tool"]
            tool_input = task["inputs"]
            
            # First, try using the tool_provider if available
            if self.tool_provider:
                try:
                    self.logger.debug(f"Attempting to execute tool '{tool_name}' via tool_provider")
                    result = self.tool_provider.execute_tool(tool_name, tool_input)
                except Exception as e:
                    self.logger.warning(f"Tool provider failed to execute '{tool_name}': {e}")
            
            # If tool_provider didn't work or isn't available, try the tool_executor
            if result is None and self.tool_executor:
                # Find the matching tool
                if any(tool.name == tool_name for tool in self.tools):
                    # Execute the tool
                    self.logger.debug(f"Executing tool '{tool_name}' via tool_executor")
                    result = self.tool_executor.execute({
                        "tool_name": tool_name,
                        "tool_input": tool_input
                    })
                else:
                    result = f"Tool '{tool_name}' not found"
            
            # If neither tool_provider nor tool_executor worked, simulate a result
            if result is None:
                result = f"Simulated result for task {task['id']} using tool {task['tool']}"
            
            # Update the task results
            task_results = state["task_results"].copy()
            task_results[task["id"]] = result
            
            return {"task_results": task_results}
            
        except Exception as e:
            self.logger.error("Error executing task %s: %s", task["id"], e, exc_info=True)
            
            # Update with error result
            task_results = state["task_results"].copy()
            task_results[task["id"]] = f"Error: {str(e)}"
            
            return {"task_results": task_results}

    def _update_task_status(self, state: LLMCompilerState) -> Dict[str, List[Dict[str, Any]]]:
        """Update the status of tasks after execution.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with updated task status.
        """
        self.logger.debug("Updating task status")
        
        if not state["tasks_in_progress"]:
            return {}  # No tasks to update
        
        # Move the first task from in-progress to completed
        task = state["tasks_in_progress"][0]
        
        in_progress = [t for t in state["tasks_in_progress"] if t["id"] != task["id"]]
        completed = state["tasks_completed"].copy()
        completed.append(task)
        
        return {
            "tasks_in_progress": in_progress,
            "tasks_completed": completed
        }

    def _should_continue_execution(self, state: LLMCompilerState) -> bool:
        """Determine if execution should continue.
        
        Args:
            state: The current graph state.
            
        Returns:
            True if there are still tasks to execute, False otherwise.
        """
        # Continue if there are tasks pending or in progress
        return len(state["tasks_pending"]) > 0 or len(state["tasks_in_progress"]) > 0

    def _synthesize_results(self, state: LLMCompilerState) -> Dict[str, Any]:
        """Synthesize the results of all tasks into a final answer.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with final answer and replanning flag.
        """
        self.logger.debug("Synthesizing results from %d completed tasks", len(state["tasks_completed"]))
        
        try:
            # Retrieve relevant memories for final synthesis
            memories = self.sync_retrieve_memories(state["input_query"])
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
                    self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for synthesis")
            
            # Load the joiner prompt template
            prompt = self._load_prompt_template("JoinerStep")
            
            # Format task results for the prompt
            task_results_text = "\n".join([
                f"Task {task['id']} ({task['tool']}): {state['task_results'].get(task['id'], 'No result')}"
                for task in state["tasks_completed"]
            ])
            
            # Format the prompt
            formatted_prompt = prompt.invoke({
                "input_query": state["input_query"],
                "task_results": task_results_text,
                "memory_context": memory_context
            })
            
            # Get the joiner response
            joiner_response = self.joiner_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the final answer and replanning flag
            response_content = joiner_response.content
            needs_replanning = "needs_replanning=True" in response_content
            
            # Extract the final answer (everything except the replanning flag)
            final_answer = response_content.replace("needs_replanning=True", "").replace("needs_replanning=False", "").strip()
            
            self.logger.debug("Synthesis complete. Needs replanning: %s", needs_replanning)
            
            # Save the execution results to memory if enabled
            if self.memory:
                # Save task execution to episodic memory
                self.sync_save_memory(
                    memory_type="episodic",
                    item={
                        "event_type": "task_execution",
                        "query": state["input_query"],
                        "tasks": [
                            {
                                "id": task["id"],
                                "tool": task["tool"],
                                "result": state["task_results"].get(task["id"], "No result")
                            }
                            for task in state["tasks_completed"]
                        ],
                        "final_answer": final_answer,
                        "needed_replanning": needs_replanning
                    },
                    query=state["input_query"]
                )
                
                # Save to semantic memory
                self.sync_save_memory(
                    memory_type="semantic",
                    item={
                        "query_type": " ".join(state["input_query"].split()[:5]),  # Use first few words as query type
                        "answer": final_answer,
                        "successful": not needs_replanning
                    },
                    query=state["input_query"]
                )
            
            return {
                "final_answer": final_answer,
                "needs_replanning": needs_replanning
            }
            
        except Exception as e:
            self.logger.error("Error synthesizing results: %s", e, exc_info=True)
            
            # Return a fallback answer
            return {
                "final_answer": "I wasn't able to properly synthesize the results due to an error.",
                "needs_replanning": False
            }

    def _needs_replanning(self, state: LLMCompilerState) -> bool:
        """Determine if replanning is needed.
        
        Args:
            state: The current graph state.
            
        Returns:
            True if replanning is needed, False otherwise.
        """
        return state["needs_replanning"]

    def run(self, input_text: str) -> Dict[str, Any]:
        """Run the LLM Compiler agent on the given input.
        
        Args:
            input_text: The input query to process
            
        Returns:
            Dict containing the final result and metadata about the process.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        # Initialize state
        initial_state: LLMCompilerState = {
            "input_query": input_text,
            "available_tools": self.tool_descriptions,
            "task_graph": {},
            "tasks_pending": [],
            "tasks_in_progress": [],
            "tasks_completed": [],
            "task_results": {},
            "needs_replanning": False,
            "final_answer": None
        }
        
        try:
            self.on_start()
            self.logger.info("Running LLM Compiler agent with input: %s", input_text[:100] + "..." if len(input_text) > 100 else input_text)
            
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Extract the final result
            result = final_state.get("final_answer", "No final answer generated.")
            
            # Create metadata about the process
            metadata = {
                "tasks_planned": len(final_state["task_graph"]),
                "tasks_completed": len(final_state["tasks_completed"]),
                "needed_replanning": final_state.get("needs_replanning", False)
            }
            
            self.logger.info("LLM Compiler agent completed successfully with %d tasks", metadata["tasks_completed"])
            return {
                "output": result,
                "metadata": metadata
            }
            
        except Exception as e:
            self.logger.error("LLM Compiler agent execution failed: %s", e, exc_info=True)
            return {"error": str(e)}
        finally:
            self.on_finish()

    def stream(self, input_text: str) -> Any:
        """Stream the LLM Compiler agent execution.
        
        Args:
            input_text: The input query to process
            
        Yields:
            State updates at each step of execution.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        # Initialize state
        initial_state: LLMCompilerState = {
            "input_query": input_text,
            "available_tools": self.tool_descriptions,
            "task_graph": {},
            "tasks_pending": [],
            "tasks_in_progress": [],
            "tasks_completed": [],
            "task_results": {},
            "needs_replanning": False,
            "final_answer": None
        }
        
        try:
            self.on_start()
            self.logger.info("Streaming LLM Compiler agent with input: %s", input_text[:100] + "..." if len(input_text) > 100 else input_text)
            
            # Stream the graph execution
            for step_output in self.graph.stream(initial_state):
                yield step_output
                
        except Exception as e:
            self.logger.error("LLM Compiler agent streaming failed: %s", e, exc_info=True)
            yield {"error": str(e)}
        finally:
            self.on_finish() 