# :snippet-start: notification-metadata-add-py
from langchain.messages import HumanMessage
from langchain_core.messages import add_notification_metadata

notification = add_notification_metadata(
    HumanMessage("Background task t_42 finished."),
    source="background_job",
    data={"task_id": "t_42", "status": "success"},
)
# :snippet-end:

# :remove-start:
from langchain.messages import AIMessage

messages = [HumanMessage("Summarize the report."), AIMessage("Working on it."), notification]
labels = []
# :remove-end:

# :snippet-start: notification-metadata-read-py
from langchain_core.messages import get_notification_metadata

for message in messages:
    metadata = get_notification_metadata(message)
    if metadata is None:
        print(message.text)  # A regular message
    else:
        print(f"[{metadata['source']}]", metadata.get("data"))
        # :remove-start:
        labels.append(metadata["source"])
        # :remove-end:
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert notification.content == "Background task t_42 finished."
    assert notification.additional_kwargs["lc_source"] == "background_job"
    assert labels == ["background_job"]
    assert get_notification_metadata(messages[0]) is None
    print("✓ notification-metadata sample validated")
# :remove-end:
