# Best Practices for Agent Patterns

Comprehensive guide to best practices, optimization strategies, common pitfalls, and production-ready patterns for building robust AI agent systems.

## Overview

This guide consolidates learnings from:
- Production deployments
- Performance optimization
- Cost management
- Quality assurance
- Security considerations
- Maintainability

## Design Principles

### 1. Choose the Right Pattern for the Task

**Decision Framework**:

```python
def select_pattern(task_characteristics):
    """Select appropriate pattern based on task."""

    if task_characteristics["requires_tools"]:
        if task_characteristics["cost_sensitive"]:
            return "REWOO"  # Plan all tool calls upfront
        else:
            return "ReAct"  # Iterative tool use

    elif task_characteristics["requires_learning"]:
        return "Reflexion"  # Learn from failures

    elif task_characteristics["requires_quality"]:
        return "Reflection"  # Iterative refinement

    elif task_characteristics["requires_research"]:
        return "STORM"  # Multi-perspective research

    elif task_characteristics["complex_reasoning"]:
        return "SelfDiscovery"  # Adaptive strategies

    else:
        return "Reflection"  # General purpose
```

### 2. Start Simple, Then Optimize

```python
# Phase 1: Proof of Concept
agent = ReflectionAgent(
    llm_configs=simple_config,
    max_reflection_cycles=1
)

# Phase 2: Production MVP
agent = ReflectionAgent(
    llm_configs=production_config,
    max_reflection_cycles=2,
    custom_instructions=domain_guidelines
)

# Phase 3: Optimized Production
agent = ReflectionAgent(
    llm_configs=optimized_config,
    max_reflection_cycles=2,
    custom_instructions=domain_guidelines,
    prompt_overrides=tested_overrides
)
```

### 3. Separate Concerns

```python
# Good: Separation of concerns
class AgentOrchestrator:
    """Orchestrates agent execution with separate responsibilities."""

    def __init__(self):
        self.agent = self._create_agent()
        self.validator = InputValidator()
        self.logger = StructuredLogger()
        self.metrics = MetricsCollector()
        self.cache = ResultCache()

    def execute(self, task: str) -> str:
        # Validate
        validated_task = self.validator.validate(task)

        # Check cache
        cached = self.cache.get(task)
        if cached:
            return cached

        # Execute
        self.logger.log_start(task)
        self.metrics.start_timer()

        try:
            result = self.agent.run(validated_task)

            self.metrics.record_success()
            self.logger.log_success(result)
            self.cache.set(task, result)

            return result

        except Exception as e:
            self.metrics.record_failure()
            self.logger.log_error(e)
            raise
```

## Prompt Engineering

### 1. Be Specific and Clear

❌ **Bad**: Vague prompts
```python
custom_instructions = "Be helpful and accurate"
```

✅ **Good**: Specific, actionable guidelines
```python
custom_instructions = """
Guidelines:
1. Cite sources for all factual claims
2. Use bullet points for lists of 3+ items
3. Define technical terms on first use
4. Provide concrete examples
5. Acknowledge uncertainties explicitly
"""
```

### 2. Use Hierarchical Goals

```python
custom_instructions = """
PRIMARY GOALS (non-negotiable):
1. Accuracy: All facts must be verifiable
2. Safety: Never provide harmful information

SECONDARY GOALS (important):
3. Clarity: 8th grade reading level
4. Completeness: Address all aspects of question

TERTIARY GOALS (nice-to-have):
5. Brevity: Concise without sacrificing clarity
6. Examples: Concrete examples for abstract concepts
"""
```

### 3. Provide Examples in Prompts

```python
prompt_override = {
    "Generate": {
        "system": """Generate structured responses.

Example format:
## Summary
- Key point 1
- Key point 2

## Details
Detailed explanation...

## Conclusion
Final thoughts...""",
        "user": "Topic: {task}\n\nProvide structured response:"
    }
}
```

### 4. Test Prompts Systematically

```python
def test_prompt_variations(task, variations):
    """A/B test prompt variations."""

    results = {}

    for name, prompts in variations.items():
        agent = ReflectionAgent(
            llm_configs=test_config,
            prompt_overrides=prompts
        )

        result = agent.run(task)

        results[name] = {
            "result": result,
            "length": len(result),
            "quality_score": evaluate_quality(result)
        }

    return results
```

## Configuration Management

### 1. Use Environment-Based Configs

```python
# config.py
import os

class Config:
    """Environment-based configuration."""

    def __init__(self, environment: str = None):
        self.env = environment or os.getenv("ENVIRONMENT", "development")

    @property
    def llm_configs(self):
        if self.env == "production":
            return {
                "thinking": {
                    "provider": "openai",
                    "model": "gpt-4-turbo",
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            }
        else:
            return {
                "thinking": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.0,  # Deterministic for testing
                    "max_tokens": 1000
                }
            }

# Usage
config = Config()
agent = ReActAgent(llm_configs=config.llm_configs, tools=tools)
```

### 2. Version Your Configurations

```python
# configs/v1.py
LLM_CONFIGS_V1 = {
    "thinking": {"provider": "openai", "model": "gpt-3.5-turbo"}
}

# configs/v2.py
LLM_CONFIGS_V2 = {
    "thinking": {"provider": "openai", "model": "gpt-4"}
}

# configs/v3.py (current)
LLM_CONFIGS_V3 = {
    "thinking": {
        "provider": "anthropic",
        "model": "claude-3-opus-20240229"
    }
}

# Usage
from configs.v3 import LLM_CONFIGS_V3 as LLM_CONFIGS
```

### 3. Centralize Domain Instructions

```python
# domain_instructions.py
class DomainInstructions:
    """Centralized domain-specific instructions."""

    MEDICAL = """
    DOMAIN: Medical
    - Cite evidence-based sources
    - Include medical disclaimers
    - Recommend professional consultation
    Version: 2.1
    Updated: 2024-01-15
    """

    LEGAL = """
    DOMAIN: Legal
    - Specify jurisdiction
    - Include legal disclaimers
    - Cite laws and regulations
    Version: 1.3
    Updated: 2024-01-10
    """

    FINANCIAL = """
    DOMAIN: Financial
    - Discuss risks comprehensively
    - Include regulatory disclosures
    - No specific investment advice
    Version: 1.5
    Updated: 2024-01-20
    """

# Usage
agent = SelfDiscoveryAgent(
    llm_configs=configs,
    custom_instructions=DomainInstructions.MEDICAL
)
```

## Error Handling

### 1. Always Use Try-Catch

```python
def safe_run(agent, task, fallback="Service unavailable"):
    """Run agent with comprehensive error handling."""

    try:
        return agent.run(task)

    except RateLimitError as e:
        logger.warning(f"Rate limit hit: {e}")
        time.sleep(60)  # Wait and retry
        return agent.run(task)

    except Timeout as e:
        logger.error(f"Timeout: {e}")
        return fallback

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise  # Re-raise validation errors

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return fallback
```

### 2. Implement Circuit Breakers

```python
class CircuitBreaker:
    """Circuit breaker for agent calls."""

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = "closed"

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker OPEN")

        try:
            result = func(*args, **kwargs)

            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0

            return result

        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()

            if self.failures >= self.failure_threshold:
                self.state = "open"

            raise

breaker = CircuitBreaker()
result = breaker.call(agent.run, task)
```

### 3. Graceful Degradation

```python
def run_with_degradation(task):
    """Try progressively simpler approaches."""

    strategies = [
        ("complex", create_complex_agent),
        ("standard", create_standard_agent),
        ("simple", create_simple_agent),
        ("fallback", create_fallback_response)
    ]

    for name, strategy in strategies:
        try:
            logger.info(f"Trying {name} strategy")
            return strategy()(task)

        except Exception as e:
            logger.warning(f"{name} strategy failed: {e}")
            continue

    return "All strategies failed. Please try again later."
```

## Performance Optimization

### 1. Cache Aggressively

```python
from functools import lru_cache
import hashlib

class CachedAgent:
    """Agent with caching."""

    def __init__(self, agent):
        self.agent = agent
        self.cache = {}

    def run(self, task: str, use_cache: bool = True) -> str:
        if not use_cache:
            return self.agent.run(task)

        cache_key = hashlib.sha256(task.encode()).hexdigest()

        if cache_key in self.cache:
            logger.info("Cache hit")
            return self.cache[cache_key]

        result = self.agent.run(task)
        self.cache[cache_key] = result

        return result
```

### 2. Use Appropriate Models

```python
def get_model_for_task(task_complexity: str):
    """Select model based on complexity."""

    models = {
        "simple": "gpt-3.5-turbo",      # Fast, cheap
        "moderate": "gpt-4",             # Balanced
        "complex": "gpt-4-turbo",        # Best quality
        "creative": "gpt-4",             # High temperature
        "analytical": "claude-3-opus"    # Strong reasoning
    }

    return models.get(task_complexity, "gpt-4")
```

### 3. Limit Iterations Appropriately

```python
# Bad: Unlimited iterations
agent = ReActAgent(llm_configs=configs, tools=tools, max_iterations=100)

# Good: Reasonable limits
agent = ReActAgent(llm_configs=configs, tools=tools, max_iterations=5)

# Better: Dynamic limits based on task
def get_max_iterations(task):
    if "simple" in task.lower():
        return 3
    elif "complex" in task.lower():
        return 10
    else:
        return 5

agent = ReActAgent(
    llm_configs=configs,
    tools=tools,
    max_iterations=get_max_iterations(task)
)
```

