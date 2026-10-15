# :remove-start:
import time

from langsmith import Client as _SeedClient
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree, tracing_context

_SEEDED: dict[str, str] = {}


@traceable(run_type="llm")
def _leaf(index: int) -> str:
    return f"leaf {index}"


@traceable
def _branch() -> str:
    _leaf(0)
    return "branch"


@traceable(name="docs-child-runs-example")
def _root() -> str:
    run_tree = get_current_run_tree()
    assert run_tree is not None, "tracing is not enabled"
    _SEEDED["run_id"] = str(run_tree.id)
    _SEEDED["trace_id"] = str(run_tree.trace_id)
    _leaf(1)
    _branch()
    return "root"


def _seed_trace() -> tuple[str, str]:
    """Trace a small nested call tree and wait until it is readable.

    The `default` project holds no nested traces of its own, so the sample
    creates one instead of depending on data it does not control. The v1 and v2
    read paths become consistent at slightly different times, so poll until the
    v1 path returns the full child tree.
    """
    client = _SeedClient()
    with tracing_context(project_name="default", enabled=True):
        _root()
    client.flush()

    run_id, trace_id = _SEEDED["run_id"], _SEEDED["trace_id"]
    for _ in range(30):
        try:
            run = client.read_run(run_id, load_child_runs=True)
        except Exception:  # noqa: BLE001 - not ingested yet
            run = None
        if run is not None and len(run.child_runs or []) == 2:
            return run_id, trace_id
        time.sleep(2)
    raise AssertionError(f"seeded run {run_id} never became readable with children")


_RUN_ID, _TRACE_ID = _seed_trace()
# :remove-end:

# :snippet-start: runs-retrieve-child-runs-before-py
# :codegroup-tab: Before
from langsmith import Client

client = Client()
run_id = "<run-id>"
# :remove-start:
run_id = _RUN_ID
# :remove-end:

run = client.read_run(run_id, load_child_runs=True)

# `child_runs` holds the direct children, each with its own nested `child_runs`.
# `child_run_ids` holds every descendant, at any depth.
for child in run.child_runs or []:
    print(child.name, child.run_type, len(child.child_runs or []))
print(len(run.child_run_ids or []), "descendants")
# :snippet-end:

# :remove-start:
_BEFORE_DIRECT = {str(child.id) for child in run.child_runs or []}
_BEFORE_DESCENDANTS = {str(child_id) for child_id in run.child_run_ids or []}
assert len(_BEFORE_DIRECT) == 2, _BEFORE_DIRECT
assert len(_BEFORE_DESCENDANTS) == 3, _BEFORE_DESCENDANTS
# :remove-end:

# :snippet-start: runs-retrieve-child-runs-after-py
# :codegroup-tab: After
import asyncio
from collections import defaultdict

from langsmith import Client


async def main():
    client = Client()
    project = await client.aread_project(project_name="default")
    # A root run is its own trace, so `trace_id` is also the run ID.
    trace_id = "<trace-id>"
    # :remove-start:
    trace_id = _TRACE_ID
    # :remove-end:

    trace_runs = await client.traces.list_runs(
        trace_id,
        project_id=str(project.id),
        selects=["ID", "NAME", "RUN_TYPE", "PARENT_RUN_IDS", "START_TIME", "END_TIME"],
    )

    # `parent_run_ids` is the full ancestor chain, root first, closest parent
    # last. A run is a descendant of any ID in that chain, at any depth, not
    # only of the immediate parent. This flat list replaces `child_run_ids`.
    descendants = [
        run for run in (trace_runs.items or []) if trace_id in (run.parent_run_ids or [])
    ]
    print(len(descendants), "descendants")

    # Optional: rebuild the nested `child_runs` shape instead of a flat list.
    by_parent = defaultdict(list)
    for run in trace_runs.items or []:
        if run.parent_run_ids:
            # The last ancestor is the immediate parent.
            by_parent[run.parent_run_ids[-1]].append(run)

    def attach(run):
        run.child_runs = by_parent.get(run.id, [])
        for child in run.child_runs:
            attach(child)

    for run in trace_runs.items or []:
        attach(run)

    children = by_parent.get(trace_id, [])
    for child in children:
        print(child.name, child.run_type, len(child.child_runs))
    # :remove-start:
    assert {str(child.id) for child in children} == _BEFORE_DIRECT, (
        f"direct children differ: {[str(c.id) for c in children]} != {_BEFORE_DIRECT}"
    )
    assert {str(run.id) for run in descendants} == _BEFORE_DESCENDANTS, (
        f"descendants differ: {[str(r.id) for r in descendants]} "
        f"!= {_BEFORE_DESCENDANTS}"
    )
    print("✓ runs-retrieve-child-runs validated")
    # :remove-end:


asyncio.run(main())
# :snippet-end:
