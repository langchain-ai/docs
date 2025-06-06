"""Tests for the markdown parser."""

from pipeline.tools.parser import Document, Heading, Paragraph, Parser


def test_parse_simple_heading():
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


def test_parse_simple_paragraph():
    """Test parsing a simple paragraph."""
    text = "This is a simple paragraph."
    parser = Parser(text)
    doc = parser.parse()

    assert isinstance(doc, Document)
    assert len(doc.blocks) == 1

    paragraph = doc.blocks[0]
    assert isinstance(paragraph, Paragraph)
    assert paragraph.value == "This is a simple paragraph."
    assert paragraph.start_line == 1
    assert paragraph.limit_line == 2
