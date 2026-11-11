"""Async subagents: recognize task notifications in the supervisor's messages."""

# :remove-start:
from langchain.messages import AIMessage, HumanMessage
from langchain_core.messages import add_notification_metadata

event = {"task_id": "thread-123", "agent_name": "researcher", "status": "success", "run_id": "run-456"}
state = {
    "messages": [
        HumanMessage(content="Research topic X"),
        AIMessage(content="I have started the research."),
        add_notification_metadata(
            HumanMessage(content=[{"type": "text", "text": "<task-notification>"}]),
            source="async_subagent",
            data=event,
        ),
    ]
}
seen = []
# :remove-end:

# :snippet-start: async-subagents-notifications-py
from langchain_core.messages import get_notification_metadata

for message in state["messages"]:
    metadata = get_notification_metadata(message)
    if metadata and metadata["source"] == "async_subagent":
        event = metadata["data"]
        print(event["agent_name"], event["status"])  # success, error, timeout, cancelled, or waiting
        # :remove-start:
        seen.append(event["status"])
        # :remove-end:
# :snippet-end:

# :remove-start:
assert seen == ["success"]
print("✓ async-subagents-notifications sample validated")
# :remove-end:
