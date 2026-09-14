"""Collect public LangSmith trace links for docs code samples.

Used by ``scripts/test_code_samples.py`` when ``CODE_SAMPLE_TRACING=1``, and by
``scripts/generate_code_snippet_mdx.py`` to append a Mintlify Card CTA under
generated snippet MDX.

Only single-snippet source files get links. Multi-snippet files are skipped until
those samples are split into one file per snippet.
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

MANIFEST_RELPATH = Path("src/code-samples/trace-links.json")
DEFAULT_PROJECT = "docs-code-samples"
TRACE_CARD_BODY = "Open a public LangSmith run for this example."
# Match the Card CTA (with or without body) and the older plain-markdown form so
# regenerations replace either.
TRACE_LINK_RE = re.compile(
    r"\n(?:"
    r"<Card\s+title=\"View example trace\"[^>]*?/>"
    r"|"
    r"<Card\s+title=\"View example trace\"[^>]*>\s*"
    + re.escape(TRACE_CARD_BODY)
    + r"\s*</Card>"
    r"|"
    r"\[View example trace\]\([^)]+\)\.?"
    r")\n?$",
)
_SNIPPET_START_RE = re.compile(r":snippet-start:\s*(\S+)")

# Root run names that indicate an agent / LangGraph harness execution.
_AGENT_NAME_RE = re.compile(
    r"(langgraph|\bagent\b|deep.?agent|create_agent|create_deep_agent)",
    re.IGNORECASE,
)


def manifest_path(repo_root: Path) -> Path:
    return repo_root / MANIFEST_RELPATH


def load_manifest(repo_root: Path) -> dict[str, Any]:
    path = manifest_path(repo_root)
    if not path.exists():
        return {
            "version": 1,
            "project": DEFAULT_PROJECT,
            "snippets": {},
            "skipped_multi_snippet": {},
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("version", 1)
    data.setdefault("project", DEFAULT_PROJECT)
    data.setdefault("snippets", {})
    data.setdefault("skipped_multi_snippet", {})
    return data


def save_manifest(repo_root: Path, data: dict[str, Any]) -> None:
    path = manifest_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def snippet_ids_in_source(source_text: str) -> list[str]:
    """Return snippet IDs in file order."""
    return _SNIPPET_START_RE.findall(source_text)


def strip_trace_link(mdx: str) -> str:
    """Remove a trailing View example trace link if present."""
    return TRACE_LINK_RE.sub("", mdx.rstrip()).rstrip() + "\n"


def append_trace_link(mdx: str, url: str | None) -> str:
    """Append or replace a View example trace CTA under snippet MDX."""
    body = strip_trace_link(mdx)
    if not url:
        return body
    return (
        f"{body.rstrip()}\n\n"
        f'<Card title="View example trace" icon="chart-line" href="{url}" arrow horizontal>\n'
        f"  {TRACE_CARD_BODY}\n"
        f"</Card>\n"
    )


def looks_like_agent_root(run: Any) -> bool:
    """Return True if a LangSmith run looks like an agent / graph root."""
    name = getattr(run, "name", None) or ""
    if _AGENT_NAME_RE.search(name):
        return True
    return False


def select_agent_root_run(client: Any, runs: list[Any]) -> Any | None:
    """Pick the best agent-like root run from a time window.

    Prefers named agent/LangGraph roots. Falls back to a chain root that has at
    least one LLM child in the same trace.
    """
    scored: list[tuple[int, Any]] = []
    for run in runs:
        name = (getattr(run, "name", None) or "").lower()
        score = 0
        if "langgraph" in name:
            score += 10
        if "deep" in name and "agent" in name:
            score += 10
        if looks_like_agent_root(run):
            score += 8
        if getattr(run, "run_type", None) == "chain":
            score += 1
        if score:
            scored.append((score, run))

    scored.sort(key=lambda item: -item[0])
    if scored:
        return scored[0][1]

    for run in runs:
        if getattr(run, "run_type", None) != "chain":
            continue
        trace_id = getattr(run, "trace_id", None)
        if not trace_id:
            continue
        llm_runs = list(
            client.list_runs(
                trace_id=trace_id,
                run_type="llm",
                limit=1,
            )
        )
        if llm_runs:
            return run
    return None


def wait_for_agent_root_run(
    *,
    client: Any,
    project_name: str,
    start_time: datetime,
    max_attempts: int = 6,
    delay_seconds: float = 2.0,
) -> Any | None:
    """Poll LangSmith for an agent-like root run started at or after start_time."""
    # Small buffer so clock skew / upload delay does not miss the run.
    window_start = start_time - timedelta(seconds=2)
    last_runs: list[Any] = []
    for attempt in range(1, max_attempts + 1):
        client.flush()
        last_runs = list(
            client.list_runs(
                project_name=project_name,
                start_time=window_start,
                is_root=True,
            )
        )
        selected = select_agent_root_run(client, last_runs)
        if selected is not None:
            return selected
        if attempt < max_attempts:
            time.sleep(delay_seconds)
    return None


def share_run_public_url(client: Any, run: Any) -> str:
    """Create or reuse a public share URL for the run's trace."""
    # Prefer the sync helper that returns a full application URL. The v2
    # runs.share.create API is async and returns only a share_token.
    return client.share_run(run.id)


def collect_trace_for_sample(
    *,
    repo_root: Path,
    source_path: Path,
    start_time: datetime,
    project_name: str = DEFAULT_PROJECT,
    client: Any | None = None,
) -> dict[str, Any] | None:
    """Share an agent trace for a single-snippet sample and update the manifest.

    Returns the updated snippet manifest entry, or None when skipped / not found.
    """
    rel_source = source_path.relative_to(repo_root).as_posix()
    text = source_path.read_text(encoding="utf-8")
    snippet_ids = snippet_ids_in_source(text)
    manifest = load_manifest(repo_root)
    manifest["project"] = project_name

    if len(snippet_ids) == 0:
        print(f"  … {rel_source}: no :snippet-start: markers; skip trace link")
        return None

    if len(snippet_ids) > 1:
        manifest["skipped_multi_snippet"][rel_source] = snippet_ids
        # Drop any stale single-snippet entries if this file used to be single.
        for snippet_id in snippet_ids:
            manifest["snippets"].pop(snippet_id, None)
        save_manifest(repo_root, manifest)
        print(
            f"  … {rel_source}: multi-snippet ({len(snippet_ids)}); "
            "skip trace links until split into separate files"
        )
        return None

    snippet_id = snippet_ids[0]
    if client is None:
        from langsmith import Client

        client = Client()

    run = wait_for_agent_root_run(
        client=client,
        project_name=project_name,
        start_time=start_time,
    )
    if run is None:
        print(f"  … {rel_source}: no agent root run found; skip trace link")
        return None

    url = share_run_public_url(client, run)
    entry = {
        "source": rel_source,
        "url": url,
        "run_id": str(run.id),
        "trace_id": str(getattr(run, "trace_id", "") or ""),
        "run_name": getattr(run, "name", None),
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    manifest["snippets"][snippet_id] = entry
    manifest["skipped_multi_snippet"].pop(rel_source, None)
    save_manifest(repo_root, manifest)
    print(f"  … {rel_source}: shared trace for `{snippet_id}`")
    return entry
