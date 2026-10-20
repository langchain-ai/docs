#!/usr/bin/env python3
"""Check ``packages.yml`` repo links; fix renames or delist dead third-party integrations.

Policy (1A):

- Skip first-party packages whose ``repo`` is under ``langchain-ai/``.
- When the recorded GitHub ``owner/repo`` returns 404, look for a live alternate
  on PyPI ``project_urls``, the npm ``repository`` field (when ``js`` is set),
  and ``docs_url`` values in ``integration_external_docs.yaml``.
- If a different live third-party GitHub ``owner/repo`` is found, update
  ``packages.yml`` (and listing hrefs that used the old GitHub URL). Never
  auto-retarget into ``langchain-ai/*``.
- If a live GitLab project remains, do not delist; report it under attention.
- If a live partner docs / homepage URL remains (PyPI Documentation/Homepage or
  an external ``docs_url``, excluding registry pages and the dead GitHub URL),
  do not delist; report it under attention. A missing GitHub repo alone is not
  enough when the package still has reachable docs (for example Writer).
- If no live GitHub, GitLab, or partner-docs alternate exists, fully delist the
  package: ``packages.yml``, matching external YAML rows, downloads-table rows,
  and the ``all_providers`` card when no other remaining package shares the
  same provider key (``name_short``).

Usage (from repo root):

    uv run python scripts/check_integration_repos.py
    uv run python scripts/check_integration_repos.py --write \\
        --evidence /tmp/evidence.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlparse

import requests
from ruamel.yaml import YAML

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
_PACKAGES_YML = _REPO_ROOT / "packages.yml"
_EXTERNAL_DOCS = _SCRIPT_DIR / "data" / "integration_external_docs.yaml"
_ALL_PROVIDERS = (
    _REPO_ROOT / "src" / "oss" / "python" / "integrations" / "providers" / "all_providers.mdx"
)
_FIRST_PARTY_OWNER = "langchain-ai"
_REQUEST_TIMEOUT = 20
_HTTP_HEADERS = {"User-Agent": "langchain-docs-check-integration-repos/1.0"}

_SAFE_REPO = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,60}/[A-Za-z0-9][A-Za-z0-9._-]{0,80}$"
)
_GITHUB_REPO_URL = re.compile(
    r"https?://(?:www\.)?github\.com/"
    r"(?P<owner>[A-Za-z0-9][A-Za-z0-9._-]{0,60})/"
    r"(?P<repo>[A-Za-z0-9][A-Za-z0-9._-]{0,80})",
    re.IGNORECASE,
)
_GITLAB_PROJECT_URL = re.compile(
    r"https?://(?:www\.)?gitlab\.com/"
    r"(?P<path>[A-Za-z0-9][A-Za-z0-9._/-]{0,200})",
    re.IGNORECASE,
)
_CARD_RE = re.compile(
    r"\n[ \t]*<Card\b[\s\S]*?</Card>\s*",
    re.MULTILINE,
)


def _yaml_loader() -> YAML:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    # packages.yml occasionally contains duplicate keys from bad merges;
    # prefer loading over failing the weekly scan.
    yaml.allow_duplicate_keys = True
    return yaml


def name_short(package_name: str) -> str:
    """Derive the provider short name used across listing surfaces."""
    short = package_name.removeprefix("langchain-")
    return short.removesuffix("-langchain")


def provider_key(package_name: str) -> str:
    """Normalize the provider key used to decide whether a card can go."""
    return name_short(package_name).casefold()


@dataclass(frozen=True)
class VcsHit:
    """A candidate source-control home for a package."""

    kind: str  # "github" | "gitlab" | "other"
    label: str  # owner/repo, gitlab path, or URL
    url: str
    source: str  # where it was found


@dataclass
class PackageFinding:
    """Disposition for one third-party ``packages.yml`` entry."""

    name: str
    repo: str
    disposition: str  # ok | fix | delist | attention | skip_first_party | error
    detail: str
    new_repo: Optional[str] = None
    pypi: Optional[str] = None
    npm: Optional[str] = None
    removed_docs_urls: list[str] = field(default_factory=list)


HttpGet = Callable[[str], requests.Response]


def github_repo_exists(repo: str, get: HttpGet) -> bool:
    """Whether a GitHub repository is reachable via ``get``."""
    if not _SAFE_REPO.match(repo):
        return False
    response = get(f"https://github.com/{repo}")
    return response.status_code == 200


def make_http_get(token: Optional[str]) -> HttpGet:
    """Build an HTTP GET helper, using the GitHub API when a token is present."""

    def _get(url: str) -> requests.Response:
        headers = dict(_HTTP_HEADERS)
        if token and url.startswith("https://api.github.com/"):
            headers["Authorization"] = f"Bearer {token}"
            headers["Accept"] = "application/vnd.github+json"
        elif token and url.startswith("https://github.com/"):
            # Prefer the API for rate limits when authenticated.
            parsed = urlparse(url)
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) >= 2 and _SAFE_REPO.match(f"{parts[0]}/{parts[1]}"):
                api_url = f"https://api.github.com/repos/{parts[0]}/{parts[1]}"
                headers["Authorization"] = f"Bearer {token}"
                headers["Accept"] = "application/vnd.github+json"
                return requests.get(
                    api_url, timeout=_REQUEST_TIMEOUT, headers=headers
                )
        return requests.get(url, timeout=_REQUEST_TIMEOUT, headers=headers)

    return _get


def url_exists(url: str, get: HttpGet) -> bool:
    """Whether ``url`` returns a successful HTTP response."""
    try:
        response = get(url)
    except requests.RequestException:
        return False
    return 200 <= response.status_code < 400


def is_registry_page(url: str) -> bool:
    """Whether ``url`` is a PyPI/npm registry page rather than partner docs."""
    host = urlparse(url).netloc.casefold().removeprefix("www.")
    return host in {"pypi.org", "npmjs.com", "registry.npmjs.org"}


def is_github_or_gitlab_url(url: str) -> bool:
    """Whether ``url`` points at GitHub or GitLab (handled as VCS, not docs)."""
    host = urlparse(url).netloc.casefold().removeprefix("www.")
    return host in {"github.com", "gitlab.com"}


def normalize_repo_slug(repo: str) -> str:
    """Collapse accidental ``owner//repo`` typos to ``owner/repo``."""
    return re.sub(r"/+", "/", repo.strip().strip("/"))


def extract_github_repo(text: str) -> Optional[str]:
    """Pull ``owner/repo`` from a GitHub URL or bare slug."""
    text = normalize_repo_slug(text) if "://" not in text.strip() else text.strip().rstrip("/")
    if "://" not in text and _SAFE_REPO.match(normalize_repo_slug(text)):
        return normalize_repo_slug(text)
    match = _GITHUB_REPO_URL.search(text)
    if not match:
        return None
    owner = match.group("owner")
    repo = match.group("repo")
    # Drop common trailing path segments that are not the repo name.
    repo = repo.removesuffix(".git")
    return f"{owner}/{repo}"


def extract_gitlab_url(text: str) -> Optional[str]:
    """Return a canonical GitLab project URL when ``text`` contains one."""
    match = _GITLAB_PROJECT_URL.search(text.strip())
    if not match:
        return None
    path = match.group("path").rstrip("/")
    for sep in ("/-/tree/", "/-/blob/", "/-/issues", "/-/merge_requests"):
        if sep in f"/{path}":
            # path has no leading slash; normalize before split
            normalized = f"/{path}"
            path = normalized.split(sep, 1)[0].lstrip("/")
            break
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 3:
        return f"https://gitlab.com/{'/'.join(parts[:3])}"
    if len(parts) >= 2:
        return f"https://gitlab.com/{'/'.join(parts[:2])}"
    return None


