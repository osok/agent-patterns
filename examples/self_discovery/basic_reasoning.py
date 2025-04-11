"""
Basic reasoning example for the Self-Discovery Agent pattern with memory and tools.

This example demonstrates how to use the Self-Discovery Agent pattern to solve
complex reasoning problems by letting the LLM select and compose reasoning structures,
enhanced with memory and tool access.
"""

import logging
import os
import sys
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import json

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent_patterns.patterns.self_discovery_agent import SelfDiscoveryAgent
from agent_patterns.core.memory import (
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
    CompositeMemory
)
from agent_patterns.core.memory.persistence import (
    InMemoryPersistence
)
from agent_patterns.core.tools.base import ToolProvider

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class EducationalDesignToolProvider(ToolProvider):
    """Tool provider for educational design and research tasks."""
    
    def list_tools(self):
        """List available tools."""
        return [
            {
                "name": "research_topic",
                "description": "Research information about a specific topic",
                "parameters": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to research"
                    }
                }
            },
            {
                "name": "get_game_analytics",
                "description": "Get analytics about educational games for a particular age group",
                "parameters": {
                    "age_group": {
                        "type": "string",
                        "description": "The target age group (e.g., '8-12', 'teenagers', 'adults')"
                    },
                    "game_type": {
                        "type": "string",
                        "description": "The type of educational game"
                    }
                }
            },
            {
                "name": "evaluate_concept",
                "description": "Evaluate a game concept against educational criteria",
                "parameters": {
                    "concept": {
                        "type": "string",
                        "description": "The game concept to evaluate"
                    },
                    "criteria": {
                        "type": "string",
                        "description": "The evaluation criteria (e.g., 'engagement', 'education', 'retention')"
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name, params):
        """Execute the requested tool with the provided parameters."""
        if tool_name == "research_topic":
            topic = params.get("topic", "")
            return self._research_topic(topic)
        elif tool_name == "get_game_analytics":
            age_group = params.get("age_group", "")
            game_type = params.get("game_type", "")
            return self._get_game_analytics(age_group, game_type)
        elif tool_name == "evaluate_concept":
            concept = params.get("concept", "")
            criteria = params.get("criteria", "")
            return self._evaluate_concept(concept, criteria)
        else:
            return f"Unknown tool: {tool_name}"
    
    def _research_topic(self, topic: str) -> str:
        """Research a specific topic."""
        topic_data = {
            "environmental sustainability": """
Environmental Sustainability for Children (Ages 8-12):

Key Concepts for This Age Group:
- Basic ecology and ecosystems
- Conservation of natural resources
- Waste reduction and recycling
- Renewable energy concepts
- Biodiversity and habitat protection
- Water and air pollution
- Climate change basics
- Individual environmental responsibility

Learning Objectives Appropriate for Ages 8-12:
1. Recognize how everyday actions impact the environment
2. Understand basic natural resource cycles
3. Identify sustainable vs. unsustainable practices
4. Develop personal habits that reduce environmental harm
5. Connect environmental health to human well-being

Effective Teaching Methods for This Age Group:
- Hands-on experiential learning
- Storytelling and narrative-based learning
- Visual demonstrations of cause and effect
- Group activities and cooperative learning
- Role-playing and simulation
- Gamification of concepts
- Connection to personal interests and local environments
            """,
            "game mechanics": """
Educational Game Mechanics Research:

Most Effective Mechanics for Learning:
1. Progression systems with meaningful learning stages
2. Immediate feedback loops
3. Scaffolded challenges that increase in difficulty
4. Choice and agency in problem-solving
5. Social interaction and collaborative play
6. Collection and discovery mechanics
7. Resource management tied to learning concepts
8. Narrative integration of educational content
9. Achievement systems aligned with learning objectives
10. Personalized difficulty adaptation

Mechanics to Avoid:
- Excessive extrinsic rewards that overshadow learning
- Overly competitive structures that frustrate struggling players
- Random chance mechanics not connected to knowledge
- Time pressure that causes anxiety rather than engagement
- Excessive grinding without new learning opportunities
            """,
            "educational measurement": """
Measuring Educational Game Effectiveness:

Key Performance Indicators:
1. Knowledge acquisition (pre/post testing)
2. Concept retention over time
3. Skill transfer to non-game contexts
4. Engagement metrics (time played, return rate)
5. Self-efficacy and confidence increase
6. Behavioral change indicators
7. Problem-solving improvement
8. Collaboration quality (for multiplayer games)

Measurement Methods:
- Embedded assessments within gameplay
- Stealth assessment through gameplay analytics
- Traditional pre/post knowledge testing
- Observational studies of gameplay
- Self-reporting of learning and engagement
- Longitudinal tracking of behavior change
- Parent/teacher feedback on observed learning
            """
        }
        
        # Return the most relevant information or a general response
        for key, value in topic_data.items():
            if key in topic.lower():
                return value
        
        return f"Research results for '{topic}' show that effective educational approaches should be age-appropriate, engaging, and connect to children's existing knowledge and interests."
    
    def _get_game_analytics(self, age_group: str, game_type: str) -> str:
        """Get analytics about educational games."""
        if "8-12" in age_group or "children" in age_group.lower():
            if "environment" in game_type.lower() or "sustainability" in game_type.lower():
                return """
Analytics for Environmental Education Games (Ages 8-12):

Engagement Metrics:
- Average session length: 24 minutes
- Return rate: 68% play multiple times per week
- Completion rate: 72% for narrative-driven games
- Social sharing: 34% play with friends or family

Learning Effectiveness:
- Knowledge gain: Average 27% improvement in pre/post tests
- Retention: 64% recall key concepts after 30 days
- Behavior change: 41% report trying new environmental actions

Most Engaging Features (Ranked):
1. Character customization with environmental themes
2. Real-world impact connections (e.g., "you saved X trees")
3. Progressive challenges with visible environmental changes
4. Collection mechanics tied to environmental species/objects
5. Social comparison of positive environmental impact

Common Drop-off Points:
- Complex scientific vocabulary without scaffolding
- Repetitive tasks without new learning
- Lack of meaningful choices with environmental consequences
- Unclear connection between actions and outcomes
                """
            else:
                return """
General Educational Game Analytics (Ages 8-12):

Engagement Patterns:
- Attention span: Average 18-30 minutes per session
- Preferred platforms: 58% tablet, 23% computer, 19% smartphone
- Peak usage times: After school (3-6pm) and weekends
- Parental involvement: 47% have parent present while playing

Effective Design Elements:
- Character customization increases play time by 42%
- Achievement systems increase completion rates by 36%
- Narrative elements improve concept retention by 28%
- Collaborative features enhance social learning by 33%

Key Success Factors:
- Clear learning goals embedded in gameplay
- Difficulty that adapts to player performance
- Immediate feedback on player actions
- Connection to school curriculum (increases adoption)
- Multi-sensory engagement (visual, audio, interactive)
                """
        else:
            return f"Analytics for {game_type} games targeting {age_group} show that effective educational games balance entertainment with learning objectives, provide immediate feedback, and include age-appropriate challenges."
    
    def _evaluate_concept(self, concept: str, criteria: str) -> str:
        """Evaluate a game concept against educational criteria."""
        if "engagement" in criteria.lower():
            return f"""
Engagement Evaluation:

Strengths:
- The concept incorporates player choice and agency
- The progression system provides clear goals
- Visual elements appear appealing to the target age range
- Mechanics allow for different play styles

Areas for Improvement:
- Consider adding more social/collaborative features
- The feedback systems could be more immediate and rewarding
- Look for opportunities to incorporate more novelty and surprise
- Ensure the difficulty curve is properly tuned for the age group

Recommendation:
Enhance engagement by adding more moment-to-moment feedback, ensuring challenge levels match player skills, and creating more opportunities for meaningful choices with visible consequences.
            """
        elif "education" in criteria.lower():
            return f"""
Educational Value Evaluation:

Strengths:
- Clear learning objectives aligned with age-appropriate standards
- Integration of educational content with gameplay mechanics
- Multiple representations of key concepts (visual, textual, interactive)
- Opportunities for application of knowledge

Areas for Improvement:
- Consider more scaffolding for complex concepts
- Add more reflection opportunities to solidify learning
- Ensure adaptability for different learning styles
- Create stronger connections between in-game actions and real-world applications

Recommendation:
Strengthen the educational value by implementing formative assessment within gameplay, adding reflection prompts at key learning moments, and creating clearer connections between game activities and real-world environmental actions.
            """
        else:
            return f"""
General Evaluation of Concept:

The concept demonstrates promise in several areas but could benefit from refinement. The core mechanics align well with the learning objectives, though the integration of gameplay and educational content could be more seamless. 

Consider how each game element directly supports your learning goals while maintaining an engaging experience. Ensure that players can clearly understand how their in-game actions relate to the environmental concepts you're teaching.

I recommend prototyping the core loop with your target audience to validate engagement before proceeding with full development.
            """

def setup_memory():
    """Set up a composite memory system."""
    # Create persistence backend
    persistence = InMemoryPersistence()
    asyncio.run(persistence.initialize())
    
    # Create individual memory types
    semantic_memory = SemanticMemory(persistence, namespace="education_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="education_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="education_procedural")
    
    # Create composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Pre-populate with some semantic memories
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "learning_principles", "attribute": "effective_methods", "value": ["active learning", "spaced repetition", "immediate feedback", "contextualized content"]}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "target_audience", "attribute": "children_8_12", "value": {"attention_span": "15-30 minutes", "cognitive_development": "concrete operational stage", "interests": ["adventure", "collection", "social interaction"]}}
    ))
    
    # Add a procedural memory for educational design
    asyncio.run(memory.save_to(
        "procedural",
        {
            "name": "educational_design_process",
            "pattern": {
                "template": """When designing educational experiences:
1. Start with clear learning objectives
2. Consider the target audience's cognitive development stage
3. Design engaging interactions that reinforce key concepts
4. Include appropriate challenge and support mechanisms
5. Incorporate opportunities for practice and feedback
6. Develop assessment methods aligned with objectives"""
            },
            "description": "Template for effective educational design process",
            "tags": ["education", "design", "learning"]
        }
    ))
    
    return memory


