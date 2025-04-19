# Testing Examples

This document serves as a guide for systematically testing each example in the codebase.

## Summary of Testing Results

- **✅ Fully Working**: 12 examples
- **⚠️ Partially Working**: 8 examples
- **❌ Not Working**: 5 examples
- **Not Tested**: 2 examples (LATS examples - excluded by requirement)

Main issues encountered:
1. Asyncio event loop errors in memory initialization
2. Missing prompt templates for some agent patterns
3. Internal agent implementation using `asyncio.run()` inside an existing event loop
4. LangGraph recursion limits for complex workflows
5. Action format parsing issues in ReAct pattern with newer models

## Instructions

1. We will run through each example one at a time.
2. If an example works, we'll note it and move to the next one.
3. If an example fails, Claude will attempt to fix it.
4. If we choose to move on past a broken example, we'll note that it's broken before proceeding to the next one.
5. We need to fix the code and **NOT** the requirements.  We modified the requirements.txt use the latest versions and we need to fix the code so it works with these newer libraries.  If you find a missing library make sure you get the newests and update the rquirements with the newest.
6. All Examples and code must use the .env to determine what llm source and model to be used.  it must know what type of model it needs thinking or coding or what have you.
7. If they are sucesful they dont need to be tested again.

## Examples List

### Test Cases
1. **Default Answer Generation Test**
   - Status: ✅ Passed
   - Description: Tests the default answer generation when LLM fails
   - Location: `tests/test_default_answer.py`

### Base Examples
2. **Memory Example**
   - Status: ⚠️ Partial Success
   - Description: Example of using memory in agents
   - Location: `examples/memory_example.py`

3. **Combined Memory Tools Example**
   - Status: ⚠️ Partial Success
   - Description: Example of combining memory and tools
   - Location: `examples/combined_memory_tools_example.py`

### ReAct Examples
4. **ReAct Simple Example**
   - Status: ✅ Success
   - Description: Simple example of using ReAct agent pattern
   - Location: `examples/react/simple_example.py`
   - Details: Fixed the prompt templates to provide clearer instructions to the LLM on the exact format to follow. The example now runs successfully and correctly uses the tools to answer both questions in the task.

5. **ReAct Complex Reasoning Example**
   - Status: ✅ Success
   - Description: Example of complex reasoning with ReAct
   - Location: `examples/react/complex_reasoning_example.py`
   - Details: Updated the example to use environment variables for model configuration and fixed the prompt templates. The agent now correctly follows the ReAct pattern to solve a multi-step reasoning task involving searching for information, extracting concepts, and comparing them. Both the agent-based and direct implementations work successfully.

6. **ReAct Tool Provider Example**
   - Status: ✅ Success
   - Description: Example of using tool providers with ReAct
   - Location: `examples/react/tool_provider_example.py`
   - Details: Updated the example to use environment variables for model configuration and run both the agent-based and fixed implementations. The agent successfully figures out the correct parameter format for the tools and uses them effectively to complete all tasks.

### Reflexion Examples
7. **Reflexion Simple Example**
   - Status: ✅ Success
   - Description: Simple example of using Reflexion agent pattern
   - Location: `examples/reflexion/simple_example.py`
   - Details: The example runs successfully, demonstrating the Reflexion agent solving a Fibonacci implementation task efficiently using an iterative approach. The agent completes the task in a single trial and provides a detailed reflection on the solution approach.

8. **Reflexion Chess Analysis Example**
   - Status: ✅ Success
   - Description: Chess analysis example using Reflexion
   - Location: `examples/reflexion/chess_analysis_example.py`
   - Details: The example successfully analyzes a chess position, identifies the best move for white, and provides a detailed explanation of the reasoning process. The agent completes the analysis in a single trial and offers a thoughtful reflection on its approach.

