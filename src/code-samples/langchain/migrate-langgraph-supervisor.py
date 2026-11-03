"""Migrate from langgraph-supervisor to the subagents pattern."""

# :remove-start:
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.types import Command

model = "openai:gpt-5-nano"


@tool
def web_search(query: str) -> str:
    """Search the web for current information."""
    return f"Search results for: {query}"


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


def fire_external_api(document_id: str) -> str:
    return f"job-{document_id}"


def render_results(result: dict) -> str:
    return f"Rendered preview: {result}"


external_result = {"status": "complete", "preview": "enrichment data"}
# :remove-end:

# :snippet-start: migrate-langgraph-supervisor-basic-py
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

research_agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt="You are a research expert.",
)

math_agent = create_agent(
    model=model,
    tools=[add, multiply],
    system_prompt="You are a math expert.",
)


@tool("research_expert", description="Research expert for current events and web lookups.")
def call_research_agent(query: str) -> str:
    result = research_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content


@tool("math_expert", description="Math expert for calculations.")
def call_math_agent(query: str) -> str:
    result = math_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content


supervisor = create_agent(
    model=model,
    tools=[call_research_agent, call_math_agent],
    system_prompt=(
        "Route research questions to research_expert and math to math_expert."
    ),
    checkpointer=InMemorySaver(),
)
# :snippet-end:

# :remove-start:
_basic_supervisor = supervisor
# :remove-end:

# :snippet-start: migrate-langgraph-supervisor-interrupt-py
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt


@tool
def preview_tool(document_id: str) -> str:
    """Run an async enrichment preview and wait for results."""
    job_id = fire_external_api(document_id)
    result = interrupt({"job_id": job_id, "status": "pending"})
    return render_results(result)


research_agent = create_agent(
    model=model,
    tools=[preview_tool],
    system_prompt="You are a research agent.",
)

@tool("research_agent", description="Research and enrichment tasks.")
def call_research_agent(query: str) -> str:
    result = research_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

supervisor = create_agent(
    model=model,
    tools=[call_research_agent],
    system_prompt="Delegate research tasks to research_agent.",
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "1"}}
# :snippet-end:

# :remove-start:
_interrupt_supervisor = supervisor
_interrupt_config = config

@tool("refunds_agent", description="Handle refund requests.")
def call_refunds_agent(query: str) -> str:
    return f"Refunds: {query}"


@tool("invoices_agent", description="Handle invoice questions.")
def call_invoices_agent(query: str) -> str:
    return f"Invoices: {query}"


@tool("support_agent", description="Handle general support requests.")
def call_support_agent(query: str) -> str:
    return f"Support: {query}"
# :remove-end:

# :snippet-start: migrate-langgraph-supervisor-nested-py
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

# Middle-tier agent with its own subagents
billing_team = create_agent(
    model=model,
    tools=[call_refunds_agent, call_invoices_agent],
    system_prompt="Coordinate billing specialists.",
)

@tool("billing_team", description="Handle billing, refunds, and invoices.")
def call_billing_team(query: str) -> str:
    result = billing_team.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

# Top-level supervisor
top_supervisor = create_agent(
    model=model,
    tools=[call_billing_team, call_support_agent],
    system_prompt="Route billing to billing_team and general support to support_agent.",
    checkpointer=InMemorySaver(),
)
# :snippet-end:

# :remove-start:
def _assistant_text(result: dict) -> str:
    last = result["messages"][-1]
    if last.content_blocks:
        return last.content_blocks[0]["text"]
    return str(last.content)


if __name__ == "__main__":
    basic_result = _basic_supervisor.invoke(
        {"messages": [{"role": "user", "content": "What is 2 + 2? Use math_expert."}]},
        config={"configurable": {"thread_id": "migrate-basic"}},
    )
    assert _assistant_text(basic_result).strip()

    interrupt_stream = _interrupt_supervisor.stream_events(
        {"messages": [{"role": "user", "content": "Preview enrichment for doc-123"}]},
        config=_interrupt_config,
        version="v3",
    )
    _ = interrupt_stream.output
    assert interrupt_stream.interrupted, "Expected interrupt from preview_tool"
    resumed = _interrupt_supervisor.stream_events(
        Command(resume=external_result),
        config=_interrupt_config,
        version="v3",
    )
    assert _assistant_text(resumed.output).strip()

    nested_result = top_supervisor.invoke(
        {"messages": [{"role": "user", "content": "I need help with a refund."}]},
        config={"configurable": {"thread_id": "migrate-nested"}},
    )
    assert _assistant_text(nested_result).strip()

    print("✓ migrate-langgraph-supervisor")
# :remove-end:
