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
    assert tokens[0].type == TokenType.FENCE_START
    assert tokens[0].value == "```python"
    assert tokens[1].type == TokenType.EOF


def test_fence_end() -> None:
    """Test lexing a fenced code block end."""
    tokens = list(lex("```"))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.FENCE_END
    assert tokens[0].value == "```"
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


def test_html_tag() -> None:
    """Test lexing a single-line HTML tag."""
    tokens = list(lex("<div>Content</div>"))
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.HTML_TAG
    assert tokens[0].value == "<div>Content</div>"
    assert tokens[1].type == TokenType.EOF


def test_two_html_tags() -> None:
    """Test lexing two HTML tags."""
    tokens = list(lex("<div>Content</div><span>More content</span>"))
    assert len(tokens) == 3
    assert tokens[0].type == TokenType.HTML_TAG
    assert tokens[0].value == "<div>Content</div>"
    assert tokens[1].type == TokenType.HTML_TAG
    assert tokens[1].value == "<span>More content</span>"
    assert tokens[2].type == TokenType.EOF
