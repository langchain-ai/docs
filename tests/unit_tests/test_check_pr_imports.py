"""Tests for `check_pr_imports.py`."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scripts.check_pr_imports import (
    analyze_diff,
    build_mapping_dict,
    check_import_line,
    load_import_mappings,
)


def test_load_existing_mappings() -> None:
    """Test loading existing import mappings file."""
    test_data = {
        "metadata": {"langchain_version": "1.0.0"},
        "analysis": [],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name

    # Mock Path to return temp file
    with patch("scripts.check_pr_imports.Path") as mock_path:
        mock_path.return_value.exists.return_value = True
        temp_file_path = Path(temp_path)
        mock_path.return_value.open.return_value.__enter__ = (
            lambda _: temp_file_path.open()
        )
        mock_path.return_value.open.return_value.__exit__ = Mock(return_value=None)

        # Mock the stat method due to file size check
        mock_stat = Mock()
        mock_stat.st_size = 100  # Small file size
        mock_path.return_value.stat.return_value = mock_stat

        result = load_import_mappings()
        assert result == test_data

    # Clean up
    Path(temp_path).unlink()


def test_missing_mappings_file() -> None:
    """Test behavior when mappings file doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use a non-existent file path
        nonexistent_file = Path(temp_dir) / "nonexistent.json"

        with patch("scripts.check_pr_imports.Path") as mock_path:
            mock_path.return_value = nonexistent_file

            with patch("builtins.print") as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    load_import_mappings()

                assert exc_info.value.code == 1
                mock_print.assert_called_once()


def test_build_mapping_dict_empty() -> None:
    """Test building mapping dictionary with empty analysis."""
    mappings: dict[str, list] = {"analysis": []}
    result = build_mapping_dict(mappings)
    assert result == {}


def test_build_mapping_dict_no_exports() -> None:
    """Test building mapping dictionary with no exported_from_core."""
    mappings = {
        "analysis": [
            {
                "file": "/temp/langchain/messages/__init__.py",
                "exported_from_core": {},
            }
        ]
    }
    result = build_mapping_dict(mappings)
    assert result == {}


def test_build_mapping_dict_invalid_path() -> None:
    """Test building mapping dictionary with invalid file path."""
    mappings = {
        "analysis": [
            {
                "file": "/invalid/path/without/lc/__init__.py",
                "exported_from_core": {
                    "HumanMessage": {
                        "module": "langchain_core.messages",
                        "original_name": "HumanMessage",
                    },
                },
            }
        ]
    }
    result = build_mapping_dict(mappings)
    # Should be empty because "langchain" is not in the path
    assert result == {}


def test_build_mapping_dict_basic() -> None:
    """Test building mapping dictionary from analysis data."""
    mappings = {
        "analysis": [
            {
                "file": "/temp/langchain/messages/__init__.py",
                "exported_from_core": {
                    "HumanMessage": {
                        "module": "langchain_core.messages",
                        "original_name": "HumanMessage",
                    },
                    "AIMessage": {
                        "module": "langchain_core.messages",
                        "original_name": "AIMessage",
                    },
                },
            },
            {
                "file": "/temp/langchain/tools/__init__.py",
                "exported_from_core": {
                    "tool": {
                        "module": "langchain_core.tools",
                        "original_name": "tool",
                    },
                },
            },
        ]
    }

    # Mock validate_path to always return True for test paths
    with patch("scripts.check_pr_imports.validate_path", return_value=True):
        result = build_mapping_dict(mappings)

    expected = {
        "langchain_core.messages.HumanMessage": "langchain.messages.HumanMessage",
        "langchain_core.messages.AIMessage": "langchain.messages.AIMessage",
        "langchain_core.messages": "langchain.messages",
        "langchain_core.tools.tool": "langchain.tools.tool",
        "langchain_core.tools": "langchain.tools",
    }

    assert result == expected


@pytest.fixture
def mapping_dict() -> dict[str, str]:
    """Test mapping dictionary fixture."""
    return {
        "langchain_core.messages": "langchain.messages",
        "langchain_core.messages.HumanMessage": "langchain.messages.HumanMessage",
        "langchain_core.messages.AIMessage": "langchain.messages.AIMessage",
        "langchain_core.tools": "langchain.tools",
        "langchain_core.tools.tool": "langchain.tools.tool",
    }


def test_from_import_module_mapping(mapping_dict: dict[str, str]) -> None:
    """Test from import with module-level mapping."""
    line = "from langchain_core.messages import HumanMessage"
    issues = check_import_line(line, mapping_dict)

    assert len(issues) == 1
    issue = issues[0]
    assert issue["original"] == line
    assert issue["suggested"] == "from langchain.messages import HumanMessage"
    assert "Import from langchain.messages instead" in issue["reason"]


def test_from_import_multiple_items(mapping_dict: dict[str, str]) -> None:
    """Test from import with multiple items."""
    line = "from langchain_core.messages import HumanMessage, AIMessage"
    issues = check_import_line(line, mapping_dict)

    assert len(issues) == 1
    issue = issues[0]
    assert issue["original"] == line
    expected_suggestion = "from langchain.messages import HumanMessage, AIMessage"
    assert issue["suggested"] == expected_suggestion