def pypi_project_urls(package: str, get: HttpGet) -> dict[str, str]:
    """Return PyPI ``info.project_urls`` plus Home-page for ``package``."""
    response = get(f"https://pypi.org/pypi/{package}/json")
    if response.status_code != 200:
        return {}
    payload = response.json()
    info = payload.get("info") or {}
    urls: dict[str, str] = {}
    project_urls = info.get("project_urls") or {}
    if isinstance(project_urls, dict):
        for key, value in project_urls.items():
            if isinstance(key, str) and isinstance(value, str) and value.strip():
                urls[key] = value.strip()
    home = info.get("home_page")
    if isinstance(home, str) and home.strip():
        urls.setdefault("Home-page", home.strip())
    return urls


def npm_repository_url(package: str, get: HttpGet) -> Optional[str]:
    """Return the npm ``repository.url`` for ``package``, if any."""
    if not package or package == "n/a":
        return None
    encoded = package.replace("/", "%2F")
    response = get(f"https://registry.npmjs.org/{encoded}")
    if response.status_code != 200:
        return None
    payload = response.json()
    repo = payload.get("repository")
    if isinstance(repo, str) and repo.strip():
        return repo.strip()
    if isinstance(repo, dict):
        url = repo.get("url")
        if isinstance(url, str) and url.strip():
            return url.strip().removeprefix("git+").removesuffix(".git")
    return None


def collect_vcs_hits(
    *,
    package_name: str,
    npm: Optional[str],
    docs_urls: list[str],
    get: HttpGet,
) -> list[VcsHit]:
    """Gather VCS candidates from registries and existing docs URLs."""
    hits: list[VcsHit] = []
    seen: set[str] = set()

    def add(hit: VcsHit) -> None:
        key = f"{hit.kind}:{hit.label.casefold()}"
        if key in seen:
            return
        seen.add(key)
        hits.append(hit)

    for label, url in pypi_project_urls(package_name, get).items():
        gh = extract_github_repo(url)
        if gh:
            add(VcsHit("github", gh, f"https://github.com/{gh}", f"pypi:{label}"))
            continue
        gl = extract_gitlab_url(url)
        if gl:
            add(VcsHit("gitlab", gl, gl, f"pypi:{label}"))

    if npm:
        npm_url = npm_repository_url(npm, get)
        if npm_url:
            gh = extract_github_repo(npm_url)
            if gh:
                add(VcsHit("github", gh, f"https://github.com/{gh}", "npm:repository"))
            else:
                gl = extract_gitlab_url(npm_url)
                if gl:
                    add(VcsHit("gitlab", gl, gl, "npm:repository"))

    for docs_url in docs_urls:
        gh = extract_github_repo(docs_url)
        if gh:
            add(
                VcsHit(
                    "github",
                    gh,
                    f"https://github.com/{gh}",
                    "external_docs",
                )
            )
            continue
        gl = extract_gitlab_url(docs_url)
        if gl:
            add(VcsHit("gitlab", gl, gl, "external_docs"))

    return hits



def collect_docs_homes(
    *,
    package_name: str,
    dead_repo: str,
    docs_urls: list[str],
    get: HttpGet,
) -> list[VcsHit]:
    """Gather live partner docs/homepage URLs that are not VCS or registry pages."""
    candidates: list[tuple[str, str]] = []
    for label, url in pypi_project_urls(package_name, get).items():
        candidates.append((url, f"pypi:{label}"))
    for docs_url in docs_urls:
        candidates.append((docs_url, "external_docs"))

    dead_github = f"https://github.com/{dead_repo}".rstrip("/").casefold()
    hits: list[VcsHit] = []
    seen: set[str] = set()
    for url, source in candidates:
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            continue
        if is_registry_page(url) or is_github_or_gitlab_url(url):
            continue
        if url.rstrip("/").casefold() == dead_github:
            continue
        key = url.rstrip("/").casefold()
        if key in seen:
            continue
        if not url_exists(url, get):
            continue
        seen.add(key)
        hits.append(VcsHit("docs", url, url, source))
    return hits


def load_external_docs_urls_by_package(path: Path) -> dict[str, list[str]]:
    """Map PyPI/npm package names to docs_url values from external YAML."""
    yaml = _yaml_loader()
    data = yaml.load(path.read_text(encoding="utf-8")) or {}
    mapping: dict[str, list[str]] = {}
    if not isinstance(data, dict):
        return mapping
    for _language, components in data.items():
        if not isinstance(components, dict):
            continue
        for _component, items in components.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                docs_url = item.get("docs_url")
                if not isinstance(docs_url, str) or not docs_url.strip():
                    continue
                for key_name in ("pypi", "npm"):
                    pkg = item.get(key_name)
                    if isinstance(pkg, str) and pkg.strip():
                        mapping.setdefault(pkg.strip(), []).append(docs_url.strip())
    return mapping


def classify_package(
    pkg: dict[str, Any],
    *,
    docs_urls_by_package: dict[str, list[str]],
    get: HttpGet,
) -> PackageFinding:
    """Decide ok / fix / delist / attention for one packages.yml entry."""
    name = str(pkg["name"])
    raw_repo = str(pkg.get("repo") or "").strip()
    repo = normalize_repo_slug(raw_repo) if raw_repo else raw_repo
    npm_raw = pkg.get("js")
    npm = npm_raw.strip() if isinstance(npm_raw, str) and npm_raw.strip() != "n/a" else None

    if not repo:
        return PackageFinding(
            name=name,
            repo=raw_repo,
            disposition="attention",
            detail="packages.yml has no repo field",
            pypi=name,
            npm=npm,
        )

    if repo.startswith(f"{_FIRST_PARTY_OWNER}/"):
        return PackageFinding(
            name=name,
            repo=repo,
            disposition="skip_first_party",
            detail="first-party langchain-ai package",
            pypi=name,
            npm=npm,
        )

    if not _SAFE_REPO.match(repo):
        return PackageFinding(
            name=name,
            repo=raw_repo,
            disposition="attention",
            detail=f"repo slug is not a valid owner/repo: {raw_repo!r}",
            pypi=name,
            npm=npm,
        )

    try:
        # Treat owner//repo typos as an auto-fix when the normalized slug lives.
        if raw_repo != repo and github_repo_exists(repo, get):
            return PackageFinding(
                name=name,
                repo=raw_repo,
                disposition="fix",
                detail=f"normalized typo {raw_repo!r} to live {repo}",
                new_repo=repo,
                pypi=name,
                npm=npm,
            )
        exists = github_repo_exists(repo, get)
    except requests.RequestException as error:
        return PackageFinding(
            name=name,
            repo=repo,
            disposition="error",
            detail=f"failed to check GitHub: {error}",
            pypi=name,
            npm=npm,
        )

    if exists:
        return PackageFinding(
            name=name,
            repo=repo,
            disposition="ok",
            detail="repo reachable",
            pypi=name,
            npm=npm,
        )

    docs_urls = list(docs_urls_by_package.get(name, []))
    if npm:
        docs_urls.extend(docs_urls_by_package.get(npm, []))

    hits = collect_vcs_hits(
        package_name=name, npm=npm, docs_urls=docs_urls, get=get
    )

    live_github: list[VcsHit] = []
    live_gitlab: list[VcsHit] = []
    first_party_hits: list[VcsHit] = []
    for hit in hits:
        if hit.kind == "github":
            if hit.label.casefold() == repo.casefold():
                continue
            if not github_repo_exists(hit.label, get):
                continue
            if hit.label.startswith(f"{_FIRST_PARTY_OWNER}/"):
                first_party_hits.append(hit)
                continue
            live_github.append(hit)
        elif hit.kind == "gitlab":
            if url_exists(hit.url, get):
                live_gitlab.append(hit)

    if live_github:
        chosen = live_github[0]
        return PackageFinding(
            name=name,
            repo=raw_repo if raw_repo != repo else repo,
            disposition="fix",
            detail=f"PyPI/npm/docs point at live {chosen.label} ({chosen.source})",
            new_repo=chosen.label,
            pypi=name,
            npm=npm,
        )

    if live_gitlab:
        chosen = live_gitlab[0]
        return PackageFinding(
            name=name,
            repo=repo,
            disposition="attention",
            detail=(
                f"GitHub {repo} is 404 but a live GitLab project remains "
                f"at {chosen.url} ({chosen.source}); not delisting"
            ),
            pypi=name,
            npm=npm,
        )

    if first_party_hits:
        chosen = first_party_hits[0]
        return PackageFinding(
            name=name,
            repo=repo,
            disposition="attention",
            detail=(
                f"GitHub {repo} is 404; PyPI/npm/docs point at first-party "
                f"{chosen.label} ({chosen.source}), which this checker does "
                "not auto-adopt"
            ),
            pypi=name,
            npm=npm,
        )

    live_docs = collect_docs_homes(
        package_name=name,
        dead_repo=repo,
        docs_urls=docs_urls,
        get=get,
    )
    if live_docs:
        chosen = live_docs[0]
        return PackageFinding(
            name=name,
            repo=repo,
            disposition="attention",
            detail=(
                f"GitHub {repo} is 404 but live partner docs remain at "
                f"{chosen.url} ({chosen.source}); not delisting"
            ),
            pypi=name,
            npm=npm,
        )

    return PackageFinding(
        name=name,
        repo=repo,
        disposition="delist",
        detail=(
            f"GitHub {repo} is 404 and no live GitHub, GitLab, or partner-docs "
            "alternate was found on PyPI, npm, or external docs_url values"
        ),
        pypi=name,
        npm=npm,
        removed_docs_urls=sorted(set(docs_urls)),
    )


