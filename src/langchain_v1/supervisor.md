---
title: Multi-agent
icon: "people-group"
---

**Multi-agent systems** break a complex application into multiple specialized agents that work together to solve problems.  
Instead of relying on a single agent to handle every step, **multi-agent architectures** allow you to compose smaller, focused agents into a coordinated workflow.

Multi-agent systems are useful when:

* A single agent has too many tools and makes poor decisions about which to use.
* Context or memory grows too large for one agent to track effectively.
* Tasks require **specialization** (e.g., a planner, researcher, math expert).

Benefits include:

| Benefit            | Description                                                       |
|--------------------|-------------------------------------------------------------------|
| **Modularity**     | Easier to develop, test, and maintain smaller, focused agents.    |
| **Specialization** | Each agent can be optimized for a particular domain or task type. |
| **Control**        | Explicitly define communication and control flow between agents.  |

## Two common patterns

| Pattern          | How it Works                                                                                                                                                     | Control Flow                                                | Example Use Case                                 |
|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|--------------------------------------------------|
| **Tool Calling** | A central agent calls other agents as *tools*. The “tool” agents don’t talk to the user directly — they just run their task and return results.                  | Centralized — all routing passes through the calling agent. | Task orchestration, structured workflows.        |
| **Handoffs**     | The current agent decides to **transfer control** to another agent. The active agent changes, and the user may continue interacting directly with the new agent. | Decentralized — agents can change who is active.            | Multi-domain conversations, specialist takeover. |

### Tool calling

In **tool calling**, one agent (the “**controller**”) treats other agents as *tools* to be invoked when needed.  

Flow:

1. The **controller** receives input and decides which tool (subagent) to call.
2. The **tool agent** runs its task based on the controller’s instructions.
3. The **tool agent** returns results to the controller.
4. The **controller** decides the next step or finishes.

✅ Predictable, centralized routing.  
⚠️ Tool agents won’t initiate new questions to the user — their role is fully defined by the controller.

```mermaid
graph LR
    A[User] --> B[Controller Agent]
    B --> C[Tool Agent 1]
    B --> D[Tool Agent 2]
    C --> B
    D --> B
    B --> E[User Response]
````

### Handoffs

In **handoffs**, agents can directly pass control to each other. The “active” agent changes, and the user interacts with whichever agent currently has control.

Flow:

1. The **current agent** decides it needs help from another agent.
2. It passes control (and state) to the **next agent**.
3. The **new agent** interacts directly with the user until it decides to hand off again or finish.

✅ Flexible, more natural conversational flow between specialists.
⚠️ Less centralized — harder to guarantee predictable behavior.

```mermaid
graph LR
    A[User] --> B[Agent A]
    B --> C[Agent B]
    C --> A
```

## Choosing between tool calling and handoffs

| Question                                              | Tool Calling | Handoffs |
|-------------------------------------------------------|--------------|----------|
| Need centralized control over workflow?               | ✅ Yes        | ❌ No     |
| Want agents to interact directly with the user?       | ❌ No         | ✅ Yes    |
| Complex, human-like conversation between specialists? | ❌ Limited    | ✅ Strong |

<Tip>
You can also combine these patterns — e.g., use a top-level **tool-calling controller** for high-level routing, but allow **handoffs** within a team of related agents for smoother conversation.
</Tip>

**Example**: [Multi-agent Tool Calling](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor) · [Handoffs](https://langchain-ai.github.io/langgraph/how-tos/multi_agent/#handoffs)

## How handoffs work

Under the hood, **handoffs** are implemented as tools.  
When an agent decides to hand off, it invokes a special *handoff tool* that:

1. Updates the **graph state** with any necessary information.
2. Changes the **active agent** so that subsequent steps are handled by the new agent.

This means that supporting handoffs in your system requires tracking the **currently active agent** in the shared graph state, so the runtime always knows which agent is “in control.”


## Context engineering

Whether you’re implementing handoffs or tool calling, the quality of your system depends heavily on **how you pass context** to agents and subagents.

LangGraph gives you fine-grained control over this process, allowing you to:

* Decide **which parts of the conversation history** or state are passed to each agent.
* Provide **specialized prompts** for different subagents.
* Include or exclude **intermediate reasoning steps** from the shared state.
* Tailor inputs so that each agent gets exactly the information it needs to work effectively.

This **context engineering** capability lets you fine-tune every aspect of agent behavior, ensuring that each agent receives the right data, at the right time, in the right format — whether it’s acting as a tool or taking over as the active agent via a handoff.

## Supervisor (using tools)


<Tabs>
  <Tab title="Supervisor (from scratch)">

```python Expandable Supervisor from scratch
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

