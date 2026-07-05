#!/usr/bin/env python3
"""Assemble weekly LangSmith Cloud + Fleet changelog entries from fragment files.

Reads per-PR changelog fragments from ``langchainplus/.changelog/`` (see that
directory's ``README.md`` for the schema), keeps the ones ready to publish,
groups them by the category map (which also routes each component to Cloud or
Fleet), and renders a Mintlify ``<Update>`` block ready to paste into
``src/langsmith/changelog.mdx``.

The weekly agent (see ``.claude/skills/changelog-weekly``) runs this, reviews the
rendered block, and opens a docs PR for human approval.

Readiness:
  - ``status: ready``            -> always included.
  - ``status: held`` + ``flag``  -> included only if the Eppo flag is fully
                                    rolled out (requires ``EPPO_API_KEY``).
  - ``status: held`` + no token  -> excluded, and reported so a human can flip it.

Usage:
  uv run python scripts/assemble_changelog.py                  # dry-run, print block
  uv run python scripts/assemble_changelog.py --week-label "June 15-19, 2026"
  uv run python scripts/assemble_changelog.py --check-flag my-eppo-flag-key   # debug Eppo
  uv run python scripts/assemble_changelog.py --promote       # flip rolled-out held -> ready

Eppo access: set ``EPPO_API_KEY`` in the environment (never pass it on the CLI or
commit it). The script only ever issues read (GET) requests to eppo.cloud.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# --- Constants -------------------------------------------------------------

# docs and langchainplus are sibling checkouts (~/gh/docs, ~/gh/langchainplus).
_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FRAGMENTS_DIR = _REPO_ROOT.parent / "langchainplus" / ".changelog"

# Eppo REST API. Domain is hardcoded (allowlist of one) and HTTPS-only per
# our SSRF guidance; never read the base URL from user input.
EPPO_API_BASE = "https://eppo.cloud/api/v1"
EPPO_TIMEOUT_SECONDS = 15



# --- Fragment model --------------------------------------------------------


@dataclass
class Fragment:
    path: Path
    title: str
    body: str
    components: list[str]
    flag: str | None
    status: str
    self_hosted: bool = False
    docs_link: str = ""
    pr: str = ""
    errors: list[str] = field(default_factory=list)


def _require_within(root: Path, candidate: Path) -> Path:
    """Resolve ``candidate`` and confirm it stays inside ``root``.

    Guards against path traversal / symlink escapes when iterating fragments.
    """
    resolved = candidate.resolve()
    root_resolved = root.resolve()
    if root_resolved not in resolved.parents and resolved != root_resolved:
        raise ValueError(f"Refusing to read path outside {root_resolved}: {resolved}")
    return resolved


def load_fragments(fragments_dir: Path) -> list[Fragment]:
    """Load and validate every ``*.yaml`` fragment directly in ``fragments_dir``.

    Files in ``published/`` and names starting with ``_`` or ``TEMPLATE`` are
    skipped.
    """
    if not fragments_dir.is_dir():
        raise SystemExit(f"Fragments directory not found: {fragments_dir}")

    fragments: list[Fragment] = []
    for entry in sorted(fragments_dir.glob("*.yaml")):
        name = entry.name
        if name.startswith(("_", "TEMPLATE")):
            continue
        path = _require_within(fragments_dir, entry)
        try:
            data = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError as exc:
            fragments.append(_invalid(path, f"YAML parse error: {exc}"))
            continue
        fragments.append(_build_fragment(path, data))
    return fragments


def _invalid(path: Path, message: str) -> Fragment:
    return Fragment(
        path=path, title="", body="", components=[], flag=None,
        status="", errors=[message],
    )


def _build_fragment(path: Path, data: dict) -> Fragment:
    frag = Fragment(
        path=path,
        title=str(data.get("title") or "").strip(),
        body=str(data.get("body") or "").strip(),
        components=list(data.get("components") or []),
        self_hosted=bool(data.get("self_hosted")),
        flag=(data.get("flag") or None),
        status=str(data.get("status") or "").strip().lower(),
        docs_link=str(data.get("docs_link") or "").strip(),
        pr=str(data.get("pr") or "").strip(),
    )
    if not frag.title:
        frag.errors.append("missing `title`")
    if not frag.body:
        frag.errors.append("missing `body`")
    if not frag.components:
        frag.errors.append("missing `components`")
    if frag.status not in {"ready", "held"}:
        frag.errors.append(f"invalid status: {frag.status!r} (want ready|held)")
    if frag.status == "held" and not frag.flag:
        frag.errors.append("status is held but no flag set")
    return frag


# --- Category map ----------------------------------------------------------


def load_category_map(fragments_dir: Path) -> dict[str, dict]:
    path = fragments_dir / "_category-map.yaml"
    if not path.is_file():
        raise SystemExit(f"Category map not found: {path}")
    data = yaml.safe_load(path.read_text()) or {}
    return data.get("components", {})


def categorize(frag: Fragment, category_map: dict[str, dict]) -> tuple[str, str | None]:
    """Return (section, group) from the first component present in the map."""
    for comp in frag.components:
        if comp in category_map:
            entry = category_map[comp]
            return entry["section"], entry.get("group")
    return "Other", None


# --- Eppo rollout check ----------------------------------------------------


def _eppo_get(path: str, token: str) -> dict | list:
    """GET a path under the Eppo REST API base (HTTPS + allowlisted domain)."""
    url = f"{EPPO_API_BASE}/{path.lstrip('/')}"
    if not url.startswith("https://eppo.cloud/"):  # belt-and-suspenders SSRF guard
        raise ValueError("Eppo URL failed allowlist check")
    req = urllib.request.Request(url, headers={"X-Eppo-Token": token})
    with urllib.request.urlopen(req, timeout=EPPO_TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode())


def eppo_flag_index(token: str) -> dict[str, dict]:
    """Fetch feature flags (with allocations) indexed by their flag key.

    Eppo's flag-detail endpoint is keyed by numeric id, not the flag key, so we
    list flags and index by ``key``. Accepts a bare list or an envelope.

    NOTE: this reads a single page. If the API paginates and a held fragment's
    flag is on a later page, it surfaces as "Eppo flag not found" (a loud error,
    never a silent wrong publish). The truncation check below warns when the
    envelope reports more flags than were returned.
    """
    payload = _eppo_get("feature-flags?include_detailed_allocations=true", token)
    if isinstance(payload, list):
        items = payload
    else:
        items = (
            payload.get("flags") or payload.get("data")
            or payload.get("results") or payload.get("items") or []
        )
        total = payload.get("total_count") or payload.get("total") or payload.get("count")
        if isinstance(total, int) and total > len(items):
            print(
                f"WARNING: Eppo returned {len(items)} of {total} flags (paginated); "
                f"some held fragments may falsely report 'flag not found'.",
                file=sys.stderr,
            )
    return {f["key"]: f for f in items if isinstance(f, dict) and f.get("key")}


def is_fully_rolled_out(flag_json: dict) -> bool:
    """Return True when the flag serves one variant to the whole production audience.

    Eppo models each environment as a waterfall of allocations (top-level
    ``allocations``, tagged by ``environment_id``). Allocations with
    ``targeting_rules`` only cover the tenants they match; users who match none
    fall through to the first allocation with no targeting rules (the catch-all,
    usually ``is_default``). That catch-all decides what the general population
    gets, so it is the signal for "shipped to everyone".

    Fully rolled out := the production environment is active AND its first
    no-targeting allocation has full traffic exposure and assigns 100% weight to
    a single variation. For BOOLEAN flags that variation must be ``"true"`` (a
    catch-all serving ``"false"`` means the feature is off for everyone).
    """
    prod = next((e for e in flag_json.get("environments", []) if e.get("is_production")), None)
    if prod is None or not prod.get("active"):
        return False
    prod_id = prod.get("id")

    is_boolean = flag_json.get("variation_type") == "BOOLEAN"
    on_variation_ids = {
        v["id"] for v in flag_json.get("variations", []) if v.get("variant_key") == "true"
    }

    prod_allocations = [
        a for a in flag_json.get("allocations", [])
        if a.get("environment_id") == prod_id and not a.get("archived_at")
    ]
    for alloc in prod_allocations:
        if alloc.get("targeting_rules"):
            continue  # only covers targeted tenants; not the general population
        # First catch-all allocation reached: it decides what everyone else gets.
        # Eppo expresses full exposure as the fraction 1; tolerate 100 (percent).
        if alloc.get("percent_exposure", 1) not in (1, 100):
            return False  # partial traffic exposure
        served = [w for w in alloc.get("variation_weight", []) if w.get("weight", 0) > 0]
        if len(served) != 1:
            return False  # split across variants (experiment), not a uniform rollout
        if is_boolean and served[0].get("variation_id") not in on_variation_ids:
            return False  # catch-all serves "false" -> off for everyone
        return True
    return False  # no catch-all -> only targeted tenants get the feature


def effective_status(frag: Fragment, flag_index: dict[str, dict], have_token: bool) -> str:
    """Resolve held entries against Eppo. Returns 'ready', 'held', or 'error'."""
    if frag.status == "ready":
        return "ready"
    if frag.status == "held":
        if not frag.flag or not have_token:
            return "held"
        flag = flag_index.get(frag.flag)
        if flag is None:
            frag.errors.append(f"Eppo flag not found: {frag.flag!r}")
            return "error"
        return "ready" if is_fully_rolled_out(flag) else "held"
    return "error"


# --- Rendering -------------------------------------------------------------


def render_bullet(frag: Fragment) -> str:
    text = frag.body
    if frag.docs_link and "](" not in text:
        sep = " " if text.endswith(".") else ". "
        text = f"{text}{sep}[Learn more]({frag.docs_link})."
    return f"- {text}"


def render_update_block(
    fragments: list[Fragment],
    category_map: dict[str, dict],
    week_label: str,
    rss_date: str,
) -> str:
    """Render ready fragments into a single Mintlify ``<Update>`` block.

    Sections and groups follow the order they appear in the category map.
    """
    section_order = []
    for entry in category_map.values():
        if entry["section"] not in section_order:
            section_order.append(entry["section"])
    section_order.append("Other")

    # section -> group(or None) -> [bullets], preserving insertion order.
    buckets: dict[str, dict[str | None, list[str]]] = {}
    for frag in fragments:
        section, group = categorize(frag, category_map)
        buckets.setdefault(section, {}).setdefault(group, []).append(render_bullet(frag))

    lines = [
        f'<Update label="{week_label}" rss={{{{ title: "{rss_date} - LangSmith Cloud update" }}}}>',
        "",
    ]
    for section in section_order:
        if section not in buckets:
            continue
        lines.append(f"## {section}")
        lines.append("")
        groups = buckets[section]
        # Render the ungrouped bullets first, then named groups.
        if None in groups:
            lines.extend(groups[None])
            lines.append("")
        for group, bullets in groups.items():
            if group is None:
                continue
            lines.append(f"### {group}")
            lines.append("")
            lines.extend(bullets)
            lines.append("")
    lines.append("</Update>")
    return "\n".join(lines)


# --- Week helpers ----------------------------------------------------------


def default_week(today: dt.date) -> tuple[str, str]:
    """Return (label, rss_date) for the Mon-Fri week containing ``today``."""
    monday = today - dt.timedelta(days=today.weekday())
    friday = monday + dt.timedelta(days=4)
    if monday.month == friday.month:
        label = f"{monday.strftime('%B')} {monday.day}-{friday.day}, {friday.year}"
    else:
        label = f"{monday.strftime('%B %-d')} - {friday.strftime('%B %-d')}, {friday.year}"
    return label, monday.isoformat()


# --- CLI -------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fragments-dir", type=Path, default=DEFAULT_FRAGMENTS_DIR)
    parser.add_argument("--week-label", default=None, help='e.g. "June 15-19, 2026"')
    parser.add_argument("--rss-date", default=None, help="ISO date for the rss title, e.g. 2026-06-15")
    parser.add_argument("--check-flag", default=None, help="debug: print Eppo JSON + rollout verdict for a flag key")
    parser.add_argument("--promote", action="store_true", help="flip rolled-out held fragments to status: ready in place")
    args = parser.parse_args(argv)

    token = os.environ.get("EPPO_API_KEY")

    # Debug mode: inspect one flag so the rollout predicate can be verified.
    if args.check_flag:
        if not token:
            print("EPPO_API_KEY not set", file=sys.stderr)
            return 2
        index = eppo_flag_index(token)
        flag = index.get(args.check_flag)
        if flag is None:
            print(f"Flag {args.check_flag!r} not found. Available keys (first 30):", file=sys.stderr)
            for key in list(index)[:30]:
                print(f"  - {key}", file=sys.stderr)
            return 1
        print(json.dumps(flag, indent=2))
        print(f"\nis_fully_rolled_out -> {is_fully_rolled_out(flag)}", file=sys.stderr)
        return 0

    fragments = load_fragments(args.fragments_dir)
    category_map = load_category_map(args.fragments_dir)

    invalid = [f for f in fragments if f.errors]
    valid = [f for f in fragments if not f.errors]

    # Fetch the Eppo flag index once if a token is available and any held
    # fragment needs resolving.
    flag_index: dict[str, dict] = {}
    if token and any(f.status == "held" and f.flag for f in valid):
        try:
            flag_index = eppo_flag_index(token)
        except (urllib.error.URLError, ValueError) as exc:
            print(f"WARNING: could not fetch Eppo flags ({exc}); held entries stay held", file=sys.stderr)

    ready, held, errored, promoted = [], [], [], []
    for frag in valid:
        status = effective_status(frag, flag_index, bool(token))
        if status == "ready":
            ready.append(frag)
            if args.promote and frag.status == "held":
                _flip_to_ready(frag)
                promoted.append(frag)
        elif status == "held":
            held.append(frag)
        else:
            errored.append(frag)

    if not args.week_label or not args.rss_date:
        label, rss = default_week(dt.date.today())
        week_label = args.week_label or label
        rss_date = args.rss_date or rss
    else:
        week_label, rss_date = args.week_label, args.rss_date

    # Report to stderr so stdout stays a clean, paste-able MDX block.
    def report(tag: str, items: list[Fragment]) -> None:
        if items:
            print(f"\n# {tag} ({len(items)}):", file=sys.stderr)
            for f in items:
                detail = f" — {'; '.join(f.errors)}" if f.errors else ""
                print(f"  - {f.path.name}: {f.title or '(no title)'}{detail}", file=sys.stderr)

    report("READY (rendered below)", ready)
    report("HELD (flag not fully rolled out)", held)
    report("ERROR (Eppo lookup failed)", errored)
    report("INVALID fragments (skipped)", invalid)
    if promoted:
        print(f"\n# PROMOTED held -> ready in place ({len(promoted)})", file=sys.stderr)

    if ready:
        print(render_update_block(ready, category_map, week_label, rss_date))
    else:
        print("# No ready fragments to render.", file=sys.stderr)
    return 0


def _flip_to_ready(frag: Fragment) -> None:
    """Rewrite the fragment's status field to ready, preserving the rest."""
    data = yaml.safe_load(frag.path.read_text()) or {}
    data["status"] = "ready"
    frag.path.write_text(yaml.safe_dump(data, sort_keys=False))


if __name__ == "__main__":
    raise SystemExit(main())
