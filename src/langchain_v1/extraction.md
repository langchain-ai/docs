# Document extraction

This guide shows you how to extract information from documents using LangChain's **prebuilt** extraction functionality. The extraction chain can produce either text summaries or structured data from one or more documents.

## Prerequisites

Before you start this tutorial, ensure you have the following:

- An [Anthropic](https://console.anthropic.com/settings/keys) API key

## 1. Install dependencies

If you haven't already, install LangGraph and LangChain:

```bash
pip install -U langgraph "langchain[anthropic]"
```

<Tip>
    LangChain is installed so the extractor can call the [model](https://python.langchain.com/docs/integrations/chat/).
</Tip>

## 2. Set up documents

First, create some documents to extract information from:

```python
from langchain_core.documents import Document

documents = [
    Document(
        id="1",
        page_content="""Bobby Luka was 10 years old.
Synthetic fuels—produced from captured carbon and green hydrogen—are gaining traction in aviation. The EU's "ReFuelEU" mandate requires increasing blends of sustainable aviation fuel (SAF) starting in 2025. Airbus and Rolls-Royce have completed long-haul test flights powered entirely by synthetic kerosene.""",
        metadata={"source": "synthetic_fuel_aviation"},
    ),
    Document(
        id="2",
        page_content="""
AI is accelerating early-stage drug discovery, especially in target identification and molecule generation. Platforms like BenevolentAI and Insilico Medicine have generated preclinical candidates using generative models trained on biological and chemical data.""",
        metadata={"source": "ai_drug_discovery"},
    ),
    Document(
        id="3",
        page_content="""Jack Johnson was 23 years old and blonde.
Bobby Luka's hair is brown.""",
        metadata={"source": "people_info"},
    ),
]
```

## 3. Configure a model

Configure an LLM for extraction using [init_chat_model](https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html):

```python
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "anthropic:claude-3-5-sonnet-latest",
    temperature=0
)
```

## 4. Extract a basic summary

Create an extractor to produce text summaries from documents:

```python
from langchain.chains.summarization import create_summarizer

# Create a basic summarizer
summarizer = create_summarizer(
    model,
    initial_prompt="Produce a concise summary of the following document in 2-3 sentences."
).compile(name="TextSummarizer")

# Extract summary
result = summarizer.invoke({"documents": documents})
print(result["result"])
```

## 5. Extract structured summaries

To produce structured responses with a specific format, use the `response_format` parameter with a Pydantic model:

```python
from pydantic import BaseModel
from langchain.chains.summarization import create_summarizer

class Summary(BaseModel):
    """Structured summary with title and key points."""
    
    title: str
    key_points: list[str]

# Create structured summarizer
structured_summarizer = create_summarizer(
    model,
    initial_prompt="Extract the main topics and create a structured summary with a title and up to 3 key points.",
    response_format=Summary
).compile(name="StructuredSummarizer")

# Extract structured summary
result = structured_summarizer.invoke({"documents": documents})

# Access structured fields
print(f"Title: {result['result'].title}")
print("Key points:")
for point in result['result'].key_points:
    print(f"  • {point}")
```

## 6. Extract entities with source tracking

Extract specific entities while tracking which documents they came from:

```python
from typing import Optional
from pydantic import BaseModel, Field

class Person(BaseModel):
    """Person entity with source tracking."""
    
    name: str
    age: Optional[str] = None
    hair_color: Optional[str] = None
    source_doc_ids: list[str] = Field(
        default=[],
        description="The IDs of the documents where the information was found.",
    )

class PeopleExtraction(BaseModel):
    """Collection of extracted people."""
    
    people: list[Person]

# Create entity extractor
entity_extractor = create_summarizer(
    model,
    initial_prompt="Extract information about people mentioned in the documents. Include the document IDs where each piece of information was found.",
    response_format=PeopleExtraction
).compile(name="EntityExtractor")

# Extract entities
result = entity_extractor.invoke({"documents": documents})

# Display extracted people with sources
for person in result['result'].people:
    print(f"Name: {person.name}")
    if person.age:
        print(f"  Age: {person.age}")
    if person.hair_color:
        print(f"  Hair: {person.hair_color}")
    print(f"  Sources: {', '.join(person.source_doc_ids)}")
    print()
```

## Custom prompts

Customize extraction behavior with specific prompts:

```python
custom_extractor = create_summarizer(
    model,
    initial_prompt="Focus on extracting technical information and key innovations mentioned in the documents."
).compile()
```

For more advanced extraction patterns and customization, see the [extraction how-to guides](../how-tos/extraction/).