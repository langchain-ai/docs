"""Deep Agents: code generation with RubricMiddleware and a test suite grader tool."""

# :snippet-start: rubric-code-generation-middleware-py
from deepagents import RubricMiddleware
from langchain.tools import tool


@tool
def run_test_suite(code: str) -> dict:
    """Run the find_duplicates test suite against Python source code."""
    namespace: dict = {"__builtins__": __builtins__}
    try:
        exec(code, namespace)
    except Exception as exc:
        return {"ok": False, "failures": [f"Failed to execute code: {exc}"]}

    find_duplicates = namespace.get("find_duplicates")
    if find_duplicates is None:
        return {"ok": False, "failures": ["Function find_duplicates is not defined"]}

    tests = [
        ("test_basic", [1, 2, 2, 3, 1], [2, 1]),
        ("test_empty", [], []),
        ("test_no_duplicates", [1, 2, 3], []),
        ("test_unhashable", [[1], [1], 2], [[1]]),
    ]
    failures: list[str] = []
    for name, args, expected in tests:
        try:
            actual = find_duplicates(args)
            if actual != expected:
                failures.append(f"{name}: expected {expected}, got {actual}")
        except Exception as exc:
            failures.append(f"{name}: {exc}")

    return {"ok": not failures, "failures": failures}


rubric_middleware = RubricMiddleware(
    model="anthropic:claude-haiku-4-5",
    system_prompt="You are a code reviewer grading generated code against a rubric.",
    tools=[run_test_suite],
    max_iterations=5,
)
# :snippet-end:

# :snippet-start: rubric-code-generation-agent-py
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt=(
        "You are a careful Python engineer. Write correct, readable code. "
        "Follow the user's instructions exactly."
    ),
    middleware=[rubric_middleware],
    checkpointer=InMemorySaver(),
)
# :snippet-end:

# :remove-start:
import os

if __name__ == "__main__":
    bad_code = """
def find_duplicates(lst):
    seen = set()
    dups = []
    for x in lst:
        if x in seen:
            dups.append(x)
        seen.add(x)
    return dups
"""
    bad_result = run_test_suite.invoke({"code": bad_code})
    assert not bad_result["ok"]
    assert any("test_unhashable" in failure for failure in bad_result["failures"])

    good_code = """
def find_duplicates(lst):
    seen = []
    dups = []
    for item in lst:
        if any(item == existing for existing in seen):
            if not any(item == dup for dup in dups):
                dups.append(item)
        else:
            seen.append(item)
    return dups
"""
    good_result = run_test_suite.invoke({"code": good_code})
    assert good_result["ok"], good_result["failures"]
    assert agent is not None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("✓ rubric code generation sample completed")
        raise SystemExit(0)
# :remove-end:

# :snippet-start: rubric-code-generation-invoke-py
from langchain.messages import HumanMessage

result = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content=(
                    "Write a Python function `find_duplicates(lst)` that returns a list of "
                    "all elements that appear more than once in the input list, in the order "
                    "they first appear."
                )
            )
        ],
        "rubric": (
            "- All tests pass in run_test_suite\n"
            "- The function is named `find_duplicates` and accepts a single list argument\n"
        ),
    },
    config={"configurable": {"thread_id": "code-generation-session"}},
)
print(result["messages"][-1].text)
# :snippet-end:
