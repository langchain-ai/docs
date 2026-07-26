"""Data analysis agent tutorial samples."""

# :snippet-start: data-analysis-backend-local-shell-py
from deepagents.backends import LocalShellBackend

backend = LocalShellBackend(
    root_dir=".",
    virtual_mode=True,
    env={"PATH": "/usr/bin:/bin"},
)
# :snippet-end:

# :snippet-start: data-analysis-upload-sample-data-py
import csv
import io

# Create sample sales data
data = [
    ["Date", "Product", "Units Sold", "Revenue"],
    ["2025-08-01", "Widget A", 10, 250],
    ["2025-08-02", "Widget B", 5, 125],
    ["2025-08-03", "Widget A", 7, 175],
    ["2025-08-04", "Widget C", 3, 90],
    ["2025-08-05", "Widget B", 8, 200],
]

# Convert to CSV bytes
text_buf = io.StringIO()
writer = csv.writer(text_buf)
writer.writerows(data)
csv_bytes = text_buf.getvalue().encode("utf-8")
text_buf.close()

# Upload to backend
backend.upload_files([("/root/data/sales_data.csv", csv_bytes)])
# :snippet-end:

# :remove-start:
import os

os.environ.setdefault("SLACK_USER_TOKEN", "xoxb-test-token")
# :remove-end:

# :snippet-start: data-analysis-slack-tool-py
import os

from langchain.tools import tool
from slack_sdk import WebClient

slack_token = os.environ["SLACK_USER_TOKEN"]
slack_client = WebClient(token=slack_token)
channel = "C0123456ABC"  # specify your own channel here


@tool(parse_docstring=True)
def slack_send_message(text: str, file_path: str | None = None) -> str:
    """Send message, optionally including attachments such as images.

    Args:
        text: (str) text content of the message
        file_path: (str) file path of attachment in the filesystem.
    """
    if not file_path:
        slack_client.chat_postMessage(channel=channel, text=text)
    else:
        fp = backend.download_files([file_path])
        slack_client.files_upload_v2(
            channel=channel,
            content=fp[0].content,
            initial_comment=text,
        )

    return "Message sent."
# :snippet-end:

# :snippet-start: data-analysis-create-agent-py
from langchain_core.utils.uuid import uuid7

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[slack_send_message],
    backend=backend,
    checkpointer=checkpointer,
)

thread_id = str(uuid7())
config = {"configurable": {"thread_id": thread_id}}
# :snippet-end:

# :remove-start:
from unittest.mock import MagicMock

slack_client.chat_postMessage = MagicMock(return_value={"ok": True})
slack_client.files_upload_v2 = MagicMock(return_value={"ok": True})

assert slack_send_message.invoke({"text": "Analysis complete"}) == "Message sent."
slack_client.chat_postMessage.assert_called_once()

slack_client.chat_postMessage.reset_mock()
slack_client.files_upload_v2.reset_mock()

assert (
    slack_send_message.invoke(
        {"text": "See plot", "file_path": "/root/data/sales_data.csv"},
    )
    == "Message sent."
)
slack_client.files_upload_v2.assert_called_once()

assert agent is not None
assert backend.read("/root/data/sales_data.csv").error is None
print("✓ data-analysis sample validated")
# :remove-end:
