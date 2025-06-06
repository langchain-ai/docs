"""Simplified Markdown parser for mapping custom commands to Mintlify syntax."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

# ---------------------------------------------------------------------------
# Regular expressions (compiled once, re.VERBOSE for readability)
# ---------------------------------------------------------------------------

HEADING_LINE_RE = re.compile(
    r"^(?P<hashes>#{1,6})"  # 1‑6 leading "#" characters
    r"\s+"  # mandatory space
    r"(?P<text>.*)$",  # heading text (rest of line)
    re.VERBOSE,
)

HEADING_PREFIX_RE = re.compile(
    r"^#{1,6}\s+",  # quick detect for a heading
    re.VERBOSE,
)

TAB_HEADER_RE = re.compile(
    r"^==="  # tab header marker
    r"\s*"  # optional space
    r"\"(?P<title>[^\"]+)\"",  # title in quotes
    re.VERBOSE,
)

UNORDERED_MARKER_RE = re.compile(
    r"^(?P<indent>\s*)(?P<marker>[-+*])\s+",  # "- ", "+ ", or "* "
    re.VERBOSE,
)

ORDERED_MARKER_RE = re.compile(
    r"^(?P<indent>\s*)(?P<num>\d+)(?P<delim>[\.)])\s+",  # "1. " / "2) "
    re.VERBOSE,
)

PARA_BREAK_RE = re.compile(
    r"(?:```"  # code fence
    r"|#{1,6}\s+"  # heading
    r"|[-+*]\s+"  # unordered list
    r"|\d+[\.)]\s+"  # ordered list
    r"|>\s*"  # blockquote
    r"|!!!"  # admonition
    r"|\?\?\?"  # foldable admonition
    r"|:::"  # directive fence
    r")",
    re.VERBOSE,
)

# ---------------------------------------------------------------------------
# AST node definitions
# ---------------------------------------------------------------------------


@dataclass
class Node:
    start_line: int
    limit_line: int


@dataclass
class Document(Node):
    blocks: List["Node"]


@dataclass
class Heading(Node):
    level: int
    value: str


@dataclass
class Paragraph(Node):
    value: str


@dataclass
class CodeBlock(Node):
    language: Optional[str]
    meta: str
    content: str


@dataclass
class ListItem(Node):
    blocks: List["Node"]


@dataclass
class UnorderedList(Node):
    items: List[ListItem]


@dataclass
class OrderedList(Node):
    items: List[ListItem]


@dataclass
class QuoteBlock(Node):
    lines: List[str]


@dataclass
class Tab(Node):
    title: str
    blocks: List["Node"]


@dataclass
class TabBlock(Node):
    tabs: List[Tab]


@dataclass
class Admonition(Node):
    tag: str  # '???' or '!!!'
    title: str
    blocks: List["Node"]
    foldable: bool


# ---------------------------------------------------------------------------
# Parser implementation
# ---------------------------------------------------------------------------


class Parser:
    """Parse the supported markdown subset into an AST suitable for Mintlify."""

    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.current = 0
        self.total = len(self.lines)

    # -- helpers ------------------------------------------------------------
    def eof(self) -> bool:
        return self.current >= self.total

    def peek(self) -> str:
        return "" if self.eof() else self.lines[self.current]

    def next_line(self) -> str:
        line = self.peek()
        self.current += 1
        return line

    # -- entry point --------------------------------------------------------
    def parse(self) -> Document:
        blocks: List[Node] = []
        while not self.eof():
            block = self.parse_block()
            if block is not None:
                blocks.append(block)
        return Document(blocks=blocks, start_line=1, limit_line=self.total + 1)

    # -- block dispatcher ---------------------------------------------------
    def parse_block(self) -> Optional[Node]:
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
        if line.startswith("!!!") or line.startswith("???"):
            return self.parse_admonition()
        if line.startswith("==="):
            return self.parse_tab_block()
        return self.parse_paragraph()

    # -- individual block parsers ------------------------------------------
    def parse_code_block(self) -> CodeBlock:
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
        content: List[str] = []
        while not self.eof():
            line = self.next_line()
            if line.strip().startswith("```"):
                break
            content.append(line)
        end_ln = self.current + 1
        return CodeBlock(language=language, meta=meta, "\n".join(content), start_ln, end_ln)

    def parse_heading(self) -> Heading:
        start_ln = self.current + 1
        line = self.next_line().strip()
        m = HEADING_LINE_RE.match(line)
        if not m:
            return Heading(1, line, start_ln, start_ln + 1)
        level = len(m.group("hashes"))
        text = m.group("text")
        return Heading(level, text, start_ln, start_ln + 1)

    # ----- lists -----------------------------------------------------------
    def _collect_list_items(self, marker_re: re.Pattern[str]) -> List[ListItem]:
        items: List[ListItem] = []
        while not self.eof() and marker_re.match(self.peek()):
            ln = self.current + 1
            text = marker_re.sub("", self.peek(), count=1).rstrip()
            para = Paragraph(text, ln, ln + 1)
            items.append(ListItem([para], ln, ln + 1))
            self.next_line()
        return items

    def parse_unordered_list(self) -> UnorderedList:
        start_ln = self.current + 1
        items = self._collect_list_items(UNORDERED_MARKER_RE)
        return UnorderedList(items, start_ln, self.current + 1)

    def parse_ordered_list(self) -> OrderedList:
        start_ln = self.current + 1
        items = self._collect_list_items(ORDERED_MARKER_RE)
        return OrderedList(items, start_ln, self.current + 1)

    # ----- quote -----------------------------------------------------------
    def parse_quote_block(self) -> QuoteBlock:
        start_ln = self.current + 1
        lines: List[str] = []
        while not self.eof() and self.peek().lstrip().startswith(">"):
            lines.append(self.peek().lstrip()[1:].lstrip())
            self.next_line()
        return QuoteBlock(lines, start_ln, self.current + 1)

    # ----- admonition ------------------------------------------------------
    def parse_admonition(self) -> Admonition:
        start_ln = self.current + 1
        header = self.next_line().strip()
        parts = header.split(None, 1)
        tag = parts[0]
        title = parts[1].strip('"') if len(parts) > 1 else ""
        # skip blank lines
        while not self.eof() and not self.peek().strip():
            self.next_line()
        body_lines: List[str] = []
        while not self.eof() and (
            self.peek().startswith("    ") or self.peek().startswith("\t")
        ):
            body_lines.append(self.next_line().lstrip())
        inner = Parser("\n".join(body_lines)).parse()
        return Admonition(tag, title, inner.blocks, False, start_ln, self.current + 1)

    # ----- tabs ------------------------------------------------------------
    def parse_tab_block(self) -> TabBlock:
        start_ln = self.current + 1
        tabs: List[Tab] = []
        while not self.eof() and TAB_HEADER_RE.match(self.peek()):
            header_ln = self.current + 1
            m = TAB_HEADER_RE.match(self.next_line())
            assert m is not None
            title = m.group("title")
            # skip blank lines before content
            while not self.eof() and not self.peek().strip():
                self.next_line()
            content: List[str] = []
            while (
                not self.eof()
                and not TAB_HEADER_RE.match(self.peek())
                and not self.peek().strip() == ""
            ):
                # Accept content lines that are indented (Mintlify expects 4‑sp)
                if self.peek().startswith("    ") or self.peek().startswith("\t"):
                    content.append(self.next_line().lstrip())
                else:
                    break
            inner = Parser("\n".join(content)).parse()
            tabs.append(Tab(title, inner.blocks, header_ln, self.current + 1))
        return TabBlock(tabs, start_ln, self.current + 1)

    # ----- paragraph -------------------------------------------------------
    def parse_paragraph(self) -> Paragraph:
        start_ln = self.current + 1
        lines: List[str] = []
        while not self.eof():
            line = self.peek()
            if not line.strip() or PARA_BREAK_RE.match(line):
                break
            lines.append(line.strip())
            self.next_line()
        return Paragraph(" ".join(lines), start_ln, self.current + 1)
