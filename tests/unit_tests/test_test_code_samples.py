"""Tests for the CODE_SAMPLE_PATHS filter in scripts/test_code_samples.py."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts import test_code_samples as runner

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def repo(tmp_path: Path) -> tuple[Path, Path]:
    """Build a throwaway repo with one sample per product directory."""
    samples = tmp_path / "src" / "code-samples"
    for product, name in [
        ("langchain", "a.py"),
        ("langchain", "a.ts"),
        ("langsmith", "b.py"),
        ("langsmith", "nested/c.sh"),
        ("deepagents", "d.go"),
    ]:
        path = samples / product / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    # Noise the runner must ignore regardless of filter.
    (samples / "langsmith" / "node_modules").mkdir()
    (samples / "langsmith" / "node_modules" / "ignored.py").write_text("")
    return tmp_path, samples


def rel_paths(files: list[tuple[Path, str]], root: Path) -> set[str]:
    """Reduce collected (path, lang) pairs to repo-relative path strings."""
    return {p.relative_to(root).as_posix() for p, _lang in files}


def test_no_filter_runs_every_sample(
    repo: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without CODE_SAMPLE_PATHS the runner behaves as before: everything runs."""
    root, samples = repo
    monkeypatch.delenv("CODE_SAMPLE_PATHS", raising=False)
    monkeypatch.delenv("FILES", raising=False)

    found = rel_paths(runner.collect_files_to_test(root, samples), root)

    assert found == {
        "src/code-samples/langchain/a.py",
        "src/code-samples/langchain/a.ts",
        "src/code-samples/langsmith/b.py",
        "src/code-samples/langsmith/nested/c.sh",
        "src/code-samples/deepagents/d.go",
    }


def test_paths_filter_limits_run_all_to_named_directories(
    repo: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """One directory keeps only that product's samples, including nested ones."""
    root, samples = repo
    monkeypatch.setenv("CODE_SAMPLE_PATHS", "src/code-samples/langsmith")
    monkeypatch.delenv("FILES", raising=False)

    found = rel_paths(runner.collect_files_to_test(root, samples), root)

    assert found == {
        "src/code-samples/langsmith/b.py",
        "src/code-samples/langsmith/nested/c.sh",
    }


def test_paths_filter_accepts_several_directories(
    repo: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The OSS leg names several directories in one space-separated value."""
    root, samples = repo
    monkeypatch.setenv(
        "CODE_SAMPLE_PATHS",
        "src/code-samples/langchain src/code-samples/deepagents",
    )
    monkeypatch.delenv("FILES", raising=False)

    found = rel_paths(runner.collect_files_to_test(root, samples), root)

    assert found == {
        "src/code-samples/langchain/a.py",
        "src/code-samples/langchain/a.ts",
        "src/code-samples/deepagents/d.go",
    }


def test_paths_filter_applies_to_explicit_files(
    repo: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A matrix leg receives every modified file and keeps only its own."""
    root, samples = repo
    monkeypatch.setenv("CODE_SAMPLE_PATHS", "src/code-samples/langsmith")
    monkeypatch.setenv(
        "FILES",
        "src/code-samples/langchain/a.py src/code-samples/langsmith/b.py "
        "src/code-samples/deepagents/d.go",
    )

    found = rel_paths(runner.collect_files_to_test(root, samples), root)

    assert found == {"src/code-samples/langsmith/b.py"}
    assert "Skipped 2 file(s) outside CODE_SAMPLE_PATHS" in capsys.readouterr().out


def test_paths_filter_can_empty_an_explicit_list(
    repo: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A leg whose product was not touched by the PR gets nothing to run."""
    root, samples = repo
    monkeypatch.setenv("CODE_SAMPLE_PATHS", "src/code-samples/langsmith")
    monkeypatch.setenv("FILES", "src/code-samples/langchain/a.py")

    assert runner.collect_files_to_test(root, samples) == []


def test_paths_outside_code_samples_are_ignored(
    repo: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A typo must not widen the run beyond src/code-samples/."""
    root, samples = repo
    (root / "scripts").mkdir()
    (root / "scripts" / "x.py").write_text("")
    monkeypatch.setenv("CODE_SAMPLE_PATHS", "scripts src/code-samples/deepagents")
    monkeypatch.delenv("FILES", raising=False)

    found = rel_paths(runner.collect_files_to_test(root, samples), root)

    assert found == {"src/code-samples/deepagents/d.go"}
    assert "CODE_SAMPLE_PATHS entry scripts is not under" in capsys.readouterr().out


def test_matches_sample_paths_is_prefix_based(tmp_path: Path) -> None:
    """Matching is by directory ancestry, not by string prefix."""
    prefix = tmp_path / "langsmith"
    assert runner.matches_sample_paths(prefix / "a.py", [prefix])
    assert runner.matches_sample_paths(prefix / "deep" / "a.py", [prefix])
    assert runner.matches_sample_paths(prefix, [prefix])
    # Sibling that merely shares the string prefix is not under the directory.
    assert not runner.matches_sample_paths(tmp_path / "langsmith2" / "a.py", [prefix])
    assert runner.matches_sample_paths(tmp_path / "anything.py", [])
