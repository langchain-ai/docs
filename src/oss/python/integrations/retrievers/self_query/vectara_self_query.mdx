---
title: Vectara self-querying
---

[Vectara](https://vectara.com/) is the trusted AI Assistant and Agent platform which focuses on enterprise readiness for mission-critical applications.
Vectara serverless RAG-as-a-service provides all the components of RAG behind an easy-to-use API, including:

1. A way to extract text from files (PDF, PPT, DOCX, etc)
2. ML-based chunking that provides state of the art performance.
3. The [Boomerang](https://vectara.com/how-boomerang-takes-retrieval-augmented-generation-to-the-next-level-via-grounded-generation/) embeddings model.
4. Its own internal vector database where text chunks and embedding vectors are stored.
5. A query service that automatically encodes the query into embedding, and retrieves the most relevant text segments, including support for [Hybrid Search](https://docs.vectara.com/docs/api-reference/search-apis/lexical-matching) as well as multiple reranking options such as the [multi-lingual relevance reranker](https://www.vectara.com/blog/deep-dive-into-vectara-multilingual-reranker-v1-state-of-the-art-reranker-across-100-languages), [MMR](https://vectara.com/get-diverse-results-and-comprehensive-summaries-with-vectaras-mmr-reranker/), [UDF reranker](https://www.vectara.com/blog/rag-with-user-defined-functions-based-reranking).
6. An LLM to for creating a [generative summary](https://docs.vectara.com/docs/learn/grounded-generation/grounded-generation-overview), based on the retrieved documents (context), including citations.

For more information:

- [Documentation](https://docs.vectara.com/docs/)
- [API Playground](https://docs.vectara.com/docs/rest-api/)
- [Quickstart](https://docs.vectara.com/docs/quickstart)

This notebook shows how to use `Vectara` as `SelfQueryRetriever`.

## Setup

To use the `VectaraVectorStore` you first need to install the partner package.

```python
!uv pip install -U pip && uv pip install -qU langchain-vectara
```

# Getting Started

To get started, use the following steps:

1. If you don't already have one, [Sign up](https://www.vectara.com/integrations/langchain) for your free Vectara trial.
2. Within your account you can create one or more corpora. Each corpus represents an area that stores text data upon ingest from input documents. To create a corpus, use the **"Create Corpus"** button. You then provide a name to your corpus as well as a description. Optionally you can define filtering attributes and apply some advanced options. If you click on your created corpus, you can see its name and corpus ID right on the top.
3. Next you'll need to create API keys to access the corpus. Click on the **"Access Control"** tab in the corpus view and then the **"Create API Key"** button. Give your key a name, and choose whether you want query-only or query+index for your key. Click "Create" and you now have an active API key. Keep this key confidential.

To use LangChain with Vectara, you'll need to have these two values: `corpus_key` and `api_key`.
You can provide `VECTARA_API_KEY` to LangChain in two ways:

1. Include in your environment these two variables: `VECTARA_API_KEY`.

   For example, you can set these variables using os.environ and getpass as follows:

```python
import os
import getpass

os.environ["VECTARA_API_KEY"] = getpass.getpass("Vectara API Key:")
```

2. Add them to the `Vectara` vectorstore constructor:

```python
vectara = Vectara(
    vectara_api_key=vectara_api_key
)
```

In this notebook we assume they are provided in the environment.

## Connecting to Vectara from LangChain

In this example, we assume that you've created an account and a corpus, and added your `VECTARA_CORPUS_KEY` and `VECTARA_API_KEY` (created with permissions for both indexing and query) as environment variables.

We further assume the corpus has 4 fields defined as filterable metadata attributes: `year`, `director`, `rating`, and `genre`

```python
import os

from langchain_core.documents import Document

os.environ["VECTARA_API_KEY"] = "VECTARA_API_KEY"
os.environ["VECTARA_CORPUS_KEY"] = "VECTARA_CORPUS_KEY"

from langchain_vectara import Vectara
```

## Dataset

We first define an example dataset of movie, and upload those to the corpus, along with the metadata:

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
            "rating": 9.9,
            "director": "Andrei Tarkovsky",
            "genre": "science fiction",
        },
    ),
]

corpus_key = os.getenv("VECTARA_CORPUS_KEY")
vectara = Vectara()
for doc in docs:
    vectara.add_texts(
        [doc.page_content], corpus_key=corpus_key, doc_metadata=doc.metadata
    )
```

## Self-query with Vectara

 You don't need self-query via the LangChain mechanism—enabling `intelligent_query_rewriting` on the Vectara platform achieves the same result.
Vectara offers Intelligent Query Rewriting option which  enhances search precision by automatically generating metadata filter expressions from natural language queries. This capability analyzes user queries, extracts relevant metadata filters, and rephrases the query to focus on the core information need. For more [details](https://docs.vectara.com/docs/search-and-retrieval/intelligent-query-rewriting).

Enable intelligent query rewriting on a per-query basis by setting the `intelligent_query_rewriting` parameter to `true` in `VectaraQueryConfig`.

```python
from langchain_vectara.vectorstores import (
    CorpusConfig,
    SearchConfig,
    VectaraQueryConfig,
)

config = VectaraQueryConfig(
    search=SearchConfig(corpora=[CorpusConfig(corpus_key=corpus_key)]),
    generation=None,
    intelligent_query_rewriting=True,
)
```

## Queries

And now we can try actually using our vectara_queries method!

```python
# This example only specifies a relevant query
vectara.vectara_query("What are movies about scientists", config)
```

```output
[(Document(metadata={'year': 1995, 'genre': 'animated', 'source': 'langchain'}, page_content='Toys come alive and have a blast doing so'),
  0.4141285717487335),
 (Document(metadata={'year': 1979, 'rating': 9.9, 'director': 'Andrei Tarkovsky', 'genre': 'science fiction', 'source': 'langchain'}, page_content='Three men walk into the Zone, three men walk out of the Zone'),
  0.4046250879764557),
 (Document(metadata={'year': 2010, 'director': 'Christopher Nolan', 'rating': 8.2, 'source': 'langchain'}, page_content='Leo DiCaprio gets lost in a dream within a dream within a dream within a ...'),
  0.227469339966774),
 (Document(metadata={'year': 2019, 'director': 'Greta Gerwig', 'rating': 8.3, 'source': 'langchain'}, page_content='A bunch of normal-sized women are supremely wholesome and some men pine after them'),
  0.19208428263664246),
 (Document(metadata={'year': 1993, 'rating': 7.7, 'genre': 'science fiction', 'source': 'langchain'}, page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose'),
  0.1902722418308258),
 (Document(metadata={'year': 2006, 'director': 'Satoshi Kon', 'rating': 8.6, 'source': 'langchain'}, page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea'),
  0.08151976019144058)]
```

```python
# This example only specifies a filter
vectara.vectara_query("I want to watch a movie rated higher than 8.5", config)
```

```output
[(Document(metadata={'year': 2006, 'director': 'Satoshi Kon', 'rating': 8.6, 'source': 'langchain'}, page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea'),
  0.34279149770736694),
 (Document(metadata={'year': 1979, 'rating': 9.9, 'director': 'Andrei Tarkovsky', 'genre': 'science fiction', 'source': 'langchain'}, page_content='Three men walk into the Zone, three men walk out of the Zone'),
  0.242923304438591)]
```

```python
# This example specifies a query and a filter
vectara.vectara_query("Has Greta Gerwig directed any movies about women", config)
```

```output
[(Document(metadata={'year': 2019, 'director': 'Greta Gerwig', 'rating': 8.3, 'source': 'langchain'}, page_content='A bunch of normal-sized women are supremely wholesome and some men pine after them'),
  0.10141132771968842)]
```

```python
# This example specifies a composite filter
vectara.vectara_query("What's a highly rated (above 8.5) science fiction film?", config)
```

```output
[(Document(metadata={'year': 1979, 'rating': 9.9, 'director': 'Andrei Tarkovsky', 'genre': 'science fiction', 'source': 'langchain'}, page_content='Three men walk into the Zone, three men walk out of the Zone'),
  0.9508692026138306)]
```

```python
# This example specifies a query and composite filter
vectara.vectara_query(
    "What's a movie after 1990 but before 2005 that's all about toys, and preferably is animated",
    config,
)
```

```output
[(Document(metadata={'year': 1995, 'genre': 'animated', 'source': 'langchain'}, page_content='Toys come alive and have a blast doing so'),
  0.7290377616882324),
 (Document(metadata={'year': 1993, 'rating': 7.7, 'genre': 'science fiction', 'source': 'langchain'}, page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose'),
  0.4838160574436188)]
```

```python

```
