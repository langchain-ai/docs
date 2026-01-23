---
title: Middleware - Deep Agents
hide:
  - toc
---

# Deep Agents Middleware

!!! note "Reference docs"

    This page contains **reference documentation** for Middleware. See [the docs](https://docs.langchain.com/oss/python/deepagents/middleware) for conceptual guides, tutorials, and examples.

Middleware components add capabilities to deep agents through a composable architecture. Each middleware can provide tools, modify state, and inject system prompts.

<div class="grid cards" markdown>

-   :material-folder-open:{ .lg .middle } __`FilesystemMiddleware`__

    ---

    File operation tools: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`.

    [:octicons-arrow-right-24: Reference](filesystem.md)

-   :material-account-multiple:{ .lg .middle } __`SubAgentMiddleware`__

    ---

    Spawn specialized subagents via the `task` tool for context-isolated work.

    [:octicons-arrow-right-24: Reference](subagents.md)

-   :material-brain:{ .lg .middle } __`MemoryMiddleware`__

    ---

    Load agent context from `AGENTS.md` files at startup.

    [:octicons-arrow-right-24: Reference](memory.md)

-   :material-lightning-bolt:{ .lg .middle } __`SkillsMiddleware`__

    ---

    Discover and expose reusable skills from `SKILL.md` files.

    [:octicons-arrow-right-24: Reference](skills.md)

-   :material-text-box-outline:{ .lg .middle } __`SummarizationMiddleware`__

    ---

    Offload conversation history to backend storage to preserve context.

    [:octicons-arrow-right-24: Reference](summarization.md)

</div>
