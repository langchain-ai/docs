!!! note "Reference docs"

    This page contains **reference documentation** for Middleware. See [the docs](https://docs.langchain.com/oss/python/langchain/middleware) for conceptual guides, tutorials, and examples on using Middleware.

## Middleware classes

LangChain provides prebuilt middleware for common agent use cases:

| CLASS | DESCRIPTION |
| ----- | ----------- |
| [`SummarizationMiddleware`](#langchain.agents.middleware.SummarizationMiddleware) | Automatically summarize conversation history when approaching token limits |
| [`HumanInTheLoopMiddleware`](#langchain.agents.middleware.HumanInTheLoopMiddleware) | Pause execution for human approval of tool calls |
| [`ModelCallLimitMiddleware`](#langchain.agents.middleware.ModelCallLimitMiddleware) | Limit the number of model calls to prevent excessive costs |
| [`ToolCallLimitMiddleware`](#langchain.agents.middleware.ToolCallLimitMiddleware) | Control tool execution by limiting call counts |
| [`ModelFallbackMiddleware`](#langchain.agents.middleware.ModelFallbackMiddleware) | Automatically fallback to alternative models when primary fails |
| [`PIIMiddleware`](#langchain.agents.middleware.PIIMiddleware) | Detect and handle Personally Identifiable Information |
| [`TodoListMiddleware`](#langchain.agents.middleware.TodoListMiddleware) | Equip agents with task planning and tracking capabilities |
| [`LLMToolSelectorMiddleware`](#langchain.agents.middleware.LLMToolSelectorMiddleware) | Use an LLM to select relevant tools before calling main model |
| [`ToolRetryMiddleware`](#langchain.agents.middleware.ToolRetryMiddleware) | Automatically retry failed tool calls with exponential backoff |
| [`LLMToolEmulator`](#langchain.agents.middleware.LLMToolEmulator) | Emulate tool execution using LLM for testing purposes |
| [`ContextEditingMiddleware`](#langchain.agents.middleware.ContextEditingMiddleware) | Manage conversation context by trimming or clearing tool uses |
| [`ShellToolMiddleware`](#langchain.agents.middleware.ShellToolMiddleware) | Expose a persistent shell session to agents for command execution |
| [`FilesystemFileSearchMiddleware`](#langchain.agents.middleware.FilesystemFileSearchMiddleware) | Provide Glob and Grep search tools over filesystem files |
| [`AgentMiddleware`](#langchain.agents.middleware.AgentMiddleware) | Base middleware class for creating custom middleware |

## Decorators

Create custom middleware using these decorators:

| DECORATOR | DESCRIPTION |
| --------- | ----------- |
| [`@before_agent`](#langchain.agents.middleware.before_agent) | Execute logic before agent execution starts |
| [`@before_model`](#langchain.agents.middleware.before_model) | Execute logic before each model call |
| [`@after_model`](#langchain.agents.middleware.after_model) | Execute logic after each model receives a response |
| [`@after_agent`](#langchain.agents.middleware.after_agent) | Execute logic after agent execution completes |
| [`@wrap_model_call`](#langchain.agents.middleware.wrap_model_call) | Wrap and intercept model calls |
| [`@wrap_tool_call`](#langchain.agents.middleware.wrap_tool_call) | Wrap and intercept tool calls |
| [`@dynamic_prompt`](#langchain.agents.middleware.dynamic_prompt) | Generate dynamic system prompts based on request context |
| [`@hook_config`](#langchain.agents.middleware.hook_config) | Configure hook behavior (e.g., conditional routing) |

## Types and utilities

Core types for building middleware:

| TYPE | DESCRIPTION |
| ---- | ----------- |
| [`AgentState`](#langchain.agents.middleware.AgentState) | State container for agent execution |
| [`ModelRequest`](#langchain.agents.middleware.ModelRequest) | Request details passed to model calls |
| [`ModelResponse`](#langchain.agents.middleware.ModelResponse) | Response details from model calls |
| [`ClearToolUsesEdit`](#langchain.agents.middleware.ClearToolUsesEdit) | Utility for clearing tool usage history from context |
| [`InterruptOnConfig`](#langchain.agents.middleware.InterruptOnConfig) | Configuration for human-in-the-loop interruptions |

[`SummarizationMiddleware`](#langchain.agents.middleware.SummarizationMiddleware) types:

| TYPE | DESCRIPTION |
| ---- | ----------- |
| [`ContextSize`](#langchain.agents.middleware.summarization.ContextSize) | Union type |
| [`ContextFraction`](#langchain.agents.middleware.summarization.ContextFraction) | Summarize at fraction of total context |
| [`ContextTokens`](#langchain.agents.middleware.summarization.ContextTokens) | Summarize at token threshold |
| [`ContextMessages`](#langchain.agents.middleware.summarization.ContextMessages) | Summarize at message threshold |

<!-- TODO: `ignore_init_summary` doesn't seem to work.  -->

::: langchain.agents.middleware.SummarizationMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.HumanInTheLoopMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.ModelCallLimitMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^(__init__|state_schema)$"]

::: langchain.agents.middleware.ToolCallLimitMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^(__init__|state_schema)$"]

::: langchain.agents.middleware.ModelFallbackMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.PIIMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.TodoListMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^(__init__|state_schema)$"]

::: langchain.agents.middleware.LLMToolSelectorMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.ToolRetryMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.LLMToolEmulator
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.ContextEditingMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.ShellToolMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.FilesystemFileSearchMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.AgentMiddleware
    options:
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]

::: langchain.agents.middleware.before_agent

::: langchain.agents.middleware.before_model

::: langchain.agents.middleware.after_model

::: langchain.agents.middleware.after_agent

::: langchain.agents.middleware.wrap_model_call

::: langchain.agents.middleware.wrap_tool_call

::: langchain.agents.middleware.dynamic_prompt

::: langchain.agents.middleware.hook_config

::: langchain.agents.middleware.AgentState
    options:
      merge_init_into_class: true

::: langchain.agents.middleware.ModelRequest
    options:
      merge_init_into_class: true

::: langchain.agents.middleware.ModelResponse
    options:
      merge_init_into_class: true

::: langchain.agents.middleware.ClearToolUsesEdit
    options:
      merge_init_into_class: true

::: langchain.agents.middleware.InterruptOnConfig
    options:
      merge_init_into_class: true

<!-- Summarization types -->

::: langchain.agents.middleware.summarization.ContextSize
::: langchain.agents.middleware.summarization.ContextFraction
::: langchain.agents.middleware.summarization.ContextTokens
::: langchain.agents.middleware.summarization.ContextMessages

<!-- Copy and paste the above for each new entry -->
<!-- (Don't use "members") -->
