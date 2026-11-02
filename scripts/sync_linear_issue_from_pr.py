#!/usr/bin/env python3
"""Sync Linear DOC issue status from a GitHub pull request lifecycle event.

Used by `.github/workflows/sync-linear-issue-from-pr.yml` for PRs opened by
docs-release-watch (and any other PR that links a DOC issue the same way).

Status mapping (resolved against the issue's team workflow states):

| PR condition              | Preferred state name | Linear type fallback |
|---------------------------|----------------------|----------------------|
| Open, draft               | In Progress          | started              |
| Open, ready for review    | In Review            | started              |
| Merged                    | Done                 | completed            |
| Closed without merge      | Canceled             | canceled             |

Usage (CI):

    export PR_TITLE=... PR_BODY=... PR_STATE=open PR_DRAFT=true PR_MERGED=false
    uv run python scripts/sync_linear_issue_from_pr.py

Title and body are read from ``PR_TITLE`` / ``PR_BODY`` by default so large
PR descriptions do not need to be passed on the argv. Requires
``LINEAR_API_KEY``. Exits 0 when there is nothing to update.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_LINEAR_URL = "https://api.linear.app/graphql"
_HTTP_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "langchain-docs-sync-linear-from-pr/1.0",
}
_REQUEST_TIMEOUT = 30

# Canonical link form in the PR ## Linear section:
#   Closes [DOC-1787](https://linear.app/.../issue/DOC-1787/...)
# Also accept plain "Closes DOC-1787" next to a Linear URL.
_CLOSES_LINK_RE = re.compile(
    r"\bCloses\s+\[(DOC-\d+)\]\((https?://linear\.app/[^\s)\]]+/issue/DOC-\d+[^\s)\]]*)\)",
    re.IGNORECASE,
)
_CLOSES_PLAIN_RE = re.compile(r"\bCloses\s+(DOC-\d+)\b", re.IGNORECASE)
_LINEAR_URL_RE = re.compile(
    r"https?://linear\.app/[^\s)\]]+/issue/(DOC-\d+)",
    re.IGNORECASE,
)

# Preferred names first; type is the portable fallback within the team.
_TARGET_BY_EVENT: dict[str, tuple[tuple[str, ...], str]] = {
    "draft": (("In Progress", "In progress"), "started"),
    "ready": (("In Review", "In review", "Review"), "started"),
    "merged": (("Done",), "completed"),
    "closed": (("Canceled", "Cancelled"), "canceled"),
}


@dataclass(frozen=True)
class PrStatus:
    """Normalized PR lifecycle used for Linear state selection."""

    event: str  # draft | ready | merged | closed

    @classmethod
    def from_github(
        cls,
        *,
        state: str,
        draft: bool,
        merged: bool,
    ) -> "PrStatus":
        normalized = (state or "").strip().lower()
        if normalized == "closed":
            return cls("merged" if merged else "closed")
        if draft:
            return cls("draft")
        return cls("ready")


def looks_like_linear_linked_pr(*texts: str) -> bool:
    """True when the PR uses the Closes DOC-N Linear link convention."""
    for text in texts:
        if not text:
            continue
        if _CLOSES_LINK_RE.search(text) or _CLOSES_PLAIN_RE.search(text):
            return True
    return False


def extract_doc_issue_identifiers(*texts: str) -> list[str]:
    """Return unique DOC-N identifiers from ``Closes DOC-N`` / linked forms."""
    found: list[str] = []
    seen: set[str] = set()

    def _add(ident: str) -> None:
        normalized = ident.upper()
        if not re.fullmatch(r"DOC-\d+", normalized):
            return
        if normalized not in seen:
            seen.add(normalized)
            found.append(normalized)

    for text in texts:
        if not text:
            continue
        for match in _CLOSES_LINK_RE.finditer(text):
            _add(match.group(1))
        for match in _CLOSES_PLAIN_RE.finditer(text):
            _add(match.group(1))
        # Fallback: Linear issue URL only when a Closes line is already present.
        if _CLOSES_LINK_RE.search(text) or _CLOSES_PLAIN_RE.search(text):
            for match in _LINEAR_URL_RE.finditer(text):
                _add(match.group(1))
    return found


def select_target_state(
    states: list[dict[str, Any]],
    event: str,
) -> Optional[dict[str, Any]]:
    """Pick a workflow state for ``event`` from the team's state list."""
    preferred_names, type_fallback = _TARGET_BY_EVENT[event]
    by_name = {
        str(state.get("name") or "").strip().lower(): state for state in states
    }
    for name in preferred_names:
        hit = by_name.get(name.lower())
        if hit and hit.get("id"):
            return hit
    for state in states:
        if str(state.get("type") or "") == type_fallback and state.get("id"):
            return state
    return None


def _normalize_api_key(raw: str) -> str:
    key = raw.strip().strip('"').strip("'")
    if key.lower().startswith("bearer "):
        return key
    return key


