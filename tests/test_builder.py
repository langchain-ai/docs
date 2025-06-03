"""Tests for the DocumentationBuilder class.

This module contains comprehensive tests for the DocumentationBuilder class,
covering all methods and edge cases including file extension handling,
directory structure preservation, and error conditions.
"""

from pathlib import Path

import pytest

from pipeline.core.builder import DocumentationBuilder
from tests.test_utils import TestFileSystem


class TestDocumentationBuilder:
    """Test suite for DocumentationBuilder class.

    This test class verifies the functionality of the DocumentationBuilder,
    including initialization, file building operations, and file extension
    filtering capabilities.
    """

    def test_init(self) -> None:
        """Test DocumentationBuilder initialization.

        Verifies that the builder is correctly initialized with the provided
        source and build directories, and that the copy_extensions set contains
        the expected file extensions.
        """
        with TestFileSystem([]) as fs:
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
            }

    def test_build_all_creates_build_directory(self) -> None:
        """Test that build_all creates the build directory.

        Verifies that the build_all method creates the build directory
        if it doesn't exist.
        """
        files = [
            test_file("index.mdx", "# Home"),
        ]

        with TestFileSystem(files) as fs:
            builder = DocumentationBuilder(fs.src_dir, fs.build_dir)

            # Remove build dir to test creation
            if fs.build_dir.exists():
                fs.build_dir.rmdir()

            builder.build_all()
            assert fs.build_dir.exists()

    def test_build_all_copies_supported_files(self) -> None:
        """Test that build_all copies all supported files.

        Verifies that all files with supported extensions are copied
        while unsupported files are skipped.
        """
        files = [
            test_file("index.mdx", "# Home\nWelcome to the docs"),
            test_file("guide.md", "# Guide\nThis is a guide"),
            test_file("config.json", '{"title": "Test Docs"}'),
            test_file("logo.svg", "<svg>test</svg>"),
            test_binary_file("image.png", b"fake png data"),
            test_file("unsupported.txt", "unsupported file"),
            test_file("guides/advanced.mdx", "# Advanced Guide"),
        ]

        with TestFileSystem(files) as fs:
            builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
            builder.build_all()

            # Check that supported files were copied
            assert fs.build_file_exists("index.mdx")
            assert fs.build_file_exists("guide.md")
            assert fs.build_file_exists("config.json")
            assert fs.build_file_exists("logo.svg")
            assert fs.build_file_exists("image.png")
            assert fs.build_file_exists("guides/advanced.mdx")

            # Check that unsupported files were not copied
            assert not fs.build_file_exists("unsupported.txt")

    def test_build_all_preserves_content(self) -> None:
        """Test that build_all preserves file content.

        Verifies that file contents are preserved exactly during the
        copy operation.
        """
        files = [
            test_file("index.mdx", "# Home\nWelcome to the docs"),
            test_file("config.json", '{"title": "Test Docs"}'),
            test_binary_file("image.png", b"fake png data"),
        ]

        with TestFileSystem(files) as fs:
            builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
            builder.build_all()

            # Check content is preserved
            assert fs.get_build_file("index.mdx") == "# Home\nWelcome to the docs"
            assert fs.get_build_file("config.json") == '{"title": "Test Docs"}'
            assert fs.get_build_file("image.png") == b"fake png data"

    def test_build_comprehensive_file_structure(self) -> None:
        """Test building a comprehensive file structure.

        Tests a realistic documentation structure with multiple directories,
        file types, and content preservation.
        """
        files = [
            # Root level files
            test_file("index.mdx", "# Documentation\nWelcome to our docs"),
            test_file("README.md", "# Project README"),
            test_file("docs.json", '{"version": "1.0", "title": "Docs"}'),
            # Images and assets
            test_binary_file("assets/logo.png", b"PNG_IMAGE_DATA"),
            test_file("assets/icon.svg", '<svg><circle r="10"/></svg>'),
            # Nested documentation
            test_file("guides/getting-started.mdx", "# Getting Started\nFirst steps"),
            test_file("guides/advanced/concepts.md", "# Advanced Concepts"),
            test_file("api/reference.json", '{"endpoints": ["/api/v1"]}'),
            # Unsupported files (should be skipped)
            test_file("temp.txt", "temporary file"),
            test_file("scripts/build.py", "#!/usr/bin/env python3"),
        ]

        with TestFileSystem(files) as fs:
            builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
            builder.build_all()

            # Verify correct files were copied
            built_files = fs.list_build_files()
            expected_files = {
                Path("index.mdx"),
                Path("README.md"),
                Path("docs.json"),
                Path("assets/logo.png"),
                Path("assets/icon.svg"),
                Path("guides/getting-started.mdx"),
                Path("guides/advanced/concepts.md"),
                Path("api/reference.json"),
            }

            assert set(built_files) == expected_files
            assert fs.get_build_file_count() == 8

            # Verify content preservation
            assert "Welcome to our docs" in fs.get_build_file("index.mdx")
            assert fs.get_build_file("assets/logo.png") == b"PNG_IMAGE_DATA"
            assert "Advanced Concepts" in fs.get_build_file(
                "guides/advanced/concepts.md",
            )

            # Verify unsupported files were not copied
            assert not fs.build_file_exists("temp.txt")
            assert not fs.build_file_exists("scripts/build.py")

    def test_build_all_preserves_directory_structure(
        self,
        temp_src_dir,
        temp_build_dir,
    ):
        """Test that build_all preserves directory structure."""
        builder = DocumentationBuilder(temp_src_dir, temp_build_dir)
        builder.build_all()

        # Check directory structure is preserved
        assert (temp_build_dir / "guides").is_dir()
        assert (temp_build_dir / "guides" / "advanced.mdx").exists()

    def test_build_all_clears_existing_build(self, temp_src_dir, temp_build_dir):
        """Test that build_all clears existing build directory."""
        # Create some existing files in build dir
        temp_build_dir.mkdir(exist_ok=True)
        (temp_build_dir / "old_file.txt").write_text("old content")

        builder = DocumentationBuilder(temp_src_dir, temp_build_dir)
        builder.build_all()

        # Old file should be gone
        assert not (temp_build_dir / "old_file.txt").exists()
        # New files should exist
        assert (temp_build_dir / "index.mdx").exists()

    def test_build_file_single_file(self, temp_src_dir, temp_build_dir):
        """Test building a single file."""
        builder = DocumentationBuilder(temp_src_dir, temp_build_dir)
        temp_build_dir.mkdir(exist_ok=True)

        file_path = temp_src_dir / "index.mdx"
        builder.build_file(file_path)

        assert (temp_build_dir / "index.mdx").exists()
        assert (
            temp_build_dir / "index.mdx"
        ).read_text() == "# Home\nWelcome to the docs"

    def test_build_files_multiple_files(self, temp_src_dir, temp_build_dir):
        """Test building multiple specific files."""
        builder = DocumentationBuilder(temp_src_dir, temp_build_dir)
        temp_build_dir.mkdir(exist_ok=True)

        files = [temp_src_dir / "index.mdx", temp_src_dir / "guide.md"]
        builder.build_files(files)

        assert (temp_build_dir / "index.mdx").exists()
        assert (temp_build_dir / "guide.md").exists()
        assert not (temp_build_dir / "config.json").exists()  # Not in the list

    @pytest.mark.parametrize(
        "extension,should_copy",
        [
            (".mdx", True),
            (".md", True),
            (".json", True),
            (".svg", True),
            (".png", True),
            (".jpg", True),
            (".jpeg", True),
            (".gif", True),
            (".txt", False),
            (".py", False),
            (".js", False),
            ("", False),
        ],
    )
    def test_file_extension_handling(
        self,
        temp_src_dir,
        temp_build_dir,
        extension,
        should_copy,
    ):
        """Test that only supported file extensions are copied."""
        builder = DocumentationBuilder(temp_src_dir, temp_build_dir)
        temp_build_dir.mkdir(exist_ok=True)

        # Create test file with specific extension
        test_file = temp_src_dir / f"test{extension}"
        test_file.write_text("test content")

        builder.build_file(test_file)

        output_file = temp_build_dir / f"test{extension}"
        if should_copy:
            assert output_file.exists()
            assert output_file.read_text() == "test content"
        else:
            assert not output_file.exists()
