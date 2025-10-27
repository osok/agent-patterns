# Error Handling Best Practices

Comprehensive guide to robust error handling, graceful degradation, and recovery strategies for Agent Patterns.

## Overview

Robust error handling is critical for production agent systems. This guide covers:
- Exception handling patterns
- Graceful degradation strategies
- Retry logic and resilience
- Error logging and monitoring
- Recovery mechanisms

## Common Error Types

### 1. LLM API Errors

```python
from openai import RateLimitError, APIError, Timeout
from anthropic import AnthropicError

try:
    result = agent.run(task)
except RateLimitError as e:
    # Rate limit exceeded
    print(f"Rate limit error: {e}")
    # Implement backoff and retry
except APIError as e:
    # API service error
    print(f"API error: {e}")
    # Log and potentially retry
except Timeout as e:
    # Request timeout
    print(f"Timeout: {e}")
    # Retry with longer timeout
except Exception as e:
    # Catch-all
    print(f"Unexpected error: {e}")
```

### 2. Configuration Errors

```python
from agent_patterns.patterns import ReActAgent

try:
    agent = ReActAgent(
        llm_configs={
            "thinking": {
                "provider": "invalid_provider",  # Error!
                "model": "gpt-4"
            }
        },
        tools=tools
    )
except ValueError as e:
    print(f"Configuration error: {e}")
    # Use fallback configuration
    agent = ReActAgent(
        llm_configs=get_default_config(),
        tools=tools
    )
```

### 3. Tool Execution Errors

```python
def safe_tool_wrapper(tool_func):
    """Wrap tools with error handling."""
    def wrapper(*args, **kwargs):
        try:
            return tool_func(*args, **kwargs)
        except Exception as e:
            return f"Tool error: {type(e).__name__}: {str(e)}"
    return wrapper

# Use wrapped tools
tools = {
    "search": safe_tool_wrapper(search_function),
    "calculate": safe_tool_wrapper(calculate_function)
}
```

## Error Handling Patterns

### Try-Catch with Fallback

```python
def run_with_fallback(agent, task, fallback_response="Unable to process request"):
    """Run agent with fallback on error."""
    try:
        return agent.run(task)
    except Exception as e:
        print(f"Error: {e}")
        return fallback_response

result = run_with_fallback(agent, task)
```

### Retry with Exponential Backoff

```python
import time

def run_with_retry(agent, task, max_retries=3, base_delay=1):
    """Run agent with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return agent.run(task)
        except (RateLimitError, Timeout) as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"Max retries reached")
                raise
        except Exception as e:
            # Non-retryable error
            raise

result = run_with_retry(agent, task)
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Circuit breaker for agent execution."""

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()

            if self.failures >= self.failure_threshold:
                self.state = "open"

            raise

# Usage
breaker = CircuitBreaker()
result = breaker.call(agent.run, task)
```

### Graceful Degradation

```python
def run_with_degradation(task):
    """Try progressively simpler approaches on failure."""

    # Try full agent first
    try:
        complex_agent = SelfDiscoveryAgent(
            llm_configs=high_quality_config,
            max_selected_modules=5
        )
        return complex_agent.run(task)
    except Exception as e:
        print(f"Complex agent failed: {e}")

    # Fallback to simpler agent
    try:
        simple_agent = ReflectionAgent(
            llm_configs=standard_config,
            max_reflection_cycles=1
        )
        return simple_agent.run(task)
    except Exception as e:
        print(f"Simple agent failed: {e}")

    # Final fallback to basic LLM
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        return llm.invoke(task).content
    except Exception as e:
        return "Service temporarily unavailable"
```

## Logging and Monitoring

### Structured Logging

```python
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LoggingAgent(ReActAgent):
    """Agent with comprehensive logging."""

    def on_start(self, input_data):
        """Log when agent starts."""
        logger.info(json.dumps({
            "event": "agent_start",
            "pattern": self.__class__.__name__,
            "input_length": len(str(input_data))
        }))

    def on_finish(self, result):
        """Log when agent finishes."""
        logger.info(json.dumps({
            "event": "agent_finish",
            "pattern": self.__class__.__name__,
            "output_length": len(str(result))
        }))

    def on_error(self, error):
        """Log errors."""
        logger.error(json.dumps({
            "event": "agent_error",
            "pattern": self.__class__.__name__,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }), exc_info=True)
```

### Metrics Collection

```python
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentMetrics:
    """Metrics for agent execution."""
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    iterations: int = 0
    llm_calls: int = 0

class MetricsCollectingAgent(ReActAgent):
    """Agent that collects execution metrics."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = AgentMetrics(start_time=time.time())

    def run(self, input_data):
        self.metrics.start_time = time.time()
        try:
            result = super().run(input_data)
            self.metrics.success = True
            return result
        except Exception as e:
            self.metrics.error = str(e)
            raise
        finally:
            self.metrics.end_time = time.time()
            self._log_metrics()

    def _log_metrics(self):
        duration = self.metrics.end_time - self.metrics.start_time
        logger.info(json.dumps({
            "duration_seconds": duration,
            "success": self.metrics.success,
            "error": self.metrics.error,
            "llm_calls": self.metrics.llm_calls
        }))
```

## Validation and Safety

### Input Validation

```python
def validate_input(task: str, max_length: int = 10000) -> str:
    """Validate and sanitize input."""

    if not task or not task.strip():
        raise ValueError("Task cannot be empty")

    if len(task) > max_length:
        raise ValueError(f"Task too long (max {max_length} characters)")

    # Remove potentially harmful content
    forbidden_patterns = ["<script>", "eval(", "exec("]
    for pattern in forbidden_patterns:
        if pattern in task.lower():
            raise ValueError(f"Forbidden pattern detected: {pattern}")

    return task.strip()

# Usage
try:
    validated_task = validate_input(user_input)
    result = agent.run(validated_task)
except ValueError as e:
    print(f"Invalid input: {e}")
```

### Output Validation

```python
def validate_output(result: str, expected_patterns: list = None) -> bool:
    """Validate agent output."""

    if not result:
        logger.warning("Empty output detected")
        return False

    # Check for error indicators
    error_indicators = ["error:", "exception:", "failed to"]
    if any(indicator in result.lower() for indicator in error_indicators):
        logger.warning("Error indicator in output")
        return False

    # Check for expected patterns
    if expected_patterns:
        if not any(pattern in result for pattern in expected_patterns):
            logger.warning("Expected patterns not found in output")
            return False

    return True
```

### Safety Guardrails

```python
class SafeAgent:
    """Agent with safety guardrails."""

    def __init__(self, agent, safety_config):
        self.agent = agent
        self.safety_config = safety_config

    def run(self, task):
        # Pre-execution checks
        self._check_input_safety(task)

        # Execute with timeout
        result = self._run_with_timeout(task)

        # Post-execution checks
        self._check_output_safety(result)

        return result

    def _check_input_safety(self, task):
        """Check input for safety issues."""
        if len(task) > self.safety_config.get("max_input_length", 10000):
            raise ValueError("Input too long")

        # Check for injection attempts
        dangerous_patterns = ["system:", "ignore previous"]
        if any(p in task.lower() for p in dangerous_patterns):
            raise ValueError("Potentially dangerous input detected")

    def _run_with_timeout(self, task):
        """Run with timeout."""
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Agent execution timeout")

        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.safety_config.get("timeout_seconds", 120))

        try:
            return self.agent.run(task)
        finally:
            signal.alarm(0)  # Cancel alarm

    def _check_output_safety(self, result):
        """Check output for safety issues."""
        # Check for sensitive data leakage
        sensitive_patterns = [
            r"sk-[a-zA-Z0-9]{48}",  # API keys
            r"\d{3}-\d{2}-\d{4}",   # SSN
            r"\d{16}",              # Credit card
        ]

        import re
        for pattern in sensitive_patterns:
            if re.search(pattern, result):
                logger.error("Sensitive data detected in output!")
                raise ValueError("Output contains sensitive data")
```

## Best Practices

### 1. Always Use Try-Catch

```python
# Bad: No error handling
result = agent.run(task)

# Good: Proper error handling
try:
    result = agent.run(task)
except Exception as e:
    logger.error(f"Agent execution failed: {e}")
    result = get_fallback_response()
```

### 2. Log All Errors

```python
try:
    result = agent.run(task)
except Exception as e:
    logger.error(
        f"Error in agent execution",
        exc_info=True,
        extra={
            "task": task[:100],  # First 100 chars
            "agent_type": type(agent).__name__,
            "error_type": type(e).__name__
        }
    )
    raise
```

### 3. Implement Timeouts

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def run_with_timeout(agent, task, timeout_seconds=60):
    """Run agent with timeout."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(agent.run, task)
        try:
            return future.result(timeout=timeout_seconds)
        except TimeoutError:
            logger.error(f"Agent execution timeout after {timeout_seconds}s")
            raise
```

### 4. Graceful Degradation

Always have fallback options:

```python
def run_with_fallbacks(task):
    """Try multiple approaches."""
    approaches = [
        (best_agent, "best"),
        (good_agent, "good"),
        (basic_agent, "basic"),
        (direct_llm, "direct")
    ]

    for agent, level in approaches:
        try:
            result = agent.run(task)
            logger.info(f"Success with {level} approach")
            return result
        except Exception as e:
            logger.warning(f"{level} approach failed: {e}")
            continue

    # All approaches failed
    return "Service unavailable, please try again later"
```

### 5. Monitor and Alert

```python
import smtplib
from email.message import EmailMessage

class MonitoredAgent:
    """Agent with monitoring and alerting."""

    def __init__(self, agent, alert_email):
        self.agent = agent
        self.alert_email = alert_email
        self.error_count = 0
        self.error_threshold = 5

    def run(self, task):
        try:
            return self.agent.run(task)
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error #{self.error_count}: {e}")

            if self.error_count >= self.error_threshold:
                self._send_alert(e)

            raise

    def _send_alert(self, error):
        """Send email alert on repeated failures."""
        msg = EmailMessage()
        msg['Subject'] = f'Agent Error Alert: {self.error_count} errors'
        msg['From'] = 'agent-monitor@example.com'
        msg['To'] = self.alert_email
        msg.set_content(f'Agent experiencing issues: {error}')

        # Send email (configure SMTP server)
        # smtp.send_message(msg)
```

## Testing Error Handling

```python
import pytest

def test_agent_handles_rate_limit():
    """Test rate limit handling."""
    agent = ReActAgent(llm_configs=test_configs, tools=tools)

    # Mock rate limit error
    with patch.object(agent, '_get_llm') as mock_llm:
        mock_llm.side_effect = RateLimitError("Rate limit")

        with pytest.raises(RateLimitError):
            agent.run("test task")

def test_agent_handles_invalid_config():
    """Test invalid configuration handling."""
    with pytest.raises(ValueError):
        agent = ReActAgent(
            llm_configs={"invalid": {}},
            tools=tools
        )

def test_timeout_handling():
    """Test timeout handling."""
    def slow_tool(x):
        time.sleep(10)
        return x

    agent = ReActAgent(
        llm_configs=test_configs,
        tools={"slow": slow_tool}
    )

    with pytest.raises(TimeoutError):
        run_with_timeout(agent, "use slow tool", timeout_seconds=1)
```

## Recovery Strategies

### Checkpoint and Resume

```python
class CheckpointAgent:
    """Agent with checkpoint/resume capability."""

    def __init__(self, agent, checkpoint_file="checkpoint.json"):
        self.agent = agent
        self.checkpoint_file = checkpoint_file

    def run(self, task):
        # Try to resume from checkpoint
        checkpoint = self._load_checkpoint()

        if checkpoint:
            logger.info("Resuming from checkpoint")
            # Resume logic here

        try:
            result = self.agent.run(task)
            self._clear_checkpoint()
            return result
        except Exception as e:
            self._save_checkpoint(task, e)
            raise

    def _save_checkpoint(self, task, error):
        """Save checkpoint on failure."""
        import json
        with open(self.checkpoint_file, 'w') as f:
            json.dump({
                "task": task,
                "error": str(error),
                "timestamp": time.time()
            }, f)

    def _load_checkpoint(self):
        """Load checkpoint if exists."""
        try:
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def _clear_checkpoint(self):
        """Clear checkpoint on success."""
        import os
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
```

## Next Steps

- Review [Testing Guide](testing.md) for error testing strategies
- See [Deployment Guide](deployment.md) for production error handling
- Explore [Best Practices](best-practices.md) for robust agents

## Reference

### Common Exceptions

- `ValueError`: Configuration or validation errors
- `RateLimitError`: API rate limits exceeded
- `APIError`: LLM API service errors
- `Timeout`: Request timeout
- `KeyError`: Missing configuration keys

### Error Handling Checklist

- ✅ Try-catch all agent.run() calls
- ✅ Log all errors with context
- ✅ Implement retry logic for transient errors
- ✅ Validate inputs and outputs
- ✅ Set execution timeouts
- ✅ Have fallback options
- ✅ Monitor error rates
- ✅ Alert on repeated failures
- ✅ Test error scenarios
- ✅ Document error handling approach
