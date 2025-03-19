from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional
import json
from pydantic import BaseModel

# Try to import firecrawl library, providing helpful error if not installed
try:
    from firecrawl import FirecrawlApp
except ImportError:
    raise ImportError(
        "The firecrawl package is required. Please install it with 'pip install firecrawl-py'"
    )

# Load environment variables
load_dotenv(override=True)

# Initialize the MCP server
mcp = FastMCP(
    name="firecrawl",
    version="1.0.0",
    description="Web scraping, crawling, and data extraction using Firecrawl API"
)

# Get API key from environment, with fallback to requesting it
api_key = os.getenv("FIRECRAWL_API_KEY")
firecrawl_app = None  # Will be initialized when needed

def get_firecrawl_app():
    """Get or initialize the FirecrawlApp instance."""
    global firecrawl_app, api_key
    
    if firecrawl_app is None:
        if api_key is None:
            raise ValueError(
                "FIRECRAWL_API_KEY environment variable not set. "
                "Please set this variable in a .env file or system environment."
            )
        firecrawl_app = FirecrawlApp(api_key=api_key)
    
    return firecrawl_app

# Helper function to format markdown content with metadata
def format_markdown_with_metadata(response):
    """Format markdown content with metadata for better readability."""
    if not response.get('success'):
        return f"Error: Failed to retrieve data. {response.get('error', '')}"
    
    data = response.get('data', {})
    markdown = data.get('markdown', '')
    metadata = data.get('metadata', {})
    
    formatted_result = f"# {metadata.get('title', 'Scraped Content')}\n\n"
    
    if metadata.get('description'):
        formatted_result += f"*{metadata.get('description')}*\n\n"
    
    formatted_result += f"**Source URL:** {metadata.get('sourceURL', 'Unknown')}\n\n"
    formatted_result += "---\n\n"
    formatted_result += markdown
    
    return formatted_result

# Helper function to format crawl status
def format_crawl_status(status):
    """Format crawl status information in a readable way."""
    if not status:
        return "Error: Failed to retrieve crawl status."
    
    formatted_status = f"# Crawl Status\n\n"
    formatted_status += f"**Current Status:** {status.get('status', 'Unknown')}\n"
    formatted_status += f"**Total Pages:** {status.get('totalCount', 0)}\n"
    formatted_status += f"**Credits Used:** {status.get('creditsUsed', 0)}\n"
    
    if status.get('expiresAt'):
        formatted_status += f"**Expires At:** {status.get('expiresAt')}\n"
    
    if status.get('data') and isinstance(status.get('data'), list):
        formatted_status += f"\n## Crawled Pages: {len(status.get('data'))}\n\n"
        for idx, page in enumerate(status.get('data')):
            metadata = page.get('metadata', {})
            formatted_status += f"{idx+1}. **{metadata.get('title', 'Unknown Title')}**\n"
            formatted_status += f"   URL: {metadata.get('sourceURL', 'Unknown URL')}\n"
    
    return formatted_status

# Helper function to format mapped links
def format_mapped_links(map_result):
    """Format mapped links in a readable way."""
    if not map_result.get('success'):
        return f"Error: Failed to map the website. {map_result.get('error', '')}"
    
    links = map_result.get('links', [])
    
    formatted_result = f"# Website Map Results\n\n"
    formatted_result += f"Found {len(links)} links:\n\n"
    
    for idx, link in enumerate(links):
        formatted_result += f"{idx+1}. {link}\n"
    
    return formatted_result

@mcp.tool()
async def scrape_url(url: str, formats: List[str] = ["markdown"]) -> str:
    """Scrape a single web page and return its content.
    
    Args:
        url: The URL of the web page to scrape
        formats: List of formats to return (default: ["markdown"])
    
    Returns:
        The scraped content in markdown format with metadata
    """
    try:
        app = get_firecrawl_app()
        response = app.scrape_url(url=url, params={
            'formats': formats,
        })
        
        return format_markdown_with_metadata(response)
    except Exception as e:
        return f"An error occurred while scraping {url}: {str(e)}"

@mcp.tool()
async def crawl_website(
    url: str, 
    limit: int = 10, 
    max_depth: int = 2, 
    formats: List[str] = ["markdown"]
) -> str:
    """Start a crawl job on a website.
    
    Args:
        url: The starting URL for the crawl
        limit: Maximum number of pages to crawl
        max_depth: Maximum depth to crawl
        formats: List of formats to return (default: ["markdown"])
    
    Returns:
        A job ID and instructions for checking the crawl status
    """
    try:
        app = get_firecrawl_app()
        crawl_result = app.crawl_url(url, params={
            'limit': limit,
            'maxDepth': max_depth,
            'scrapeOptions': {
                'formats': formats
            }
        })
        
        job_id = crawl_result.get("jobId")
        if not job_id:
            return f"Error: Failed to start crawl job. {crawl_result.get('error', '')}"
        
        result = f"# Crawl Job Started\n\n"
        result += f"**Job ID:** {job_id}\n\n"
        result += "To check the status of this crawl, use the `check_crawl_status` tool with this Job ID."
        
        return result
    except Exception as e:
        return f"An error occurred while starting the crawl job for {url}: {str(e)}"

@mcp.tool()
async def check_crawl_status(job_id: str) -> str:
    """Check the status of a crawl job.
    
    Args:
        job_id: The ID of the crawl job to check
    
    Returns:
        The current status of the crawl job
    """
    try:
        app = get_firecrawl_app()
        status = app.check_crawl_status(job_id)
        
        return format_crawl_status(status)
    except Exception as e:
        return f"An error occurred while checking the crawl status for job {job_id}: {str(e)}"

@mcp.tool()
async def map_website(url: str, include_subdomains: bool = True) -> str:
    """Map a website to discover all accessible links.
    
    Args:
        url: The URL of the website to map
        include_subdomains: Whether to include subdomains in the mapping
    
    Returns:
        A list of all discovered links on the website
    """
    try:
        app = get_firecrawl_app()
        map_result = app.map_url(url, params={
            'includeSubdomains': include_subdomains
        })
        
        return format_mapped_links(map_result)
    except Exception as e:
        return f"An error occurred while mapping the website {url}: {str(e)}"

@mcp.tool()
async def extract_structured_data(
    urls: List[str], 
    prompt: str,
    schema: Dict[str, Any]
) -> str:
    """Extract structured data from web pages based on a schema.
    
    Args:
        urls: List of URLs to extract data from
        prompt: A prompt describing what data to extract
        schema: JSON schema defining the structure of data to extract
    
    Returns:
        The extracted structured data
    """
    try:
        app = get_firecrawl_app()
        data = app.extract(urls, {
            'prompt': prompt,
            'schema': schema,
        })
        
        if not data.get('success'):
            return f"Error: Failed to extract structured data. {data.get('error', '')}"
        
        formatted_result = f"# Extracted Structured Data\n\n"
        formatted_result += f"```json\n{json.dumps(data.get('data', {}), indent=2)}\n```"
        
        return formatted_result
    except Exception as e:
        return f"An error occurred while extracting structured data: {str(e)}"

# Run the server
if __name__ == "__main__":
    print(f"Running {mcp.name} MCP server...")
    mcp.run()
