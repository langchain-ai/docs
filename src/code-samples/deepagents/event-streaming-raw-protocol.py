"""Event streaming: raw protocol events with namespace routing."""

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

# :snippet-start: event-streaming-raw-protocol-py
stream = agent.stream_events(input, version="v3")

text_deltas: list[str] = []
for event in stream:
    if event.get("method") != "messages":
        continue

    payload = event["params"]["data"][0]
    if not isinstance(payload, dict):
        continue
    if payload.get("event") != "content-block-delta":
        continue

    block = payload.get("delta") or {}
    if block.get("type") == "text-delta":
        source = "subagent" if event["params"]["namespace"] else "coordinator"
        print(f"[{source}] {block['text']}")
        text_deltas.append(block["text"])
# :snippet-end:

# :remove-start:
if not text_deltas:
    raise ValueError("expected at least one text delta event")
print("✓ event-streaming-raw-protocol sample validated")
# :remove-end:
