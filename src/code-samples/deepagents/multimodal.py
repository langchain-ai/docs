"""Deep Agents multimodal inputs, tool outputs, and summarization examples."""

# :remove-start:
from unittest.mock import MagicMock

agent = MagicMock()
# :remove-end:

# :snippet-start: multimodal-user-input-py
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "What is in this screenshot?"},
            {"type": "image", "url": "https://example.com/screenshot.png"},
        ],
    }],
})
# :snippet-end:

# :remove-start:
agent.invoke.assert_called_once()
# :remove-end:

# :snippet-start: multimodal-capture-screenshot-py
from langchain.tools import tool


@tool
def capture_screenshot() -> list[dict]:
    """Capture a screenshot of the current page."""
    return [
        {"type": "text", "text": "Screenshot of the current page:"},
        {"type": "image", "url": "https://example.com/page.png"},
    ]
# :snippet-end:

# :remove-start:
blocks = capture_screenshot.invoke({})
assert len(blocks) == 2
assert blocks[0]["type"] == "text"
assert blocks[1]["type"] == "image"
# :remove-end:

# :remove-start:
from langchain.messages import AIMessage, HumanMessage, ToolMessage

IMG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRUdu5ErkJggg=="
)
# :remove-end:

# :snippet-start: multimodal-summarization-py
# Before — model receives image blocks in older turns
[
    HumanMessage(
        content=[
            {"type": "text", "text": "What trends do you see in this chart?"},
            {"type": "image", "base64": IMG, "mime_type": "image/png"},
        ]
    ),
    ToolMessage(
        content=[
            {"type": "text", "text": "Updated chart:"},
            {"type": "image", "base64": IMG, "mime_type": "image/png"},
        ],
        tool_call_id="call_chart_1",
    ),
    AIMessage(content="Revenue rose in Q3 based on the chart trend."),
    HumanMessage(content="Reply with one sentence summarizing our analysis."),
]

# After — those turns collapse to text; image blocks are gone
{"content": (
    "User asked about trends in a chart screenshot. "
    "Tool returned an updated chart. Agent identified Q3 revenue growth."
)}
# :snippet-end:

# :remove-start:
assert IMG
# :remove-end:
