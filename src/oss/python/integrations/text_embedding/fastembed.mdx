---
title: FastEmbed by Qdrant
---

>[FastEmbed](https://qdrant.github.io/fastembed/) from [Qdrant](https://qdrant.tech) is a lightweight, fast, Python library built for embedding generation.
>
>- Quantized model weights
>- ONNX Runtime, no PyTorch dependency
>- CPU-first design
>- Data-parallelism for encoding of large datasets.

## Dependencies

To use FastEmbed with LangChain, install the `fastembed` Python package.

```python
%pip install -qU  fastembed
```

## Imports

```python
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
```

## Instantiating FastEmbed

### Parameters

- `model_name: str` (default: "BAAI/bge-small-en-v1.5")
        > Name of the FastEmbedding model to use. You can find the list of supported models [here](https://qdrant.github.io/fastembed/examples/Supported_Models/).

- `max_length: int` (default: 512)
        > The maximum number of tokens. Unknown behavior for values > 512.

- `cache_dir: Optional[str]` (default: None)
        > The path to the cache directory. Defaults to `local_cache` in the parent directory.

- `threads: Optional[int]` (default: None)
        > The number of threads a single onnxruntime session can use.

- `doc_embed_type: Literal["default", "passage"]` (default: "default")
        > "default": Uses FastEmbed's default embedding method.

        > "passage": Prefixes the text with "passage" before embedding.

- `batch_size: int` (default: 256)
        > Batch size for encoding. Higher values will use more memory, but be faster.

- `parallel: Optional[int]` (default: None)

        > If `>1`, data-parallel encoding will be used, recommended for offline encoding of large datasets.
        > If `0`, use all available cores.
        > If `None`, don't use data-parallel processing, use default onnxruntime threading instead.

```python
embeddings = FastEmbedEmbeddings()
```

## Usage

### Generating document embeddings

```python
document_embeddings = embeddings.embed_documents(
    ["This is a document", "This is some other document"]
)
```

### Generating query embeddings

```python
query_embeddings = embeddings.embed_query("This is a query")
```
