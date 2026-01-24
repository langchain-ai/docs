---
title: Backends
hide:
  - toc
---

# Backends

!!! note "Reference docs"

    This page contains **reference documentation** for Backends. See [the docs](https://docs.langchain.com/oss/python/deepagents/backends) for conceptual guides, tutorials, and examples.

Backends provide a unified interface for file operations across different storage types. All backends implement the `BackendProtocol`, enabling agents to work with files regardless of where they're stored.

<div class="grid cards" markdown>

-   :material-memory:{ .lg .middle } __`BackendProtocol`__

    ---

    Abstract protocol defining the interface all backends must implement.

    [:octicons-arrow-right-24: Reference](protocol.md)

-   :material-state-machine:{ .lg .middle } __`StateBackend`__

    ---

    In-memory backend using LangGraph state. Ephemeral, thread-local storage.

    [:octicons-arrow-right-24: Reference](state.md)

-   :material-database:{ .lg .middle } __`StoreBackend`__

    ---

    Persistent backend using LangGraph's BaseStore. Cross-thread storage.

    [:octicons-arrow-right-24: Reference](store.md)

-   :material-folder:{ .lg .middle } __`FilesystemBackend`__

    ---

    Real filesystem access with optional virtual mode.

    [:octicons-arrow-right-24: Reference](filesystem.md)

-   :material-bash:{ .lg .middle } __`BaseSandbox`__

    ---

    Base class for backends supporting shell command execution.

    [:octicons-arrow-right-24: Reference](sandbox.md)

-   :material-source-branch:{ .lg .middle } __`CompositeBackend`__

    ---

    Router that delegates operations to different backends by path prefix.

    [:octicons-arrow-right-24: Reference](composite.md)

</div>
