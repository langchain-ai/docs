"""Tests for the markdown parser."""

from pipeline.tools.parser import (
    Document,
    FrontMatter,
    Heading,
    Paragraph,
    Parser,
    to_mint,
)


def test_parse_simple_heading() -> None:
    """Test parsing a simple heading."""
    text = "# Hello World"
    parser = Parser(text)
    doc = parser.parse()

    assert isinstance(doc, Document)
    assert len(doc.blocks) == 1

    heading = doc.blocks[0]
    assert isinstance(heading, Heading)
    assert heading.level == 1
    assert heading.value == "Hello World"
    assert heading.start_line == 1
    assert heading.limit_line == 2


def test_parse_simple_paragraph() -> None:
    """Test parsing a simple paragraph."""
    text = "This is a simple paragraph."
    parser = Parser(text)
    doc = parser.parse()

    assert isinstance(doc, Document)
    assert len(doc.blocks) == 1

    paragraph = doc.blocks[0]
    assert isinstance(paragraph, Paragraph)
    assert paragraph.value == ["This is a simple paragraph."]
    assert paragraph.start_line == 1
    assert paragraph.limit_line == 2


MARKDOWN1 = """\
??? example "Example Title"

    Foldable example
"""

EXPECTED_MARKDOWN = """\
<Accordion title="Example Title">
Foldable example
</Accordion>"""


def test_example_blocks() -> None:
    """Test the Mintlify printer."""
    output = to_mint(MARKDOWN1)
    assert output == EXPECTED_MARKDOWN


def test_parse_front_matter() -> None:
    """Test parsing front matter."""
    text = """---
title: Overview
search:
  boost: 2
tags:
  - agent
hide:
  - tags
---

# Hello World

This is content."""
    parser = Parser(text)
    doc = parser.parse()

    assert isinstance(doc, Document)
    assert len(doc.blocks) == 3

    # First block should be front matter
    front_matter = doc.blocks[0]
    assert isinstance(front_matter, FrontMatter)
    expected_content = """title: Overview
search:
  boost: 2
tags:
  - agent
hide:
  - tags"""
    assert front_matter.content == expected_content

    # Second block should be heading
    heading = doc.blocks[1]
    assert isinstance(heading, Heading)
    assert heading.value == "Hello World"

    # Third block should be paragraph
    paragraph = doc.blocks[2]
    assert isinstance(paragraph, Paragraph)
    assert paragraph.value == ["This is content."]


def test_front_matter_ignored_in_output() -> None:
    """Test that front matter is ignored in Mintlify output."""
    text = """---
title: Overview
---

# Hello World"""
    expected = "# Hello World"
    output = to_mint(text)
    assert output == expected
