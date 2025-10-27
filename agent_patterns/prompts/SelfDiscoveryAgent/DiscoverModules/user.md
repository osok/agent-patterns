# Self-Discovery Agent - Discover Modules User Prompt

## Context

You are in the **Module Discovery** phase of the Self-Discovery process. Your task is to analyze the given problem and select the most appropriate reasoning modules from the available library. These modules will serve as the foundation for the subsequent adaptation, planning, and execution stages.

The reasoning modules represent different cognitive strategies and frameworks that can be applied to problem-solving. Your selection will determine which reasoning approaches are available for solving this task.

## Current Task

{task}

## Available Reasoning Modules

The following reasoning modules are available in the library:

{modules}

## Module Selection Constraints

- **Maximum modules allowed**: {max_modules}
- **Minimum modules required**: 1
- **Selection criteria**: Relevance, utility, and complementarity to the task

## Your Assignment

Carefully analyze the task above and select the most appropriate reasoning modules from the available library. Consider:

1. **What type of problem is this?** (analytical, creative, mathematical, strategic, etc.)
2. **What cognitive strategies would be most effective?** (decomposition, critical analysis, creative thinking, etc.)
3. **What are the key challenges in this task?** (complexity, ambiguity, multiple constraints, etc.)
4. **Which modules would work well together?** (complementary vs. redundant)
5. **What would an expert use to approach this problem?**

## Output Format Reminder

Respond ONLY with your module selections in this exact format:

```
SELECTED: module_name_1
SELECTED: module_name_2
SELECTED: module_name_3
```

**Important**:
- Use the EXACT module names from the library above
- One module per line
- No explanations, commentary, or additional text
- Stay within the maximum limit of {max_modules} modules
- Select at least 1 module

## Quality Checklist

Before finalizing your selection, verify:
- [ ] Each selected module directly addresses a task requirement
- [ ] No two modules are redundant or overlapping
- [ ] The combination covers the major reasoning needs of the task
- [ ] You're within the {max_modules} module limit
- [ ] Module names are spelled exactly as shown in the library
- [ ] Output format is correct (SELECTED: module_name)

Select the modules now.
