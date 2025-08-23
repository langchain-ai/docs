---
sidebar_position: 5
---

# How to handle multiple retrievers when doing query analysis

Sometimes, a query analysis technique may allow for selection of which [retriever](/oss/concepts/retrievers/) to use. To use this, you will need to add some logic to select the retriever to do. We will show a simple example (using mock data) of how to do that.

## Setup
#### Install dependencies


```python
%pip install -qU langchain langchain-community langchain-openai langchain-chroma
```
```output
Note: you may need to restart the kernel to use updated packages.
```
#### Set environment variables

We'll use OpenAI in this example:


```python
import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass()

# Optional, uncomment to trace runs with LangSmith. Sign up here: https://smith.langchain.com.
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
```

### Create Index

We will create a vectorstore over fake information.


```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

texts = ["Harrison worked at Kensho"]
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_texts(texts, embeddings, collection_name="harrison")
retriever_harrison = vectorstore.as_retriever(search_kwargs={"k": 1})

texts = ["Ankush worked at Facebook"]
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_texts(texts, embeddings, collection_name="ankush")
retriever_ankush = vectorstore.as_retriever(search_kwargs={"k": 1})
```

## Query analysis

We will use function calling to structure the output. We will let it return multiple queries.


```python
from typing import List, Optional

from pydantic import BaseModel, Field


class Search(BaseModel):
    """Search for information about a person."""

    query: str = Field(
        ...,
        description="Query to look up",
    )
    person: str = Field(
        ...,
        description="Person to look things up for. Should be `HARRISON` or `ANKUSH`.",
    )
```


```python
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

output_parser = PydanticToolsParser(tools=[Search])

system = """You have the ability to issue search queries to get information to help answer user information."""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm = llm.with_structured_output(Search)
query_analyzer = {"question": RunnablePassthrough()} | prompt | structured_llm
```

We can see that this allows for routing between retrievers


```python
query_analyzer.invoke("where did Harrison Work")
```



```output
Search(query='work history', person='HARRISON')
```



```python
query_analyzer.invoke("where did ankush Work")
```



```output
Search(query='work history', person='ANKUSH')
```


## Retrieval with query analysis

So how would we include this in a chain? We just need some simple logic to select the retriever and pass in the search query


```python
from langchain_core.runnables import chain
```


```python
retrievers = {
    "HARRISON": retriever_harrison,
    "ANKUSH": retriever_ankush,
}
```


```python
@chain
def custom_chain(question):
    response = query_analyzer.invoke(question)
    retriever = retrievers[response.person]
    return retriever.invoke(response.query)
```


```python
custom_chain.invoke("where did Harrison Work")
```



```output
[Document(page_content='Harrison worked at Kensho')]
```



```python
custom_chain.invoke("where did ankush Work")
```



```output
[Document(page_content='Ankush worked at Facebook')]
```



```python

```
