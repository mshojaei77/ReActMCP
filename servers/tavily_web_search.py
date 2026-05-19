
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import List
import os
from tavily import TavilyClient

load_dotenv(override=True)


mcp = FastMCP(
    name="tavily_websearch",
    version="1.0.0",
    description="Web search capability using Tavily API that provides real-time internet search results. Supports both basic and advanced search with filtering options including domain restrictions and date filtering. Returns formatted results with titles, URLs, and content summaries."
)

# Initialize the Tavily client
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=tavily_api_key)

# Default search configuration
websearch_config = {
    "parameters": {
        "default_num_results": 5,
        "include_domains": []  # Empty list by default
    }
}

@mcp.tool()
async def search_web_tavily(query: str, num_results: int = None) -> str:
    """Search the web using Tavily API and return results as markdown formatted text.

    Args:
        query: The search query
        num_results: Optional number of results to return (overrides config)

    Returns:
        Search results formatted in markdown
    """
    try:
        results = tavily.search(
            query=query,
            max_results=num_results or websearch_config["parameters"]["default_num_results"],
            search_depth="advanced",
        )

        return format_search_results(results)
    except Exception as e:
        return f"An error occurred while searching with Tavily: {e}"

@mcp.tool()
async def advanced_search_web_tavily(
    query: str,
    num_results: int = None,
    include_domains: List[str] = None,
    exclude_domains: List[str] = None,
    max_age_days: int = None
) -> str:
    """Advanced web search using Tavily API with additional filtering options.

    Args:
        query: The search query
        num_results: Optional number of results to return (overrides config)
        include_domains: List of domains to include in search results
        exclude_domains: List of domains to exclude from search results
        max_age_days: Maximum age of results in days

    Returns:
        Search results formatted in markdown
    """
    try:
        search_args = {
            "query": query,
            "max_results": num_results or websearch_config["parameters"]["default_num_results"],
            "search_depth": "advanced",
        }

        # Add domain filters if specified
        if include_domains:
            search_args["include_domains"] = include_domains
        elif websearch_config["parameters"]["include_domains"]:
            search_args["include_domains"] = websearch_config["parameters"]["include_domains"]

        if exclude_domains:
            search_args["exclude_domains"] = exclude_domains

        # Add time range filter if specified
        if max_age_days:
            if max_age_days <= 1:
                search_args["time_range"] = "day"
            elif max_age_days <= 7:
                search_args["time_range"] = "week"
            elif max_age_days <= 30:
                search_args["time_range"] = "month"
            else:
                search_args["time_range"] = "year"

        results = tavily.search(**search_args)

        return format_search_results(results)
    except Exception as e:
        return f"An error occurred while searching with Tavily: {e}"

def format_search_results(response):
    """Format search results into markdown.

    Args:
        response: Results from Tavily search

    Returns:
        Formatted markdown string
    """
    results = response.get("results", [])
    if not results:
        return "No results found."

    # Format the results in Markdown
    markdown_results = "### Search Results:\n\n"
    for idx, result in enumerate(results, 1):
        title = result.get("title", "No title")
        url = result.get("url", "")

        markdown_results += f"**{idx}.** [{title}]({url})\n"

        # Add content snippet if available
        content = result.get("content")
        if content:
            markdown_results += f"> **Summary:** {content}\n\n"
        else:
            markdown_results += "\n"

    return markdown_results

if __name__ == "__main__":
    print("Running Tavily Web Search MCP server...")
    mcp.run()
