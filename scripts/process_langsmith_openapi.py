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
    "/v1/beacon/",
    "/v1/platform/nps/",
    "/v2/sandboxes/internal/",
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
    # Fleet
    "agents": "Fleet",
    "skills": "Fleet",
    "fleet auth": "Fleet",
    "fleet credentials": "Fleet",
    "fleet github-app": "Fleet",
    "fleet integrations": "Fleet",
    "fleet mcp": "Fleet",
    "fleet threads": "Fleet",
    "fleet trigger-templates": "Fleet",
    "fleet triggers": "Fleet",
    "fleet usage": "Fleet",
    "fleet_webhooks": "Fleet",
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
    "threads": "System",
}

# Display order for groups in the generated docs sidebar.
# Groups not listed here are appended alphabetically after the listed ones.
GROUP_ORDER: list[str] = [
    "Tracing",
    "Datasets",
    "Evaluation",
    "Feedback & Annotation",
    "Monitoring",
    "Prompts & Playground",
    "Prompt Hub",
    "Integrations & Tools",
    "LLM Gateway",
    "Sandboxes",
    "Fleet",
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
        f"{hidden_count} hidden, {total_count - hidden_count} public",
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
