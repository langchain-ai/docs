"""Tests for the mirrored external version checker."""

import json
from pathlib import Path

import pytest
import yaml

from scripts import check_external_versions as checker

CODEX_LINE = (
    "- [Codex CLI](https://developers.openai.com/codex/quickstart?setup=cli) "
    "v0.128 or later, with synchronous `UserPromptSubmit` plugin hooks enabled.\n"
)
CODEX_PATTERN = r"Codex CLI\]\([^)]*\) v(?P<version>[0-9][0-9a-zA-Z.]*) or later"


def write_registry(tmp_path: Path, entries: list[dict[str, object]]) -> Path:
    """Write a registry file holding `entries`."""
    path = tmp_path / "external_versions.yaml"
    path.write_text(yaml.safe_dump(entries), encoding="utf-8")
    return path


def codex_source(**overrides: str) -> dict[str, str]:
    """Build the upstream source block, with any field replaced."""
    return {
        "type": "github_file",
        "repo": "langchain-ai/langsmith-codex-plugins",
        "path": "README.md",
        "pattern": r"Codex >= (?P<version>[0-9][0-9a-zA-Z.]*)",
        **overrides,
    }


def codex_entry(
    page: str = "src/langsmith/trace-with-codex.mdx",
    pattern: str = CODEX_PATTERN,
    source: dict[str, str] | None = None,
) -> dict[str, object]:
    """Build the Codex CLI registry entry used across these tests."""
    return {
        "id": "codex-cli",
        "label": "Codex CLI",
        "page": page,
        "pattern": pattern,
        "source": codex_source() if source is None else source,
    }


@pytest.fixture
def docs_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A minimal repo root with the Codex page in place."""
    page = tmp_path / "src" / "langsmith" / "trace-with-codex.mdx"
    page.parent.mkdir(parents=True)
    page.write_text(CODEX_LINE, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_documented_version_reads_the_page(docs_tree: Path) -> None:
    """The page pattern extracts the version the docs currently claim."""
    entry = checker.load_registry(write_registry(docs_tree, [codex_entry()]))[0]
    found = checker.documented_version(entry, CODEX_LINE)
    assert found is not None
    assert found[0] == "0.128"


def test_rewrite_replaces_only_the_captured_digits(docs_tree: Path) -> None:
    """A rewrite touches the version and nothing else on the line."""
    entry = checker.load_registry(write_registry(docs_tree, [codex_entry()]))[0]
    found = checker.documented_version(entry, CODEX_LINE)
    assert found is not None
    updated = checker.rewrite(CODEX_LINE, found[1], "0.153.4")
    assert "v0.153.4 or later" in updated
    # The rest of the requirement is untouched.
    assert "synchronous `UserPromptSubmit` plugin hooks enabled" in updated
    assert "https://developers.openai.com/codex/quickstart?setup=cli" in updated


def test_ambiguous_pattern_is_not_rewritten(docs_tree: Path) -> None:
    """A pattern matching twice is reported, never guessed at."""
    entry = checker.load_registry(write_registry(docs_tree, [codex_entry()]))[0]
    assert checker.documented_version(entry, CODEX_LINE * 2) is None


def test_missing_pattern_is_reported(docs_tree: Path) -> None:
    """A pattern that matches nothing is reported, not treated as in sync."""
    entry = checker.load_registry(write_registry(docs_tree, [codex_entry()]))[0]
    assert checker.documented_version(entry, "no version here") is None


def test_page_outside_src_is_refused(docs_tree: Path) -> None:
    """A registry page path may not escape the docs tree."""
    registry = write_registry(docs_tree, [codex_entry(page="../../etc/passwd")])
    with pytest.raises(checker.RegistryError, match="outside"):
        checker.load_registry(registry)


def test_absolute_page_is_refused(docs_tree: Path) -> None:
    """A registry page path must be relative to the repository root."""
    registry = write_registry(docs_tree, [codex_entry(page="/etc/passwd")])
    with pytest.raises(checker.RegistryError, match="relative"):
        checker.load_registry(registry)


def test_bad_repo_slug_is_refused(docs_tree: Path) -> None:
    """A repo slug is checked before it reaches a request URL."""
    entry = codex_entry(source=codex_source(repo="langchain-ai/repo/../../evil"))
    with pytest.raises(checker.RegistryError, match="repo slug"):
        checker.load_registry(write_registry(docs_tree, [entry]))


def test_traversal_in_source_path_is_refused(docs_tree: Path) -> None:
    """A traversal in the upstream file path is refused."""
    entry = codex_entry(source=codex_source(path="docs/../../../secrets"))
    with pytest.raises(checker.RegistryError, match="source path"):
        checker.load_registry(write_registry(docs_tree, [entry]))


def test_pattern_without_a_version_group_is_refused(docs_tree: Path) -> None:
    """Without a `version` group there is nothing to compare or rewrite."""
    entry = codex_entry(pattern=r"Codex CLI v[0-9.]+")
    with pytest.raises(checker.RegistryError, match="`version` named group"):
        checker.load_registry(write_registry(docs_tree, [entry]))


def test_unknown_source_type_is_refused(docs_tree: Path) -> None:
    """Only the supported upstream source types are accepted."""
    entry = codex_entry(source=codex_source(type="ftp"))
    with pytest.raises(checker.RegistryError, match="unknown source type"):
        checker.load_registry(write_registry(docs_tree, [entry]))


def test_upstream_version_from_a_file(
    docs_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A README states the requirement the docs mirror."""
    readme = "## Prerequisites\n\n- Node.js >= 22.x\n- Codex >= 0.153.4 with hooks\n"
    monkeypatch.setattr(checker, "_get", lambda url, *, accept: readme)
    entry = checker.load_registry(write_registry(docs_tree, [codex_entry()]))[0]
    assert checker.upstream_version(entry.source) == "0.153.4"


