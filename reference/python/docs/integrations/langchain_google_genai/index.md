---
title: Google (GenAI)
---

# :simple-googlegemini:{ .lg .middle } `langchain-google-genai`

[![PyPI - Version](https://img.shields.io/pypi/v/langchain-google-genai?label=%20)](https://pypi.org/project/langchain-google-genai/#history)
[![PyPI - License](https://img.shields.io/pypi/l/langchain-google-genai)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pepy/dt/langchain-google-genai)](https://pypistats.org/packages/langchain-google-genai)

LangChain integration for Google's Generative AI models, providing access to Gemini models via both the **Gemini Developer API** and **Vertex AI**.

!!! note "Vertex AI consolidation"

    As of `langchain-google-genai` 4.0.0, this package uses the consolidated [`google-genai`](https://googleapis.github.io/python-genai/) SDK instead of the legacy [`google-ai-generativelanguage`](https://googleapis.dev/python/generativelanguage/latest/) SDK.

    This migration brings support for Gemini models both via the Gemini Developer API and Gemini API in Vertex AI, superseding certain classes in `langchain-google-vertexai`, such as `ChatVertexAI`. Refer to [the provider docs](https://docs.langchain.com/oss/python/integrations/providers/google) and [release notes](https://github.com/langchain-ai/langchain-google/discussions/1422) for more information.

## Modules

!!! note "Usage documentation"
    Refer to [the docs](https://docs.langchain.com/oss/python/integrations/providers/google) for a high-level guide on how to use each module. These reference pages contain auto-generated API documentation for each module, focusing on the "what" rather than the "how" or "why" (i.e. no end-to-end tutorials or conceptual overviews).

<div class="grid cards" markdown>

- :material-message-text:{ .lg .middle } __`ChatGoogleGenerativeAI`__

    ---

    Gemini chat models.

    [:octicons-arrow-right-24: Reference](./ChatGoogleGenerativeAI.md)

- :material-message-text:{ .lg .middle } __`GoogleGenerativeAI`__

    ---

    (Legacy) Google text completion abstraction.

    [:octicons-arrow-right-24: Reference](./GoogleGenerativeAI.md)

- :fontawesome-solid-layer-group:{ .lg .middle } __`GoogleGenerativeAIEmbeddings`__

    ---

    Gemini embedding models.

    [:octicons-arrow-right-24: Reference](./GoogleGenerativeAIEmbeddings.md)

</div>
