"""
Example: Using custom_instructions to add domain-specific context to agent patterns.

This example demonstrates how to use the custom_instructions parameter to inject
domain-specific knowledge, constraints, or guidelines into any agent pattern
without modifying the original prompt templates.

NOTE: In v0.2.0, all system prompts are enterprise-grade (150-300+ lines) with
comprehensive sections including Role, Capabilities, Process, Examples, and more.
Your custom_instructions are appended to these comprehensive prompts, building on
a solid foundation that already includes error handling, quality standards, and
edge case management.
"""

from agent_patterns.patterns.self_discovery_agent import SelfDiscoveryAgent
from agent_patterns.patterns.storm_agent import STORMAgent


def example_medical_domain():
    """Example: Using custom instructions for medical domain expertise."""

    # Define medical domain instructions
    medical_instructions = """
    You are providing information in the MEDICAL domain. Follow these guidelines:

    1. ACCURACY: Always prioritize medical accuracy and cite evidence-based sources
    2. DISCLAIMERS: Include appropriate medical disclaimers where necessary
    3. TERMINOLOGY: Use proper medical terminology but explain complex terms
    4. ETHICS: Consider ethical implications and patient privacy
    5. LIMITATIONS: Acknowledge the limitations of AI in medical contexts
    6. RECOMMENDATION: Always recommend consulting healthcare professionals for medical decisions
    """

    # Create SelfDiscovery agent with medical instructions
    agent = SelfDiscoveryAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model_name": "gpt-4"},
            "execution": {"provider": "openai", "model_name": "gpt-4"}
        },
        custom_instructions=medical_instructions,
        max_selected_modules=3
    )

    # The custom instructions will be appended to ALL system prompts in the workflow
    result = agent.run("What are the key considerations for diagnosing Type 2 Diabetes?")

    print("Medical Domain Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_legal_domain():
    """Example: Using custom instructions for legal domain expertise."""

    # Define legal domain instructions
    legal_instructions = """
    You are providing information in the LEGAL domain. Follow these guidelines:

    1. JURISDICTION: Be clear about which jurisdiction's laws you're discussing
    2. DISCLAIMERS: Include appropriate legal disclaimers (not legal advice)
    3. CITATIONS: Reference specific laws, regulations, or case precedents when possible
    4. NEUTRALITY: Present balanced views when discussing legal interpretations
    5. UPDATES: Note that laws change and information may become outdated
    6. RECOMMENDATION: Always recommend consulting licensed attorneys for legal advice
    """

    # Create STORM agent with legal instructions
    def mock_search(query: str) -> str:
        return f"Legal information about: {query}"

    agent = STORMAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model_name": "gpt-4"},
            "documentation": {"provider": "openai", "model_name": "gpt-4"}
        },
        retrieval_tools={"search": mock_search},
        custom_instructions=legal_instructions
    )

    # The custom instructions guide the agent through all stages of STORM
    result = agent.run("Overview of intellectual property rights for software")

    print("Legal Domain Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_financial_compliance():
    """Example: Adding compliance and regulatory constraints."""

    # Define financial compliance instructions
    compliance_instructions = """
    You are operating under FINANCIAL REGULATORY COMPLIANCE requirements:

    1. DISCLOSURES: Include all required regulatory disclosures
    2. ACCURACY: Financial information must be verifiable and accurate
    3. RISKS: Always discuss relevant risks associated with financial decisions
    4. OBJECTIVITY: Avoid promotional or biased language
    5. ACCESSIBILITY: Explain financial concepts in clear, accessible language
    6. SUITABILITY: Consider the suitability of financial products for different investors
    7. DISCLAIMER: This is not financial advice - consult licensed financial advisors

    PROHIBITED:
    - Making specific investment recommendations
    - Guaranteeing returns or outcomes
    - Omitting material risks
    """

    agent = SelfDiscoveryAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model_name": "gpt-4"},
            "execution": {"provider": "openai", "model_name": "gpt-4"}
        },
        custom_instructions=compliance_instructions,
        max_selected_modules=4
    )

    result = agent.run("Explain the pros and cons of index funds versus actively managed funds")

    print("Financial Compliance Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_educational_context():
    """Example: Adding pedagogical guidelines for educational content."""

    # Define educational instructions
    educational_instructions = """
    You are creating EDUCATIONAL CONTENT. Follow these principles:

    1. SCAFFOLDING: Build concepts progressively from simple to complex
    2. EXAMPLES: Provide concrete examples for abstract concepts
    3. ENGAGEMENT: Use questions and prompts to encourage active learning
    4. CLARITY: Use clear, grade-appropriate language
    5. FEEDBACK: Explain not just "what" but "why" and "how"
    6. ERRORS: Treat misconceptions as learning opportunities
    7. ASSESSMENT: Include ways for learners to check their understanding

    TARGET AUDIENCE: High school students (ages 14-18)
    """

    agent = SelfDiscoveryAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model_name": "gpt-4"},
            "execution": {"provider": "openai", "model_name": "gpt-4"}
        },
        custom_instructions=educational_instructions
    )

    result = agent.run("Explain how photosynthesis works")

    print("Educational Context Result:")
    print(result)
    print("\n" + "="*80 + "\n")


def example_cultural_sensitivity():
    """Example: Adding cultural awareness and sensitivity guidelines."""

    # Define cultural sensitivity instructions
    cultural_instructions = """
    You are operating with CULTURAL SENSITIVITY AND AWARENESS:

    1. RESPECT: Show respect for diverse cultural perspectives and practices
    2. INCLUSIVITY: Use inclusive language that doesn't assume a specific cultural context
    3. AWARENESS: Be mindful of cultural differences in communication styles and values
    4. NEUTRALITY: Avoid imposing one culture's values as universal
    5. REPRESENTATION: Acknowledge and represent diverse viewpoints
    6. SENSITIVITY: Be aware of potentially sensitive cultural or historical topics
    7. LEARNING: Approach cultural differences with curiosity and openness

    CONTEXT: Creating content for a global, multicultural audience
    """

    def mock_search(query: str) -> str:
        return f"Cross-cultural information about: {query}"

    agent = STORMAgent(
        llm_configs={
            "thinking": {"provider": "openai", "model_name": "gpt-4"},
            "documentation": {"provider": "openai", "model_name": "gpt-4"}
        },
        retrieval_tools={"search": mock_search},
        custom_instructions=cultural_instructions
    )

    result = agent.run("Communication styles in business settings")

    print("Cultural Sensitivity Result:")
    print(result)
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("CUSTOM INSTRUCTIONS EXAMPLES")
    print("="*80 + "\n")

    print("Example 1: Medical Domain")
    print("-" * 80)
    example_medical_domain()

    print("Example 2: Legal Domain")
    print("-" * 80)
    example_legal_domain()

    print("Example 3: Financial Compliance")
    print("-" * 80)
    example_financial_compliance()

    print("Example 4: Educational Context")
    print("-" * 80)
    example_educational_context()

    print("Example 5: Cultural Sensitivity")
    print("-" * 80)
    example_cultural_sensitivity()

    print("\n" + "="*80)
    print("KEY TAKEAWAYS:")
    print("="*80)
    print("""
    1. custom_instructions are appended to ALL system prompts throughout the workflow
    2. They're ideal for adding domain expertise, constraints, or guidelines
    3. They work with ANY agent pattern without modifying prompt files
    4. Multiple concerns can be combined in a single custom_instructions string
    5. Instructions persist across all reasoning steps in multi-stage patterns
    """)
