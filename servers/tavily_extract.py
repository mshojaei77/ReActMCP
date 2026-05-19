from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
from typing import List, Optional

# Try to import tavily library, providing helpful error if not installed
try:
    from tavily import TavilyClient
except ImportError:
    raise ImportError(
        "The tavily-python package is required. Please install it with 'pip install tavily-python'"
    )

# Load environment variables
load_dotenv(override=True)

# Initialize the MCP server
mcp = FastMCP(
    name="tavily_extract",
    version="1.0.0",
    description="URL content extraction using Tavily Extract API"
)

# Get API key from environment
api_key = os.getenv("TAVILY_API_KEY")
tavily_client = None  # Will be initialized when needed


def get_tavily_client():
    """Get or initialize the TavilyClient instance."""
    global tavily_client, api_key

    if tavily_client is None:
        if api_key is None:
            raise ValueError(
                "TAVILY_API_KEY environment variable not set. "
                "Please set this variable in a .env file or system environment."
            )
        tavily_client = TavilyClient(api_key=api_key)

    return tavily_client


def format_extract_result(result):
    """Format extracted content with metadata for better readability."""
    results = result.get("results", [])
    if not results:
        failed = result.get("failed_results", [])
        if failed:
            urls = ", ".join(f.get("url", "unknown") for f in failed)
            return f"Error: Failed to extract content from: {urls}"
        return "Error: No content was extracted."

    formatted_parts = []
    for item in results:
        url = item.get("url", "Unknown")
        raw_content = item.get("raw_content", "")

        part = f"# Extracted Content\n\n"
        part += f"**Source URL:** {url}\n\n"
        part += "---\n\n"
        part += raw_content

        formatted_parts.append(part)

    return "\n\n---\n\n".join(formatted_parts)


@mcp.tool()
async def extract_url_content(
    urls: List[str],
    query: Optional[str] = None,
    chunks_per_source: int = 3
) -> str:
    """Extract content from one or more URLs using Tavily Extract API.

    Args:
        urls: List of URLs to extract content from (max 20)
        query: Optional query to rerank extracted chunks by relevance
        chunks_per_source: Number of content chunks per source (1-5, default: 3)

    Returns:
        The extracted content in a readable format with metadata
    """
    try:
        client = get_tavily_client()

        kwargs = {"urls": urls}
        if query:
            kwargs["query"] = query
        if chunks_per_source:
            kwargs["chunks_per_source"] = chunks_per_source

        result = client.extract(**kwargs)

        return format_extract_result(result)
    except Exception as e:
        url_list = ", ".join(urls)
        return f"An error occurred while extracting content from {url_list}: {str(e)}"


# Run the server
if __name__ == "__main__":
    print(f"Running {mcp.name} MCP server...")
    mcp.run()
