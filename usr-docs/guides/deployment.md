# Production Deployment Guide

Complete guide to deploying Agent Patterns in production, covering API design, scaling, monitoring, cost optimization, and security.

## Overview

Deploying AI agents to production requires careful consideration of:
- API design and wrapping
- Scalability and performance
- Cost management
- Monitoring and observability
- Security and safety
- Reliability and error handling

## API Wrapping

### FastAPI Wrapper

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent_patterns.patterns import ReActAgent
import logging

app = FastAPI(title="Agent API")

logger = logging.getLogger(__name__)

# Request/Response models
class AgentRequest(BaseModel):
    task: str
    pattern: str = "react"
    max_iterations: int = 5

class AgentResponse(BaseModel):
    result: str
    success: bool
    error: str = None
    metadata: dict = {}

# Initialize agents (singleton pattern)
def get_agent(pattern: str):
    """Get or create agent instance."""
    llm_configs = {
        "thinking": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        }
    }

    if pattern == "react":
        return ReActAgent(llm_configs=llm_configs, tools=get_tools())
    elif pattern == "reflection":
        return ReflectionAgent(llm_configs=llm_configs)
    else:
        raise ValueError(f"Unknown pattern: {pattern}")

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """Run agent on task."""
    try:
        agent = get_agent(request.pattern)
        result = agent.run(request.task)

        return AgentResponse(
            result=result,
            success=True,
            metadata={
                "pattern": request.pattern,
                "task_length": len(request.task)
            }
        )

    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Flask Wrapper

```python
from flask import Flask, request, jsonify
from agent_patterns.patterns import ReflectionAgent
import logging

app = Flask(__name__)

logger = logging.getLogger(__name__)

@app.route('/agent/run', methods=['POST'])
def run_agent():
    """Run agent endpoint."""
    try:
        data = request.get_json()
        task = data.get('task')

        if not task:
            return jsonify({"error": "Task required"}), 400

        agent = get_agent()
        result = agent.run(task)

        return jsonify({
            "result": result,
            "success": True
        })

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

## Containerization

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install agent-patterns
RUN pip install -e .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  agent-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## Scaling Strategies

### Horizontal Scaling

```python
# Use load balancer (nginx, AWS ALB, etc.)
# Multiple instances of your API

# docker-compose.yml
services:
  agent-api:
    build: .
    deploy:
      replicas: 3  # Run 3 instances
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - agent-api
```

### Async Processing with Celery

```python
from celery import Celery
from agent_patterns.patterns import ReActAgent

# Configure Celery
celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery.task
def run_agent_async(task, pattern="react"):
    """Run agent asynchronously."""
    try:
        agent = get_agent(pattern)
        result = agent.run(task)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# API endpoint
@app.post("/agent/run/async")
async def run_agent_async_endpoint(request: AgentRequest):
    """Queue agent task."""
    task = run_agent_async.delay(request.task, request.pattern)
    return {"task_id": task.id, "status": "queued"}

@app.get("/agent/result/{task_id}")
async def get_result(task_id: str):
    """Get async task result."""
    task = run_agent_async.AsyncResult(task_id)

    if task.ready():
        return {"status": "completed", "result": task.result}
    else:
        return {"status": "processing"}
```

### Caching

```python
import redis
import hashlib
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cache_key(task: str, pattern: str) -> str:
    """Generate cache key."""
    content = f"{pattern}:{task}"
    return hashlib.sha256(content.encode()).hexdigest()

def run_with_cache(task: str, pattern: str, ttl: int = 3600):
    """Run agent with caching."""

    cache_key = get_cache_key(task, pattern)

    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        logger.info(f"Cache hit for task: {task[:50]}...")
        return json.loads(cached)

    # Execute
    agent = get_agent(pattern)
    result = agent.run(task)

    # Cache result
    redis_client.setex(
        cache_key,
        ttl,
        json.dumps({"result": result, "cached_at": time.time()})
    )

    return {"result": result, "cached": False}
```

## Monitoring and Observability

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
request_count = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['pattern', 'status']
)

request_duration = Histogram(
    'agent_request_duration_seconds',
    'Agent request duration',
    ['pattern']
)

active_requests = Gauge(
    'agent_active_requests',
    'Active agent requests',
    ['pattern']
)

# Instrumented endpoint
@app.post("/agent/run")
async def run_agent(request: AgentRequest):
    pattern = request.pattern

    active_requests.labels(pattern=pattern).inc()
    start_time = time.time()

    try:
        agent = get_agent(pattern)
        result = agent.run(request.task)

        request_count.labels(pattern=pattern, status='success').inc()

        return AgentResponse(result=result, success=True)

    except Exception as e:
        request_count.labels(pattern=pattern, status='error').inc()
        raise

    finally:
        duration = time.time() - start_time
        request_duration.labels(pattern=pattern).observe(duration)
        active_requests.labels(pattern=pattern).dec()
```

### Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info(
    "Agent execution completed",
    extra={
        "pattern": "react",
        "task_id": "12345",
        "duration_ms": 1234
    }
)
```

### Distributed Tracing

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name='localhost',
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Traced agent execution
@app.post("/agent/run")
async def run_agent(request: AgentRequest):
    with tracer.start_as_current_span("agent_execution") as span:
        span.set_attribute("pattern", request.pattern)
        span.set_attribute("task_length", len(request.task))

        try:
            agent = get_agent(request.pattern)
            result = agent.run(request.task)

            span.set_attribute("success", True)
            return AgentResponse(result=result, success=True)

        except Exception as e:
            span.set_attribute("success", False)
            span.record_exception(e)
            raise
```

