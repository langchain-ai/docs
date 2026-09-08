# :snippet-start: langgraph-functional-api-interrupt-stream-py
import time

from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.types import Command, interrupt


@task
def write_essay(topic: str) -> str:
    """Write an essay about the given topic."""
    time.sleep(1)  # This is a placeholder for a long-running task.
    return f"An essay about topic: {topic}"


@entrypoint(checkpointer=InMemorySaver())
def workflow(topic: str) -> dict:
    """A simple workflow that writes an essay and asks for a review."""
    essay = write_essay("cat").result()
    is_approved = interrupt(
        {
            # Any json-serializable payload provided to interrupt as argument.
            # It will be surfaced on the client side as an Interrupt when streaming data
            # from the workflow.
            "essay": essay,  # The essay we want reviewed.
            # We can add any additional information that we need.
            # For example, introduce a key called "action" with some instructions.
            "action": "Please approve/reject the essay",
        }
    )
    return {
        "essay": essay,  # The essay that was generated
        "is_approved": is_approved,  # Response from HIL
    }


thread_id = str(uuid7())
config = {"configurable": {"thread_id": thread_id}}
stream = workflow.stream_events("cat", config, version="v3")
_ = stream.output
print({"write_essay": stream.interrupts[0].value["essay"]})
print({"__interrupt__": stream.interrupts})
# {'write_essay': 'An essay about topic: cat'}
# {
#   '__interrupt__': [
#     Interrupt(
#       value={
#           'essay': 'An essay about topic: cat',
#           'action': 'Please approve/reject the essay'
#       },
#       id='369d44b3d93d4a631ae583367ac6b5cc'
#     )
#   ]
# }
# :snippet-end:

# :snippet-start: langgraph-functional-api-interrupt-resume-py
# Get review from a user (e.g., via a UI)
# In this case, we're using a bool, but this can be any json-serializable value.
human_review = True

resumed_stream = workflow.stream_events(Command(resume=human_review), config, version="v3")
print(resumed_stream.output)
# {'essay': 'An essay about topic: cat', 'is_approved': True}
# :snippet-end:


# :remove-start:
test_thread_id = str(uuid7())
test_config = {"configurable": {"thread_id": test_thread_id}}
test_stream = workflow.stream_events("cat", test_config, version="v3")
_ = test_stream.output

assert test_stream.interrupted
interrupt_payload = test_stream.interrupts[0].value
assert interrupt_payload["essay"] == "An essay about topic: cat"
assert interrupt_payload["action"] == "Please approve/reject the essay"
resumed_test_stream = workflow.stream_events(
    Command(resume=True), test_config, version="v3"
)
assert resumed_test_stream.output["is_approved"] is True
print("✓ langgraph-functional-api-interrupt-stream")
# :remove-end:
