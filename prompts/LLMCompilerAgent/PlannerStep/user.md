## User Input
{input_query}

{memory_context}

## Available Tools
{available_tools}

## Task
Please analyze the user input and create a detailed plan with the following format:

1. First identify the tasks that need to be performed to answer the user query.
2. Structure these tasks as a DAG by using a numbered list with dependencies in parentheses.
3. For each task, specify:
   - The tool to use
   - The specific inputs for that tool
   - Which previous task outputs (if any) this task depends on

Example Format:
1. task_1(tool="tool_name", inputs={"param1": "value1"})
2. task_2(tool="tool_name", inputs={"param1": "value1"}, depends_on=[1])
3. task_3(tool="tool_name", inputs={"param1": "value1"}, depends_on=[1, 2])

Please create an optimized plan that maximizes parallel execution when possible.
Consider any relevant information from memory when creating your plan. 