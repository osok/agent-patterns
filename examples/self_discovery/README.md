# Self-Discovery Agent Examples

The Self-Discovery agent is designed to solve complex reasoning problems by self-composing task-specific reasoning structures. This agent implements the SELF-DISCOVER pattern developed by researchers at the University of Southern California and Google Research.

## How Self-Discovery Works

The Self-Discovery agent operates in two main stages:

1. **Discovery Stage**: The agent first discovers a tailored reasoning structure for the specific task
   - **SELECT**: Choose relevant reasoning modules from a library of approaches
   - **ADAPT**: Adapt selected modules to make them task-specific
   - **IMPLEMENT**: Compose a structured reasoning plan

2. **Execution Stage**: The agent applies the discovered reasoning structure to solve the task

The key strength of this approach is that it can dynamically select and adapt different reasoning strategies based on the specific requirements of each problem, rather than using a fixed approach.

## Examples

### Basic Reasoning

The `basic_reasoning.py` example demonstrates how to use the Self-Discovery agent to solve complex reasoning tasks. It:

- Configures different LLM models for discovery and execution roles
- Defines a complex reasoning task
- Shows how the agent selects and adapts reasoning modules
- Displays the composed reasoning structure
- Shows the final solution to the problem

Run the example:

```bash
python examples/self_discovery/basic_reasoning.py
```

### Streaming Execution

The `basic_reasoning.py` file also includes a `streamed_execution()` function that demonstrates how to use the Self-Discovery agent with streaming output, allowing you to see the agent's progress in real-time as it:

- Selects reasoning modules
- Adapts them to the task
- Builds a reasoning structure
- Executes the structure step-by-step

To run the streaming example, uncomment the appropriate line at the bottom of the file:

```python
if __name__ == "__main__":
    # main()
    streamed_execution()  # Uncomment this line
```

## Requirements

To run these examples, you need:

1. OpenAI API key set in your environment variables or `.env` file
2. Required Python packages (install with `pip install -r requirements.txt`):
   - langchain
   - langchain-openai
   - python-dotenv

## Customization

You can customize the Self-Discovery agent by:

- Using different LLM models for the discovery and execution roles
- Creating a custom set of reasoning modules in a JSON file
- Modifying the prompt templates in `src/agent_patterns/prompts/SelfDiscoveryAgent/`

## References

- Original Paper: [SELF-DISCOVER: Large Language Models Self-Compose Reasoning Structures](https://arxiv.org/abs/2402.03620)
- Authors: Pei Zhou, Jay Pujara, Xiang Ren, Xinyun Chen, Heng-Tze Cheng, Quoc V. Le, Ed H. Chi, Denny Zhou, Swaroop Mishra, Huaixiu Steven Zheng 