chat_model = init_chat_model("anthropic:claude-opus-4-20250514")

def book_hotel(hotel_name: str):
    """Book a hotel"""
    return f"Successfully booked a stay at {hotel_name}."

def book_flight(from_airport: str, to_airport: str):
    """Book a flight"""
    return f"Successfully booked a flight from {from_airport} to {to_airport}."

flight_assistant = create_react_agent(
    model="anthropic:claude-opus-4-20250514",
    tools=[book_flight],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
)

hotel_assistant = create_react_agent(
    model="anthropic:claude-opus-4-20250514",
    tools=[book_hotel],
    prompt="You are a hotel booking assistant",
    name="hotel_assistant"
)


@tool
def booking_agent(instructions: str):
    """Give instructions to the booking agent about what flight to book."""
    results = flight_assistant.invoke({
        "messages": [{
        "role": "user",
        "content": instructions
        }]
    })
    return results['messages'][-1].content

@tool
def hotel_agent(instructions: str):
    """Give instructions to the hotel assistant about what hotel to book."""
    result = hotel_assistant.invoke({
        "messages": [{
        "role": "user",
        "content": instructions
        }]
    })
    return result['messages'][-1].content

supervisor = create_react_agent(
    model=chat_model,
    prompt=(
         "You manage a hotel booking assistant and a"
         "flight booking assistant. Assign work to them based on the user requests."
     ),
    tools=[hotel_agent, booking_agent],
)

response = supervisor.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
            }
        ]
    }
)

```


</Tab>
<Tab title="Supervisor prebuilt">

```python Expandable Supervisor prebuilt
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model

chat_model = init_chat_model("google_vertexai: gemini-2.5-flash")

def book_hotel(hotel_name: str):
    """Book a hotel"""
    return f"Successfully booked a stay at {hotel_name}."

def book_flight(from_airport: str, to_airport: str):
    """Book a flight"""
    return f"Successfully booked a flight from {from_airport} to {to_airport}."

flight_assistant = create_react_agent(
    model="anthropic:claude-opus-4-20250514",
    tools=[book_flight],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
)

hotel_assistant = create_react_agent(
    model="anthropic:claude-opus-4-20250514",
    tools=[book_hotel],
    prompt="You are a hotel booking assistant",
    name="hotel_assistant"
)


hotel_assistant = create_react_agent(
    model="anthropic:claude-opus-4-20250514",
    tools=[book_hotel],
    prompt="You are a hotel booking assistant",
    name="hotel_assistant"
)

supervisor = create_supervisor(
    model=chat_model,
    prompt=(
        "You manage a hotel booking assistant and a"
        "flight booking assistant. Assign work to them."
    ),
   agents=[flight_assistant, hotel_assistant],
).compile()

response = supervisor.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
            }
        ]
    }
)
```

</Tab>
</Tabs>

### Context engineering with tools

LangGraph tools are flexible and give you the ability to both read and write context appropriately.

### Include the final result

```python
@tool
def booking_agent(instructions: str):
    """Give instructions to the booking agent about what flight to book."""
    results = flight_assistant.invoke({
        "messages": [{
        "role": "user",
        "content": instructions
        }]
    })
    return results['messages'][-1].content
```

### Include internal message history in ToolMessage

```python
@tool
def booking_agent(instructions: str) -> str:
    """Use an agent to book a flight."""
    result = flight_assistant.invoke({
        "messages": [{
            "role": "user",
            "content": instructions
        }]
    })
    if len(result['messages']) == 0:
        raise AssertionError("No messages in the result from flight assistant.")

    content = "<history>"
    for msg in result['messages'][:-1]:
        content += f"<message role='{msg['role']}'>{msg['content']}</message>"
    content += "</history>"
    content += f"<result>{result['messages'][-1]['content']}</result>"
    return content
```

### Attach internal message history to the overall graph state

```python
@tool
def booking_agent(instructions: str) -> str:
    """Use an agent to book a flight."""
    result = flight_assistant.invoke({
        "messages": [{
            "role": "user",
            "content": instructions
        }]
    })
    if len(result['messages']) == 0:
        raise AssertionError("No messages in the result from flight assistant.")

    content = "<history>"
    for msg in result['messages'][:-1]:
        content += f"<message role='{msg['role']}'>{msg['content']}</message>"
    content += "</history>"
    content += f"<result>{result['messages'][-1]['content']}</result>"
    return content
```
