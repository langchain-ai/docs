"""Create Linear issues for documentation updates."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from langchain.tools import tool

from tools.credentials import github_token, linear_api_key
from tools.evidence import ensure_evidence_in_body, parse_evidence_json
from tools.source import verify_evidence_in_source

LINEAR_API = "https://api.linear.app/graphql"
_HTTP_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "docs-release-watch/1.0",
}

# Optional override. When unset, issues are assigned to the Linear API key owner
# (the authenticated viewer). Set LINEAR_ASSIGNEE_ID to a specific user UUID to
# assign to someone else.
_ASSIGNEE_ID_ENV = "LINEAR_ASSIGNEE_ID"


def _normalize_api_key(raw: str) -> str:
    key = raw.strip().strip('"').strip("'")
    # Personal API keys are sent raw. OAuth access tokens use Bearer.
    if key.lower().startswith("bearer "):
        return key
    return key


async def _linear_graphql(
    query: str, variables: dict[str, Any] | None = None
) -> dict[str, Any]:
    token = _normalize_api_key(await linear_api_key())
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            LINEAR_API,
            headers={
                **_HTTP_HEADERS,
                "Authorization": token,
            },
            json={"query": query, "variables": variables or {}},
        )
    try:
        payload = response.json()
    except Exception:
        payload = {"raw": response.text[:500]}

    if response.status_code >= 400:
        raise RuntimeError(f"Linear HTTP {response.status_code}: {payload}")
    if payload.get("errors"):
        raise RuntimeError(f"Linear GraphQL error: {payload['errors']}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected Linear response: {payload}")
    return data


async def _resolve_team_id(team_key: str) -> str:
    key = team_key.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]+", key):
        raise ValueError(f"Invalid Linear team key {team_key!r}")

    data = await _linear_graphql(
        """
        query TeamByKey($key: String!) {
          teams(filter: { key: { eq: $key } }, first: 1) {
            nodes { id key name }
          }
        }
        """,
        {"key": key},
    )
    nodes = data.get("teams", {}).get("nodes") or []
    if not nodes:
        raise RuntimeError(f"Linear team with key {key!r} was not found.")
    return str(nodes[0]["id"])


async def _resolve_assignee() -> dict[str, str]:
    """Return assignee id/name for new issues.

    Defaults to the authenticated Linear viewer (the API key owner). Override
    with LINEAR_ASSIGNEE_ID when tickets should go to a different user.
    """
    override = os.environ.get(_ASSIGNEE_ID_ENV, "").strip()
    if override:
        data = await _linear_graphql(
            """
            query UserById($id: String!) {
              user(id: $id) { id name displayName email active }
            }
            """,
            {"id": override},
        )
        user = data.get("user")
        if not user or not user.get("active"):
            raise RuntimeError(
                f"LINEAR_ASSIGNEE_ID {override!r} was not found or is inactive."
            )
        return {
            "id": str(user["id"]),
            "name": str(user.get("name") or user.get("displayName") or ""),
            "email": str(user.get("email") or ""),
        }

    data = await _linear_graphql("{ viewer { id name displayName email } }")
    viewer = data.get("viewer") or {}
    if not viewer.get("id"):
        raise RuntimeError("Could not resolve Linear viewer for issue assignment.")
    return {
        "id": str(viewer["id"]),
        "name": str(viewer.get("name") or viewer.get("displayName") or ""),
        "email": str(viewer.get("email") or ""),
    }


@tool(parse_docstring=True)
async def create_linear_issue(
    title: str,
    description: str,
    evidence_json: str,
    team_key: str = "DOC",
    product: str = "openwiki",
    release_tag: str = "",
) -> str:
    """Create one Linear issue for a single documentation feature update.

    Args:
        title: Short issue title focused on one feature.
        description: Markdown description with release context, docs paths, and scope.
        evidence_json: JSON object with source_repo, source_tag, and items
            [{path, symbol}] or [{path, quote}] verified in product source at
            the release tag. Required; the tool refuses empty evidence.
        team_key: Linear team key (default: DOC).
        product: Product key this issue covers.
        release_tag: Product release tag that triggered the work.
    """
    evidence = parse_evidence_json(evidence_json)
    gh_token = None
    try:
        gh_token = await github_token()
    except RuntimeError:
        pass
    verification = await verify_evidence_in_source(evidence, token=gh_token)
    team_id = await _resolve_team_id(team_key)
    assignee = await _resolve_assignee()
    body = ensure_evidence_in_body((description or "").strip(), evidence)
    meta_lines = [
        "",
        "---",
        f"- Product: `{product}`",
    ]
    if release_tag:
        meta_lines.append(f"- Release: `{release_tag}`")
    meta_lines.append("- Source: docs-release-watch agent")
    if "Source: docs-release-watch agent" not in body:
        body = body + "\n".join(meta_lines)

    issue_title = (title or "").strip()
    if not issue_title:
        raise ValueError("title must be a non-empty string.")

    data = await _linear_graphql(
        """
        mutation CreateIssue($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue {
              id
              identifier
              title
              url
              assignee { id name }
            }
          }
        }
        """,
        {
            "input": {
                "teamId": team_id,
                "title": issue_title,
                "description": body,
                "assigneeId": assignee["id"],
            }
        },
    )
    result = data.get("issueCreate") or {}
    if not result.get("success") or not result.get("issue"):
        raise RuntimeError(f"Linear issueCreate failed: {result}")
    issue = result["issue"]
    return json.dumps(
        {
            "id": issue["id"],
            "identifier": issue["identifier"],
            "title": issue["title"],
            "url": issue["url"],
            "assignee": issue.get("assignee")
            or {
                "id": assignee["id"],
                "name": assignee["name"],
            },
            "team_key": team_key.strip().upper(),
            "product": product,
            "release_tag": release_tag,
            "evidence": evidence,
            "evidence_verified": verification,
        }
    )
