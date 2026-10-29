# :snippet-start: langgraph-functional-api-stream-writer-inject-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint
from langgraph.types import StreamWriter

checkpointer = InMemorySaver()

@entrypoint(checkpointer=checkpointer)
async def main(inputs: dict, writer: StreamWriter) -> int:  # [!code highlight]
    writer("Started processing")
    return inputs["x"] * 2
# :snippet-end:

# :remove-start:
import asyncio

assert asyncio.run(main.ainvoke({"x": 5}, {"configurable": {"thread_id": "1"}})) == 10
print("✓ langgraph-functional-api-stream-writer-inject")
# :remove-end:
