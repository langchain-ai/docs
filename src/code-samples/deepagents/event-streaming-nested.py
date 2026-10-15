"""Event streaming: nested subagent work."""

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

# :snippet-start: event-streaming-nested-py
stream = agent.stream_events(input, version="v3")

subagent_names: list[str] = []
for subagent in stream.subagents:
    print(f"subagent {subagent.name}: {subagent.status}")

    for tool_call in subagent.tool_calls:
        print(f"{tool_call.tool_name}({tool_call.input})")
        for delta in tool_call.output_deltas:
            print(delta, end="", flush=True)

    for nested in subagent.subagents:
        print(f"nested subagent {nested.name}: {nested.status}")

    subagent_names.append(subagent.name)
# :snippet-end:

# :remove-start:
if not subagent_names:
    raise ValueError("expected at least one subagent handle")
print("✓ event-streaming-nested sample validated")
# :remove-end:
