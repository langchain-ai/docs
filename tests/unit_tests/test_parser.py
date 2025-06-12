"""Tests for the markdown parser."""

from pipeline.tools.parser import (
    CodeBlock,
    Document,
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


# This is a set of tests that verifies end-to-end functionality from parsing markdown
# to converting it to Mintlify format.

MARKDOWN1 = """\
??? example "Example Title"
    Foldable example
"""

EXPECTED_MARKDOWN = """\
<Accordion title="Example Title">
  Foldable example
</Accordion>
"""


def test_example_admonition() -> None:
    """Test the Mintlify printer."""
    output = to_mint(MARKDOWN1)
    assert output == EXPECTED_MARKDOWN


EXAMPLE_ADMONITION_BLANK = """\
??? example "Example Title"

    Paragraph 1

    Paragraph 2
"""

EXPECTED_ADMONITION_BLANK = """\
<Accordion title="Example Title">
  Paragraph 1

  Paragraph 2
</Accordion>
"""


def test_example_admonition_with_blank_line() -> None:
    """Test the Mintlify printer with a blank line after admonition."""
    assert to_mint(EXAMPLE_ADMONITION_BLANK) == EXPECTED_ADMONITION_BLANK


INPUT_FRONT_MATTER = """\
---
title: Example Document
other_field: value
---
# Example Heading
This is a simple document with front matter.
"""

EXPECTED_FRONT_MATTER = """\
---
title: Example Document
other_field: value
---
# Example Heading
This is a simple document with front matter.
"""


def test_front_matter_ignored_in_output() -> None:
    """Test that front matter is ignored in Mintlify output."""
    assert to_mint(INPUT_FRONT_MATTER) == EXPECTED_FRONT_MATTER


INPUT_WITH_TABS = """\
=== "Python"
    Content with tabs

=== "javascript"

    Other content with tabs
"""

EXPECTED_TABS = """\
<Tabs>
  <Tab title="Python">
    Content with tabs
  </Tab>
  <Tab title="javascript">
    Other content with tabs
  </Tab>
</Tabs>
"""


def test_tabs() -> None:
    """Test parsing with tabs."""
    assert to_mint(INPUT_WITH_TABS) == EXPECTED_TABS


INPUT_WITH_CODE_BLOCK = """\
```python
print("Hello, World!")
```
"""

EXPECTED_CODE_BLOCK = """\
```python
print("Hello, World!")
```
"""


def test_code_block() -> None:
    """Test parsing a code block."""
    assert to_mint(INPUT_WITH_CODE_BLOCK) == EXPECTED_CODE_BLOCK


INPUT_CODE_BLOCK_WITH_EXTRAS = """\
```python hl_lines="1-2"
print("Hello, World!")
print("This is a test.")
```
"""

EXPECTED_CODE_BLOCK_WITH_EXTRAS = """\
```python hl_lines="1-2"
print("Hello, World!")
print("This is a test.")
```
"""


def test_code_block_with_extras() -> None:
    """Test parsing a code block with extra lines."""
    assert to_mint(INPUT_CODE_BLOCK_WITH_EXTRAS) == EXPECTED_CODE_BLOCK_WITH_EXTRAS


INPUT_WITH_UNORDERED_LIST = """\
# Example List

- Item 1
- Item 2
- Item 3
"""

EXPECTED_UNORDERED_LIST = """\
# Example List

- Item 1
- Item 2
- Item 3
"""


def test_unordered_list() -> None:
    """Test parsing an unordered list."""
    assert to_mint(INPUT_WITH_UNORDERED_LIST) == EXPECTED_UNORDERED_LIST


INPUT_WITH_ORDERED_LIST = """\
# Example Ordered List

1. First item
2. Second item
3. Third item
"""

EXPECTED_ORDERED_LIST = """\
# Example Ordered List

1. First item
2. Second item
3. Third item
"""


def test_ordered_list() -> None:
    """Test parsing an ordered list."""
    assert to_mint(INPUT_WITH_ORDERED_LIST) == EXPECTED_ORDERED_LIST


INPUT_WITH_BLOCKQUOTE = """\
> Example Blockquote
> More text in the blockquote.
"""

EXPECTED_BLOCKQUOTE = """\
> Example Blockquote
> More text in the blockquote.
"""


def test_blockquote() -> None:
    """Test parsing a blockquote."""
    assert to_mint(INPUT_WITH_BLOCKQUOTE) == EXPECTED_BLOCKQUOTE


INPUT_WITH_HTML = """\
<div>
    <p>This is a paragraph inside a div.</p>
</div>
"""

EXPECTED_HTML = """\
<div>
    <p>This is a paragraph inside a div.</p>
</div>
"""


def test_html() -> None:
    """Test parsing HTML content."""
    assert to_mint(INPUT_WITH_HTML) == EXPECTED_HTML


INPUT_CODE_BLOCK_IN_TAB = """\
=== "Python"

    ```python
    def hello_world():
        print("Hello, World!")
    ```
"""

EXPECTED_CODE_BLOCK_IN_TAB = """\
<Tabs>
  <Tab title="Python">
    ```python
    def hello_world():
        print("Hello, World!")
    ```
  </Tab>
</Tabs>
"""


def test_code_block_in_tab() -> None:
    """Test parsing a code block inside a tab."""
    assert to_mint(INPUT_CODE_BLOCK_IN_TAB) == EXPECTED_CODE_BLOCK_IN_TAB


INPUT_CODE_FENCE = """\
``` 
def example_function():
    print("This is an example function.")
```
"""  # noqa: W291

EXPECTED_CODE_FENCE = """\
```
def example_function():
    print("This is an example function.")
```
"""


def test_code_fence() -> None:
    """Test parsing a code fence."""
    assert to_mint(INPUT_CODE_FENCE) == EXPECTED_CODE_FENCE


INPUT_CODE_BLOCK_WITH_BLANK_LINE = """\
```python
def foo():
    x = 1
    
    y = 2
```
"""  # noqa: W293


def test_long_code_block() -> None:
    """Test parsing a long code block."""
    ast = Parser(INPUT_CODE_BLOCK_WITH_BLANK_LINE).parse()
    first_block = ast.blocks[0]
    assert isinstance(first_block, CodeBlock)
    assert first_block.language == "python"
    assert first_block.content == "def foo():\n    x = 1\n    \n    y = 2"
