---
name: langgraph
description: Build stateful, durable agent workflows with LangGraph. Use when you need custom graph-based control flow, human-in-the-loop, persistence, or multi-agent orchestration.
license: MIT
compatibility: Python 3.10+, Node.js 20+
metadata:
  author: langchain-ai
  version: "1.0"
---

# LangGraph

LangGraph is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents. It provides durable execution, streaming, human-in-the-loop interactions, and time-travel debugging.

## When to use

Use LangGraph when you need to:
- **Design custom agent workflows** with explicit graph-based control flow
- **Add durable execution** so agents survive failures and restarts
- **Implement human-in-the-loop** with interrupts and approval steps
- **Build multi-agent systems** with state shared across agents
- **Stream intermediate results** from long-running agent tasks
- **Time-travel debug** by replaying agent execution from any checkpoint

## When NOT to use

- For a simple tool-calling agent, use [LangChain](https://docs.langchain.com/oss/langchain/overview) agents instead—less boilerplate for common patterns
- For a batteries-included agent with planning and subagents, use [Deep Agents](https://docs.langchain.com/oss/deepagents/overview) instead
- LangGraph is the **orchestration layer**—use it when you need fine-grained control over agent behavior

## Install

```bash
# Python
pip install -U langgraph

# JavaScript/TypeScript
npm install @langchain/langgraph @langchain/core
```

## Quick reference

### Graph API (recommended for most use cases)

```python
from langgraph.graph import StateGraph, MessagesState, START, END

def my_node(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

graph = StateGraph(MessagesState)
graph.add_node(my_node)
graph.add_edge(START, "my_node")
graph.add_edge("my_node", END)
graph = graph.compile()

result = graph.invoke(
    {"messages": [{"role": "user", "content": "Hello!"}]}
)
```

### Functional API (for simple pipelines)

```python
from langgraph.func import entrypoint, task

@task
def step_one(input: str) -> str:
    return f"processed: {input}"

@entrypoint()
def pipeline(input: str) -> str:
    return step_one(input).result()
```

### Add human-in-the-loop

```python
from langgraph.types import interrupt

def human_approval(state: MessagesState):
    answer = interrupt({"question": "Approve this action?"})
    return {"messages": [{"role": "user", "content": answer}]}
```

## Key concepts

| Concept | Description |
|---------|-------------|
| `StateGraph` | Define nodes and edges that form your agent's control flow |
| `MessagesState` | Built-in state schema for chat-based agents |
| `compile()` | Compile a graph builder into an executable graph |
| `interrupt()` | Pause execution and wait for human input |
| Checkpointer | Persist state for durable execution and time-travel |
| Graph API vs Functional API | Graph API for complex workflows; Functional API for linear pipelines |

## Key documentation

- [Overview](https://docs.langchain.com/oss/langgraph/overview)—What LangGraph is and when to use it
- [Quickstart](https://docs.langchain.com/oss/langgraph/quickstart)—Build your first graph
- [Persistence](https://docs.langchain.com/oss/langgraph/persistence)—Add memory and durable execution
- [Interrupts](https://docs.langchain.com/oss/langgraph/interrupts)—Human-in-the-loop patterns
- [Streaming](https://docs.langchain.com/oss/langgraph/streaming)—Stream intermediate results
- [Graph API](https://docs.langchain.com/oss/langgraph/graph-api)—Define nodes, edges, and state
- [Deploy](https://docs.langchain.com/oss/langgraph/deploy)—Deploy to production with LangSmith

## API reference

For SDK class and method details, use the [LangChain API Reference](https://reference.langchain.com) site:
- Browse: `https://reference.langchain.com/python/langgraph`
- MCP server: `https://reference.langchain.com/mcp`

## Related skills

- **langchain**—Core building blocks for models, tools, and simple agents
- **deep-agents**—High-level agent harness built on LangGraph
- **langsmith**—Trace, evaluate, and deploy your LangGraph agents
