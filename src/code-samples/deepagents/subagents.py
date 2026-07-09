"""Subagents page code samples."""

from __future__ import annotations

# :remove-start:
def internet_search(query: str, max_results: int = 5) -> str:
    return f"search results for {query}"


def web_search(query: str) -> str:
    return f"web results for {query}"


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"sent to {to}"


def validate_email(address: str) -> bool:
    """Validate an email address."""
    return "@" in address


def read_document(path: str) -> str:
    """Read a document."""
    return f"document: {path}"


def analyze_contract(path: str) -> str:
    """Analyze a contract."""
    return "contract analysis"


def get_stock_price(symbol: str) -> str:
    """Get a stock price."""
    return f"price for {symbol}"


def analyze_fundamentals(symbol: str) -> str:
    """Analyze stock fundamentals."""
    return f"fundamentals for {symbol}"


def web_search_tool(query: str) -> str:
    """Search the web."""
    return f"web: {query}"


def api_call(endpoint: str) -> str:
    """Call an API endpoint."""
    return f"api: {endpoint}"


def database_query(sql: str) -> str:
    """Run a database query."""
    return f"db: {sql}"


def statistical_analysis(data: str) -> str:
    """Run statistical analysis."""
    return f"stats: {data}"


def format_document(content: str) -> str:
    """Format a document."""
    return f"formatted: {content}"


def strict_lookup(query: str) -> str:
    return f"strict: {query}"


def general_lookup(query: str) -> str:
    return f"general: {query}"


def strict_verification(claim: str) -> str:
    return f"strict verified: {claim}"


def basic_verification(claim: str) -> str:
    return f"basic verified: {claim}"


def perform_search(query: str, max_results: int = 5, include_raw: bool = False) -> str:
    return f"search {query} max={max_results} raw={include_raw}"


research_instructions = "You are a research coordinator."
your_model = "openai:gpt-5.5"
specialized_tools: list = []
# :remove-end:

# :snippet-start: subagents-compiled-subagent-py
from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent


def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"


research_instructions = "You are a research coordinator."
your_model = "openai:gpt-5.5"
specialized_tools: list = []

# Create a custom agent graph
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    system_prompt="You are a specialized agent for data analysis...",
)

# Use it as a custom subagent
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph,
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents,
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:

# :snippet-start: subagents-structured-output-py
import asyncio

from pydantic import BaseModel, Field

from deepagents import create_deep_agent


def web_search(query: str) -> str:
    """Search the web."""
    return f"web results for {query}"


class ResearchFindings(BaseModel):
    """Structured findings from a research task."""

    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLs")


research_subagent = {
    "name": "researcher",
    "description": "Researches topics and returns structured findings",
    "system_prompt": "Research the given topic thoroughly. Return your findings.",
    "tools": [web_search],
    "response_format": ResearchFindings,
}

agent = create_deep_agent(
    model="claude-sonnet-4-6",
    subagents=[research_subagent],
)

async def main():
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Research recent advances in quantum computing"}]}
    )
    return result

result = asyncio.run(main())

# The parent's ToolMessage contains JSON-serialized structured data:
# '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
# :snippet-end:

# :remove-start:
assert result is not None
# :remove-end:

# :snippet-start: subagents-general-purpose-override-py
from deepagents import create_deep_agent


def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"


# Main agent uses Gemini; general-purpose subagent uses GPT
agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[internet_search],
    subagents=[
        {
            "name": "general-purpose",
            "description": "General-purpose agent for research and multi-step tasks",
            "system_prompt": "You are a general-purpose assistant.",
            "tools": [internet_search],
            "model": "openai:gpt-5.5",  # Different model for delegated tasks
        },
    ],
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:

# :snippet-start: subagents-research-prompt-py
research_subagent = {
    "name": "research-agent",
    "description": "Conducts in-depth research using web search and synthesizes findings",
    "system_prompt": """You are a thorough researcher. Your job is to:

    1. Break down the research question into searchable queries
    2. Use internet_search to find relevant information
    3. Synthesize findings into a comprehensive but concise summary
    4. Cite sources when making claims

    Output format:
    - Summary (2-3 paragraphs)
    - Key findings (bullet points)
    - Sources (with URLs)

    Keep your response under 500 words to maintain clean context.""",
    "tools": [internet_search],
}
# :snippet-end:

# :remove-start:
_research_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[research_subagent],
)
assert _research_agent is not None
# :remove-end:

# :snippet-start: subagents-email-tools-good-py
# ✅ Good: Focused tool set
email_agent = {
    "name": "email-sender",
    "tools": [send_email, validate_email],  # Only email-related
}
# :snippet-end:

# :remove-start:
assert len(email_agent["tools"]) == 2
_focused_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[
        {
            "description": "Sends and validates email",
            "system_prompt": "You send email messages.",
            **email_agent,
        },
    ],
)
assert _focused_agent is not None
# :remove-end:

# :snippet-start: subagents-email-tools-bad-py
# ❌ Bad: Too many tools
email_agent = {
    "name": "email-sender",
    "tools": [send_email, web_search_tool, database_query, format_document],  # Unfocused
}
# :snippet-end:

# :remove-start:
assert len(email_agent["tools"]) == 4
_unfocused_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[
        {
            "description": "Sends email but has too many tools",
            "system_prompt": "You send email messages.",
            **email_agent,
        },
    ],
)
assert _unfocused_agent is not None
# :remove-end:

# :snippet-start: subagents-choose-models-py
subagents = [
    {
        "name": "contract-reviewer",
        "description": "Reviews legal documents and contracts",
        "system_prompt": "You are an expert legal reviewer...",
        "tools": [read_document, analyze_contract],
        "model": "google_genai:gemini-3.5-flash",  # Large context for long documents
    },
    {
        "name": "financial-analyst",
        "description": "Analyzes financial data and market trends",
        "system_prompt": "You are an expert financial analyst...",
        "tools": [get_stock_price, analyze_fundamentals],
        "model": "openai:gpt-5.5",  # Better for numerical analysis
    },
]
# :snippet-end:

# :remove-start:
assert len(subagents) == 2
assert subagents[0]["model"].startswith("google_genai:")
_choose_models_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=subagents,
)
assert _choose_models_agent is not None
# :remove-end:

# :snippet-start: subagents-concise-results-py
data_analyst = {
    "system_prompt": """Analyze the data and return:
    1. Key insights (3-5 bullet points)
    2. Overall confidence score
    3. Recommended next actions

    Do NOT include:
    - Raw data
    - Intermediate calculations
    - Detailed tool outputs

    Keep response under 300 words."""
}
# :snippet-end:

# :remove-start:
assert "Key insights" in data_analyst["system_prompt"]
_concise_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[
        {
            "name": "data-analyst",
            "description": "Analyzes data and returns concise summaries",
            **data_analyst,
        },
    ],
)
assert _concise_agent is not None
# :remove-end:

# :snippet-start: subagents-multiple-specialized-py
from deepagents import create_deep_agent

subagents = [
    {
        "name": "data-collector",
        "description": "Gathers raw data from various sources",
        "system_prompt": "Collect comprehensive data on the topic",
        "tools": [web_search_tool, api_call, database_query],
    },
    {
        "name": "data-analyzer",
        "description": "Analyzes collected data for insights",
        "system_prompt": "Analyze data and extract key insights",
        "tools": [statistical_analysis],
    },
    {
        "name": "report-writer",
        "description": "Writes polished reports from analysis",
        "system_prompt": "Create professional reports from insights",
        "tools": [format_document],
    },
]

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    system_prompt="You coordinate data analysis and reporting. Use subagents for specialized tasks.",
    subagents=subagents,
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:

# :snippet-start: subagents-context-propagation-py
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool


@dataclass
class Context:
    user_id: str
    session_id: str


@tool
def get_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    """Fetch data for the current user."""
    user_id = runtime.context.user_id
    return f"Data for user {user_id}: {query}"


research_subagent = {
    "name": "researcher",
    "description": "Conducts research for the current user",
    "system_prompt": "You are a research assistant.",
    "tools": [get_user_data],
}

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[research_subagent],
    context_schema=Context,
)

# Context flows to the researcher subagent and its tools automatically
async def main():
    result = await agent.invoke(
        {"messages": [HumanMessage("Look up my recent activity")]},
        context=Context(user_id="user-123", session_id="abc"),
    )
    return result

result = asyncio.run(main())
# :snippet-end:

# :remove-start:

@dataclass
class _MockRuntime:
    context: Context


_direct = get_user_data.func(
    "recent activity",
    _MockRuntime(context=Context(user_id="user-123", session_id="abc")),
)
assert "user-123" in _direct
assert agent is not None
assert result is not None
# :remove-end:

# :snippet-start: subagents-per-subagent-context-py
from dataclasses import dataclass

from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool


@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None


@tool
def verify_claim(claim: str, runtime: ToolRuntime[Context]) -> str:
    """Verify a factual claim."""
    strict_mode = runtime.context.fact_checker_strict_mode or False
    if strict_mode:
        return strict_verification(claim)
    return basic_verification(claim)


async def main():
    result = await agent.invoke(
        {"messages": [HumanMessage("Research this and verify the claims")]},
        context=Context(
            user_id="user-123",
            researcher_max_depth=3,
            fact_checker_strict_mode=True,
        ),
    )
    return result

result = asyncio.run(main())
# :snippet-end:

# :remove-start:
assert result is not None


@dataclass
class _VerifyRuntime:
    context: Context


