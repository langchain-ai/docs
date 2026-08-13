#!/usr/bin/env python3
"""Reconciliation audit: find user-facing merged PRs with no changelog fragment.

Lists merged PRs in langchain-ai/langchainplus over a CONTIGUOUS date window
(covering weekends, so Friday/weekend merges never fall between weekly runs),
filters to user-facing ``feat``/``fix`` changes, and reports any that have no
corresponding ``.changelog`` fragment. This is the backstop that guarantees no
user-facing PR silently slips out of the Cloud/Fleet changelog.

It errs toward over-reporting: a borderline PR is flagged for a human to
disposition rather than dropped. Dispositioned PRs (for example, ones written
into the changelog by hand during the transition) go in ``--ignore-file`` so
they are not re-flagged.

Usage:
  uv run python scripts/audit_changelog_coverage.py --since 2026-06-06 --until 2026-06-22
  uv run python scripts/audit_changelog_coverage.py            # default: last 14 days
  uv run python scripts/audit_changelog_coverage.py --ignore-file dispositioned.txt

Requires the `gh` CLI, authenticated for langchain-ai/langchainplus (read-only).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FRAGMENTS_DIR = _REPO_ROOT.parent / "langchainplus" / ".changelog"
REPO = "langchain-ai/langchainplus"

GH_TIMEOUT_SECONDS = 90
GH_PAGE_LIMIT = 1000          # gh search hard cap; we sub-window to stay under it.
SUBWINDOW_DAYS = 7            # query at most a week at a time to avoid truncation.

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Only feat/fix are candidate user-facing changes (docs/refactor/perf/chore/ci/
# test/build/revert are excluded by type). Within feat/fix, drop scopes that are
# clearly internal/infra. Kept deliberately SHORT so the audit over-reports
# rather than hiding a real gap.
TYPE_RE = re.compile(r"^(feat|fix)(\([^)]*\))?!?:", re.IGNORECASE)
INTERNAL_SCOPE_RE = re.compile(
    r"^(feat|fix)\((sandbox-host|sandbox-router|v21proxy|v21shadow|e2e|stlc|"
    r"langdev|ci|smith-go|smith-sdks|messages|issuebench)\)",
    re.IGNORECASE,
)
# Self-hosted/BYOC/provisioning work has no scope to filter on but is out of
# scope for the Cloud/Fleet changelog. Matched anywhere in the title.
TITLE_INTERNAL_RE = re.compile(r"\b(byoc|data[ -]plane|provisioning)\b", re.IGNORECASE)
PR_NUM_RE = re.compile(r"#(\d+)\s*$")


def _validate_date(value: str) -> str:
    if not DATE_RE.match(value):
        raise SystemExit(f"Invalid date {value!r}; expected YYYY-MM-DD")
    return value


def _subwindows(since: dt.date, until: dt.date) -> list[tuple[dt.date, dt.date]]:
    """Split [since, until] into contiguous chunks of at most SUBWINDOW_DAYS."""
    if since > until:
        raise SystemExit(f"--since ({since}) is after --until ({until})")
    out = []
    start = since
    while start <= until:
        end = min(start + dt.timedelta(days=SUBWINDOW_DAYS - 1), until)
        out.append((start, end))
        start = end + dt.timedelta(days=1)
    return out


def fetch_merged_prs(since: dt.date, until: dt.date) -> list[dict]:
    """Fetch merged PRs across the window, sub-windowing to avoid the page cap."""
    prs: dict[int, dict] = {}
    for start, end in _subwindows(since, until):
        argv = [
            "gh", "search", "prs", "--repo", REPO, "--merged",
            "--merged-at", f"{start.isoformat()}..{end.isoformat()}",
            "--limit", str(GH_PAGE_LIMIT),
            "--json", "number,title,url",
        ]
        result = subprocess.run(
            argv, capture_output=True, text=True, timeout=GH_TIMEOUT_SECONDS, check=False,
        )
        if result.returncode != 0:
            raise SystemExit(f"gh failed for {start}..{end}: {result.stderr.strip()}")
        batch = json.loads(result.stdout or "[]")
        if len(batch) >= GH_PAGE_LIMIT:
            print(
                f"WARNING: {start}..{end} hit the {GH_PAGE_LIMIT}-result cap; "
                f"narrow SUBWINDOW_DAYS to avoid missing PRs.",
                file=sys.stderr,
            )
        for pr in batch:
            prs[pr["number"]] = pr
    return list(prs.values())


def is_user_facing(title: str) -> bool:
    return (
        bool(TYPE_RE.match(title))
        and not INTERNAL_SCOPE_RE.match(title)
        and not TITLE_INTERNAL_RE.search(title)
    )


def covered_pr_numbers(fragments_dir: Path) -> set[int]:
    """PR numbers referenced by any fragment (active or already published)."""
    root = fragments_dir.resolve()
    covered: set[int] = set()
    for sub in (root, root / "published"):
        if not sub.is_dir():
            continue
        for path in sub.glob("*.yaml"):
            resolved = path.resolve()
            if root not in resolved.parents:  # path-traversal guard
                continue
            if resolved.name.startswith(("_", "TEMPLATE")):
                continue
            try:
                data = yaml.safe_load(resolved.read_text()) or {}
            except yaml.YAMLError:
                continue
            m = PR_NUM_RE.search(str(data.get("pr", "")))
            if m:
                covered.add(int(m.group(1)))
    return covered


def pr_added_fragment(pr_number: int) -> bool:
    """True if the PR's own diff adds or touches a .changelog/*.yaml fragment.

    This is the primary (going-forward) coverage signal: a fragment authored in
    the same PR as the change needs no `pr:` field. The `pr:` field is only the
    fallback for fragments added separately from their source PR (e.g. backfills).
    """
    argv = ["gh", "pr", "view", str(pr_number), "--repo", REPO, "--json", "files"]
    result = subprocess.run(
        argv, capture_output=True, text=True, timeout=GH_TIMEOUT_SECONDS, check=False
    )
    if result.returncode != 0:
        return False
    files = json.loads(result.stdout or "{}").get("files", [])
    return any(
        f.get("path", "").startswith(".changelog/") and f.get("path", "").endswith(".yaml")
        for f in files
    )


def load_ignore(path: Path | None) -> set[int]:
    if not path:
        return set()
    nums: set[int] = set()
    for raw in path.read_text().splitlines():
        token = raw.split("#", 1)[0].strip()  # drop inline/full-line comments
        if token.isdigit():
            nums.add(int(token))
    return nums


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", type=_validate_date, default=None, help="YYYY-MM-DD (default: 14 days ago)")
    parser.add_argument("--until", type=_validate_date, default=None, help="YYYY-MM-DD (default: today)")
    parser.add_argument("--fragments-dir", type=Path, default=DEFAULT_FRAGMENTS_DIR)
    parser.add_argument("--ignore-file", type=Path, default=None, help="newline list of PR numbers to skip")
    args = parser.parse_args(argv)

    today = dt.date.today()
    until = dt.date.fromisoformat(args.until) if args.until else today
    since = dt.date.fromisoformat(args.since) if args.since else until - dt.timedelta(days=14)

    prs = fetch_merged_prs(since, until)
    covered = covered_pr_numbers(args.fragments_dir)
    ignored = load_ignore(args.ignore_file)

    candidates = [p for p in prs if is_user_facing(p["title"])]
    # Going-forward coverage: a PR that added a fragment in its own diff is
    # covered without a `pr:` field. Only check candidates not already covered
    # (by a fragment's pr: field) or dispositioned, to limit gh calls.
    for p in candidates:
        if p["number"] not in covered and p["number"] not in ignored and pr_added_fragment(p["number"]):
            covered.add(p["number"])
    uncovered = [
        p for p in candidates
        if p["number"] not in covered and p["number"] not in ignored
    ]
    uncovered.sort(key=lambda p: p["number"], reverse=True)

    print(
        f"# Audit {since}..{until} (contiguous, includes weekends)\n"
        f"# merged PRs: {len(prs)} | user-facing feat/fix: {len(candidates)} | "
        f"covered by a fragment: {sum(1 for p in candidates if p['number'] in covered)} | "
        f"ignored: {sum(1 for p in candidates if p['number'] in ignored)}\n"
        f"# UNCOVERED (no fragment, needs disposition): {len(uncovered)}",
        file=sys.stderr,
    )
    for p in uncovered:
        print(f"{p['number']}\t{p['title']}\t{p['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
