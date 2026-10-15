"""Collect public LangSmith trace links for docs code samples.

Used by ``scripts/test_code_samples.py`` when ``CODE_SAMPLE_TRACING=1``, and by
``scripts/generate_code_snippet_mdx.py`` to append a Mintlify Card CTA under
generated snippet MDX.

Only single-snippet source files get links. Multi-snippet files are skipped until
those samples are split into one file per snippet.

Matching is stamp-based: the sample runner sets ``LANGSMITH_DOCS_SNIPPET`` to the
snippet ID so the Python and JS LangSmith SDKs attach it as run metadata. The
collector then requires that metadata value and does not fall back to an
arbitrary LangGraph root in the time window (which previously shuffled links
under parallel ``CODE_SAMPLE_JOBS``).

When a successful sample run has no stamped root (for example a mock-only tool
harness), any previous manifest entry for that snippet is removed so generated
MDX does not keep a stale CTA.
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
# Env var name and metadata key (LangSmith copies non-secret LANGSMITH_* env
# vars onto run metadata for Python and JS SDKs).
DOCS_SNIPPET_ENV = "LANGSMITH_DOCS_SNIPPET"
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
# Snippet IDs appear in LangSmith filter strings; keep the charset conservative.
_SNIPPET_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


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


def primary_snippet_id(source_text: str) -> str | None:
    """Return the sole snippet ID when the source is eligible for a trace link."""
    ids = snippet_ids_in_source(source_text)
    if len(ids) != 1:
        return None
    snippet_id = ids[0]
    if not _SNIPPET_ID_RE.fullmatch(snippet_id):
        return None
    return snippet_id


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


def _run_metadata(run: Any) -> dict[str, Any]:
    """Return metadata from a LangSmith run object or mapping."""
    direct = getattr(run, "metadata", None)
    if isinstance(direct, dict):
        return direct
    extra = getattr(run, "extra", None)
    if isinstance(extra, dict):
        meta = extra.get("metadata")
        if isinstance(meta, dict):
            return meta
    if isinstance(run, dict):
        meta = run.get("metadata")
        if isinstance(meta, dict):
            return meta
        extra = run.get("extra")
        if isinstance(extra, dict):
            nested = extra.get("metadata")
            if isinstance(nested, dict):
                return nested
    return {}


def run_has_docs_snippet(run: Any, snippet_id: str) -> bool:
    """Return True when the run was stamped with the given docs snippet ID."""
    return _run_metadata(run).get(DOCS_SNIPPET_ENV) == snippet_id


def _run_start_time(run: Any) -> datetime | None:
    """Normalize a run's start_time to an aware UTC datetime, if present."""
    value = getattr(run, "start_time", None)
    if value is None and isinstance(run, dict):
        value = run.get("start_time")
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    return None


def select_stamped_root_run(
    runs: list[Any],
    *,
    snippet_id: str,
    sample_start: datetime,
) -> Any | None:
    """Pick the stamped root run closest to the sample start time.

    Requires ``LANGSMITH_DOCS_SNIPPET`` metadata equal to ``snippet_id``. Does not
    fall back to an unstamped LangGraph or agent root.
    """
    if sample_start.tzinfo is None:
        sample_start = sample_start.replace(tzinfo=timezone.utc)
    else:
        sample_start = sample_start.astimezone(timezone.utc)

    stamped: list[tuple[float, datetime, Any]] = []
    for run in runs:
        if not run_has_docs_snippet(run, snippet_id):
            continue
        started = _run_start_time(run)
        if started is None:
            # Prefer timed matches; keep untimed stamped runs as a last resort.
            stamped.append((float("inf"), sample_start, run))
            continue
        delta = abs((started - sample_start).total_seconds())
        stamped.append((delta, started, run))

    if not stamped:
        return None
    stamped.sort(key=lambda item: (item[0], item[1]))
    return stamped[0][2]


