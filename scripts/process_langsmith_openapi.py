#!/usr/bin/env python3
"""Post-process the LangSmith OpenAPI spec for public documentation.

Adds ``x-hidden: true`` to fleet and internal endpoints so Mintlify skips them,
and injects ``x-group`` on tags so auto-generated pages are grouped under
human-readable headings.

Usage
-----
Fetch the live spec from api.smith.langchain.com and write to src/::

    python scripts/process_langsmith_openapi.py --write

Read from a local file instead::

    python scripts/process_langsmith_openapi.py --input /path/to/openapi.json --write

Preview to stdout (dry run)::

    python scripts/process_langsmith_openapi.py --input /path/to/openapi.json
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "src" / "langsmith" / "langsmith-platform-openapi.json"

# Only these hosts are allowed when fetching a spec over the network.
ALLOWED_HOSTS = {
    "api.smith.langchain.com",
}
DEFAULT_URL = "https://api.smith.langchain.com/openapi.json"
FETCH_TIMEOUT_SECONDS = 30

# Tags whose operations should be hidden from the public docs.
HIDDEN_TAGS: set[str] = {
    # Fleet
    "agents",
    "fleet auth",
    "fleet credentials",
    "fleet github-app",
    "fleet integrations",
    "fleet mcp",
    "fleet threads",
    "fleet trigger-templates",
    "fleet triggers",
    "fleet usage",
    "fleet_webhooks",
    "skills",
    # Internal / infra
    "beacon",
    "nps",
    "sandboxes-internal",
    "internal",
    "admin-panel",
    "provisioning",
    "debug",
    # Low-value system endpoints
    "metrics",
    # Untagged health checks are caught by HIDDEN_PATHS below.
}

# Exact paths that should always be hidden (health checks, etc.).
HIDDEN_PATHS: set[str] = {
    "/api/v1/ok",
    "/ok",
}

# Path prefixes that should always be hidden regardless of tag.
HIDDEN_PATH_PREFIXES: list[str] = [
    "/v1/fleet/",
    "/v1/platform/fleet/",
    "/v1/platform/fleet-webhooks/",
    "/v1/beacon/",
    "/v1/platform/nps/",
    "/v2/sandboxes/internal/",
]

# v2 API endpoints (paths under ``/v2/``) carry their backend resource tag
# (runs, datasets, threads), so they group with their v1 siblings automatically.
# Append a "(v2)" marker to their titles so the two versions are distinguishable
# in the sidebar. Sandboxes are a v2-only feature with no v1 counterpart, so they
# are excluded from the marker.
V2_PATH_PREFIX = "/v2/"
V2_LABEL_SUFFIX = " (v2)"
V2_LABEL_EXCLUDE_PREFIXES: list[str] = [
    "/v2/sandboxes/",
]

# Map raw tag names to human-readable group headings (``x-group``).
# Tags not listed here keep their original name as the group heading.
TAG_GROUPS: dict[str, str] = {
    # Tracing
    "run": "Tracing",
    "runs": "Tracing",
    "tracer-sessions": "Tracing",
    "sessions": "Tracing",
    # Datasets
    "datasets": "Datasets",
    "examples": "Datasets",
    # Evaluation
    "experiments": "Evaluation",
    "evaluators": "Evaluation",
    "experiment-view-overrides": "Evaluation",
    # Feedback & annotation
    "feedback": "Feedback & Annotation",
    "feedback-configs": "Feedback & Annotation",
    "annotation-queues": "Feedback & Annotation",
    "annotation_queues": "Feedback & Annotation",
    # Prompts & playground
    "prompts": "Prompts & Playground",
    "prompt-webhooks": "Prompts & Playground",
    "playground-settings": "Prompts & Playground",
    "commits": "Prompts & Playground",
    "directories": "Prompts & Playground",
    "hub_environments": "Prompts & Playground",
    "tag-transitions": "Prompts & Playground",
    # Prompt hub
    "repos": "Prompt Hub",
    "comments": "Prompt Hub",
    "likes": "Prompt Hub",
    "tags": "Prompt Hub",
    "ownerships": "Prompt Hub",
    "settings": "Prompt Hub",
    "optimization-jobs": "Prompt Hub",
    # Monitoring
    "charts": "Monitoring",
    "alert_rules": "Monitoring",
    "bulk-exports": "Monitoring",
    # Sandboxes
    "sandboxes": "Sandboxes",
    "checkpoint": "Sandboxes",
    "execute": "Sandboxes",
    # Administration
    "Organizations": "Administration",
    "orgs": "Administration",
    "workspaces": "Administration",
    "tenant": "Administration",
    "api-key": "Administration",
    "auth": "Administration",
    "me": "Administration",
    "service-accounts": "Administration",
    "SCIM Tokens": "Administration",
    "TTL Settings": "Administration",
    "ttl-settings": "Administration",
    "access_policies": "Administration",
    "audit-logs": "Administration",
    "usage-limits": "Administration",
    "data_planes": "Administration",
    "aws_marketplace": "Administration",
    # LLM Gateway
    "gateway-policies": "LLM Gateway",
    # Integrations & tools
    "integrations": "Integrations & Tools",
    "tools": "Integrations & Tools",
    "mcp_vendors": "Integrations & Tools",
    "mcp": "Integrations & Tools",
    "oauth": "Integrations & Tools",
    # Issues
    "issues": "Issues",
    "issues-agent": "Issues",
    # Files
    "files": "Files",
    # System
    "info": "System",
    "features": "System",
    "model-price-map": "System",
    "public": "System",
    "ace": "System",
    "backfills": "System",
    # Threads
    "threads": "Threads",
}

# Display order for groups in the generated docs sidebar.
# Groups not listed here are appended alphabetically after the listed ones.
GROUP_ORDER: list[str] = [
    "Tracing",
    "Threads",
    "Datasets",
    "Evaluation",
    "Feedback & Annotation",
    "Monitoring",
    "Prompts & Playground",
    "Prompt Hub",
    "Integrations & Tools",
    "LLM Gateway",
    "Sandboxes",
    "Issues",
    "Administration",
    "Files",
    "System",
]


# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------


def _should_hide_by_path(path: str) -> bool:
    """Return True if the path matches a hidden prefix or exact path."""
    return (
        path in HIDDEN_PATHS
        or any(path.startswith(prefix) for prefix in HIDDEN_PATH_PREFIXES)
    )


def _should_hide_by_tags(tags: list[str]) -> bool:
    """Return True if any of the operation's tags are in the hidden set."""
    return any(tag in HIDDEN_TAGS for tag in tags)