def scan_packages(
    packages: list[dict[str, Any]],
    *,
    docs_urls_by_package: dict[str, list[str]],
    get: HttpGet,
    sleep_s: float = 0.0,
) -> list[PackageFinding]:
    """Classify every package in ``packages.yml``."""
    findings: list[PackageFinding] = []
    for pkg in packages:
        if not isinstance(pkg, dict) or "name" not in pkg:
            continue
        findings.append(
            classify_package(
                pkg,
                docs_urls_by_package=docs_urls_by_package,
                get=get,
            )
        )
        if sleep_s:
            time.sleep(sleep_s)
    return findings


def apply_repo_fixes(
    packages: list[dict[str, Any]], findings: list[PackageFinding]
) -> list[tuple[str, str, str]]:
    """Update ``repo`` fields in-place. Returns (name, old, new) triples."""
    by_name = {f.name: f for f in findings if f.disposition == "fix" and f.new_repo}
    changes: list[tuple[str, str, str]] = []
    for pkg in packages:
        finding = by_name.get(str(pkg.get("name")))
        if not finding or not finding.new_repo:
            continue
        old = str(pkg.get("repo"))
        pkg["repo"] = finding.new_repo
        changes.append((finding.name, old, finding.new_repo))
    return changes


def remove_packages(
    packages: list[dict[str, Any]], names: set[str]
) -> list[dict[str, Any]]:
    """Return packages with ``names`` removed."""
    return [pkg for pkg in packages if str(pkg.get("name")) not in names]


def remove_external_entries(
    data: dict[str, Any], *, pypi_names: set[str], npm_names: set[str]
) -> list[tuple[str, str, str]]:
    """Drop external YAML rows for the given packages. Returns removals."""
    removed: list[tuple[str, str, str]] = []
    for language, components in list(data.items()):
        if not isinstance(components, dict):
            continue
        for component, items in list(components.items()):
            if not isinstance(items, list):
                continue
            kept = []
            for item in items:
                if not isinstance(item, dict):
                    kept.append(item)
                    continue
                pypi = item.get("pypi")
                npm = item.get("npm")
                drop = (isinstance(pypi, str) and pypi in pypi_names) or (
                    isinstance(npm, str) and npm in npm_names
                )
                if drop:
                    removed.append(
                        (str(language), str(component), str(item.get("name") or "?"))
                    )
                else:
                    kept.append(item)
            components[component] = kept
    return removed


