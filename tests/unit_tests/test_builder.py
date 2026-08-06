"""Tests for the DocumentationBuilder class.

This module contains comprehensive tests for the DocumentationBuilder class,
covering all methods and edge cases including file extension handling,
directory structure preservation, and error conditions.
"""

from pathlib import Path

import pytest

from pipeline.core.builder import DocumentationBuilder
from tests.unit_tests.utils import File, file_system


def test_builder_initialization() -> None:
    """Test DocumentationBuilder initialization.

    Verifies that the builder is correctly initialized with the provided
    source and build directories, and that the copy_extensions set contains
    the expected file extensions.
    """
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        assert builder.src_dir == fs.src_dir
        assert builder.build_dir == fs.build_dir
        assert builder.copy_extensions == {
            ".mdx",
            ".md",
            ".json",
            ".svg",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".mp4",
            ".webm",
            ".yml",
            ".yaml",
            ".css",
            ".js",
            ".jsx",
            ".tsx",
            ".txt",
            ".woff2",
            ".woff",
            ".ttf",
            ".html",
        }


def test_build_all_empty_directory() -> None:
    """Test building from an empty directory.

    Verifies that the builder handles empty source directories correctly.
    """
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()
        assert not fs.list_build_files()


def test_build_all_copies_tsx_snippets() -> None:
    """Test that local TSX snippet components are copied to build/snippets."""
    files = [
        File(
            path="snippets/example-component.tsx",
            content="export default function Example() { return null; }",
        ),
    ]

    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()

        assert fs.build_file_exists("snippets/example-component.tsx")

    def test_build_all_supported_files() -> None:
        """Test building all supported file types.

        Verifies that the builder correctly copies all supported file types
        while maintaining directory structure.
        """
        files = [
            # LangGraph (oss) files - both Python and JavaScript versions
            File(path="oss/index.mdx", content="# Welcome"),
            File(path="oss/config.json", content='{"name": "test"}'),
            File(path="oss/guides/setup.md", content="# Setup Guide"),
            # LangGraph Platform files
            File(path="langgraph-platform/index.mdx", content="# Platform"),
            File(path="langgraph-platform/guide.md", content="# Guide"),
            # LangChain Labs files
            File(path="labs/index.mdx", content="# Labs"),
            # Shared files
            File(path="images/logo.png", bytes=b"PNG_DATA"),
            File(path="docs.json", content='{"name": "test"}'),
        ]

        with file_system(files) as fs:
            builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
            builder.build_all()

            # Verify all files were copied with correct structure
            build_files = {str(p) for p in fs.list_build_files()}

            # Python version of LangGraph files
            assert "oss/python/index.mdx" in build_files
            assert "oss/python/config.json" in build_files
            assert "oss/python/guides/setup.md" in build_files

            # JavaScript version of LangGraph files
            assert "oss/javascript/index.mdx" in build_files
            assert "oss/javascript/config.json" in build_files
            assert "oss/javascript/guides/setup.md" in build_files

            # LangGraph Platform files
            assert "langgraph-platform/index.mdx" in build_files
            assert "langgraph-platform/guide.md" in build_files

            # LangChain Labs files
            assert "labs/index.mdx" in build_files

            # Shared files
            assert "images/logo.png" in build_files
            assert "docs.json" in build_files

            # Total number of files should be:
            # - 3 files * 2 versions (Python/JavaScript) for LangGraph
            # - 2 files for Platform
            # - 1 file for Labs
            # - 2 shared files
            assert len(build_files) == 11

    def test_build_all_unsupported_files() -> None:
        """Test building with unsupported file types.

        Verifies that the builder skips unsupported file types.
        """
        files = [
            # LangGraph files with supported and unsupported types
            File(
                path="oss/index.mdx",
                content="# Welcome",
            ),
            File(
                path="oss/ignored.txt",
                content="This should be ignored",
            ),
            File(
                path="oss/data.csv",
                content="col1,col2\n1,2",
            ),
            # Platform files with supported and unsupported types
            File(
                path="langgraph-platform/guide.md",
                content="# Guide",
            ),
            File(
                path="langgraph-platform/ignored.txt",
                content="This should be ignored",
            ),
            # Labs files with supported and unsupported types
            File(
                path="labs/index.mdx",
                content="# Labs",
            ),
            File(
                path="labs/data.csv",
                content="col1,col2\n1,2",
            ),
            # Shared files with supported and unsupported types
            File(
                path="images/logo.png",
                bytes=b"PNG_DATA",
            ),
            File(
                path="ignored.txt",
                content="This should be ignored",
            ),
        ]

        with file_system(files) as fs:
            builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
            builder.build_all()

            # Verify only supported files were copied
            build_files = {str(p) for p in fs.list_build_files()}

            # Python version of LangGraph files (only .mdx)
            assert "oss/python/index.mdx" in build_files
            assert "oss/python/ignored.txt" not in build_files
            assert "oss/python/data.csv" not in build_files

            # JavaScript version of LangGraph files (only .mdx)
            assert "oss/javascript/index.mdx" in build_files
            assert "oss/javascript/ignored.txt" not in build_files
            assert "oss/javascript/data.csv" not in build_files

            # Platform files (only .md)
            assert "langgraph-platform/guide.md" in build_files
            assert "langgraph-platform/ignored.txt" not in build_files

            # Labs files (only .mdx)
            assert "labs/index.mdx" in build_files
            assert "labs/data.csv" not in build_files

            # Shared files (only .png)
            assert "images/logo.png" in build_files
            assert "ignored.txt" not in build_files

            # Total number of files should be:
            # - 1 file * 2 versions (Python/JavaScript) for LangGraph
            # - 1 file for Platform
            # - 1 file for Labs
            # - 1 shared file
            assert len(build_files) == 4


