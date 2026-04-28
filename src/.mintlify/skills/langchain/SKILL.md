---
name: langchain
description: Build agents with a prebuilt architecture and integrations for any model or tool. Use when creating tool-calling agents, switching model providers, or adding structured output.
license: MIT
compatibility: Python 3.10+, Node.js 20+
metadata:
  author: langchain-ai
  version: "1.0"
---

# LangChain

LangChain is an open-source framework with a prebuilt agent architecture and integrations for any model or tool. Build agents and LLM-powered applications in under 10 lines of code, with integrations for OpenAI, Anthropic, Google, and hundreds more.

## When to use

Use LangChain when you need to:
- **Build tool-calling agents** with `create_agent()` and a prebuilt agent loop
- **Switch model providers** without changing application code via `init_chat_model()`
- **Add structured output** to parse LLM responses into typed objects
- **Integrate with any model or tool** using LangChain's provider packages
- **Use middleware** for cross-cutting concerns like rate limiting and caching

## When NOT to use

- For complex multi-step workflows with custom control flow, use [LangGraph](https://docs.langchain.com/oss/langgraph/overview) instead
- For a batteries-included agent with planning, subagents, and context management, use [Deep Agents](https://docs.langchain.com/oss/deepagents/overview) instead
- LangChain provides the **core building blocks**; LangGraph adds orchestration; Deep Agents adds high-level capabilities on top

## Install

```bash
# Python
pip install -U langchain

# JavaScript/TypeScript
npm install langchain @langchain/core
```

Install a provider integration:

```bash
# Python
pip install -U langchain-openai       # or langchain-anthropic, langchain-google-genai

# JavaScript/TypeScript
npm install @langchain/openai         # or @langchain/anthropic, @langchain/google-genai
```

## Quick reference

### Create an agent

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="openai:gpt-5.4",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]}
)
```

### Initialize a chat model

```python
from langchain.chat_models import init_chat_model

# Switch providers by changing the string
model = init_chat_model("openai:gpt-5.4")
model = init_chat_model("anthropic:claude-opus-4-6")
model = init_chat_model("google_genai:gemini-2.5-flash-lite")
```

### Define a tool

```python
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search the web for information."""
    return "search results"
```

## Gotchas

1. **Snake_case tool names**—Tool function names must be valid Python identifiers. Use `get_weather`, not `get-weather`.
2. **Reserved parameters**—Do not name tool parameters `type`, `name`, or `description` as these conflict with the tool schema.
3. **Provider packages**—Models live in separate packages (e.g., `langchain-openai`). The base `langchain` package does not include providers.
4. **Model string format**—Use `"provider:model-name"` format with `init_chat_model()` (e.g., `"openai:gpt-5.4"`).

## Key documentation

- [Overview](https://docs.langchain.com/oss/langchain/overview)—What LangChain is and how to get started
- [Quickstart](https://docs.langchain.com/oss/langchain/quickstart)—Build your first agent
- [Agents](https://docs.langchain.com/oss/langchain/agents)—Prebuilt agent architecture
- [Models](https://docs.langchain.com/oss/langchain/models)—Chat models and provider integrations
- [Tools](https://docs.langchain.com/oss/langchain/tools)—Define and use tools
- [Structured output](https://docs.langchain.com/oss/langchain/structured-output)—Parse LLM responses into typed objects
- [MCP integration](https://docs.langchain.com/oss/langchain/mcp)—Use Model Context Protocol servers as tools

## API reference

For SDK class and method details, use the [LangChain API Reference](https://reference.langchain.com) site:
- Browse: `https://reference.langchain.com/python/langchain-core`
- MCP server: `https://reference.langchain.com/mcp`

## Related skills

- **langgraph**—Low-level orchestration for stateful, durable agent workflows
- **deep-agents**—Batteries-included agent harness built on LangChain
- **langsmith**—Trace, evaluate, and deploy your LangChain agents