### Plan and Solve Examples
9. **Plan and Solve Simple Example**
   - Status: ⚠️ Partial Success
   - Description: Simple example of using Plan and Solve pattern
   - Location: `examples/plan_and_solve/simple_example.py`
   - Details: Fixed asyncio issues with memory operations and updated to use model configuration from .env file. The example runs but hits a graph recursion limit after successfully executing 12 steps out of 19 in the plan.

10. **Plan and Solve Trip Planner Example**
    - Status: ⚠️ Partial Success
    - Description: Trip planning with Plan and Solve
    - Location: `examples/plan_and_solve/trip_planner_example.py`
    - Details: Fixed code to properly handle errors and display error messages. The example runs correctly but also encounters a graph recursion limit after executing 12 steps out of 17 in the trip planning process.

11. **Plan and Solve Memory Integration Example**
    - Status: ✅ Success
    - Description: Memory integration with Plan and Solve
    - Location: `examples/plan_and_solve/memory_integration_example.py`
    - Details: Fixed asyncio issues with memory operations, updated the CalculatorTool to implement the ToolProvider interface, and used model configuration from the .env file. The example runs successfully, demonstrating how the agent uses different types of memory during multi-turn interactions.

### Storm Examples
12. **Storm Basic Article Generation**
    - Status: ⚠️ Not Working
    - Description: Basic article generation with Storm
    - Location: `examples/storm/basic_article_generation.py`
    - Details: Attempted to fix the example by updating model configurations to use environment variables from .env file. The example has multiple issues:
      1. asyncio errors with nested event loops in memory retrieval
      2. Missing prompt templates for the STORM agent
      3. After creating the missing templates, encountered string attribute errors, suggesting structural issues with the agent's implementation

13. **Storm Streaming Article Generation**
    - Status: ⚠️ Not Working
    - Description: Streaming article generation with Storm
    - Location: `examples/storm/streaming_article_generation.py`
    - Details: Similar issues to the basic article generation example:
      1. Updated model configurations to use environment variables from .env file
      2. Created missing prompt templates for ExpertRole and ResearcherRole
      3. Encountered string attribute error ('str' object has no attribute 'content'), suggesting a mismatch between expected model response format and actual implementation

### ReWOO Examples
14. **ReWOO Simple Example**
    - Status: ✅ Success
    - Description: Simple example of using ReWOO pattern
    - Location: `examples/rewoo/simple_example.py`
    - Details: Fixed the asyncio issues in the setup_memory function by making it async and properly awaiting persistence and memory operations. The example now runs successfully, demonstrating how the ReWOO agent follows a structured plan to research climate change and generate a comprehensive summary. The model configurations are properly loaded from the .env file.

15. **ReWOO Math Solver Example**
    - Status: ✅ Success
    - Description: Math problem solving with ReWOO
    - Location: `examples/rewoo/math_solver_example.py`
    - Details: Fixed the example by updating import paths to use the current package structure, implementing a proper ToolProvider class, and using environment variables for model configuration. The example works successfully, demonstrating how the ReWOO agent can solve a math word problem about movie theater ticket sales through step-by-step reasoning and calculation.

16. **ReWOO Travel Planner Example**
    - Status: ✅ Success
    - Description: Travel planning with ReWOO
    - Location: `examples/rewoo/travel_planner_example.py`
    - Details: The example runs successfully, generating a comprehensive travel plan for a 3-day trip from New York to Paris, completing all 10 planned steps including flights, accommodations, and daily itineraries.

17. **ReWOO Web Research Example**
    - Status: ⚠️ Not Working
    - Description: Web research with ReWOO
    - Location: `examples/rewoo/web_research_example.py`
    - Details: The example encounters a LangGraph recursion limit error, appearing to get stuck in a loop while executing the planned steps. The error occurs after completing 5 out of 8 planned steps.

### MCP Example
18. **MCP Example**
    - Status: ⚠️ Not Working
    - Description: Example of using MCP (Multimodal Conversational Pathway)
    - Location: `examples/mcp/mcp_example.py`
    - Details: The example requires specific MCP server configuration in the environment which is not set up. The example exits with the message "No MCP servers configured in environment."

