"""Simplified Markdown parser for mapping custom commands to Mintlify syntax."""
import re
from dataclasses import dataclass
from typing import List, Optional, Union


# AST node definitions with start_line and limit_line
@dataclass
class Node:
    start_line: int
    limit_line: int


@dataclass
class Document(Node):
    blocks: List[Node]


@dataclass
class TextInline(Node):
    value: str


@dataclass
class LinkInline(Node):
    text: str
    url: str


Inline = Union[TextInline, LinkInline]


@dataclass
class Heading(Node):
    level: int
    inlines: List[Inline]


@dataclass
class Paragraph(Node):
    inlines: List[Inline]


@dataclass
class CodeBlock(Node):
    language: Optional[str]
    content: str


@dataclass
class ListItem(Node):
    blocks: List[Node]


@dataclass
class BulletList(Node):
    items: List[ListItem]


@dataclass
class QuoteBlock(Node):
    lines: List[str]


@dataclass
class Tab(Node):
    title: str
    blocks: List[Node]


@dataclass
class TabBlock(Node):
    tabs: List[Tab]


@dataclass
class Admonition(Node):
    tag: str  # '???' or '!!!'
    title: str
    blocks: List[Node]
    foldable: bool


class Parser:
    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.current = 0
        self.total = len(self.lines)

    def eof(self) -> bool:
        return self.current >= self.total

    def peek(self) -> str:
        return "" if self.eof() else self.lines[self.current]

    def next_line(self) -> str:
        line = self.peek()
        self.current += 1
        return line

    def parse(self) -> Document:
        blocks: List[Node] = []
        while not self.eof():
            block = self.parse_block()
            if block:
                blocks.append(block)
        return Document(blocks=blocks, start_line=1, limit_line=self.total + 1)

    def parse_block(self) -> Optional[Node]:
        line = self.peek()
        # Skip blank lines
        if not line:
            self.next_line()
            return None
        # Code fence
        if line.startswith("```"):
            return self.parse_code_block()
        # Heading
        if re.match(r"#{1,6}\s+", line):
            return self.parse_heading()
        # Bullet list
        if line.startswith(("- ", "+ ", "* ")):
            return self.parse_bullet_list()
        # Blockquote
        if line.startswith(">"):
            return self.parse_quote_block()
        # Admonition
        if line.startswith("!!!") or line.startswith("???"):
            return self.parse_admonition()
        # Tab block
        if line.startswith("==="):
            return self.parse_simple_tab_block()
        # Paragraph
        return self.parse_paragraph()

    def parse_code_block(self) -> CodeBlock:
        start_ln = self.current + 1
        fence = self.next_line().strip()
        lang = fence[3:].strip() or None
        content_lines: List[str] = []
        while not self.eof():
            line = self.next_line()
            if line.strip().startswith("```"):
                break
            content_lines.append(line)
        end_ln = self.current + 1
        content = "\n".join(content_lines)
        return CodeBlock(
            language=lang, content=content, start_line=start_ln, limit_line=end_ln
        )

    def parse_heading(self) -> Heading:
        start_ln = self.current + 1
        line = self.next_line().strip()
        end_ln = self.current + 1
        m = re.match(r"(#{1,6})\s+(.*)", line)
        level = len(m.group(1))
        text = m.group(2)
        inlines = self.parse_inlines(text, start_ln)
        return Heading(
            level=level, inlines=inlines, start_line=start_ln, limit_line=end_ln
        )

    def parse_bullet_list(self) -> BulletList:
        start_ln = self.current + 1
        items: List[ListItem] = []
        while not self.eof():
            line = self.peek()
            if not line.strip().startswith("- "):
                break
            ln = self.current + 1
            content = line.strip()[2:].strip()
            inlines = self.parse_inlines(content, ln)
            para = Paragraph(inlines=inlines, start_line=ln, limit_line=ln + 1)
            items.append(ListItem(blocks=[para], start_line=ln, limit_line=ln + 1))
            self.next_line()
        end_ln = self.current + 1
        return BulletList(items=items, start_line=start_ln, limit_line=end_ln)

    def parse_quote_block(self) -> QuoteBlock:
        start_ln = self.current + 1
        lines: List[str] = []
        while not self.eof():
            line = self.peek()
            if not line.lstrip().startswith(">"):
                break
            content = line.lstrip()[1:].lstrip()
            lines.append(content)
            self.next_line()
        end_ln = self.current + 1
        return QuoteBlock(lines=lines, start_line=start_ln, limit_line=end_ln)

    def parse_admonition(self) -> Admonition:
        start_ln = self.current + 1
        header = self.next_line().strip()
        parts = header.split(None, 1)
        tag = parts[0]
        title = parts[1].strip('"') if len(parts) > 1 else ""
        # skip blank line
        while not self.eof() and self.peek().strip() == "":
            self.next_line()
        content_lines: List[str] = []
        while not self.eof():
            line = self.peek()
            if line.startswith("    ") or line.startswith("\t"):
                content_lines.append(line.lstrip())
                self.next_line()
            else:
                break
        end_ln = self.current + 1
        inner = Parser("\n".join(content_lines)).parse()
        return Admonition(
            tag=tag,
            title=title,
            blocks=inner.blocks,
            foldable=False,
            start_line=start_ln,
            limit_line=end_ln,
        )

    def parse_simple_tab_block(self) -> TabBlock:
        start_ln = self.current + 1
        tabs: List[Tab] = []
        # Loop over consecutive tab headers
        while not self.eof():
            # Skip any blank lines between tabs
            while not self.eof() and not self.peek().strip():
                self.next_line()
            if self.eof():
                break
            line = self.peek().strip()
            m = re.match(r"===\s*\"([^\"]+)\"", line)
            if not m:
                break
            title = m.group(1)
            tab_start = self.current + 1
            self.next_line()  # consume the header
            # Skip blank lines before content
            while not self.eof() and not self.peek().strip():
                self.next_line()
            # Collect indented lines as content
            content_lines: List[str] = []
            while not self.eof() and (
                self.peek().startswith("    ") or self.peek().startswith("\t")
            ):
                content_lines.append(self.peek().lstrip())
                self.next_line()
            # Parse inner content
            inner = Parser("\n".join(content_lines)).parse()
            tab_end = self.current + 1
            tabs.append(
                Tab(
                    title=title,
                    blocks=inner.blocks,
                    start_line=tab_start,
                    limit_line=tab_end,
                )
            )
        end_ln = self.current + 1
        return TabBlock(tabs=tabs, start_line=start_ln, limit_line=end_ln)

    def parse_paragraph(self) -> Paragraph:
        start_ln = self.current + 1
        lines: List[str] = []
        while not self.eof():
            line = self.peek()
            if not line.strip() or re.match(
                r"(?:```|#{1,6}\s+|-\s+|>\s*|!!!|\?\?\?|:::)", line.strip()
            ):
                break
            lines.append(line.strip())
            self.next_line()
        end_ln = self.current + 1
        text = " ".join(lines)
        inlines = self.parse_inlines(text, start_ln)
        return Paragraph(inlines=inlines, start_line=start_ln, limit_line=end_ln)

    def parse_inlines(self, text: str, line: int) -> List[Inline]:
        inlines: List[Inline] = []
        pos = 0
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
            if m.start() > pos:
                inlines.append(
                    TextInline(
                        value=text[pos : m.start()],
                        start_line=line,
                        limit_line=line + 1,
                    )
                )
            inlines.append(
                LinkInline(
                    text=m.group(1),
                    url=m.group(2),
                    start_line=line,
                    limit_line=line + 1,
                )
            )
            pos = m.end()
        if pos < len(text):
            inlines.append(
                TextInline(value=text[pos:], start_line=line, limit_line=line + 1)
            )
        return inlines
