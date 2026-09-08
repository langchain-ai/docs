# :snippet-start: middleware-tool-call-monitoring-decorator-py
from collections.abc import Callable

from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langgraph.types import Command


@wrap_tool_call
def monitor_tool(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    print(f"Executing tool: {request.tool_call['name']}")
    print(f"Arguments: {request.tool_call['args']}")
    try:
        result = handler(request)
        print("Tool completed successfully")
        return result
    except Exception as e:
        print(f"Tool failed: {e}")
        raise


# :snippet-end:

# :snippet-start: middleware-tool-call-monitoring-class-py
from collections.abc import Callable

from langchain.agents.middleware import AgentMiddleware
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langgraph.types import Command


class ToolMonitoringMiddleware(AgentMiddleware):
    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        print(f"Executing tool: {request.tool_call['name']}")
        print(f"Arguments: {request.tool_call['args']}")
        try:
            result = handler(request)
            print("Tool completed successfully")
            return result
        except Exception as e:
            print(f"Tool failed: {e}")
            raise


# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert monitor_tool is not None, "Decorator middleware should be defined"
    print("✓ Tool call monitoring middleware definitions are valid")
# :remove-end:
