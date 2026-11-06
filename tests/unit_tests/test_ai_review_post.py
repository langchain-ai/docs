"""Tests for the AI docs review poster and its feedback reader."""

import subprocess
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from scripts.ai_review_feedback import parse_comment, report
from scripts.ai_review_post import (
    FINDING_MARKER,
    LABEL_LOW_RISK,
    LABEL_NEEDS_HUMAN,
    Diff,
    Finding,
    _clean,
    choose_label,
    dedupe,
    parse_findings,
    read_diff,
    render_inline,
    screen_private,
)

DEFAULT = Finding(
    skill="docs-review",
    file="src/a.mdx",
    line=5,
    end_line=5,
    severity="minor",
    fix_class="suggest",
    rule="rule",
    summary="The sentence uses a contraction in the Note block.",
    replacement=None,
    evidence_kind="docs",
    evidence_public="",
)


def _f(**overrides: Any) -> Finding:  # noqa: ANN401
    """Build a finding from the default with some fields changed."""
    f = replace(DEFAULT, **overrides)
    if "skills" not in overrides:
        f.skills = [f.skill]
    return f


def _diff(
    files: dict[str, str] | None = None,
    lines: dict[str, set[int]] | None = None,
    added: str = "",
) -> Diff:
    """Build a one-file diff by default."""
    return Diff(
        files=files or {"src/a.mdx": "M"},
        lines=lines or {"src/a.mdx": {5}},
        added_text=added,
    )


def _git(cwd: Path, *args: str) -> str:
    """Run git in a test repository."""
    return subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _raw(path: str, severity: str, summary: str, fix_class: str = "suggest") -> dict:
    """One raw finding as a review pass writes it."""
    return {
        "file": path,
        "line": 3,
        "severity": severity,
        "fix_class": fix_class,
        "summary": summary,
    }


def test_parse_rejects_bad_enums_and_paths() -> None:
    """Invalid severities, unsafe paths, and empty summaries are dropped."""
    data = {
        "skill": "docs-review",
        "findings": [
            _raw("src/a.mdx", "major", "ok"),
            _raw("src/a.mdx", "critical", "bad severity"),
            _raw("../etc/passwd", "minor", "traversal"),
            _raw("/abs.mdx", "minor", "absolute"),
            _raw("src/a.mdx", "minor", " ", fix_class="auto"),
            "not a dict",
        ],
    }
    findings, rejected = parse_findings(data)
    assert [f.summary for f in findings] == ["ok"]
    assert rejected == 5


def test_parse_handles_garbage_file() -> None:
    """A file that is not a findings object counts as one rejection."""
    assert parse_findings(None) == ([], 1)
    assert parse_findings({"findings": "nope"}) == ([], 1)


def test_clean_strips_hidden_markers_and_mentions() -> None:
    """Model text cannot hide markers, open details blocks, or ping people."""
    out = _clean("Ask @npentrel <!-- x --> <details>y</details> `@[create_agent]`")
    assert "<!--" not in out
    assert "@npentrel" not in out
    assert "<details>" not in out
    assert "`@[create_agent]`" in out


def test_screen_private_drops_unless_term_is_in_diff() -> None:
    """A private term is allowed only when the PR's own diff already uses it."""
    leak = _f(summary="Checked smith-backend config for the default.")
    flag = _f(summary="Set FF_OPTIMIZED_STREAMING to enable it.")
    kept, dropped = screen_private(
        [leak, flag], diff_text="FF_OPTIMIZED_STREAMING=true"
    )
    assert kept == [flag]
    assert dropped == 1


def test_dedupe_merges_same_problem_from_two_passes() -> None:
    """Two passes reporting one problem become one finding at the higher severity."""
    a = _f(severity="major", summary="The page states a dollar price per run.")
    b = _f(
        skill="verify-against-source",
        severity="must_fix",
        summary="The page states a dollar price per Engine run.",
    )
    merged = dedupe([a, b])
    assert len(merged) == 1
    assert merged[0].severity == "must_fix"
    assert set(merged[0].skills) == {"docs-review", "verify-against-source"}


def test_dedupe_keeps_different_problems_on_one_line() -> None:
    """Different problems on the same line stay separate."""
    price = _f(summary="The page states a dollar price per run.")
    claim = _f(summary="Cannot verify from here: retry_backoff is never mentioned.")
    assert len(dedupe([price, claim])) == 2


def test_dedupe_never_moves_a_replacement_to_another_range() -> None:
    """A one-line fix is never attached to a finding that spans more lines."""
    question = _f(
        line=18,
        end_line=27,
        fix_class="human",
        summary="Cannot verify the Helm chart 0.13.0 floor or the error text.",
    )
    fix = _f(
        line=21,
        end_line=21,
        replacement="Helm chart version 0.13.0 or later.",
        summary="The Helm chart 0.13.0 floor uses >= in prose.",
    )
    merged = dedupe([question, fix])
    assert len(merged) == 2
    assert next(m for m in merged if m.line == 18).replacement is None


def test_dedupe_merges_file_level_findings_across_files() -> None:
    """A missing nav entry filed under docs.json or under the page is one finding."""
    a = _f(
        file="src/docs.json",
        line=None,
        end_line=None,
        summary="The new page engine-run-retries is not in src/docs.json navigation.",
    )
    b = _f(
        line=None,
        end_line=None,
        summary="The new page engine-run-retries is not in docs.json navigation.",
    )
    assert len(dedupe([a, b])) == 1


def test_label_low_risk_needs_every_condition() -> None:
    """Any blocking finding, question, or risky path means a human reviews."""
    assert choose_label([_f()], _diff(), []) == LABEL_LOW_RISK
    assert choose_label([_f(severity="major")], _diff(), []) == LABEL_NEEDS_HUMAN
    assert choose_label([_f(fix_class="human")], _diff(), []) == LABEL_NEEDS_HUMAN
    unmet = [{"documents_claimed_change": "no"}]
    assert choose_label([], _diff(), unmet) == LABEL_NEEDS_HUMAN
    assert choose_label([], _diff(files={"src/new.mdx": "A"}), []) == LABEL_NEEDS_HUMAN
    assert (
        choose_label([], _diff(files={"src/docs.json": "M"}), []) == LABEL_NEEDS_HUMAN
    )
    big = _diff(lines={"src/a.mdx": set(range(1, 60))})
    assert choose_label([], big, []) == LABEL_NEEDS_HUMAN


def test_render_inline_carries_marker_and_safe_fence() -> None:
    """A replacement containing a code fence gets a longer suggestion fence."""
    f = _f(severity="major", replacement="```bash\nexport X=1\n```")
    body = render_inline(f)
    assert FINDING_MARKER.format(fp=f.fingerprint) in body
    assert "````suggestion" in body


def test_human_finding_gets_no_suggestion() -> None:
    """A question never renders a one-click suggestion."""
    f = _f(severity="major", fix_class="human", replacement="ignored")
    assert "suggestion" not in render_inline(f)


def test_fingerprint_is_stable_across_reruns() -> None:
    """A finding that moved lines after a push keeps its fingerprint."""
    a = _f(summary="The page states a dollar price.", line=5)
    b = _f(summary="The page states a dollar price.", line=9)
    assert a.fingerprint == b.fingerprint


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A two-commit repository: one modified file and one added file."""
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@example.invalid")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/a.mdx").write_text("one\ntwo\nthree\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "base")
    (tmp_path / "src/a.mdx").write_text("one\nTWO\nthree\nfour\n")
    (tmp_path / "src/b.mdx").write_text("new\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "head")
    return tmp_path


def test_read_diff_finds_changed_lines(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Changed line numbers and file statuses come from the real diff."""
    monkeypatch.chdir(repo)
    diff = read_diff(_git(repo, "rev-parse", "HEAD~1"), _git(repo, "rev-parse", "HEAD"))
    assert diff.files == {"src/a.mdx": "M", "src/b.mdx": "A"}
    assert diff.lines["src/a.mdx"] == {2, 4}
    assert "TWO" in diff.added_text


def test_read_diff_rejects_non_sha() -> None:
    """Only commit SHAs reach git."""
    with pytest.raises(ValueError, match="not a commit SHA"):
        read_diff("main; rm -rf /", "HEAD")


def test_feedback_parses_the_posters_own_comments() -> None:
    """The feedback reader understands exactly what the poster writes."""
    f = _f(
        severity="major",
        rule="Use American spelling",
        replacement="canceled",
        skills=["docs-review", "docs-team-voice"],
    )
    comment = {
        "id": 1,
        "html_url": "https://example.invalid/c/1",
        "path": f.file,
        "position": None,
        "body": render_inline(f),
        "reactions": {"+1": 0, "-1": 2},
    }
    row = parse_comment(comment)
    assert row is not None
    assert row["fingerprint"] == f.fingerprint
    assert row["severity"] == "Major"
    assert row["rule"] == "Use American spelling"
    assert row["skills"] == ["docs-review", "docs-team-voice"]
    assert row["down"] == 2
    assert row["outdated"]
    assert row["suggestion"]
    row["pr"] = 7
    assert "Thumbs down (1)" in report([row])
    assert parse_comment({"body": "a human comment"}) is None
