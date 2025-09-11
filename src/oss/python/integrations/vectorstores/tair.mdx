---
title: Tair
---

>[Tair](https://www.alibabacloud.com/help/en/tair/latest/what-is-tair) is a cloud native in-memory database service developed by `Alibaba Cloud`.
It provides rich data models and enterprise-grade capabilities to support your real-time online scenarios while maintaining full compatibility with open-source `Redis`. `Tair` also introduces persistent memory-optimized instances that are based on the new non-volatile memory (NVM) storage medium.

This notebook shows how to use functionality related to the `Tair` vector database.

You'll need to install `langchain-community` with `pip install -qU langchain-community` to use this integration

To run, you should have a `Tair` instance up and running.

```python
from langchain_community.embeddings.fake import FakeEmbeddings
from langchain_community.vectorstores import Tair
from langchain_text_splitters import CharacterTextSplitter
```

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = FakeEmbeddings(size=128)
```

Connect to Tair using the `TAIR_URL` environment variable

```
export TAIR_URL="redis://{username}:{password}@{tair_address}:{tair_port}"
```

or the keyword argument `tair_url`.

Then store documents and embeddings into Tair.

```python
tair_url = "redis://localhost:6379"

# drop first if index already exists
Tair.drop_index(tair_url=tair_url)

vector_store = Tair.from_documents(docs, embeddings, tair_url=tair_url)
```

Query similar documents.

```python
query = "What did the president say about Ketanji Brown Jackson"
docs = vector_store.similarity_search(query)
docs[0]
```

Tair Hybrid Search Index build

```python
# drop first if index already exists
Tair.drop_index(tair_url=tair_url)

vector_store = Tair.from_documents(
    docs, embeddings, tair_url=tair_url, index_params={"lexical_algorithm": "bm25"}
)
```

Tair Hybrid Search

```python
query = "What did the president say about Ketanji Brown Jackson"
# hybrid_ratio: 0.5 hybrid search, 0.9999 vector search, 0.0001 text search
kwargs = {"TEXT": query, "hybrid_ratio": 0.5}
docs = vector_store.similarity_search(query, **kwargs)
docs[0]
```