def docs_snippet_filter(snippet_id: str) -> str:
    """Return a LangSmith ``list_runs`` filter for the docs snippet stamp."""
    if not _SNIPPET_ID_RE.fullmatch(snippet_id):
        raise ValueError(f"unsafe snippet id for filter: {snippet_id!r}")
    return (
        f'and(eq(metadata_key, "{DOCS_SNIPPET_ENV}"), '
        f'eq(metadata_value, "{snippet_id}"))'
    )


def wait_for_agent_root_run(
    *,
    client: Any,
    project_name: str,
    snippet_id: str,
    start_time: datetime,
    end_time: datetime | None = None,
    exclude_ids: set[str] | None = None,
    max_attempts: int = 6,
    delay_seconds: float = 2.0,
) -> Any | None:
    """Poll LangSmith for the root run stamped with ``snippet_id``.

    When ``end_time`` is set, ignore roots that started after the sample finished
    (plus a small upload buffer). When ``exclude_ids`` is set, ignore runs already
    claimed by another sample—needed when samples run in parallel against one
    project.

    Matching requires the ``LANGSMITH_DOCS_SNIPPET`` metadata stamp. There is no
    fallback to an arbitrary agent-like root in the time window.
    """
    # Small buffer so clock skew / upload delay does not miss the run.
    window_start = start_time - timedelta(seconds=2)
    window_end = (
        end_time + timedelta(seconds=15) if end_time is not None else None
    )
    excluded = exclude_ids or set()
    run_filter = docs_snippet_filter(snippet_id)
    for attempt in range(1, max_attempts + 1):
        client.flush()
        last_runs = list(
            client.list_runs(
                project_name=project_name,
                start_time=window_start,
                is_root=True,
                filter=run_filter,
            )
        )
        candidates: list[Any] = []
        for run in last_runs:
            run_id = str(getattr(run, "id", "") or "")
            if run_id and run_id in excluded:
                continue
            # Defense in depth: never trust filter alone.
            if not run_has_docs_snippet(run, snippet_id):
                continue
            run_started = _run_start_time(run)
            if (
                window_end is not None
                and run_started is not None
                and run_started > window_end
            ):
                continue
            candidates.append(run)
        selected = select_stamped_root_run(
            candidates,
            snippet_id=snippet_id,
            sample_start=start_time,
        )
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
    end_time: datetime | None = None,
    exclude_ids: set[str] | None = None,
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

    snippet_id = primary_snippet_id(text)
    if snippet_id is None:
        print(
            f"  … {rel_source}: snippet id {snippet_ids[0]!r} is not safe "
            "for trace stamping; skip trace link"
        )
        return None

    if client is None:
        from langsmith import Client

        client = Client()

    run = wait_for_agent_root_run(
        client=client,
        project_name=project_name,
        snippet_id=snippet_id,
        start_time=start_time,
        end_time=end_time,
        exclude_ids=exclude_ids,
    )
    if run is None:
        # Fail closed: drop any prior link. Keeping an unstamped/shuffled
        # leftover after a successful sample run is worse than omitting the CTA
        # (common for mock-only harnesses that never create a root run).
        if snippet_id in manifest["snippets"]:
            manifest["snippets"].pop(snippet_id, None)
            save_manifest(repo_root, manifest)
            print(
                f"  … {rel_source}: no root run stamped with "
                f"{DOCS_SNIPPET_ENV}={snippet_id}; cleared stale trace link"
            )
        else:
            print(
                f"  … {rel_source}: no root run stamped with "
                f"{DOCS_SNIPPET_ENV}={snippet_id}; skip trace link"
            )
        return None

    url = share_run_public_url(client, run)
    entry = {
        "source": rel_source,
        "url": url,
        "run_id": str(run.id),
        "trace_id": str(getattr(run, "trace_id", "") or ""),
        "run_name": getattr(run, "name", None),
        "docs_snippet": snippet_id,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    manifest["snippets"][snippet_id] = entry
    manifest["skipped_multi_snippet"].pop(rel_source, None)
    save_manifest(repo_root, manifest)
    print(f"  … {rel_source}: shared trace for `{snippet_id}`")
    return entry
