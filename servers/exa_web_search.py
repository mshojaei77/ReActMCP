
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import List
import os
from exa_py import Exa 

load_dotenv(override=True)


mcp = FastMCP(
    name="websearch", 
    version="1.0.0",
    description="Web search capability using Exa API that provides real-time internet search results. Supports both basic and advanced search with filtering options including domain restrictions, text inclusion requirements, and date filtering. Returns formatted results with titles, URLs, publication dates, and content summaries."
)

# Initialize the Exa client
exa_api_key = os.getenv("EXA_API_KEY")
exa = Exa(api_key=exa_api_key)

# Default search configuration
websearch_config = {
    "parameters": {
        "default_num_results": 5,
        "include_domains": []  # Empty list by default
    }
}

@mcp.tool()
async def search_web(query: str, num_results: int = None) -> str:
    """Search the web using Exa API and return results as markdown formatted text.
    
    Args:
        query: The search query
        num_results: Optional number of results to return (overrides config)
    
    Returns:
        Search results formatted in markdown
    """
    try:
        # Use parameters from config
        search_args = {
            "num_results": num_results or websearch_config["parameters"]["default_num_results"]
        }
        
        # Request summaries using search_and_contents instead of basic search
        search_results = exa.search_and_contents(
            query, 
            summary={"query": "Main points and key takeaways"},
            **search_args
        )
        
        return format_search_results(search_results)
    except Exception as e:
        return f"An error occurred while searching with Exa: {e}"

@mcp.tool()
async def advanced_search_web(
    query: str, 
    num_results: int = None, 
    include_domains: List[str] = None, 
    include_text: str = None,
    max_age_days: int = None
) -> str:
    """Advanced web search using Exa API with additional filtering options.
    
    Args:
        query: The search query
        num_results: Optional number of results to return (overrides config)
        include_domains: List of domains to include in search results
        include_text: Text that must be included in the search results
        max_age_days: Maximum age of results in days
        
    Returns:
        Search results formatted in markdown
    """
    try:
        # Use parameters from config and override with provided parameters
        search_args = {
            "num_results": num_results or websearch_config["parameters"]["default_num_results"]
        }
        
        # Add domain filters if specified
        if include_domains:
            search_args["include_domains"] = include_domains
        elif websearch_config["parameters"]["include_domains"]:
            search_args["include_domains"] = websearch_config["parameters"]["include_domains"]
            
        # Add include_text if specified
        if include_text:
            search_args["include_text"] = [include_text]
            
        # Add max age filter if specified
        if max_age_days:
            from datetime import datetime, timedelta
            start_date = (datetime.now() - timedelta(days=max_age_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
            search_args["start_published_date"] = start_date
        
        # Request summaries using search_and_contents
        search_results = exa.search_and_contents(
            query, 
            summary={"query": "Main points and key takeaways"},
            **search_args
        )
        
        return format_search_results(search_results)
    except Exception as e:
        return f"An error occurred while searching with Exa: {e}"

def format_search_results(search_results):
    """Format search results into markdown.
    
    Args:
        search_results: Results from Exa search
        
    Returns:
        Formatted markdown string
    """
    if not search_results.results:
        return "No results found."

    # Format the results in Markdown
    markdown_results = "### Search Results:\n\n"
    for idx, result in enumerate(search_results.results, 1):
        title = result.title if hasattr(result, 'title') and result.title else "No title"
        url = result.url
        published_date = f" (Published: {result.published_date})" if hasattr(result, 'published_date') and result.published_date else ""
        
        markdown_results += f"**{idx}.** [{title}]({url}){published_date}\n"
        
        # Add summary if available
        if hasattr(result, 'summary') and result.summary:
            markdown_results += f"> **Summary:** {result.summary}\n\n"
        else:
            markdown_results += "\n"
    
    return markdown_results

# Test function
async def test_search():
    query = 'latest AI developments'
    print(f"Searching for: {query}")
    results = await search_web(query)
    print(results)
    
    # Test advanced search
    print("\nTesting advanced search:")
    advanced_results = await advanced_search_web(
        query="gemma 3", 
        include_text="open source", 
        max_age_days=30
    )
    print(advanced_results)

if __name__ == "__main__":
    import asyncio
    # Test the search function
    #asyncio.run(test_search())
    
    # Comment out the line below when testing directly
    print("Running Exa Web Search MCP server...")
    mcp.run()