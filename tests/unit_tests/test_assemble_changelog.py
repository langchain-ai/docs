"""Tests for the published-fragment ledger in scripts/assemble_changelog.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import assemble_changelog
from scripts.assemble_changelog import Fragment, load_ledger, record_published

FRAGMENT = """\
title: {title}
body: {title} now works.
components: [tracing]
flag: null
status: ready
"""


def _fragment(name: str) -> Fragment:
    return Fragment(
        path=Path(name),
        title=name,
        body="Body.",
        components=["tracing"],
        flag=None,
        status="ready",
    )


def test_load_ledger_ignores_comments_and_blank_lines(tmp_path: Path) -> None:
    """Read names, skipping comments, blank lines, and surrounding whitespace."""
    ledger = tmp_path / "ledger.txt"
    ledger.write_text("# header\n\na.yaml\n  b.yaml  \n")

    assert load_ledger(ledger) == {"a.yaml", "b.yaml"}


def test_load_ledger_missing_file_is_empty(tmp_path: Path) -> None:
    """Treat a missing ledger as nothing published yet."""
    assert load_ledger(tmp_path / "missing.txt") == set()


def test_record_published_keeps_header_sorted_and_unique(tmp_path: Path) -> None:
    """Append new names, keep the header, and do not duplicate existing names."""
    ledger = tmp_path / "ledger.txt"
    ledger.write_text("# header\nc.yaml\n")

    record_published(ledger, [_fragment("a.yaml"), _fragment("c.yaml")])

    assert ledger.read_text() == "# header\na.yaml\nc.yaml\n"


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Build a repo root holding two ready fragments and a category map."""
    monkeypatch.setattr(assemble_changelog, "_REPO_ROOT", tmp_path)
    monkeypatch.delenv("EPPO_API_KEY", raising=False)
    fragments = tmp_path / "fragments"
    fragments.mkdir()
    (fragments / "_category-map.yaml").write_text(
        "components:\n  tracing: {product: cloud, section: Tracing}\n"
    )
    for name in ("old", "new"):
        (fragments / f"{name}.yaml").write_text(FRAGMENT.format(title=name.title()))
    return tmp_path


def test_main_skips_ledger_entries_and_records_rendered(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Skip fragments in the ledger and record the ones rendered."""
    ledger = repo / "ledger.txt"
    ledger.write_text("old.yaml\n")
    argv = ["--fragments-dir", str(repo / "fragments"), "--ledger", str(ledger)]

    assemble_changelog.main([*argv, "--record"])
    out = capsys.readouterr().out
    assert "New now works." in out
    assert "Old now works." not in out
    assert load_ledger(ledger) == {"new.yaml", "old.yaml"}

    # A second run publishes nothing, because both fragments are recorded.
    assemble_changelog.main(argv)
    assert "now works." not in capsys.readouterr().out


def test_main_does_not_record_without_flag(repo: Path) -> None:
    """Leave the ledger untouched unless --record is passed."""
    ledger = repo / "ledger.txt"
    argv = ["--fragments-dir", str(repo / "fragments"), "--ledger", str(ledger)]
    assemble_changelog.main(argv)

    assert not ledger.exists()


def test_main_rejects_ledger_outside_repo(
    repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """Refuse a ledger path that resolves outside the repo root."""
    outside = tmp_path_factory.mktemp("elsewhere") / "ledger.txt"

    with pytest.raises(ValueError, match="outside"):
        assemble_changelog.main(
            ["--fragments-dir", str(repo / "fragments"), "--ledger", str(outside)]
        )
