---
title: Astra DB
---

> [DataStax Astra DB](https://docs.datastax.com/en/astra-db-serverless/index.html) is a serverless
> AI-ready database built on `Apache Cassandra®` and made conveniently available
> through an easy-to-use JSON API.

In the walkthrough, we'll demo the `SelfQueryRetriever` with an `Astra DB` vector store.

## Creating an Astra DB vector store

First, create an Astra DB vector store and seed it with some data.

We've created a small demo set of documents containing movie summaries.

NOTE: The self-query retriever requires the `lark` package installed (`pip install lark`).

```python
!pip install "langchain-astradb>=0.6,<0.7" \
  "langchain_openai>=0.3,<0.4" \
  "lark>=1.2,<2.0"
```

In this example, you'll use the `OpenAIEmbeddings`. Please enter an OpenAI API Key.

```python
import os
from getpass import getpass

from langchain_openai.embeddings import OpenAIEmbeddings

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass("OpenAI API Key:")

embeddings = OpenAIEmbeddings()
```

```output
OpenAI API Key: ········
```

Create the Astra DB VectorStore:

- the API Endpoint looks like `https://01234567-89ab-cdef-0123-456789abcdef-us-east1.apps.astra.datastax.com`
- the Token looks like `AstraCS:aBcD0123...`

```python
ASTRA_DB_API_ENDPOINT = input("ASTRA_DB_API_ENDPOINT = ")
ASTRA_DB_APPLICATION_TOKEN = getpass("ASTRA_DB_APPLICATION_TOKEN = ")
```

```output
ASTRA_DB_API_ENDPOINT =  https://01234567-89ab-cdef-0123-456789abcdef-us-east1.apps.astra.datastax.com
ASTRA_DB_APPLICATION_TOKEN =  ········
```

```python
from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document

docs = [
    Document(
        page_content="A bunch of scientists bring back dinosaurs and mayhem breaks loose",
        metadata={"year": 1993, "rating": 7.7, "genre": "science fiction"},
    ),
    Document(
        page_content="Leo DiCaprio gets lost in a dream within a dream within a dream within a ...",
        metadata={"year": 2010, "director": "Christopher Nolan", "rating": 8.2},
    ),
    Document(
        page_content="A psychologist / detective gets lost in a series of dreams within dreams "
        "within dreams and Inception reused the idea",
        metadata={"year": 2006, "director": "Satoshi Kon", "rating": 8.6},
    ),
    Document(
        page_content="A bunch of normal-sized women are supremely wholesome and some men "
        "pine after them",
        metadata={"year": 2019, "director": "Greta Gerwig", "rating": 8.3},
    ),
    Document(
        page_content="Toys come alive and have a blast doing so",
        metadata={"year": 1995, "genre": "animated"},
    ),
    Document(
        page_content="Three men walk into the Zone, three men walk out of the Zone",
        metadata={
            "year": 1979,
            "director": "Andrei Tarkovsky",
            "genre": "science fiction",
            "rating": 9.9,
        },
    ),
]

vectorstore = AstraDBVectorStore.from_documents(
    docs,
    embeddings,
    collection_name="astra_self_query_demo",
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    token=ASTRA_DB_APPLICATION_TOKEN,
)
```

## Creating a self-querying retriever

Now you can instantiate the retriever.

To do this, you need to provide some information upfront about the metadata fields that the documents support, along with a short description of the documents' contents.

```python
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import OpenAI

metadata_field_info = [
    AttributeInfo(
        name="genre",
        description="The genre of the movie",
        type="string or list[string]",
    ),
    AttributeInfo(
        name="year",
        description="The year the movie was released",
        type="integer",
    ),
    AttributeInfo(
        name="director",
        description="The name of the movie director",
        type="string",
    ),
    AttributeInfo(
        name="rating", description="A 1-10 rating for the movie", type="float"
    ),
]
document_content_description = "Brief summary of a movie"
llm = OpenAI(temperature=0)

retriever = SelfQueryRetriever.from_llm(
    llm,
    vectorstore,
    document_content_description,
    metadata_field_info,
    verbose=True,
)
```

## Testing it out

Now you can try actually using our retriever:

```python
# This example only specifies a relevant query
retriever.invoke("What are some movies about dinosaurs?")
```

```output
[Document(id='d7b9ec1edafa467caab524455e8c1f5d', metadata={'year': 1993, 'rating': 7.7, 'genre': 'science fiction'}, page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose'),
 Document(id='8ad04ef2a73d4f74897a51e49be1a8d2', metadata={'year': 1995, 'genre': 'animated'}, page_content='Toys come alive and have a blast doing so'),
 Document(id='5b07e600d3494506952b60e0a45a0546', metadata={'year': 1979, 'director': 'Andrei Tarkovsky', 'genre': 'science fiction', 'rating': 9.9}, page_content='Three men walk into the Zone, three men walk out of the Zone'),
 Document(id='a0cef19e27c341929098ac4793602829', metadata={'year': 2006, 'director': 'Satoshi Kon', 'rating': 8.6}, page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea')]
```

```python
# This example specifies a filter
retriever.invoke("I want to watch a movie rated higher than 8.5")
```

```output
[Document(id='5b07e600d3494506952b60e0a45a0546', metadata={'year': 1979, 'director': 'Andrei Tarkovsky', 'genre': 'science fiction', 'rating': 9.9}, page_content='Three men walk into the Zone, three men walk out of the Zone'),
 Document(id='a0cef19e27c341929098ac4793602829', metadata={'year': 2006, 'director': 'Satoshi Kon', 'rating': 8.6}, page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea')]
```

```python
# This example only specifies a query and a filter
retriever.invoke("Has Greta Gerwig directed any movies about women")
```

```output
[Document(id='0539843fd203484c9be486c2a0e2454c', metadata={'year': 2019, 'director': 'Greta Gerwig', 'rating': 8.3}, page_content='A bunch of normal-sized women are supremely wholesome and some men pine after them')]
```

```python
# This example specifies a composite filter
retriever.invoke("What's a highly rated (above 8.5), science fiction movie ?")
```

```output
[Document(id='a0cef19e27c341929098ac4793602829', metadata={'year': 2006, 'director': 'Satoshi Kon', 'rating': 8.6}, page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea'),
 Document(id='5b07e600d3494506952b60e0a45a0546', metadata={'year': 1979, 'director': 'Andrei Tarkovsky', 'genre': 'science fiction', 'rating': 9.9}, page_content='Three men walk into the Zone, three men walk out of the Zone')]
```

```python
# This example specifies a query and composite filter
retriever.invoke(
    "What's a movie about toys after 1990 but before 2005, and is animated"
)
```

```output
[Document(id='8ad04ef2a73d4f74897a51e49be1a8d2', metadata={'year': 1995, 'genre': 'animated'}, page_content='Toys come alive and have a blast doing so')]
```

## Set a limit ('k')

you can also use the self-query retriever to specify `k`, the number of documents to fetch.

You achieve this by passing `enable_limit=True` to the constructor.

```python
retriever_k = SelfQueryRetriever.from_llm(
    llm,
    vectorstore,
    document_content_description,
    metadata_field_info,
    verbose=True,
    enable_limit=True,
)
```

```python
# This example only specifies a relevant query
retriever_k.invoke("What are two movies about dinosaurs?")
```

```output
[Document(id='d7b9ec1edafa467caab524455e8c1f5d', metadata={'year': 1993, 'rating': 7.7, 'genre': 'science fiction'}, page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose'),
 Document(id='8ad04ef2a73d4f74897a51e49be1a8d2', metadata={'year': 1995, 'genre': 'animated'}, page_content='Toys come alive and have a blast doing so')]
```

## Cleanup

If you want to completely delete the collection from your Astra DB instance, run this.

_(You will lose the data you stored in it.)_

```python
vectorstore.delete_collection()
```
