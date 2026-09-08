#!/usr/bin/env python3
"""Flag external integrations that may warrant hosted docs.

Reads scripts/data/integration_external_docs.yaml, fetches current monthly
download counts, and creates Linear issues for any entry at or above
50,000 downloads/month (override with --threshold).

Component curation bars (chat, tools, sandboxes, retrievers, embeddings,
vectorstores, and document_loaders: 50k) are included in the issue for
context.

Skips creating a duplicate when an open Linear issue already matches the
stable title for that integration.

Usage (from repo root):

    # Dry-run (no Linear calls):
    uv run python scripts/flag_hosted_docs_candidates.py

    # Create Linear issues (requires LINEAR_API_KEY and LINEAR_TEAM_KEY):
    uv run python scripts/flag_hosted_docs_candidates.py --create

    uv run python scripts/flag_hosted_docs_candidates.py --create --threshold 50000
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import requests
import yaml

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
_EXTERNAL_DOCS_PATH = _SCRIPT_DIR / "data" / "integration_external_docs.yaml"

# Linear early-warning threshold for external integrations.
FLAG_THRESHOLD = 50_000

# Component curation bars for hosted guides (used in issue context).
COMPONENT_CURATION_BARS = {
    "chat": 50_000,
    "tools": 50_000,
    "sandboxes": 50_000,
    "retrievers": 50_000,
    "embeddings": 50_000,
    "vectorstores": 50_000,
    "document_loaders": 50_000,
}

_LINEAR_URL = "https://api.linear.app/graphql"
_HTTP_HEADERS = {"User-Agent": "langchain-docs-hosted-docs-flag/1.0"}
_REQUEST_TIMEOUT = 20

# Import download helpers from the refresh script (same package dir).
sys.path.insert(0, str(_SCRIPT_DIR))
import refresh_integration_downloads as rid  # noqa: E402


@dataclass(frozen=True)
class Candidate:
    language: str
    component: str
    name: str
    package: str
    registry: str
    docs_url: str
    downloads: int
    curation_bar: int

    @property
    def issue_title(self) -> str:
        return (
            f"Consider hosting {self.component} docs for {self.name} "
            f"({self.downloads:,}/mo)"
        )

    @property
    def search_term(self) -> str:
        # Stable fragment for dedupe across changing download counts.
        return f"Consider hosting {self.component} docs for {self.name}"

    @property
    def meets_curation_bar(self) -> bool:
        return self.downloads >= self.curation_bar


def _load_external_entries() -> list[tuple[str, str, dict[str, Any]]]:
    if not _EXTERNAL_DOCS_PATH.is_file():
        return []
    data = yaml.safe_load(_EXTERNAL_DOCS_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return []
    entries: list[tuple[str, str, dict[str, Any]]] = []
    for language, components in data.items():
        if not isinstance(components, dict):
            continue
        for component, items in components.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    entries.append((str(language), str(component), item))
    return entries


def _package_and_registry(
    language: str, item: dict[str, Any]
) -> tuple[Optional[str], Optional[str]]:
    if language == "javascript":
        npm = item.get("npm")
        if isinstance(npm, str) and npm.strip() and not npm.strip().startswith("-"):
            return npm.strip(), "npm"
    pypi = item.get("pypi")
    if isinstance(pypi, str) and pypi.strip() and not pypi.strip().startswith("-"):
        return pypi.strip(), "pypi"
    return None, None


def collect_candidates(threshold: int | None = None) -> list[Candidate]:
    package_cache: dict[tuple[str, str], int] = {}
    candidates: list[Candidate] = []
    flag_threshold = FLAG_THRESHOLD if threshold is None else threshold

    for language, component, item in _load_external_entries():
        name = item.get("name")
        docs_url = item.get("docs_url")
        if not isinstance(name, str) or not name.strip():
            continue
        if not isinstance(docs_url, str) or not docs_url.strip():
            continue
        package, registry = _package_and_registry(language, item)
        if not package or not registry:
            continue

        curation_bar = COMPONENT_CURATION_BARS.get(component, FLAG_THRESHOLD)

        cache_key = (registry, package)
        if cache_key not in package_cache:
            try:
                if registry == "npm":
                    package_cache[cache_key] = rid.fetch_npm_downloads(package)
                else:
                    package_cache[cache_key] = rid.fetch_pypi_downloads(package)
                print(f"{registry}:{package} -> {package_cache[cache_key]}")
                time.sleep(0.15)
            except (requests.RequestException, ValueError, KeyError) as exc:
                print(
                    f"warn: failed to fetch {registry} downloads for {package}: {exc}",
                    file=sys.stderr,
                )
                continue

        downloads = package_cache[cache_key]
        if downloads < flag_threshold:
            continue
        candidates.append(
            Candidate(
                language=language,
                component=component,
                name=name.strip(),
                package=package,
                registry=registry,
                docs_url=docs_url.strip(),
                downloads=downloads,
                curation_bar=curation_bar,
            )
        )

    candidates.sort(key=lambda c: (-c.downloads, c.name.lower()))
    return candidates


def _linear_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": api_key,
        "Content-Type": "application/json",
        **_HTTP_HEADERS,
    }


def _linear_graphql(api_key: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        _LINEAR_URL,
        headers=_linear_headers(api_key),
        json={"query": query, "variables": variables},
        timeout=_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(f"Linear GraphQL errors: {payload['errors']}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected Linear response: {payload}")
    return data


def resolve_team_id(api_key: str, team_key: str) -> str:
    data = _linear_graphql(
        api_key,
        """
        query TeamByKey($key: String!) {
          teams(filter: { key: { eq: $key } }, first: 1) {
            nodes { id key name }
          }
        }
        """,
        {"key": team_key},
    )
    nodes = data.get("teams", {}).get("nodes") or []
    if not nodes:
        raise RuntimeError(f"No Linear team found for key {team_key!r}")
    return str(nodes[0]["id"])


def find_open_issue(api_key: str, search_term: str) -> Optional[dict[str, Any]]:
    data = _linear_graphql(
        api_key,
        """
        query SearchIssues($term: String!) {
          searchIssues(term: $term, first: 25, includeArchived: false) {
            nodes {
              id
              identifier
              title
              url
              state { name type }
            }
          }
        }
        """,
        {"term": search_term},
    )
    nodes = data.get("searchIssues", {}).get("nodes") or []
    for node in nodes:
        title = str(node.get("title") or "")
        state = node.get("state") or {}
        state_type = str(state.get("type") or "")
        if search_term not in title:
            continue
        # completed / canceled are done; anything else counts as open.
        if state_type in {"completed", "canceled"}:
            continue
        return node
    return None


def create_issue(api_key: str, team_id: str, candidate: Candidate) -> dict[str, Any]:
    bar_note = (
        f"This package is at or above the `{candidate.component}` curation bar "
        f"({candidate.curation_bar:,}/mo)."
        if candidate.meets_curation_bar
        else (
            f"This package crossed the {FLAG_THRESHOLD:,}/mo early-warning threshold. "
            f"The `{candidate.component}` curation bar for hosting docs is "
            f"{candidate.curation_bar:,}/mo."
        )
    )
    description = f"""External integration crossed the {FLAG_THRESHOLD:,}/mo download flag threshold.

**Integration:** `{candidate.name}`
**Component:** `{candidate.component}` ({candidate.language})
**Package:** `{candidate.package}` ({candidate.registry})
**Monthly downloads:** {candidate.downloads:,}
**Component curation bar:** {candidate.curation_bar:,}/mo
**Current docs:** {candidate.docs_url}

{bar_note}

## Suggested action

Consider adding a hosted guide under `src/oss/{candidate.language}/integrations/{candidate.component}/` and removing this entry from `scripts/data/integration_external_docs.yaml` when it meets the component curation bar (or an explicit featured allowlist).

Filed by `scripts/flag_hosted_docs_candidates.py` during the weekly package-downloads workflow.
"""
    data = _linear_graphql(
        api_key,
        """
        mutation CreateIssue($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue { id identifier title url }
          }
        }
        """,
        {
            "input": {
                "teamId": team_id,
                "title": candidate.issue_title,
                "description": description,
            }
        },
    )
    result = data.get("issueCreate") or {}
    if not result.get("success") or not result.get("issue"):
        raise RuntimeError(f"Failed to create Linear issue: {data}")
    return result["issue"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--threshold",
        type=int,
        default=None,
        help=(
            "Override the Linear flag threshold for all components "
            f"(default: {FLAG_THRESHOLD:,}/mo)"
        ),
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create Linear issues for candidates (default: dry-run print only)",
    )
    args = parser.parse_args()

    candidates = collect_candidates(args.threshold)
    if not candidates:
        threshold = FLAG_THRESHOLD if args.threshold is None else args.threshold
        print(f"No external integrations at or above {threshold:,} downloads/month.")
        return 0

    print(f"Found {len(candidates)} candidate(s) (>= {FLAG_THRESHOLD if args.threshold is None else args.threshold:,}/mo):")
    for candidate in candidates:
        bar_mark = "meets curation bar" if candidate.meets_curation_bar else (
            f"below {candidate.component} bar {candidate.curation_bar:,}"
        )
        print(
            f"  - {candidate.language}/{candidate.component} "
            f"{candidate.name}: {candidate.downloads:,} ({bar_mark}) "
            f"({candidate.docs_url})"
        )

    if not args.create:
        print("Dry-run only. Re-run with --create to file Linear issues.")
        return 0

    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    team_key = os.environ.get("LINEAR_TEAM_KEY", "").strip()
    if not api_key or not team_key:
        print(
            "error: LINEAR_API_KEY and LINEAR_TEAM_KEY are required with --create",
            file=sys.stderr,
        )
        return 1

    team_id = resolve_team_id(api_key, team_key)
    created = 0
    skipped = 0
    for candidate in candidates:
        existing = find_open_issue(api_key, candidate.search_term)
        if existing:
            print(
                f"skip: open issue already exists for {candidate.name}: "
                f"{existing.get('identifier')} {existing.get('url')}"
            )
            skipped += 1
            continue
        issue = create_issue(api_key, team_id, candidate)
        print(
            f"created: {issue.get('identifier')} {issue.get('url')} "
            f"({candidate.name})"
        )
        created += 1
        time.sleep(0.2)

    print(f"Done. created={created} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
