# :remove-start:
import os

# Constructing chat models needs a credential even though no request is sent.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-runtime-system-message-py
from dataclasses import dataclass
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage
from langgraph.graph import END, MessagesState, StateGraph, START
from langgraph.runtime import Runtime

@dataclass
class ContextSchema:
    model_provider: str = "anthropic"
    system_message: str | None = None

MODELS = {
    "anthropic": init_chat_model("claude-haiku-4-5-20251001"),
    "openai": init_chat_model("gpt-5.4-mini"),
}

def call_model(state: MessagesState, runtime: Runtime[ContextSchema]):
    model = MODELS[runtime.context.model_provider]
    messages = state["messages"]
    if (system_message := runtime.context.system_message):
        messages = [SystemMessage(system_message)] + messages
    response = model.invoke(messages)
    return {"messages": [response]}

builder = StateGraph(MessagesState, context_schema=ContextSchema)
builder.add_node("model", call_model)
builder.add_edge(START, "model")
builder.add_edge("model", END)

graph = builder.compile()
# :remove-start:
# Construction only: stop before the invocation below, which calls a live model.
assert "model" in graph.nodes
assert set(MODELS) == {"anthropic", "openai"}
assert ContextSchema(system_message="Respond in Italian.").system_message
print(
    "✓ langgraph-graph-api-nodes-runtime-system-message-py validated "
    "(construction only)"
)
raise SystemExit(0)
# :remove-end:

# Usage
input_message = {"role": "user", "content": "hi"}
response = graph.invoke({"messages": [input_message]}, context={"model_provider": "openai", "system_message": "Respond in Italian."})
for message in response["messages"]:
    message.pretty_print()
# :snippet-end:
