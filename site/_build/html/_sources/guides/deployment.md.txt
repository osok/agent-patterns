# Deployment Guide

This guide covers best practices for deploying Agent Patterns in production environments.

## Scaling Considerations

### Architecture Options for Different Scales

| Scale | Architecture | Description | Best For |
|-------|--------------|-------------|----------|
| Small | Single Process | Run agents in a single process | Testing, prototyping, personal assistants |
| Medium | Microservices | Split agent components into separate services | Team productivity tools, department-level applications |
| Large | Distributed | Fully distributed with message queues and load balancing | Enterprise applications, customer-facing services |

### Single Process Architecture

For small-scale deployments or internal tools:

```mermaid
graph TD
    A[User Interface] --> B[FastAPI Server]
    B --> C[Agent Manager]
    C --> D[Agent Instance 1]
    C --> E[Agent Instance 2]
    D --> F[LLM API]
    E --> F
    D --> G[Memory Storage]
    E --> G
    D --> H[Tool Providers]
    E --> H
```

Implementation example:

```python
from fastapi import FastAPI, BackgroundTasks
from agent_patterns.patterns.re_act_agent import ReActAgent
import os
from typing import Dict, Any

app = FastAPI()
agents = {}  # Store agent instances

@app.post("/agent/{agent_id}/query")
async def query_agent(agent_id: str, query: Dict[str, Any], background_tasks: BackgroundTasks):
    # Get or create agent
    if agent_id not in agents:
        agents[agent_id] = ReActAgent(
            llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o"}},
            memory_config={"semantic": True, "episodic": True}
        )
    
    # Run agent in background
    def run_agent():
        result = agents[agent_id].run(query["text"])
        # Store result or send notification
    
    background_tasks.add_task(run_agent)
    return {"status": "processing", "agent_id": agent_id}

@app.get("/agent/{agent_id}/result")
async def get_result(agent_id: str):
    # Return result for the agent
    # Implementation depends on how results are stored
    pass
```

### Microservices Architecture

For medium-scale deployments:

```mermaid
graph TD
    A[Load Balancer] --> B[API Gateway]
    B --> C[Agent Service]
    B --> D[Memory Service]
    B --> E[Tool Service]
    C --> F[LLM Service]
    C --> D
    C --> E
    F --> G[LLM Provider APIs]
    D --> H[Database]
    E --> I[External APIs]
```

Key components:
- Agent Service: Manages agent instances and workflows
- Memory Service: Handles memory persistence and retrieval
- Tool Service: Manages tool execution and external API connections
- LLM Service: Handles LLM provider communication and caching

### Distributed Architecture

For large-scale deployments:

```mermaid
graph TD
    A[Load Balancer] --> B[API Gateways]
    B --> C[Agent Orchestrator]
    C --> D[Message Queue]
    D --> E[Agent Worker Pool]
    E --> F[LLM Service Cluster]
    E --> G[Memory Service Cluster]
    E --> H[Tool Service Cluster]
    F --> I[LLM Provider APIs]
    G --> J[Database Cluster]
    H --> K[External APIs]
    L[Monitoring Service] --> E
    L --> F
    L --> G
    L --> H
```

Key considerations:
- Horizontal scaling of worker pools
- Message queues for asynchronous processing
- Database sharding for memory storage
- Redundancy and failover mechanisms

## Security Best Practices

### Authentication and Authorization

1. **API Authentication**:
   - Use OAuth 2.0 or API keys for service authentication
   - Implement token-based authentication for user sessions
   - Rotate credentials regularly

   ```python
   from fastapi import FastAPI, Depends, HTTPException, status
   from fastapi.security import APIKeyHeader
   
   app = FastAPI()
   api_key_header = APIKeyHeader(name="X-API-Key")
   
   def validate_api_key(api_key: str = Depends(api_key_header)):
       if api_key != os.getenv("API_KEY"):
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid API Key"
           )
       return api_key
   
   @app.post("/agent/query")
   async def query_agent(query: dict, api_key: str = Depends(validate_api_key)):
       # Process agent query
       pass
   ```