### 4. Parallel Processing When Possible

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_batch(tasks, agent):
    """Process multiple tasks in parallel."""

    results = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {
            executor.submit(agent.run, task): task
            for task in tasks
        }

        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                results[task] = future.result()
            except Exception as e:
                logger.error(f"Task failed: {task[:50]}: {e}")
                results[task] = None

    return results
```

## Cost Management

### 1. Monitor and Track Costs

```python
def estimate_cost(input_text, output_text, model):
    """Estimate API cost."""

    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "claude-3-opus": {"input": 0.015, "output": 0.075}
    }

    input_tokens = len(input_text.split()) * 1.3
    output_tokens = len(output_text.split()) * 1.3

    pricing = PRICING.get(model, PRICING["gpt-4"])

    return (
        (input_tokens / 1000) * pricing["input"] +
        (output_tokens / 1000) * pricing["output"]
    )

class CostTrackingAgent:
    def __init__(self, agent, model):
        self.agent = agent
        self.model = model
        self.total_cost = 0.0

    def run(self, task):
        result = self.agent.run(task)

        cost = estimate_cost(task, result, self.model)
        self.total_cost += cost

        logger.info(f"Cost: ${cost:.4f}, Total: ${self.total_cost:.4f}")

        return result
```

### 2. Use Cost-Effective Patterns

```python
# Expensive: ReAct with many iterations
expensive = ReActAgent(
    llm_configs={"thinking": {"model": "gpt-4"}},
    tools=tools,
    max_iterations=10  # Many LLM calls
)

# Cheaper: REWOO (plans all tools upfront)
cheaper = REWOOAgent(
    llm_configs={"thinking": {"model": "gpt-4"}},
    tools=tools  # Single planning call + tool execution
)
```

### 3. Implement Budgets

```python
class BudgetedAgent:
    """Agent with cost budget."""

    def __init__(self, agent, budget: float):
        self.agent = agent
        self.budget = budget
        self.spent = 0.0

    def run(self, task):
        if self.spent >= self.budget:
            raise BudgetExceededError(
                f"Budget ${self.budget:.2f} exceeded (spent ${self.spent:.2f})"
            )

        result = self.agent.run(task)

        # Estimate and track cost
        cost = estimate_cost(task, result, "gpt-4")
        self.spent += cost

        return result
```

## Testing

### 1. Test at Multiple Levels

```python
# Unit tests: Test components in isolation
def test_agent_initialization():
    agent = ReflectionAgent(llm_configs=test_configs)
    assert agent.max_reflection_cycles == 1

# Integration tests: Test workflows with mocks
@patch.object(ReflectionAgent, "_get_llm")
def test_reflection_workflow(mock_llm):
    # Test full workflow
    pass

# E2E tests: Test with real LLMs (expensive)
@pytest.mark.slow
def test_real_llm():
    agent = ReflectionAgent(llm_configs=real_configs)
    result = agent.run("Test task")
    assert result is not None
```

### 2. Use Deterministic Settings for Tests

```python
test_configs = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.0,  # Deterministic!
        "max_tokens": 500
    }
}
```

### 3. Mock Expensive Operations

```python
@patch.object(Agent, "_get_llm")
def test_with_mock(mock_get_llm):
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="Test response")
    mock_get_llm.return_value = mock_llm

    agent = create_agent()
    result = agent.run("test")

    assert result == "Test response"
```

## Security

### 1. Validate All Inputs

```python
def validate_input(task: str, max_length: int = 10000):
    """Validate and sanitize input."""

    if not task or not task.strip():
        raise ValueError("Empty input")

    if len(task) > max_length:
        raise ValueError(f"Input too long (max {max_length})")

    # Check for injection attempts
    forbidden = ["<script>", "eval(", "exec(", "system("]
    for pattern in forbidden:
        if pattern in task.lower():
            raise ValueError(f"Forbidden pattern: {pattern}")

    return task.strip()
```

### 2. Sanitize Outputs

```python
def sanitize_output(result: str):
    """Remove sensitive data from output."""

    import re

    # Remove API keys
    result = re.sub(r'sk-[a-zA-Z0-9]{48}', '[API_KEY_REDACTED]', result)

    # Remove credit cards
    result = re.sub(r'\d{16}', '[CC_REDACTED]', result)

    # Remove SSNs
    result = re.sub(r'\d{3}-\d{2}-\d{4}', '[SSN_REDACTED]', result)

    return result