def rewrite_github_urls(text: str, replacements: dict[str, str]) -> str:
    """Replace ``https://github.com/old`` with new repo URLs."""
    updated = text
    for old_repo, new_repo in replacements.items():
        old_url = f"https://github.com/{old_repo}"
        new_url = f"https://github.com/{new_repo}"
        updated = updated.replace(old_url, new_url)
        # Handle accidental double-slash typos in older listings.
        updated = updated.replace(
            f"https://github.com/{old_repo.replace('/', '//')}", new_url
        )
    return updated


def remove_downloads_rows(text: str, package_markers: set[str]) -> tuple[str, int]:
    """Remove markdown table rows that reference any marker substring."""
    if not package_markers:
        return text, 0
    kept: list[str] = []
    removed = 0
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("|") and any(marker in line for marker in package_markers):
            removed += 1
            continue
        kept.append(line)
    return "".join(kept), removed


def _card_title(card: str) -> Optional[str]:
    match = re.search(r'\btitle="([^"]+)"', card)
    return match.group(1) if match else None


def _card_href(card: str) -> Optional[str]:
    match = re.search(r'\bhref="([^"]+)"', card)
    return match.group(1) if match else None


def remove_provider_cards(
    text: str,
    *,
    delisted: list[PackageFinding],
    remaining_provider_keys: set[str],
) -> tuple[str, list[str]]:
    """Remove all_providers cards for delisted providers with no survivors."""

    def should_drop(card: str) -> bool:
        title = _card_title(card)
        href = _card_href(card)
        href_norm = href.rstrip("/") if href else None
        for finding in delisted:
            key = provider_key(finding.name)
            if key in remaining_provider_keys:
                continue
            urls = {url.rstrip("/") for url in finding.removed_docs_urls}
            urls.add(f"https://github.com/{finding.repo}".rstrip("/"))
            if href_norm and href_norm in urls:
                return True
            if not title:
                continue
            short = name_short(finding.name).casefold()
            title_folded = title.casefold()
            if title_folded == short or title_folded.replace(" ", "-") == short:
                return True
            if title_folded.replace(" ", "") == short.replace("-", ""):
                return True
        return False

    out: list[str] = []
    removed_titles: list[str] = []
    last = 0
    for match in _CARD_RE.finditer(text):
        out.append(text[last : match.start()])
        card = match.group(0)
        if should_drop(card):
            removed_titles.append(_card_title(card) or "?")
        else:
            out.append(card)
        last = match.end()
    out.append(text[last:])
    return "".join(out), removed_titles


