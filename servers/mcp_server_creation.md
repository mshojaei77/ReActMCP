# Building a Model Context Protocol (MCP) Server

This guide will walk you through the process of creating a Model Context Protocol (MCP) server, which allows LLMs like Claude to interact with external systems and data.

## Prerequisites

- Python 3.7+
- Basic knowledge of async Python
- Understanding of MCP concepts ([modelcontextprotocol.io](https://modelcontextprotocol.io))

## Step 1: Create your server file

Create a new Python file (e.g., `my_server.py`) in servers directory with the following structure:

```python
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(override=True)

# Initialize your MCP server
mcp = FastMCP(
    name="my-server",
    version="1.0.0",
    description="Description of your server's capabilities and purpose"
)

# Define tools and resources here

if __name__ == "__main__":
    print(f"Running {mcp.name} MCP server...")
    mcp.run()
```

## Step 3: Configure external services

If your server needs to interact with external APIs or services, configure them:

```python
# Example: Setting up an API client
api_key = os.getenv("API_KEY")
client = SomeAPIClient(api_key=api_key)

# Set up default configuration
config = {
    "parameters": {
        "default_option": "value",
        "other_setting": True
    }
}
```

## Step 4: Define MCP tools

Tools are functions that LLMs can call. Define them with the `@mcp.tool()` decorator:

```python
@mcp.tool()
async def my_tool(param1: str, param2: int = None) -> str:
    """Describe what your tool does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
    
    Returns:
        Description of the return value
    """
    try:
        # Tool implementation
        result = await do_something(param1, param2)
        return format_result(result)
    except Exception as e:
        return f"An error occurred: {e}"
```

## Step 5: Create helper functions

Break down complex functionality into helper functions:

```python
def format_result(result):
    """Format the result in a user-friendly way.
    
    Args:
        result: Raw result from your operation
        
    Returns:
        Formatted string, often using markdown
    """
    # Formatting logic
    return formatted_output
```

## Step 6: Add testing functions

Create testing functions to verify your server works correctly:

```python
async def test_my_tool():
    print("Testing my_tool...")
    result = await my_tool("test", 42)
    print(result)
    
    # Test edge cases
    error_result = await my_tool("", -1)
    print(error_result)
```

## Step 7: Run your server

Add code to run your server or tests:

```python
if __name__ == "__main__":
    import asyncio
    
    # For testing:
    # asyncio.run(test_my_tool())
    
    # For production:
    print(f"Running {mcp.name} MCP server...")
    mcp.run()
```

## Example: Web Search MCP Server

Here's a simplified example of a web search server using the Exa API:

```python
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import List
import os
from exa_py import Exa

load_dotenv(override=True)

# Initialize MCP server
mcp = FastMCP(
    name="websearch", 
    version="1.0.0",
    description="Web search capability using Exa API"
)

# Initialize Exa client
exa_api_key = os.getenv("EXA_API_KEY")
exa = Exa(api_key=exa_api_key)

# Define search tool
@mcp.tool()
async def search_web(query: str, num_results: int = 5) -> str:
    """Search the web using Exa API.
    
    Args:
        query: The search query
        num_results: Number of results to return
    
    Returns:
        Search results formatted in markdown
    """
    try:
        search_results = exa.search_and_contents(
            query, 
            num_results=num_results,
            summary={"query": "Main points and key takeaways"}
        )
        
        return format_search_results(search_results)
    except Exception as e:
        return f"An error occurred: {e}"

# Start the server
if __name__ == "__main__":
    mcp.run()
```

## Configuring MCP Server in Claude Desktop

To use your server with Claude Desktop:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["path/to/my_server.py"]
    }
  }
}
```

## Testing Your Server

Run your server with the test functions enabled to verify it works correctly before connecting it to Claude or other clients.

## Next Steps

- Visit [modelcontextprotocol.io](https://modelcontextprotocol.io) for comprehensive documentation
- Explore adding resources to expose structured data
- Add more complex tool implementations
- Add authentication if needed
- Deploy your server for production use

## Best Practices

1. Always add detailed docstrings to your tools
2. Implement robust error handling
3. Use type hints for tool parameters
4. Break down complex logic into helper functions
5. Create both simple and advanced versions of tools when appropriate
6. Test thoroughly before deployment

For more examples and documentation, visit the [MCP GitHub repository](https://github.com/modelcontextprotocol/servers).