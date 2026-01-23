---
title: Anthropic Middleware
---

# :simple-claude:{ .lg .middle } Anthropic Middleware

!!! note "Reference docs"

    This page contains **reference documentation** for Anthropic Middleware. See [the docs](https://docs.langchain.com/oss/python/langchain/middleware/built-in#anthropic) for conceptual guides, tutorials, and examples on using Anthropic Middleware.

Provider-specific middleware for Anthropic's Claude models:

| CLASS | DESCRIPTION |
| ----- | ----------- |
| [`AnthropicPromptCachingMiddleware`](#langchain_anthropic.middleware.AnthropicPromptCachingMiddleware) | Reduce costs by caching repetitive prompt prefixes |
| [`ClaudeBashToolMiddleware`](#langchain_anthropic.middleware.ClaudeBashToolMiddleware) | Execute Claude's native bash tool with local command execution |
| [`StateClaudeTextEditorMiddleware`](#langchain_anthropic.middleware.StateClaudeTextEditorMiddleware) | Provide Claude's text editor tool for state-based file editing |
| [`FilesystemClaudeTextEditorMiddleware`](#langchain_anthropic.middleware.FilesystemClaudeTextEditorMiddleware) | Provide Claude's text editor tool for filesystem-based file editing |
| [`StateClaudeMemoryMiddleware`](#langchain_anthropic.middleware.StateClaudeMemoryMiddleware) | Provide Claude's memory tool for state-based persistent agent memory |
| [`FilesystemClaudeMemoryMiddleware`](#langchain_anthropic.middleware.FilesystemClaudeMemoryMiddleware) | Provide Claude's memory tool for filesystem-based persistent agent memory |
| [`StateFileSearchMiddleware`](#langchain_anthropic.middleware.StateFileSearchMiddleware) | Search tools for state-based file systems |

<!-- TODO: `ignore_init_summary` doesn't seem to work.  -->

<!-- `"^__init__$"` used to exclude everything other than `__init__` -->

::: langchain_anthropic.middleware.AnthropicPromptCachingMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain_anthropic.middleware.ClaudeBashToolMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain_anthropic.middleware.StateClaudeTextEditorMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain_anthropic.middleware.FilesystemClaudeTextEditorMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain_anthropic.middleware.StateClaudeMemoryMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain_anthropic.middleware.FilesystemClaudeMemoryMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain_anthropic.middleware.StateFileSearchMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

<!-- Copy and paste the above for each new entry -->
<!-- (Don't use "members") -->
