---
title: LangChain Core home
---

# :material-atom:{ .lg .middle } `langchain-core`

[![PyPI - Version](https://img.shields.io/pypi/v/langchain-core?label=%20)](https://pypi.org/project/langchain-core/#history)
[![PyPI - License](https://img.shields.io/pypi/l/langchain-core)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pepy/dt/langchain-core)](https://pypistats.org/packages/langchain-core)

Reference documentation for the [`langchain-core`](https://pypi.org/project/langchain-core/) package.

`langchain-core` contains the core interfaces and abstractions used across the LangChain ecosystem. Most users will primarily interact with the main [`langchain`](../langchain/langchain/index.md) package, which builds on top of `langchain-core` and provides implementations for all the core interfaces.

- [Caches](caches.md): Caching mechanisms.
- [Callbacks](callbacks.md): Callback handlers and management.
- [Documents](documents.md): Document abstractions.
- [Embeddings](embeddings.md): Embedding abstractions.
- [Exceptions](exceptions.md): Common LangChain exception types.
- [Language models](language_models.md): Base interfaces for language models.
- [Serialization](load.md): Components for serialization and deserialization.
- [Output parsers](output_parsers.md): Parsing model outputs.
- [Prompts](prompts.md): Prompt templates and related utilities.
- [Rate limiters](rate_limiters.md): Rate limiting utilities.
- [Retrievers](retrievers.md): Retriever interfaces and implementations.
- [Runnables](runnables.md): Runnables and related abstractions.
- [Utilities](utils.md): Various utility functions and classes.
- [Vector stores](vectorstores.md): Vector store interfaces and implementations.