def test_build_single_file() -> None:
    """Test building a single file.

    Verifies that the builder correctly copies a single file
    when requested.
    """
    files = [
        File(
            path="index.mdx",
            content="# Welcome",
        ),
        File(
            path="config.json",
            content='{"name": "test"}',
        ),
    ]

    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_file(fs.src_dir / "index.mdx")

        # Verify only the requested file was copied
        build_files = fs.list_build_files()
        assert len(build_files) == 1
        assert Path("index.mdx") in build_files
        assert not fs.build_file_exists("config.json")


def test_build_multiple_files() -> None:
    """Test building multiple specific files.

    Verifies that the builder correctly copies multiple specified files
    while maintaining directory structure.
    """
    files = [
        File(
            path="index.mdx",
            content="# Welcome",
        ),
        File(
            path="config.json",
            content='{"name": "test"}',
        ),
        File(
            path="guides/setup.md",
            content="# Setup Guide",
        ),
    ]

    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_files(
            [
                fs.src_dir / "index.mdx",
                fs.src_dir / "guides/setup.md",
            ],
        )

        # Verify only specified files were copied
        build_files = fs.list_build_files()
        assert len(build_files) == 2
        assert Path("index.mdx") in build_files
        assert Path("guides/setup.mdx") in build_files
        assert not fs.build_file_exists("config.json")


def test_build_nonexistent_file() -> None:
    """Test building a nonexistent file.

    Verifies that the builder handles attempts to build
    nonexistent files gracefully.
    """
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        with pytest.raises(AssertionError):
            builder.build_file(fs.src_dir / "nonexistent.md")


def test_rewrite_oss_links_inserts_language() -> None:
    """Bare /oss/ links get the target language inserted after 'oss'."""
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        content = "[Deep Agents](/oss/deepagents/overview)"
        assert (
            builder._rewrite_oss_links(content, "python")
            == "[Deep Agents](/oss/python/deepagents/overview)"
        )
        assert (
            builder._rewrite_oss_links(content, "js")
            == "[Deep Agents](/oss/javascript/deepagents/overview)"
        )


def test_rewrite_oss_links_preserves_existing_language() -> None:
    """Links that already specify a language are left untouched.

    Regression test: unversioned langsmith pages are built with
    target_language="python", so a link that already points at
    /oss/python/... or /oss/javascript/... must not have a second
    language segment inserted (which produced /oss/python/python/...).
    """
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        py = "[LangChain](/oss/python/langchain/overview)"
        js = "[LangChain](/oss/javascript/langchain/overview)"
        # Building langsmith uses target_language="python"; both must survive.
        assert builder._rewrite_oss_links(py, "python") == py
        assert builder._rewrite_oss_links(js, "python") == js


def test_rewrite_oss_links_preserves_deepagents_code() -> None:
    """Deep Agents Code URLs stay language-agnostic (no python/javascript insert)."""
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        link = "[Overview](/oss/deepagents/code/overview)"
        assert builder._rewrite_oss_links(link, "python") == link
        assert builder._rewrite_oss_links(link, "js") == link
        # Sibling OSS paths still get the language prefix.
        other = "[SDK](/oss/deepagents/quickstart)"
        assert (
            builder._rewrite_oss_links(other, "python")
            == "[SDK](/oss/python/deepagents/quickstart)"
        )


