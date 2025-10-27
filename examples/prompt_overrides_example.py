"""
Example: Using prompt_overrides to programmatically replace specific prompts.

This example demonstrates how to use the prompt_overrides parameter to completely
replace specific prompt templates in an agent workflow without modifying files.
This is useful for:
- A/B testing different prompts
- Dynamic prompt generation based on runtime conditions
- Experimenting with prompt engineering
- Creating specialized variants of patterns

IMPORTANT: In v0.2.0, default system prompts are enterprise-grade (150-300+ lines)
with comprehensive structure including Role, Capabilities, Process, Examples, etc.
When you override prompts, you're replacing these comprehensive prompts. For
production use, consider maintaining the comprehensive structure. See the
documentation for template examples that preserve quality standards.
"""

from agent_patterns.patterns.self_discovery_agent import SelfDiscoveryAgent
from agent_patterns.patterns.reflexion_agent import ReflexionAgent
from agent_patterns.patterns.reflection_agent import ReflectionAgent


def example_basic_override():
    """Example: Basic override of a single prompt."""

    # Override the DiscoverModules step with a custom prompt
    overrides = {
        "DiscoverModules": {
            "system": "You are an expert at selecting reasoning strategies. Be concise.",
            "user": """
Task: {task}

Available reasoning modules:
{modules}

Select the {max_modules} MOST relevant modules for this specific task.

Output format (one per line):
SELECTED: module_name
"""
        }
    }

    agent = SelfDiscoveryAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model": "gpt-4"},
            "execution": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=overrides,
        max_selected_modules=3
    )

    result = agent.run("Calculate the optimal route for visiting 5 cities")

    print("Basic Override Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_multiple_overrides():
    """Example: Override multiple prompts in a workflow."""

    # Override multiple steps in the SelfDiscovery workflow
    overrides = {
        "DiscoverModules": {
            "system": "You are a strategic reasoning expert. Select wisely.",
            "user": "Task: {task}\n\nModules:\n{modules}\n\nSelect {max_modules} best modules:\nSELECTED: module_name"
        },
        "AdaptModules": {
            "system": "You adapt generic reasoning strategies to specific problems.",
            "user": "Task: {task}\n\nModule: {module_name}\nDescription: {module_description}\n\nAdapt this to the task:"
        },
        "SynthesizeOutput": {
            "system": "You synthesize reasoning steps into a clear, final answer.",
            "user": "Task: {task}\n\nReasoning:\n{reasoning_steps}\n\nProvide the final answer:"
        }
    }

    agent = SelfDiscoveryAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model": "gpt-4"},
            "execution": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=overrides,
        max_selected_modules=2
    )

    result = agent.run("Design a data structure for a social network")

    print("Multiple Overrides Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_style_customization():
    """Example: Customize the style/tone of responses."""

    # Create a variant that produces more concise outputs
    concise_overrides = {
        "Generate": {
            "system": """You are a concise assistant. Follow these rules:
- Use bullet points instead of paragraphs
- Maximum 3 sentences per point
- No fluff or filler words
- Get straight to the point""",
            "user": "Task: {task}\n\nProvide a concise, bulleted response."
        },
        "Refine": {
            "system": """You are a ruthless editor. Make responses MORE concise:
- Cut unnecessary words
- Use shorter sentences
- Remove redundancy
- Keep only essential information""",
            "user": "Task: {task}\n\nCurrent response:\n{output}\n\nCritique:\n{reflection}\n\nMake it more concise:"
        }
    }

    agent = ReflectionAgent(
        llm_configs={
            "documentation": {"provider": "openai", "model": "gpt-4"},
            "reflection": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=concise_overrides,
        max_reflection_cycles=1
    )

    result = agent.run("Explain machine learning")

    print("Concise Style Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_socratic_method():
    """Example: Override to create a Socratic questioning variant."""

    # Create a variant that uses Socratic method
    socratic_overrides = {
        "Reflect": {
            "system": """You are a Socratic teacher who improves thinking through questions.
Instead of telling what's wrong, ask probing questions that guide toward better answers:
- What assumptions are being made?
- What evidence supports this?
- What alternative explanations exist?
- What are the implications?
- How would you test this?""",
            "user": """Original task: {task}

Current response:
{output}

Ask 3-5 Socratic questions that would improve this response:"""
        }
    }

    agent = ReflectionAgent(
        llm_configs={
            "documentation": {"provider": "openai", "model": "gpt-4"},
            "reflection": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=socratic_overrides,
        max_reflection_cycles=1
    )

    result = agent.run("Why is the sky blue?")

    print("Socratic Method Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_expert_level():
    """Example: Adjust complexity level for expert audience."""

    # Create an expert-level variant
    expert_overrides = {
        "Generate": {
            "system": """You are addressing PhD-level experts in the field.
- Use advanced technical terminology without explanation
- Reference current research and state-of-the-art methods
- Discuss nuances, edge cases, and open research questions
- Assume deep domain knowledge
- Focus on cutting-edge developments""",
            "user": "Task: {task}\n\nProvide an expert-level technical response."
        }
    }

    agent = ReflectionAgent(
        llm_configs={
            "documentation": {"provider": "openai", "model": "gpt-4"},
            "reflection": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=expert_overrides,
        max_reflection_cycles=1
    )

    result = agent.run("Explain transformer architecture in NLP")

    print("Expert Level Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_debugging_focus():
    """Example: Override for debugging/troubleshooting focus."""

    # Create a debugging-focused variant for Reflexion
    debugging_overrides = {
        "Reflect": {
            "system": """You are a debugging expert. Analyze failed attempts systematically:
1. What was the approach?
2. Where exactly did it fail?
3. What assumptions were incorrect?
4. What edge cases weren't considered?
5. What should be tried next?

Be specific and technical.""",
            "user": """Task: {task}

Attempt #{attempt_number}:
{previous_attempt}

Result: FAILED
Error/Issue: {failure_reason}

Analyze what went wrong and suggest corrections:"""
        }
    }

    agent = ReflexionAgent(
        llm_configs={
            "execution": {"provider": "openai", "model": "gpt-4"},
            "reflection": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=debugging_overrides,
        max_trials=3
    )

    result = agent.run("Write a function to find the longest palindromic substring")

    print("Debugging Focus Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_combining_with_custom_instructions():
    """Example: Combine prompt_overrides with custom_instructions."""

    # Override specific prompts
    overrides = {
        "Generate": {
            "system": "You create structured, well-organized responses.",
            "user": "Task: {task}\n\nCreate a structured response with clear sections."
        }
    }

    # Add domain-specific instructions
    instructions = """
DOMAIN: Software Architecture
AUDIENCE: Senior engineers
FORMAT: Include diagrams (described in text), code examples, and trade-offs
"""

    agent = ReflectionAgent(
        llm_configs={
            "documentation": {"provider": "openai", "model": "gpt-4"},
            "reflection": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=overrides,
        custom_instructions=instructions,
        max_reflection_cycles=1
    )

    result = agent.run("Design a microservices architecture for an e-commerce platform")

    print("Combined Approach Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_dynamic_overrides():
    """Example: Generate overrides dynamically based on task characteristics."""

    def create_overrides_for_task(task: str) -> dict:
        """Dynamically create overrides based on task."""

        # Detect if task is mathematical
        if any(word in task.lower() for word in ["calculate", "solve", "equation", "math"]):
            return {
                "ExecuteStep": {
                    "system": "You are a mathematical problem solver. Show all work step-by-step.",
                    "user": "Step: {step_description}\n\nSolve this step, showing all calculations:"
                }
            }

        # Detect if task is creative
        elif any(word in task.lower() for word in ["design", "create", "write", "story"]):
            return {
                "ExecuteStep": {
                    "system": "You are a creative thinker. Explore multiple possibilities.",
                    "user": "Step: {step_description}\n\nApproach this creatively with multiple ideas:"
                }
            }

        # Default analytical approach
        else:
            return {
                "ExecuteStep": {
                    "system": "You are an analytical problem solver. Use logic and evidence.",
                    "user": "Step: {step_description}\n\nAnalyze this systematically:"
                }
            }

    # Example 1: Mathematical task
    task1 = "Calculate the compound interest on $10,000 at 5% for 10 years"
    agent1 = SelfDiscoveryAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model": "gpt-4"},
            "execution": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=create_overrides_for_task(task1)
    )

    result1 = agent1.run(task1)
    print(f"Dynamic Override (Math) Result:\n{result1}\n")

    # Example 2: Creative task
    task2 = "Design a logo for a tech startup focused on sustainability"
    agent2 = SelfDiscoveryAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model": "gpt-4"},
            "execution": {"provider": "openai", "model": "gpt-4"}
        },
        prompt_overrides=create_overrides_for_task(task2)
    )

    result2 = agent2.run(task2)
    print(f"Dynamic Override (Creative) Result:\n{result2}\n")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("PROMPT OVERRIDES EXAMPLES")
    print("="*80 + "\n")

    print("Example 1: Basic Override")
    print("-" * 80)
    example_basic_override()

    print("Example 2: Multiple Overrides")
    print("-" * 80)
    example_multiple_overrides()

    print("Example 3: Style Customization")
    print("-" * 80)
    example_style_customization()

    print("Example 4: Socratic Method")
    print("-" * 80)
    example_socratic_method()

    print("Example 5: Expert Level")
    print("-" * 80)
    example_expert_level()

    print("Example 6: Debugging Focus")
    print("-" * 80)
    example_debugging_focus()

    print("Example 7: Combining with Custom Instructions")
    print("-" * 80)
    example_combining_with_custom_instructions()

    print("Example 8: Dynamic Overrides")
    print("-" * 80)
    example_dynamic_overrides()

    print("\n" + "="*80)
    print("KEY TAKEAWAYS:")
    print("="*80)
    print("""
    1. prompt_overrides give you complete control over specific prompts
    2. You can override system prompts, user prompts, or both
    3. Overrides are perfect for A/B testing and experimentation
    4. Multiple prompts can be overridden independently
    5. Combine with custom_instructions for maximum flexibility
    6. Overrides can be generated dynamically at runtime
    7. This enables creating specialized variants without file changes
    8. Priority: overrides > file system > custom instructions
    """)
