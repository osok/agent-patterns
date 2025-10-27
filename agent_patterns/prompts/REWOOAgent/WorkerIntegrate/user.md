# REWOO Agent - Worker Integration User Prompt

## Context

You are in the **Integration Phase** of the REWOO (Reason Without Observation) process. Earlier, you created a plan with placeholders. Now the Solver has executed all tools, and you have the actual results.

This is where raw tool outputs become a polished answer. Your job is to synthesize the results into a comprehensive response to the original task.

## Original Task

{task}

## Your Plan (with placeholders)

{plan}

## Actual Results from Solver

{results}

## Your Assignment

Integrate the tool results into a comprehensive final answer that:

1. **Answers the task completely** - Addresses all aspects of what was asked
2. **Integrates all results** - Weaves tool outputs into coherent response
3. **Is accurate** - Faithfully represents the information obtained
4. **Is cohesive** - Reads as unified answer, not tool output list
5. **Is clear** - Well-organized and easy to understand
6. **Is polished** - Professional, final-quality output

## Integration Guidelines

### Synthesize, Don't List
- DON'T: "Tool 1 returned X. Tool 2 returned Y."
- DO: Weave information into natural, flowing answer

### Use Actual Results
- Ground answer in the tool outputs provided
- Don't invent information not in results
- Work with what's available

### Address the Task
- Fully answer what was originally asked
- Cover all parts of the question
- Provide complete response

### Add Context
- Help user understand the information
- Provide appropriate framing
- Make answer accessible

## Quality Checklist

Before finalizing, verify:
- [ ] I fully answered the original task
- [ ] I incorporated information from all relevant results
- [ ] Answer is accurate to the tool outputs
- [ ] I synthesized (not just listed) results
- [ ] Answer is coherent and flows naturally
- [ ] Response is well-organized and clear
- [ ] Output is polished and professional
- [ ] Answer is complete (no gaps)
- [ ] I didn't add information not in results

Create the final answer now.
