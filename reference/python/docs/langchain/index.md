---
title: LangChain overview
hide:
  - toc
---

Welcome to the [LangChain](https://github.com/langchain-ai/langchain) package reference documentation!

Most users will primarily interact with the main [`langchain`](./langchain/index.md) package, which provides the complete set of implementations for building LLM applications. The packages below form the foundation of the LangChain ecosystem, each serving a specific purpose in the architecture:

<div class="grid cards" markdown>

- :simple-langchain:{ .lg .middle } __`langchain`__

    ---

    The main entrypoint containing all implementations you need for building applications with LLMs.

    [:octicons-arrow-right-24: Reference](./langchain/index.md)

- :material-atom:{ .lg .middle } __`langchain-core`__

    ---

    Core interfaces and abstractions used across the LangChain ecosystem.

    [:octicons-arrow-right-24: Reference](../langchain_core/index.md)

- :material-format-text:{ .lg .middle } __`langchain-text-splitters`__

    ---

    Text splitting utilities for document processing.

    [:octicons-arrow-right-24: Reference](../langchain_text_splitters/index.md)

- :fontawesome-solid-down-left-and-up-right-to-center:{ .lg .middle } __`langchain-mcp-adapters`__

    ---

    Make MCP tools available in LangChain and LangGraph applications.

    [:octicons-arrow-right-24: Reference](../langchain_mcp_adapters/index.md)

- :material-test-tube:{ .lg .middle } __`langchain-tests`__

    ---

    Standard tests suite used to validate LangChain integration package implementations.

    [:octicons-arrow-right-24: Reference](../langchain_tests/index.md)

- :fontawesome-solid-building-columns:{ .lg .middle } __`langchain-classic`__

    ---

    Legacy `langchain` implementations and components.

    [:octicons-arrow-right-24: Reference](../langchain_classic/index.md)

</div>

!!! info "Integration Packages"

    Looking for integrations with specific providers and services? Check out the [integrations reference](../integrations/index.md) for packages that connect with popular LLM providers, vector stores, tools, and other services.
