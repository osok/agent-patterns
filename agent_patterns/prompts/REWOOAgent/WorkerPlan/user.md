# REWOO Agent - Worker Plan User Prompt

## Context

You are in the **Planning Phase** of the REWOO (Reason Without Observation) process. You must create an execution plan using tool calls with placeholders for results you haven't seen yet.

This is the unique aspect of REWOO: you design the entire information-gathering strategy WITHOUT seeing actual tool results. You work with placeholders like {{result_name}} instead.

## Task

{task}

## Available Tools

{tools}

## Your Assignment

Create an execution plan that:

1. **Uses placeholders** - Reference results as {{placeholder_name}}, not actual values
2. **Sequences logically** - Order tool calls with proper dependencies
3. **Is complete** - Gathers all information needed to answer the task
4. **Is efficient** - Uses minimal necessary tool calls
5. **Follows format** - Uses PLAN/SOLVER/TOOL/PARAMS structure exactly

## Key Principle: Reason Without Observation

**CRITICAL**: You will NOT see the actual results. You must plan with placeholders:
- Use descriptive names: {{ceo_name}}, {{stock_price}}, {{company_info}}
- Reference placeholders in later steps: `{{"query": "news about {{ceo_name}}"}}`
- Think like a compiler creating an execution blueprint

## Planning Process

### Step 1: Identify Information Needs
- What specific information is needed to answer the task?
- What tool calls can retrieve that information?
- What order makes logical sense?

### Step 2: Design Placeholders
- What descriptive placeholder names represent each result?
- How will later steps reference earlier placeholders?
- Are placeholders clear and meaningful?

### Step 3: Structure Tool Calls
- Order calls so dependencies are satisfied
- Use placeholders in PARAMS for forward references
- Minimize unnecessary calls

### Step 4: Write the Plan
- PLAN: Describe approach with placeholders
- For each tool call: SOLVER/TOOL/PARAMS
- Verify correct format and dependencies

## Output Format

Use this EXACT format:

```
PLAN: <Description using placeholders>

SOLVER: <placeholder_name>
TOOL: <tool_name>
PARAMS: <JSON_dict_of_parameters>

SOLVER: <next_placeholder_name>
TOOL: <tool_name>
PARAMS: <JSON_dict_possibly_referencing_earlier_placeholders>
```

**Requirements**:
- PLAN statement describes overall approach with placeholders
- Each tool call has SOLVER, TOOL, PARAMS (in that order)
- PARAMS must be valid JSON
- Use {{placeholder_name}} syntax for references
- No actual results, only placeholders

## Example

**Task**: "Find the founder of SpaceX and their net worth"

**Output**:
```
PLAN: Search for SpaceX founder -> {{founder_name}}. Then search for {{founder_name}} net worth -> {{net_worth}}.

SOLVER: founder_name
TOOL: search_tool
PARAMS: {{"query": "SpaceX founder who founded SpaceX"}}

SOLVER: net_worth
TOOL: search_tool
PARAMS: {{"query": "{{founder_name}} net worth current"}}
```

## Quality Checklist

Before finalizing, verify:
- [ ] Used PLAN/SOLVER/TOOL/PARAMS format exactly
- [ ] All tool results have placeholder names
- [ ] Placeholders are descriptive (not result1, result2)
- [ ] Later steps can reference earlier placeholders using {{name}}
- [ ] PARAMS are valid JSON dictionaries
- [ ] Tool calls are in logical order (dependencies satisfied)
- [ ] Plan would gather all information needed
- [ ] Used minimal necessary tool calls
- [ ] No actual values, only placeholders

Create the plan now.