_strict = verify_claim.func(
    "test claim",
    _VerifyRuntime(
        context=Context(
            user_id="user-123",
            researcher_max_depth=3,
            fact_checker_strict_mode=True,
        ),
    ),
)
assert "strict verified" in _strict
_per_subagent_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[
        {
            "name": "fact-checker",
            "description": "Verifies factual claims",
            "system_prompt": "You verify claims carefully.",
            "tools": [verify_claim],
        },
    ],
    context_schema=Context,
)
assert _per_subagent_agent is not None
# :remove-end:

# :snippet-start: subagents-shared-lookup-py

# :snippet-start: subagents-shared-lookup-py
from langchain.tools import ToolRuntime, tool


@tool
def shared_lookup(query: str, runtime: ToolRuntime) -> str:
    """Look up information."""
    agent_name = runtime.config.get("metadata", {}).get("lc_agent_name")
    if agent_name == "fact-checker":
        return strict_lookup(query)
    return general_lookup(query)
# :snippet-end:

# :remove-start:


class _ConfigRuntime:
    config = {"metadata": {"lc_agent_name": "fact-checker"}}


assert "strict" in shared_lookup.func("query", _ConfigRuntime())
# :remove-end:

# :snippet-start: subagents-flexible-search-py
from dataclasses import dataclass

from langchain.tools import ToolRuntime, tool


@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None


@tool
def flexible_search(query: str, runtime: ToolRuntime[Context]) -> str:
    """Search with agent-specific settings."""
    agent_name = runtime.config.get("metadata", {}).get("lc_agent_name", "unknown")
    ctx = runtime.context
    if agent_name == "researcher":
        max_results = ctx.researcher_max_depth or 5
    else:
        max_results = 5
    include_raw = False

    return perform_search(query, max_results=max_results, include_raw=include_raw)
# :snippet-end:

# :remove-start:


@dataclass
class _FlexRuntime:
    context: Context
    config: dict


_flex = flexible_search.func(
    "quantum",
    _FlexRuntime(
        context=Context(user_id="u1", researcher_max_depth=3),
        config={"metadata": {"lc_agent_name": "researcher"}},
    ),
)
assert "max=3" in _flex
# :remove-end:

# :snippet-start: subagents-troubleshooting-description-good-py
# ✅ Good
good_subagent = {
    "name": "research-specialist",
    "description": "Conducts in-depth research on specific topics using web search. Use when you need detailed information that requires multiple searches.",
}
# :snippet-end:

# :remove-start:
_good_description_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[
        {
            "system_prompt": "You are a research specialist.",
            **good_subagent,
        },
    ],
)
assert _good_description_agent is not None
# :remove-end:

# :snippet-start: subagents-troubleshooting-description-bad-py
# ❌ Bad
bad_subagent = {
    "name": "helper",
    "description": "helps with stuff",
}
# :snippet-end:

# :remove-start:
_bad_description_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[
        {
            "system_prompt": "You are a helper.",
            **bad_subagent,
        },
    ],
)
assert _bad_description_agent is not None
# :remove-end:

# :snippet-start: subagents-troubleshooting-delegate-py
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:

# :snippet-start: subagents-troubleshooting-concise-prompt-py
system_prompt = """...

IMPORTANT: Return only the essential summary.
Do NOT include raw data, intermediate search results, or detailed tool outputs.
Your response should be under 500 words."""
# :snippet-end:

# :remove-start:
assert "essential summary" in system_prompt
_concise_prompt_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[
        {
            "name": "research-agent",
            "description": "Researches topics and returns concise summaries",
            "system_prompt": system_prompt,
        },
    ],
)
assert _concise_prompt_agent is not None
# :remove-end:

# :snippet-start: subagents-troubleshooting-filesystem-prompt-py
system_prompt = """When you gather large amounts of data:
1. Save raw data to /data/raw_results.txt
2. Process and analyze the data
3. Return only the analysis summary

This keeps context clean."""
# :snippet-end:

# :remove-start:
assert "/data/raw_results.txt" in system_prompt
_filesystem_prompt_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[
        {
            "name": "data-analyst",
            "description": "Analyzes large datasets via the filesystem",
            "system_prompt": system_prompt,
        },
    ],
)
assert _filesystem_prompt_agent is not None
# :remove-end:

# :snippet-start: subagents-troubleshooting-differentiate-py
subagents = [
    {
        "name": "quick-researcher",
        "description": "For simple, quick research questions that need 1-2 searches. Use when you need basic facts or definitions.",
        "system_prompt": "You are the quick-researcher subagent.",
    },
    {
        "name": "deep-researcher",
        "description": "For complex, in-depth research requiring multiple searches, synthesis, and analysis. Use for comprehensive reports.",
        "system_prompt": "You are the deep-researcher subagent.",
    },
]
# :snippet-end:

# :remove-start:
assert subagents[0]["name"] == "quick-researcher"
_differentiate_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=subagents,
)
assert _differentiate_agent is not None
# :remove-end:
