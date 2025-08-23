# How to use a time-weighted vector store retriever

This [retriever](/oss/concepts/retrievers/) uses a combination of semantic [similarity](/oss/concepts/embedding_models/#measure-similarity) and a time decay.

The algorithm for scoring them is:

```
semantic_similarity + (1.0 - decay_rate) ^ hours_passed
```

Notably, `hours_passed` refers to the hours passed since the object in the retriever **was last accessed**, not since it was created. This means that frequently accessed objects remain "fresh".



```python
from datetime import datetime, timedelta

import faiss
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
```

## Low decay rate

A low `decay rate` (in this, to be extreme, we will set it close to 0) means memories will be "remembered" for longer. A `decay rate` of 0 means memories never be forgotten, making this retriever equivalent to the vector lookup.



```python
# Define your embedding model
embeddings_model = OpenAIEmbeddings()
# Initialize the vectorstore as empty
embedding_size = 1536
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(embeddings_model, index, InMemoryDocstore({}), {})
retriever = TimeWeightedVectorStoreRetriever(
    vectorstore=vectorstore, decay_rate=0.0000000000000000000000001, k=1
)
```


```python
yesterday = datetime.now() - timedelta(days=1)
retriever.add_documents(
    [Document(page_content="hello world", metadata={"last_accessed_at": yesterday})]
)
retriever.add_documents([Document(page_content="hello foo")])
```



```output
['73679bc9-d425-49c2-9d74-de6356c73489']
```



```python
# "Hello World" is returned first because it is most salient, and the decay rate is close to 0., meaning it's still recent enough
retriever.invoke("hello world")
```



```output
[Document(metadata={'last_accessed_at': datetime.datetime(2024, 10, 22, 16, 37, 40, 818583), 'created_at': datetime.datetime(2024, 10, 22, 16, 37, 37, 975074), 'buffer_idx': 0}, page_content='hello world')]
```


## High decay rate

With a high `decay rate` (e.g., several 9's), the `recency score` quickly goes to 0! If you set this all the way to 1, `recency` is 0 for all objects, once again making this equivalent to a vector lookup.




```python
# Define your embedding model
embeddings_model = OpenAIEmbeddings()
# Initialize the vectorstore as empty
embedding_size = 1536
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(embeddings_model, index, InMemoryDocstore({}), {})
retriever = TimeWeightedVectorStoreRetriever(
    vectorstore=vectorstore, decay_rate=0.999, k=1
)
```


```python
yesterday = datetime.now() - timedelta(days=1)
retriever.add_documents(
    [Document(page_content="hello world", metadata={"last_accessed_at": yesterday})]
)
retriever.add_documents([Document(page_content="hello foo")])
```



```output
['379631f0-42c2-4773-8cc2-d36201e1e610']
```



```python
# "Hello Foo" is returned first because "hello world" is mostly forgotten
retriever.invoke("hello world")
```



```output
[Document(metadata={'last_accessed_at': datetime.datetime(2024, 10, 22, 16, 37, 46, 553633), 'created_at': datetime.datetime(2024, 10, 22, 16, 37, 43, 927429), 'buffer_idx': 1}, page_content='hello foo')]
```


## Virtual time

Using some utils in LangChain, you can mock out the time component.



```python
from langchain_core.utils import mock_now
```


```python
# Notice the last access time is that date time

tomorrow = datetime.now() + timedelta(days=1)

with mock_now(tomorrow):
    print(retriever.invoke("hello world"))
```
```output
[Document(metadata={'last_accessed_at': MockDateTime(2024, 10, 23, 16, 38, 19, 66711), 'created_at': datetime.datetime(2024, 10, 22, 16, 37, 43, 599877), 'buffer_idx': 0}, page_content='hello world')]
```

```python

```
