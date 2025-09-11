---
title: Neo4j
---

>[Neo4j](https://neo4j.com/docs/) is a graph database that stores nodes and relationships, that also supports native vector search.

In the notebook, we'll demo the `SelfQueryRetriever` wrapped around a `Neo4j` vector store.

## Creating a Neo4j vector store

First we'll want to create a Neo4j vector store and seed it with some data. We've created a small demo set of documents that contain summaries of movies.

We want to use `OpenAIEmbeddings` so we have to get the OpenAI API Key.

```python
%pip install -U neo4j
```

```output
Requirement already satisfied: neo4j in /Users/moyi/git/langchain/env/lib/python3.11/site-packages (5.24.0)
Requirement already satisfied: pytz in /Users/moyi/git/langchain/env/lib/python3.11/site-packages (from neo4j) (2024.1)
Note: you may need to restart the kernel to use updated packages.
```

```python
import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")
```

```output
OpenAI API Key: ········
```

```python
# To run this notebook, you can set up a free neo4j account on neo4j.com and input the following information.
# (If you are having trouble connecting to the database, try using neo4j+ssc: instead of neo4j+s)

if "NEO4J_URI" not in os.environ:
    os.environ["NEO4J_URI"] = getpass.getpass("Neo4j URL:")
if "NEO4J_USERNAME" not in os.environ:
    os.environ["NEO4J_USERNAME"] = getpass.getpass("Neo4j User Name:")
if "NEO4J_PASSWORD" not in os.environ:
    os.environ["NEO4J_PASSWORD"] = getpass.getpass("Neo4j Password:")
```

```output
Neo4j URL: ········
Neo4j User Name: ········
Neo4j Password: ········
```

```python
from langchain_core.documents import Document
from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
```

```python
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
        page_content="A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea",
        metadata={"year": 2006, "director": "Satoshi Kon", "rating": 8.6},
    ),
    Document(
        page_content="A bunch of normal-sized women are supremely wholesome and some men pine after them",
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
vectorstore = Neo4jVector.from_documents(docs, embeddings)
```

```output
Received notification from DBMS server: {severity: WARNING} {code: Neo.ClientNotification.Statement.FeatureDeprecationWarning} {category: DEPRECATION} {title: This feature is deprecated and will be removed in future versions.} {description: CALL subquery without a variable scope clause is now deprecated. Use CALL (row) { ... }} {position: line: 1, column: 21, offset: 20} for query: "UNWIND $data AS row CALL { WITH row MERGE (c:`Chunk` {id: row.id}) WITH c, row CALL db.create.setNodeVectorProperty(c, 'embedding', row.embedding) SET c.`text` = row.text SET c += row.metadata } IN TRANSACTIONS OF 1000 ROWS "
```

## Creating our self-querying retriever

Now we can instantiate our retriever. To do this we'll need to provide some information upfront about the metadata fields that our documents support and a short description of the document contents.

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
    llm, vectorstore, document_content_description, metadata_field_info, verbose=True
)
```

## Testing it out

And now we can try actually using our retriever!

```python
# This example only specifies a relevant query
retriever.invoke("What are some movies about dinosaurs")
```

```output
[Document(metadata={'genre': 'science fiction', 'year': 1993, 'rating': 7.7}, page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose'),
 Document(metadata={'genre': 'animated', 'year': 1995}, page_content='Toys come alive and have a blast doing so'),
 Document(metadata={'genre': 'science fiction', 'year': 1979, 'rating': 9.9, 'director': 'Andrei Tarkovsky'}, page_content='Three men walk into the Zone, three men walk out of the Zone'),
 Document(metadata={'year': 2006, 'rating': 8.6, 'director': 'Satoshi Kon'}, page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea')]
```

```python
# This example only specifies a filter
retriever.invoke("I want to watch a movie rated higher than 8.5")
```

```output
[Document(metadata={'genre': 'science fiction', 'year': 1979, 'rating': 9.9, 'director': 'Andrei Tarkovsky'}, page_content='Three men walk into the Zone, three men walk out of the Zone'),
 Document(metadata={'year': 2006, 'rating': 8.6, 'director': 'Satoshi Kon'}, page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea')]
```

```python
# This example specifies a query and a filter
retriever.invoke("Has Greta Gerwig directed any movies about women")
```

```output
[Document(metadata={'year': 2019, 'rating': 8.3, 'director': 'Greta Gerwig'}, page_content='A bunch of normal-sized women are supremely wholesome and some men pine after them')]
```

```python
# This example specifies a composite filter
retriever.invoke("What's a highly rated (above 8.5) science fiction film?")
```

```output
[Document(metadata={'year': 2006, 'rating': 8.6, 'director': 'Satoshi Kon'}, page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea'),
 Document(metadata={'genre': 'science fiction', 'year': 1979, 'rating': 9.9, 'director': 'Andrei Tarkovsky'}, page_content='Three men walk into the Zone, three men walk out of the Zone')]
```

```python
# This example specifies a query and composite filter
retriever.invoke(
    "What's a movie after 1990 but before 2005 that's all about toys, and preferably is animated"
)
```

```output
[Document(metadata={'genre': 'animated', 'year': 1995}, page_content='Toys come alive and have a blast doing so')]
```

## Filter k

We can also use the self query retriever to specify `k`: the number of documents to fetch.

We can do this by passing `enable_limit=True` to the constructor.

```python
retriever = SelfQueryRetriever.from_llm(
    llm,
    vectorstore,
    document_content_description,
    metadata_field_info,
    enable_limit=True,
    verbose=True,
)
```

```python
# This example only specifies a relevant query
retriever.invoke("what are two movies about dinosaurs")
```

```output
[Document(metadata={'genre': 'science fiction', 'year': 1993, 'rating': 7.7}, page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose'),
 Document(metadata={'genre': 'animated', 'year': 1995}, page_content='Toys come alive and have a blast doing so')]
```

```python
```

```python

```
