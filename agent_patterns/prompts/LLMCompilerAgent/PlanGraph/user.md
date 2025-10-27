# Task

{task}

## Available Tools

{tools}

---

Create an execution graph (DAG) for this task using the available tools.

Break the task into discrete tool operations, identify dependencies, and structure for parallel execution where possible.

Use the exact format:
```
NODE: <node_id>
TOOL: <tool_name>
ARGS: <JSON_dictionary>
DEPENDS_ON: <list_or_empty>

NODE: <node_id>
TOOL: <tool_name>
ARGS: <JSON_dictionary>
DEPENDS_ON: <list_or_empty>
```

Use #node_id to reference outputs from other nodes. Maximize parallelism by setting DEPENDS_ON: [] for independent operations. Ensure the graph is acyclic and covers the complete task.
