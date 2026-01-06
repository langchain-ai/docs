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
            ".yml",
            ".yaml",
            ".css",
            ".js",
            ".txt",
        }


def test_build_all_empty_directory() -> None:
    """Test building from an empty directory.

    Verifies that the builder handles empty source directories correctly.
    """
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()
        assert not fs.list_build_files()

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
