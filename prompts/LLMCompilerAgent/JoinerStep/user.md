## Original User Query
{input_query}

{memory_context}

## Task Results
{task_results}

## Synthesis Instructions
Please synthesize the results of all completed tasks into a coherent response that addresses the user's original query. The task results above contain all the information gathered from executing the plan.

In your response:
1. Integrate information from all the completed tasks
2. Provide a clear, direct answer to the user's original query
3. Organize the information in a logical structure
4. Include relevant details while remaining concise
5. Consider any relevant context from memory when forming your response

Additionally, determine if the results are sufficient to fully answer the user's query, or if more information is needed.

If more information is needed:
- Set needs_replanning=True
- Briefly explain what additional information would be helpful

If the current results are sufficient:
- Set needs_replanning=False
- Provide the complete answer 