"""Tests for the cross-reference checker script."""

import tempfile
from pathlib import Path

from scripts.check_cross_refs import check_cross_refs


def _write(tmp: Path, rel_path: str, content: str) -> None:
    p = tmp / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_valid_python_ref() -> None:
    """Known Python-scope ref resolves."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(src, "langsmith/page.mdx", "Use @[StateGraph] here.")
        errors = check_cross_refs(src)
        assert errors == []


def test_unresolved_ref() -> None:
    """Unknown ref is reported."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(src, "langsmith/page.mdx", "Use @[NonExistentWidget] here.")
        errors = check_cross_refs(src)
        assert len(errors) == 1
        assert errors[0][2] == "NonExistentWidget"


def test_js_scope_fence() -> None:
    """Ref inside :::js fence is checked against js scope."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        content = ":::js\n@[StateGraph]\n:::\n"
        _write(src, "oss/page.mdx", content)
        errors = check_cross_refs(src)
        assert errors == []


def test_js_only_ref_in_python_scope_fails() -> None:
    """JS-only ref is unresolved when file defaults to Python scope."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(src, "oss/python/page.mdx", "@[wrapVitest]")
        errors = check_cross_refs(src)
        assert len(errors) == 1
        assert errors[0][2] == "wrapVitest"


def test_oss_shared_file_checks_both_scopes() -> None:
    """Shared oss/ file (not python/ or javascript/) checks both scopes."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(src, "oss/page.mdx", "@[StateGraph]")
        errors = check_cross_refs(src)
        assert errors == []


def test_ref_inside_code_block_ignored() -> None:
    """Refs inside fenced code blocks are not checked."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        content = "```python\n@[NonExistentWidget]\n```\n"
        _write(src, "langsmith/page.mdx", content)
        errors = check_cross_refs(src)
        assert errors == []


def test_escaped_ref_ignored() -> None:
    r"""Escaped refs (\@[...]) are not checked."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(src, "langsmith/page.mdx", "\\@[NonExistentWidget]")
        errors = check_cross_refs(src)
        assert errors == []


def test_titled_ref_format() -> None:
    """@[title][ref] format extracts the ref name correctly."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(src, "langsmith/page.mdx", "@[my title][StateGraph]")
        errors = check_cross_refs(src)
        assert errors == []


def test_titled_ref_unresolved() -> None:
    """@[title][unknown] format reports the ref name."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(src, "langsmith/page.mdx", "@[my title][UnknownRef]")
        errors = check_cross_refs(src)
        assert len(errors) == 1
        assert errors[0][2] == "UnknownRef"


def test_code_samples_snippets_skipped() -> None:
    """Files under snippets/code-samples/ are skipped."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(src, "snippets/code-samples/example.mdx", "@[NonExistentWidget]")
        errors = check_cross_refs(src)
        assert errors == []


def test_backtick_ref() -> None:
    """@[`ClassName`] format resolves correctly."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(src, "langsmith/page.mdx", "@[`StateGraph`]")
        errors = check_cross_refs(src)
        assert errors == []


def test_multiple_refs_on_same_line() -> None:
    """Multiple refs on the same line are all checked."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        _write(
            src,
            "langsmith/page.mdx",
            "Use @[StateGraph] and @[NonExistentWidget] together.",
        )
        errors = check_cross_refs(src)
        assert len(errors) == 1
        assert errors[0][2] == "NonExistentWidget"
