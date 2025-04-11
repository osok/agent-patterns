# Building a Customer Support Bot

This tutorial guides you through building a customer support bot that can handle inquiries, access knowledge bases, and manage support tickets.

## Overview

Customer support bots need to:

1. Understand customer queries in natural language
2. Access knowledge bases to retrieve relevant information
3. Handle multi-turn conversations while maintaining context
4. Create and update support tickets
5. Escalate complex issues to human agents

For this use case, we'll use the ReAct agent pattern, which excels at reasoning and tool use, with memory integration for conversation history.

## Prerequisites

- Agent Patterns library installed
- OpenAI API key (or other supported LLM provider)
- Basic Python knowledge

## Step 1: Setting Up the Project

Create a new Python file called `customer_support_bot.py`:

```python
import os
import asyncio
from dotenv import load_dotenv
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.memory import EpisodicMemory, SemanticMemory, CompositeMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence
from agent_patterns.core.tools.base import BaseToolProvider, Tool

# Load environment variables
load_dotenv()
```

## Step 2: Creating Custom Tools

We'll create custom tools for knowledge base access and ticket management:

```python
class CustomerSupportToolProvider(BaseToolProvider):
    """Tool provider for customer support operations."""
    
    def __init__(self):
        super().__init__()
        # Simulated knowledge base
        self.knowledge_base = {
            "product_features": {
                "basic": ["Feature A", "Feature B", "Feature C"],
                "premium": ["Feature A", "Feature B", "Feature C", "Feature D", "Feature E"],
                "enterprise": ["Feature A", "Feature B", "Feature C", "Feature D", "Feature E", "Feature F", "Feature G"]
            },
            "pricing": {
                "basic": "$10/month",
                "premium": "$25/month",
                "enterprise": "Custom pricing"
            },
            "common_issues": {
                "login_problem": "Try clearing your browser cache and cookies, then restart your browser.",
                "payment_failed": "Verify your payment information is up-to-date and try again.",
                "feature_not_working": "Ensure you're on the latest version. If the issue persists, try restarting the application."
            }
        }
        
        # Simulated ticket system
        self.tickets = {}
        self.next_ticket_id = 1000
    
    def get_tools(self):
        """Return available tools."""
        return [
            Tool(
                name="search_knowledge_base",
                description="Search the knowledge base for information",
                function=self.search_knowledge_base,
                parameters={
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                }
            ),
            Tool(
                name="get_product_features",
                description="Get features for a specific product tier",
                function=self.get_product_features,
                parameters={
                    "tier": {
                        "type": "string",
                        "description": "Product tier (basic, premium, or enterprise)"
                    }
                }
            ),
            Tool(
                name="get_pricing",
                description="Get pricing information for a specific tier",
                function=self.get_pricing,
                parameters={
                    "tier": {
                        "type": "string",
                        "description": "Product tier (basic, premium, or enterprise)"
                    }
                }
            ),
            Tool(
                name="create_ticket",
                description="Create a support ticket",
                function=self.create_ticket,
                parameters={
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Ticket subject"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Ticket priority (low, medium, high)",
                        "enum": ["low", "medium", "high"]
                    }
                }
            ),
            Tool(
                name="get_ticket",
                description="Get details of a support ticket",
                function=self.get_ticket,
                parameters={
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID"
                    }
                }
            ),
            Tool(
                name="update_ticket",
                description="Update a support ticket",
                function=self.update_ticket,
                parameters={
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID"
                    },
                    "status": {
                        "type": "string",
                        "description": "New ticket status",
                        "enum": ["open", "in_progress", "pending", "resolved", "closed"]
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes to add to the ticket"
                    }
                }
            ),
            Tool(
                name="escalate_to_human",
                description="Escalate the conversation to a human agent",
                function=self.escalate_to_human,
                parameters={
                    "reason": {
                        "type": "string",
                        "description": "Reason for escalation"
                    },
                    "urgency": {
                        "type": "string",
                        "description": "Urgency level",
                        "enum": ["low", "medium", "high"]
                    }
                }
            )
        ]
    
    async def search_knowledge_base(self, query):
        """Search the knowledge base for information."""
        # Simple keyword-based search in our simulated knowledge base
        query = query.lower()
        results = []
        
        # Search in product features
        for tier, features in self.knowledge_base["product_features"].items():
            for feature in features:
                if query in feature.lower():
                    results.append({
                        "category": "product_features",
                        "tier": tier,
                        "content": feature
                    })
        
        # Search in pricing
        for tier, price in self.knowledge_base["pricing"].items():
            if query in tier.lower() or query in price.lower():
                results.append({
                    "category": "pricing",
                    "tier": tier,
                    "content": price
                })
        
        # Search in common issues
        for issue, solution in self.knowledge_base["common_issues"].items():
            if query in issue.lower() or query in solution.lower():
                results.append({
                    "category": "common_issues",
                    "issue": issue,
                    "content": solution
                })
        
        return {
            "query": query,
            "results": results,
            "result_count": len(results)
        }
    
    async def get_product_features(self, tier):
        """Get features for a specific product tier."""
        tier = tier.lower()
        if tier in self.knowledge_base["product_features"]:
            features = self.knowledge_base["product_features"][tier]
            return {
                "tier": tier,
                "features": features,
                "feature_count": len(features)
            }
        else:
            return {
                "error": f"Tier '{tier}' not found",
                "available_tiers": list(self.knowledge_base["product_features"].keys())
            }
    
    async def get_pricing(self, tier):
        """Get pricing information for a specific tier."""
        tier = tier.lower()
        if tier in self.knowledge_base["pricing"]:
            price = self.knowledge_base["pricing"][tier]
            return {
                "tier": tier,
                "price": price
            }
        else:
            return {
                "error": f"Tier '{tier}' not found",
                "available_tiers": list(self.knowledge_base["pricing"].keys())
            }
    
    async def create_ticket(self, customer_id, subject, description, priority="medium"):
        """Create a support ticket."""
        ticket_id = str(self.next_ticket_id)
        self.next_ticket_id += 1
        
        # Create timestamp
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        
        # Create ticket
        ticket = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "subject": subject,
            "description": description,
            "priority": priority,
            "status": "open",
            "created_at": timestamp,
            "updated_at": timestamp,
            "notes": []
        }
        
        # Save ticket
        self.tickets[ticket_id] = ticket
        
        return {
            "ticket_id": ticket_id,
            "status": "created",
            "message": f"Ticket {ticket_id} created successfully"
        }
    
    async def get_ticket(self, ticket_id):
        """Get details of a support ticket."""
        if ticket_id in self.tickets:
            return self.tickets[ticket_id]
        else:
            return {
                "error": f"Ticket {ticket_id} not found"
            }
    
    async def update_ticket(self, ticket_id, status=None, notes=None):
        """Update a support ticket."""
        if ticket_id not in self.tickets:
            return {
                "error": f"Ticket {ticket_id} not found"
            }
        
        ticket = self.tickets[ticket_id]
        
        # Update timestamp
        import datetime
        ticket["updated_at"] = datetime.datetime.now().isoformat()
        
        # Update status if provided
        if status:
            ticket["status"] = status
        
        # Add notes if provided
        if notes:
            ticket["notes"].append({
                "content": notes,
                "timestamp": ticket["updated_at"]
            })
        
        return {
            "ticket_id": ticket_id,
            "status": ticket["status"],
            "message": f"Ticket {ticket_id} updated successfully"
        }
    
    async def escalate_to_human(self, reason, urgency="medium"):
        """Escalate the conversation to a human agent."""
        # In a real implementation, this would integrate with a queue system
        return {
            "status": "escalated",
            "reason": reason,
            "urgency": urgency,
            "message": "This conversation has been escalated to a human agent who will respond shortly."
        }
```

## Step 3: Setting Up Memory

Our support bot needs memory to maintain conversation context:

```python
# Set up memory persistence
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# Create memory components
episodic_memory = EpisodicMemory(
    persistence, 
    namespace="conversations"
)

semantic_memory = SemanticMemory(
    persistence,
    namespace="customer_info"
)

# Create composite memory
memory = CompositeMemory({
    "episodic": episodic_memory,
    "semantic": semantic_memory
})
```

## Step 4: Creating the Support Bot Agent

Now let's create our ReAct-based support bot:

```python
# Configure LLM settings
llm_configs = {
    "default": {
        "provider": os.getenv("DEFAULT_MODEL_PROVIDER", "openai"),
        "model_name": os.getenv("DEFAULT_MODEL_NAME", "gpt-4o")
    }
}

# Create tool provider
support_tool_provider = CustomerSupportToolProvider()

# Create support bot agent
support_agent = ReActAgent(
    llm_configs=llm_configs,
    memory=memory,
    memory_config={
        "episodic": True,
        "semantic": True
    },
    tool_provider=support_tool_provider
)
```

## Step 5: Creating a Customer Support Interface

Let's wrap our agent with a class that provides a user-friendly interface:

```python
class CustomerSupportBot:
    def __init__(self):
        self.agent = support_agent
        self.current_customer_id = None
        self.active_conversation = False
        self.conversation_history = []
    
    def start_conversation(self, customer_id):
        """Start a new conversation with a customer."""
        self.current_customer_id = customer_id
        self.active_conversation = True
        self.conversation_history = []
        
        # Store customer information if available (simulated)
        customer_info = self.get_customer_info(customer_id)
        
        # Save customer info to memory
        if customer_info:
            for attribute, value in customer_info.items():
                asyncio.run(semantic_memory.save({
                    "entity": f"customer:{customer_id}",
                    "attribute": attribute,
                    "value": value
                }))
        
        # Prepare greeting
        greeting = "Hello! I'm your AI support assistant. How can I help you today?"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })
        
        return greeting
    
    def get_customer_info(self, customer_id):
        """Simulate retrieving customer info from a database."""
        # In a real implementation, this would query a customer database
        # For this example, we'll return mock data
        customer_db = {
            "C12345": {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "plan": "premium",
                "signup_date": "2023-01-15"
            },
            "C67890": {
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "plan": "basic",
                "signup_date": "2023-06-22"
            },
            "C24680": {
                "name": "Robert Johnson",
                "email": "robert.johnson@example.com",
                "plan": "enterprise",
                "signup_date": "2022-11-05"
            }
        }
        
        return customer_db.get(customer_id, {})
    
    def process_message(self, message):
        """Process a customer message and generate a response."""
        if not self.active_conversation:
            return "No active conversation. Please start a conversation first."
        
        # Add customer message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Save to episodic memory
        asyncio.run(episodic_memory.save({
            "customer_id": self.current_customer_id,
            "role": "user",
            "content": message,
            "timestamp": self._get_timestamp()
        }))
        
        # Check for conversation ending
        if message.lower() in ["bye", "goodbye", "end", "quit", "exit"]:
            self.active_conversation = False
            response = "Thank you for contacting our support. Is there anything else I can help you with before you go?"
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Save to episodic memory
            asyncio.run(episodic_memory.save({
                "customer_id": self.current_customer_id,
                "role": "assistant",
                "content": response,
                "timestamp": self._get_timestamp()
            }))
            
            return response
        
        # Create context for agent
        customer_info = self.get_customer_info(self.current_customer_id)
        context = f"Customer ID: {self.current_customer_id}\n"
        if customer_info:
            context += f"Name: {customer_info.get('name', 'Unknown')}\n"
            context += f"Plan: {customer_info.get('plan', 'Unknown')}\n"
        
        # Run agent with message and context
        prompt = f"""
        {context}
        
        You are a helpful customer support bot. The customer has sent the following message:
        
        {message}
        
        Please help the customer by providing information or using the appropriate tools.
        If you need to create a ticket, use the customer's ID: {self.current_customer_id}
        If you can't help with something, offer to escalate to a human agent.
        """
        
        response = self.agent.run(prompt)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Save to episodic memory
        asyncio.run(episodic_memory.save({
            "customer_id": self.current_customer_id,
            "role": "assistant",
            "content": response,
            "timestamp": self._get_timestamp()
        }))
        
        return response
    
    def end_conversation(self):
        """End the current conversation."""
        if not self.active_conversation:
            return "No active conversation to end."
        
        self.active_conversation = False
        return "Conversation ended. Thank you for contacting our support."
    
    def get_conversation_history(self):
        """Get the current conversation history."""
        return self.conversation_history
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.now().isoformat()
```

