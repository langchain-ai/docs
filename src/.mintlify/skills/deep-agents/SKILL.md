---
name: deep-agents
description: Build batteries-included agents with planning, context management, subagent delegation, and sandboxed execution. Use for complex, multi-step tasks that need built-in capabilities.
license: MIT
compatibility: Python 3.10+, Node.js 20+. Requires a model that supports tool calling.
metadata:
  author: langchain-ai
  version: "1.0"
---

# Deep Agents

Deep Agents is the easiest way to start building agents powered by LLMs—with built-in capabilities for task planning, file systems for context management, subagent delegation, and long-term memory. It is an "agent harness" built on [LangChain](https://docs.langchain.com/oss/langchain/overview) core building blocks and the [LangGraph](https://docs.langchain.com/oss/langgraph/overview) runtime.

## When to use

Use Deep Agents when you need to:
- **Build agents fast** with sensible defaults and minimal configuration
- **Handle complex, multi-step tasks** that benefit from automatic planning
- **Manage context** with a built-in virtual filesystem for large inputs
- **Delegate subtasks** to specialized subagents
- **Run code safely** in sandboxed execution environments
- **Use a terminal agent** via the Deep Agents CLI

## When NOT to use

- For simple tool-calling agents without planning or subagents, use [LangChain](https://docs.langchain.com/oss/langchain/overview) agents instead—lighter weight
- For custom graph-based orchestration with explicit control flow, use [LangGraph](https://docs.langchain.com/oss/langgraph/overview) directly
- Deep Agents is the **highest-level abstraction**—it trades flexibility for convenience

## Install

```bash
# Python
pip install deepagents

# JavaScript/TypeScript
npm install deepagents langchain @langchain/core
```

## Quick reference

### Create a deep agent

```python
# pip install deepagents langchain-anthropic
from deepagents import create_deep_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]}
)
```

### Use the CLI

```bash
# Install the CLI
pip install deepagents-cli

# Run an interactive terminal agent
deepagents
```

### Built-in capabilities

| Capability | Description |
|-----------|-------------|
| Planning | Automatic task decomposition for complex requests |
| File system | Virtual filesystem for reading, writing, and managing context |
| Subagents | Spawn child agents for parallel subtask execution |
| Context management | Automatic context compression for long conversations |
| Sandboxed execution | Run code in isolated environments (Modal, Runloop, Daytona) |
| Protocols | ACP, MCP, and A2A support for interoperability |

## Key documentation

- [Overview](https://docs.langchain.com/oss/deepagents/overview)—What Deep Agents is and how it compares to LangChain and LangGraph
- [Quickstart](https://docs.langchain.com/oss/deepagents/quickstart)—Build your first deep agent
- [Customization](https://docs.langchain.com/oss/deepagents/customization)—Configure models, tools, and behavior
- [Context engineering](https://docs.langchain.com/oss/deepagents/context-engineering)—Manage context for complex tasks
- [Subagents](https://docs.langchain.com/oss/deepagents/subagents)—Delegate work to child agents
- [Sandboxes](https://docs.langchain.com/oss/deepagents/sandboxes)—Run code in isolated environments
- [CLI](https://docs.langchain.com/oss/deepagents/cli/overview)—Terminal agent interface
- [Deploy](https://docs.langchain.com/oss/deepagents/deploy)—Deploy to production

## API reference

For SDK class and method details, use the [LangChain API Reference](https://reference.langchain.com) site:
- MCP server: `https://reference.langchain.com/mcp`

## Related skills

- **langchain**—Core building blocks that Deep Agents is built on
- **langgraph**—Runtime that powers Deep Agents' durable execution
- **langsmith**—Trace, evaluate, and deploy your deep agents
