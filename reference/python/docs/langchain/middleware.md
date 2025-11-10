!!! warning "Reference docs"

    This page contains **reference documentation** for Middleware. See [the docs](https://docs.langchain.com/oss/python/langchain/middleware) for conceptual guides, tutorials, and examples on using Middleware.

## Middleware classes

| CLASS | DESCRIPTION |
| -------------- | ----------- |
| [`ContextEditingMiddleware`](./#langchain.agents.middleware.ContextEditingMiddleware) | Edit context in agent workflows |
| [`HumanInTheLoopMiddleware`](./#langchain.agents.middleware.HumanInTheLoopMiddleware) | Enable human intervention in agent processes |
| [`LLMToolSelectorMiddleware`](./#langchain.agents.middleware.LLMToolSelectorMiddleware) | Select tools using LLM-based logic |
| [`LLMToolEmulator`](./#langchain.agents.middleware.LLMToolEmulator) | Emulate tool execution using LLM |
| [`ModelCallLimitMiddleware`](./#langchain.agents.middleware.ModelCallLimitMiddleware) | Limit the number of model calls |
| [`ModelFallbackMiddleware`](./#langchain.agents.middleware.ModelFallbackMiddleware) | Provide fallback model options |
| [`PIIMiddleware`](./#langchain.agents.middleware.PIIMiddleware) | Handle personally identifiable information |
| [`SummarizationMiddleware`](./#langchain.agents.middleware.SummarizationMiddleware) | Summarize content in agent workflows |
| [`TodoListMiddleware`](./#langchain.agents.middleware.TodoListMiddleware) | Manage TODO lists in agent processes |
| [`ToolCallLimitMiddleware`](./#langchain.agents.middleware.ToolCallLimitMiddleware) | Limit the number of tool calls |
| [`AgentMiddleware`](./#langchain.agents.middleware.AgentMiddleware) | Base middleware class for agent operations |

## Components and utilities

The following classes and functions provide the foundation for building and managing agent middleware:

| COMPONENT | DESCRIPTION |
| -------------- | ----------- |
| [`AgentState`](./#langchain.agents.middleware.AgentState) | Represent the state of an agent |
| [`ClearToolUsesEdit`](./#langchain.agents.middleware.ClearToolUsesEdit) | Function to clear tool usage edits |
| [`InterruptOnConfig`](./#langchain.agents.middleware.InterruptOnConfig) | Configuration class for interruption handling |
| [`ModelRequest`](./#langchain.agents.middleware.ModelRequest) | Represent a request to a model |
| [`ModelResponse`](./#langchain.agents.middleware.ModelResponse) | Represent a response from a model |
| [`before_model`](./#langchain.agents.middleware.before_model) | Function executed before model calls |
| [`after_model`](./#langchain.agents.middleware.after_model) | Function executed after model calls |
| [`wrap_model_call`](./#langchain.agents.middleware.wrap_model_call) | Function wrapper for model calls |
| [`wrap_tool_call`](./#langchain.agents.middleware.wrap_tool_call) | Function wrapper for tool calls |

<!-- `group_by_category false to allow custom ordering -->
<!-- `summary false since overriding above -->
::: langchain.agents.middleware
    options:
      summary: false
      group_by_category: false
      members:
        - ContextEditingMiddleware
        - HumanInTheLoopMiddleware
        - LLMToolSelectorMiddleware
        - LLMToolEmulator
        - ModelCallLimitMiddleware
        - ModelFallbackMiddleware
        - PIIMiddleware
        - PIIDetectionError
        - SummarizationMiddleware
        - TodoListMiddleware
        - ToolCallLimitMiddleware
        - AgentMiddleware
        - AgentState
        - ClearToolUsesEdit
        - InterruptOnConfig
        - ModelRequest
        - ModelResponse
        - before_model
        - after_model
        - wrap_model_call
        - wrap_tool_call
        - ModelRequest
