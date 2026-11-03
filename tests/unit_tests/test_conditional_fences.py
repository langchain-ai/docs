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


def test_compact_closers_pass() -> None:
    """A closer may carry text, as the rendering regex accepts."""
    text = (
        "| A |\n| - |\n:::python\n| py |\n::: | shared |\n"
        ":::python\nPy.\n::::::js\nJS.\n:::\n"
    )
    _validate_conditional_fences(text)
    rendered = _apply_conditional_rendering(text, "js")
    assert "| shared |" in rendered
    assert "JS." in rendered
    assert "py" not in rendered


def test_escaped_fences_are_ignored() -> None:
    """Escaped fences render literally and are not checked."""
    _validate_conditional_fences("\\:::python\nLiteral.\n\\:::\n")


@pytest.mark.parametrize(
    ("text", "problem"),
    [
        (":::python\nA\n:::python\nB\n:::\n", "line 3: :::python opens inside"),
        ("Text.\n:::\n", "line 2: ::: closes a block that is not open"),
        ("Intro.\n:::caution Deprecated.\n", "line 2: ::: closes a block"),
        (":::js\nNever closed.\n", "line 1: block is never closed"),
    ],
)
def test_broken_fences_raise(text: str, problem: str) -> None:
    """Each kind of broken fence raises with its line number."""
    with pytest.raises(ValueError, match="Broken conditional fences") as error:
        _apply_conditional_rendering(text, "python")
    assert problem in str(error.value)
