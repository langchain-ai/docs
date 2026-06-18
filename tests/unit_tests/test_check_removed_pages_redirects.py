"""Tests for the removed-pages redirect checker."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Never

import pytest

from scripts import check_removed_pages_redirects


def test_main_accepts_base_ref(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The CLI accepts --base-ref and passes it to the git-backed loader."""
    base_docs: dict[str, object] = {"navigation": {"products": []}}
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "docs.json").write_text(json.dumps(base_docs), encoding="utf-8")

    calls: list[tuple[str, Path]] = []

    def fake_load_base_docs_from_ref(
        base_ref: str,
        head_path: Path,
    ) -> dict[str, object]:
        calls.append((base_ref, head_path))
        return base_docs

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        check_removed_pages_redirects,
        "_load_base_docs_from_ref",
        fake_load_base_docs_from_ref,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_removed_pages_redirects.py",
            "--base-ref",
            "HEAD",
            "src/docs.json",
        ],
    )

    assert check_removed_pages_redirects.main() == 0
    assert calls == [("HEAD", Path("src/docs.json"))]


def test_load_base_docs_from_ref_reads_docs_json_from_git(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The base-ref loader reads docs.json from the requested git ref."""
    calls: list[tuple[list[str], int, bool]] = []
    base_docs: dict[str, object] = {"navigation": {"products": []}}

    def fake_check_output(cmd: list[str], stderr: int, text: bool) -> str:
        calls.append((cmd, stderr, text))
        return json.dumps(base_docs)

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    result = check_removed_pages_redirects._load_base_docs_from_ref(
        "origin/main",
        Path("src/docs.json"),
    )

    assert result == base_docs
    assert calls == [
        (
            ["git", "show", "origin/main:src/docs.json"],
            subprocess.PIPE,
            True,
        )
    ]


def test_load_base_docs_from_ref_returns_none_when_git_show_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The base-ref loader reports git-show failures instead of raising."""

    def fake_check_output(cmd: list[str], stderr: int, text: bool) -> Never:
        raise subprocess.CalledProcessError(
            128,
            cmd,
            stderr="fatal: invalid object name\n",
        )

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    result = check_removed_pages_redirects._load_base_docs_from_ref(
        "missing-ref",
        Path("src/docs.json"),
    )

    assert result is None
    captured = capsys.readouterr()
    assert "could not read src/docs.json from base ref missing-ref" in captured.err
    assert "fatal: invalid object name" in captured.err
