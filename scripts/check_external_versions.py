"""Check version requirements the docs mirror from an upstream project.

Some pages restate a requirement another project owns. `/langsmith/trace-with-codex`
names the Codex CLI version its plugin needs, and the plugin's own README is the
truth. Nothing in the docs repo changes when that README does, so the page drifts
silently: it sat at v0.128 while upstream had moved to v0.153.4, and a reader
reported it before anything here noticed.

Registry lookups cannot help, because these requirements are not packages. So
each mirrored claim is registered in ``scripts/data/external_versions.yaml``
with the regex that finds it in the page and the upstream source that owns it.

    uv run python scripts/check_external_versions.py
    uv run python scripts/check_external_versions.py --only codex-cli
    uv run python scripts/check_external_versions.py --write

``--write`` substitutes the upstream version into the page. It only ever
replaces the digits the pattern captured. The surrounding prose is not checked
against upstream, so a rewrite still needs a human to confirm the rest of the
requirement (a new peer dependency, a changed flag) did not also change.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import yaml

REGISTRY = Path("scripts/data/external_versions.yaml")
SRC = Path("src")

# Only slugs and paths matching these are interpolated into a request URL.
SAFE_REPO = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,60}/[A-Za-z0-9][A-Za-z0-9._-]{0,60}$"
)
SAFE_REPO_PATH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,200}$")

REQUEST_TIMEOUT = 30
GITHUB_FILE = "github_file"
GITHUB_RELEASE = "github_release"


class RegistryError(Exception):
    """The registry file describes an entry that cannot be acted on."""


@dataclass(frozen=True)
class Entry:
    """One mirrored version claim."""

    id: str
    label: str
    page: Path
    pattern: re.Pattern[str]
    source: dict[str, str]


def resolve_page(raw: str) -> Path:
    """Resolve a registry page path, refusing anything outside `src/`.

    The registry is committed and reviewed, but `--write` edits whatever it
    names, so the path is confirmed to stay inside the docs tree.
    """
    candidate = Path(raw)
    if candidate.is_absolute():
        msg = f"page must be a relative path, got {raw!r}"
        raise RegistryError(msg)
    resolved = (Path.cwd() / candidate).resolve()
    root = (Path.cwd() / SRC).resolve()
    if not resolved.is_relative_to(root):
        msg = f"page {raw!r} resolves outside {SRC}/"
        raise RegistryError(msg)
    return candidate


def load_registry(path: Path) -> list[Entry]:
    """Parse and validate the registry file."""
    if not path.exists():
        msg = f"{path} not found; run from the repository root"
        raise RegistryError(msg)

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(raw, list):
        msg = f"{path} must hold a list of entries"
        raise RegistryError(msg)

    entries = []
    for item in raw:
        missing = {"id", "label", "page", "pattern", "source"} - set(item)
        if missing:
            msg = f"entry {item.get('id', '?')!r} is missing {sorted(missing)}"
            raise RegistryError(msg)

        pattern = re.compile(item["pattern"])
        if "version" not in pattern.groupindex:
            msg = f"entry {item['id']!r}: pattern needs a `version` named group"
            raise RegistryError(msg)

        source = item["source"]
        kind = source.get("type")
        if kind not in (GITHUB_FILE, GITHUB_RELEASE):
            msg = f"entry {item['id']!r}: unknown source type {kind!r}"
            raise RegistryError(msg)
        if not SAFE_REPO.match(source.get("repo", "")):
            msg = f"entry {item['id']!r}: bad repo slug {source.get('repo')!r}"
            raise RegistryError(msg)
        if kind == GITHUB_FILE:
            repo_path = source.get("path", "")
            if not SAFE_REPO_PATH.match(repo_path) or ".." in repo_path:
                msg = f"entry {item['id']!r}: bad source path {repo_path!r}"
                raise RegistryError(msg)
            if "version" not in re.compile(source["pattern"]).groupindex:
                msg = f"entry {item['id']!r}: source pattern needs a `version` group"
                raise RegistryError(msg)

        entries.append(
            Entry(
                id=item["id"],
                label=item["label"],
                page=resolve_page(item["page"]),
                pattern=pattern,
                source=source,
            )
        )
    return entries


def _get(url: str, *, accept: str) -> str:
    headers = {"User-Agent": "langchain-docs-version-check/1.0", "Accept": accept}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)  # noqa: S310 - https literal
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:  # noqa: S310
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset)


def upstream_version(source: dict[str, str]) -> str | None:
    """Fetch the version the upstream source states, or None if unavailable."""
    repo = source["repo"]
    if not SAFE_REPO.match(repo):
        return None
    try:
        if source["type"] == GITHUB_RELEASE:
            payload = json.loads(
                _get(
                    f"https://api.github.com/repos/{repo}/releases/latest",
                    accept="application/vnd.github+json",
                )
            )
            tag = payload.get("tag_name", "")
            return tag.removeprefix("v") or None

        repo_path = urllib.parse.quote(source["path"])
        body = _get(
            f"https://raw.githubusercontent.com/{repo}/HEAD/{repo_path}",
            accept="text/plain",
        )
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None

    match = re.search(source["pattern"], body)
    return match.group("version") if match else None


def documented_version(entry: Entry, text: str) -> tuple[str, re.Match[str]] | None:
    """Find the version the page states. The pattern must match exactly once."""
    matches = list(entry.pattern.finditer(text))
    if len(matches) != 1:
        return None
    return matches[0].group("version"), matches[0]


def rewrite(text: str, match: re.Match[str], new_version: str) -> str:
    """Replace only the digits the `version` group captured."""
    start, end = match.span("version")
    return text[:start] + new_version + text[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--only", help="Check a single entry by id.")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Update pages whose version has drifted.",
    )
    args = parser.parse_args()

    try:
        entries = load_registry(args.registry)
    except RegistryError as error:
        print(f"❌ {error}")
        return 1

    if args.only:
        entries = [e for e in entries if e.id == args.only]
        if not entries:
            print(f"❌ no entry with id {args.only!r}")
            return 1

    drifted: list[tuple[Entry, str, str]] = []
    unreadable: list[tuple[Entry, str]] = []
    in_sync = 0

    for entry in entries:
        if not entry.page.exists():
            unreadable.append((entry, f"page {entry.page} not found"))
            continue
        text = entry.page.read_text(encoding="utf-8")

        found = documented_version(entry, text)
        if found is None:
            unreadable.append(
                (entry, f"pattern did not match exactly once in {entry.page}")
            )
            continue
        current, match = found

        latest = upstream_version(entry.source)
        if latest is None:
            unreadable.append((entry, f"could not read {entry.source['repo']}"))
            continue

        if latest == current:
            in_sync += 1
            print(f"✅ {entry.label}: {current} matches {entry.source['repo']}")
            continue

        drifted.append((entry, current, latest))
        print(
            f"⚠️  {entry.label}: docs say {current}, "
            f"{entry.source['repo']} says {latest}"
        )
        if args.write:
            entry.page.write_text(rewrite(text, match, latest), encoding="utf-8")
            print(f"    updated {entry.page}")

    if unreadable:
        print(f"\n❌ {len(unreadable)} entr(ies) could not be checked:")
        for entry, reason in unreadable:
            print(f"  {entry.id}: {reason}")

    print(f"\n{in_sync} in sync, {len(drifted)} drifted, {len(unreadable)} unreadable")

    if args.write:
        if drifted:
            print(
                "\nReview the surrounding prose before merging. Only the version "
                "number was rewritten; a changed peer requirement or flag "
                "upstream will not show up here."
            )
        # Syncing reports problems but does not fail on them. A GitHub outage
        # must not stop the entries that did resolve from reaching a pull
        # request, and a pattern that stopped matching its page already fails
        # test_committed_registry_is_valid on every pull request.
        return 0
    return 1 if drifted or unreadable else 0


if __name__ == "__main__":
    sys.exit(main())