def test_from_import_with_alias(mapping_dict: dict[str, str]) -> None:
    """Test from import with alias."""
    line = "from langchain_core.messages import HumanMessage as HM"
    issues = check_import_line(line, mapping_dict)

    assert len(issues) == 1
    issue = issues[0]
    assert issue["original"] == line
    assert issue["suggested"] == "from langchain.messages import HumanMessage as HM"


def test_direct_import(mapping_dict: dict[str, str]) -> None:
    """Test direct module import."""
    line = "import langchain_core.messages"
    issues = check_import_line(line, mapping_dict)

    assert len(issues) == 1
    issue = issues[0]
    assert issue["original"] == line
    assert issue["suggested"] == "import langchain.messages"
    assert "Import langchain.messages instead" in issue["reason"]


def test_no_mapping_found(mapping_dict: dict[str, str]) -> None:
    """Test line with no mapping available."""
    line = "from langchain_core.unknown import Something"
    issues = check_import_line(line, mapping_dict)
    assert len(issues) == 0


def test_non_langchain_core_import(mapping_dict: dict[str, str]) -> None:
    """Test line that doesn't import from `langchain_core`.

    e.g. an already correct import.
    """
    line = "from langchain.messages import HumanMessage"
    issues = check_import_line(line, mapping_dict)
    assert len(issues) == 0


def test_analyze_simple_diff(mapping_dict: dict[str, str]) -> None:
    """Test analyzing a simple diff with one issue."""
    diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 import os
+from langchain_core.messages import HumanMessage

 def main():
"""

    issues = analyze_diff(diff, mapping_dict)

    assert len(issues) == 1
    issue = issues[0]
    assert issue["file"] == "test.py"
    assert issue["line"] == 2
    assert issue["original"] == "from langchain_core.messages import HumanMessage"
    assert issue["suggested"] == "from langchain.messages import HumanMessage"


def test_analyze_multiple_files_diff(mapping_dict: dict[str, str]) -> None:
    """Test analyzing diff with multiple files."""
    diff = """diff --git a/file1.py b/file1.py
index 1234567..abcdefg 100644
--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,3 @@
 import os
+from langchain_core.messages import HumanMessage
diff --git a/file2.py b/file2.py
index 2345678..bcdefgh 100644
--- a/file2.py
+++ b/file2.py
@@ -10,3 +10,4 @@ def func():
     pass

+import langchain_core.messages
"""

    issues = analyze_diff(diff, mapping_dict)

    assert len(issues) == 2

    # First issue
    assert issues[0]["file"] == "file1.py"
    assert issues[0]["line"] == 2
    assert issues[0]["original"] == "from langchain_core.messages import HumanMessage"

    # Second issue
    assert issues[1]["file"] == "file2.py"
    assert issues[1]["line"] == 12
    assert issues[1]["original"] == "import langchain_core.messages"


def test_analyze_diff_no_issues(mapping_dict: dict[str, str]) -> None:
    """Test analyzing diff with no import issues."""
    diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 import os
+from langchain.messages import HumanMessage

 def main():
"""

    issues = analyze_diff(diff, mapping_dict)
    assert len(issues) == 0


def test_analyze_diff_removed_lines(mapping_dict: dict[str, str]) -> None:
    """Test analyzing diff with removed lines (should be ignored)."""
    diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,4 +1,3 @@
 import os
-from langchain_core.messages import HumanMessage

 def main():
"""

    issues = analyze_diff(diff, mapping_dict)
    assert len(issues) == 0


def test_analyze_empty_diff(mapping_dict: dict[str, str]) -> None:
    """Test analyzing empty diff."""
    issues = analyze_diff("", mapping_dict)
    assert len(issues) == 0


def test_from_import_direct_langchain_core(mapping_dict: dict[str, str]) -> None:
    """Test direct import from langchain_core package (no submodule)."""
    line = "from langchain_core import AIMessage, SystemMessage"
    issues = check_import_line(line, mapping_dict)

    # This should find issues but currently doesn't due to regex bug
    # Once the bug is fixed, this test should pass
    assert len(issues) == 1
    issue = issues[0]
    assert issue["original"] == line
    # Should suggest importing from langchain.messages
    assert "langchain.messages" in issue["suggested"]


def test_analyze_diff_direct_langchain_core_import(
    mapping_dict: dict[str, str],
) -> None:
    """Test analyzing diff with direct langchain_core import (reproduces the bug)."""
    diff = """diff --git a/src/oss/langchain/models.mdx b/src/oss/langchain/models.mdx
index d51f18f8a..077e9ba03 100644
--- a/src/oss/langchain/models.mdx
+++ b/src/oss/langchain/models.mdx
@@ -1438,6 +1438,7 @@ If a model invokes a tool server-side, content will
 :::python
 ```python Invoke with server-side tool use
 from langchain.chat_models import init_chat_model
+from langchain_core import AIMessage, SystemMessage

 model = init_chat_model("gpt-4.1-mini")
"""

    issues = analyze_diff(diff, mapping_dict)

    # This should find the issue but currently doesn't due to regex bug
    assert len(issues) == 1
    issue = issues[0]
    assert issue["file"] == "src/oss/langchain/models.mdx"
    assert issue["original"] == "from langchain_core import AIMessage, SystemMessage"
    assert "langchain.messages" in issue["suggested"]
