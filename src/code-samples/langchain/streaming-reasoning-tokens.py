# :snippet-start: streaming-reasoning-tokens-py
from langchain.agents import create_agent
from langchain.messages import AIMessageChunk
from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import Runnable


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


model = ChatAnthropic(
    model_name="claude-sonnet-4-6",
    timeout=None,
    stop=None,
    thinking={"type": "enabled", "budget_tokens": 5000},
)
agent: Runnable = create_agent(
    model=model,
    tools=[get_weather],
)
for token, metadata in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode="messages",
):
    if not isinstance(token, AIMessageChunk):
        continue
    reasoning = [
        b for b in token.content_blocks if b["type"] == "reasoning"
    ]  # [!code highlight]
    text = [b for b in token.content_blocks if b["type"] == "text"]  # [!code highlight]
    if reasoning:
        print(f"[thinking] {reasoning[0]['reasoning']}", end="")
    if text:
        print(text[0]["text"], end="")
# :snippet-end:

# :remove-start:
# This test is disabled because it requires an API key and would make actual API calls
# To run manually:
#   export ANTHROPIC_API_KEY=your_key
#   python src/code-samples/langchain/streaming-reasoning-tokens.py
if __name__ == "__main__":
    print("\n✓ Code sample is syntactically valid")
# :remove-end:
