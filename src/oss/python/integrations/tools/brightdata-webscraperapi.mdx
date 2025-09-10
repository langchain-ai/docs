---
title: BrightDataWebScraperAPI
---

[Bright Data](https://brightdata.com/) provides a powerful Web Scraper API that allows you to extract structured data from 100+ ppular domains, including Amazon product details, LinkedIn profiles, and more, making it particularly useful for AI agents requiring reliable structured web data feeds.

## Overview

### Integration details

|Class|Package|Serializable|JS support|Version|
|:--|:--|:-:|:-:|:-:|
|[BrightDataWebScraperAPI](https://pypi.org/project/langchain-brightdata/)|[langchain-brightdata](https://pypi.org/project/langchain-brightdata/)|✅|❌|![PyPI - Version](https://img.shields.io/pypi/v/langchain-brightdata?style=flat-square&label=%20)|

### Tool features

|Native async|Returns artifact|Return data|Pricing|
|:-:|:-:|:--|:-:|
|❌|❌|Structured data from websites (Amazon products, LinkedIn profiles, etc.)|Requires Bright Data account|

## Setup

The integration lives in the `langchain-brightdata` package.

```python
pip install langchain-brightdata
```

You'll need a Bright Data API key to use this tool. You can set it as an environment variable:

```python
import os

os.environ["BRIGHT_DATA_API_KEY"] = "your-api-key"
```

Or pass it directly when initializing the tool:

```python
from langchain_brightdata import BrightDataWebScraperAPI

scraper_tool = BrightDataWebScraperAPI(bright_data_api_key="your-api-key")
```

## Instantiation

Here we show how to instantiate an instance of the BrightDataWebScraperAPI tool. This tool allows you to extract structured data from various websites including Amazon product details, LinkedIn profiles, and more using Bright Data's Dataset API.

The tool accepts various parameters during instantiation:

- `bright_data_api_key` (required, str): Your Bright Data API key for authentication.
- `dataset_mapping` (optional, Dict[str, str]): A dictionary mapping dataset types to their corresponding Bright Data dataset IDs. The default mapping includes:
  - "amazon_product": "gd_l7q7dkf244hwjntr0"
  - "amazon_product_reviews": "gd_le8e811kzy4ggddlq"
  - "linkedin_person_profile": "gd_l1viktl72bvl7bjuj0"
  - "linkedin_company_profile": "gd_l1vikfnt1wgvvqz95w"

## Invocation

### Basic Usage

```python
from langchain_brightdata import BrightDataWebScraperAPI

# Initialize the tool
scraper_tool = BrightDataWebScraperAPI(
    bright_data_api_key="your-api-key"  # Optional if set in environment variables
)

# Extract Amazon product data
results = scraper_tool.invoke(
    {"url": "https://www.amazon.com/dp/B08L5TNJHG", "dataset_type": "amazon_product"}
)

print(results)
```

### Advanced Usage with Parameters

```python
from langchain_brightdata import BrightDataWebScraperAPI

# Initialize with default parameters
scraper_tool = BrightDataWebScraperAPI(bright_data_api_key="your-api-key")

# Extract Amazon product data with location-specific pricing
results = scraper_tool.invoke(
    {
        "url": "https://www.amazon.com/dp/B08L5TNJHG",
        "dataset_type": "amazon_product",
        "zipcode": "10001",  # Get pricing for New York City
    }
)

print(results)

# Extract LinkedIn profile data
linkedin_results = scraper_tool.invoke(
    {
        "url": "https://www.linkedin.com/in/satyanadella/",
        "dataset_type": "linkedin_person_profile",
    }
)

print(linkedin_results)
```

## Customization Options

The BrightDataWebScraperAPI tool accepts several parameters for customization:

|Parameter|Type|Description|
|:--|:--|:--|
|`url`|str|The URL to extract data from|
|`dataset_type`|str|Type of dataset to use (e.g., "amazon_product")|
|`zipcode`|str|Optional zipcode for location-specific data|

## Available Dataset Types

The tool supports the following dataset types for structured data extraction:

|Dataset Type|Description|
|:--|:--|
|`amazon_product`|Extract detailed Amazon product data|
|`amazon_product_reviews`|Extract Amazon product reviews|
|`linkedin_person_profile`|Extract LinkedIn person profile data|
|`linkedin_company_profile`|Extract LinkedIn company profile data|

## Use within an agent

```python
from langchain_brightdata import BrightDataWebScraperAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key="your-api-key")

# Initialize the Bright Data Web Scraper API tool
scraper_tool = BrightDataWebScraperAPI(bright_data_api_key="your-api-key")

# Create the agent with the tool
agent = create_agent(llm, [scraper_tool])

# Provide a user query
user_input = "Scrape Amazon product data for https://www.amazon.com/dp/B0D2Q9397Y?th=1 in New York (zipcode 10001)."

# Stream the agent's step-by-step output
for step in agent.stream(
    {"messages": user_input},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()
```

## API reference

- [Bright Data API Documentation](https://docs.brightdata.com/scraping-automation/web-scraper-api/overview)
