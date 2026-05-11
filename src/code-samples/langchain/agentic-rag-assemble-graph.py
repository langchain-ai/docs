# :snippet-start: agentic-rag-assemble-graph-py
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

# :remove-start:
from typing import Any
from langgraph.graph import MessagesState
from langchain.messages import AIMessage
from langchain.tools import tool


@tool
def retriever_tool(query: str) -> str:
    """Return deterministic context for a query."""
    return f"context for: {query}"


def generate_query_or_respond(state: MessagesState) -> dict[str, Any]:
    """Minimal stub that passes through state."""
    return {"messages": state["messages"]}


def rewrite_question(state: MessagesState) -> dict[str, Any]:
    return {"messages": state["messages"]}


def generate_answer(state: MessagesState) -> dict[str, Any]:
    return {"messages": state["messages"]}


def grade_documents(state: MessagesState) -> str:
    """Minimal stub router for the next step."""
    return "generate_answer"


# :remove-end:

workflow = StateGraph(MessagesState)

# Define the nodes we will cycle between
workflow.add_node(generate_query_or_respond)
workflow.add_node("retrieve", ToolNode([retriever_tool]))
workflow.add_node(rewrite_question)
workflow.add_node(generate_answer)

workflow.add_edge(START, "generate_query_or_respond")


# Route based on whether the model requested tool calls.
def route_on_tool_calls(state: MessagesState):
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


# Decide whether to retrieve
workflow.add_conditional_edges(
    "generate_query_or_respond",
    # Assess LLM decision (call `retriever_tool` tool or respond to the user)
    route_on_tool_calls,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
)
workflow.add_edge("generate_answer", END)
workflow.add_edge("rewrite_question", "generate_query_or_respond")

# Compile
graph = workflow.compile()

# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    # Sanity check routing behavior
    tool_calling_state: MessagesState = {
        "messages": [
            AIMessage(
                content="x",
                tool_calls=[
                    {"name": "retriever_tool", "args": {"query": "q"}, "id": "1"}
                ],
            )
        ]
    }
    assert route_on_tool_calls(tool_calling_state) == "tools"

    no_tool_call_state: MessagesState = {"messages": [AIMessage(content="x")]}
    assert route_on_tool_calls(no_tool_call_state) == END

    assert graph is not None
    print("✓ graph compiles and route_on_tool_calls works")

# :remove-end:
