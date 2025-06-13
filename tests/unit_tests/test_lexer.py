"""Tests for the markdown lexer module."""

from pipeline.tools.lexer import TokenType, lex


def test_lexer() -> None:
    """Test the lexer."""
    tokens = list(lex("Hello"))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "Hello"
    assert tokens[1].type == TokenType.EOF


def test_empty_file() -> None:
    """Test lexing an empty file."""
    tokens = list(lex(""))
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF


def test_heading() -> None:
    """Test lexing a heading."""
    tokens = list(lex("# Heading"))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.HEADING
    assert tokens[0].value == "# Heading"
    assert tokens[1].type == TokenType.EOF


def test_fence_start() -> None:
    """Test lexing a fenced code block start."""
    tokens = list(lex("```python"))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.FENCE
    assert tokens[0].value == "```python"
    assert tokens[1].type == TokenType.EOF


def test_unordered_list_marker() -> None:
    """Test lexing an unordered list marker."""
    tokens = list(lex("- Item"))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.UL_MARKER
    assert tokens[0].value == "- Item"
    assert tokens[1].type == TokenType.EOF


def test_ordered_list_marker() -> None:
    """Test lexing an ordered list marker."""
    tokens = list(lex("1. Item"))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.OL_MARKER
    assert tokens[0].value == "1. Item"
    assert tokens[1].type == TokenType.EOF


def test_blockquote() -> None:
    """Test lexing a blockquote."""
    tokens = list(lex("> Quote"))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.BLOCKQUOTE
    assert tokens[0].value == "> Quote"
    assert tokens[1].type == TokenType.EOF


def test_tab_header() -> None:
    """Test lexing a tab header."""
    tokens = list(lex('=== "Tab Header"'))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.TAB_HEADER
    assert tokens[0].value == '=== "Tab Header"'
    assert tokens[1].type == TokenType.EOF


def test_admonition() -> None:
    """Test lexing an admonition."""
    tokens = list(lex('??? note "Important Note"'))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.ADMONITION
    assert tokens[0].value == '??? note "Important Note"'
    assert tokens[1].type == TokenType.EOF


CODE_IN_TAB = """\
=== "Example Tab"

    ```python
    def test():
        print("Hello, World!")
    ```
"""


def test_indentation_in_tab() -> None:
    """Test indentation is handled correctly inside a code block in a tab."""
    tokens = list(lex(CODE_IN_TAB))

    types = [
        TokenType.TAB_HEADER,
        TokenType.BLANK,
        TokenType.FENCE,
        TokenType.TEXT,
        TokenType.TEXT,
        TokenType.FENCE,
        TokenType.EOF,
    ]

    assert [token.type for token in tokens] == types

    # Check indents
    assert tokens[0].indent == 0
    assert tokens[1].indent == 0
    assert tokens[2].indent == 4  # Fence starts with 4 spaces
    assert tokens[3].indent == 4  # Same indent for code line
    assert tokens[4].indent == 8  # Indent for the print


CODEBLOCK_WITH_BLANK_LINES = """\
```python
def example():
    x = 2
    
    y = 3
"""  # noqa: W293


def test_lex_code_with_blank_lines() -> None:
    """Test lexing a code block with blank lines."""
    tokens = list(lex(CODEBLOCK_WITH_BLANK_LINES))

    types = [
        TokenType.FENCE,
        TokenType.TEXT,
        TokenType.TEXT,
        TokenType.BLANK,
        TokenType.TEXT,
        TokenType.EOF,
    ]

    assert [token.type for token in tokens] == types

    # Check indents
    assert tokens[0].indent == 0  # Fence starts with no indent
    assert tokens[1].indent == 0  # Function definition
    assert tokens[2].indent == 4  # Assignment line
    # We want to check that the ident on the blank line is preserved correctly
    assert tokens[3].indent == 4  # Blank line
    assert tokens[4].indent == 4  # Second assignment line


INPUT_TABLE = """\
| Property | Description                           |
| -------- | ------------------------------------- |
| Name     | Full name of user                     |
| Age      | Reported age                          |
| Joined   | Whether the user joined the community |
"""


def test_lex_table() -> None:
    """Test lexing a table."""
    tokens = list(lex(INPUT_TABLE))
    assert len(tokens) == 6
    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "| Property | Description                           |"
    assert tokens[1].type == TokenType.TEXT
    assert tokens[1].value == "| -------- | ------------------------------------- |"
    assert tokens[2].type == TokenType.TEXT
    assert tokens[2].value == "| Name     | Full name of user                     |"
