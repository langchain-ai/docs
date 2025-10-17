# Middleware

<!-- `group_by_category false to allow custom ordering -->
::: langchain.agents.middleware
    options:
      summary:
        # <https://mkdocstrings.github.io/python/usage/configuration/members/#summary>
        classes: true
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
        - TodoListMiddleWare
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
        - dynamic-prompt
        - ModelRequest
