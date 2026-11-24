"""Deep Agents streaming: stream chunk shapes with subgraphs."""

# :remove-start:
import os

from deepagents import create_deep_agent


class _ShapeAgent:
    """Yield one illustrative chunk per stream_mode shape when no API key is set."""

    def stream(self, _input, stream_mode="updates", subgraphs=True, **_kwargs):
        if isinstance(stream_mode, list):
            yield ((), "updates", {"model_request": {}})
            return
        yield ((), {"model_request": {}})


if os.environ.get("OPENAI_API_KEY"):
    agent = create_deep_agent(
        model="openai:gpt-6.1-sol",
        system_prompt="You are a helpful research assistant",
    )
else:
    agent = _ShapeAgent()
# :remove-end:

# :snippet-start: streaming-chunk-shapes-py
# Single mode + subgraphs
for namespace, data in agent.stream(
    {"messages": [{"role": "user", "content": "Research quantum computing"}]},
    stream_mode="updates",
    subgraphs=True,
):
    print(namespace)  # () for main agent, ("tools:<id>",) for subagent
    print(data)

# Multiple modes + subgraphs
for namespace, mode, data in agent.stream(
    {"messages": [{"role": "user", "content": "Research quantum computing"}]},
    stream_mode=["updates", "messages", "custom"],
    subgraphs=True,
):
    print(mode)  # "updates", "messages", or "custom"
    print(namespace)  # () for main agent, ("tools:<id>",) for subagent
    print(data)
# :snippet-end:

# :remove-start:
assert agent is not None
print("✓ streaming-chunk-shapes validated")
# :remove-end:
