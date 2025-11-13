!!! warning "Reference docs"

    This page contains **reference documentation** for Middleware. See [the docs](https://docs.langchain.com/oss/python/langchain/middleware) for conceptual guides, tutorials, and examples on using Middleware.

## Middleware classes

LangChain provides prebuilt middleware for common agent use cases:

| CLASS | DESCRIPTION |
| ----- | ----------- |
| [`SummarizationMiddleware`](./#langchain.agents.middleware.SummarizationMiddleware) | Automatically summarize conversation history when approaching token limits |
| [`HumanInTheLoopMiddleware`](./#langchain.agents.middleware.HumanInTheLoopMiddleware) | Pause execution for human approval of tool calls |
| [`ModelCallLimitMiddleware`](./#langchain.agents.middleware.ModelCallLimitMiddleware) | Limit the number of model calls to prevent excessive costs |
| [`ToolCallLimitMiddleware`](./#langchain.agents.middleware.ToolCallLimitMiddleware) | Control tool execution by limiting call counts |
| [`ModelFallbackMiddleware`](./#langchain.agents.middleware.ModelFallbackMiddleware) | Automatically fallback to alternative models when primary fails |
| [`PIIMiddleware`](./#langchain.agents.middleware.PIIMiddleware) | Detect and handle Personally Identifiable Information |
| [`TodoListMiddleware`](./#langchain.agents.middleware.TodoListMiddleware) | Equip agents with task planning and tracking capabilities |
| [`LLMToolSelectorMiddleware`](./#langchain.agents.middleware.LLMToolSelectorMiddleware) | Use an LLM to select relevant tools before calling main model |
| [`ToolRetryMiddleware`](./#langchain.agents.middleware.ToolRetryMiddleware) | Automatically retry failed tool calls with exponential backoff |
| [`LLMToolEmulator`](./#langchain.agents.middleware.LLMToolEmulator) | Emulate tool execution using LLM for testing purposes |
| [`ContextEditingMiddleware`](./#langchain.agents.middleware.ContextEditingMiddleware) | Manage conversation context by trimming or clearing tool uses |
| [`AgentMiddleware`](./#langchain.agents.middleware.AgentMiddleware) | Base middleware class for creating custom middleware |

## Decorators

Create custom middleware using these decorators:

| DECORATOR | DESCRIPTION |
| --------- | ----------- |
| [`@before_agent`](./#langchain.agents.middleware.before_agent) | Execute logic before agent execution starts |
| [`@before_model`](./#langchain.agents.middleware.before_model) | Execute logic before each model call |
| [`@after_model`](./#langchain.agents.middleware.after_model) | Execute logic after each model receives a response |
| [`@after_agent`](./#langchain.agents.middleware.after_agent) | Execute logic after agent execution completes |
| [`@wrap_model_call`](./#langchain.agents.middleware.wrap_model_call) | Wrap and intercept model calls |
| [`@wrap_tool_call`](./#langchain.agents.middleware.wrap_tool_call) | Wrap and intercept tool calls |
| [`@dynamic_prompt`](./#langchain.agents.middleware.dynamic_prompt) | Generate dynamic system prompts based on request context |
| [`@hook_config`](./#langchain.agents.middleware.hook_config) | Configure hook behavior (e.g., conditional routing) |

## Types and utilities

Core types for building middleware:

| TYPE | DESCRIPTION |
| ---- | ----------- |
| [`AgentState`](./#langchain.agents.middleware.AgentState) | State container for agent execution |
| [`ModelRequest`](./#langchain.agents.middleware.ModelRequest) | Request details passed to model calls |
| [`ModelResponse`](./#langchain.agents.middleware.ModelResponse) | Response details from model calls |
| [`ClearToolUsesEdit`](./#langchain.agents.middleware.ClearToolUsesEdit) | Utility for clearing tool usage history from context |
| [`InterruptOnConfig`](./#langchain.agents.middleware.InterruptOnConfig) | Configuration for human-in-the-loop interruptions |

<!-- Configuration notes:
- summary: false - Using custom tables above instead of auto-generated summaries
- group_by_category: false - Custom ordering via explicit members list
- filters: Show only __init__ for middleware classes; all members for other types
- inherited_members: false - Hide inherited members by default
- show_if_no_docstring: true - Show members even without docstrings
-->

::: langchain.agents.middleware
    options:
      summary: false
      group_by_category: false
      inherited_members: false
      show_if_no_docstring: true
      members:
        - SummarizationMiddleware
        - HumanInTheLoopMiddleware
        - ModelCallLimitMiddleware
        - ToolCallLimitMiddleware
        - ModelFallbackMiddleware
        - PIIMiddleware
        - TodoListMiddleware
        - LLMToolSelectorMiddleware
        - ToolRetryMiddleware
        - LLMToolEmulator
        - ContextEditingMiddleware
        - AgentMiddleware
        - before_agent
        - before_model
        - after_model
        - after_agent
        - wrap_model_call
        - wrap_tool_call
        - dynamic_prompt
        - hook_config
        - AgentState
        - ModelRequest
        - ModelResponse
        - ClearToolUsesEdit
        - InterruptOnConfig

::: langchain.agents.middleware.SummarizationMiddleware
    options:
      show_bases: false
      filters: ["^__init__$"]

::: langchain.agents.middleware.HumanInTheLoopMiddleware
    options:
      show_bases: false
      filters: ["^__init__$"]

::: langchain.agents.middleware.ModelCallLimitMiddleware
    options:
      show_bases: false
      members: ["__init__", "state_schema"]

::: langchain.agents.middleware.ToolCallLimitMiddleware
    options:
      show_bases: false
      members: ["__init__", "state_schema"]

::: langchain.agents.middleware.ModelFallbackMiddleware
    options:
      show_bases: false
      filters: ["^__init__$"]

::: langchain.agents.middleware.PIIMiddleware
    options:
      show_bases: false
      filters: ["^__init__$"]

::: langchain.agents.middleware.TodoListMiddleware
    options:
      show_bases: false
      members: ["__init__", "state_schema"]

::: langchain.agents.middleware.LLMToolSelectorMiddleware
    options:
      show_bases: false
      filters: ["^__init__$"]

::: langchain.agents.middleware.ToolRetryMiddleware
    options:
      show_bases: false
      filters: ["^__init__$"]

::: langchain.agents.middleware.LLMToolEmulator
    options:
      show_bases: false
      filters: ["^__init__$"]

::: langchain.agents.middleware.ContextEditingMiddleware
    options:
      show_bases: false
      filters: ["^__init__$"]