2. **Input Validation**:
   - Validate all user inputs
   - Use schema validation for API requests
   - Sanitize inputs to prevent injection attacks

   ```python
   from pydantic import BaseModel, validator
   
   class QueryRequest(BaseModel):
       text: str
       
       @validator('text')
       def validate_text(cls, value):
           if len(value) > 1000:
               raise ValueError("Query text too long")
           if value.strip() == "":
               raise ValueError("Query text cannot be empty")
           return value
   
   @app.post("/agent/query")
   async def query_agent(query: QueryRequest, api_key: str = Depends(validate_api_key)):
       # Process validated query
       pass
   ```

### Data Protection

1. **Sensitive Data Handling**:
   - Implement memory filtering for sensitive data
   - Use encryption for data at rest and in transit
   - Define data retention policies

   ```python
   class SecureMemory(SemanticMemory):
       """Memory implementation with sensitive data filtering."""
       
       def __init__(self, persistence, namespace, sensitive_patterns=None):
           super().__init__(persistence, namespace)
           self.sensitive_patterns = sensitive_patterns or [
               r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
               r'\b\d{16}\b',              # Credit card
               r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
           ]
       
       async def save(self, data):
           """Filter sensitive data before saving."""
           import re
           
           # Check if data contains content to filter
           if "content" in data:
               content = data["content"]
               # Apply each pattern
               for pattern in self.sensitive_patterns:
                   content = re.sub(pattern, "[REDACTED]", content)
               data["content"] = content
           
           return await super().save(data)
   ```

2. **Memory Security**:
   - Implement access controls for memory components
   - Create separate memory namespaces for different users/contexts
   - Encrypt sensitive memory entries

   ```python
   from cryptography.fernet import Fernet

   class EncryptedPersistence(BasePersistence):
       """Persistence layer with encryption."""
       
       def __init__(self, base_persistence, encryption_key=None):
           self.base_persistence = base_persistence
           if encryption_key is None:
               encryption_key = os.getenv("ENCRYPTION_KEY")
               if encryption_key is None:
                   encryption_key = Fernet.generate_key()
           self.cipher = Fernet(encryption_key)
       
       async def initialize(self):
           return await self.base_persistence.initialize()
       
       async def save(self, namespace, data):
           """Encrypt data before saving."""
           import json
           serialized = json.dumps(data)
           encrypted = self.cipher.encrypt(serialized.encode())
           return await self.base_persistence.save(namespace, {
               "encrypted_data": encrypted.decode()
           })
       
       async def retrieve(self, namespace, query, limit=10):
           """Decrypt data after retrieval."""
           results = await self.base_persistence.retrieve(namespace, query, limit)
           decrypted_results = []
           for item in results:
               if "encrypted_data" in item:
                   decrypted = self.cipher.decrypt(item["encrypted_data"].encode())
                   decrypted_data = json.loads(decrypted.decode())
                   decrypted_data["id"] = item.get("id")
                   decrypted_results.append(decrypted_data)
           return decrypted_results
   ```

### Tool Security

1. **Tool Access Control**:
   - Implement permission-based tool access
   - Validate tool inputs carefully
   - Apply rate limiting to tool executions

   ```python
   class SecureToolProvider(BaseToolProvider):
       """Tool provider with enhanced security."""
       
       def __init__(self, base_provider, permissions=None, rate_limits=None):
           self.base_provider = base_provider
           self.permissions = permissions or {}  # Tool -> allowed roles
           self.rate_limits = rate_limits or {}  # Tool -> max calls per minute
           self.call_history = {}  # Tool -> list of timestamps
       
       async def execute_tool(self, tool_name, user_role=None, **params):
           """Execute tool with security checks."""
           # Check permissions
           if tool_name in self.permissions:
               allowed_roles = self.permissions[tool_name]
               if user_role not in allowed_roles:
                   return {"error": f"Access denied: {tool_name} requires one of {allowed_roles}"}
           
           # Check rate limits
           if tool_name in self.rate_limits:
               max_calls = self.rate_limits[tool_name]
               if tool_name not in self.call_history:
                   self.call_history[tool_name] = []
               
               # Clean up old calls (older than 1 minute)
               import time
               now = time.time()
               self.call_history[tool_name] = [
                   t for t in self.call_history[tool_name] 
                   if now - t < 60
               ]
               
               # Check if under limit
               if len(self.call_history[tool_name]) >= max_calls:
                   return {"error": f"Rate limit exceeded for tool: {tool_name}"}
               
               # Record this call
               self.call_history[tool_name].append(now)
           
           # Execute the tool
           return await self.base_provider.execute_tool(tool_name, **params)
   ```

## Monitoring and Logging Setup

### Comprehensive Logging

1. **Configure Structured Logging**:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "agent_id"):
            log_record["agent_id"] = record.agent_id
        
        return json.dumps(log_record)

# Configure logging
def setup_logging(log_file=None):
    logger = logging.getLogger("agent_patterns")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # Create file handler if log file provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    return logger
```

2. **Create Agent Execution Logs**:

```python
class LoggingAgent(BaseAgent):
    """Agent with enhanced logging capabilities."""
    
    def __init__(self, logger=None, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger or logging.getLogger("agent_patterns")
        self.agent_id = str(uuid.uuid4())
    
    def run(self, query):
        """Run agent with logging."""
        self.logger.info(
            f"Starting agent execution", 
            extra={"agent_id": self.agent_id, "query": query}
        )
        
        start_time = time.time()
        try:
            result = super().run(query)
            execution_time = time.time() - start_time
            
            self.logger.info(
                f"Agent execution completed successfully",
                extra={
                    "agent_id": self.agent_id,
                    "execution_time": execution_time,
                    "result_length": len(result) if isinstance(result, str) else 0
                }
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Agent execution failed: {str(e)}",
                exc_info=True,
                extra={"agent_id": self.agent_id, "execution_time": execution_time}
            )
            raise
```

### Metrics Collection

1. **Prometheus Integration**:

```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
AGENT_RUNS = Counter(
    'agent_patterns_runs_total',
    'Total number of agent runs',
    ['agent_type', 'status']
)

AGENT_DURATION = Histogram(
    'agent_patterns_duration_seconds',
    'Duration of agent runs',
    ['agent_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

LLM_CALLS = Counter(
    'agent_patterns_llm_calls_total',
    'Total number of LLM API calls',
    ['model_provider', 'model_name', 'status']
)

TOOL_CALLS = Counter(
    'agent_patterns_tool_calls_total',
    'Total number of tool calls',
    ['tool_name', 'status']
)

MEMORY_OPERATIONS = Counter(
    'agent_patterns_memory_operations_total',
    'Total number of memory operations',
    ['operation', 'memory_type', 'status']
)

# Start metrics server
start_http_server(8000)  # Metrics exposed on http://localhost:8000
```

2. **Instrumented Agent**:

```python
class MetricsAgent(BaseAgent):
    """Agent with metrics instrumentation."""
    
    def run(self, query):
        """Run agent with metrics collection."""
        agent_type = self.__class__.__name__
        
        # Use metrics context manager for timing
        with AGENT_DURATION.labels(agent_type).time():
            try:
                result = super().run(query)
                AGENT_RUNS.labels(agent_type, "success").inc()
                return result
            except Exception as e:
                AGENT_RUNS.labels(agent_type, "failure").inc()
                raise
    
    async def _call_llm(self, prompt, model_config_key="default"):
        """Call LLM with metrics."""
        model_config = self.llm_configs.get(model_config_key, {})
        provider = model_config.get("provider", "unknown")
        model_name = model_config.get("model_name", "unknown")
        
        try:
            result = await super()._call_llm(prompt, model_config_key)
            LLM_CALLS.labels(provider, model_name, "success").inc()
            return result
        except Exception as e:
            LLM_CALLS.labels(provider, model_name, "failure").inc()
            raise
```

### Health Checks

1. **Agent Health Endpoints**:

```python
from fastapi import FastAPI
import psutil

app = FastAPI()

@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "ok"}

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check with system metrics."""
    return {
        "status": "ok",
        "memory_usage": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "cpu_usage": psutil.cpu_percent(interval=1),
        "disk_usage": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        },
        "active_agents": len(agents)  # Assuming you track active agents
    }

@app.get("/health/agent/{agent_id}")
async def agent_health(agent_id: str):
    """Check specific agent health."""
    if agent_id not in agents:
        return {"status": "not_found"}
    
    # Agent-specific health information
    return {
        "status": "ok",
        "agent_type": agents[agent_id].__class__.__name__,
        "memory_usage": get_agent_memory_usage(agent_id),
        "last_active": get_agent_last_active(agent_id)
    }
```

## Cost Optimization Strategies

### Model Selection Optimization

1. **Tiered Model Strategy**:

```python
class TieredAgent(BaseAgent):
    """Agent that uses different models based on complexity."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.complexity_threshold = kwargs.get("complexity_threshold", 0.7)
    
    def run(self, query):
        """Run with model selection based on complexity."""
        # Assess query complexity
        complexity = self._assess_complexity(query)
        
        # Select model based on complexity
        if complexity > self.complexity_threshold:
            # Use powerful model for complex queries
            self.current_model = "advanced"
        else:
            # Use efficient model for simple queries
            self.current_model = "basic"
        
        return super().run(query)
    
    async def _call_llm(self, prompt, model_config_key="default"):
        """Override to use current model selection."""
        # Use the currently selected model
        return await super()._call_llm(prompt, self.current_model)
    
    def _assess_complexity(self, query):
        """Assess query complexity (0-1 scale)."""
        # Simple heuristic: longer queries tend to be more complex
        import re
        
        # Count tokens (approximation)
        tokens = re.findall(r'\b\w+\b', query)
        token_count = len(tokens)
        
        # Check for indicators of complexity
        has_math = bool(re.search(r'[+\-*/^()=]', query))
        has_logic = bool(re.search(r'\b(if|then|else|and|or|not)\b', query.lower()))
        has_comparison = bool(re.search(r'(greater|less|equal|more|fewer)', query.lower()))
        
        # Calculate complexity score
        complexity = min(1.0, (
            (token_count / 100) * 0.5 +
            (0.2 if has_math else 0) +
            (0.15 if has_logic else 0) +
            (0.15 if has_comparison else 0)
        ))
        
        return complexity
```

2. **Model Caching**:

```python
class CachingLLMService:
    """Service with response caching for cost optimization."""
    
    def __init__(self, cache_ttl=3600):
        self.cache = {}
        self.cache_ttl = cache_ttl  # seconds
    
    async def call_llm(self, provider, model, prompt):
        """Call LLM with caching."""
        import hashlib
        import time
        
        # Generate cache key
        cache_key = hashlib.md5(f"{provider}:{model}:{prompt}".encode()).hexdigest()
        
        # Check cache
        current_time = time.time()
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            # Check if cache is still valid
            if current_time - entry["timestamp"] < self.cache_ttl:
                return entry["response"]
        
        # Call LLM
        if provider == "openai":
            response = await self._call_openai(model, prompt)
        elif provider == "anthropic":
            response = await self._call_anthropic(model, prompt)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Cache response
        self.cache[cache_key] = {
            "response": response,
            "timestamp": current_time
        }
        
        return response
    
    def _call_openai(self, model, prompt):
        """Call OpenAI API."""
        # Implementation details...
        pass
    
    def _call_anthropic(self, model, prompt):
        """Call Anthropic API."""
        # Implementation details...
        pass
```

### Input Preprocessing

1. **Query Optimization**:

```python
def optimize_query(query):
    """Optimize query before sending to LLM."""
    import re
    
    # Remove redundant whitespace
    query = re.sub(r'\s+', ' ', query).strip()
    
    # Truncate very long queries
    if len(query) > 1000:
        query = query[:997] + "..."
    
    # Remove redundant instructions
    common_prefixes = [
        "I want you to", 
        "Please", 
        "Can you", 
        "I'd like you to",
        "I need you to"
    ]
    
    for prefix in common_prefixes:
        if query.lower().startswith(prefix.lower()):
            query = query[len(prefix):].strip()
    
    return query
```

2. **Context Pruning**:

```python
class ContextOptimizer:
    """Optimizes agent context to reduce token usage."""
    
    def optimize_memory_context(self, memories, query, max_tokens=1000):
        """Prune and optimize memory context."""
        from agent_patterns.core.utils.tokenizer import count_tokens
        
        # Sort memories by relevance
        sorted_memories = sorted(
            memories, 
            key=lambda x: x.get("relevance", 0), 
            reverse=True
        )
        
        # Calculate query tokens
        query_tokens = count_tokens(query)
        available_tokens = max_tokens - query_tokens
        
        # Select most relevant memories
        selected_memories = []
        current_tokens = 0
        
        for memory in sorted_memories:
            # Convert memory to string representation
            memory_str = str(memory.get("content", ""))
            memory_tokens = count_tokens(memory_str)
            
            # Check if adding this memory exceeds token limit
            if current_tokens + memory_tokens > available_tokens:
                continue
            
            selected_memories.append(memory)
            current_tokens += memory_tokens
        
        return selected_memories
```

### Batch Processing

1. **Agent Batching**:

```python
class BatchProcessor:
    """Process multiple queries in batches for efficiency."""
    
    def __init__(self, agent_class, batch_size=5, **agent_kwargs):
        self.agent_class = agent_class
        self.agent_kwargs = agent_kwargs
        self.batch_size = batch_size
        self.query_queue = []
        self.results = {}
    
    async def add_query(self, query_id, query):
        """Add query to processing queue."""
        self.query_queue.append((query_id, query))
        
        # Process batch if queue is full
        if len(self.query_queue) >= self.batch_size:
            await self.process_batch()
    
    async def process_batch(self):
        """Process a batch of queries."""
        if not self.query_queue:
            return
        
        # Create agent instance
        agent = self.agent_class(**self.agent_kwargs)
        
        # Process each query
        batch = self.query_queue[:self.batch_size]
        self.query_queue = self.query_queue[self.batch_size:]
        
        for query_id, query in batch:
            try:
                result = agent.run(query)
                self.results[query_id] = {
                    "status": "success",
                    "result": result
                }
            except Exception as e:
                self.results[query_id] = {
                    "status": "error",
                    "error": str(e)
                }
    
    async def get_result(self, query_id):
        """Get result for a specific query."""
        return self.results.get(query_id, {"status": "not_found"})
```

## Production Configuration Recommendations

### Environment Configuration

Example production `.env` file:

```
# API Keys (use environment variables in production)
OPENAI_API_KEY=<from-environment>
ANTHROPIC_API_KEY=<from-environment>

# Model Configuration
DEFAULT_MODEL_PROVIDER=openai
DEFAULT_MODEL_NAME=gpt-4o-mini
ADVANCED_MODEL_PROVIDER=anthropic
ADVANCED_MODEL_NAME=claude-3-opus-20240229

# Security
ENCRYPTION_KEY=<from-environment>
API_KEY=<from-environment>

# Memory Configuration
MEMORY_PERSISTENCE_TYPE=vector_db
PINECONE_API_KEY=<from-environment>
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX=production-agent-memory

# Logging & Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
METRICS_PORT=9090

# Scaling Configuration
AGENT_CONCURRENCY=10
TOOL_TIMEOUT=30
MEMORY_CACHE_TTL=3600
LLM_CACHE_TTL=300
```

### Docker Deployment

Example `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Example `docker-compose.yml` for complete deployment:

```yaml
version: '3'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - API_KEY=${API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - LOG_LEVEL=INFO
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
  
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  redis-data:
  prometheus-data:
  grafana-data:
```

### Kubernetes Configuration

Example Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-patterns-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-patterns-api
  template:
    metadata:
      labels:
        app: agent-patterns-api
    spec:
      containers:
      - name: api
        image: your-registry/agent-patterns-api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-api-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: anthropic-api-key
        - name: DEFAULT_MODEL_PROVIDER
          value: "openai"
        - name: DEFAULT_MODEL_NAME
          value: "gpt-4o-mini"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: agent-patterns-api
spec:
  selector:
    app: agent-patterns-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent-patterns-api-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: agent-patterns-api
            port:
              number: 80
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: tls-secret
```

### Serverless Deployment

Example AWS Lambda integration:

```python
from agent_patterns.patterns.re_act_agent import ReActAgent
import os
import json

# Initialize agent outside handler for container reuse
agent = ReActAgent(
    llm_configs={
        "default": {
            "provider": os.getenv("DEFAULT_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("DEFAULT_MODEL_NAME", "gpt-4o-mini")
        }
    }
)

def lambda_handler(event, context):
    """AWS Lambda handler."""
    try:
        # Extract query from event
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Query is required'})
            }
        
        # Run agent
        result = agent.run(query)
        
        # Return response
        return {
            'statusCode': 200,
            'body': json.dumps({'result': result})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```