```

### 3. Implement Rate Limiting

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=100, window=3600):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        window_start = now - self.window

        # Clean old requests
        self.requests[user_id] = [
            t for t in self.requests[user_id]
            if t > window_start
        ]

        if len(self.requests[user_id]) >= self.max_requests:
            return False

        self.requests[user_id].append(now)
        return True
```

## Monitoring and Observability

### 1. Structured Logging

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_agent_execution(agent_type, task, result, duration):
    """Log agent execution with structured data."""

    logger.info(json.dumps({
        "event": "agent_execution",
        "agent_type": agent_type,
        "task_length": len(task),
        "result_length": len(result),
        "duration_ms": duration * 1000,
        "timestamp": time.time()
    }))
```

### 2. Metrics Collection

```python
from prometheus_client import Counter, Histogram

request_count = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['pattern', 'status']
)

request_duration = Histogram(
    'agent_duration_seconds',
    'Agent execution duration',
    ['pattern']
)

# Usage
with request_duration.labels(pattern="reflection").time():
    try:
        result = agent.run(task)
        request_count.labels(pattern="reflection", status="success").inc()
    except Exception:
        request_count.labels(pattern="reflection", status="error").inc()
        raise
```

### 3. Distributed Tracing

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def run_with_tracing(agent, task):
    """Run agent with distributed tracing."""

    with tracer.start_as_current_span("agent_execution") as span:
        span.set_attribute("pattern", type(agent).__name__)
        span.set_attribute("task_length", len(task))

        try:
            result = agent.run(task)
            span.set_attribute("success", True)
            return result
        except Exception as e:
            span.set_attribute("success", False)
            span.record_exception(e)
            raise
```

## Common Pitfalls

### 1. Not Handling Rate Limits

❌ **Bad**: No rate limit handling
```python
result = agent.run(task)  # Crashes on rate limit
```

✅ **Good**: Handle rate limits with retry
```python
def run_with_retry(agent, task, max_retries=3):
    for i in range(max_retries):
        try:
            return agent.run(task)
        except RateLimitError:
            if i < max_retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                raise
```

### 2. Ignoring Costs

❌ **Bad**: No cost awareness
```python
agent = ReActAgent(
    llm_configs={"thinking": {"model": "gpt-4"}},
    max_iterations=100  # Could be very expensive!
)
```

✅ **Good**: Cost-conscious configuration
```python
agent = ReActAgent(
    llm_configs={"thinking": {"model": "gpt-3.5-turbo"}},
    max_iterations=5
)
```

### 3. No Input Validation

❌ **Bad**: Raw user input
```python
result = agent.run(user_input)  # Could be malicious
```

✅ **Good**: Validated input
```python
validated = validate_input(user_input)
result = agent.run(validated)
```

### 4. Poor Error Messages

❌ **Bad**: Generic errors
```python
except Exception:
    return "Error occurred"
```

✅ **Good**: Informative errors
```python
except RateLimitError:
    return "Rate limit exceeded. Please try again in 60 seconds."
except Timeout:
    return "Request timeout. Try a simpler query."
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return "Unexpected error. Support has been notified."
```

### 5. Not Testing with Real Scenarios

Always test with realistic inputs:

```python
test_cases = [
    ("simple query", "What is Python?"),
    ("complex query", "Explain quantum computing with examples"),
    ("edge case", "a" * 10000),  # Very long input
    ("empty", ""),
    ("special chars", "Test with émojis 🎉 and symbols @#$%")
]

for name, test_input in test_cases:
    try:
        result = agent.run(test_input)
        print(f"✓ {name}: Passed")
    except Exception as e:
        print(f"✗ {name}: Failed - {e}")
```

## Production Checklist

Before deploying to production:

- ✅ Input validation implemented
- ✅ Output sanitization in place
- ✅ Error handling comprehensive
- ✅ Rate limiting configured
- ✅ Cost tracking enabled
- ✅ Logging structured
- ✅ Metrics being collected
- ✅ Caching implemented
- ✅ Circuit breakers in place
- ✅ Health checks working
- ✅ Security review completed
- ✅ Load testing done
- ✅ Monitoring configured
- ✅ Alerts set up
- ✅ Documentation updated

## Next Steps

- Review specific guides for detailed information
- Test thoroughly before production
- Monitor and iterate on production data
- Join community for latest practices

## Summary

**Golden Rules**:

1. Choose the right pattern for the task
2. Start simple, optimize based on data
3. Always validate inputs and sanitize outputs
4. Implement comprehensive error handling
5. Monitor costs and performance
6. Test at multiple levels
7. Use structured logging
8. Cache aggressively
9. Limit iterations appropriately
10. Security first, always
