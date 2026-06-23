from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.func import entrypoint

checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def main(inputs: dict) -> int:
    writer = get_stream_writer()
    writer("Started processing")
    result = inputs["x"] * 2
    writer(f"Result is {result}")
    return result


# :snippet-start: langgraph-functional-api-stream-custom-data-py
config = {"configurable": {"thread_id": str(uuid7())}}

stream = main.stream_events({"x": 5}, config=config, version="v3")
for mode, chunk in stream.interleave("values"):
    print(f"{mode}: {chunk}")
# values: 10
# :snippet-end:


# :remove-start:
test_config = {"configurable": {"thread_id": str(uuid7())}}
test_stream = main.stream_events({"x": 5}, config=test_config, version="v3")
chunks = list(test_stream.interleave("values"))

assert chunks == [
    ("values", 10),
]
print("✓ langgraph-functional-api-stream-custom-data")
# :remove-end:
