"""Async subagents: recognize task notifications in the supervisor's messages."""

# :remove-start:
from langchain.messages import AIMessage, HumanMessage

event = {"task_id": "thread-123", "agent_name": "researcher", "status": "success", "run_id": "run-456"}
state = {
    "messages": [
        HumanMessage(content="Research topic X"),
        AIMessage(content="Started task thread-123"),
        HumanMessage(content=[{"type": "text", "text": "[SYSTEM NOTIFICATION]"}], additional_kwargs={"deepagents_notification": event}),
    ]
}
seen = []
# :remove-end:

# :snippet-start: async-subagents-notifications-py
for message in state["messages"]:
    if event := message.additional_kwargs.get("deepagents_notification"):
        print(event["agent_name"], event["status"])  # success, error, timeout, cancelled, or waiting
        # :remove-start:
        seen.append(event["status"])
        # :remove-end:
# :snippet-end:

# :remove-start:
assert seen == ["success"]
print("✓ async-subagents-notifications sample validated")
# :remove-end:
