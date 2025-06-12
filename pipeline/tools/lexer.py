"""Markdown lexer for tokenizing markdown text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

TAB_SIZE = 4  # change this if you want tabs to expand differently


class TokenType(Enum):
    """All token kinds recognised by the Markdown lexer."""

    HEADING = auto()  # #, ##, ### …
    FENCE = auto()  # ```lang [meta] or fence close
    FRONT_MATTER = auto()  # ---
    UL_MARKER = auto()  # -, +, *
    OL_MARKER = auto()  # 1.  2)  etc.
    BLOCKQUOTE = auto()  # >
    TAB_HEADER = auto()  # === "title"
    ADMONITION = auto()  # !!! note "Title" or ??? note
    HTML_TAG = auto()  # <div> … (single-line)
    BLANK = auto()  # empty or whitespace-only line
    TEXT = auto()  # anything else
    EOF = auto()  # synthetic end-of-file marker


@dataclass(slots=True)
class Token:
    """Single token emitted by the lexer."""

    type: TokenType
    value: str  # text after leading indent has been stripped
    indent: int  # indent width in spaces (tabs → spaces)
    line: int  # 1-based line number where this token was found


# ---------------------------------------------------------------------------
# Regular-expressions are evaluated against the *trimmed* line (indent removed)
# ---------------------------------------------------------------------------

_PATTERNS: list[tuple[TokenType, re.Pattern[str]]] = [
    # Block/ATX headings
    (TokenType.HEADING, re.compile(r"(#{1,6})\s+.*")),
    # Fenced code blocks
    (TokenType.FENCE, re.compile(r"```(?:\S*)")),
    # Unordered and ordered list markers
    (TokenType.UL_MARKER, re.compile(r"[-+*]\s+")),
    (TokenType.OL_MARKER, re.compile(r"\d+[.)]\s+")),
    # Blockquote prefix
    (TokenType.BLOCKQUOTE, re.compile(r">")),
    # === "Tab" blocks
    (TokenType.TAB_HEADER, re.compile(r'===\s*"[^"]+"')),
    # !!! or ??? admonitions
    (TokenType.ADMONITION, re.compile(r"(?:!!!|\?\?\?)\s+\w+(?:\s+\"[^\"]+\")?")),
    # Single-line HTML tag (kept permissive; full parsing happens later)
    (TokenType.HTML_TAG, re.compile(r"<[/A-Za-z][^>]*>$")),
]


# ---------------------------------------------------------------------------
# Helper: indent calculation with tab expansion
# ---------------------------------------------------------------------------


def _indent_width(line: str) -> int:
    """Return indent width in spaces, expanding tabs with `TAB_SIZE`."""
    width = 0
    for ch in line:
        if ch == " ":
            width += 1
        elif ch == "\t":
            # advance to next tab stop
            width += TAB_SIZE - (width % TAB_SIZE)
        else:
            break
    return width


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def lex(text: str | Iterable[str]) -> Iterator[Token]:
    """Yield a stream of :class:`Token` objects from *text*.

    Args:
        text: The full Markdown source (string or iterable of lines).

    Yields:
        Token objects, **including** a final EOF token.
    """
    lines = text.splitlines() if isinstance(text, str) else list(text)

    for idx, raw in enumerate(lines, 1):
        indent = _indent_width(raw)
        trimmed = raw[indent:]

        # blank line → BLANK token
        if not trimmed:
            yield Token(TokenType.BLANK, "", indent, idx)
            continue

        # match token patterns, first hit wins
        for ttype, pattern in _PATTERNS:
            if pattern.match(trimmed):
                yield Token(ttype, trimmed, indent, idx)
                break
        else:
            # fallback: plain text
            yield Token(TokenType.TEXT, trimmed, indent, idx)

    # synthetic EOF token (needed for parsers that expect a sentinel)
    yield Token(TokenType.EOF, "", 0, len(lines) + 1)


__all__ = ["Token", "TokenType", "lex"]
