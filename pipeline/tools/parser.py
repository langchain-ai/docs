"""Simplified Markdown parser for mapping custom commands to Mintlify syntax.

Most of this parser was generated with Claude code. It's created to help
with a quick migration from a custom markdown format to Mintlify's format and
is not meant to be perfect or handle all edge cases of Markdown syntax.

If we keep the parser, we may need to re-design the architecture a bit to separate
the tokenization from the parsing logic, which will make it simpler to handle
indentation and other nuances of Markdown syntax.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Regular expressions (compiled once, re.VERBOSE for readability)
# ---------------------------------------------------------------------------

HEADING_LINE_RE = re.compile(
    r"""
    ^ (?P<hashes>\#{1,6})      # 1-6 leading “#” characters
      \s+                      # mandatory space
      (?P<text>.*) $           # heading text (rest of line)
    """,
    re.VERBOSE,
)

HEADING_PREFIX_RE = re.compile(
    r"""
    ^ \#{1,6} \s+              # quick detect for a heading
    """,
    re.VERBOSE,
)

TAB_HEADER_RE = re.compile(
    r"""
    ^ ===                      # tab header marker
      \s*                      # optional space
      "(?P<title>[^"]+)"       # title in double quotes
    """,
    re.VERBOSE,
)

UNORDERED_MARKER_RE = re.compile(
    r"""
    ^ (?P<indent>\s*)          # leading indentation
      (?P<marker>[-+*]) \s+    # “- ”, “+ ”, or “* ”
    """,
    re.VERBOSE,
)

ORDERED_MARKER_RE = re.compile(
    r"""
    ^ (?P<indent>\s*)          # leading indentation
      (?P<num>\d+)             # number
      (?P<delim>[.)]) \s+      # “.” or “)” after the number
    """,
    re.VERBOSE,
)

HTML_TAG_RE = re.compile(
    r"""
    ^ \s* <                    # optional whitespace, then <
      (?P<closing>/?)          # optional closing slash
      (?P<tag>[a-zA-Z][a-zA-Z0-9-]*) # tag name
      (?:\s[^>]*)?             # optional attributes
      (?P<self_closing>/?)     # optional self-closing slash
      >                        # closing >
    """,
    re.VERBOSE,
)

PARA_BREAK_RE = re.compile(
    r"""
    (?:
        ```                    # code-fence
      | \#{1,6}\s+             # heading
      | [-+*]\s+               # unordered list
      | \d+[.)]\s+             # ordered list
      | >\s*                   # blockquote
      | !!!                    # admonition
      | \?\?\?                 # foldable admonition
      | :::                    # directive fence
      | \s*<[a-zA-Z]           # HTML tag
    )
    """,
    re.VERBOSE,
)
# ---------------------------------------------------------------------------
# AST node definitions
# ---------------------------------------------------------------------------


@dataclass(kw_only=True)
class Node:
    """Base class for all AST nodes."""

    start_line: int
    limit_line: int


@dataclass(kw_only=True)
class Document(Node):
    """Root document node containing all blocks."""

    blocks: list[Node]


@dataclass(kw_only=True)
class Heading(Node):
    """Heading node with level (1-6) and text content."""

    level: int
    value: str


@dataclass(kw_only=True)
class Paragraph(Node):
    """Paragraph node containing text content."""

    value: list[str]


@dataclass(kw_only=True)
class CodeBlock(Node):
    """Code block with optional language and metadata."""

    language: str | None
    meta: str
    content: str


@dataclass(kw_only=True)
class ListItem(Node):
    """Single item in a list containing nested blocks."""

    blocks: list[Node]


@dataclass(kw_only=True)
class UnorderedList(Node):
    """Unordered list (bullet list) containing list items."""

    items: list[ListItem]


@dataclass(kw_only=True)
class OrderedList(Node):
    """Ordered list (numbered list) containing list items."""

    items: list[ListItem]


@dataclass(kw_only=True)
class QuoteBlock(Node):
    """Block quote containing multiple lines of text."""

    lines: list[str]


@dataclass(kw_only=True)
class Tab(Node):
    """Single tab in a tab block with title and content."""

    title: str
    blocks: list[Node]


@dataclass(kw_only=True)
class TabBlock(Node):
    """Tab block containing multiple tabs."""

    tabs: list[Tab]


@dataclass(kw_only=True)
class Admonition(Node):
    """Admonition block (note, warning, etc.) with optional folding."""

    tag: str  # '???' or '!!!'
    kind: str  # 'note', 'warning', etc.
    title: str
    blocks: list[Node]


@dataclass(kw_only=True)
class FrontMatter(Node):
    """YAML front matter block."""

    content: str


@dataclass(kw_only=True)
class HTMLBlock(Node):
    """HTML block that can span multiple lines."""

    content: str


# ---------------------------------------------------------------------------
# Parser implementation
# ---------------------------------------------------------------------------


class Parser:
    """Parse the supported markdown subset into an AST suitable for Mintlify."""

    def __init__(self, text: str) -> None:
        """Initialize parser with markdown text."""
        self.lines = text.splitlines()
        self.current = 0
        self.total = len(self.lines)

    # -- helpers ------------------------------------------------------------
    def eof(self) -> bool:
        """Check if the parser has reached the end of input."""
        return self.current >= self.total

    def peek(self) -> str:
        """Return the current line without advancing the parser."""
        return "" if self.eof() else self.lines[self.current]

    def next_line(self) -> str:
        """Return the current line and advance to the next."""
        line = self.peek()
        self.current += 1
        return line

    # -- entry point --------------------------------------------------------
    def parse(self) -> Document:
        """Parse the markdown text into a Document AST."""
        blocks: list[Node] = []

        # Check for front matter at the beginning
        if not self.eof() and self.peek().strip() == "---":
            front_matter = self.parse_front_matter()
            if front_matter is not None:
                blocks.append(front_matter)

        while not self.eof():
            block = self.parse_block()
            if block is not None:
                blocks.append(block)
        return Document(blocks=blocks, start_line=1, limit_line=self.total + 1)

    # -- block dispatcher ---------------------------------------------------
    def parse_block(self) -> Node | None:  # noqa: PLR0911 (too-many-returns)
        """Parse a single block element based on the current line."""
        line = self.peek()

        if not line:
            self.next_line()
            return None
        if line.startswith("```"):
            return self.parse_code_block()
        if HEADING_PREFIX_RE.match(line):
            return self.parse_heading()
        if UNORDERED_MARKER_RE.match(line):
            return self.parse_unordered_list()
        if ORDERED_MARKER_RE.match(line):
            return self.parse_ordered_list()
        if line.startswith(">"):
            return self.parse_quote_block()
        if line.startswith(("!!!", "???")):
            return self.parse_admonition()
        if line.startswith("==="):
            return self.parse_tab_block()
        if HTML_TAG_RE.match(line):
            return self.parse_html_block()
        return self.parse_paragraph()

    def parse_front_matter(self) -> FrontMatter | None:
        """Parse YAML front matter block."""
        if self.peek().strip() != "---":
            return None

        start_ln = self.current + 1
        self.next_line()  # consume opening ---

        content_lines: list[str] = []
        while not self.eof():
            line = self.peek()
            if line.strip() == "---":
                self.next_line()  # consume closing ---
                break
            content_lines.append(line)
            self.next_line()

        content = "\n".join(content_lines)
        return FrontMatter(
            content=content, start_line=start_ln, limit_line=self.current + 1
        )

    def parse_html_block(self) -> HTMLBlock:
        """Parse an HTML block, tracking tag nesting to find the end."""
        start_ln = self.current + 1
        lines: list[str] = []
        tag_stack: list[str] = []

        while not self.eof():
            line = self.peek()
            lines.append(line)
            self.next_line()

            # Find all HTML tags in this line
            for match in HTML_TAG_RE.finditer(line):
                is_closing = bool(match.group("closing"))
                tag_name = match.group("tag").lower()
                is_self_closing = bool(match.group("self_closing")) or tag_name in {
                    "area",
                    "base",
                    "br",
                    "col",
                    "embed",
                    "hr",
                    "img",
                    "input",
                    "link",
                    "meta",
                    "source",
                    "track",
                    "wbr",
                }

                if is_self_closing:
                    continue
                if is_closing:
                    # Remove matching opening tag from stack
                    if tag_stack and tag_stack[-1] == tag_name:
                        tag_stack.pop()
                else:
                    # Add opening tag to stack
                    tag_stack.append(tag_name)

            # If we've closed all tags, we're done
            if not tag_stack:
                break

        content = "\n".join(lines)
        return HTMLBlock(
            content=content, start_line=start_ln, limit_line=self.current + 1
        )

    # -- individual block parsers ------------------------------------------
    def parse_code_block(self) -> CodeBlock:
        """Parse a fenced code block with optional language and metadata."""
        start_ln = self.current + 1
        fence_line = self.next_line().strip()
        fence_body = fence_line[3:].strip()
        if fence_body:
            parts = fence_body.split(None, 1)
            language = parts[0]
            meta = parts[1] if len(parts) > 1 else ""
        else:
            language = None
            meta = ""
        content: list[str] = []
        while not self.eof():
            line = self.next_line()
            if line.strip().startswith("```"):
                break
            content.append(line)
        end_ln = self.current + 1
        return CodeBlock(
            language=language,
            meta=meta,
            content="\n".join(content),
            start_line=start_ln,
            limit_line=end_ln,
        )

    def parse_heading(self) -> Heading:
        """Parse a heading line (# through ######)."""
        start_ln = self.current + 1
        line = self.next_line().strip()
        m = HEADING_LINE_RE.match(line)
        if not m:
            return Heading(
                level=1, value=line, start_line=start_ln, limit_line=start_ln + 1
            )
        level = len(m.group("hashes"))
        text = m.group("text")
        return Heading(
            level=level, value=text, start_line=start_ln, limit_line=start_ln + 1
        )

    # ----- lists -----------------------------------------------------------
    def _collect_list_items(self, marker_re: re.Pattern[str]) -> list[ListItem]:
        """Collect consecutive list items matching the given marker pattern."""
        items: list[ListItem] = []
        while not self.eof() and marker_re.match(self.peek()):
            items.append(self._parse_list_item(marker_re))
        return items

    def _parse_list_item(self, marker_re: re.Pattern[str]) -> ListItem:
        """Parse a single list item, including any indented content."""
        start_ln = self.current + 1

        # Parse the first line of the list item
        line = self.peek()
        match = marker_re.match(line)
        if not match:
            error_msg = "Expected list marker"
            raise ValueError(error_msg)

        # Get the indentation level of the list marker
        marker_indent = (
            len(match.group("indent")) if "indent" in match.groupdict() else 0
        )
        text = marker_re.sub("", line, count=1).rstrip()
        self.next_line()

        # Start with the main text as a paragraph
        blocks: list[Node] = []
        if text.strip():
            blocks.append(
                Paragraph(value=[text], start_line=start_ln, limit_line=start_ln + 1)
            )

        # Collect any indented content that belongs to this list item
        while not self.eof():
            line = self.peek()

            # If line is empty, skip it but continue looking for indented content
            if not line.strip():
                self.next_line()
                continue

            # Check if this line starts a new list item at the same level
            match_result = marker_re.match(line)
            if match_result:
                new_marker_indent = (
                    len(match_result.group("indent"))
                    if "indent" in match_result.groupdict()
                    else 0
                )
                if new_marker_indent == marker_indent:
                    break  # This is a new list item at the same level

            # Check if this line is indented more than the marker (belongs to this item)
            line_indent = len(line) - len(line.lstrip())
            min_required_indent = marker_indent + 4  # Standard markdown indentation

            if line_indent >= min_required_indent:
                # This line belongs to the current list item
                # Collect all consecutive indented lines and parse them as a
                # sub-document
                indented_lines: list[str] = []

                while not self.eof():
                    line = self.peek()
                    if not line.strip():  # Empty line
                        indented_lines.append(line)
                        self.next_line()
                        continue

                    # Check if this starts a new list item at the same level
                    match_result = marker_re.match(line)
                    if match_result:
                        new_marker_indent = (
                            len(match_result.group("indent"))
                            if "indent" in match_result.groupdict()
                            else 0
                        )
                        if new_marker_indent == marker_indent:
                            break

                    line_indent = len(line) - len(line.lstrip())
                    if line_indent >= min_required_indent:
                        # Remove the base indentation to normalize the content
                        if len(line) >= min_required_indent:
                            indented_lines.append(line[min_required_indent:])
                        else:
                            indented_lines.append(line.lstrip())
                        self.next_line()
                    else:
                        break

                # Parse the indented content as a sub-document
                if indented_lines:
                    # Remove trailing empty lines
                    while indented_lines and not indented_lines[-1].strip():
                        indented_lines.pop()

                    if indented_lines:
                        sub_content = "\n".join(indented_lines)
                        sub_parser = Parser(sub_content)
                        sub_doc = sub_parser.parse()
                        blocks.extend(sub_doc.blocks)
                break
            # This line is not indented enough, so it doesn't belong to this list item
            break

        return ListItem(blocks=blocks, start_line=start_ln, limit_line=self.current + 1)

    def parse_unordered_list(self) -> UnorderedList:
        """Parse an unordered list (bullets: -, +, *)."""
        start_ln = self.current + 1
        items = self._collect_list_items(UNORDERED_MARKER_RE)
        return UnorderedList(
            items=items, start_line=start_ln, limit_line=self.current + 1
        )

    def parse_ordered_list(self) -> OrderedList:
        """Parse an ordered list (numbered: 1., 2), etc.)."""
        start_ln = self.current + 1
        items = self._collect_list_items(ORDERED_MARKER_RE)
        return OrderedList(
            items=items, start_line=start_ln, limit_line=self.current + 1
        )

    # ----- quote -----------------------------------------------------------
    def parse_quote_block(self) -> QuoteBlock:
        """Parse a block quote (lines starting with >)."""
        start_ln = self.current + 1
        lines: list[str] = []
        while not self.eof() and self.peek().lstrip().startswith(">"):
            lines.append(self.peek().lstrip()[1:].lstrip())
            self.next_line()
        return QuoteBlock(lines=lines, start_line=start_ln, limit_line=self.current + 1)

    # ----- admonition ------------------------------------------------------
    def parse_admonition(self) -> Admonition:
        """Parse an admonition block (!!! or ??? with indented content)."""
        start_ln = self.current + 1
        header = self.next_line().strip()
        parts = header.split(None, 2)

        num_parts = len(parts)

        if num_parts == 2:  # noqa: PLR2004
            tag, kind = parts
            title = ""
        elif num_parts == 3:  # noqa: PLR2004
            # This is the case where we have a title
            tag, kind, title = parts
            title = title.strip('"')  # strip quotes around title
        else:
            msg = "Invalid admonition header format"
            raise NotImplementedError(msg)

        if tag not in {"!!!", "???"}:
            msg = f"Invalid admonition type: {tag}"
            raise NotImplementedError(msg)

        kind = kind.lower()

        if kind not in {"note", "warning", "info", "tip", "example"}:
            msg = f"Unsupported admonition type: {kind}"
            raise NotImplementedError(msg)

        # skip blank lines
        while not self.eof() and not self.peek().strip():
            self.next_line()
        body_lines: list[str] = []

        # Collect all indented content, handling block boundaries properly
        while not self.eof():
            line = self.peek()

            # If line is completely empty, include it and continue
            if not line.strip():
                body_lines.append(line)
                self.next_line()
                continue

            # If line is not indented at all, we've reached the end of the admonition
            if not line.startswith(("    ", "\t")):
                break

            # Remove the base indentation and add to body
            if line.startswith("    "):
                body_lines.append(line[4:])
            elif line.startswith("\t"):
                body_lines.append(line[1:])
            else:
                body_lines.append(line.lstrip())
            self.next_line()

        # Remove trailing empty lines
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()

        inner = Parser("\n".join(body_lines)).parse()
        return Admonition(
            tag=tag,
            kind=kind,
            title=title,
            blocks=inner.blocks,
            start_line=start_ln,
            limit_line=self.current + 1,
        )

    # ----- tabs ------------------------------------------------------------
    def parse_tab_block(self) -> TabBlock:
        """Parse a tab block with multiple === "title" sections."""
        start_ln = self.current + 1
        tabs: list[Tab] = []
        while not self.eof() and TAB_HEADER_RE.match(self.peek()):
            header_ln = self.current + 1
            m = TAB_HEADER_RE.match(self.next_line())
            if m is None:
                error_msg = "Expected tab header match"
                raise ValueError(error_msg)
            # m is guaranteed to be not None after this check
            title = m.group("title")
            # skip blank lines before content
            while not self.eof() and not self.peek().strip():
                self.next_line()
            content: list[str] = []

            # Collect all indented content, handling empty lines properly
            while not self.eof():
                line = self.peek()

                # Check if this is the start of a new tab
                if TAB_HEADER_RE.match(line):
                    break

                # If line is completely empty, include it and continue
                if not line.strip():
                    content.append(line)
                    self.next_line()
                    continue

                # If line is not indented at all, we've reached the end of this tab
                if not line.startswith(("    ", "\t")):
                    break

                # Remove the base indentation and add to content
                if line.startswith("    "):
                    content.append(line[4:])
                elif line.startswith("\t"):
                    content.append(line[1:])
                else:
                    content.append(line.lstrip())
                self.next_line()

            # Remove trailing empty lines
            while content and not content[-1].strip():
                content.pop()

            inner = Parser("\n".join(content)).parse()
            tabs.append(
                Tab(
                    title=title,
                    blocks=inner.blocks,
                    start_line=header_ln,
                    limit_line=self.current + 1,
                )
            )
        return TabBlock(tabs=tabs, start_line=start_ln, limit_line=self.current + 1)

    # ----- paragraph -------------------------------------------------------
    def parse_paragraph(self) -> Paragraph:
        """Parse a paragraph from consecutive non-empty lines."""
        start_ln = self.current + 1
        lines: list[str] = []
        while not self.eof():
            line = self.peek()
            if not line.strip() or PARA_BREAK_RE.match(line):
                break
            lines.append(line.strip())
            self.next_line()
        return Paragraph(value=lines, start_line=start_ln, limit_line=self.current + 1)


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
        return "\n".join(self.output).rstrip()

    def _add_line(self, line: str) -> None:
        """Add a line with proper indentation."""
        if line.strip():
            indent = "  " * self.indent_level
            self.output.append(f"{indent}{line}")
        else:
            self.output.append("")

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
                # Handle special Mintlify syntax like [expandable] and line highlighting
                if "[expandable]" in node.meta:
                    fence_line = f"{fence}{node.language} {node.meta}"
                elif "{" in node.meta and "}" in node.meta:
                    # Line highlighting syntax
                    fence_line = f"{fence}{node.language} {node.meta}"
                else:
                    # Regular filename or title
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
        """Visit a front matter node (ignored in output)."""
        # Front matter is ignored in Mintlify output

    def _visit_htmlblock(self, node: HTMLBlock) -> None:
        """Visit an HTML block node."""
        # Output HTML content as-is
        for line in node.content.split("\n"):
            self._add_line(line)


def to_mint(markdown: str) -> str:
    """Convenience function to print an AST node as Mintlify markdown."""
    parser = Parser(markdown)
    doc = parser.parse()
    printer = MintPrinter()
    return printer.print(doc)