def render_evidence(findings: list[PackageFinding]) -> str:
    """Build the markdown evidence table for the draft PR body."""
    lines = [
        "## Integration repo check",
        "",
        "Automated scan of `packages.yml` `repo:` values. First-party "
        "`langchain-ai/*` packages are skipped. Draft only; maintainers review "
        "before merge.",
        "",
    ]

    fixes = [f for f in findings if f.disposition == "fix"]
    delists = [f for f in findings if f.disposition == "delist"]
    attention = [f for f in findings if f.disposition == "attention"]
    errors = [f for f in findings if f.disposition == "error"]

    if fixes:
        lines.extend(
            [
                "### Repo renames applied",
                "",
                "| Package | Old repo | New repo | Notes |",
                "| --- | --- | --- | --- |",
            ]
        )
        for finding in fixes:
            lines.append(
                f"| `{finding.name}` | `{finding.repo}` | `{finding.new_repo}` | "
                f"{finding.detail} |"
            )
        lines.append("")

    if delists:
        lines.extend(
            [
                "### Full delist (no live VCS alternate)",
                "",
                "| Package | Dead repo | Notes |",
                "| --- | --- | --- |",
            ]
        )
        for finding in delists:
            lines.append(
                f"| `{finding.name}` | `{finding.repo}` | {finding.detail} |"
            )
        lines.append("")

    if attention:
        lines.extend(
            [
                "### Needs attention (not changed)",
                "",
                "| Package | Repo | Notes |",
                "| --- | --- | --- |",
            ]
        )
        for finding in attention:
            lines.append(
                f"| `{finding.name}` | `{finding.repo}` | {finding.detail} |"
            )
        lines.append("")

    if errors:
        lines.extend(
            [
                "### Check errors",
                "",
                "| Package | Repo | Notes |",
                "| --- | --- | --- |",
            ]
        )
        for finding in errors:
            lines.append(
                f"| `{finding.name}` | `{finding.repo}` | {finding.detail} |"
            )
        lines.append("")

    if not fixes and not delists and not attention and not errors:
        lines.append("No broken third-party repo links found.")
        lines.append("")

    lines.extend(
        [
            "### Policy",
            "",
            "- Auto-fix when PyPI, npm, or an existing `docs_url` points at a "
            "different live third-party GitHub repository.",
            "- Delist when the recorded GitHub repo is gone and no live "
            "GitHub/GitLab alternate is found (marketing docs sites do not count).",
            "- Leave alone (attention) when a live GitLab project remains, or "
            "when the only alternate is a first-party `langchain-ai/*` repo.",
            "- Remove the `all_providers` card only when no other package shares "
            "the provider key (`name_short`).",
            "",
            "Generated by `scripts/check_integration_repos.py` / "
            "`.github/workflows/check-integration-repos.yml`.",
            "",
        ]
    )
    return "\n".join(lines)


def apply_changes(
    *,
    repo_root: Path,
    findings: list[PackageFinding],
    write: bool,
) -> dict[str, Any]:
    """Apply fix/delist mutations when ``write`` is true."""
    yaml = _yaml_loader()
    packages_path = repo_root / "packages.yml"
    external_path = repo_root / "scripts" / "data" / "integration_external_docs.yaml"
    all_providers_path = (
        repo_root
        / "src"
        / "oss"
        / "python"
        / "integrations"
        / "providers"
        / "all_providers.mdx"
    )

    packages_data = yaml.load(packages_path.read_text(encoding="utf-8"))
    packages = list(packages_data.get("packages") or [])

    summary: dict[str, Any] = {
        "fixes": [],
        "delisted": [],
        "external_removed": [],
        "downloads_rows_removed": 0,
        "cards_removed": [],
        "files_changed": [],
    }

    fixes = apply_repo_fixes(packages, findings)
    summary["fixes"] = [
        {"name": name, "old": old, "new": new} for name, old, new in fixes
    ]
    repo_replacements = {old: new for _name, old, new in fixes}

    delist_findings = [f for f in findings if f.disposition == "delist"]
    delist_names = {f.name for f in delist_findings}
    packages = remove_packages(packages, delist_names)
    summary["delisted"] = sorted(delist_names)

    remaining_keys = {provider_key(str(pkg["name"])) for pkg in packages if "name" in pkg}

    packages_data["packages"] = packages

    external_data = yaml.load(external_path.read_text(encoding="utf-8")) or {}
    pypi_names = set(delist_names)
    npm_names = {f.npm for f in delist_findings if f.npm}
    external_removed = remove_external_entries(
        external_data, pypi_names=pypi_names, npm_names=npm_names
    )
    summary["external_removed"] = [
        {"language": lang, "component": comp, "name": name}
        for lang, comp, name in external_removed
    ]

    providers_text = all_providers_path.read_text(encoding="utf-8")
    if repo_replacements:
        providers_text = rewrite_github_urls(providers_text, repo_replacements)
    providers_text, cards = remove_provider_cards(
        providers_text,
        delisted=delist_findings,
        remaining_provider_keys=remaining_keys,
    )
    summary["cards_removed"] = cards

    markers: set[str] = set()
    for finding in delist_findings:
        markers.add(f"pypi.org/project/{finding.name}")
        markers.add(f"pepy.tech/badge/{finding.name}")
        if finding.npm:
            markers.add(f"npmjs.com/package/{finding.npm}")
            markers.add(f"npm/dm/{finding.npm}")
        markers.add(f"github.com/{finding.repo}")

    downloads_removed = 0
    downloads_updates: list[tuple[Path, str]] = []
    for path in sorted((repo_root / "src" / "snippets" / "oss").glob("*-downloads.mdx")):
        original = path.read_text(encoding="utf-8")
        updated = (
            rewrite_github_urls(original, repo_replacements)
            if repo_replacements
            else original
        )
        updated, count = remove_downloads_rows(updated, markers)
        downloads_removed += count
        if updated != original:
            downloads_updates.append((path, updated))
    summary["downloads_rows_removed"] = downloads_removed

    original_providers = all_providers_path.read_text(encoding="utf-8")
    providers_changed = providers_text != original_providers
    packages_changed = bool(fixes or delist_names)
    external_changed = bool(external_removed)

    if write and (
        packages_changed or external_changed or providers_changed or downloads_updates
    ):
        if packages_changed:
            with packages_path.open("w", encoding="utf-8") as handle:
                yaml.dump(packages_data, handle)
            summary["files_changed"].append("packages.yml")
        if external_changed:
            with external_path.open("w", encoding="utf-8") as handle:
                yaml.dump(external_data, handle)
            summary["files_changed"].append(
                "scripts/data/integration_external_docs.yaml"
            )
        if providers_changed:
            all_providers_path.write_text(providers_text, encoding="utf-8")
            summary["files_changed"].append(
                str(all_providers_path.relative_to(repo_root))
            )
        for path, content in downloads_updates:
            path.write_text(content, encoding="utf-8")
            summary["files_changed"].append(str(path.relative_to(repo_root)))

    summary["files_changed"] = sorted(set(summary["files_changed"]))
    return summary


