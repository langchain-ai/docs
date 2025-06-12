"""Simplified Markdown parser for mapping custom commands to Mintlify syntax.

Most of this parser was generated with Claude code. It's created to help
with a quick migration from a custom markdown format to Mintlify's format and
is not meant to be perfect or handle all edge cases of Markdown syntax.

If we keep the parser, we may need to re-design the architecture a bit to separate
the tokenization from the parsing logic, which will make it simpler to handle
indentation and other nuances of Markdown syntax.
"""

from __future__ import annotations

import typing
from dataclasses import dataclass

from pipeline.tools.lexer import Token, TokenType, lex

if typing.TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(kw_only=True)
class Node:
    """Base-class for all AST nodes."""

    start_line: int  #: First source line (1-based, inclusive).
    limit_line: int  #: Line *after* the last source line (exclusive).


@dataclass(kw_only=True)
class Document(Node):
    """Root node that stores top-level blocks."""

    blocks: list[Node]


@dataclass(kw_only=True)
class Heading(Node):
    """Markdown heading (#, ##, …)."""

    level: int
    value: str


@dataclass(kw_only=True)
class Paragraph(Node):
    """Consecutive text lines."""

    value: list[str]


@dataclass(kw_only=True)
class CodeBlock(Node):
    """Fenced code block (```lang [meta])."""

    language: str | None
    meta: str | None
    content: str


@dataclass(kw_only=True)
class ListItem(Node):
    """Single bullet/number item (may contain nested blocks)."""

    blocks: list[Node]


@dataclass(kw_only=True)
class UnorderedList(Node):
    """Bullet list (-, +, *)."""

    items: list[ListItem]


@dataclass(kw_only=True)
class OrderedList(Node):
    """Numbered list (1., 2), …)."""

    items: list[ListItem]


@dataclass(kw_only=True)
class QuoteBlock(Node):
    """> Blockquote."""

    lines: list[str]


@dataclass(kw_only=True)
class Tab(Node):
    """One tab inside a tab block (=== "Title")."""

    title: str
    blocks: list[Node]


@dataclass(kw_only=True)
class TabBlock(Node):
    """Container for :class:`Tab` nodes."""

    tabs: list[Tab]


@dataclass(kw_only=True)
class Admonition(Node):
    """!!! / ??? admonition."""

    tag: str
    kind: str
    title: str
    blocks: list[Node]


@dataclass(kw_only=True)
class FrontMatter(Node):
    """YAML front-matter between --- delimiters."""

    content: str


@dataclass(kw_only=True)
class HTMLBlock(Node):
    """Raw HTML block (single line for now)."""

    content: str


class Parser:
    """Recursive-descent parser that consumes tokens and builds an AST."""

    def __init__(self, source: str) -> None:
        """Create a parser.

        Args:
            source: Full Markdown text.
        """
        self._tokens: Iterator[Token] = iter(lex(source))
        self._token: Token = next(self._tokens)  # current look-ahead

    def parse(self) -> Document:
        """Parse *source* and return an AST root."""
        blocks: list[Node] = []

        if self._check(TokenType.FRONT_MATTER):
            blocks.append(self._parse_front_matter())

        while not self._check(TokenType.EOF):
            if self._match(TokenType.BLANK):
                continue  # skip blank lines
            blocks.append(self._parse_block())

        return Document(blocks=blocks, start_line=1, limit_line=self._token.line)

    def _advance(self) -> Token:
        """Consume the current token and return it."""
        previous = self._token
        self._token = next(self._tokens)
        return previous

    def _check(self, *kinds: TokenType) -> bool:
        """Return ``True`` if current token matches any *kinds*."""
        return self._token.type in kinds

    def _match(self, *kinds: TokenType) -> bool:
        """Advance if token matches any *kinds* and report success."""
        if self._check(*kinds):
            self._advance()
            return True
        return False

    # ------------------------------------------------------------------
    # Block dispatch
    # ------------------------------------------------------------------

    # Ignoring PLR0911 (too many return statements) here as this is a
    # dispatch method that routes to specific block parsers based on the
    # current token type.
    def _parse_block(self) -> Node:  # noqa: PLR0911
        """Route to the correct *block* parser based on current token."""
        if self._check(TokenType.HEADING):
            return self._parse_heading()
        if self._check(TokenType.FENCE):
            return self._parse_code_block()
        if self._check(TokenType.UL_MARKER):
            return self._parse_list(ordered=False)
        if self._check(TokenType.OL_MARKER):
            return self._parse_list(ordered=True)
        if self._check(TokenType.BLOCKQUOTE):
            return self._parse_quote_block()
        if self._check(TokenType.ADMONITION):
            return self._parse_admonition()
        if self._check(TokenType.TAB_HEADER):
            return self._parse_tab_block()
        if self._check(TokenType.HTML_TAG):
            return self._parse_html_block()
        return self._parse_paragraph()

    # ------------------------------------------------------------------
    # Concrete block parsers
    # ------------------------------------------------------------------

    def _parse_blocks_until_indent(self, min_indent: int) -> list[Node]:
        """Parse blocks into a sequence until we hit a shallower indent."""
        blocks: list[Node] = []
        while not self._check(TokenType.EOF) and (
            self._token.indent > min_indent or self._token.type == TokenType.BLANK
        ):
            if self._match(TokenType.BLANK):
                continue  # skip blank lines at this level
            blocks.append(self._parse_block())
        return blocks

    def _parse_front_matter(self) -> FrontMatter:
        """Parse YAML front-matter (--- … ---)."""
        open_token = self._advance()  # opening '---'
        content_lines: list[str] = []
        while not self._check(TokenType.FRONT_MATTER):
            content_lines.append(self._advance().value)
        close_token = self._advance()  # closing '---'
        return FrontMatter(
            content="\n".join(content_lines),
            start_line=open_token.line,
            limit_line=close_token.line + 1,
        )

    def _parse_heading(self) -> Heading:
        """Parse a heading (#, ##, …)."""
        token = self._advance()
        hashes, text = token.value.split(" ", 1)
        return Heading(
            level=len(hashes),
            value=text,
            start_line=token.line,
            limit_line=token.line + 1,
        )

    def _parse_code_block(self) -> CodeBlock:
        """Parse a fenced code block (```lang [meta])."""
        open_token = self._advance()
        fence_body = open_token.value[3:].strip()

        parts = fence_body.split(" ", maxsplit=1)

        if len(parts) == 1:
            language = parts[0] if parts[0] else None
            meta = ""
        else:
            language, meta = parts

        # All lines that belong to this fenced block will have an
        # indent *at least* as big as the opening fence.  Everything
        # beyond that is real, user-written indentation that we must
        # preserve in the output.
        fence_indent = open_token.indent
        body_lines: list[str] = []
        while not self._check(TokenType.FENCE):
            tok = self._advance()
            # Preserve **relative** indentation of the code block
            rel_ident = max(0, tok.indent - fence_indent)
            body_lines.append(" " * rel_ident + tok.value)

        close_token = self._advance()

        return CodeBlock(
            language=language,
            meta=meta,
            content="\n".join(body_lines),
            start_line=open_token.line,
            limit_line=close_token.line + 1,
        )

    def _parse_list(self, *, ordered: bool) -> Node:
        """Parse ordered/unordered lists (handles nesting recursively)."""
        list_indent = self._token.indent
        items: list[ListItem] = []
        marker_type = TokenType.OL_MARKER if ordered else TokenType.UL_MARKER

        while self._check(marker_type) and self._token.indent == list_indent:
            items.append(self._parse_list_item(list_indent))

        if ordered:
            return OrderedList(
                items=items,
                start_line=items[0].start_line,
                limit_line=items[-1].limit_line,
            )

        return UnorderedList(
            items=items, start_line=items[0].start_line, limit_line=items[-1].limit_line
        )

    def _parse_list_item(self, list_indent: int) -> ListItem:
        """Parse a single list item and its nested content."""
        marker_tok = self._advance()
        first_text = (
            marker_tok.value.split(maxsplit=1)[1] if " " in marker_tok.value else ""
        )

        nested_blocks = self._parse_blocks_until_indent(list_indent)

        if first_text:
            nested_blocks.insert(
                0,
                Paragraph(
                    value=[first_text],
                    start_line=marker_tok.line,
                    limit_line=marker_tok.line + 1,
                ),
            )

        return ListItem(
            blocks=nested_blocks,
            start_line=marker_tok.line,
            limit_line=self._token.line,
        )

    def _parse_quote_block(self) -> QuoteBlock:
        """Parse a > blockquote."""
        first_token = self._advance()
        lines = [first_token.value.lstrip("> ")]
        while self._check(TokenType.BLOCKQUOTE):
            lines.append(self._advance().value.lstrip("> "))
        return QuoteBlock(
            lines=lines, start_line=first_token.line, limit_line=self._token.line
        )

    def _parse_admonition(self) -> Admonition:
        """Parse !!! / ??? admonitions."""
        header_tok = self._advance()
        tag, *tail = header_tok.value.split(None, 2)
        kind = tail[0].lower() if tail else "note"
        expected_tail_length = 2
        title = tail[1].strip('"') if len(tail) == expected_tail_length else ""

        body_blocks = self._parse_blocks_until_indent(header_tok.indent)

        return Admonition(
            tag=tag,
            kind=kind,
            title=title,
            blocks=body_blocks,
            start_line=header_tok.line,
            limit_line=self._token.line,
        )

    def _parse_tab_block(self) -> TabBlock:
        """Parse === "Title" tab blocks."""
        tabs: list[Tab] = []
        while self._check(TokenType.TAB_HEADER):
            header_tok = self._advance()
            title = header_tok.value.split('"', 1)[1].rsplit('"', 1)[0]

            inner_blocks = self._parse_blocks_until_indent(header_tok.indent)

            tabs.append(
                Tab(
                    title=title,
                    blocks=inner_blocks,
                    start_line=header_tok.line,
                    limit_line=self._token.line,
                )
            )

        return TabBlock(
            tabs=tabs, start_line=tabs[0].start_line, limit_line=tabs[-1].limit_line
        )

    def _parse_html_block(self) -> HTMLBlock:
        """Collect consecutive HTML-tag lines into one block, keeping indent."""
        first_tok = self._advance()

        lines = [" " * first_tok.indent + first_tok.value]
        while self._check(TokenType.HTML_TAG):
            tok = self._advance()
            lines.append(" " * tok.indent + tok.value)

        return HTMLBlock(
            content="\n".join(lines),
            start_line=first_tok.line,
            limit_line=self._token.line,
        )

    def _parse_paragraph(self) -> Paragraph:
        """Collect consecutive TEXT tokens into a paragraph."""
        first = self._token
        text_lines: list[str] = []
        while self._check(TokenType.TEXT):
            text_lines.append(self._advance().value)
        while self._match(TokenType.BLANK):
            pass  # swallow blank lines following the paragraph
        return Paragraph(
            value=text_lines, start_line=first.line, limit_line=self._token.line
        )