def test_unreachable_upstream_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """A GitHub outage must not be reported as drift."""

    def fail(url: str, *, accept: str) -> str:
        raise TimeoutError

    monkeypatch.setattr(checker, "_get", fail)
    source = {"type": "github_release", "repo": "langchain-ai/helm"}
    assert checker.upstream_version(source) is None


def test_main_reports_drift_and_writes(
    docs_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """End to end over the bug that prompted this check."""
    registry = write_registry(docs_tree, [codex_entry()])
    readme = "- Codex >= 0.153.4 with synchronous hooks\n"
    monkeypatch.setattr(checker, "_get", lambda url, *, accept: readme)
    monkeypatch.setattr(
        "sys.argv",
        ["check_external_versions.py", "--registry", str(registry)],
    )

    assert checker.main() == 1
    assert "docs say 0.128" in capsys.readouterr().out

    monkeypatch.setattr(
        "sys.argv",
        ["check_external_versions.py", "--registry", str(registry), "--write"],
    )
    assert checker.main() == 0
    page = docs_tree / "src" / "langsmith" / "trace-with-codex.mdx"
    assert "v0.153.4 or later" in page.read_text(encoding="utf-8")


def test_main_is_quiet_when_in_sync(
    docs_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A matching version reports success and changes nothing."""
    page = docs_tree / "src" / "langsmith" / "trace-with-codex.mdx"
    page.write_text(CODEX_LINE.replace("v0.128", "v0.153.4"), encoding="utf-8")
    registry = write_registry(docs_tree, [codex_entry()])
    monkeypatch.setattr(checker, "_get", lambda url, *, accept: "- Codex >= 0.153.4\n")
    monkeypatch.setattr(
        "sys.argv",
        ["check_external_versions.py", "--registry", str(registry)],
    )
    assert checker.main() == 0
    assert "1 in sync, 0 drifted" in capsys.readouterr().out


def test_committed_registry_is_valid() -> None:
    """The real registry must always parse; a broken entry fails CI here."""
    entries = checker.load_registry(checker.REGISTRY)
    assert entries, "registry should not be empty"
    for entry in entries:
        assert entry.page.exists(), f"{entry.id} names a missing page {entry.page}"
        text = entry.page.read_text(encoding="utf-8")
        assert checker.documented_version(entry, text) is not None, (
            f"{entry.id}: pattern does not match exactly once in {entry.page}"
        )


def test_write_mode_does_not_fail_on_an_unreachable_upstream(
    docs_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A GitHub outage must not stop the weekly job before it opens its PR."""

    def fail(url: str, *, accept: str) -> str:
        raise TimeoutError

    registry = write_registry(docs_tree, [codex_entry()])
    monkeypatch.setattr(checker, "_get", fail)
    monkeypatch.setattr(
        "sys.argv",
        ["check_external_versions.py", "--registry", str(registry), "--write"],
    )
    assert checker.main() == 0


def test_check_mode_fails_on_an_unreadable_entry(
    docs_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without --write, an entry that cannot be checked is a failure."""

    def fail(url: str, *, accept: str) -> str:
        raise TimeoutError

    registry = write_registry(docs_tree, [codex_entry()])
    monkeypatch.setattr(checker, "_get", fail)
    monkeypatch.setattr(
        "sys.argv",
        ["check_external_versions.py", "--registry", str(registry)],
    )
    assert checker.main() == 1


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("v1.2.3", "1.2.3"),
        ("1.2.3", "1.2.3"),
        # One `v` is a prefix; a second is part of the tag. `lstrip("v")` would
        # eat both.
        ("vv1.2.3", "v1.2.3"),
    ],
)
def test_release_tag_drops_only_a_v_prefix(
    monkeypatch: pytest.MonkeyPatch,
    tag: str,
    expected: str,
) -> None:
    """Exactly one leading `v` is a prefix, not every leading `v` character."""
    monkeypatch.setattr(
        checker,
        "_get",
        lambda url, *, accept: json.dumps({"tag_name": tag}),
    )
    source = {"type": "github_release", "repo": "langchain-ai/helm"}
    assert checker.upstream_version(source) == expected
