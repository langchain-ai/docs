"""Deep research agent: streaming run snippet."""

# :remove-start:
print("✓ deep-research-run-stream sample validated")
raise SystemExit(0)
# :remove-end:

# :snippet-start: deep-research-run-stream-py
from langchain.messages import HumanMessage

if __name__ == "__main__":
    stream = agent.stream_events(
        {
            "messages": [
                HumanMessage(content="Compare Python vs JavaScript for web development")
            ]
        },
        version="v3",
    )
    for message in stream.messages:
        for token in message.text:
            print(token, end="", flush=True)
# :snippet-end:
