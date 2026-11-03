"""Subagents: stream coordinator and delegated subagent progress."""

# :snippet-start: subagent-stream-progress-py
from deepagents import (
    create_deep_agent
)

agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt=(
        "You are a project coordinator with no research knowledge. "
        "For every user request, you must call the task() tool with "
        "subagent_type set to research-agent. Never answer research "
        "questions yourself."
    ),
    subagents=[
        {
            "name": "research-agent",
            "description": (
                "Delegate research to this subagent. Give one topic at a time."
            ),
            "system_prompt": (
                "You are a great researcher. Return a brief summary."
            ),
        },
    ],
    name="main-agent",
)

if __name__ == "__main__":
    stream = agent.stream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Research one recent advance in quantum computing.",
                }
            ]
        },
        version="v3",
    )

    coordinator_messages: list[str] = []
    subagent_handles = []

    for name, item in stream.interleave("messages", "subagents"):
        if name == "messages":
            print("[coordinator]", item.text)
            coordinator_messages.append(item.text)
        else:
            print(f"[{item.name}] started")
            subagent_handles.append(item)
            for message in item.messages:
                print(f"[{item.name}]", message.text)
            print(f"[{item.name}] status: {item.status}")
# :snippet-end:

# :remove-start:
    assert len(coordinator_messages) > 0, "expected coordinator messages"
    assert len(subagent_handles) > 0, (
        "expected at least one subagent handle; "
        "ensure the coordinator delegates via task()"
    )
    assert subagent_handles[0].name == "research-agent"
    print("✓ subagent stream progress sample completed")
# :remove-end:
