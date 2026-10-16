"""Report outdated model IDs in LangSmith's in-product onboarding snippets.

Reads the snippet files named in ``scripts/data/onboarding_models.yaml`` and
reports each model ID not listed as current for its provider. Never edits them.

    uv run python scripts/check_onboarding_models.py
    uv run python scripts/check_onboarding_models.py --repo-dir ../langchainplus

Reading over the API needs ``GITHUB_TOKEN`` or ``GH_TOKEN`` with read access to
langchainplus. Exits 0 if all current, 1 if any are outdated, 2 if unreadable.
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

REGISTRY = Path("scripts/data/onboarding_models.yaml")

# Only slugs and paths matching these are interpolated into a request URL.
SAFE_REPO = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,60}/[A-Za-z0-9][A-Za-z0-9._-]{0,60}$"
)
SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,100}$")
SAFE_REPO_PATH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,300}$")

REQUEST_TIMEOUT = 30

# Claude IDs need a digit after the family name, which keeps package and
# product names such as `claude-agent-sdk` and `claude-code` out. The bare
# OpenAI o-series needs a quote, colon, or slash before it, so prose such as
# "o3" in a sentence is not read as a model.
MODEL_ID = re.compile(
    r"(?<![\w.-])"
    r"(?P<id>gpt-[0-9][\w.-]*"
    r"|claude-(?:[a-z]+-)?[0-9][\w.-]*"
    r"|gemini-[0-9][\w.-]*)"
    r"|(?<=[\"'`:/])(?P<oseries>o[0-9](?:-mini|-pro)?)(?=[\"'`])"
)

PROVIDER_PREFIXES = (
    ("openai", ("gpt-", "o")),
    ("anthropic", ("claude-",)),
    ("google", ("gemini-",)),
)

# A dated snapshot of a listed model, such as `claude-haiku-4-5-20251001`.
SNAPSHOT_SUFFIX = re.compile(r"^-20[0-9]{2}-?[0-9]{2}-?[0-9]{2}$")


class RegistryError(Exception):
    """The registry file cannot be acted on."""


@dataclass(frozen=True)
class Provider:
    """The model IDs one provider's snippets may use."""

    name: str
    preferred: str
    current: tuple[str, ...]


@dataclass(frozen=True)
class Registry:
    """The parsed registry file."""

    repo: str
    ref: str
    paths: tuple[str, ...]
    providers: dict[str, Provider]
    ignore: frozenset[str]


@dataclass(frozen=True)
class Finding:
    """One outdated model ID in one snippet line."""

    path: str
    line: int
    model: str
    provider: str
    suggestion: str


def load_registry(path: Path) -> Registry:
    """Parse and validate the registry file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    try:
        source = data["source"]
        repo, ref, paths = source["repo"], source["ref"], source["paths"]
        raw_providers = data["providers"]
    except (KeyError, TypeError) as error:
        msg = f"{path}: missing required field {error}"
        raise RegistryError(msg) from error

    if not SAFE_REPO.match(repo):
        msg = f"{path}: unsafe repo slug {repo!r}"
        raise RegistryError(msg)
    if not SAFE_REF.match(ref):
        msg = f"{path}: unsafe ref {ref!r}"
        raise RegistryError(msg)
    for repo_path in paths:
        if not SAFE_REPO_PATH.match(repo_path) or ".." in repo_path.split("/"):
            msg = f"{path}: unsafe source path {repo_path!r}"
            raise RegistryError(msg)

    known = {name for name, _ in PROVIDER_PREFIXES}
    providers: dict[str, Provider] = {}
    for name, entry in raw_providers.items():
        if name not in known:
            msg = f"{path}: unknown provider {name!r}, expected one of {sorted(known)}"
            raise RegistryError(msg)
        current = tuple(entry["current"])
        if entry["preferred"] not in current:
            msg = f"{path}: {name} preferred model {entry['preferred']!r} is not in current"
            raise RegistryError(msg)
        providers[name] = Provider(name, entry["preferred"], current)

    return Registry(
        repo=repo,
        ref=ref,
        paths=tuple(paths),
        providers=providers,
        ignore=frozenset(data.get("ignore") or ()),
    )


def provider_for(model: str) -> str | None:
    """Return the provider a model ID belongs to, or None."""
    for name, prefixes in PROVIDER_PREFIXES:
        if any(model.startswith(prefix) for prefix in prefixes):
            return name
    return None


def is_current(model: str, provider: Provider) -> bool:
    """Whether a model ID is a listed current model or a dated snapshot of one."""
    for listed in provider.current:
        if model == listed:
            return True
        if model.startswith(listed) and SNAPSHOT_SUFFIX.match(model[len(listed) :]):
            return True
    return False


def find_outdated(path: str, text: str, registry: Registry) -> list[Finding]:
    """Return every outdated model ID in one file's text."""
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in MODEL_ID.finditer(line):
            model = (match.group("id") or match.group("oseries")).rstrip(".-")
            if model in registry.ignore:
                continue
            name = provider_for(model)
            provider = registry.providers.get(name) if name else None
            if provider is None or is_current(model, provider):
                continue
            findings.append(
                Finding(path, line_number, model, provider.name, provider.preferred)
            )
    return findings


def in_scope(repo_path: str, paths: tuple[str, ...]) -> bool:
    """Whether a repository file falls under one of the registry paths."""
    return any(
        repo_path.startswith(prefix) if prefix.endswith("/") else repo_path == prefix
        for prefix in paths
    )


def _get(url: str, *, accept: str) -> str:
    headers = {"User-Agent": "langchain-docs-onboarding-models/1.0", "Accept": accept}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)  # noqa: S310 - https literal
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:  # noqa: S310
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset)


def read_remote(registry: Registry) -> dict[str, str]:
    """Fetch the in-scope files from GitHub, keyed by repository path."""
    ref = urllib.parse.quote(registry.ref, safe="")
    tree = json.loads(
        _get(
            f"https://api.github.com/repos/{registry.repo}/git/trees/{ref}?recursive=1",
            accept="application/vnd.github+json",
        )
    )
    files: dict[str, str] = {}
    for item in tree.get("tree", []):
        repo_path = item.get("path", "")
        if item.get("type") != "blob" or not in_scope(repo_path, registry.paths):
            continue
        if not SAFE_REPO_PATH.match(repo_path):
            continue
        files[repo_path] = _get(
            f"https://api.github.com/repos/{registry.repo}/contents/"
            f"{urllib.parse.quote(repo_path)}?ref={ref}",
            accept="application/vnd.github.raw",
        )
    return files


def read_local(registry: Registry, repo_dir: Path) -> dict[str, str]:
    """Read the in-scope files from a local checkout, keyed by repository path."""
    root = repo_dir.resolve()
    files: dict[str, str] = {}
    for file in sorted(root.rglob("*")):
        resolved = file.resolve()
        if not file.is_file() or not resolved.is_relative_to(root):
            continue
        repo_path = file.relative_to(root).as_posix()
        if in_scope(repo_path, registry.paths):
            files[repo_path] = resolved.read_text(encoding="utf-8", errors="replace")
    return files


def render(findings: list[Finding], registry: Registry, file_count: int) -> str:
    """Render the findings as a Markdown report."""
    base = f"https://github.com/{registry.repo}/blob/{registry.ref}"
    if not findings:
        return (
            f"All model IDs in {file_count} onboarding snippet files in "
            f"`{registry.repo}` are current.\n"
        )
    lines = [
        f"{len(findings)} outdated model IDs in the LangSmith onboarding snippets "
        f"(`{registry.repo}`, {file_count} files checked).",
        "",
        "| Snippet | Model | Suggested |",
        "|---------|-------|-----------|",
    ]
    lines.extend(
        f"| [{finding.path}:{finding.line}]({base}/{finding.path}#L{finding.line}) "
        f"| `{finding.model}` | `{finding.suggestion}` |"
        for finding in findings
    )
    lines += [
        "",
        "The suggestions come from `scripts/data/onboarding_models.yaml` in "
        "langchain-ai/docs. If a snippet pins a model on purpose, add it to "
        "`ignore` there.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report outdated model IDs in LangSmith onboarding snippets."
    )
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument(
        "--repo-dir",
        type=Path,
        help="Read the snippets from a local checkout instead of the GitHub API.",
    )
    parser.add_argument("--output", type=Path, help="Also write the report here.")
    args = parser.parse_args(argv)

    try:
        registry = load_registry(args.registry)
    except RegistryError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    try:
        files = (
            read_local(registry, args.repo_dir)
            if args.repo_dir
            else read_remote(registry)
        )
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
        print(f"error: could not read {registry.repo}: {error}", file=sys.stderr)
        return 2
    if not files:
        print(f"error: no files in {registry.repo} match source.paths", file=sys.stderr)
        return 2

    findings = [
        finding
        for path, text in sorted(files.items())
        for finding in find_outdated(path, text, registry)
    ]
    report = render(findings, registry, len(files))
    print(report, end="")
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
