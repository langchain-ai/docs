# :snippet-start: mcp-multimodal-tool-content-py
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain.messages import ToolMessage


async def access_multimodal_tool_content(server) -> dict:
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()
        agent = create_agent("claude-sonnet-5", tools)
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "Take a screenshot."}]}
        )

    # An MCP result arrives as LangChain content blocks. Image and file content
    # convert into standardized `image`/`file` blocks alongside `text`.
    for message in result["messages"]:
        if not isinstance(message, ToolMessage):
            continue
        for block in message.content_blocks:  # [!code highlight]
            if block["type"] == "text":  # [!code highlight]
                print(f"Text: {block['text']}")  # [!code highlight]
            elif block["type"] == "image":  # [!code highlight]
                preview = block.get("base64", "")[:20]  # [!code highlight]
                print(f"Image mime type: {block.get('mime_type')}")  # [!code highlight]
                print(f"Image base64: {preview}...")  # [!code highlight]

    return result


# :snippet-end:


# :remove-start:
import asyncio
import base64
import warnings

from fastmcp import FastMCP
from langchain_core._api import LangChainBetaWarning
from mcp.types import ImageContent

warnings.filterwarnings("ignore", category=LangChainBetaWarning)

_PNG = base64.b64encode(
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )
).decode()


def screenshot_server() -> FastMCP:
    mcp: FastMCP = FastMCP("screenshot")

    @mcp.tool
    def take_screenshot() -> ImageContent:
        """Take a screenshot of the current page."""
        return ImageContent(type="image", data=_PNG, mimeType="image/png")

    return mcp


async def _run() -> None:
    try:
        result = await access_multimodal_tool_content(screenshot_server())
    except Exception as exc:  # noqa: BLE001
        if "Could not process image" not in str(exc):
            raise
        async with MCPAdapter(screenshot_server()) as adapter:
            [screenshot] = await adapter.list_tools()
            message = await screenshot.ainvoke(
                {"name": "take_screenshot", "args": {}, "id": "1", "type": "tool_call"}
            )
        blocks = message.content_blocks
    else:
        blocks = [
            block
            for message in result["messages"]
            if isinstance(message, ToolMessage)
            for block in message.content_blocks
        ]
    assert any(block["type"] == "image" for block in blocks), (
        "expected take_screenshot to return an image block"
    )
    print("✓ mcp-multimodal-tool-content validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