_BETA_PREFIX_RE = re.compile(r"^\[Beta\]\s*(.+)$")
_TRAILING_V2_RE = re.compile(r"^(.*\S)\s+V2$")


def _normalize_summary(summary: str) -> str:
    """Rewrite inline markers to a trailing suffix.

    ``"[Beta] X"`` becomes ``"X (Beta)"`` and ``"X V2"`` becomes ``"X (v2)"`` so
    version and release-stage markers read consistently across the reference.
    """
    beta = _BETA_PREFIX_RE.match(summary)
    if beta:
        summary = f"{beta.group(1).rstrip()} (Beta)"
    trailing = _TRAILING_V2_RE.match(summary)
    if trailing:
        summary = f"{trailing.group(1)} (v2)"
    return summary


def process_spec(spec: dict) -> dict:
    """Add ``x-hidden`` and ``x-group`` annotations to *spec* in place."""
    hidden_count = 0
    total_count = 0

    # 1. Mark operations as hidden.
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            # Skip OpenAPI metadata keys like "parameters", "summary" at path level.
            if method in ("parameters", "summary", "description", "servers"):
                continue
            total_count += 1
            tags = operation.get("tags", [])
            if _should_hide_by_path(path) or _should_hide_by_tags(tags):
                operation["x-hidden"] = True
                hidden_count += 1

    # 1b. Standardize endpoint titles: normalize inline markers to a trailing
    # suffix (see _normalize_summary), and append a "(v2)" marker to visible
    # non-sandbox /v2/ operations so they are distinguishable from their v1
    # siblings. Idempotent on re-runs.
    v2_count = 0
    marker = V2_LABEL_SUFFIX.strip()
    for path, methods in spec.get("paths", {}).items():
        is_v2 = path.startswith(V2_PATH_PREFIX) and not any(
            path.startswith(p) for p in V2_LABEL_EXCLUDE_PREFIXES
        )
        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            if method in ("parameters", "summary", "description", "servers"):
                continue
            summary = _normalize_summary((operation.get("summary") or "").strip())
            if is_v2 and not operation.get("x-hidden"):
                if not summary:
                    summary = f"{method.upper()} {path}"
                if not summary.endswith(marker):
                    summary = f"{summary}{V2_LABEL_SUFFIX}"
                v2_count += 1
            if summary:
                operation["summary"] = summary

    # 1c. Place each v2 endpoint that has a direct v1 counterpart immediately
    # after it, sharing the v1 tag, so the two versions sit together in the
    # sidebar. Only /v2/ paths with a matching "/api/v1/..." path are paired;
    # the rest stay grouped by their own resource tag.
    paths = spec.get("paths", {})
    v2_after_v1: dict[str, str] = {}
    for path in paths:
        if not path.startswith(V2_PATH_PREFIX):
            continue
        if any(path.startswith(p) for p in V2_LABEL_EXCLUDE_PREFIXES):
            continue
        v1_path = "/api/v1" + path[len("/v2"):]
        if v1_path not in paths:
            continue
        v2_after_v1[v1_path] = path
        v1_tags = next(
            (
                op["tags"]
                for op in paths[v1_path].values()
                if isinstance(op, dict) and op.get("tags")
            ),
            None,
        )
        if v1_tags:
            for op in paths[path].values():
                if isinstance(op, dict) and "tags" in op:
                    op["tags"] = list(v1_tags)

    if v2_after_v1:
        v2_targets = set(v2_after_v1.values())
        reordered: dict = {}
        for p, methods in paths.items():
            if p in v2_targets:
                continue
            reordered[p] = methods
            if p in v2_after_v1:
                vp = v2_after_v1[p]
                reordered[vp] = paths[vp]
        spec["paths"] = reordered

    # 2. Ensure top-level tags array exists and add x-group.
    if "tags" not in spec:
        spec["tags"] = []
    existing_names = {t["name"] for t in spec["tags"]}

    # Update existing tag objects.
    for tag_obj in spec["tags"]:
        name = tag_obj["name"]
        if name in TAG_GROUPS:
            tag_obj["x-group"] = TAG_GROUPS[name]
        # Also hide top-level tag entries for hidden tags.
        if name in HIDDEN_TAGS:
            tag_obj["x-hidden"] = True

    # Add tag objects for tags that appear only on operations.
    seen_on_operations: set[str] = set()
    for _path, methods in spec.get("paths", {}).items():
        for _method, operation in methods.items():
            if isinstance(operation, dict):
                for tag in operation.get("tags", []):
                    seen_on_operations.add(tag)

    for tag_name in sorted(seen_on_operations - existing_names):
        entry: dict = {"name": tag_name}
        if tag_name in TAG_GROUPS:
            entry["x-group"] = TAG_GROUPS[tag_name]
        if tag_name in HIDDEN_TAGS:
            entry["x-hidden"] = True
        spec["tags"].append(entry)

    # 3. Sort tags so groups appear in GROUP_ORDER.
    group_rank = {g: i for i, g in enumerate(GROUP_ORDER)}
    fallback = len(GROUP_ORDER)

    def _tag_sort_key(tag_obj: dict) -> tuple:
        group = tag_obj.get("x-group", tag_obj["name"])
        return (group_rank.get(group, fallback), group, tag_obj["name"])

    spec["tags"] = sorted(spec["tags"], key=_tag_sort_key)

    print(
        f"Processed {total_count} operations: "
        f"{hidden_count} hidden, {total_count - hidden_count} public "
        f"({v2_count} labeled '(v2)')",
        file=sys.stderr,
    )

    return spec


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def fetch_spec(url: str) -> dict:
    """Fetch an OpenAPI JSON spec from *url*."""
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(
            f"Host {parsed.hostname!r} is not in the allow-list: {ALLOWED_HOSTS}"
        )
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS, context=ctx) as resp:
        return json.loads(resp.read())


def load_spec(path: str) -> dict:
    """Load an OpenAPI JSON spec from a local file."""
    resolved = Path(path).resolve()
    return json.loads(resolved.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post-process the LangSmith OpenAPI spec for public docs."
    )
    parser.add_argument(
        "--input",
        help=(
            "Path to a local OpenAPI JSON file. "
            f"If omitted, fetches from {DEFAULT_URL}."
        ),
    )
    parser.add_argument(
        "--output",
        help=f"Output path (default: {OUTPUT_PATH.relative_to(REPO_ROOT)})",
        default=str(OUTPUT_PATH),
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write to output file. Without this flag, prints to stdout.",
    )
    args = parser.parse_args()

    # Load.
    if args.input:
        print(f"Loading spec from {args.input}", file=sys.stderr)
        spec = load_spec(args.input)
    else:
        print(f"Fetching spec from {DEFAULT_URL}", file=sys.stderr)
        spec = fetch_spec(DEFAULT_URL)

    # Process.
    result = process_spec(spec)
    output_json = json.dumps(result, indent=2, ensure_ascii=False) + "\n"

    # Write.
    if args.write:
        out = Path(args.output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output_json, encoding="utf-8")
        print(f"Wrote {len(output_json):,} bytes to {out}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
