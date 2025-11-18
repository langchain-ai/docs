---
title: Anthropic Middleware
---

!!! warning "Reference docs"

    This page contains **reference documentation** for Anthropic Middleware. See [the docs](https://docs.langchain.com/oss/python/langchain/middleware/built-in#anthropic) for conceptual guides, tutorials, and examples on using Anthropic Middleware.

## Middleware classes

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

<!-- Configuration notes:
- summary: false - Using custom tables above instead of auto-generated summaries
- group_by_category: false - Custom ordering via explicit members list
- members: Show only __init__ for middleware classes
- inherited_members: false - Hide inherited members by default
- show_if_no_docstring: true - Show members even without docstrings
-->

<!-- Module-level documentation removed to avoid duplicates - using explicit class blocks below -->

::: langchain_anthropic.middleware.AnthropicPromptCachingMiddleware
    options:
      show_bases: false
      members:
        - __init__

::: langchain_anthropic.middleware.ClaudeBashToolMiddleware
    options:
      show_bases: false
      members:
        - __init__

::: langchain_anthropic.middleware.StateClaudeTextEditorMiddleware
    options:
      show_bases: false
      members:
        - __init__

::: langchain_anthropic.middleware.FilesystemClaudeTextEditorMiddleware
    options:
      show_bases: false
      members:
        - __init__

::: langchain_anthropic.middleware.StateClaudeMemoryMiddleware
    options:
      show_bases: false
      members:
        - __init__

::: langchain_anthropic.middleware.FilesystemClaudeMemoryMiddleware
    options:
      show_bases: false
      members:
        - __init__

::: langchain_anthropic.middleware.StateFileSearchMiddleware
    options:
      show_bases: false
      members:
        - __init__