## Step 6: Creating a Simple Command Line Interface

Let's create a simple interface to test our support bot:

```python
def main():
    # Create the support bot
    bot = CustomerSupportBot()
    
    # Get customer ID
    customer_id = input("Enter customer ID (e.g., C12345): ")
    if not customer_id:
        customer_id = "C12345"  # Default for testing
    
    # Start conversation
    greeting = bot.start_conversation(customer_id)
    print(f"Bot: {greeting}")
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for exit command
        if user_input.lower() in ["quit", "exit"]:
            bot.end_conversation()
            print("Bot: Goodbye!")
            break
        
        # Process message
        response = bot.process_message(user_input)
        print(f"Bot: {response}")
        
        # Check if conversation ended
        if not bot.active_conversation:
            break

if __name__ == "__main__":
    main()
```

## Step 7: Adding Analytics and Performance Tracking

Let's add basic analytics to track bot performance:

```python
class SupportBotAnalytics:
    def __init__(self):
        self.conversations = {}
        self.ticket_stats = {
            "created": 0,
            "resolved": 0
        }
        self.tool_usage = {}
        self.response_times = []
    
    def log_conversation(self, customer_id, conversation):
        """Log a completed conversation."""
        if customer_id not in self.conversations:
            self.conversations[customer_id] = []
        
        self.conversations[customer_id].append(conversation)
    
    def log_ticket_creation(self):
        """Log a ticket creation event."""
        self.ticket_stats["created"] += 1
    
    def log_ticket_resolution(self):
        """Log a ticket resolution event."""
        self.ticket_stats["resolved"] += 1
    
    def log_tool_usage(self, tool_name):
        """Log a tool usage event."""
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        
        self.tool_usage[tool_name] += 1
    
    def log_response_time(self, seconds):
        """Log response time in seconds."""
        self.response_times.append(seconds)
    
    def get_average_response_time(self):
        """Get the average response time."""
        if not self.response_times:
            return 0
        
        return sum(self.response_times) / len(self.response_times)
    
    def get_most_used_tools(self, limit=5):
        """Get the most frequently used tools."""
        sorted_tools = sorted(
            self.tool_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_tools[:limit]
    
    def get_conversation_count(self):
        """Get the total number of conversations."""
        return sum(len(convs) for convs in self.conversations.values())
    
    def get_customer_count(self):
        """Get the number of unique customers."""
        return len(self.conversations)
    
    def generate_report(self):
        """Generate an analytics report."""
        report = {
            "conversation_count": self.get_conversation_count(),
            "customer_count": self.get_customer_count(),
            "ticket_stats": self.ticket_stats,
            "most_used_tools": self.get_most_used_tools(),
            "average_response_time": self.get_average_response_time()
        }
        
        return report
```

Update the `CustomerSupportBot` class to integrate analytics:

```python
class CustomerSupportBot:
    def __init__(self, analytics=None):
        self.agent = support_agent
        self.current_customer_id = None
        self.active_conversation = False
        self.conversation_history = []
        self.analytics = analytics or SupportBotAnalytics()
    
    # ... other methods ...
    
    def process_message(self, message):
        """Process a customer message and generate a response."""
        if not self.active_conversation:
            return "No active conversation. Please start a conversation first."
        
        # Record start time for response time tracking
        import time
        start_time = time.time()
        
        # ... existing code ...
        
        # Run agent with message and context
        prompt = f"""
        {context}
        
        You are a helpful customer support bot. The customer has sent the following message:
        
        {message}
        
        Please help the customer by providing information or using the appropriate tools.
        If you need to create a ticket, use the customer's ID: {self.current_customer_id}
        If you can't help with something, offer to escalate to a human agent.
        """
        
        response = self.agent.run(prompt)
        
        # Log tool usage from agent response (simplified)
        if "search_knowledge_base" in response.lower():
            self.analytics.log_tool_usage("search_knowledge_base")
        if "create_ticket" in response.lower():
            self.analytics.log_tool_usage("create_ticket")
            self.analytics.log_ticket_creation()
        if "escalate_to_human" in response.lower():
            self.analytics.log_tool_usage("escalate_to_human")
        
        # ... existing code ...
        
        # Log response time
        end_time = time.time()
        self.analytics.log_response_time(end_time - start_time)
        
        return response
    
    def end_conversation(self):
        """End the current conversation."""
        if not self.active_conversation:
            return "No active conversation to end."
        
        # Log the completed conversation
        self.analytics.log_conversation(
            self.current_customer_id,
            self.conversation_history
        )
        
        self.active_conversation = False
        return "Conversation ended. Thank you for contacting our support."
```

