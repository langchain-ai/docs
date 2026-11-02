"""Async subagents: answer a subagent that is waiting for input."""

# :snippet-start: async-subagents-answer-waiting-py
from langgraph_sdk import get_client


async def answer_waiting_subagent(task_id: str, graph_id: str, answer: object) -> None:
    client = get_client()  # Pass url=... for a subagent on another deployment
    thread = await client.threads.get(task_id)  # The task ID is the subagent's thread ID
    interrupt = next(iter(thread["interrupts"].values()))[0]
    await client.runs.create(
        task_id,
        graph_id,
        command={"resume": {interrupt["id"]: answer}},
    )
# :snippet-end:

# :remove-start:
import inspect

assert inspect.iscoroutinefunction(answer_waiting_subagent)
print("✓ async-subagents-answer-waiting sample validated")
# :remove-end:
