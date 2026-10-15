"""Event streaming: track subagent lifecycle."""

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

# :snippet-start: event-streaming-lifecycle-py
stream = agent.stream_events(input, version="v3")

running = 0
completed = 0
failed = 0

for subagent in stream.subagents:
    running += 1
    print(f"{subagent.name}: started")

    try:
        _ = subagent.output
        running -= 1
        completed += 1
        print(f"{subagent.name}: completed")
    except Exception:
        running -= 1
        failed += 1
        print(f"{subagent.name}: failed")
# :snippet-end:

# :remove-start:
if completed < 1:
    raise ValueError("expected at least one completed subagent")
print("✓ event-streaming-lifecycle sample validated")
# :remove-end:
