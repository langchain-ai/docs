"""Event streaming: coordinator and subagent tool calls."""

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

# :snippet-start: event-streaming-tool-calls-py
stream = agent.stream_events(input, version="v3")

coordinator_tool_names: list[str] = []
for call in stream.tool_calls:
    print("[coordinator tool]", call.tool_name, call.input)
    print(call.completed, call.error)
    coordinator_tool_names.append(call.tool_name)

for subagent in stream.subagents:
    for call in subagent.tool_calls:
        print(f"[{subagent.name} tool]", call.tool_name, call.input)
        for delta in call.output_deltas:
            print(delta, end="", flush=True)

        if call.completed and call.error is None:
            print(call.output)
        elif call.error is not None:
            print(call.error)
# :snippet-end:

# :remove-start:
if not coordinator_tool_names:
    raise ValueError("expected at least one coordinator tool call")
if coordinator_tool_names[0] != "task":
    raise ValueError(f"expected task tool call, got {coordinator_tool_names[0]}")
print("✓ event-streaming-tool-calls sample validated")
# :remove-end:
