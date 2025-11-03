---
title: LangGraph overview
hide:
  - toc
---

[![PyPI - Version](https://img.shields.io/pypi/v/langgraph?label=%20)](https://pypi.org/project/langgraph/#history)
[![PyPI - License](https://img.shields.io/pypi/l/langgraph)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pepy/dt/langgraph)](https://pypistats.org/packages/langgraph)

Welcome to the LangGraph reference docs!

These pages detail the core interfaces you will use when building with LangGraph. Each section covers a different part of the ecosystem.

## :simple-langgraph:{ .lg .middle } `langgraph`

The core APIs for the LangGraph open source library.

- [Graphs](graphs.md): Main graph abstraction and usage.
- [Functional API](func.md): Functional programming interface for graphs.
- [Pregel](pregel.md): Pregel-inspired computation model.
- [Checkpointing](checkpoints.md): Saving and restoring graph state.
- [Storage](store.md): Storage backends and options.
- [Caching](cache.md): Caching mechanisms for performance.
- [Types](types.md): Type definitions for graph components.
- [Runtime](runtime.md): Runtime configuration and options.
- [Config](config.md): Configuration options.
- [Errors](errors.md): Error types and handling.
- [Constants](constants.md): Global constants.
- [Channels](channels.md): Message passing and channels.

!!! tip "Model Context Protocol (MCP) support"

    To use MCP tools in your LangGraph application, check out [`langchain-mcp-adapters`](../langchain_mcp_adapters/index.md).

## :material-package-check:{ .lg .middle } Prebuilt components

Higher-level abstractions for common workflows, agents, and other patterns.

- [Agents](agents.md): Built-in agent patterns.
- [Supervisor](supervisor.md): Orchestration and delegation.
- [Swarm](swarm.md): Multi-agent collaboration.
