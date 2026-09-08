# :snippet-start: mcp-multimodal-tool-content-py
from langchain.mcp import MCPAdapter


async def access_multimodal_tool_content(server) -> None:
    async with MCPAdapter(server) as adapter:
        [screenshot] = await adapter.list_tools()

    # An MCP result arrives as LangChain content blocks. Image and file content
    # convert into standardized `image`/`file` blocks alongside `text`.
    message = await screenshot.ainvoke(
        {"name": "take_screenshot", "args": {}, "id": "1", "type": "tool_call"}
    )
    for block in message.content_blocks:  # [!code highlight]
        if block["type"] == "text":  # [!code highlight]
            print(f"Text: {block['text']}")  # [!code highlight]
        elif block["type"] == "image":  # [!code highlight]
            print(f"Image mime type: {block.get('mime_type')}")  # [!code highlight]
            print(  # [!code highlight]
                f"Image base64: {block.get('base64', '')[:20]}..."  # [!code highlight]
            )  # [!code highlight]


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
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
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
    await access_multimodal_tool_content(screenshot_server())
    print("✓ mcp-multimodal-tool-content validated")


if __name__ == "__main__":
    asyncio.run(_run())
# :remove-end:
