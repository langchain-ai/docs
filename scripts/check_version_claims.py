"""Verify that package versions named in the docs were actually published.

Pages state minimum versions constantly ("requires `langchain>=1.3.2`"). A floor
is a claim about which release a feature landed in, so nothing here tries to
bump one: only a human knows whether a feature needs 1.3.2 or 1.4.0, and many
floors are deliberately capped below the next major. What a machine can settle
is narrower and absolute — whether the version in the page exists on the
registry at all. A reader who pastes a version that was never published gets a
resolver error, and that is always a bug.

The hard part is deciding which registry a specifier belongs to. `deepagents`
is published to both PyPI (0.x) and npm (1.x) on completely divergent version
lines, so `deepagents>=1.9.0` is correct inside a `:::js` fence and wrong inside
a `:::python` one. See ``resolve_ecosystem`` for the signals used.

Check every page, or just the ones a pull request touched::

    uv run python scripts/check_version_claims.py
    uv run python scripts/check_version_claims.py --files src/langsmith/evaluators.mdx
    uv run python scripts/check_version_claims.py --advisory-only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

SRC = Path("src")
IGNORE_FILE = Path("scripts/version_claims_ignore.txt")

# A specifier as it appears in prose or a requirements block:
#   langchain>=1.3.2   langsmith[livekit]>=0.11.2   @langchain/langgraph>=1.4.0
# The version group deliberately excludes a trailing dot so that a specifier
# ending a sentence ("requires `langgraph-api>=0.2.3`.") does not capture it.
SPECIFIER = re.compile(
    r"(?P<scope>@[a-z0-9][a-z0-9._-]{0,40}/)?"
    r"(?P<name>[a-z][a-z0-9._-]{1,40})"
    r"(?P<extras>\[[a-z0-9,_-]+\])?"
    r"(?P<op>>=|==)"
    r"(?P<version>[0-9][0-9a-zA-Z.]*[0-9a-zA-Z])"
)

# Only names matching these are ever interpolated into a registry URL.
SAFE_PYPI = re.compile(r"^[a-z0-9][a-z0-9._-]{1,60}$")
SAFE_NPM = re.compile(r"^(@[a-z0-9][a-z0-9._-]{0,40}/)?[a-z0-9][a-z0-9._-]{1,60}$")

# Pages routinely name both SDKs on one line, outside any language fence:
#   "requires `deepagents>=0.5.2` (Python) or `deepagents>=1.9.1` (TypeScript)"
# so the label nearest a specifier, on either side, wins over the fence around
# it ("Requires JS SDK version `langsmith>=0.5.25`" labels from the left).
PY_LABEL = re.compile(
    r"\((?:python|py)\b|\bfor python\b|\bpypi\b|\bpython sdk\b",
    re.IGNORECASE,
)
JS_LABEL = re.compile(
    r"\((?:typescript|ts|javascript|js|node)\b"
    r"|\bfor (?:typescript|javascript)\b"
    r"|\bnpm\b"
    r"|\b(?:js|ts|javascript|typescript|node) sdk\b",
    re.IGNORECASE,
)
LABEL_WINDOW = 40  # how far from a specifier a label can sit and still count

# A flat LangSmith page documenting a JavaScript-only SDK, so a bare
# `langsmith>=x` on it means the npm package. Pages under an /oss/javascript/ or
# /oss/python/ path are routed by their path instead and need no entry here.
JS_ONLY_PAGES = frozenset({"src/langsmith/trace-with-vercel-ai-sdk.mdx"})

PYPI = "pypi"
NPM = "npm"
REQUEST_TIMEOUT = 30
MAX_WORKERS = 8


@dataclass(frozen=True)
class Claim:
    """A single version specifier found in a page."""

    ecosystem: str
    package: str
    version: str
    operator: str

    @property
    def spec(self) -> str:
        return f"{self.package}{self.operator}{self.version}"


def nearest_label(line: str, start: int, end: int) -> str | None:
    """Return the ecosystem named by the language label closest to a specifier.

    `start` and `end` bound the specifier within `line`. Labels overlapping the
    specifier itself are skipped, and one further than LABEL_WINDOW away is
    treated as belonging to a different clause.
    """
    best: str | None = None
    best_distance = LABEL_WINDOW
    for pattern, ecosystem in ((JS_LABEL, NPM), (PY_LABEL, PYPI)):
        for match in pattern.finditer(line):
            if match.start() >= end:
                distance = match.start() - end
            elif match.end() <= start:
                distance = start - match.end()
            else:
                continue
            if distance < best_distance:
                best, best_distance = ecosystem, distance
    return best


def page_default(path: Path | None) -> str | None:
    """Return the ecosystem a page defaults to, from its path or the override set."""
    if path is None:
        return None
    posix = path.as_posix()
    if posix in JS_ONLY_PAGES or "/javascript/" in posix:
        return NPM
    if "/python/" in posix:
        return PYPI
    return None


def resolve_ecosystem(
    match: re.Match[str],
    line: str,
    fence: str | None,
    path: Path | None,
) -> str:
    """Decide whether a specifier names a PyPI or an npm package.

    Signals, strongest first: an `@scope/` prefix is npm-only syntax; an extras
    bracket is PyPI-only syntax; the nearest language label on the line, since
    pages name both SDKs in one unfenced sentence; then the enclosing fence;
    then the page's own language; then PyPI, because most bare specifiers in
    these docs are Python.
    """
    if match.group("scope"):
        return NPM
    if match.group("extras"):
        return PYPI

    label = nearest_label(line, match.start(), match.end())
    if label:
        return label
    if fence:
        return NPM if fence == "js" else PYPI
    return page_default(path) or PYPI


def claims_in_text(text: str, path: Path | None = None) -> dict[Claim, list[int]]:
    """Map every specifier in one page to the line numbers where it appears."""
    found: dict[Claim, list[int]] = {}
    fence: str | None = None
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped in (":::python", ":::js"):
            fence = stripped.removeprefix(":::")
            continue
        if stripped == ":::":
            fence = None
            continue
        for match in SPECIFIER.finditer(line):
            claim = Claim(
                ecosystem=resolve_ecosystem(match, line, fence, path),
                package=(match.group("scope") or "") + match.group("name"),
                version=match.group("version"),
                operator=match.group("op"),
            )
            found.setdefault(claim, []).append(lineno)
    return found


def collect_claims(paths: list[Path]) -> dict[Claim, list[str]]:
    """Map every specifier across `paths` to `file:line` locations."""
    everywhere: dict[Claim, list[str]] = {}
    for path in sorted(paths):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for claim, linenos in claims_in_text(text, path).items():
            everywhere.setdefault(claim, []).extend(
                f"{path}:{lineno}" for lineno in linenos
            )
    return everywhere


def _fetch_json(url: str) -> object:
    request = urllib.request.Request(  # noqa: S310 - https literal, name validated
        url,
        headers={
            "User-Agent": "langchain-docs-version-check/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:  # noqa: S310
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(response.read().decode(charset))


def fetch_releases(ecosystem: str, package: str) -> tuple[set[str], str] | None:
    """Return (all published versions, latest) or None if the lookup failed.

    A lookup that fails is reported as unresolved rather than as a bad version.
    A registry outage or a private package must not fail the build.
    """
    try:
        if ecosystem == PYPI:
            if not SAFE_PYPI.match(package):
                return None
            quoted = urllib.parse.quote(package, safe="")
            payload = _fetch_json(f"https://pypi.org/pypi/{quoted}/json")
            if not isinstance(payload, dict):
                return None
            return set(payload["releases"]), payload["info"]["version"]

        if not SAFE_NPM.match(package):
            return None
        quoted = urllib.parse.quote(package, safe="@").replace("/", "%2F")
        payload = _fetch_json(f"https://registry.npmjs.org/{quoted}")
        if not isinstance(payload, dict):
            return None
        return set(payload.get("versions", {})), payload["dist-tags"]["latest"]
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError, OSError):
        return None


def version_exists(version: str, published: set[str]) -> bool:
    """Whether `version` names a real release.

    Floors are often truncated to a series (`deepagents>=0.7`, `langchain>=1.1`),
    which is satisfied by any release in that series.
    """
    if version in published:
        return True
    prefix = f"{version}."
    return any(release.startswith(prefix) for release in published)


def load_ignores(path: Path) -> set[str]:
    """Read specifiers that are known-good despite not resolving."""
    if not path.exists():
        return set()
    entries = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = line.split("#", 1)[0].strip()
        if entry:
            entries.add(entry)
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--files",
        nargs="*",
        type=Path,
        help="Only check these pages (CI passes the pull request's changed files).",
    )
    parser.add_argument(
        "--advisory-only",
        action="store_true",
        help="Report findings but always exit 0.",
    )
    args = parser.parse_args()

    if args.files:
        paths = [p for p in args.files if p.suffix == ".mdx" and p.is_file()]
        if not paths:
            print("no .mdx files to check")
            return 0
    elif SRC.is_dir():
        paths = sorted(SRC.rglob("*.mdx"))
    else:
        print(f"❌ {SRC} not found; run from the repository root")
        return 1

    ignored = load_ignores(IGNORE_FILE)
    claims = {
        claim: locations
        for claim, locations in collect_claims(paths).items()
        if claim.spec not in ignored
    }
    if not claims:
        print(f"no version specifiers to check in {len(paths)} page(s)")
        return 0

    packages = sorted({(c.ecosystem, c.package) for c in claims})
    print(
        f"checking {len(claims)} specifier(s) "
        f"across {len(packages)} package(s) in {len(paths)} page(s)\n"
    )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = pool.map(lambda key: fetch_releases(*key), packages)
    registry = dict(zip(packages, results, strict=True))

    ghosts: list[tuple[Claim, str, list[str]]] = []
    unresolved: set[str] = set()

    for claim, locations in claims.items():
        entry = registry.get((claim.ecosystem, claim.package))
        if entry is None:
            unresolved.add(f"[{claim.ecosystem}] {claim.package}")
        elif not version_exists(claim.version, entry[0]):
            ghosts.append((claim, entry[1], sorted(locations)))

    if unresolved:
        print(f"note: {len(unresolved)} package(s) could not be looked up")
        for package in sorted(unresolved)[:10]:
            print(f"  {package}")
        print()

    if ghosts:
        print(f"❌ {len(ghosts)} version(s) named in the docs were never published:\n")
        for claim, latest, locations in sorted(ghosts, key=lambda row: -len(row[2])):
            print(f"  [{claim.ecosystem}] {claim.spec}   (latest is {latest})")
            for location in locations[:5]:
                print(f"      {location}")
        print(
            "\nFix the version in the page. If the specifier is correct and the "
            f"lookup is wrong, add it to {IGNORE_FILE} with a reason."
        )
        return 0 if args.advisory_only else 1

    print("✅ every version named in the docs exists on its registry")
    return 0


if __name__ == "__main__":
    sys.exit(main())