def _linear_graphql(
    api_key: str, query: str, variables: dict[str, Any] | None = None
) -> dict[str, Any]:
    payload = json.dumps(
        {"query": query, "variables": variables or {}}
    ).encode("utf-8")
    request = Request(
        _LINEAR_URL,
        data=payload,
        headers={
            **_HTTP_HEADERS,
            "Authorization": _normalize_api_key(api_key),
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=_REQUEST_TIMEOUT) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Linear HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Linear request failed: {exc.reason}") from exc

    parsed = json.loads(body)
    if parsed.get("errors"):
        raise RuntimeError(f"Linear GraphQL error: {parsed['errors']}")
    data = parsed.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected Linear response shape: {type(data)}")
    return data


def fetch_issue(api_key: str, identifier: str) -> dict[str, Any]:
    if not re.fullmatch(r"DOC-\d+", identifier):
        raise ValueError(f"Invalid Linear identifier: {identifier!r}")
    data = _linear_graphql(
        api_key,
        """
        query IssueById($id: String!) {
          issue(id: $id) {
            id
            identifier
            title
            url
            state { id name type }
            team {
              id
              key
              states { nodes { id name type } }
            }
          }
        }
        """,
        {"id": identifier},
    )
    issue = data.get("issue")
    if not isinstance(issue, dict) or not issue.get("id"):
        raise RuntimeError(f"Linear issue {identifier} was not found.")
    return issue


def update_issue_state(
    api_key: str, issue_id: str, state_id: str
) -> dict[str, Any]:
    data = _linear_graphql(
        api_key,
        """
        mutation IssueUpdate($id: String!, $stateId: String!) {
          issueUpdate(id: $id, input: { stateId: $stateId }) {
            success
            issue {
              id
              identifier
              url
              state { id name type }
            }
          }
        }
        """,
        {"id": issue_id, "stateId": state_id},
    )
    result = data.get("issueUpdate") or {}
    if not result.get("success") or not result.get("issue"):
        raise RuntimeError(f"Linear issueUpdate failed: {result}")
    return result["issue"]


def sync_identifiers(
    api_key: str,
    identifiers: list[str],
    status: PrStatus,
    *,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Update each identifier to the state for ``status``. Return result rows."""
    rows: list[dict[str, Any]] = []
    for identifier in identifiers:
        issue = fetch_issue(api_key, identifier)
        team = issue.get("team") or {}
        states = (team.get("states") or {}).get("nodes") or []
        target = select_target_state(states, status.event)
        current = issue.get("state") or {}
        row: dict[str, Any] = {
            "identifier": issue.get("identifier") or identifier,
            "issue_url": issue.get("url"),
            "event": status.event,
            "current_state": current.get("name"),
            "target_state": target.get("name") if target else None,
            "updated": False,
            "skipped_reason": None,
        }
        if target is None:
            row["skipped_reason"] = (
                f"No workflow state for event {status.event!r} "
                f"on team {team.get('key')!r}"
            )
            rows.append(row)
            continue
        if current.get("id") == target.get("id"):
            row["skipped_reason"] = "already in target state"
            rows.append(row)
            continue
        if dry_run:
            row["skipped_reason"] = "dry-run"
            rows.append(row)
            continue
        updated = update_issue_state(
            api_key, str(issue["id"]), str(target["id"])
        )
        row["updated"] = True
        row["current_state"] = (updated.get("state") or {}).get("name")
        rows.append(row)
    return rows


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Pull request title (default: env PR_TITLE)",
    )
    parser.add_argument(
        "--body",
        default=None,
        help="Pull request body (default: env PR_BODY)",
    )
    parser.add_argument(
        "--state",
        default=None,
        choices=("open", "closed"),
        help="GitHub pull request state (default: env PR_STATE or open)",
    )
    parser.add_argument(
        "--draft",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Whether the PR is a draft (default: env PR_DRAFT)",
    )
    parser.add_argument(
        "--merged",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Whether the closed PR was merged (default: env PR_MERGED)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve targets without calling issueUpdate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable results",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    title = args.title if args.title is not None else os.environ.get("PR_TITLE", "")
    body = args.body if args.body is not None else os.environ.get("PR_BODY", "")
    state = (
        args.state
        if args.state is not None
        else os.environ.get("PR_STATE", "open").strip().lower() or "open"
    )
    if state not in {"open", "closed"}:
        print(f"error: invalid PR state {state!r}", file=sys.stderr)
        return 1
    draft = args.draft if args.draft is not None else _env_bool("PR_DRAFT")
    merged = args.merged if args.merged is not None else _env_bool("PR_MERGED")

    if not looks_like_linear_linked_pr(title, body):
        message = (
            "PR is not Linear-linked (need Closes DOC-N or "
            "Closes [DOC-N](<linear url>)); skipping."
        )
        if args.json:
            print(json.dumps({"skipped": True, "reason": message}))
        else:
            print(message)
        return 0

    identifiers = extract_doc_issue_identifiers(title, body)
    if not identifiers:
        message = "No DOC issue identifier found in PR title/body; skipping."
        if args.json:
            print(json.dumps({"skipped": True, "reason": message}))
        else:
            print(message)
        return 0

    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        print("error: LINEAR_API_KEY is required", file=sys.stderr)
        return 1

    status = PrStatus.from_github(state=state, draft=draft, merged=merged)
    rows = sync_identifiers(
        api_key, identifiers, status, dry_run=args.dry_run
    )
    if args.json:
        print(json.dumps({"event": status.event, "results": rows}, indent=2))
    else:
        print(f"PR event={status.event} identifiers={identifiers}")
        for row in rows:
            if row["updated"]:
                print(
                    f"  updated {row['identifier']} -> {row['current_state']}"
                )
            else:
                print(
                    f"  skipped {row['identifier']}: {row['skipped_reason']} "
                    f"(current={row['current_state']}, "
                    f"target={row['target_state']})"
                )
    # Fail the job only when an intended update could not find a state.
    for row in rows:
        if row["target_state"] is None:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
