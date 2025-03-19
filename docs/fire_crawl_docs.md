# Getting Started with Firecrawl: A Beginner's Guide

Welcome to **Firecrawl**! This guide is designed for beginners who want to harness the power of Firecrawl for web scraping, crawling, mapping websites, and extracting structured data. Whether you are using Python or Node.js (with Yarn for JavaScript projects), follow these step-by-step instructions to get started.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Scrape a Web Page](#scrape-a-web-page)
4. [Crawl a Website](#crawl-a-website)
5. [Check Crawl Status](#check-crawl-status)
6. [Crawl Webhook](#crawl-webhook)
7. [Map a Website](#map-a-website)
8. [Extract Structured Data](#extract-structured-data)
9. [Troubleshooting and Next Steps](#troubleshooting-and-next-steps)

---

## 1. Introduction

**Firecrawl** is an API service that simplifies web scraping and crawling tasks. With Firecrawl, you can:

- **Scrape a web page:** Retrieve the content of a single URL in markdown format.
- **Crawl a website:** Fetch multiple pages and collect data across subpages.
- **Map a website:** Discover and list all accessible links.
- **Extract structured data:** Pull out specific information using a predefined schema.

This guide provides simple examples and explanations to help you integrate these functionalities into your projects.

---

## 2. Installation


Install the Firecrawl Python package using pip:

```bash
pip install firecrawl-py
```

_*Remember:* Replace the placeholder API key with your actual Firecrawl API key in all examples._

---

## 3. Scrape a Web Page

This feature allows you to extract the content of a single web page and return it in markdown format.

### Python Example

```python:docs/fire_crawl_docs.md
# Scrape a Web Page using Firecrawl (Python)

from firecrawl import FirecrawlApp

# Initialize Firecrawl with your API key.
app = FirecrawlApp(api_key='YOUR_API_KEY')

# Scrape the URL with markdown format.
response = app.scrape_url(url='https://en.wikipedia.org/wiki/Main_Page', params={
    'formats': ['markdown'],
})

# Check if the request was successful.
if response.get('success'):
    print("Scraped Markdown Content:")
    print(response['data']['markdown'])
else:
    print("An error occurred while scraping.")
```

**Sample Response:**

```json
{
    "success": true,
    "data": {
        "markdown": "# Markdown Content",
        "metadata": {
            "title": "Mendable | AI for CX and Sales",
            "description": "AI for CX and Sales",
            "language": null,
            "sourceURL": "https://www.mendable.ai/"
        }
    }
}
```

---

## 4. Crawl a Website

Crawl an entire site to fetch multiple pages and their content. This process starts a crawl job and returns a job ID for monitoring.

### Python Example

```python:docs/fire_crawl_docs.md
# Crawl a Website using Firecrawl (Python)

from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key='YOUR_API_KEY')

# Start a crawl job on a specified URL.
crawl_result = app.crawl_url('https://en.wikipedia.org/wiki/Main_Page', params={
    'limit': 10,         # Limit to 10 pages.
    'maxDepth': 2,       # Maximum depth to crawl.
    'scrapeOptions': {
        'formats': ['markdown']
    }
})

job_id = crawl_result.get("jobId")
print("Crawl job started with Job ID:", job_id)
```

---

## 5. Check Crawl Status

Use the job ID obtained from the crawl task to check its current status.

### Python Example

```python:docs/fire_crawl_docs.md
# Check Crawl Status using Firecrawl (Python)

status = app.check_crawl_status(job_id)
print("Crawl Status:", status)
```

**Sample Status Response:**

```json
{
    "status": "scraping", 
    "totalCount": 22,
    "creditsUsed": 17,
    "expiresAt": "2024-01-01",
    "next": "http://api.firecrawl.dev/v1/crawl/123-456?skip=17",
    "data": null
}
```

---

## 6. Crawl Webhook

Set up a webhook to automatically receive notifications when the crawl job is complete. When the job finishes, your webhook endpoint will be sent a JSON payload with details about the crawl.

**Example Payload:**

```json
{
    "status": "completed",
    "totalCount": 22,
    "creditsUsed": 22,
    "expiresAt": "2024-01-01",
    "data": [
        {
            "markdown": "# Markdown Content",
            "metadata": {
                "title": "Mendable | AI for CX and Sales",
                "description": "AI for CX and Sales",
                "language": null,
                "sourceURL": "https://www.mendable.ai/",
                "statusCode": 200,
                "error": null
            }
        }
    ]
}
```

---

## 7. Map a Website

Mapping a website returns a list of all accessible links within that site, helping you to understand its structure.

### Python Example

```python:docs/fire_crawl_docs.md
# Map a Website using Firecrawl (Python)

map_result = app.map_url('https://en.wikipedia.org/wiki/Main_Page', params={
    'includeSubdomains': True
})

if map_result.get('success'):
    print("Discovered Links:")
    for link in map_result.get('links', []):
        print(link)
else:
    print("Failed to map the website.")
```

**Sample Response:**

```json
{
    "success": true,
    "links": [
        "https://www.mendable.ai/",
        "https://www.mendable.ai/features",
        "https://www.mendable.ai/pricing",
        "https://www.mendable.ai/about"
    ]
}
```

---

## 8. Extract Structured Data

Extract specific, structured data from a webpage by providing a JSON schema that defines the data format you need.

### Python Example with Schema Definition

```python:docs/fire_crawl_docs.md
# Extract Structured Data using Firecrawl (Python)

from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field

app = FirecrawlApp(api_key='YOUR_API_KEY')

# Define a nested model for detailed data extraction.
class NestedModel1(BaseModel):
    company_name: str
    stock_price: float
    market_trend: str = None
    analysis_summary: str = None

# Define the overall extraction schema.
class ExtractSchema(BaseModel):
    stock_analysis: NestedModel1

# Request structured data from the provided URL.
data = app.extract([
    "https://livetse.ir/market-report-28-esfand-1403-12-28/"
], {
    'prompt': 'Extract stock analysis including company name, stock price, market trend, and analysis summary from the specified URL.',
    'schema': ExtractSchema.model_json_schema(),
})

print("Extracted Data:", data)
```

**Sample Response:**

```json
{
  "success": true,
  "data": {
    "stock_analysis": {}
  }
}
```

---

## 9. Troubleshooting and Next Steps

### Error Handling

- **HTTP 402:** Payment Required. Verify your API plan and key.
- **HTTP 429:** Too Many Requests. Ensure you respect rate limits.
- **HTTP 500:** Internal Server Error. Try again later or contact support.

### Getting Support

Refer to the official Firecrawl documentation or contact support if you run into issues.


