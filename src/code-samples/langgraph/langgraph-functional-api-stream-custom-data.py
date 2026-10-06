# :snippet-start: langgraph-functional-api-stream-custom-data-py
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


config = {"configurable": {"thread_id": str(uuid7())}}

for chunk in main.stream({"x": 5}, config, stream_mode="custom"):
    print(chunk)
# Started processing
# Result is 10
# :snippet-end:

# :snippet-start: langgraph-functional-api-stream-values-py
values_config = {"configurable": {"thread_id": str(uuid7())}}
stream = main.stream_events({"x": 5}, config=values_config, version="v3")
for snapshot in stream.values:
    print(snapshot)
# 10
# :snippet-end:

# :remove-start:
test_config = {"configurable": {"thread_id": str(uuid7())}}
chunks = list(main.stream({"x": 5}, test_config, stream_mode="custom"))

assert chunks == ["Started processing", "Result is 10"], chunks

values_test_config = {"configurable": {"thread_id": str(uuid7())}}
values_stream = main.stream_events(
    {"x": 5}, config=values_test_config, version="v3"
)
values_chunks = list(values_stream.values)
assert values_chunks == [10], values_chunks
print("✓ langgraph-functional-api-stream-custom-data")
# :remove-end:
