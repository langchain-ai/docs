"""Event streaming: coordinator and subagent messages."""

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
input = {
    "messages": [{"role": "user", "content": "Write me a haiku about the sea"}],
}
# :remove-end:

# :snippet-start: event-streaming-messages-py
stream = agent.stream_events(input, version="v3")

coordinator_messages: list[str] = []
for message in stream.messages:
    print("[coordinator]", message.text)
    coordinator_messages.append(message.text)

for subagent in stream.subagents:
    for message in subagent.messages:
        print(f"[{subagent.name}]", message.text)
# :snippet-end:

# :remove-start:
if not coordinator_messages:
    raise ValueError("expected coordinator messages")
print("✓ event-streaming-messages sample validated")
# :remove-end:
