"""Tests for conditional fence validation in the markdown preprocessor."""

import pytest

from pipeline.preprocessors.markdown_preprocessor import (
    _apply_conditional_rendering,
    _validate_conditional_fences,
)


def test_balanced_fences_pass() -> None:
    """Balanced fences around whole blocks render without error."""
    text = ":::python\nPython text.\n:::\n\n:::js\nJS text.\n:::\n"
    assert _apply_conditional_rendering(text, "js").strip() == "JS text."


def test_per_language_tables_pass() -> None:
    """A full table inside each fence is valid."""
    text = ":::python\n| A |\n| - |\n| py |\n:::\n\n:::js\n| A |\n| - |\n| js |\n:::\n"
    _validate_conditional_fences(text)


def test_fences_inside_code_blocks_are_ignored() -> None:
    """Fence-like lines inside a code block are not checked."""
    text = "```md\n:::\n:::python\n```\n"
    _validate_conditional_fences(text)


def test_escaped_fences_are_ignored() -> None:
    """Escaped fences render literally and are not checked."""
    _validate_conditional_fences("\\:::python\nLiteral.\n\\:::\n")


@pytest.mark.parametrize(
    ("text", "problem"),
    [
        (":::python\nA\n:::python\nB\n:::\n", "line 3: :::python opens inside"),
        ("Text.\n:::\n", "line 2: ::: closes a block that is not open"),
        (":::python\nA\n::::::js\nB\n:::\n", "line 3: malformed fence"),
        (":::python\nA\n::: | row |\n", "line 3: malformed fence"),
        (":::js\nNever closed.\n", "line 1: block is never closed"),
        ("| A |\n| - |\n:::python\n| py |\n:::\n", "line 3: fence inside a table"),
    ],
)
def test_broken_fences_raise(text: str, problem: str) -> None:
    """Each kind of broken fence raises with its line number."""
    with pytest.raises(ValueError, match="Broken conditional fences") as error:
        _apply_conditional_rendering(text, "python")
    assert problem in str(error.value)
