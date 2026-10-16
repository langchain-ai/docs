"""Unit tests for pipeline.tools.move_files module."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from pipeline.tools.links import (
    _build_route_map,
    _find_git_root,
    _rel_to_docs_root,
    _rewrite_docs_json,
    _rewrite_links,
    _rewrite_links_in_notebook,
    _rewrite_route_links,
    _route_forms,
    _scan_and_rewrite,
    _update_internal_links_in_moved_file,
    _update_internal_links_in_moved_notebook,
    move_file_with_link_updates,
)
from tests.unit_tests.utils import File, temp_directory


class TestRouteForms:
    """Tests for _route_forms function."""

    def test_plain_page(self) -> None:
        """Test a LangSmith page is reached by its path alone."""
        assert _route_forms(Path("langsmith/page.mdx")) == {
            "unversioned": "/langsmith/page"
        }

    def test_shared_oss_page(self) -> None:
        """Test a shared OSS page is reached unversioned and per language."""
        assert _route_forms(Path("oss/langchain/agents.mdx")) == {
            "unversioned": "/oss/langchain/agents",
            "python": "/oss/python/langchain/agents",
            "javascript": "/oss/javascript/langchain/agents",
        }

    def test_language_specific_oss_page(self) -> None:
        """Test a language-specific OSS page keeps its own language only."""
        assert _route_forms(Path("oss/python/integrations/chat/openai.mdx")) == {
            "python": "/oss/python/integrations/chat/openai",
            "unversioned": "/oss/integrations/chat/openai",
        }

    @pytest.mark.parametrize(
        "rel_path", ["oss/deepagents/code/overview.mdx", "oss/openwiki/index.mdx"]
    )
    def test_unversioned_oss_product(self, rel_path: str) -> None:
        """Test Deep Agents Code and OpenWiki pages have no language routes."""
        assert set(_route_forms(Path(rel_path))) == {"unversioned"}

    def test_managed_deep_agents_page(self) -> None:
        """Test a Managed Deep Agents page is reached by its language routes."""
        assert _route_forms(Path("langsmith/managed-deep-agents-cli.mdx")) == {
            "unversioned": "/langsmith/managed-deep-agents-cli",
            "python": "/langsmith/python/managed-deep-agents-cli",
            "javascript": "/langsmith/javascript/managed-deep-agents-cli",
        }


class TestBuildRouteMap:
    """Tests for _build_route_map function."""

    def test_shared_oss_page_keeps_each_form(self) -> None:
        """Test each link form maps to the same form at the destination."""
        with temp_directory([]) as temp_dir:
            route_map = _build_route_map(
                Path("oss/langchain/old.mdx"), Path("oss/langchain/new.mdx"), temp_dir
            )
        assert route_map == {
            "/oss/langchain/old": "/oss/langchain/new",
            "/oss/python/langchain/old": "/oss/python/langchain/new",
            "/oss/javascript/langchain/old": "/oss/javascript/langchain/new",
        }

    def test_unversioned_link_with_counterpart_is_left(self) -> None:
        """Test an unversioned link that also reaches the other language is skipped."""
        files: list[File] = [
            {"path": "oss/javascript/integrations/chat/openai.mdx", "content": ""}
        ]
        with temp_directory(files) as temp_dir:
            route_map = _build_route_map(
                Path("oss/python/integrations/chat/openai.mdx"),
                Path("oss/python/integrations/chat/openai-new.mdx"),
                temp_dir,
            )
        assert route_map == {
            "/oss/python/integrations/chat/openai": (
                "/oss/python/integrations/chat/openai-new"
            )
        }

    def test_unversioned_link_without_counterpart_is_rewritten(self) -> None:
        """Test an unversioned link that reaches only this page is rewritten."""
        with temp_directory([]) as temp_dir:
            route_map = _build_route_map(
                Path("oss/python/integrations/chat/only.mdx"),
                Path("oss/python/integrations/chat/only-new.mdx"),
                temp_dir,
            )
        assert route_map["/oss/integrations/chat/only"] == (
            "/oss/integrations/chat/only-new"
        )

    def test_form_missing_at_destination_is_left(self) -> None:
        """Test a JavaScript link is skipped when the page moves into Python."""
        with temp_directory([]) as temp_dir:
            route_map = _build_route_map(
                Path("oss/langchain/page.mdx"),
                Path("oss/python/langchain/page.mdx"),
                temp_dir,
            )
        assert "/oss/javascript/langchain/page" not in route_map

    def test_language_form_maps_to_plain_destination(self) -> None:
        """Test language links collapse to the path when the destination has none."""
        with temp_directory([]) as temp_dir:
            route_map = _build_route_map(
                Path("langsmith/managed-deep-agents-old.mdx"),
                Path("langsmith/old.mdx"),
                temp_dir,
            )
        assert route_map["/langsmith/python/managed-deep-agents-old"] == (
            "/langsmith/old"
        )


_ROUTE_MAP: dict[str, str] = {"/langsmith/old": "/langsmith/new"}


class TestRewriteRouteLinks:
    """Tests for _rewrite_route_links function."""

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("[a](/langsmith/old)", "[a](/langsmith/new)"),
            ("[a](/langsmith/old#step-2)", "[a](/langsmith/new#step-2)"),
            ('[a](/langsmith/old "Title")', '[a](/langsmith/new "Title")'),
            ("[a](/langsmith/old/)", "[a](/langsmith/new/)"),
            ('<Card href="/langsmith/old">', '<Card href="/langsmith/new">'),
            ("[a](/langsmith/old-other)", "[a](/langsmith/old-other)"),
            ("[a](/langsmith/old/child)", "[a](/langsmith/old/child)"),
            ("Use /langsmith/old in prose.", "Use /langsmith/old in prose."),
        ],
    )
    def test_rewrite(self, text: str, expected: str) -> None:
        """Test only exact route matches are rewritten, keeping the rest."""
        assert _rewrite_route_links(text, _ROUTE_MAP)[0] == expected

    def test_index_page_by_folder_route(self) -> None:
        """Test a link to an index page by its folder route is rewritten."""
        route_map = {"/oss/guide/index": "/oss/handbook/index"}
        text, changes = _rewrite_route_links("[a](/oss/guide)", route_map)
        assert text == "[a](/oss/handbook)"
        assert changes == [("/oss/guide", "/oss/handbook")]


class TestRewriteDocsJson:
    """Tests for _rewrite_docs_json function."""

    def test_rewrites_nav_and_destination_not_source(self) -> None:
        """Test nav entries and redirect destinations move; sources stay."""
        docs_json = {
            "navigation": {"pages": ["langsmith/old", "langsmith/other"]},
            "redirects": [
                {"source": "/langsmith/old", "destination": "/langsmith/x"},
                {"source": "/langsmith/legacy", "destination": "/langsmith/old#a"},
            ],
        }
        files: list[File] = [
            {"path": "docs.json", "content": json.dumps(docs_json, indent=2)}
        ]
        with temp_directory(files) as temp_dir:
            changes = _rewrite_docs_json(
                temp_dir, {"/langsmith/old": "/langsmith/new"}, dry_run=False
            )
            result = json.loads((temp_dir / "docs.json").read_text(encoding="utf-8"))
        assert result["navigation"]["pages"] == ["langsmith/new", "langsmith/other"]
        assert result["redirects"][0]["source"] == "/langsmith/old"
        assert result["redirects"][1]["destination"] == "/langsmith/new#a"
        assert len(changes) == 2


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

    def test_find_git_root_worktree(self) -> None:
        """Test finding git root when .git is a file, as in a worktree."""
        files: list[File] = [
            {"path": ".git", "content": "gitdir: /repo/.git/worktrees/wt\n"},
            {"path": "subdir/file.md", "content": "# Test"},
        ]
        with temp_directory(files) as temp_dir:
            result = _find_git_root(temp_dir / "subdir")
            assert result == temp_dir

    def test_find_git_root_worktree_inside_checkout(self) -> None:
        """Test a worktree nested in a checkout resolves to the worktree."""
        files: list[File] = [
            {"path": ".git/config", "content": "[core]\n"},
            {"path": ".worktrees/wt/.git", "content": "gitdir: ../../.git\n"},
            {"path": ".worktrees/wt/src/file.md", "content": "# Test"},
        ]
        with temp_directory(files) as temp_dir:
            result = _find_git_root(temp_dir / ".worktrees/wt/src")
            assert result == temp_dir / ".worktrees/wt"

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
            old_abs = temp_dir / "page2.md"
            new_abs = temp_dir / "subdir" / "page2.md"
            md_file = temp_dir / "page1.md"

            changes = _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
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
            old_abs = temp_dir / "target.md"
            new_abs = temp_dir / "new" / "target.md"
            md_file = temp_dir / "index.md"

            changes = _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
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
            old_abs = temp_dir / "nonexistent.md"
            new_abs = temp_dir / "new.md"
            md_file = temp_dir / "page.md"

            original_content = md_file.read_text(encoding="utf-8")
            changes = _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
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
            old_abs = temp_dir / "page2.md"
            new_abs = temp_dir / "subdir" / "page2.md"
            md_file = temp_dir / "page1.md"

            original_content = md_file.read_text(encoding="utf-8")
            changes = _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
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
            old_abs = temp_dir / "target.md"
            new_abs = temp_dir / "foo" / "b.md"
            md_file = temp_dir / "page1.md"

            changes = _rewrite_links(
                md_file,
                old_abs,
                new_abs,
                temp_dir,
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
            # Test rewriting links to docs.md
            old_abs = temp_dir / "docs.md"
            new_abs = temp_dir / "reference" / "docs.md"
            mdx_file = temp_dir / "page.mdx"

            changes = _rewrite_links(
                mdx_file,
                old_abs,
                new_abs,
                temp_dir,
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

    def test_rewrite_links_in_jupyter_notebook(self) -> None:
        """Test that links in Jupyter notebook markdown cells are rewritten."""
        # Create a simple notebook with markdown cells containing links
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": [
                        "# Documentation\n",
                        "\n",
                        "See [guide](guide.md) and [API docs](api.md#functions).\n",
                    ],
                },
                {
                    "cell_type": "code",
                    "source": ["# This is a code cell\n", "print('hello')\n"],
                },
                {
                    "cell_type": "markdown",
                    "source": "Also check [guide](guide.md) again.",
                },
            ]
        }

        files: list[File] = [
            {
                "path": "notebook.ipynb",
                "content": json.dumps(notebook_content, indent=1),
            },
            {"path": "guide.md", "content": "# Guide"},
            {"path": "api.md", "content": "# API\n## Functions"},
        ]

        with temp_directory(files) as temp_dir:
            # Test rewriting links to guide.md
            old_abs = temp_dir / "guide.md"
            new_abs = temp_dir / "docs" / "guide.md"
            notebook_file = temp_dir / "notebook.ipynb"

            changes = _rewrite_links_in_notebook(
                notebook_file,
                old_abs,
                new_abs,
                temp_dir,
                dry_run=False,
            )

            # Read the updated notebook
            updated_notebook = json.loads(notebook_file.read_text(encoding="utf-8"))

            # Check that links in markdown cells were updated
            first_cell_source = "".join(updated_notebook["cells"][0]["source"])
            assert "See [guide](docs/guide.md)" in first_cell_source
            assert (
                "[API docs](api.md#functions)" in first_cell_source
            )  # Should remain unchanged

            # Check second markdown cell
            third_cell_source = updated_notebook["cells"][2]["source"]
            assert "Also check [guide](docs/guide.md) again." in third_cell_source

            # Check that code cell was not modified
            code_cell_source = "".join(updated_notebook["cells"][1]["source"])
            assert "print('hello')" in code_cell_source

            # Check that changes were tracked
            assert changes == [
                ("guide.md", "docs/guide.md"),
                ("guide.md", "docs/guide.md"),
            ]


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

    def test_scan_includes_ipynb_files(self) -> None:
        """Test that _scan_and_rewrite processes .ipynb files."""
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": ["Check [target](target.md) in notebook."],
                }
            ]
        }

        files: list[File] = [
            {"path": "page.md", "content": "See [target](target.md)."},
            {
                "path": "notebook.ipynb",
                "content": json.dumps(notebook_content, indent=1),
            },
            {"path": "target.md", "content": "# Target"},
        ]

        with temp_directory(files) as temp_dir:
            old_abs = temp_dir / "target.md"
            new_abs = temp_dir / "reference" / "target.md"

            changes = _scan_and_rewrite(temp_dir, old_abs, new_abs, dry_run=False)

            # Check .md file was updated
            md_content = (temp_dir / "page.md").read_text(encoding="utf-8")
            assert "See [target](reference/target.md)." in md_content

            # Check .ipynb file was updated
            updated_notebook = json.loads(
                (temp_dir / "notebook.ipynb").read_text(encoding="utf-8")
            )
            notebook_source = "".join(updated_notebook["cells"][0]["source"])
            assert "Check [target](reference/target.md) in notebook." in notebook_source

            # Check changes from both file types were tracked
            expected_changes = [
                ("target.md", "reference/target.md"),
                ("target.md", "reference/target.md"),
            ]
            assert changes == expected_changes


class TestUpdateInternalLinksInMovedFile:
    """Tests for _update_internal_links_in_moved_file function."""

    def test_update_relative_links_in_moved_file(self) -> None:
        """Test updating relative links within a file that's been moved."""
        files: list[File] = [
            {
                "path": "docs/guide.md",
                "content": "See [API](../api/reference.md) and "
                "[examples](examples.md).",
            },
            {"path": "api/reference.md", "content": "# API Reference"},
            {"path": "docs/examples.md", "content": "# Examples"},
        ]
        with temp_directory(files) as temp_dir:
            # Move guide.md from docs/ to tutorials/
            moved_file = temp_dir / "tutorials" / "guide.md"
            moved_file.parent.mkdir(exist_ok=True)

            # Copy the original file to the new location
            original_file = temp_dir / "docs" / "guide.md"
            moved_file.write_text(
                original_file.read_text(encoding="utf-8"), encoding="utf-8"
            )

            old_parent = temp_dir / "docs"
            new_parent = temp_dir / "tutorials"

            changes = _update_internal_links_in_moved_file(
                moved_file, old_parent, new_parent, temp_dir, dry_run=False
            )

            # Check that the relative links were updated
            updated_content = moved_file.read_text(encoding="utf-8")
            assert (
                "[API](../api/reference.md)" in updated_content
            )  # ../api should remain unchanged
            assert (
                "[examples](../docs/examples.md)" in updated_content
            )  # examples.md should become ../docs/examples.md

            # Check changes were tracked
            assert ("examples.md", "../docs/examples.md") in changes

    def test_update_internal_links_skip_absolute_paths(self) -> None:
        """Test that absolute paths and external links are not modified."""
        files: list[File] = [
            {
                "path": "docs/page.md",
                "content": (
                    "See [absolute](/api/docs) and "
                    "[external](https://example.com) and "
                    "[relative](other.md)."
                ),
            },
            {"path": "docs/other.md", "content": "# Other"},
        ]
        with temp_directory(files) as temp_dir:
            moved_file = temp_dir / "guides" / "page.md"
            moved_file.parent.mkdir(exist_ok=True)

            original_file = temp_dir / "docs" / "page.md"
            moved_file.write_text(
                original_file.read_text(encoding="utf-8"), encoding="utf-8"
            )

            old_parent = temp_dir / "docs"
            new_parent = temp_dir / "guides"

            changes = _update_internal_links_in_moved_file(
                moved_file, old_parent, new_parent, temp_dir, dry_run=False
            )

            updated_content = moved_file.read_text(encoding="utf-8")
            # Absolute and external links should remain unchanged
            assert "[absolute](/api/docs)" in updated_content
            assert "[external](https://example.com)" in updated_content
            # Only relative link should be updated
            assert "[relative](../docs/other.md)" in updated_content

            # Only the relative link change should be tracked
            assert changes == [("other.md", "../docs/other.md")]

    def test_update_internal_links_dry_run(self) -> None:
        """Test dry run mode for internal link updates."""
        files: list[File] = [
            {
                "path": "src/page.md",
                "content": "See [guide](guide.md) for details.",
            },
            {"path": "src/guide.md", "content": "# Guide"},
        ]
        with temp_directory(files) as temp_dir:
            file_path = temp_dir / "src" / "page.md"
            old_parent = temp_dir / "src"
            new_parent = temp_dir / "docs"

            original_content = file_path.read_text(encoding="utf-8")
            changes = _update_internal_links_in_moved_file(
                file_path, old_parent, new_parent, temp_dir, dry_run=True
            )

            # File should be unchanged in dry run
            updated_content = file_path.read_text(encoding="utf-8")
            assert updated_content == original_content

            # But changes should still be tracked
            assert changes == [("guide.md", "../src/guide.md")]

    def test_update_internal_links_with_anchors(self) -> None:
        """Test updating relative links that include anchors."""
        files: list[File] = [
            {
                "path": "guides/tutorial.md",
                "content": (
                    "See [setup section](setup.md#installation) and "
                    "[config](setup.md#config)."
                ),
            },
            {
                "path": "guides/setup.md",
                "content": "# Setup\n## Installation\n## Config",
            },
        ]
        with temp_directory(files) as temp_dir:
            moved_file = temp_dir / "docs" / "tutorial.md"
            moved_file.parent.mkdir(exist_ok=True)

            original_file = temp_dir / "guides" / "tutorial.md"
            moved_file.write_text(
                original_file.read_text(encoding="utf-8"), encoding="utf-8"
            )

            old_parent = temp_dir / "guides"
            new_parent = temp_dir / "docs"

            changes = _update_internal_links_in_moved_file(
                moved_file, old_parent, new_parent, temp_dir, dry_run=False
            )

            # Check that links with anchors were updated
            updated_content = moved_file.read_text(encoding="utf-8")
            assert (
                "See [setup section](../guides/setup.md#installation)"
                in updated_content
            )
            assert "[config](../guides/setup.md#config)" in updated_content

            # Check that changes tracked the full URLs including anchors
            expected_changes = [
                ("setup.md#installation", "../guides/setup.md#installation"),
                ("setup.md#config", "../guides/setup.md#config"),
            ]
            assert changes == expected_changes

    def test_update_internal_links_in_notebook(self) -> None:
        """Test updating internal links within a moved Jupyter notebook."""
        # Create a notebook with markdown cells containing relative links
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": [
                        "# Tutorial\n",
                        "\n",
                        "See [setup guide](setup.md) and "
                        "[API docs](../api/reference.md).\n",
                    ],
                },
                {
                    "cell_type": "code",
                    "source": ["# Code cell\n", "print('hello')\n"],
                },
            ]
        }

        files: list[File] = [
            {
                "path": "tutorials/notebook.ipynb",
                "content": json.dumps(notebook_content, indent=1),
            },
            {"path": "tutorials/setup.md", "content": "# Setup"},
            {"path": "api/reference.md", "content": "# API Reference"},
        ]

        with temp_directory(files) as temp_dir:
            # Move notebook from tutorials/ to docs/
            moved_notebook = temp_dir / "docs" / "notebook.ipynb"
            moved_notebook.parent.mkdir(exist_ok=True)

            original_notebook = temp_dir / "tutorials" / "notebook.ipynb"
            moved_notebook.write_text(
                original_notebook.read_text(encoding="utf-8"), encoding="utf-8"
            )

            old_parent = temp_dir / "tutorials"
            new_parent = temp_dir / "docs"

            changes = _update_internal_links_in_moved_notebook(
                moved_notebook, old_parent, new_parent, temp_dir, dry_run=False
            )

            # Read the updated notebook
            updated_notebook = json.loads(moved_notebook.read_text(encoding="utf-8"))

            # Check that relative links in markdown cells were updated
            first_cell_source = "".join(updated_notebook["cells"][0]["source"])
            assert "See [setup guide](../tutorials/setup.md)" in first_cell_source
            assert (
                "[API docs](../api/reference.md)" in first_cell_source
            )  # Should remain unchanged

            # Check that code cell was not modified
            code_cell_source = "".join(updated_notebook["cells"][1]["source"])
            assert "print('hello')" in code_cell_source

            # Check that changes were tracked
            assert changes == [("setup.md", "../tutorials/setup.md")]


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

    @pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
    @pytest.mark.parametrize("layout", ["sibling", "nested"])
    def test_move_file_from_git_worktree(
        self, layout: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test auto-detected git root in a real worktree rewrites that worktree."""

        def git(*args: str, cwd: Path) -> None:
            subprocess.run(  # noqa: S603
                ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],  # noqa: S607
                cwd=cwd,
                check=True,
                capture_output=True,
            )

        main = tmp_path / "main"
        (main / "src").mkdir(parents=True)
        (main / "src/page1.md").write_text("See [page 2](page2.md).", encoding="utf-8")
        (main / "src/page2.md").write_text("# Page 2", encoding="utf-8")
        git("init", "-q", cwd=main)
        git("add", ".", cwd=main)
        git("commit", "-q", "-m", "init", cwd=main)

        worktree = (
            tmp_path / "wt" if layout == "sibling" else main / ".worktrees" / "wt"
        )
        git("worktree", "add", "-q", "--detach", str(worktree), cwd=main)
        monkeypatch.chdir(worktree / "src")

        changes = move_file_with_link_updates(Path("page2.md"), Path("moved/page2.md"))

        assert changes == [("page2.md", "moved/page2.md")]
        assert (worktree / "src/moved/page2.md").exists()
        page1 = (worktree / "src/page1.md").read_text(encoding="utf-8")
        assert page1 == "See [page 2](moved/page2.md)."
        assert (worktree / "link_changes.jsonl").exists()
        # The main checkout is untouched.
        assert (main / "src/page2.md").exists()
        assert (main / "src/page1.md").read_text(encoding="utf-8") == (
            "See [page 2](page2.md)."
        )
        assert not (main / "link_changes.jsonl").exists()

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

    def test_move_file_with_internal_link_updates(self) -> None:
        """Test that internal links within the moved file are also updated."""
        files: list[File] = [
            {"path": ".git/config", "content": "[core]\n"},
            {
                "path": "src/guides/tutorial.md",
                "content": (
                    "# Tutorial\n\n"
                    "See [setup guide](setup.md) and "
                    "[API reference](../api/reference.md) for details."
                ),
            },
            {"path": "src/guides/setup.md", "content": "# Setup"},
            {"path": "src/api/reference.md", "content": "# API Reference"},
            {
                "path": "src/index.md",
                "content": "Check out [tutorial](guides/tutorial.md).",
            },
        ]
        with temp_directory(files) as temp_dir:
            src_dir = temp_dir / "src"
            old_path = src_dir / "guides" / "tutorial.md"
            new_path = src_dir / "docs" / "tutorial.md"

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

            # Check that external references TO the moved file were updated
            index_content = (src_dir / "index.md").read_text(encoding="utf-8")
            assert "Check out [tutorial](docs/tutorial.md)." in index_content

            # Check that internal links WITHIN the moved file were updated
            tutorial_content = new_path.read_text(encoding="utf-8")
            assert (
                "[setup guide](../guides/setup.md)" in tutorial_content
            )  # setup.md -> ../guides/setup.md
            assert (
                "[API reference](../api/reference.md)" in tutorial_content
            )  # ../api should remain the same

            # Verify all changes were tracked
            expected_changes = [
                ("guides/tutorial.md", "docs/tutorial.md"),  # External reference update
                ("setup.md", "../guides/setup.md"),  # Internal link update
            ]
            assert all(change in changes for change in expected_changes)

    def test_move_file_with_internal_links_dry_run(self) -> None:
        """Test dry run shows both external and internal link changes."""
        files: list[File] = [
            {"path": ".git/config", "content": "[core]\n"},
            {
                "path": "src/page.md",
                "content": "See [other](other.md) and [guide](../guides/setup.md).",
            },
            {"path": "src/other.md", "content": "# Other"},
            {"path": "guides/setup.md", "content": "# Setup"},
            {"path": "src/index.md", "content": "Check [page](page.md)."},
        ]
        with temp_directory(files) as temp_dir:
            src_dir = temp_dir / "src"
            old_path = src_dir / "page.md"
            new_path = temp_dir / "tutorials" / "page.md"

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

            # Should track both external references to the file AND internal
            # links within it

            # Check that the dry run identified the external reference change
            assert ("page.md", "../tutorials/page.md") in changes
            # Check that the dry run identified the internal link change
            assert ("other.md", "../src/other.md") in changes