### Self Discovery Examples
19. **Self Discovery Basic Reasoning**
    - Status: ⚠️ Partial Success
    - Description: Basic reasoning with Self Discovery
    - Location: `examples/self_discovery/basic_reasoning.py`
    - Details: Fixed the asyncio event loop error by properly handling async/await patterns in memory setup and initialization. The example now runs but encounters errors in the SelfDiscoveryAgent internal implementation. The error occurs because the agent's internal methods use `asyncio.run()` inside an existing event loop, which is not allowed.

### LATS Examples  (Don't TEST)
20. **LATS Simple Example**
    - Status: ⚠️ Not Working (Don't TEST)
    - Description: Simple example of using LATS
    - Location: `examples/lats/simple_example.py`
    - Details: The example encounters the same asyncio event loop error as other examples. This appears to be a common issue with the memory initialization process.

21. **LATS Engineering Problem Example**
    - Status: Not tested  (Don't TEST)
    - Description: Engineering problem solving with LATS
    - Location: `examples/lats/engineering_problem_example.py`
    - Details: Not tested due to the same issue observed in the LATS simple example.

22. **LATS Medical Diagnosis Example**
    - Status: Not tested  (Don't TEST)
    - Description: Medical diagnosis with LATS
    - Location: `examples/lats/medical_diagnosis_example.py`
    - Details: Not tested due to the same issue observed in the LATS simple example.

### LLM Compiler Examples
23. **LLM Compiler Example**
    - Status: ✅ Partial Success
    - Description: Basic LLM Compiler usage
    - Location: `examples/llm_compiler/llm_compiler_example.py`
    - Details: Fixed the issue with missing prompt templates by updating the prompt directory path to correctly point to src/agent_patterns/prompts. The basic example now runs successfully, but complex query example hits a recursion limit in the LangGraph execution, which seems to be a limitation of the framework rather than an issue with our code.

24. **LLM Compiler DAG Example**
    - Status: ✅ Success
    - Description: DAG-based LLM Compiler
    - Location: `examples/llm_compiler/llm_compiler_dag_example.py`
    - Details: Fixed the prompt template directory path to use the correct location at src/agent_patterns/prompts.
    - The example runs successfully, generating a comprehensive research summary on AI planning.
    - The task visualization component works as expected, but no task graph is displayed since the agent processed the query directly without breaking it into subtasks.

25. **LLM Compiler Parallel vs Sequential Example**
    - Status: ⚠️ Partial Success
    - Description: Comparing parallel and sequential execution
    - Location: `examples/llm_compiler/parallel_vs_sequential_example.py`
    - Details: Fixed the prompt template directory paths for both the LLMCompiler and ReAct agents.
    - The LLM Compiler portion works correctly, executing the multiple tasks in parallel and generating the final output.
    - The ReAct agent part has issues parsing the action format, suggesting the ReAct prompts may need updating for newer models.
    - The performance comparison isn't accurate since only one of the methods fully worked.

### Reflection Examples
26. **Reflection Simple Example**
    - Status: ⚠️ Partial Success
    - Description: Simple example of using Reflection
    - Location: `examples/reflection/simple_example.py`
    - Details: Fixed the asyncio event loop error by properly handling async/await patterns in memory setup and initialization. The example now runs but encounters errors in the ReflectionAgent internal implementation. Similar to the Self Discovery agent, it uses `asyncio.run()` inside an existing event loop.

27. **Reflection Code Review Example**
    - Status: ✅ Success
    - Description: Code review with Reflection
    - Location: `examples/reflection/code_review_example.py`
    - Details: The example runs successfully, performing a detailed code review of a Python function that calculates statistics, identifying issues with empty lists, inefficient variance calculation, and providing an improved implementation with proper error handling.

## Testing Log

### 1. Default Answer Generation Test
- **Command run**: `python -m tests.test_default_answer`
- **Result**: ✅ Success
- **Details**: All 2 tests passed successfully.

### 2. Memory Example
- **Command run**: `python -m examples.memory_example`
- **Result**: ⚠️ Partial Success
- **Details**: 
  - Fixed the initial asyncio event loop error by rewriting the example to use proper async/await patterns.
  - Installed the missing `wikipedia` package.
  - The example runs but still has warnings about `asyncio.run()` being called from a running event loop in the ReActAgent class.
  - The agent responses were generic and didn't properly use the memory, suggesting deeper integration issues.
  - Memories were successfully stored and retrieved at the end of the example.

### 3. Combined Memory Tools Example
- **Command run**: `python -m examples.combined_memory_tools_example`
- **Result**: ⚠️ Partial Success
- **Details**: 
  - Fixed the initial asyncio event loop error by rewriting the example to use proper async/await patterns.
  - The example runs but has the same issues as the Memory Example with warnings about `asyncio.run()` in the ReActAgent class.
  - The tools were not properly loaded (0 tools shown) and the agent responses were generic.
  - Memories were successfully stored and retrieved at the end of the example.
  - More comprehensive fixes would require modifying the core ReActAgent class to properly handle async operations.

### 19. Self Discovery Basic Reasoning
- **Command run**: `python -m examples.self_discovery.basic_reasoning`
- **Result**: ⚠️ Partial Success
- **Details**:
  - Fixed the initial asyncio event loop error by modifying setup_memory to return the persistence layer and creating a separate initialize_memory async function.
  - Updated main to use proper async/await patterns with asyncio.run() at the top level.
  - The example runs but encounters internal errors in the SelfDiscoveryAgent implementation which uses asyncio.run() inside an already running event loop.
  - Core agent code would need to be modified to properly support async operations.

### 26. Reflection Simple Example
- **Command run**: `python -m examples.reflection.simple_example`
- **Result**: ⚠️ Partial Success
- **Details**:
  - Applied the same async/await pattern fixes as for the Self Discovery example.
  - Similar issues with the agent's internal implementation using asyncio.run() inside an existing event loop.
  - Semantic memories were successfully retrieved at the end of the example.

### 23. LLM Compiler Example
- **Command run**: `python -m examples.llm_compiler.llm_compiler_example`
- **Result**: ✅ Partial Success
- **Details**:
  - Fixed the issue with missing prompt templates by updating the prompt directory path to correctly point to src/agent_patterns/prompts.
  - The basic example runs successfully, calculating results and retrieving weather information.
  - The complex query example hits a recursion limit in LangGraph after 25 iterations, which seems to be a framework limitation.
  - The streaming example also works well for the basic tasks.

### 24. LLM Compiler DAG Example
- **Command run**: `python -m examples.llm_compiler.llm_compiler_dag_example`
- **Result**: ✅ Success
- **Details**:
  - Fixed the prompt template directory path to use the correct location at src/agent_patterns/prompts.
  - The example runs successfully, generating a comprehensive research summary on AI planning.
  - The task visualization component works as expected, but no task graph is displayed since the agent processed the query directly without breaking it into subtasks.

### 25. LLM Compiler Parallel vs Sequential Example
- **Command run**: `python -m examples.llm_compiler.parallel_vs_sequential_example`
- **Result**: ⚠️ Partial Success
- **Details**:
  - Fixed the prompt template directory paths for both the LLMCompiler and ReAct agents.
  - The LLM Compiler portion works correctly, executing the multiple tasks in parallel and generating the final output.
  - The ReAct agent part has issues parsing the action format, suggesting the ReAct prompts may need updating for newer models.
  - The performance comparison isn't accurate since only one of the methods fully worked.

## Model Configuration

To ensure all examples use consistent model configurations from the environment variables rather than hardcoded values:
1. Created a utility module `examples/utils/model_config.py` that provides standardized functions to load model configurations
2. Updated examples to use these utilities instead of hardcoded model defaults
3. This ensures all examples respect the model configurations defined in the `.env` file 