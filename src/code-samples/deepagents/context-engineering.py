"""Context engineering page code samples."""

# :snippet-start: context-engineering-system-prompt-py
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    system_prompt=(
        "You are a research assistant specializing in scientific literature. "
        "Always cite sources. Use subagents for parallel research on different topics."
    ),
)
# :snippet-end:

# :snippet-start: context-engineering-memory-py
agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    memory=["/project/AGENTS.md", "~/.deepagents/preferences.md"],
)
# :snippet-end:

# :snippet-start: context-engineering-skills-py
agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    skills=["/skills/research/", "/skills/web-search/"],
)
# :snippet-end:

# :snippet-start: context-engineering-tool-prompts-py
from langchain.tools import tool


@tool(parse_docstring=True)
def search_orders(
    user_id: str,
    status: str,
    limit: int = 10,
) -> str:
    """Search for user orders by status.

    Use this when the user asks about order history or wants to check
    order status. Always filter by the provided status.

    Args:
        user_id: Unique identifier for the user
        status: Order status: 'pending', 'shipped', or 'delivered'
        limit: Maximum number of results to return
    """
    # Implementation here
    return f"orders for {user_id} with status {status} (limit {limit})"
# :snippet-end:

# :snippet-start: context-engineering-runtime-context-py
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.tools import ToolRuntime, tool


@dataclass
class Context:
    user_id: str
    api_key: str


@tool
def fetch_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    """Fetch data for the current user."""
    user_id = runtime.context.user_id
    return f"Data for user {user_id}: {query}"


agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[fetch_user_data],
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Get my recent activity"}]},
    context=Context(user_id="user-123", api_key="sk-..."),
)
# :snippet-end:

# :snippet-start: context-engineering-state-schema-py
from deepagents import DeepAgentState, create_deep_agent
from langchain.tools import ToolRuntime, tool


class ResearchState(DeepAgentState):
    page_url: str
    file_urls: list[str]


@tool
def cite_page(runtime: ToolRuntime) -> str:
    """Return the current page URL."""
    return runtime.state["page_url"]


agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[cite_page],
    state_schema=ResearchState,
)

result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "Cite the current page"}],
        "page_url": "https://example.com/report",
        "file_urls": [],
    },
)
# :snippet-end:

# :snippet-start: context-engineering-summarization-tool-py
from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.middleware.summarization import create_summarization_tool_middleware

backend = StateBackend  # if using default backend

model = "google_genai:gemini-3.5-flash"
agent = create_deep_agent(
    model=model,
    middleware=[  # [!code highlight]
        create_summarization_tool_middleware(model, backend),  # [!code highlight]
    ],  # [!code highlight]
)
# :snippet-end:

# :remove-start:
def web_search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"
# :remove-end:

# :snippet-start: context-engineering-research-subagent-py
research_subagent = {
    "name": "researcher",
    "description": "Conducts research on a topic",
    "system_prompt": """You are a research assistant.
    IMPORTANT: Return only the essential summary (under 500 words).
    Do NOT include raw search results or detailed tool outputs.""",
    "tools": [web_search],
}
# :snippet-end:

# :snippet-start: context-engineering-long-term-memory-py
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore


def make_backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={"/memories/": StoreBackend(runtime)},
    )


agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    store=InMemoryStore(),
    backend=make_backend,
    system_prompt="""When users tell you their preferences, save them to
    /memories/user_preferences.txt so you remember them in future conversations.""",
)
# :snippet-end:

# :remove-start:
assert agent is not None
assert search_orders.name == "search_orders"
assert fetch_user_data.name == "fetch_user_data"
assert result is not None
assert research_subagent["name"] == "researcher"
print("✓ context-engineering sample validated")
# :remove-end:
