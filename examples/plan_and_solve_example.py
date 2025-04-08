"""Example demonstrating the PlanAndSolveAgent."""

import os
import logging
from pathlib import Path

from agent_patterns.patterns.plan_and_solve_agent import PlanAndSolveAgent

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Setup LLM configs
    # Make sure your environment variables are set (e.g., OPENAI_API_KEY)
    llm_configs = {
        "planner": {
            "model_name": "gpt-4-turbo-preview",  # More powerful model for planning
            "provider": "openai",
            "temperature": 0.7
        },
        "executor": {
            "model_name": "gpt-3.5-turbo",  # Less expensive model for execution
            "provider": "openai",
            "temperature": 0.5
        }
    }
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent
    prompt_dir = str(project_root / "src" / "agent_patterns" / "prompts")
    
    # Initialize the agent
    agent = PlanAndSolveAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        log_level=logging.INFO
    )
    
    # Example task
    task = "Create a comprehensive study plan for learning Python programming from scratch to advanced level in 3 months."
    
    logger.info(f"Running Plan and Solve agent with task: {task}")
    
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