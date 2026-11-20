"""Interpreters: QuickJS middleware examples for the interpreters docs page."""

from __future__ import annotations

from deepagents import create_deep_agent
from langchain.tools import tool
from langchain_quickjs import CodeInterpreterMiddleware
from langchain_quickjs._ptc import filter_tools_for_ptc
from langchain_quickjs._repl import _Slot, _SlotConfig
from langgraph.checkpoint.memory import MemorySaver

# :snippet-start: interpreters-quickstart-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[CodeInterpreterMiddleware()],
)
# :snippet-end:

# :snippet-start: interpreters-enable-ptc-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[CodeInterpreterMiddleware(ptc=["web_search"])],
)
# :snippet-end:

# :snippet-start: interpreters-enable-fs-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[CodeInterpreterMiddleware(fs=True)],
)
# :snippet-end:

# :snippet-start: interpreters-persistence-default-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[
        CodeInterpreterMiddleware(
            mode="thread",  # Default
        )
    ],
)
# :snippet-end:

# :snippet-start: interpreters-persistence-checkpointer-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    checkpointer=MemorySaver(),
    middleware=[CodeInterpreterMiddleware(mode="thread")],
)
# :snippet-end:

# :remove-start:
@tool
def web_search(query: str) -> str:
    """Search the web."""
    return f"results for {query}"


def _slot(name: str) -> _Slot:
    return _Slot(name, _SlotConfig(subagents_enabled=False))


def _eval_js(code: str) -> str:
    outcome = _slot("interpreters-eval-test").eval_sync(code)
    if outcome.error_type:
        msg = outcome.error_message or outcome.error_type
        raise AssertionError(msg)
    return outcome.result or ""


assert agent is not None
assert CodeInterpreterMiddleware().tools
assert CodeInterpreterMiddleware(ptc=["web_search"]).tools
assert CodeInterpreterMiddleware(mode="thread").tools
assert CodeInterpreterMiddleware(fs=True).tools
persistence_agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    checkpointer=MemorySaver(),
    middleware=[CodeInterpreterMiddleware(mode="thread")],
)
assert persistence_agent is not None

totals_result = _eval_js(
    """
const rows = [
  { team: "alpha", score: 8 },
  { team: "beta", score: 13 },
  { team: "alpha", score: 21 },
];

const totals = rows.reduce((acc, row) => {
  acc[row.team] = (acc[row.team] ?? 0) + row.score;
  console.log(`${row.team} score: ${acc[row.team]}`)
  return acc;
}, {});

totals;
"""
)
assert "alpha" in totals_result and "29" in totals_result

repl = _slot("interpreters-ptc-test")
ptc_tools = filter_tools_for_ptc([web_search], [web_search], self_tool_name="eval")
ptc_outcome = repl.eval_sync(
    """
const result = await tools.webSearch({
  query: "deepagents interpreters",
});
result;
""",
    tools=ptc_tools,
)
assert ptc_outcome.result == "results for deepagents interpreters"

parallel_outcome = repl.eval_sync(
    """
const topics = ["retrieval", "memory", "evaluation"];

const results = await Promise.all(
  topics.map((topic) =>
    tools.webSearch({ query: `${topic} best practices 2025` }),
  ),
);

results.join("\\n\\n");
""",
    tools=ptc_tools,
)
assert "retrieval best practices 2025" in (parallel_outcome.result or "")

task_outcome = repl.eval_sync(
    """
const paths = ["src/auth.ts", "src/routes/api.ts"];
paths.length;
""",
    tools=ptc_tools,
)
assert task_outcome.result == "2"

print("✓ interpreters")
# :remove-end:
