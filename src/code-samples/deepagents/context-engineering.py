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

# :remove-start:
assert agent is not None
# :remove-end:

# :snippet-start: context-engineering-memory-py
agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    memory=["/project/AGENTS.md", "~/.deepagents/preferences.md"],
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:

# :snippet-start: context-engineering-skills-py
agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    skills=["/skills/research/", "/skills/web-search/"],
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:

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

# :remove-start:
_direct_tool_result = search_orders.invoke(
    {"user_id": "user-123", "status": "pending", "limit": 5},
)
assert "user-123" in _direct_tool_result and "pending" in _direct_tool_result
# :remove-end:

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

# :remove-start:


@dataclass
class _MockRuntime:
    context: Context


_runtime_direct = fetch_user_data.func(
    "recent activity",
    _MockRuntime(context=Context(user_id="user-123", api_key="sk-test")),
)
assert "user-123" in _runtime_direct
# :remove-end:

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

# :remove-start:
_state_messages = result["messages"]
assert any(
    "https://example.com/report" in str(getattr(message, "content", ""))
    for message in _state_messages
)
# :remove-end:

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
assert agent is not None
# :remove-end:

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

# :remove-start:
from langchain.messages import AIMessage

_research_agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt=(
        "You are a coordinator. For every request, call task() with "
        "subagent_type set to researcher."
    ),
    subagents=[research_subagent],
)
_research_result = _research_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Research recent advances in quantum computing.",
            },
        ],
    },
)
_research_messages = _research_result["messages"]
_delegated_research = any(
    isinstance(message, AIMessage)
    and message.tool_calls
    and any(tool_call["name"] == "task" for tool_call in message.tool_calls)
    for message in _research_messages
)
assert _delegated_research
# :remove-end:

# :snippet-start: context-engineering-long-term-memory-py
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    store=store,
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(namespace=lambda _rt: ("memories",)),
        },
    ),
    system_prompt="""When users tell you their preferences, save them to
    /memories/user_preferences.txt so you remember them in future conversations.""",
)
# :snippet-end:

# :remove-start:
from langchain.messages import AIMessage

_test_store = InMemoryStore()
_test_agent = create_deep_agent(
    model="openai:gpt-5.5",
    store=_test_store,
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(namespace=lambda _rt: ("memories",)),
        },
    ),
    system_prompt=(
        "When the user shares a preference, you MUST call write_file to save it "
        "to /memories/user_preferences.txt before replying. Include the preference "
        "text verbatim in the file content."
    ),
)
_long_term_result = _test_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Remember that I prefer concise responses.",
            },
        ],
    },
)

_preferences_path = "/memories/user_preferences.txt"
_file_content = ""
_preferences_file = _long_term_result.get("files", {}).get(_preferences_path)
if isinstance(_preferences_file, dict):
    _raw_content = _preferences_file.get("content", "")
    if isinstance(_raw_content, list):
        _file_content = "\n".join(str(line) for line in _raw_content)
    else:
        _file_content = str(_raw_content)

if "concise" not in _file_content.lower():
    for _item in _test_store.search(("memories",)):
        _text = str(_item.value)
        if "concise" in _text.lower():
            _file_content = _text
            break

if "concise" not in _file_content.lower():
    _wrote_preference = any(
        isinstance(message, AIMessage)
        and message.tool_calls
        and any(
            tool_call["name"] == "write_file"
            and "concise" in str(tool_call.get("args", {})).lower()
            for tool_call in message.tool_calls
        )
        for message in _long_term_result["messages"]
    )
    if not _wrote_preference:
        raise AssertionError(
            f'expected {_preferences_path} to contain "concise", got: {_file_content or "(missing file)"}',
        )

print("✓ context-engineering sample validated")
# :remove-end:
