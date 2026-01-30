---
title: Google (VertexAI)
---

# :simple-googlecloud:{ .lg .middle } `langchain-google-vertexai`

[![PyPI - Version](https://img.shields.io/pypi/v/langchain-google-vertexai?label=%20)](https://pypi.org/project/langchain-google-vertexai/#history)
[![PyPI - License](https://img.shields.io/pypi/l/langchain-google-vertexai)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pepy/dt/langchain-google-vertexai)](https://pypistats.org/packages/langchain-google-vertexai)

LangChain integration for Google's Vertex AI Platform.

!!! note "Vertex AI consolidation"

    As of `langchain-google-vertexai` 3.2.0, certain classes are deprecated in favor of equivalents in `langchain-google-genai` 4.0.0, which uses the consolidated [`google-genai`](https://googleapis.github.io/python-genai/) SDK.

    Refer to [the provider docs](https://docs.langchain.com/oss/python/integrations/providers/google) and [release notes](https://github.com/langchain-ai/langchain-google/discussions/1422) for more information.

## Modules

!!! note "Usage documentation"
    Refer to [the docs](https://docs.langchain.com/oss/python/integrations/providers/google) for a high-level guide on how to use each module. These reference pages contain auto-generated API documentation for each module, focusing on the "what" rather than the "how" or "why" (i.e. no end-to-end tutorials or conceptual overviews).

<div class="grid cards" markdown>

- :material-message-text:{ .lg .middle } **`ChatVertexAI`**

    ---

    **Deprecated:** Use `ChatGoogleGenerativeAI` from `langchain-google-genai` instead.

    [:octicons-arrow-right-24: Reference](./ChatVertexAI.md)

- :material-message-text:{ .lg .middle } **`VertexAI`**

    ---

    **Deprecated:** Use `GoogleGenerativeAI` from `langchain-google-genai` instead.

    [:octicons-arrow-right-24: Reference](./VertexAI.md)

- :fontawesome-solid-layer-group:{ .lg .middle } **`VertexAIEmbeddings`**

    ---

    **Deprecated:** Use `GoogleGenerativeAIEmbeddings` from `langchain-google-genai` instead.

    [:octicons-arrow-right-24: Reference](./VertexAIEmbeddings.md)

- **Other**

    ---

    [:octicons-arrow-right-24: Reference](./other.md)

</div>
