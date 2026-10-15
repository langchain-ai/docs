"""Interpreters: QuickJS middleware examples for the interpreters docs page."""

from __future__ import annotations

from deepagents import create_deep_agent
from langchain.tools import tool
from langchain_quickjs import CodeInterpreterMiddleware
from langchain_quickjs._ptc import filter_tools_for_ptc
from langchain_quickjs._repl import _Registry
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


def _registry() -> _Registry:
    return _Registry(
        memory_limit=64 * 1024 * 1024,
        timeout=5.0,
        capture_console=True,
        max_stdout_chars=4000,
        max_ptc_calls=256,
        subagents_enabled=False,
    )


def _eval_js(code: str) -> str:
    repl = _registry().get("interpreters-eval-test")
    outcome = repl.eval_sync(code, outer_runtime=None)
    if outcome.error_type:
        msg = outcome.error_message or outcome.error_type
        raise AssertionError(msg)
    return outcome.result or ""


assert agent is not None
assert CodeInterpreterMiddleware().tools
assert CodeInterpreterMiddleware(ptc=["web_search"]).tools
assert CodeInterpreterMiddleware(mode="thread").tools
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

repl = _registry().get("interpreters-ptc-test")
repl.install_tools(
    filter_tools_for_ptc([web_search], [web_search], self_tool_name="eval"),
)
ptc_outcome = repl.eval_sync(
    """
const result = await tools.webSearch({
  query: "deepagents interpreters",
});
result;
""",
    outer_runtime=None,
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
    outer_runtime=None,
)
assert "retrieval best practices 2025" in (parallel_outcome.result or "")

task_outcome = repl.eval_sync(
    """
const paths = ["src/auth.ts", "src/routes/api.ts"];
paths.length;
""",
    outer_runtime=None,
)
assert task_outcome.result == "2"

print("✓ interpreters")
# :remove-end:
