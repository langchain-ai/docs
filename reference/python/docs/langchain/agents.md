!!! note "Reference docs"

    This page contains **reference documentation** for Agents. See [the docs](https://docs.langchain.com/oss/python/langchain/agents) for conceptual guides, tutorials, and examples on using Agents.

<!-- Intentionally want to highlight `create_agent` on this page first -->
<!-- (`group_by_category orders `AgentState` (a class) before functions) -->
::: langchain.agents
    options:
      summary: false
      group_by_category: false
      parameter_headings: true
      members:
        - create_agent
        - AgentState
        - before_model
        - after_model
        - wrap_model_call
        - wrap_tool_call
        - dynamic-prompt
        - ModelRequest

---

## Structured output

::: langchain.agents.structured_output.ResponseFormat
::: langchain.agents.structured_output.ToolStrategy
    options:
      merge_init_into_class: true
      filters: ["!^schema$", "!^schema_specs$"]
::: langchain.agents.structured_output.ProviderStrategy
    options:
      merge_init_into_class: true
      filters: ["!^schema$", "!^schema_spec$"]
::: langchain.agents.structured_output.AutoStrategy
    options:
      merge_init_into_class: true
      filters: ["!^schema$"]
