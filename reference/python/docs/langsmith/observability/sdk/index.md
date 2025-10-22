---
title: LangSmith SDK - LangChain Reference
---

Welcome to the LangSmith Python SDK reference docs! These pages detail the core interfaces you will use when building with LangSmith's Observability and Evaluations tools.

--8<-- "wip.md"

## Quick Reference

| Class/function | Description |
| :- | :- |
| [`Client`](client.md) | Synchronous client for interacting with the LangSmith API. |
| [`AsyncClient`](async_client.md) | Asynchronous client for interacting with the LangSmith API. |
| [`traceable`](run_helpers.md) | Wrapper/decorator for tracing any function. |
| [`evaluate`](evaluation.md) | Evaluate a function or model on a dataset. |
| [`RunTree`](run_trees.md) | Tree structure representing a run and its nested runs. |
| [`wrap_openai`](wrappers.md) | Wrapper for OpenAI client, adds LangSmith tracing. |
| [`wrap_anthropic`](wrappers.md) | Wrapper for Anthropic client, adds LangSmith tracing. |

## Core APIs

The primary interfaces for the LangSmith SDK.

- [`Client`](client.md): Synchronous client for the LangSmith API.
- [`AsyncClient`](async_client.md): Asynchronous client for the LangSmith API.
- [Run Helpers](run_helpers.md): Functions like `traceable`, `trace`, and tracing context management.
- [Run Trees](run_trees.md): Tree structure for representing runs and nested runs.
- [Evaluation](evaluation.md): Tools for evaluating functions and models on datasets.

## Additional APIs

- [Schemas](schemas.md): Data schemas and type definitions.
- [Utilities](utils.md): Utility classes including error types and thread pool executors.
- [Wrappers](wrappers.md): Tracing wrappers for popular LLM providers.
- [Anonymizer](anonymizer.md): Tools for anonymizing sensitive data.
- [Testing](testing.md): Testing utilities and pytest integration.
- [Expect API](expect.md): Assertions and expectations for testing.
