"""Collect reviewer feedback on AI docs review comments.

Reads every inline comment the review workflow posted on PRs labeled by it, and
tallies 👍, 👎, replies, and comments that GitHub marked outdated (the line
changed after the comment, which usually means the author acted on it). Read
only: it never writes to GitHub.

    export GITHUB_TOKEN="$(gh auth token)"
    uv run python scripts/ai_review_feedback.py --since 2026-11-06
    uv run python scripts/ai_review_feedback.py --since 2026-11-06 --json > feedback.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, timedelta

from scripts.ai_review_post import FINDING_MARKER, LABELS, GitHub

FP_RE = re.compile(re.escape(FINDING_MARKER).replace(r"\{fp\}", r"([0-9a-f]{12})"))
HEAD_RE = re.compile(r"^\*\*(Must fix|Major|Minor)\*\*(?: · (.+))?$", re.MULTILINE)
SKILLS_RE = re.compile(r"AI docs review \(([^)]+)\)")


def parse_comment(c: dict) -> dict | None:
    """Pull the finding's metadata and reactions out of one review comment."""
    body = c.get("body") or ""
    fp = FP_RE.search(body)
    if not fp:
        return None
    head = HEAD_RE.search(body)
    skills = SKILLS_RE.search(body)
    reactions = c.get("reactions") or {}
    return {
        "fingerprint": fp.group(1),
        "id": c.get("id"),
        "url": c.get("html_url"),
        "path": c.get("path"),
        "severity": head.group(1) if head else "",
        "rule": (head.group(2) or "").strip() if head else "",
        "skills": [s.strip() for s in skills.group(1).split(",")] if skills else [],
        "up": int(reactions.get("+1", 0)),
        "down": int(reactions.get("-1", 0)),
        "outdated": c.get("position") is None,
        "suggestion": "```suggestion" in body or "````suggestion" in body,
        "replies": 0,
    }


def collect(gh: GitHub, since: str) -> list[dict]:
    """Return one row per bot finding on PRs the workflow labeled since a date."""
    prs: set[int] = set()
    for label in LABELS:
        q = f"/issues?state=all&since={since}T00:00:00Z&labels={label.replace(' ', '%20').replace(':', '%3A')}"
        for issue in gh.paginate(q):
            if "pull_request" in issue:
                prs.add(issue["number"])
    rows = []
    for pr in sorted(prs):
        comments = gh.paginate(f"/pulls/{pr}/comments")
        found = {c["id"]: parse_comment(c) for c in comments}
        found = {k: v for k, v in found.items() if v}
        for c in comments:
            parent = c.get("in_reply_to_id")
            if parent in found:
                found[parent]["replies"] += 1
        for row in found.values():
            row["pr"] = pr
            rows.append(row)
    return rows


def report(rows: list[dict]) -> str:
    """Markdown tables by pass and by rule, then every 👎 with a link."""
    out = [f"# AI docs review feedback ({len(rows)} findings)", ""]

    def table(title: str, key) -> None:
        groups: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            for k in key(r):
                groups[k].append(r)
        out.extend(
            [
                f"## By {title}",
                "",
                f"| {title} | Findings | 👍 | 👎 | Replied | Outdated |",
                "|---|---|---|---|---|---|",
            ]
        )
        for k, rs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            out.append(
                f"| {k or '(none)'} | {len(rs)} | {sum(r['up'] > 0 for r in rs)} | {sum(r['down'] > 0 for r in rs)} "
                f"| {sum(r['replies'] > 0 for r in rs)} | {sum(r['outdated'] for r in rs)} |"
            )
        out.append("")

    table("pass", lambda r: r["skills"] or [""])
    table("severity", lambda r: [r["severity"]])
    table("rule", lambda r: [r["rule"][:80]])
    downs = [r for r in rows if r["down"] > r["up"]]
    out.extend([f"## Thumbs down ({len(downs)})", ""])
    out.extend(
        f"- [#{r['pr']} {r['path']}]({r['url']}): {r['severity']} · {r['rule'][:100]}"
        for r in downs
    )
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--since",
        default=(date.today() - timedelta(days=14)).isoformat(),
        help="YYYY-MM-DD",
    )
    parser.add_argument(
        "--repo", default=os.environ.get("GITHUB_REPOSITORY", "langchain-ai/docs")
    )
    parser.add_argument(
        "--json", action="store_true", help="Print raw rows instead of the report"
    )
    args = parser.parse_args(argv)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.since):
        parser.error("--since must be YYYY-MM-DD")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("GITHUB_TOKEN is not set", file=sys.stderr)
        return 1
    rows = collect(GitHub(args.repo, token), args.since)
    print(json.dumps(rows, indent=1) if args.json else report(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
