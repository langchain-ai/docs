"""Tests for the onboarding snippet model checker."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts import check_onboarding_models as checker

REGISTRY: dict[str, Any] = {
    "source": {
        "repo": "langchain-ai/langchainplus",
        "ref": "main",
        "paths": ["web/snippets/", "web/constants.tsx"],
    },
    "providers": {
        "openai": {"preferred": "gpt-6-luna", "current": ["gpt-6-luna", "o3-mini"]},
        "anthropic": {
            "preferred": "claude-sonnet-4-6",
            "current": ["claude-sonnet-4-6", "claude-haiku-4-5"],
        },
        "google": {"preferred": "gemini-3.7-flash", "current": ["gemini-3.7-flash"]},
    },
    "ignore": ["gpt-4o-mini-transcribe"],
}


def write_registry(tmp_path: Path, data: dict[str, Any] = REGISTRY) -> Path:
    """Write a registry file holding `data`."""
    path = tmp_path / "onboarding_models.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


@pytest.fixture
def registry(tmp_path: Path) -> checker.Registry:
    """Load the sample registry."""
    return checker.load_registry(write_registry(tmp_path))


def models(text: str, registry: checker.Registry) -> list[str]:
    """Return the outdated model IDs found in `text`."""
    return [f.model for f in checker.find_outdated("f.md", text, registry)]


def test_flags_outdated_ids_with_provider_prefixes(registry: checker.Registry) -> None:
    """Flags outdated ids with provider prefixes."""
    text = 'model="gpt-4o-mini"\nmodel: "openai:gpt-5-mini"\nllm="openai/gpt-4o"\n'
    assert models(text, registry) == ["gpt-4o-mini", "gpt-5-mini", "gpt-4o"]


def test_current_ids_and_dated_snapshots_pass(registry: checker.Registry) -> None:
    """Current ids and dated snapshots pass."""
    text = (
        'model="gpt-6-luna"\n'
        'model="claude-haiku-4-5-20251001"\n'
        'model="openai:o3-mini"\n'
        'model="gemini-3.7-flash"\n'
    )
    assert models(text, registry) == []


def test_snapshot_rule_does_not_pass_a_different_model(
    registry: checker.Registry,
) -> None:
    """Snapshot rule does not pass a different model."""
    # `claude-sonnet-4-6` is current, but a longer ID is not a snapshot of it.
    assert models('model="claude-sonnet-4-6-preview"', registry) == [
        "claude-sonnet-4-6-preview"
    ]


def test_ignores_non_models_and_listed_ignores(registry: checker.Registry) -> None:
    """Ignores non models and listed ignores."""
    text = (
        "pip install claude-agent-sdk\n"
        "npx claude-code\n"
        'stt="openai/gpt-4o-mini-transcribe"\n'
        "Compare o3 with other models in this sentence.\n"
    )
    assert models(text, registry) == []


def test_flags_quoted_o_series(registry: checker.Registry) -> None:
    """Flags quoted o series."""
    assert models('model="o1"\nmodel: "openai:o3-mini"', registry) == ["o1"]


def test_findings_carry_line_and_suggestion(registry: checker.Registry) -> None:
    """Findings carry line and suggestion."""
    [finding] = checker.find_outdated(
        "web/snippets/anthropic.md", 'x\nmodel="claude-sonnet-4-5-20250929"\n', registry
    )
    assert finding.line == 2
    assert finding.provider == "anthropic"
    assert finding.suggestion == "claude-sonnet-4-6"


def test_trailing_sentence_punctuation_is_not_part_of_the_id(
    registry: checker.Registry,
) -> None:
    """Trailing sentence punctuation is not part of the id."""
    assert models("This uses gpt-4o.", registry) == ["gpt-4o"]


def test_in_scope_matches_prefixes_and_exact_files() -> None:
    """In scope matches prefixes and exact files."""
    paths = ("web/snippets/", "web/constants.tsx")
    assert checker.in_scope("web/snippets/openai.md", paths)
    assert checker.in_scope("web/constants.tsx", paths)
    assert not checker.in_scope("web/constants.tsx.bak", paths)
    assert not checker.in_scope("web/other/openai.md", paths)


def test_registry_rejects_preferred_not_in_current(tmp_path: Path) -> None:
    """Registry rejects preferred not in current."""
    data = yaml.safe_load(yaml.safe_dump(REGISTRY))
    data["providers"]["openai"]["preferred"] = "gpt-7"
    with pytest.raises(checker.RegistryError, match="not in current"):
        checker.load_registry(write_registry(tmp_path, data))


@pytest.mark.parametrize(
    ("field", "value"),
    [("repo", "../evil"), ("ref", "-rf"), ("paths", ["../secrets/"])],
)
def test_registry_rejects_unsafe_source(
    tmp_path: Path, field: str, value: object
) -> None:
    """Registry rejects unsafe source."""
    data = yaml.safe_load(yaml.safe_dump(REGISTRY))
    data["source"][field] = value
    with pytest.raises(checker.RegistryError, match="unsafe"):
        checker.load_registry(write_registry(tmp_path, data))


def test_main_reads_a_local_checkout(tmp_path: Path) -> None:
    """Main reads a local checkout."""
    registry_path = write_registry(tmp_path)
    repo = tmp_path / "repo"
    (repo / "web" / "snippets").mkdir(parents=True)
    (repo / "web" / "snippets" / "openai.md").write_text('model="gpt-4o-mini"\n')
    (repo / "web" / "other.md").write_text('model="gpt-3.5-turbo"\n')
    report = tmp_path / "report.md"

    status = checker.main(
        [
            "--registry",
            str(registry_path),
            "--repo-dir",
            str(repo),
            "--output",
            str(report),
        ]
    )

    assert status == 1
    body = report.read_text()
    assert "`gpt-4o-mini` | `gpt-6-luna`" in body
    assert "gpt-3.5-turbo" not in body


def test_main_is_clean_when_everything_is_current(tmp_path: Path) -> None:
    """Main is clean when everything is current."""
    registry_path = write_registry(tmp_path)
    repo = tmp_path / "repo"
    (repo / "web" / "snippets").mkdir(parents=True)
    (repo / "web" / "snippets" / "openai.md").write_text('model="gpt-6-luna"\n')

    assert (
        checker.main(["--registry", str(registry_path), "--repo-dir", str(repo)]) == 0
    )


def test_committed_registry_is_valid() -> None:
    """Committed registry is valid."""
    registry = checker.load_registry(checker.REGISTRY)
    assert registry.repo == "langchain-ai/langchainplus"
    assert registry.providers["openai"].preferred == "gpt-6-luna"