Update the main function to show analytics:

```python
def main():
    # Create analytics
    analytics = SupportBotAnalytics()
    
    # Create the support bot with analytics
    bot = CustomerSupportBot(analytics=analytics)
    
    # ... existing code ...
    
    # After conversation ends, show analytics
    print("\nSupport Bot Analytics:")
    print("-" * 50)
    report = analytics.generate_report()
    for key, value in report.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
```

## Complete Code

Here's the complete code for our customer support bot:

```python
import os
import asyncio
import time
import datetime
from dotenv import load_dotenv
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.memory import EpisodicMemory, SemanticMemory, CompositeMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence
from agent_patterns.core.tools.base import BaseToolProvider, Tool

# Load environment variables
load_dotenv()

class CustomerSupportToolProvider(BaseToolProvider):
    """Tool provider for customer support operations."""
    
    def __init__(self):
        super().__init__()
        # Simulated knowledge base
        self.knowledge_base = {
            "product_features": {
                "basic": ["Feature A", "Feature B", "Feature C"],
                "premium": ["Feature A", "Feature B", "Feature C", "Feature D", "Feature E"],
                "enterprise": ["Feature A", "Feature B", "Feature C", "Feature D", "Feature E", "Feature F", "Feature G"]
            },
            "pricing": {
                "basic": "$10/month",
                "premium": "$25/month",
                "enterprise": "Custom pricing"
            },
            "common_issues": {
                "login_problem": "Try clearing your browser cache and cookies, then restart your browser.",
                "payment_failed": "Verify your payment information is up-to-date and try again.",
                "feature_not_working": "Ensure you're on the latest version. If the issue persists, try restarting the application."
            }
        }
        
        # Simulated ticket system
        self.tickets = {}
        self.next_ticket_id = 1000
    
    def get_tools(self):
        """Return available tools."""
        return [
            Tool(
                name="search_knowledge_base",
                description="Search the knowledge base for information",
                function=self.search_knowledge_base,
                parameters={
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                }
            ),
            Tool(
                name="get_product_features",
                description="Get features for a specific product tier",
                function=self.get_product_features,
                parameters={
                    "tier": {
                        "type": "string",
                        "description": "Product tier (basic, premium, or enterprise)"
                    }
                }
            ),
            Tool(
                name="get_pricing",
                description="Get pricing information for a specific tier",
                function=self.get_pricing,
                parameters={
                    "tier": {
                        "type": "string",
                        "description": "Product tier (basic, premium, or enterprise)"
                    }
                }
            ),
            Tool(
                name="create_ticket",
                description="Create a support ticket",
                function=self.create_ticket,
                parameters={
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Ticket subject"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Ticket priority (low, medium, high)",
                        "enum": ["low", "medium", "high"]
                    }
                }
            ),
            Tool(
                name="get_ticket",
                description="Get details of a support ticket",
                function=self.get_ticket,
                parameters={
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID"
                    }
                }
            ),
            Tool(
                name="update_ticket",
                description="Update a support ticket",
                function=self.update_ticket,
                parameters={
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID"
                    },
                    "status": {
                        "type": "string",
                        "description": "New ticket status",
                        "enum": ["open", "in_progress", "pending", "resolved", "closed"]
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes to add to the ticket"
                    }
                }
            ),
            Tool(
                name="escalate_to_human",
                description="Escalate the conversation to a human agent",
                function=self.escalate_to_human,
                parameters={
                    "reason": {
                        "type": "string",
                        "description": "Reason for escalation"
                    },
                    "urgency": {
                        "type": "string",
                        "description": "Urgency level",
                        "enum": ["low", "medium", "high"]
                    }
                }
            )
        ]
    
    async def search_knowledge_base(self, query):
        """Search the knowledge base for information."""
        query = query.lower()
        results = []
        
        # Search in product features
        for tier, features in self.knowledge_base["product_features"].items():
            for feature in features:
                if query in feature.lower():
                    results.append({
                        "category": "product_features",
                        "tier": tier,
                        "content": feature
                    })
        
        # Search in pricing
        for tier, price in self.knowledge_base["pricing"].items():
            if query in tier.lower() or query in price.lower():
                results.append({
                    "category": "pricing",
                    "tier": tier,
                    "content": price
                })
        
        # Search in common issues
        for issue, solution in self.knowledge_base["common_issues"].items():
            if query in issue.lower() or query in solution.lower():
                results.append({
                    "category": "common_issues",
                    "issue": issue,
                    "content": solution
                })
        
        return {
            "query": query,
            "results": results,
            "result_count": len(results)
        }
    
    async def get_product_features(self, tier):
        """Get features for a specific product tier."""
        tier = tier.lower()
        if tier in self.knowledge_base["product_features"]:
            features = self.knowledge_base["product_features"][tier]
            return {
                "tier": tier,
                "features": features,
                "feature_count": len(features)
            }
        else:
            return {
                "error": f"Tier '{tier}' not found",
                "available_tiers": list(self.knowledge_base["product_features"].keys())
            }
    
    async def get_pricing(self, tier):
        """Get pricing information for a specific tier."""
        tier = tier.lower()
        if tier in self.knowledge_base["pricing"]:
            price = self.knowledge_base["pricing"][tier]
            return {
                "tier": tier,
                "price": price
            }
        else:
            return {
                "error": f"Tier '{tier}' not found",
                "available_tiers": list(self.knowledge_base["pricing"].keys())
            }
    
    async def create_ticket(self, customer_id, subject, description, priority="medium"):
        """Create a support ticket."""
        ticket_id = str(self.next_ticket_id)
        self.next_ticket_id += 1
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Create ticket
        ticket = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "subject": subject,
            "description": description,
            "priority": priority,
            "status": "open",
            "created_at": timestamp,
            "updated_at": timestamp,
            "notes": []
        }
        
        # Save ticket
        self.tickets[ticket_id] = ticket
        
        return {
            "ticket_id": ticket_id,
            "status": "created",
            "message": f"Ticket {ticket_id} created successfully"
        }
    
    async def get_ticket(self, ticket_id):
        """Get details of a support ticket."""
        if ticket_id in self.tickets:
            return self.tickets[ticket_id]
        else:
            return {
                "error": f"Ticket {ticket_id} not found"
            }
    
    async def update_ticket(self, ticket_id, status=None, notes=None):
        """Update a support ticket."""
        if ticket_id not in self.tickets:
            return {
                "error": f"Ticket {ticket_id} not found"
            }
        
        ticket = self.tickets[ticket_id]
        
        # Update timestamp
        ticket["updated_at"] = datetime.datetime.now().isoformat()
        
        # Update status if provided
        if status:
            ticket["status"] = status
        
        # Add notes if provided
        if notes:
            ticket["notes"].append({
                "content": notes,
                "timestamp": ticket["updated_at"]
            })
        
        return {
            "ticket_id": ticket_id,
            "status": ticket["status"],
            "message": f"Ticket {ticket_id} updated successfully"
        }
    
    async def escalate_to_human(self, reason, urgency="medium"):
        """Escalate the conversation to a human agent."""
        # In a real implementation, this would integrate with a queue system
        return {
            "status": "escalated",
            "reason": reason,
            "urgency": urgency,
            "message": "This conversation has been escalated to a human agent who will respond shortly."
        }

class SupportBotAnalytics:
    def __init__(self):
        self.conversations = {}
        self.ticket_stats = {
            "created": 0,
            "resolved": 0
        }
        self.tool_usage = {}
        self.response_times = []
    
    def log_conversation(self, customer_id, conversation):
        """Log a completed conversation."""
        if customer_id not in self.conversations:
            self.conversations[customer_id] = []
        
        self.conversations[customer_id].append(conversation)
    
    def log_ticket_creation(self):
        """Log a ticket creation event."""
        self.ticket_stats["created"] += 1
    
    def log_ticket_resolution(self):
        """Log a ticket resolution event."""
        self.ticket_stats["resolved"] += 1
    
    def log_tool_usage(self, tool_name):
        """Log a tool usage event."""
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        
        self.tool_usage[tool_name] += 1
    
    def log_response_time(self, seconds):
        """Log response time in seconds."""
        self.response_times.append(seconds)
    
    def get_average_response_time(self):
        """Get the average response time."""
        if not self.response_times:
            return 0
        
        return sum(self.response_times) / len(self.response_times)
    
    def get_most_used_tools(self, limit=5):
        """Get the most frequently used tools."""
        sorted_tools = sorted(
            self.tool_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_tools[:limit]
    
    def get_conversation_count(self):
        """Get the total number of conversations."""
        return sum(len(convs) for convs in self.conversations.values())
    
    def get_customer_count(self):
        """Get the number of unique customers."""
        return len(self.conversations)
    
    def generate_report(self):
        """Generate an analytics report."""
        report = {
            "conversation_count": self.get_conversation_count(),
            "customer_count": self.get_customer_count(),
            "ticket_stats": self.ticket_stats,
            "most_used_tools": self.get_most_used_tools(),
            "average_response_time": self.get_average_response_time()
        }
        
        return report

# Set up memory persistence
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# Create memory components
episodic_memory = EpisodicMemory(
    persistence, 
    namespace="conversations"
)

semantic_memory = SemanticMemory(
    persistence,
    namespace="customer_info"
)

# Create composite memory
memory = CompositeMemory({
    "episodic": episodic_memory,
    "semantic": semantic_memory
})

# Configure LLM settings
llm_configs = {
    "default": {
        "provider": os.getenv("DEFAULT_MODEL_PROVIDER", "openai"),
        "model_name": os.getenv("DEFAULT_MODEL_NAME", "gpt-4o")
    }
}

# Create tool provider
support_tool_provider = CustomerSupportToolProvider()

# Create support bot agent
support_agent = ReActAgent(
    llm_configs=llm_configs,
    memory=memory,
    memory_config={
        "episodic": True,
        "semantic": True
    },
    tool_provider=support_tool_provider
)

class CustomerSupportBot:
    def __init__(self, analytics=None):
        self.agent = support_agent
        self.current_customer_id = None
        self.active_conversation = False
        self.conversation_history = []
        self.analytics = analytics or SupportBotAnalytics()
    
    def start_conversation(self, customer_id):
        """Start a new conversation with a customer."""
        self.current_customer_id = customer_id
        self.active_conversation = True
        self.conversation_history = []
        
        # Store customer information if available (simulated)
        customer_info = self.get_customer_info(customer_id)
        
        # Save customer info to memory
        if customer_info:
            for attribute, value in customer_info.items():
                asyncio.run(semantic_memory.save({
                    "entity": f"customer:{customer_id}",
                    "attribute": attribute,
                    "value": value
                }))
        
        # Prepare greeting
        greeting = "Hello! I'm your AI support assistant. How can I help you today?"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })
        
        return greeting
    
    def get_customer_info(self, customer_id):
        """Simulate retrieving customer info from a database."""
        # In a real implementation, this would query a customer database
        # For this example, we'll return mock data
        customer_db = {
            "C12345": {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "plan": "premium",
                "signup_date": "2023-01-15"
            },
            "C67890": {
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "plan": "basic",
                "signup_date": "2023-06-22"
            },
            "C24680": {
                "name": "Robert Johnson",
                "email": "robert.johnson@example.com",
                "plan": "enterprise",
                "signup_date": "2022-11-05"
            }
        }
        
        return customer_db.get(customer_id, {})
    
    def process_message(self, message):
        """Process a customer message and generate a response."""
        if not self.active_conversation:
            return "No active conversation. Please start a conversation first."
        
        # Record start time for response time tracking
        start_time = time.time()
        
        # Add customer message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Save to episodic memory
        asyncio.run(episodic_memory.save({
            "customer_id": self.current_customer_id,
            "role": "user",
            "content": message,
            "timestamp": self._get_timestamp()
        }))
        
        # Check for conversation ending
        if message.lower() in ["bye", "goodbye", "end", "quit", "exit"]:
            self.active_conversation = False
            response = "Thank you for contacting our support. Is there anything else I can help you with before you go?"
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Save to episodic memory
            asyncio.run(episodic_memory.save({
                "customer_id": self.current_customer_id,
                "role": "assistant",
                "content": response,
                "timestamp": self._get_timestamp()
            }))
            
            return response
        
        # Create context for agent
        customer_info = self.get_customer_info(self.current_customer_id)
        context = f"Customer ID: {self.current_customer_id}\n"
        if customer_info:
            context += f"Name: {customer_info.get('name', 'Unknown')}\n"
            context += f"Plan: {customer_info.get('plan', 'Unknown')}\n"
        
        # Run agent with message and context
        prompt = f"""
        {context}
        
        You are a helpful customer support bot. The customer has sent the following message:
        
        {message}
        
        Please help the customer by providing information or using the appropriate tools.
        If you need to create a ticket, use the customer's ID: {self.current_customer_id}
        If you can't help with something, offer to escalate to a human agent.
        """
        
        response = self.agent.run(prompt)
        
        # Log tool usage from agent response (simplified)
        if "search_knowledge_base" in response.lower():
            self.analytics.log_tool_usage("search_knowledge_base")
        if "create_ticket" in response.lower():
            self.analytics.log_tool_usage("create_ticket")
            self.analytics.log_ticket_creation()
        if "escalate_to_human" in response.lower():
            self.analytics.log_tool_usage("escalate_to_human")
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Save to episodic memory
        asyncio.run(episodic_memory.save({
            "customer_id": self.current_customer_id,
            "role": "assistant",
            "content": response,
            "timestamp": self._get_timestamp()
        }))
        
        # Log response time
        end_time = time.time()
        self.analytics.log_response_time(end_time - start_time)
        
        return response
    
    def end_conversation(self):
        """End the current conversation."""
        if not self.active_conversation:
            return "No active conversation to end."
        
        # Log the completed conversation
        self.analytics.log_conversation(
            self.current_customer_id,
            self.conversation_history
        )
        
        self.active_conversation = False
        return "Conversation ended. Thank you for contacting our support."
    
    def get_conversation_history(self):
        """Get the current conversation history."""
        return self.conversation_history
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        return datetime.datetime.now().isoformat()

def main():
    # Create analytics
    analytics = SupportBotAnalytics()
    
    # Create the support bot with analytics
    bot = CustomerSupportBot(analytics=analytics)
    
    # Get customer ID
    customer_id = input("Enter customer ID (e.g., C12345): ")
    if not customer_id:
        customer_id = "C12345"  # Default for testing
    
    # Start conversation
    greeting = bot.start_conversation(customer_id)
    print(f"Bot: {greeting}")
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for exit command
        if user_input.lower() in ["quit", "exit"]:
            bot.end_conversation()
            print("Bot: Goodbye!")
            break
        
        # Process message
        response = bot.process_message(user_input)
        print(f"Bot: {response}")
        
        # Check if conversation ended
        if not bot.active_conversation:
            break
    
    # After conversation ends, show analytics
    print("\nSupport Bot Analytics:")
    print("-" * 50)
    report = analytics.generate_report()
    for key, value in report.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
```

