# :snippet-start: message-serialization-py
from langchain.messages import HumanMessage
from langchain_core.load import dumpd, load

message = HumanMessage("What is the capital of France?")

# Serialize to a plain dict
serialized = dumpd(message)

# Deserialize back to a message object
restored = load(serialized)
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert isinstance(serialized, dict)
    assert isinstance(restored, HumanMessage)
    assert restored.content == message.content
    print("✓ Message serialization round-trip works")
# :remove-end:
