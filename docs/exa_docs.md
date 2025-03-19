# Exa_py: Comprehensive Guide for Exa Web Search API

Exa_py is a powerful Python client for Exa Web Search. It automatically selects the best search model (keyword or neural via embeddings) for your query and offers robust filtering and content extraction options. This guide explains how to install the package, set up your client, and use the various search endpoints with detailed parameter information.

---

## Table of Contents

1. [Installation](#installation)
2. [Basic Setup](#basic-setup)
3. [Basic Search](#basic-search)
4. [Advanced Search with Content Extraction](#advanced-search-with-content-extraction)
5. [API Reference & Parameters](#api-reference--parameters)
6. [Additional Examples](#additional-examples)
7. [Error Handling & Best Practices](#error-handling--best-practices)
8. [Rate Limits & Pricing](#rate-limits--pricing)

---

## Installation

Install the package using pip:

```bash:web_search.md
pip install exa-py
```

---

## Basic Setup

Before you can start searching, set your Exa API key (which can be provided via the `x-api-key` header or the Bearer Authorization header). The simplest way to set this up is by using an environment variable.

```python:web_search.md
import os
from exa_py import Exa

# Initialize the client using your API key
exa = Exa(api_key=os.getenv('EXA_API_KEY'))
```

---

## Basic Search

Perform a simple keyword search. The client automatically chooses between a traditional keyword search and Exa’s embeddings-based model for relevance.

```python:web_search.md
# Simple keyword search query
results = exa.search("artificial intelligence news")

# Process and display search results
for result in results.results:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Published Date: {result.published_date}")
```

---

## Advanced Search with Content Extraction

For a more granular search, you can use `search_and_contents`. This method lets you specify parameters such as search type, auto-prompt conversion, date filters, domain inclusion/exclusion, and options for content extraction (e.g., fetching page text, highlights, summaries, etc.).

Below is an example that uses neural search, custom text limits, and returns additional results information like subpages and extra links.

```python:web_search.md
from exa_py import Exa

exa = Exa(api_key="YOUR_EXA_API_KEY")

results = exa.search_and_contents(
    "Latest research in LLMs",
    type="auto",  # "auto" lets Exa choose between neural and keyword
    category="research paper",
    num_results=10,
    text={
        "max_characters": 1000,
        "include_html_tags": False
    },
    summary={
        "query": "Main developments and key takeaways"
    },
    subpages=1,
    subpage_target="sources",
    extras={
        "links": 1,
        "image_links": 1
    },
    use_autoprompt=True,
    start_published_date="2025-02-28T20:30:00.000Z",
    start_crawl_date="2025-04-29T20:30:01.000Z",
    include_domains=["towardsdatascience.com"],
    include_text=["LLMs"],
    exclude_text=["keras"],
    livecrawl="always"
)

print(results)
```

The above example demonstrates:
- **Search Type:** Setting `type` to `"auto"` delegates the choice between keyword and neural search.
- **Content Extraction:** Providing a `text` dictionary limits text capture to a maximum of 1000 characters.
- **Summarization:** Automatically extract a summary based on the query provided.
- **Subpages & Extras:** Fetch related subpages (such as source pages) and additional links or image links.
- **Filtering:** Narrow down results with domain and text inclusion/exclusion, and specific crawl & publish dates.

---

## API Reference & Parameters

Exa_py uses a simple POST endpoint (`/search`) for both search and content extraction. Below is an overview of key parameters:

### Request Body Parameters

- **query** (`string`, *required*):  
  The search string.  
  _Example:_ `"Latest developments in LLM capabilities"`

- **useAutoprompt** (`boolean`, default: `true`):  
  If enabled, autoprompt automatically converts your query into an Exa-style query. _(Not available for keyword searches)_

- **type** (`enum<string>`, default: `"auto"`):  
  Search type – either `"keyword"`, `"neural"`, or `"auto"`.  
  _Available options:_ `"keyword"`, `"neural"`, `"auto"`

- **category** (`enum<string>`):  
  Focus the search by data category.  
  _Options include:_ `"company"`, `"research paper"`, `"news"`, `"pdf"`, `"github"`, `"tweet"`, `"personal site"`, `"linkedin profile"`, `"financial report"`

- **numResults** (`integer`, default: `10`):  
  Number of results to return. Maximum values vary by plan.

- **includeDomains** (`string[]`):  
  List of domains to include in the search (results will only be from these domains).

- **excludeDomains** (`string[]`):  
  List of domains to exclude from the results.

- **startCrawlDate** and **endCrawlDate** (`string` in ISO 8601 format):  
  Filter results by the crawl date (when a link was first discovered).

- **startPublishedDate** and **endPublishedDate** (`string` in ISO 8601 format):  
  Filter results based on their publication dates.

- **includeText** (`string[]`):  
  Only return pages containing these strings in their text _(limited to one string of up to 5 words)_.

- **excludeText** (`string[]`):  
  Exclude pages that contain these strings in their text _(limited to one string of up to 5 words)_.

- **contents** (`object`):  
  Options for what content to extract. This contains:
  - **text**: A dictionary (`max_characters`, `include_html_tags`, etc.)
  - **summary**: A dictionary (e.g., with a `"query"` for summarization)
  
- **subpages** (`integer`):  
  Number of subpages to retrieve.
  
- **subpage_target** (`string`):  
  Specifies the target type for subpages (for example, `"sources"`).

- **extras** (`object`):  
  Additional options to return extra information such as additional links or image links.

### Response Example

A typical response from a successful call contains:

```json
{
  "requestId": "b5947044c4b78efa9552a7c89b306d95",
  "autopromptString": "Heres a link to the latest research in LLMs:",
  "autoDate": "2024-02-08T02:15:42.180Z",
  "resolvedSearchType": "neural",
  "results": [
    {
      "title": "A Comprehensive Overview of Large Language Models",
      "url": "https://arxiv.org/pdf/2307.06435.pdf",
      "publishedDate": "2023-11-16T01:36:32.547Z",
      "author": "Author Name",
      "score": 0.4600165784358978,
      "id": "https://arxiv.org/abs/2307.06435",
      "image": "https://arxiv.org/pdf/2307.06435.pdf/page_1.png",
      "favicon": "https://arxiv.org/favicon.ico",
      "text": "Abstract Large Language Models (LLMs)...",
      "highlights": [
        "Key highlight of the text..."
      ],
      "summary": "This overview paper on LLMs highlights key developments...",
      "subpages": [
        {
          "id": "https://arxiv.org/abs/2303.17580",
          "url": "https://arxiv.org/pdf/2303.17580.pdf",
          "title": "HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face",
          "author": "Researcher Name",
          "publishedDate": "2023-11-16T01:36:20.486Z",
          "text": "Detailed abstract or snippet...",
          "summary": "A brief summary of the subpage content..."
        }
      ],
      "extras": {
        "links": []
      }
    }
  ],
  "searchType": "auto",
  "costDollars": {
    "total": 0.005,
    "breakDown": [
      {
        "search": 0.005,
        "contents": 0,
        "breakdown": {
          "keywordSearch": 0,
          "neuralSearch": 0.005,
          "contentText": 0,
          "contentHighlight": 0,
          "contentSummary": 0
        }
      }
    ]
  }
}
```

_Note:_ The response also includes pricing details under **costDollars**, which break down the cost of the search and content extraction by operation type and number of results.

---

## Additional Examples

### Time-based Filtering

Search for content published within the last 24 hours:

```python:web_search.md
from datetime import datetime, timedelta

# Compute start date (24 hours ago)
start_date = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")

results = exa.search(
    "breaking news",
    start_published_date=start_date
)
```

### Domain Filtering

Restrict search results to specific domains while excluding others:

```python:web_search.md
results = exa.search(
    "technology trends",
    include_domains=["techcrunch.com", "wired.com"],
    exclude_domains=["example.com"]
)
```

### Using a Custom Autoprompt and Subpage Extraction

```python:web_search.md
results = exa.search_and_contents(
    "blog post about AI",
    type="neural",
    use_autoprompt=True,
    category="tweet",
    num_results=10,
    start_published_date="2025-02-28T20:30:00.000Z",
    start_crawl_date="2025-04-29T20:30:01.000Z",
    include_domains=["towardsdatascience.com"],
    include_text=["LLMs"],
    exclude_text=["keras"],
    livecrawl="always",
    text={
        "max_characters": 1000
    },
    summary={
        "query": "main points and important parts of the content"
    }
)

print(results)
```

---

## Error Handling & Best Practices

### Error Handling

Always wrap your API calls within try/except blocks to gracefully handle any network issues or API errors:

```python:web_search.md
try:
    results = exa.search("your query here")
except Exception as e:
    print(f"Search failed: {str(e)}")
```

### Best Practices

1. **Choose the Right Search Type:**  
   Use keyword search for faster results when precise text matching is required. Use neural search when semantic understanding is more important.

2. **Limit Content Extraction Length:**  
   Restrict text content via the `max_characters` option to improve performance.

3. **Filter Domains:**  
   Narrow the scope of your search results by including only trusted domains and excluding irrelevant ones.

4. **Cache Frequent Queries:**  
   If your application performs recurring searches, consider caching results to reduce API calls.

5. **Respect API Rate Limits:**  
   Be aware of your API plan’s rate limits. Implement throttling and error handling as necessary.

---

## Rate Limits & Pricing

Be sure to understand the cost breakdown associated with your requests. Exa_py returns detailed cost information in the response:

- **Neural Search Pricing:**
  - 1–25 results: \$0.005 per request
  - 26–100 results: \$0.025 per request
  - 100+ results: \$1 per request

- **Keyword Search Pricing:**
  - 1–100 results: \$0.0025 per request
  - 100+ results: \$3 per request

- **Content Extraction Pricing:**
  - Content text: \$0.001 per page
  - Highlights: \$0.001 per page
  - Summaries: \$0.001 per page

Make sure you build with cost efficiency in mind, particularly for high-volume or complex queries.

---

This documentation should provide a comprehensive overview of how to leverage the *exa_py* package to perform intelligent web searches with advanced content extraction capabilities. For more detailed technical information, consult the official Exa API documentation.

Happy Searching!