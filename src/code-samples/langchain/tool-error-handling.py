# :snippet-start: tool-error-handling-py
from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest


@wrap_tool_call
def handle_tool_errors(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage],
) -> ToolMessage:
    """Convert tool exceptions into ToolMessages the model can handle."""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({e})",
            tool_call_id=request.tool_call["id"],
        )


agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[],
    middleware=[handle_tool_errors],
)

# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    from langchain.messages import AIMessage
    from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

    request = ToolCallRequest(
        tool_call={"id": "1", "name": "divide", "args": {"a": 1, "b": 0}},
        tool=object(),  # not used by this middleware
        state={},
        runtime={},
    )

    def failing_handler(_: ToolCallRequest) -> ToolMessage:
        raise ZeroDivisionError("division by zero")

    msg = handle_tool_errors.wrap_tool_call(request, failing_handler)
    assert isinstance(msg, ToolMessage)
    assert msg.tool_call_id == "1"
    assert "division by zero" in msg.content
    print("✓ tool errors convert to ToolMessage")

    # Sanity check: middleware is accepted by agent wiring.
    model = GenericFakeChatModel(messages=iter([AIMessage(content="ok")]))
    create_agent(model=model, tools=[], middleware=[handle_tool_errors])
    print("✓ agent wires tool middleware")

# :remove-end:
