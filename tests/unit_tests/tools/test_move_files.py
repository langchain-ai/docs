"""Unit tests for pipeline.tools.move_files module."""

import json
from pathlib import Path

import pytest

from pipeline.tools.move_files import (
    _find_git_root,
    _LinkChange,
    _rel_to_docs_root,
    _rewrite_links,
    _scan_and_rewrite,
    _write_changes_log,
    move_file_with_link_updates,
)
from tests.unit_tests.utils import File, temp_directory


class TestFindGitRoot:
    """Tests for _find_git_root function."""

    def test_find_git_root_success(self) -> None:
        """Test finding git root when .git directory exists."""
        files: list[File] = [{"path": ".git/config", "content": "[core]\n"}]
        with temp_directory(files) as temp_dir:
            result = _find_git_root(temp_dir)
            assert result == temp_dir

    def test_find_git_root_from_subdirectory(self) -> None:
        """Test finding git root from a subdirectory."""
        files: list[File] = [
            {"path": ".git/config", "content": "[core]\n"},
            {"path": "subdir/file.md", "content": "# Test"},
        ]
        with temp_directory(files) as temp_dir:
            result = _find_git_root(temp_dir / "subdir")
            assert result == temp_dir

    def test_find_git_root_not_found(self) -> None:
        """Test RuntimeError when no .git directory is found."""
        files: list[File] = [{"path": "file.md", "content": "# Test"}]
        with (
            temp_directory(files) as temp_dir,
            pytest.raises(RuntimeError, match="Could not locate Git repository"),
        ):
            _find_git_root(temp_dir)


class TestRelToDocsRoot:
    """Tests for _rel_to_docs_root function."""

    def test_rel_to_docs_root(self) -> None:
        """Test calculating relative path to docs root."""
        files: list[File] = [{"path": "subdir/file.md", "content": "# Test"}]
        with temp_directory(files) as temp_dir:
            file_path = temp_dir / "subdir" / "file.md"
            result = _rel_to_docs_root(file_path, temp_dir)
            assert result == Path("subdir/file.md")


class TestRewriteLinks:
    """Tests for _rewrite_links function."""

    def test_rewrite_relative_link(self) -> None:
        """Test rewriting a relative link when file is moved."""
        files: list[File] = [
            {"path": "page1.md", "content": "See [page 2](page2.md) for details."},
            {"path": "page2.md", "content": "# Page 2"},
        ]
        with temp_directory(files) as temp_dir:
            changes: list[_LinkChange] = []
            old_abs = temp_dir / "page2.md"
            new_abs = temp_dir / "subdir" / "page2.md"
            md_file = temp_dir / "page1.md"

            _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
                changes=changes,
                dry_run=False,
            )

            # Check that the link was updated
            updated_content = md_file.read_text(encoding="utf-8")
            assert "See [page 2](subdir/page2.md) for details." in updated_content
            assert changes == [("page2.md", "subdir/page2.md")]

    def test_rewrite_multiple_links(self) -> None:
        """Test rewriting multiple links to the same file."""
        files: list[File] = [
            {
                "path": "index.md",
                "content": "See [link1](target.md) and [link2](target.md).",
            },
            {"path": "target.md", "content": "# Target"},
        ]
        with temp_directory(files) as temp_dir:
            changes: list[_LinkChange] = []
            old_abs = temp_dir / "target.md"
            new_abs = temp_dir / "new" / "target.md"
            md_file = temp_dir / "index.md"

            _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
                changes=changes,
                dry_run=False,
            )

            updated_content = md_file.read_text(encoding="utf-8")
            assert (
                "See [link1](new/target.md) and [link2](new/target.md)."
                in updated_content
            )
            assert changes == [
                ("target.md", "new/target.md"),
                ("target.md", "new/target.md"),
            ]

    def test_skip_external_links(self) -> None:
        """Test that external links are not modified."""
        files: list[File] = [
            {
                "path": "page.md",
                "content": (
                    "See [external](https://example.com) and "
                    "[email](mailto:test@example.com) and "
                    "[anchor](#section)."
                ),
            }
        ]
        with temp_directory(files) as temp_dir:
            changes: list[_LinkChange] = []
            old_abs = temp_dir / "nonexistent.md"
            new_abs = temp_dir / "new.md"
            md_file = temp_dir / "page.md"

            original_content = md_file.read_text(encoding="utf-8")
            _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
                changes=changes,
                dry_run=False,
            )

            updated_content = md_file.read_text(encoding="utf-8")
            assert updated_content == original_content
            assert changes == []

    def test_dry_run_mode(self) -> None:
        """Test that dry run mode doesn't modify files."""
        files: list[File] = [
            {"path": "page1.md", "content": "See [page 2](page2.md) for details."},
            {"path": "page2.md", "content": "# Page 2"},
        ]
        with temp_directory(files) as temp_dir:
            changes: list[_LinkChange] = []
            old_abs = temp_dir / "page2.md"
            new_abs = temp_dir / "subdir" / "page2.md"
            md_file = temp_dir / "page1.md"

            original_content = md_file.read_text(encoding="utf-8")
            _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
                changes=changes,
                dry_run=True,
            )

            # File should be unchanged in dry run
            updated_content = md_file.read_text(encoding="utf-8")
            assert updated_content == original_content
            # But changes should still be tracked
            assert changes == [("page2.md", "subdir/page2.md")]

    def test_rewrite_links_with_anchors(self) -> None:
        """Test rewriting links that include anchors."""
        files: list[File] = [
            {
                "path": "page1.md",
                "content": (
                    "See [section 1](target.md#section1) and "
                    "[section 2](target.md#section2)."
                ),
            },
            {"path": "target.md", "content": "# Target\n## Section 1\n## Section 2"},
        ]
        with temp_directory(files) as temp_dir:
            changes: list[_LinkChange] = []
            old_abs = temp_dir / "target.md"
            new_abs = temp_dir / "foo" / "b.md"
            md_file = temp_dir / "page1.md"

            _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
                changes=changes,
                dry_run=False,
            )

            # Check that the links with anchors were updated
            updated_content = md_file.read_text(encoding="utf-8")
            assert (
                "See [section 1](foo/b.md#section1) and [section 2](foo/b.md#section2)."
            ) in updated_content

            # Check that changes tracked the full URLs including anchors
            expected_changes = [
                ("target.md#section1", "foo/b.md#section1"),
                ("target.md#section2", "foo/b.md#section2"),
            ]
            assert changes == expected_changes

    def test_rewrite_links_in_mdx_files(self) -> None:
        """Test that links in .mdx files are also rewritten."""
        files: list[File] = [
            {
                "path": "page.mdx",
                "content": (
                    "import Component from './component.js'\n\n"
                    "See [documentation](docs.md) and [guide](guide.md#setup).\n\n"
                    "<Component />"
                ),
            },
            {"path": "docs.md", "content": "# Documentation"},
            {"path": "guide.md", "content": "# Guide\n## Setup"},
        ]
        with temp_directory(files) as temp_dir:
            changes: list[_LinkChange] = []

            # Test rewriting links to docs.md
            old_abs = temp_dir / "docs.md"
            new_abs = temp_dir / "reference" / "docs.md"
            mdx_file = temp_dir / "page.mdx"

            _rewrite_links(
                mdx_file,
                old_abs,
                new_abs,
                temp_dir,
                changes=changes,
                dry_run=False,
            )

            # Check that the link was updated in the .mdx file
            updated_content = mdx_file.read_text(encoding="utf-8")
            assert "See [documentation](reference/docs.md)" in updated_content
            assert (
                "[guide](guide.md#setup)" in updated_content
            )  # Should remain unchanged
            assert (
                "import Component from './component.js'" in updated_content
            )  # Should remain unchanged
            assert "<Component />" in updated_content  # Should remain unchanged

            # Check that changes were tracked
            assert changes == [("docs.md", "reference/docs.md")]


class TestScanAndRewrite:
    """Tests for _scan_and_rewrite function."""

    def test_scan_multiple_files(self) -> None:
        """Test scanning and rewriting links across multiple files."""
        files: list[File] = [
            {"path": "page1.md", "content": "See [target](target.md)."},
            {"path": "page2.md", "content": "Also see [target](target.md)."},
            {"path": "subdir/page3.md", "content": "Check [target](../target.md)."},
            {"path": "target.md", "content": "# Target"},
        ]
        with temp_directory(files) as temp_dir:
            old_abs = temp_dir / "target.md"
            new_abs = temp_dir / "moved" / "target.md"

            changes = _scan_and_rewrite(temp_dir, old_abs, new_abs, dry_run=False)

            # Check all files were updated
            page1_content = (temp_dir / "page1.md").read_text(encoding="utf-8")
            assert "See [target](moved/target.md)." in page1_content

            page2_content = (temp_dir / "page2.md").read_text(encoding="utf-8")
            assert "Also see [target](moved/target.md)." in page2_content

            page3_content = (temp_dir / "subdir" / "page3.md").read_text(
                encoding="utf-8"
            )
            assert "Check [target](../moved/target.md)." in page3_content

            # Check changes were tracked
            expected_changes = [
                ("target.md", "moved/target.md"),
                ("target.md", "moved/target.md"),
                ("../target.md", "../moved/target.md"),
            ]
            assert changes == expected_changes

    def test_scan_includes_mdx_files(self) -> None:
        """Test that _scan_and_rewrite processes both .md and .mdx files."""
        files: list[File] = [
            {"path": "page.md", "content": "See [target](target.md)."},
            {"path": "component.mdx", "content": "Check [target](target.md) in MDX."},
            {"path": "target.md", "content": "# Target"},
        ]
        with temp_directory(files) as temp_dir:
            old_abs = temp_dir / "target.md"
            new_abs = temp_dir / "docs" / "target.md"

            changes = _scan_and_rewrite(temp_dir, old_abs, new_abs, dry_run=False)

            # Check both .md and .mdx files were updated
            md_content = (temp_dir / "page.md").read_text(encoding="utf-8")
            assert "See [target](docs/target.md)." in md_content

            mdx_content = (temp_dir / "component.mdx").read_text(encoding="utf-8")
            assert "Check [target](docs/target.md) in MDX." in mdx_content

            # Check changes from both file types were tracked
            expected_changes = [
                ("target.md", "docs/target.md"),
                ("target.md", "docs/target.md"),
            ]
            assert changes == expected_changes


class TestWriteChangesLog:
    """Tests for _write_changes_log function."""

    def test_write_changes_log(self) -> None:
        """Test writing changes to log file."""
        files: list[File] = []
        with temp_directory(files) as temp_dir:
            changes = [("old1.md", "new1.md"), ("old2.md", "new2.md")]
            _write_changes_log(changes, temp_dir)

            log_path = temp_dir / "link_changes.jsonl"
            assert log_path.exists()

            lines = log_path.read_text(encoding="utf-8").strip().split("\n")
            assert len(lines) == 2
            assert json.loads(lines[0]) == ["old1.md", "new1.md"]
            assert json.loads(lines[1]) == ["old2.md", "new2.md"]

    def test_write_changes_log_empty(self) -> None:
        """Test that empty changes don't create a log file."""
        files: list[File] = []
        with temp_directory(files) as temp_dir:
            _write_changes_log([], temp_dir)
            log_path = temp_dir / "link_changes.jsonl"
            assert not log_path.exists()

    def test_write_changes_log_append(self) -> None:
        """Test that changes are appended to existing log file."""
        files: list[File] = []
        with temp_directory(files) as temp_dir:
            # Write first batch of changes
            changes1 = [("old1.md", "new1.md")]
            _write_changes_log(changes1, temp_dir)

            # Write second batch of changes
            changes2 = [("old2.md", "new2.md")]
            _write_changes_log(changes2, temp_dir)

            log_path = temp_dir / "link_changes.jsonl"
            lines = log_path.read_text(encoding="utf-8").strip().split("\n")
            assert len(lines) == 2
            assert json.loads(lines[0]) == ["old1.md", "new1.md"]
            assert json.loads(lines[1]) == ["old2.md", "new2.md"]


class TestMoveFileWithLinkUpdates:
    """Tests for move_file_with_link_updates function."""

    def test_move_file_with_link_updates_dry_run(self) -> None:
        """Test complete file move operation in dry run mode."""
        files: list[File] = [
            {"path": ".git/config", "content": "[core]\n"},
            {"path": "src/page1.md", "content": "See [page 2](page2.md)."},
            {"path": "src/page2.md", "content": "# Page 2"},
        ]
        with temp_directory(files) as temp_dir:
            src_dir = temp_dir / "src"
            old_path = src_dir / "page2.md"
            new_path = src_dir / "moved" / "page2.md"

            changes = move_file_with_link_updates(
                old_path,
                new_path,
                dry_run=True,
                git_root=temp_dir,
                docs_root=src_dir,
            )

            # File should not be moved in dry run
            assert old_path.exists()
            assert not new_path.exists()

            # But links should be tracked for potential changes
            assert changes == [("page2.md", "moved/page2.md")]

    def test_move_file_with_link_updates_actual_move(self) -> None:
        """Test complete file move operation with actual file movement."""
        files: list[File] = [
            {"path": ".git/config", "content": "[core]\n"},
            {"path": "src/page1.md", "content": "See [page 2](page2.md)."},
            {"path": "src/page2.md", "content": "# Page 2"},
        ]
        with temp_directory(files) as temp_dir:
            src_dir = temp_dir / "src"
            old_path = src_dir / "page2.md"
            new_path = src_dir / "moved" / "page2.md"

            changes = move_file_with_link_updates(
                old_path,
                new_path,
                dry_run=False,
                git_root=temp_dir,
                docs_root=src_dir,
            )

            # File should be moved
            assert not old_path.exists()
            assert new_path.exists()
            assert new_path.read_text(encoding="utf-8") == "# Page 2"

            # Links should be updated
            page1_content = (src_dir / "page1.md").read_text(encoding="utf-8")
            assert "See [page 2](moved/page2.md)." in page1_content

            # Changes should be tracked
            assert changes == [("page2.md", "moved/page2.md")]

            # Log file should be created
            log_path = temp_dir / "link_changes.jsonl"
            assert log_path.exists()

    def test_move_file_invalid_docs_root(self) -> None:
        """Test RuntimeError when docs root doesn't exist."""
        files: list[File] = [{"path": ".git/config", "content": "[core]\n"}]
        with temp_directory(files) as temp_dir:
            old_path = temp_dir / "page.md"
            new_path = temp_dir / "new.md"
            invalid_docs_root = temp_dir / "nonexistent"

            with pytest.raises(RuntimeError, match="Expected docs root"):
                move_file_with_link_updates(
                    old_path,
                    new_path,
                    git_root=temp_dir,
                    docs_root=invalid_docs_root,
                )
