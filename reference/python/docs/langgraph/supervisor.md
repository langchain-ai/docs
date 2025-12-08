# :material-account-supervisor:{ .lg .middle } `langgraph-supervisor`

[![PyPI - Version](https://img.shields.io/pypi/v/langgraph-supervisor?label=%20)](https://pypi.org/project/langgraph-supervisor/#history)
[![PyPI - License](https://img.shields.io/pypi/l/langgraph-supervisor)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pepy/dt/langgraph-supervisor)](https://pypistats.org/packages/langgraph-supervisor)

!!! note

    We now recommend using the **supervisor pattern directly via tools** rather than this library for most use cases. The tool-calling approach gives you more control over context engineering and is the recommended pattern in the [LangChain multi-agent guide](https://docs.langchain.com/oss/python/langchain/multi-agent).

    See our [supervisor tutorial](https://docs.langchain.com/oss/python/langchain/supervisor) for a step-by-step guide.

    We're making this library compatible with LangChain 1.0 to help users upgrade their existing code. If you find this library solves a problem that can't be easily addressed with the manual supervisor pattern, we'd love to hear about your use case!

See the [project description](https://pypi.org/project/langgraph-supervisor/) for more details.

::: langgraph_supervisor.supervisor
    options:
      members:
        - create_supervisor

::: langgraph_supervisor.handoff
    options:
      members:
        - create_handoff_tool
        - create_forward_message_tool