## Cost Optimization

### Model Selection Strategy

```python
def get_optimized_config(task_complexity: str):
    """Get cost-optimized configuration."""

    if task_complexity == "simple":
        return {
            "thinking": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",  # Cheaper
                "temperature": 0.7
            }
        }
    elif task_complexity == "complex":
        return {
            "thinking": {
                "provider": "openai",
                "model": "gpt-4",  # Better quality
                "temperature": 0.7
            }
        }
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/agent/run")
@limiter.limit("10/minute")
async def run_agent(request: Request, agent_request: AgentRequest):
    """Rate limited endpoint."""
    # Implementation
```

### Usage Tracking

```python
import sqlite3

def track_usage(user_id: str, pattern: str, tokens_used: int, cost: float):
    """Track API usage."""

    conn = sqlite3.connect('usage.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO usage (user_id, pattern, tokens_used, cost, timestamp)
        VALUES (?, ?, ?, ?, datetime('now'))
    ''', (user_id, pattern, tokens_used, cost))

    conn.commit()
    conn.close()

# In endpoint
@app.post("/agent/run")
async def run_agent(request: AgentRequest, user_id: str):
    result = agent.run(request.task)

    # Track usage
    tokens_used = estimate_tokens(request.task, result)
    cost = calculate_cost(tokens_used, model="gpt-4")

    track_usage(user_id, request.pattern, tokens_used, cost)

    return AgentResponse(result=result, success=True)
```

## Security

### API Authentication

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def verify_token(credentials: HTTPAuthorizationCredentials):
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/agent/run")
async def run_agent(
    request: AgentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Authenticated endpoint."""
    user = verify_token(credentials)

    # Run agent
    agent = get_agent(request.pattern)
    result = agent.run(request.task)

    return AgentResponse(result=result, success=True)
```

### Input Sanitization

```python
import re

def sanitize_input(task: str, max_length: int = 10000) -> str:
    """Sanitize user input."""

    # Length check
    if len(task) > max_length:
        raise ValueError(f"Input too long (max {max_length})")

    # Remove potentially harmful patterns
    forbidden = ["<script>", "eval(", "exec(", "system("]
    for pattern in forbidden:
        if pattern in task.lower():
            raise ValueError(f"Forbidden pattern: {pattern}")

    # Remove excessive whitespace
    task = re.sub(r'\s+', ' ', task)

    return task.strip()
```

### Rate Limiting per User

```python
from collections import defaultdict
import time

class UserRateLimiter:
    """Per-user rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limit."""
        now = time.time()
        window_start = now - self.window_seconds

        # Remove old requests
        self.requests[user_id] = [
            t for t in self.requests[user_id]
            if t > window_start
        ]

        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        # Add current request
        self.requests[user_id].append(now)
        return True

rate_limiter = UserRateLimiter(max_requests=100, window_seconds=3600)

@app.post("/agent/run")
async def run_agent(request: AgentRequest, user_id: str):
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Process request
```

## Deployment Environments

### Development

```python
# config/dev.py
ENVIRONMENT = "development"
LOG_LEVEL = "DEBUG"
CACHE_TTL = 60

LLM_CONFIGS = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",  # Cheaper for dev
        "temperature": 0.7
    }
}
```

### Staging

```python
# config/staging.py
ENVIRONMENT = "staging"
LOG_LEVEL = "INFO"
CACHE_TTL = 300

LLM_CONFIGS = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4",  # Production model
        "temperature": 0.7
    }
}
```

### Production

```python
# config/production.py
ENVIRONMENT = "production"
LOG_LEVEL = "WARNING"
CACHE_TTL = 3600

LLM_CONFIGS = {
    "thinking": {
        "provider": "openai",
        "model": "gpt-4-turbo",
        "temperature": 0.7
    }
}

# Additional production settings
ENABLE_MONITORING = True
ENABLE_TRACING = True
ENABLE_CACHING = True
```

## Best Practices

### 1. Use Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

### 2. Implement Health Checks

```python
@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    checks = {
        "api": "healthy",
        "llm": check_llm_connection(),
        "cache": check_redis_connection(),
        "database": check_db_connection()
    }

    all_healthy = all(v == "healthy" for v in checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(checks, status_code=status_code)
```

### 3. Graceful Shutdown

```python
import signal
import sys

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info("Shutting down gracefully...")

    # Cleanup
    redis_client.close()
    # Close other connections

    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### 4. Use Circuit Breakers

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_llm(agent, task):
    """Call LLM with circuit breaker."""
    return agent.run(task)
```

### 5. Monitor Costs

```python
def estimate_cost(input_text: str, output_text: str, model: str) -> float:
    """Estimate API call cost."""

    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    }

    input_tokens = len(input_text.split()) * 1.3
    output_tokens = len(output_text.split()) * 1.3

    pricing = PRICING.get(model, PRICING["gpt-4"])

    cost = (
        (input_tokens / 1000) * pricing["input"] +
        (output_tokens / 1000) * pricing["output"]
    )

    return cost
```

## Next Steps

- Review [Error Handling](error-handling.md) for production robustness
- See [Testing](testing.md) for deployment testing
- Explore [Best Practices](best-practices.md) for optimization

## Reference

### Deployment Checklist

- ✅ API authentication implemented
- ✅ Rate limiting configured
- ✅ Input validation and sanitization
- ✅ Error handling and logging
- ✅ Monitoring and metrics
- ✅ Cost tracking
- ✅ Caching strategy
- ✅ Horizontal scaling ready
- ✅ Health checks implemented
- ✅ Security measures in place
- ✅ Documentation updated
- ✅ Load tested
