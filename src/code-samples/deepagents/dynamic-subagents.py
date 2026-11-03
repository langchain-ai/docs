"""Dynamic subagents: interpreter orchestration examples for the dynamic subagents docs page."""

from __future__ import annotations

from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware
from langchain_quickjs._repl import _Registry

# :snippet-start: dynamic-subagents-quickstart-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Report issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
# :snippet-end:

# :snippet-start: dynamic-subagents-invoke-py
result = agent.invoke({
    "messages": [{"role": "user", "content": "Run a workflow that reviews every file in src/routes/ and summarizes the top risks."}]
})
# :snippet-end:

# :snippet-start: dynamic-subagents-classify-configure-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[
        {
            "name": "bug-fixer",
            "description": "Investigates bug reports and provides reproduction steps",
            "system_prompt": "You are a bug triage specialist. Investigate each bug report and provide clear reproduction steps.",
        },
        {
            "name": "feature-analyst",
            "description": "Evaluates feature requests for feasibility and effort",
            "system_prompt": "You are a product analyst. Evaluate each feature request for technical feasibility, estimated effort, and potential impact.",
        },
        {
            "name": "support-agent",
            "description": "Answers user questions based on documentation",
            "system_prompt": "You are a support specialist. Answer user questions clearly based on the available documentation.",
        },
    ],
    middleware=[CodeInterpreterMiddleware()],
)
# :snippet-end:

# :snippet-start: dynamic-subagents-fanout-configure-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Read the file carefully and report any authentication or authorization issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware(ptc=["glob"])],
)
# :snippet-end:

# :snippet-start: dynamic-subagents-adversarial-configure-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[
        {
            "name": "reviewer",
            "description": "Finds potential security vulnerabilities in code",
            "system_prompt": "You are a security auditor. Find potential vulnerabilities and report each with file, line, and description.",
        },
        {
            "name": "verifier",
            "description": "Independently verifies whether a reported vulnerability is real",
            "system_prompt": "You are a security verification specialist. Given a reported vulnerability, independently verify whether it is exploitable. Be skeptical. Only confirm real issues.",
        },
    ],
    middleware=[CodeInterpreterMiddleware()],
)
# :snippet-end:

# :snippet-start: dynamic-subagents-generate-configure-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[{
        "name": "architect",
        "description": "Proposes a database schema design with tradeoff analysis",
        "system_prompt": "You are a database architect. Propose a schema design for the given requirements. Include tradeoffs, migration considerations, and a clear rationale.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
# :snippet-end:

# :snippet-start: dynamic-subagents-tournament-configure-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[
        {
            "name": "writer",
            "description": "Rewrites a function with a focus on readability and clarity",
            "system_prompt": "You are an expert programmer focused on clean code. Rewrite the given function to maximize readability. Explain your choices.",
        },
        {
            "name": "judge",
            "description": "Compares two code implementations and picks the more readable one",
            "system_prompt": "You are a code quality judge. Compare two implementations and pick the more readable one. Justify your choice with specific criteria.",
        },
    ],
    middleware=[CodeInterpreterMiddleware()],
)
# :snippet-end:

# :snippet-start: dynamic-subagents-loop-configure-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[{
        "name": "analyzer",
        "description": "Analyzes code for unused exports, functions, and dead code paths",
        "system_prompt": "You are a code analyst specializing in dead code detection. Find unused exports, unreachable functions, and orphaned modules. Report each with file path and evidence.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
# :snippet-end:

# :snippet-start: dynamic-subagents-disable-py
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[{"name": "reviewer", "description": "Reviews code", "system_prompt": "Review code."}],
    middleware=[CodeInterpreterMiddleware(subagents=False)],
)
# :snippet-end:

# :remove-start:
def _eval_js(code: str) -> str:
    repl = _Registry(
        memory_limit=64 * 1024 * 1024,
        timeout=5.0,
        capture_console=True,
        max_stdout_chars=4000,
        max_ptc_calls=256,
        subagents_enabled=True,
    ).get("dynamic-subagents-eval-test")
    outcome = repl.eval_sync(code, outer_runtime=None)
    if outcome.error_type:
        msg = outcome.error_message or outcome.error_type
        raise AssertionError(msg)
    return outcome.result or ""


assert agent is not None
assert CodeInterpreterMiddleware().tools
assert CodeInterpreterMiddleware(ptc=["glob"]).tools
assert CodeInterpreterMiddleware(subagents=False).tools

task_api_result = _eval_js(
    """
const review = {
  issues: [
    { file: "src/auth/login.ts", line: 12, severity: "high", description: "missing auth" },
    { file: "src/auth/login.ts", line: 40, severity: "low", description: "style" },
  ],
};
const critical = review.issues.filter((issue) => issue.severity === "high");
critical.length;
"""
)
assert task_api_result == "1"

print("✓ dynamic-subagents")
# :remove-end:
