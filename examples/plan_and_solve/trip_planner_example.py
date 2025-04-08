"""Example demonstrating the PlanAndSolveAgent for trip planning."""

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
            "model_name": "gpt-4-turbo-preview",  # Using the same model for detailed itinerary
            "provider": "openai",
            "temperature": 0.5
        }
    }
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "src" / "agent_patterns" / "prompts")
    
    # Initialize the agent
    agent = PlanAndSolveAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        log_level=logging.INFO
    )
    
    # Example task for trip planning
    task = """
    Create a detailed 5-day itinerary for a trip to Tokyo, Japan. The travelers are a couple in their 30s 
    who are interested in food, culture, and technology. They have a moderate budget (about $200/day for 
    activities and meals, not including accommodation). They want a mix of popular tourist attractions and 
    off-the-beaten-path experiences. They prefer public transportation and walking.
    
    The itinerary should include:
    1. Day-by-day schedule with morning, afternoon, and evening activities
    2. Recommended restaurants for each day (breakfast, lunch, dinner)
    3. Estimated costs for activities and meals
    4. Transit information between locations
    5. One day trip outside of central Tokyo
    
    The travelers are arriving on a Monday morning and departing Saturday evening.
    """
    
    logger.info(f"Running Plan and Solve agent for trip planning")
    
    # Run the agent
    result = agent.run(task)
    
    # Display the result
    if "error" in result:
        logger.error(f"Agent execution failed: {result['error']}")
    else:
        logger.info("Trip planning completed successfully")
        print("\n" + "="*80 + "\n")
        print("TRIP PLANNING TASK:")
        print(task)
        print("\n" + "="*80 + "\n")
        print("ITINERARY RESULT:")
        print(result["output"])
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()