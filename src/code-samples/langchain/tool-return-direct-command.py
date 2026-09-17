# :snippet-start: tool-return-direct-command-py
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command


@tool(return_direct=True)
def fetch_and_store_order(order_id: str, runtime: ToolRuntime) -> Command:
    """Fetch order status and store it in state."""
    status = f"Order {order_id} is shipped and will arrive in 2 days."
    return Command(
        update={
            "last_order_status": status,
            # Must include a ToolMessage so the message history stays valid
            "messages": [
                ToolMessage(
                    content=status,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass
    class MockRuntime:
        tool_call_id: str = "test_call_123"

    mock_runtime = MockRuntime()
    # func exists at runtime, not in BaseTool type stubs
    command = fetch_and_store_order.func("12345", mock_runtime)  # type: ignore[attr-defined]

    assert fetch_and_store_order.return_direct is True
    assert isinstance(command, Command)
    assert command.update is not None
    assert (
        command.update["last_order_status"]
        == "Order 12345 is shipped and will arrive in 2 days."
    )
    assert len(command.update["messages"]) == 1
    assert (
        command.update["messages"][0].content
        == "Order 12345 is shipped and will arrive in 2 days."
    )
    assert command.update["messages"][0].tool_call_id == "test_call_123"

    print("✓ returnDirect Command tool sample completed")
# :remove-end:
