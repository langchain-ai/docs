---
title: NeuralDB
---

NeuralDB is a CPU-friendly and fine-tunable retrieval engine developed by ThirdAI.

### **Initialization**

There are two initialization methods:

- From Scratch: Basic model
- From Checkpoint: Load a model that was previously saved

For all of the following initialization methods, the `thirdai_key` parameter can be ommitted if the `THIRDAI_KEY` environment variable is set.

ThirdAI API keys can be obtained at [www.thirdai.com/try-bolt/](https://www.thirdai.com/try-bolt/)

```python
from langchain_community.retrievers import NeuralDBRetriever

# From scratch
retriever = NeuralDBRetriever.from_scratch(thirdai_key="your-thirdai-key")

# From checkpoint
retriever = NeuralDBRetriever.from_checkpoint(
    # Path to a NeuralDB checkpoint. For example, if you call
    # retriever.save("/path/to/checkpoint.ndb") in one script, then you can
    # call NeuralDBRetriever.from_checkpoint("/path/to/checkpoint.ndb") in
    # another script to load the saved model.
    checkpoint="/path/to/checkpoint.ndb",
    thirdai_key="your-thirdai-key",
)
```

### **Inserting document sources**

```python
retriever.insert(
    # If you have PDF, DOCX, or CSV files, you can directly pass the paths to the documents
    sources=["/path/to/doc.pdf", "/path/to/doc.docx", "/path/to/doc.csv"],
    # When True this means that the underlying model in the NeuralDB will
    # undergo unsupervised pretraining on the inserted files. Defaults to True.
    train=True,
    # Much faster insertion with a slight drop in performance. Defaults to True.
    fast_mode=True,
)

from thirdai import neural_db as ndb

retriever.insert(
    # If you have files in other formats, or prefer to configure how
    # your files are parsed, then you can pass in NeuralDB document objects
    # like this.
    sources=[
        ndb.PDF(
            "/path/to/doc.pdf",
            version="v2",
            chunk_size=100,
            metadata={"published": 2022},
        ),
        ndb.Unstructured("/path/to/deck.pptx"),
    ]
)
```

### **Retrieving documents**

To query the retriever, you can use the standard LangChain retriever method `get_relevant_documents`, which returns a list of LangChain Document objects. Each document object represents a chunk of text from the indexed files. For example, it may contain a paragraph from one of the indexed PDF files. In addition to the text, the document's metadata field contains information such as the document's ID, the source of this document (which file it came from), and the score of the document.

```python
# This returns a list of LangChain Document objects
documents = retriever.invoke("query", top_k=10)
```

### **Fine tuning**

NeuralDBRetriever can be fine-tuned to user behavior and domain-specific knowledge. It can be fine-tuned in two ways:

1. Association: the retriever associates a source phrase with a target phrase. When the retriever sees the source phrase, it will also consider results that are relevant to the target phrase.
2. Upvoting: the retriever upweights the score of a document for a specific query. This is useful when you want to fine-tune the retriever to user behavior. For example, if a user searches "how is a car manufactured" and likes the returned document with id 52, then we can upvote the document with id 52 for the query "how is a car manufactured".

```python
retriever.associate(source="source phrase", target="target phrase")
retriever.associate_batch(
    [
        ("source phrase 1", "target phrase 1"),
        ("source phrase 2", "target phrase 2"),
    ]
)

retriever.upvote(query="how is a car manufactured", document_id=52)
retriever.upvote_batch(
    [
        ("query 1", 52),
        ("query 2", 20),
    ]
)
```