def run(
    *,
    repo_root: Path = _REPO_ROOT,
    write: bool = False,
    evidence_path: Optional[Path] = None,
    get: Optional[HttpGet] = None,
    token: Optional[str] = None,
    sleep_s: float = 0.05,
) -> int:
    """Scan and optionally apply changes. Returns process exit code."""
    token = token if token is not None else (
        os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    )
    get = get or make_http_get(token)

    yaml = _yaml_loader()
    packages_data = yaml.load((repo_root / "packages.yml").read_text(encoding="utf-8"))
    packages = list(packages_data.get("packages") or [])
    docs_map = load_external_docs_urls_by_package(
        repo_root / "scripts" / "data" / "integration_external_docs.yaml"
    )

    findings = scan_packages(
        packages,
        docs_urls_by_package=docs_map,
        get=get,
        sleep_s=sleep_s,
    )
    evidence = render_evidence(findings)
    if evidence_path:
        evidence_path.write_text(evidence, encoding="utf-8")

    actionable = [f for f in findings if f.disposition in {"fix", "delist"}]
    print(evidence)
    if not actionable:
        return 0

    summary = apply_changes(repo_root=repo_root, findings=findings, write=write)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not write:
        print(
            "Dry-run only. Re-run with --write to apply fix/delist changes.",
            file=sys.stderr,
        )
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply repo fixes and delists to the working tree",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        help="Write the markdown evidence report to this path",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_REPO_ROOT,
        help="Repository root (default: detected from script location)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.05,
        help="Delay between GitHub checks to ease rate limits",
    )
    args = parser.parse_args(argv)
    return run(
        repo_root=args.repo_root.resolve(),
        write=args.write,
        evidence_path=args.evidence,
        sleep_s=args.sleep,
    )


if __name__ == "__main__":
    raise SystemExit(main())