# ---------------------------------------------------------------------------
# MintPrinter - AST to Mintlify markdown converter
# ---------------------------------------------------------------------------


class MintPrinter:
    """Convert AST nodes to Mintlify-formatted markdown.

    **Warning**: this is a mutable class that accumulates output in `self.output`.
    """

    def __init__(self) -> None:
        """Initialize the printer."""
        self.output: list[str] = []
        self.indent_level: int = 0

    def print(self, node: Node) -> str:
        """Convert an AST node to Mintlify markdown string."""
        self.output = []
        self.indent_level = 0
        self._visit(node)
        return "\n".join(self.output).rstrip() + "\n"

    def _add_line(self, line: str) -> None:
        """Add a line with proper indentation."""
        indent = "  " * self.indent_level
        self.output.append(f"{indent}{line}")

    def _visit(self, node: Node) -> None:
        """Visit a node and dispatch to the appropriate handler."""
        method_name = f"_visit_{type(node).__name__.lower()}"
        method = getattr(self, method_name, self._visit_generic)
        method(node)

    def _visit_generic(self, node: Node) -> None:
        """Generic visitor for unhandled nodes."""
        self._add_line(f"<!-- Unhandled node: {type(node).__name__} -->")

    def _visit_document(self, node: Document) -> None:
        """Visit a document node."""
        for i, block in enumerate(node.blocks):
            if i > 0:
                self._add_line("")
            self._visit(block)

    def _visit_heading(self, node: Heading) -> None:
        """Visit a heading node."""
        prefix = "#" * node.level
        self._add_line(f"{prefix} {node.value}")

    def _visit_paragraph(self, node: Paragraph) -> None:
        """Visit a paragraph node."""
        for i, line in enumerate(node.value):
            self._add_line(line.strip())
            if i > 0:
                self._add_line("\n")

    def _visit_codeblock(self, node: CodeBlock) -> None:
        """Visit a code block node and format for Mintlify."""
        fence = "```"

        # Build the opening fence with language and metadata
        if node.language:
            fence_line = f"{fence}{node.language}"
            if node.meta:
                fence_line = f"{fence}{node.language} {node.meta}"
        else:
            fence_line = fence

        self._add_line(fence_line)

        # Add the code content
        if node.content:
            for line in node.content.split("\n"):
                self._add_line(line)

        self._add_line(fence)

    def _visit_unorderedlist(self, node: UnorderedList) -> None:
        """Visit an unordered list node."""
        for item in node.items:
            self._visit_list_item(item, "- ")

    def _visit_orderedlist(self, node: OrderedList) -> None:
        """Visit an ordered list node."""
        for i, item in enumerate(node.items, 1):
            self._visit_list_item(item, f"{i}. ")

    def _visit_list_item(self, item: ListItem, prefix: str) -> None:
        """Visit a list item with the given prefix."""
        for i, block in enumerate(item.blocks):
            if i == 0:
                # First block gets the list marker
                if isinstance(block, Paragraph):
                    self._add_line(f"{prefix}{' '.join(block.value)}")
                else:
                    self._add_line(prefix)
                    self._visit(block)
            else:
                # Subsequent blocks are indented
                self.indent_level += 1
                self._visit(block)
                self.indent_level -= 1

    def _visit_quoteblock(self, node: QuoteBlock) -> None:
        """Visit a quote block node."""
        for line in node.lines:
            self._add_line(f"> {line}")

    def _visit_tabblock(self, node: TabBlock) -> None:
        """Visit a tab block node and convert to Mintlify <Tabs> format."""
        self._add_line("<Tabs>")

        self.indent_level += 1
        for tab in node.tabs:
            self._add_line(f'<Tab title="{tab.title}">')

            self.indent_level += 1
            for i, block in enumerate(tab.blocks):
                if i > 0:
                    self._add_line("")
                self._visit(block)
            self.indent_level -= 1

            self._add_line("</Tab>")
        self.indent_level -= 1

        self._add_line("</Tabs>")

    def _visit_tab(self, node: Tab) -> None:
        """Visit a single tab node (handled by tabblock)."""
        raise NotImplementedError

    def _visit_admonition(self, node: Admonition) -> None:
        """Visit an admonition node and convert to Mintlify format."""
        # Map common admonition types to Mintlify equivalents
        if node.tag == "???":
            # Then it's an Accordion (foldable)
            if node.title:
                self._add_line(f'<Accordion title="{node.title}">')
            else:
                self._add_line("<Accordion>")

            self.indent_level += 1
            for i, block in enumerate(node.blocks):
                if i > 0:
                    self._add_line("")
                self._visit(block)
            self.indent_level -= 1
            self._add_line("</Accordion>")
        elif node.tag == "!!!":
            kind_to_callout = {
                "note": "Note",
                "warning": "Warning",
                "info": "Info",
                "tip": "Tip",
                "danger": "Danger",
            }
            kind = node.kind.lower()
            if kind not in kind_to_callout:
                msg = f"Unsupported admonition kind: {kind}"
                raise NotImplementedError(msg)
            callout = kind_to_callout[kind]

            self._add_line(f"<{callout}>")
            self.indent_level += 1
            # as a bolded string
            if node.title:
                self._add_line(f"**{node.title}**")
            for i, block in enumerate(node.blocks):
                if i > 0:
                    self._add_line("")
                self._visit(block)
            self.indent_level -= 1
            self._add_line(f"</{callout}>")
        else:
            raise NotImplementedError

    def _visit_listitem(self, node: ListItem) -> None:
        """Visit a list item node (handled by list visitors)."""
        raise NotImplementedError

    def _visit_frontmatter(self, node: FrontMatter) -> None:
        """Remove front matter from the output."""

    def _visit_htmlblock(self, node: HTMLBlock) -> None:
        """Visit an HTML block node."""
        # Output HTML content as-is
        lines = node.content.split("\n")
        for i, line in enumerate(lines):
            if line.strip() or i == 0:
                self._add_line(line)
            else:
                self._add_line("")


def to_mint(markdown: str) -> str:
    """Convenience function to print an AST node as Mintlify markdown."""
    parser = Parser(markdown)
    doc = parser.parse()
    printer = MintPrinter()
    return printer.print(doc)