def main():
    """Run the Self-Discovery Agent example with memory and tools."""
    # Configure the LLMs for discovery and execution
    llm_configs = {
        "discovery": {
            "provider": "openai",
            "model_name": "gpt-4o",  # Using GPT-4o for discovery
            "temperature": 0.2,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        "execution": {
            "provider": "openai",
            "model_name": "gpt-4o",  # Using GPT-4o for execution
            "temperature": 0.3,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
    }

    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "src" / "agent_patterns" / "prompts")
    
    # Set up memory
    memory = setup_memory()
    
    # Set up tool provider
    tool_provider = EducationalDesignToolProvider()

    # Create the Self-Discovery Agent with memory and tools
    agent = SelfDiscoveryAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        },
        tool_provider=tool_provider,
        log_level=logging.INFO,
    )

    # Define a complex reasoning task
    task = """
    You're designing a new educational game for children aged 8-12 to teach them 
    about environmental sustainability. The game needs to be engaging, educational, 
    and promote positive environmental behaviors. Design the core game mechanics, 
    educational content, and how you'll measure its effectiveness.
    """

    # Alternatively, try a logical reasoning problem
    # task = """
    # There are five houses in a row, each with a different color. The people living
    # in these houses are of different nationalities, have different pets, drink
    # different beverages, and play different sports. Given the following clues:
    # 1. The Norwegian lives in the first house.
    # 2. The person who plays tennis lives in the blue house.
    # 3. The Spaniard owns a dog.
    # 4. Coffee is drunk in the green house.
    # 5. The Ukrainian drinks tea.
    # 6. The green house is immediately to the right of the ivory house.
    # 7. The person who plays cricket owns snails.
    # 8. The person who plays hockey lives in the yellow house.
    # 9. Milk is drunk in the middle house.
    # 10. The American lives in the first house on the right.
    # 11. The person who plays basketball lives in the house next to the house with a fox.
    # 12. The person who plays hockey lives in the house next to the house where the horse is kept.
    # 13. The person who plays golf drinks orange juice.
    # 14. The Japanese plays baseball.
    # 15. The Norwegian lives next to the blue house.
    # Determine who plays basketball.
    # """

    logger.info("Running Self-Discovery Agent with task: %s", task[:100] + "...")

    # Run the agent
    result = agent.run(task)

    # Check for errors
    if "error" in result:
        logger.error("Agent execution failed: %s", result["error"])
        return

    # Print the final answer
    print("\n\n=== FINAL ANSWER ===\n")
    print(result["output"])

    # Print the discovered reasoning structure
    print("\n\n=== DISCOVERED REASONING STRUCTURE ===\n")
    print(json.dumps(result["reasoning_structure"], indent=2))
    
    # Show what was stored in memory
    print("\n\n=== MEMORY AFTER EXECUTION ===\n")
    
    print("\nSemantic memories:")
    facts = asyncio.run(memory.retrieve_from("semantic", "", limit=5))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = asyncio.run(memory.retrieve_from("episodic", "educational game", limit=5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")


def example_with_fake_streaming():
    """Simulate a streaming example by running each step with visual separation."""
    # Configure the LLMs for discovery and execution
    llm_configs = {
        "discovery": {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.2,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        "execution": {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.3,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
    }
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "src" / "agent_patterns" / "prompts")
    
    # Set up memory
    memory = setup_memory()
    
    # Set up tool provider
    tool_provider = EducationalDesignToolProvider()

    # Create the Self-Discovery Agent with memory and tools
    agent = SelfDiscoveryAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        },
        tool_provider=tool_provider,
        log_level=logging.INFO,
    )

    # Define a complex reasoning task
    task = """
    Design a sustainable urban transportation system for a city of 500,000 people
    that reduces carbon emissions by at least 30% within 5 years while improving
    mobility for all residents, including those with disabilities and low incomes.
    """

    print("\n\n=== TASK ===\n")
    print(task.strip())
    
    print("\n\n=== STAGE: SELECT MODULES ===\n")
    # Manually call the first step
    initial_state = {
        "input": task,
        "chat_history": [],
        "reasoning_modules": agent.reasoning_modules,
        "selected_modules": None,
        "adapted_modules": None,
        "reasoning_structure": None,
        "execution_result": None,
        "final_answer": None
    }
    selection_state = agent._select_reasoning_modules(initial_state)
    print("\nSelected Reasoning Modules:")
    for module in selection_state["selected_modules"]:
        print(f"- {module}")
    
    # Small delay for readability
    time.sleep(1)
    
    print("\n\n=== STAGE: ADAPT MODULES ===\n")
    adaptation_state = agent._adapt_reasoning_modules({**initial_state, **selection_state})
    print("\nAdapted Reasoning Modules:")
    print(adaptation_state["adapted_modules"][0])
    
    # Small delay for readability
    time.sleep(1)
    
    print("\n\n=== STAGE: IMPLEMENT STRUCTURE ===\n")
    implementation_state = agent._implement_reasoning_structure({**initial_state, **selection_state, **adaptation_state})
    print("\nReasoning Structure:")
    print(json.dumps(implementation_state["reasoning_structure"], indent=2))
    
    # Small delay for readability
    time.sleep(1)
    
    print("\n\n=== STAGE: EXECUTE STRUCTURE ===\n")
    execution_state = agent._execute_reasoning_structure({**initial_state, **selection_state, **adaptation_state, **implementation_state})
    print("\nExecution Result (first 500 chars):")
    result = execution_state["execution_result"]
    print(result[:500] + "..." if len(result) > 500 else result)
    
    # Small delay for readability
    time.sleep(1)
    
    print("\n\n=== STAGE: FORMAT FINAL ANSWER ===\n")
    final_state = agent._format_final_answer({**initial_state, **selection_state, **adaptation_state, **implementation_state, **execution_state})
    print("\nFinal Answer (first 200 chars):")
    answer = final_state["final_answer"]
    print(answer[:200] + "..." if len(answer) > 200 else answer)
    
    print("\n\n=== COMPLETE FINAL ANSWER ===\n")
    print(answer)
    
    # Show what was stored in memory
    print("\n\n=== MEMORY AFTER EXECUTION ===\n")
    
    print("\nSemantic memories:")
    facts = asyncio.run(memory.retrieve_from("semantic", "", limit=5))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = asyncio.run(memory.retrieve_from("episodic", "transportation", limit=5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")


if __name__ == "__main__":
    # Run the main example
    main()
    
    # Run the "streaming" example
    # example_with_fake_streaming() 