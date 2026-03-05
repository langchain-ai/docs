# :snippet-start: tool-return-command
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command


@tool
def set_language(language: str, runtime: ToolRuntime) -> Command:
    """Set the preferred response language."""
    return Command(
        update={
            "preferred_language": language,
            "messages": [
                ToolMessage(
                    content=f"Language set to {language}.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    # Test by directly calling the function with a mock runtime
    from dataclasses import dataclass

    @dataclass
    class MockRuntime:
        tool_call_id: str = "test_call_123"

    mock_runtime = MockRuntime()
    # func exists at runtime, not in BaseTool type stubs
    result = set_language.func("Spanish", mock_runtime)  # type: ignore[attr-defined]

    assert isinstance(result, Command)
    assert result.update is not None
    assert result.update["preferred_language"] == "Spanish"
    assert len(result.update["messages"]) == 1
    assert result.update["messages"][0].content == "Language set to Spanish."
    assert result.update["messages"][0].tool_call_id == "test_call_123"

    print("✓ Tool works as expected")
# :remove-end:
