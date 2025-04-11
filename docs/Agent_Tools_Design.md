# **Model Context Protocol (MCP) Integration Design for Agent-Patterns**

**Version:** 1.0  
 **Date:** April 10, 2025  
 **Author:** Agent-Patterns Team

---

## **1\. Overview**

This design document outlines the integration of Model Context Protocol (MCP) into the agent-patterns library. MCP is an open standard developed by Anthropic that standardizes how AI models connect with external tools and data sources. This integration will enable agents built with our library to leverage any MCP-compatible server, providing access to a wide ecosystem of tools without having to implement custom integrations for each one.

## **2\. Design Goals**

1. **Extensibility**: Support MCP-based tools while maintaining the ability to use other tool integration approaches  
2. **Separation of Concerns**: Keep agent logic separate from tool implementation details  
3. **Ease of Use**: Provide a simple, intuitive interface for connecting MCP servers to agents  
4. **Performance**: Minimize overhead when making tool calls  
5. **Flexibility**: Allow for different MCP server implementations (local, remote, etc.)

## **3\. Architecture**

### **3.1 Core Components**

1. **ToolProvider Interface**: An abstract interface that defines how agents interact with tools  
2. **MCPToolProvider**: An implementation of the ToolProvider interface that connects to MCP servers  
3. **MCPTool**: A representation of an individual tool from an MCP server  
4. **MCPServer Connection Manager**: Handles connections to MCP servers and caches tool definitions

### **3.2 Class Hierarchy**

core/  
  ├── tools/  
  │   ├── base.py                  \# Contains the ToolProvider ABC  
  │   ├── providers/  
  │   │   ├── \_\_init\_\_.py  
  │   │   ├── mcp\_provider.py      \# MCP-specific implementation  
  │   │   └── ... (other providers)  
  │   └── registry.py              \# Optional global tool registry  
  └── ...

### **3.3 Key Interfaces**

#### **ToolProvider (Abstract Base Class)**

from abc import ABC, abstractmethod  
from typing import Dict, List, Any

class ToolProvider(ABC):  
    """Abstract interface for tool providers."""  
      
    @abstractmethod  
    def list\_tools(self) \-\> List\[Dict\]:  
        """  
        List available tools with their metadata.  
          
        Returns:  
            A list of tool specifications, each containing at minimum:  
            \- name: The tool's name  
            \- description: What the tool does  
            \- parameters: The expected input parameters  
        """  
        pass  
      
    @abstractmethod  
    def execute\_tool(self, tool\_name: str, params: Dict\[str, Any\]) \-\> Any:  
        """  
        Execute a tool with the given parameters.  
          
        Args:  
            tool\_name: The name of the tool to execute  
            params: The parameters to pass to the tool  
              
        Returns:  
            The result of the tool execution  
              
        Raises:  
            ToolNotFoundError: If the tool doesn't exist  
            ToolExecutionError: If the tool execution fails  
        """  
        pass

#### **MCPToolProvider (Implementation)**

from typing import Dict, List, Any, Optional  
from .base import ToolProvider

class MCPToolProvider(ToolProvider):  
    """MCP-based implementation of the ToolProvider interface."""  
      
    def \_\_init\_\_(self, mcp\_servers: List\[Any\], cache\_tools: bool \= True):  
        """  
        Initialize with a list of MCP server connections.  
          
        Args:  
            mcp\_servers: List of MCP server connections  
            cache\_tools: Whether to cache tool definitions (recommended for performance)  
        """  
        self.mcp\_servers \= mcp\_servers  
        self.cache\_tools \= cache\_tools  
        self.\_tools\_cache \= None if not cache\_tools else {}  
          
    def list\_tools(self) \-\> List\[Dict\]:  
        """Get tools from all connected MCP servers."""  
        if self.cache\_tools and self.\_tools\_cache is not None:  
            return self.\_tools\_cache  
              
        tools \= \[\]  
        for server in self.mcp\_servers:  
            tools.extend(server.list\_tools())  
              
        if self.cache\_tools:  
            self.\_tools\_cache \= tools  
              
        return tools  
      
    def execute\_tool(self, tool\_name: str, params: Dict\[str, Any\]) \-\> Any:  
        """Find the right MCP server and execute the tool."""  
        for server in self.mcp\_servers:  
            \# Check if this server has the requested tool  
            tools \= server.list\_tools()  
            if any(tool\["name"\] \== tool\_name for tool in tools):  
                return server.call\_tool(tool\_name, params)  
                  
        raise ToolNotFoundError(f"Tool '{tool\_name}' not found in any MCP server")  
          
    def invalidate\_cache(self):  
        """Invalidate the tools cache to force a refresh on next list\_tools call."""  
        self.\_tools\_cache \= None

## **4\. Integration with Agent Patterns**

### **4.1 BaseAgent Enhancement**

Modify the BaseAgent class to support tool providers:

class BaseAgent(abc.ABC):  
    def \_\_init\_\_(self,   
                 llm\_configs: dict,   
                 prompt\_dir: str \= "prompts",  
                 tool\_provider: Optional\[ToolProvider\] \= None):  
        """  
        Initialize the agent.  
          
        Args:  
            llm\_configs: Dictionary specifying provider, model, and roles  
            prompt\_dir: Directory for prompt templates  
            tool\_provider: Optional provider for tools the agent can use  
        """  
        self.llm\_configs \= llm\_configs  
        self.prompt\_dir \= prompt\_dir  
        self.tool\_provider \= tool\_provider  
        self.graph \= None  \# set by self.build\_graph()  
          
        \# Subclass is expected to build/compile its graph  
        self.build\_graph()

### **4.2 ReAct Pattern Update**

Modify the ReActAgent to leverage the tool provider:

def \_execute\_action(self, state: Dict) \-\> Dict:  
    """Call the actual tool with the specified input."""  
    action \= state\["action"\]  
    tool\_name \= action\["tool\_name"\]  
    tool\_input \= action\["tool\_input"\]  
      
    if self.tool\_provider:  
        \# Use the tool provider if available  
        try:  
            observation \= self.tool\_provider.execute\_tool(tool\_name, tool\_input)  
        except Exception as e:  
            observation \= f"Error executing tool: {str(e)}"  
    else:  
        \# Fall back to the legacy \_call\_tool method  
        observation \= self.\_call\_tool(tool\_name, tool\_input)  
          
    state\["observation"\] \= observation  
    \# Update the last step in intermediate\_steps with the observation  
    if state\["intermediate\_steps"\]:  
        last\_thought, last\_action, \_ \= state\["intermediate\_steps"\]\[-1\]  
        state\["intermediate\_steps"\]\[-1\] \= (last\_thought, last\_action, observation)  
    return state

### **4.3 Other Pattern Updates**

Apply similar updates to other patterns that use tools:

* `PlanAndSolveAgent`  
* `LLMCompilerAgent`  
* `REWOOAgent`  
* etc.

## **5\. MCP Server Connection Management**

### **5.1 Helper Functions**

def create\_mcp\_server\_connection(server\_type: str, config: Dict\[str, Any\]) \-\> Any:  
    """  
    Create a connection to an MCP server.  
      
    Args:  
        server\_type: The type of connection (stdio, sse, socket, etc.)  
        config: Configuration for the connection  
          
    Returns:  
        An MCP server connection object  
    """  
    if server\_type \== "stdio":  
        return create\_stdio\_connection(config)  
    elif server\_type \== "sse":  
        return create\_sse\_connection(config)  
    \# ... other connection types  
    else:  
        raise ValueError(f"Unknown MCP server type: {server\_type}")

### **5.2 Configuration**

Sample configuration for MCP servers:

mcp\_config \= {  
    "servers": \[  
        {  
            "type": "stdio",  
            "command": \["python", "mcp\_server.py"\],  
            "working\_dir": "/path/to/server",  
            "cache\_tools": True  
        },  
        {  
            "type": "sse",  
            "url": "http://localhost:3000/events",  
            "headers": {"Authorization": "Bearer token"}  
        }  
    \]  
}

## **6\. Usage Examples**

### **6.1 Basic Usage**

from agent\_patterns.patterns.re\_act\_agent import ReActAgent  
from agent\_patterns.core.tools.providers.mcp\_provider import MCPToolProvider, create\_mcp\_server\_connection

\# Create MCP server connections  
mcp\_servers \= \[  
    create\_mcp\_server\_connection("stdio", {  
        "command": \["python", "search\_server.py"\],  
        "working\_dir": "./mcp\_servers"  
    }),  
    create\_mcp\_server\_connection("stdio", {  
        "command": \["python", "weather\_server.py"\],  
        "working\_dir": "./mcp\_servers"  
    })  
\]

\# Create the tool provider  
tool\_provider \= MCPToolProvider(mcp\_servers)

\# Create the agent with the tool provider  
agent \= ReActAgent(  
    llm\_configs={  
        "thinking": {  
            "provider": "anthropic",  
            "model\_name": "claude-3-opus-20240229"  
        }  
    },  
    tool\_provider=tool\_provider  
)

\# Run the agent  
result \= agent.run("What's the weather like in New York?")  
print(result)

### **6.2 Environment Variables**

import os  
from dotenv import load\_dotenv

load\_dotenv()

\# Load MCP server configs from environment  
mcp\_servers \= \[\]  
for i in range(int(os.getenv("MCP\_SERVER\_COUNT", "0"))):  
    prefix \= f"MCP\_SERVER\_{i+1}\_"  
    server\_type \= os.getenv(f"{prefix}TYPE")  
    if server\_type \== "stdio":  
        mcp\_servers.append(create\_mcp\_server\_connection("stdio", {  
            "command": os.getenv(f"{prefix}COMMAND").split(),  
            "working\_dir": os.getenv(f"{prefix}WORKING\_DIR")  
        }))  
    \# ... other server types

## **7\. Testing**

### **7.1 Mock MCP Servers**

For testing, we'll provide mock MCP servers that implement the protocol but return predictable results:

class MockMCPServer:  
    def \_\_init\_\_(self, tools: List\[Dict\]):  
        self.tools \= tools  
          
    def list\_tools(self) \-\> List\[Dict\]:  
        return self.tools  
          
    def call\_tool(self, tool\_name: str, params: Dict\[str, Any\]) \-\> Any:  
        for tool in self.tools:  
            if tool\["name"\] \== tool\_name:  
                \# Return a mock response  
                return f"Mock response for {tool\_name} with params {params}"  
                  
        raise Exception(f"Tool {tool\_name} not found")

### **7.2 Unit Tests**

def test\_mcp\_tool\_provider():  
    \# Create mock MCP servers  
    mock\_servers \= \[  
        MockMCPServer(\[  
            {"name": "search", "description": "Search the web", "parameters": {"query": "string"}}  
        \]),  
        MockMCPServer(\[  
            {"name": "weather", "description": "Get weather", "parameters": {"location": "string"}}  
        \])  
    \]  
      
    \# Create the tool provider  
    provider \= MCPToolProvider(mock\_servers)  
      
    \# Test list\_tools  
    tools \= provider.list\_tools()  
    assert len(tools) \== 2  
    assert tools\[0\]\["name"\] \== "search"  
    assert tools\[1\]\["name"\] \== "weather"  
      
    \# Test execute\_tool  
    result \= provider.execute\_tool("search", {"query": "test"})  
    assert "Mock response for search" in result  
      
    \# Test tool not found  
    with pytest.raises(ToolNotFoundError):  
        provider.execute\_tool("nonexistent", {})

## **8\. Future Enhancements**

1. **Auto-Discovery**: Add support for auto-discovering MCP servers on the local network  
2. **Authentication**: Enhance security with robust authentication mechanisms  
3. **Tool Filtering**: Allow agents to filter available tools based on capabilities or permissions  
4. **Parallel Execution**: Support executing tools from multiple MCP servers in parallel  
5. **Observability**: Add metrics and tracing for tool executions

## **9\. Conclusion**

This design provides a flexible, modular approach to integrating MCP servers with the agent-patterns library. By leveraging the ToolProvider abstraction, we maintain separation between agent logic and tool implementation details, allowing for easy integration of MCP while still supporting other tool integration approaches.

The proposed architecture ensures that agents can leverage the growing ecosystem of MCP-compatible tools without tight coupling to specific implementations. This design aligns with the overall philosophy of agent-patterns, providing reusable, extensible patterns for AI agent workflows.
