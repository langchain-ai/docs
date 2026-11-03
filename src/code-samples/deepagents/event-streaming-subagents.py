"""Event streaming: stream subagents projection."""

# :remove-start:
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt=(
        "You are a project coordinator with no creative writing knowledge. "
        "For every user request, you must call the task() tool with "
        "subagent_type set to writer-agent. Never answer creative requests yourself."
    ),
    subagents=[
        {
            "name": "writer-agent",
            "description": "Delegate creative writing to this subagent.",
            "system_prompt": "You are a concise creative writer.",
        },
    ],
)
# :remove-end:

# :snippet-start: event-streaming-subagents-py
stream = agent.stream_events(
    {
        "messages": [{"role": "user", "content": "Write me a haiku about the sea"}],
    },
    version="v3",
)

subagent_names: list[str] = []
for subagent in stream.subagents:
    print(subagent.name, subagent.path, subagent.status)

    for message in subagent.messages:
        print(message.text)

    subagent_names.append(subagent.name)
# :snippet-end:

# :remove-start:
if not subagent_names:
    raise ValueError("expected at least one subagent handle")
if subagent_names[0] != "writer-agent":
    raise ValueError(f"expected writer-agent, got {subagent_names[0]}")
print("✓ event-streaming-subagents sample validated")
# :remove-end:
