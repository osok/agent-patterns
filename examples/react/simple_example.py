"""Example demonstrating the ReActAgent."""

import os
import logging
from pathlib import Path

from langchain_core.tools import Tool
from agent_patterns.patterns.re_act_agent import ReActAgent

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Setup LLM configs
    # Make sure your environment variables are set (e.g., OPENAI_API_KEY)
    llm_configs = {
        "default": {
            "model_name": "gpt-4-turbo-preview",
            "provider": "openai",
            "temperature": 0.7
        }
    }
    
    # Define sample tools for the ReAct agent
    tools = [
        Tool(
            name="search",
            func=lambda query: f"Search results for: {query}",
            description="Search the web for information on a given topic."
        ),
        Tool(
            name="calculator",
            func=lambda expression: str(eval(expression)),
            description="Evaluate a mathematical expression."
        ),
        Tool(
            name="weather",
            func=lambda location: f"The weather in {location} is currently sunny and 75°F.",
            description="Get the current weather for a specified location."
        )
    ]
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "agent_patterns" / "prompts")
    
    # Initialize the agent
    agent = ReActAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir=prompt_dir,
        max_steps=5,
        log_level=logging.INFO
    )
    
    # Example task
    task = "What's the weather like in San Francisco? Also, what is 25 * 4?"
    
    logger.info(f"Running ReAct agent with task: {task}")
    
    # Run the agent
    result = agent.run(task)
    
    # Display the result
    if "error" in result:
        logger.error(f"Agent execution failed: {result['error']}")
    else:
        logger.info("Agent execution completed successfully")
        print("\n" + "="*80 + "\n")
        print("TASK:")
        print(task)
        print("\n" + "="*80 + "\n")
        print("RESULT:")
        print(result["output"])
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()