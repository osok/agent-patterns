# Self-Discovery Agent - Plan Reasoning User Prompt

## Context

You are in the **Reasoning Plan** phase of the Self-Discovery process. You have been provided with adapted reasoning modules that are tailored to the current task. Your job is to organize these modules into a logical, step-by-step reasoning plan that will guide the execution phase.

The plan should create a coherent reasoning narrative that progresses from initial understanding through analysis to final solution.

## Current Task

{task}

## Adapted Reasoning Modules

You have the following adapted reasoning modules to work with:

{adapted_modules}

## Your Assignment

Create a step-by-step reasoning plan that:

1. **Incorporates all adapted modules** - Every module above must appear in your plan
2. **Follows logical sequence** - Earlier steps should set up later steps
3. **Respects dependencies** - Steps requiring prior information come after foundational steps
4. **Creates coherent flow** - The plan should tell a clear reasoning story
5. **Leads to solution** - The final steps should culminate in solving the task

## Planning Considerations

### Typical Reasoning Sequence

1. **Foundation** (Understanding, decomposition, clarification)
2. **Analysis** (Investigation, evaluation, examination)
3. **Synthesis** (Integration, decision-making, solution creation)
4. **Validation** (Verification, checking, confirmation)

### Key Questions

- Which reasoning steps must happen before others?
- What information needs to be established first?
- How do the modules build upon each other?
- What sequence would an expert follow?
- Does the plan address all aspects of the task?

## Output Format

Respond using this EXACT format:

```
STEP 1: [Description of what this step accomplishes and which module(s) it uses]
STEP 2: [Description of what this step accomplishes and which module(s) it uses]
STEP 3: [Description of what this step accomplishes and which module(s) it uses]
...
```

**Requirements**:
- Number steps sequentially (STEP 1, STEP 2, STEP 3, etc.)
- Each step should be 1-2 sentences describing both the action and purpose
- Explicitly mention which adapted module(s) each step applies
- Include all adapted modules in the plan
- Order steps logically based on dependencies and reasoning flow

## Quality Checklist

Before finalizing your plan, verify:
- [ ] All adapted modules are included in the plan
- [ ] Steps are in a logical, sensible sequence
- [ ] Dependencies are respected (prerequisites come first)
- [ ] Each step has a clear purpose and description
- [ ] The plan progresses from understanding through analysis to solution
- [ ] Following this plan would lead to solving the task
- [ ] Step numbers are sequential with no gaps
- [ ] Each step explicitly references which module(s) it uses

Create the reasoning plan now.
