---
title: Agents (LangGraph)
---

::: langgraph.prebuilt.chat_agent_executor
    options:
      members:
        - AgentState
        - create_react_agent

::: langgraph.prebuilt.tool_node
    options:
      show_docstring_description: true
      show_docstring_examples: true
      docstring_options:
        ignore_init_summary: true
      merge_init_into_class: true
      filters: ["^__init__$"]
      members:
        - ToolNode
        - InjectedState
        - InjectedStore
        - ToolRuntime
        - tools_condition

::: langgraph.prebuilt.tool_validator.ValidationNode
    options:
      show_if_no_docstring: true
      inherited_members: false
      members: false

::: langgraph.prebuilt.interrupt
    options:
      members:
        - HumanInterruptConfig
        - ActionRequest
        - HumanInterrupt
        - HumanResponse