## Architecture Diagram

```mermaid
graph TD
    A[Customer Interface] --> B[CustomerSupportBot]
    B --> C[ReAct Agent]
    C --> D[Tool Provider]
    C --> E[Memory System]
    B --> F[Analytics]
    
    D --> G[Knowledge Base Tools]
    D --> H[Ticket Management Tools]
    D --> I[Escalation Tools]
    
    E --> J[Episodic Memory]
    E --> K[Semantic Memory]
    
    F --> L[Conversation Metrics]
    F --> M[Tool Usage Metrics]
    F --> N[Response Time Metrics]
```

## Next Steps

You can enhance this support bot with:

1. **Integration with Real Systems**: Connect to actual customer databases, CRMs, and ticketing systems
2. **Multi-Channel Support**: Add interfaces for web chat, email, SMS, and messaging platforms
3. **Sentiment Analysis**: Add sentiment detection to identify frustrated customers
4. **Proactive Support**: Implement triggered messages based on user behavior
5. **Handoff Protocols**: Create seamless handoffs to human agents with full context

By using the ReAct agent pattern, our support bot benefits from:
- Tool-based problem solving capabilities
- Reasoning about customer issues before taking action
- Access to knowledge bases and ticketing systems
- Memory of past interactions for personalized support

This approach creates a support bot that can handle routine inquiries, create tickets when needed, and know when to escalate to human agents.