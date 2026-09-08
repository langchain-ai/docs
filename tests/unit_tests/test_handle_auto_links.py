"""Tests for the autolink preprocessor."""

from collections.abc import Iterator
from unittest.mock import patch

import pytest

from pipeline.preprocessors.handle_auto_links import replace_autolinks

MOCK_LINK_MAP = {
    "python": {"StateGraph": "/ref/stategraph", "Command": "/ref/command"},
    "js": {"StateGraph": "/ref/js/stategraph"},
}


@pytest.fixture(autouse=True)
def _mock_link_maps() -> Iterator[None]:
    """Provide a small link map for all tests."""
    with patch(
        "pipeline.preprocessors.handle_auto_links.SCOPE_LINK_MAPS",
        MOCK_LINK_MAP,
    ):
        yield


def test_autolinks_outside_code_blocks_are_replaced() -> None:
    """Autolinks outside code blocks should be transformed."""
    md = "Use @[StateGraph] here.\n"
    result = replace_autolinks(md, "test.mdx")
    assert "[StateGraph](/ref/stategraph)" in result
    assert "@[StateGraph]" not in result


def test_autolinks_inside_backtick_code_blocks_are_preserved() -> None:
    """Autolinks inside triple-backtick fences should not be transformed."""
    md = "```python\n@[StateGraph]\n```\n"
    result = replace_autolinks(md, "test.mdx")
    assert "@[StateGraph]" in result
    assert "[StateGraph](/ref/stategraph)" not in result


def test_autolinks_inside_tilde_code_blocks_are_preserved() -> None:
    """Autolinks inside tilde fences should not be transformed."""
    md = "~~~python\n@[StateGraph]\n~~~\n"
    result = replace_autolinks(md, "test.mdx")
    assert "@[StateGraph]" in result
    assert "[StateGraph](/ref/stategraph)" not in result


def test_autolinks_inside_extended_backtick_fences_are_preserved() -> None:
    """Autolinks inside 4+ backtick fences should not be transformed."""
    md = "````\n@[StateGraph]\n````\n"
    result = replace_autolinks(md, "test.mdx")
    assert "@[StateGraph]" in result


def test_code_block_with_language_specifier() -> None:
    """Language specifiers on code fences should still trigger detection."""
    md = "```shell\nnpm install @[StateGraph]\n```\n"
    result = replace_autolinks(md, "test.mdx")
    assert "@[StateGraph]" in result


def test_empty_lines_are_not_duplicated() -> None:
    """Empty/whitespace lines should appear exactly once in output."""
    md = "line1\n\nline2\n"
    result = replace_autolinks(md, "test.mdx")
    assert result == md


def test_empty_lines_inside_code_block_are_not_duplicated() -> None:
    """Empty lines inside code blocks should not be duplicated."""
    md = "```python\ncode\n\nmore code\n```\n"
    result = replace_autolinks(md, "test.mdx")
    assert result == md


def test_whitespace_only_lines_preserved() -> None:
    """Whitespace-only lines should pass through unchanged."""
    md = "before\n   \nafter\n"
    result = replace_autolinks(md, "test.mdx")
    assert result == md


def test_mixed_conditional_and_code_fences() -> None:
    """Conditional fences inside code blocks should not change scope."""
    md = ":::python\n@[StateGraph]\n```\n:::js\n@[StateGraph]\n```\n@[Command]\n:::\n"
    result = replace_autolinks(md, "test.mdx")
    # Outside code block: both autolinks should be transformed (python scope)
    assert "[StateGraph](/ref/stategraph)" in result
    assert "[Command](/ref/command)" in result
    # Inside code block: :::js should NOT change scope, @[StateGraph] preserved
    assert "@[StateGraph]" in result


def test_unclosed_code_block_suppresses_remaining() -> None:
    """An unclosed code fence should suppress autolinks for the rest of the doc."""
    md = "```python\n@[StateGraph]\nsome text\n@[Command]\n"
    result = replace_autolinks(md, "test.mdx")
    assert "@[StateGraph]" in result
    assert "@[Command]" in result
    assert "[StateGraph](/ref/stategraph)" not in result


def test_autolink_before_and_after_code_block() -> None:
    """Autolinks before and after a code block should both be transformed."""
    md = "@[StateGraph]\n```\ncode\n```\n@[Command]\n"
    result = replace_autolinks(md, "test.mdx")
    assert "[StateGraph](/ref/stategraph)" in result
    assert "[Command](/ref/command)" in result


def test_no_autolinks_produces_identical_output() -> None:
    """Content with no autolinks should pass through completely unchanged."""
    md = "# Heading\n\nSome text.\n\n```python\nprint('hello')\n```\n"
    result = replace_autolinks(md, "test.mdx")
    assert result == md


def test_escaped_autolinks_inside_and_outside_code_blocks() -> None:
    r"""Escaped autolinks (\@[...]) should be unescaped but not transformed."""
    md = "\\@[StateGraph]\n```\n\\@[StateGraph]\n```\n"
    result = replace_autolinks(md, "test.mdx")
    # Outside: unescaped but not linked
    assert "@[StateGraph]" in result
    assert "[StateGraph](/ref/stategraph)" not in result


@pytest.mark.parametrize(
    "fence",
    ["```", "~~~", "````", "~~~~~"],
    ids=["backtick-3", "tilde-3", "backtick-4", "tilde-5"],
)
def test_various_fence_styles(fence: str) -> None:
    """All valid CommonMark fence styles should protect their content."""
    md = f"{fence}python\n@[StateGraph]\n{fence}\n"
    result = replace_autolinks(md, "test.mdx")
    assert "@[StateGraph]" in result
    assert "[StateGraph](/ref/stategraph)" not in result


def test_indented_code_fence() -> None:
    """Indented code fences (up to 3 spaces) should be detected."""
    md = "   ```python\n   @[StateGraph]\n   ```\n"
    result = replace_autolinks(md, "test.mdx")
    assert "@[StateGraph]" in result


def test_regex_pattern_in_code_block_no_warning() -> None:
    """Regex patterns like email validators inside code blocks should not warn.

    This is the original issue (#2069).
    """
    md = (
        '```python\npattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"\n```\n'
    )
    result = replace_autolinks(md, "test.mdx")
    assert "@[a-zA-Z0-9.-]" in result