def test_unversioned_oss_code_builds_once() -> None:
    """Deep Agents Code pages build to oss/deepagents/code/, not per-language copies."""
    files = [
        File(
            path="oss/deepagents/code/overview.mdx",
            content=(
                "---\ntitle: Code\n---\n\n"
                "See [SDK](/oss/deepagents/quickstart) and "
                "[Config](/oss/deepagents/code/configuration).\n"
            ),
        ),
        File(
            path="oss/deepagents/quickstart.mdx",
            content="---\ntitle: Quickstart\n---\n\nSDK docs.\n",
        ),
    ]
    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        code_src = fs.src_dir / "oss" / "deepagents" / "code" / "overview.mdx"
        assert builder.is_unversioned_oss_file(code_src)
        assert not builder.is_unversioned_oss_file(
            fs.src_dir / "oss" / "deepagents" / "quickstart.mdx"
        )

        builder.build_file(code_src)
        unversioned = fs.build_dir / "oss" / "deepagents" / "code" / "overview.mdx"
        assert unversioned.exists()
        assert not (
            fs.build_dir / "oss" / "python" / "deepagents" / "code" / "overview.mdx"
        ).exists()
        assert not (
            fs.build_dir / "oss" / "javascript" / "deepagents" / "code" / "overview.mdx"
        ).exists()

        content = unversioned.read_text()
        assert "/oss/python/deepagents/quickstart" in content
        assert "/oss/deepagents/code/configuration" in content
        assert "/oss/python/deepagents/code/" not in content


def test_rewrite_oss_links_skips_images_and_none() -> None:
    """Image paths and a None target language are passed through unchanged."""
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        img = '<img src="/oss/images/diagram.png" />'
        assert builder._rewrite_oss_links(img, "python") == img
        link = "[x](/oss/deepagents/overview)"
        assert builder._rewrite_oss_links(link, None) == link


def test_rewrite_snippet_imports_for_language() -> None:
    """MDX snippet imports are scoped under /snippets/{python|javascript}/."""
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        content = (
            "import RequiresLanggraphServer from "
            "'/snippets/oss/requires-langgraph-server.mdx';\n"
            'import { PatternEmbed } from "/snippets/pattern-embed.jsx"\n'
        )
        assert builder._rewrite_snippet_imports_for_language(content, "python") == (
            "import RequiresLanggraphServer from "
            "'/snippets/python/oss/requires-langgraph-server.mdx';\n"
            'import { PatternEmbed } from "/snippets/pattern-embed.jsx"\n'
        )
        assert builder._rewrite_snippet_imports_for_language(content, "js") == (
            "import RequiresLanggraphServer from "
            "'/snippets/javascript/oss/requires-langgraph-server.mdx';\n"
            'import { PatternEmbed } from "/snippets/pattern-embed.jsx"\n'
        )
        already = (
            "import X from '/snippets/python/oss/requires-langgraph-server.mdx';\n"
        )
        assert builder._rewrite_snippet_imports_for_language(already, "js") == already


def test_snippet_oss_links_are_language_prefixed_not_relative() -> None:
    """Shared snippets with /oss/ links get absolute language-prefixed copies.

    Regression for nested consumers such as langchain/frontend/branching-chat:
    a fixed ``../langgraph/local-server`` relative link resolved incorrectly to
    ``/oss/{lang}/langchain/langgraph/local-server``.
    """
    files = [
        File(
            path="snippets/oss/requires-langgraph-server.mdx",
            content=(
                "<Note>\n"
                "This feature requires the "
                "[LangGraph Agent Server](/oss/langgraph/local-server).\n"
                "</Note>\n"
            ),
        ),
        File(
            path="oss/langchain/frontend/branching-chat.mdx",
            content=(
                "---\ntitle: Branching chat\n---\n\n"
                "import RequiresLanggraphServer from "
                "'/snippets/oss/requires-langgraph-server.mdx';\n\n"
                "<RequiresLanggraphServer />\n"
            ),
        ),
    ]
    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()

        default = (
            fs.build_dir / "snippets" / "oss" / "requires-langgraph-server.mdx"
        ).read_text()
        py_snippet = (
            fs.build_dir
            / "snippets"
            / "python"
            / "oss"
            / "requires-langgraph-server.mdx"
        ).read_text()
        js_snippet = (
            fs.build_dir
            / "snippets"
            / "javascript"
            / "oss"
            / "requires-langgraph-server.mdx"
        ).read_text()

        assert "/oss/python/langgraph/local-server" in default
        assert "/oss/python/langgraph/local-server" in py_snippet
        assert "/oss/javascript/langgraph/local-server" in js_snippet
        assert "../langgraph/local-server" not in default
        assert "../langgraph/local-server" not in py_snippet
        assert "../langgraph/local-server" not in js_snippet

        py_page = (
            fs.build_dir
            / "oss"
            / "python"
            / "langchain"
            / "frontend"
            / "branching-chat.mdx"
        ).read_text()
        js_page = (
            fs.build_dir
            / "oss"
            / "javascript"
            / "langchain"
            / "frontend"
            / "branching-chat.mdx"
        ).read_text()
        assert "from '/snippets/python/oss/requires-langgraph-server.mdx'" in py_page
        assert (
            "from '/snippets/javascript/oss/requires-langgraph-server.mdx'" in js_page
        )
