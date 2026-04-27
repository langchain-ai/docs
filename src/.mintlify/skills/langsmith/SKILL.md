---
name: langsmith
description: Trace, evaluate, and deploy AI agents and LLM applications with LangSmith. Use when adding observability, running evaluations, engineering prompts, or deploying agents to production.
license: MIT
compatibility: Framework-agnostic. Works with LangChain, LangGraph, Deep Agents, OpenAI Agents SDK, CrewAI, Pydantic AI, and more.
metadata:
  author: langchain-ai
  version: "1.0"
---

# LangSmith

LangSmith is a framework-agnostic platform for building, debugging, and deploying AI agents and LLM applications. Trace requests, evaluate outputs, test prompts, and manage deployments all in one place at [smith.langchain.com](https://smith.langchain.com).

## When to use

Use LangSmith when you need to:
- **Trace and debug** LLM calls, agent steps, retrieval, and tool use
- **Evaluate** LLM outputs with automated or human-in-the-loop scoring
- **Engineer prompts** with a visual playground and version control
- **Deploy agents** to production with the LangGraph-based agent server
- **Monitor** production systems with dashboards, alerts, and cost tracking

## When NOT to use

- To build agent logic or LLM pipelines, use [LangChain](https://docs.langchain.com/oss/langchain/overview), [LangGraph](https://docs.langchain.com/oss/langgraph/overview), or [Deep Agents](https://docs.langchain.com/oss/deepagents/overview) instead
- LangSmith is the **platform layer** that complements these frameworks

## Quick setup

Set two environment variables to enable tracing from any supported framework:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="your-api-key"  # from smith.langchain.com/settings
```

### Install the SDK

```bash
# Python
pip install langsmith

# JavaScript/TypeScript
npm install langsmith
```

### Verify tracing

```python
from langsmith import traceable

@traceable
def my_function(query: str) -> str:
    # Your LLM logic here—all calls inside are traced automatically
    return "result"
```

## Core capabilities

| Capability | Description |
|-----------|-------------|
| Observability | Trace every step of your LLM app with automatic or manual instrumentation |
| Evaluation | Run evaluations with code, LLM-as-judge, or composite evaluators |
| Prompt engineering | Create, version, and test prompts in a visual playground |
| Agent deployment | Deploy LangGraph agents with streaming, human-in-the-loop, and durable execution |
| Monitoring | Dashboards, alerts, and cost tracking for production workloads |

## Key documentation

- [Overview](https://docs.langchain.com/langsmith/home)—Get started with LangSmith
- [Observability quickstart](https://docs.langchain.com/langsmith/observability-quickstart)—Add tracing in minutes
- [Evaluation quickstart](https://docs.langchain.com/langsmith/evaluation-quickstart)—Run your first evaluation
- [Prompt engineering quickstart](https://docs.langchain.com/langsmith/prompt-engineering-quickstart)—Iterate on prompts
- [Deployment quickstart](https://docs.langchain.com/langsmith/deployment-quickstart)—Deploy an agent
- [Integrations](https://docs.langchain.com/langsmith/integrations)—Connect your framework or provider
- [Create account & API key](https://docs.langchain.com/langsmith/create-account-api-key)—Account setup

## API reference

For SDK class and method details, use the [LangChain API Reference](https://reference.langchain.com) site:
- Browse: `https://reference.langchain.com/python/langsmith`
- MCP server: `https://reference.langchain.com/mcp`

## Related skills

- **langchain**—Build agents with prebuilt architecture and model integrations
- **langgraph**—Orchestrate stateful, durable agent workflows
- **deep-agents**—Batteries-included agent harness with planning and subagents
