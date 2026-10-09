# :snippet-start: trace-agent-decorator-py
import langsmith as ls
from langsmith import traceable


@traceable(address=ls.AgentAddress("checkout", "production"))
def handle_order(order_id: str) -> dict:
    return {"order_id": order_id, "status": "charged"}


# :snippet-end:

# :remove-start:
assert handle_order("A-1") == {"order_id": "A-1", "status": "charged"}
print("✓ trace-agent-decorator validated")
# :remove-end:


# :snippet-start: trace-agent-context-py
import langsmith as ls
from langsmith import traceable, tracing_context


@traceable
def handle_order(order_id: str) -> dict:
    return {"order_id": order_id, "status": "charged"}


with tracing_context(address=ls.AgentAddress("checkout", "production")):
    handle_order("A-1")
# :snippet-end:

# :remove-start:
print("✓ trace-agent-context validated")
# :remove-end:
