# :snippet-start: mcp-multimodal-tool-content-py
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

async def access_multimodal_tool_content():
    client = MultiServerMCPClient({})
    tools = await client.get_tools()
    agent = create_agent("claude-sonnet-4-6", tools)

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Take a screenshot of the current page"}]}
    )

    # Access multimodal content from tool messages
    for message in result["messages"]:
        if message.type == "tool":
            # Raw content in provider-native format
            print(f"Raw content: {message.content}")

            # Standardized content blocks  # [!code highlight]
            for block in message.content_blocks:  # [!code highlight]
                if block["type"] == "text":  # [!code highlight]
                    print(f"Text: {block['text']}")  # [!code highlight]
                elif block["type"] == "image":  # [!code highlight]
                    print(f"Image URL: {block.get('url')}")  # [!code highlight]
                    print(f"Image base64: {block.get('base64', '')[:50]}...")  # [!code highlight]


# :snippet-end:

# :remove-start:
def _test_multimodal_tool_content_blocks() -> None:
    from langchain.messages import ToolMessage

    message = ToolMessage(
        content=[
            {"type": "text", "text": "Screenshot of the current page:"},
            {"type": "image", "url": "https://example.com/page.png"},
        ],
        tool_call_id="call-1",
    )

    text_blocks = [b for b in message.content_blocks if b["type"] == "text"]
    image_blocks = [b for b in message.content_blocks if b["type"] == "image"]

    assert len(text_blocks) == 1
    assert text_blocks[0]["text"] == "Screenshot of the current page:"
    assert len(image_blocks) == 1
    assert image_blocks[0]["url"] == "https://example.com/page.png"


if __name__ == "__main__":
    _test_multimodal_tool_content_blocks()
    print("✓ multimodal ToolMessage content_blocks work")
# :remove-end:
