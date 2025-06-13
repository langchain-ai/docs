---
title: Context
---

Agents often require more than a list of messages to function effectively. They need **context**.

Context includes *any* data outside the message list that can shape agent behavior or tool execution. This can be:

* Information passed at runtime, like a `user_id` or API credentials.
* Internal state updated during a multi-step reasoning process.
* Persistent memory or facts from previous interactions.

LangGraph provides **three** primary ways to supply context:

| Type                                                                         | Description                                   | Mutable? | Lifetime                |
|------------------------------------------------------------------------------|-----------------------------------------------|----------|-------------------------|
| [**Config**](#config-static-context)                                         | data passed at the start of a run             | ❌        | per run                 |
| [**State**](#state-mutable-context)                                          | dynamic data that can change during execution | ✅        | per run or conversation |
| [**Long-term Memory (Store)**](#long-term-memory-cross-conversation-context) | data that can be shared between conversations | ✅        | across conversations    |

You can use context to:

* Adjust the system prompt the model sees
* Feed tools with necessary inputs
* Track facts during an ongoing conversation

## Providing Runtime Context

Use this when you need to inject data into an agent at runtime.

<a id="static-context"></a>
### Config

Config is for immutable data like user metadata or API keys. Use
when you have values that don't change mid-run.

Specify configuration using a key called **"configurable"** which is reserved
for this purpose:

```python
agent.invoke(
    {"messages": [{"role": "user", "content": "hi!"}]},
    # highlight-next-line
    config={"configurable": {"user_id": "user_123"}}
)
```

<a id="mutable-context"></a>
### State

State acts as short-term memory during a run. It holds dynamic data that can evolve during execution, such as values derived from tools or LLM outputs.

```python
class CustomState(AgentState):
    # highlight-next-line
    user_name: str

agent = create_react_agent(
    # Other agent parameters...
    # highlight-next-line
    state_schema=CustomState,
)

agent.invoke({
    "messages": "hi!",
    "user_name": "Jane"
})
```

<Tip>
  **Turning on memory**
  Please see the [memory guide](./memory) for more details on how to enable memory. This is a powerful feature that allows you to persist the agent's state across multiple invocations.
  Otherwise, the state is scoped only to a single agent run.
</Tip>

<a id="cross-conversation-context"></a>
### Long-Term Memory

For context that spans *across* conversations or sessions, LangGraph allows access to **long-term memory** via a `store`. This can be used to read or update persistent facts (e.g., user profiles, preferences, prior interactions). For more, see the [Memory guide](./memory).

<a id="prompts"></a>
## Customizing Prompts with Context

Prompts define how the agent behaves. To incorporate runtime context, you can dynamically generate prompts based on the agent's state or config.

Common use cases:

* Personalization
* Role or goal customization
* Conditional behavior (e.g., user is admin)

<Tabs>
  <Tab title="Using config">
    ```python
    from langchain_core.messages import AnyMessage
    from langchain_core.runnables import RunnableConfig
    from langgraph.prebuilt import create_react_agent
    from langgraph.prebuilt.chat_agent_executor import AgentState
    
    def prompt(
        state: AgentState,
        # highlight-next-line
        config: RunnableConfig,
    ) -> list[AnyMessage]:
        # highlight-next-line
        user_name = config["configurable"].get("user_name")
        system_msg = f"You are a helpful assistant. User's name is {user_name}"
        return [{"role": "system", "content": system_msg}] + state["messages"]
    
    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_weather],
        # highlight-next-line
        prompt=prompt
    )
    
    agent.invoke(
        ...,
        # highlight-next-line
        config={"configurable": {"user_name": "John Smith"}}
    )
    ```
  </Tab>
  <Tab title="Using state">
    ```python
    from langchain_core.messages import AnyMessage
    from langchain_core.runnables import RunnableConfig
    from langgraph.prebuilt import create_react_agent
    from langgraph.prebuilt.chat_agent_executor import AgentState
    
    class CustomState(AgentState):
        # highlight-next-line
        user_name: str
    
    def prompt(
        # highlight-next-line
        state: CustomState
    ) -> list[AnyMessage]:
        # highlight-next-line
        user_name = state["user_name"]
        system_msg = f"You are a helpful assistant. User's name is {user_name}"
        return [{"role": "system", "content": system_msg}] + state["messages"]
    
    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[...],
        # highlight-next-line
        state_schema=CustomState,
        # highlight-next-line
        prompt=prompt
    )
    
    agent.invoke({
        "messages": "hi!",
        # highlight-next-line
        "user_name": "John Smith"
    })
    ```
  </Tab>
</Tabs>

<a id="tools"></a>
## Accessing Context in Tools

Tools can access context through special parameter **annotations**.

* Use `RunnableConfig` for config access
* Use `Annotated[StateSchema, InjectedState]` for agent state

<Tip>
  These annotations prevent LLMs from attempting to fill in the values. These parameters will be **hidden** from the LLM.
</Tip>

<Tabs>
  <Tab title="Using config">
    ```python
    def get_user_info(
        # highlight-next-line
        config: RunnableConfig,
    ) -> str:
        """Look up user info."""
        # highlight-next-line
        user_id = config["configurable"].get("user_id")
        return "User is John Smith" if user_id == "user_123" else "Unknown user"
    
    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_user_info],
    )
    
    agent.invoke(
        {"messages": [{"role": "user", "content": "look up user information"}]},
        # highlight-next-line
        config={"configurable": {"user_id": "user_123"}}
    )
    ```
  </Tab>
  <Tab title="Using State">
    ```python
    from typing import Annotated
    from langgraph.prebuilt import InjectedState
    
    class CustomState(AgentState):
        # highlight-next-line
        user_id: str
    
    def get_user_info(
        # highlight-next-line
        state: Annotated[CustomState, InjectedState]
    ) -> str:
        """Look up user info."""
        # highlight-next-line
        user_id = state["user_id"]
        return "User is John Smith" if user_id == "user_123" else "Unknown user"
    
    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_user_info],
        # highlight-next-line
        state_schema=CustomState,
    )
    
    agent.invoke({
        "messages": "look up user information",
        # highlight-next-line
        "user_id": "user_123"
    })
    ```
  </Tab>
</Tabs>

### Update Context from Tools

Tools can update agent's context (state and long-term memory) during execution. This is useful for persisting intermediate results or making information accessible to subsequent tools or prompts. See [Memory](./memory#read-short-term) guide for more information.
