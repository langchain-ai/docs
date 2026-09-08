"""Tests for the DocumentationBuilder class.

This module contains comprehensive tests for the DocumentationBuilder class,
covering all methods and edge cases including file extension handling,
directory structure preservation, and error conditions.
"""

import json
import re
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


def test_unversioned_oss_openwiki_builds_once() -> None:
    """OpenWiki pages build to oss/openwiki/, not per-language copies."""
    files = [
        File(
            path="oss/openwiki/overview.mdx",
            content=(
                "---\ntitle: OpenWiki\n---\n\n"
                "See [SDK](/oss/deepagents/quickstart) and "
                "[Quickstart](/oss/openwiki/quickstart).\n"
            ),
        ),
        File(
            path="oss/deepagents/quickstart.mdx",
            content="---\ntitle: Quickstart\n---\n\nSDK docs.\n",
        ),
    ]
    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        openwiki_src = fs.src_dir / "oss" / "openwiki" / "overview.mdx"
        assert builder.is_unversioned_oss_file(openwiki_src)

        link = "[Overview](/oss/openwiki/overview)"
        assert builder._rewrite_oss_links(link, "python") == link
        assert builder._rewrite_oss_links(link, "js") == link

        builder.build_file(openwiki_src)
        unversioned = fs.build_dir / "oss" / "openwiki" / "overview.mdx"
        assert unversioned.exists()
        assert not (
            fs.build_dir / "oss" / "python" / "openwiki" / "overview.mdx"
        ).exists()
        assert not (
            fs.build_dir / "oss" / "javascript" / "openwiki" / "overview.mdx"
        ).exists()

        content = unversioned.read_text()
        assert "/oss/python/deepagents/quickstart" in content
        assert "/oss/openwiki/quickstart" in content
        assert "/oss/python/openwiki/" not in content


def test_safe_source_files_skips_symlinks() -> None:
    """Source collection rejects symlinks so host files cannot be exfiltrated."""
    files = [
        File(
            path="oss/openwiki/overview.mdx",
            content="---\ntitle: OpenWiki\n---\n\nOverview.\n",
        ),
    ]
    with file_system(files) as fs:
        openwiki_dir = fs.src_dir / "oss" / "openwiki"
        secret_target = fs.temp_dir / "outside-secret.txt"
        secret_target.write_text("secret-value\n", encoding="utf-8")
        symlink_path = openwiki_dir / "leaked.env"
        symlink_path.symlink_to(secret_target)

        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        collected = builder._safe_source_files(openwiki_dir)

        assert openwiki_dir / "overview.mdx" in collected
        assert symlink_path not in collected
        assert all(not path.is_symlink() for path in collected)

        builder._build_unversioned_oss_openwiki()
        assert not (fs.build_dir / "oss" / "openwiki" / "leaked.env").exists()
        overview = fs.build_dir / "oss" / "openwiki" / "overview.mdx"
        assert overview.exists()
        assert "secret-value" not in overview.read_text()


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


def test_rewrite_managed_deep_agents_links_inserts_language() -> None:
    """Managed Deep Agents links get the target language route."""
    with file_system([]) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        content = (
            "[Quickstart](/langsmith/managed-deep-agents-quickstart)\n"
            '<Card href="/langsmith/managed-deep-agents-tools#example" />\n'
            "[Python](/langsmith/python/managed-deep-agents-overview)"
        )

        python_content = builder._rewrite_managed_deep_agents_links(content, "python")
        assert "/langsmith/python/managed-deep-agents-quickstart" in python_content
        assert "/langsmith/python/managed-deep-agents-tools#example" in python_content
        assert python_content.count("/langsmith/python/") == 3

        js_content = builder._rewrite_managed_deep_agents_links(content, "js")
        assert "/langsmith/javascript/managed-deep-agents-quickstart" in js_content
        assert "/langsmith/javascript/managed-deep-agents-tools#example" in js_content
        assert "/langsmith/python/managed-deep-agents-overview" in js_content


def test_build_all_creates_managed_deep_agents_language_routes() -> None:
    """Managed Deep Agents pages and snippets build for both languages."""
    files = [
        File(
            path="langsmith/managed-deep-agents-overview.mdx",
            content=(
                "---\ntitle: Managed Deep Agents\n---\n\n"
                "import NextSteps from "
                "'/snippets/langsmith/managed-deep-agents-next-steps.mdx';\n\n"
                "[Quickstart](/langsmith/managed-deep-agents-quickstart)\n\n"
                "[Deep Agents](/oss/deepagents/overview)\n"
            ),
        ),
        File(
            path="langsmith/managed-deep-agents-quickstart.mdx",
            content="---\ntitle: Quickstart\n---\n",
        ),
        File(
            path="snippets/langsmith/managed-deep-agents-next-steps.mdx",
            content=(
                "[Tools](/langsmith/managed-deep-agents-tools)\n"
                "[Deep Agents](/oss/deepagents/overview)\n"
                ":::python\nPython only.\n:::\n"
                ":::js\nTypeScript only.\n:::\n"
            ),
        ),
    ]

    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()

        # Unversioned routes are redirects only; do not emit orphaned pages.
        assert not (
            fs.build_dir / "langsmith" / "managed-deep-agents-overview.mdx"
        ).exists()
        assert not (
            fs.build_dir / "langsmith" / "managed-deep-agents-quickstart.mdx"
        ).exists()

        python_page = (
            fs.build_dir / "langsmith" / "python" / "managed-deep-agents-overview.mdx"
        ).read_text()
        js_page = (
            fs.build_dir
            / "langsmith"
            / "javascript"
            / "managed-deep-agents-overview.mdx"
        ).read_text()

        assert "/langsmith/python/managed-deep-agents-quickstart" in python_page
        assert "/langsmith/javascript/managed-deep-agents-quickstart" in js_page
        assert "/oss/python/deepagents/overview" in python_page
        assert "/oss/javascript/deepagents/overview" in js_page
        assert (
            "from '/snippets/python/langsmith/managed-deep-agents-next-steps.mdx'"
            in python_page
        )
        assert (
            "from '/snippets/javascript/langsmith/managed-deep-agents-next-steps.mdx'"
            in js_page
        )

        python_snippet = (
            fs.build_dir
            / "snippets"
            / "python"
            / "langsmith"
            / "managed-deep-agents-next-steps.mdx"
        ).read_text()
        js_snippet = (
            fs.build_dir
            / "snippets"
            / "javascript"
            / "langsmith"
            / "managed-deep-agents-next-steps.mdx"
        ).read_text()
        assert "/langsmith/python/managed-deep-agents-tools" in python_snippet
        assert "Python only." in python_snippet
        assert "TypeScript only." not in python_snippet
        assert "/langsmith/javascript/managed-deep-agents-tools" in js_snippet
        assert "TypeScript only." in js_snippet
        assert "Python only." not in js_snippet


def test_build_all_writes_llms_txt() -> None:
    """Test that build_all emits a custom llms.txt indexing every page.

    Mintlify truncates its auto-generated llms.txt at 100,000 characters, so
    the pipeline writes its own uncapped file at the build root.
    """
    files: list[File] = [
        {
            "path": "langsmith/tracing.mdx",
            "content": "---\ntitle: Tracing\ndescription: Trace runs.\n---\n\nBody.\n",
        },
        {
            "path": "langsmith/hidden.mdx",
            "content": "---\ntitle: Hidden\nnoindex: true\n---\n\nBody.\n",
        },
        {
            "path": "snippets/shared.mdx",
            "content": "---\ntitle: Shared\n---\n\nSnippet body.\n",
        },
    ]
    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()

        llms_txt = (fs.build_dir / "llms.txt").read_text(encoding="utf-8")

        assert llms_txt.startswith("# ")
        assert (
            "- [Tracing](https://docs.langchain.com/langsmith/tracing.md): Trace runs."
            in llms_txt
        )
        # noindex pages and snippets are not real pages, so they stay out.
        assert "hidden.md" not in llms_txt
        assert "snippets/shared.md" not in llms_txt


def test_tag_slug_preserves_underscores() -> None:
    """Test that OpenAPI tag slugs keep underscores but normalize case and spaces.

    The LangSmith spec carries both `annotation-queues` and `annotation_queues`
    as distinct tags that Mintlify renders to different directories, so
    collapsing them together would generate URLs for pages that do not exist.
    """
    slug = DocumentationBuilder._tag_slug
    assert slug("annotation_queues") == "annotation_queues"
    assert slug("annotation-queues") == "annotation-queues"
    assert slug("SCIM Tokens") == "scim-tokens"
    assert slug("A2A") == "a2a"


def test_slugify_drops_apostrophes() -> None:
    """Test that apostrophes are removed rather than turned into separators."""
    slug = DocumentationBuilder._slugify
    assert slug("Get the authenticated user's provider user ID") == (
        "get-the-authenticated-users-provider-user-id"
    )
    assert slug("Get company info") == "get-company-info"


def test_openapi_entries_skip_hidden_and_number_duplicates() -> None:
    """Test that hidden operations are omitted and duplicate slugs get suffixes.

    Mintlify renders no page for `x-hidden` operations, and disambiguates two
    operations sharing a summary with a numeric suffix instead of dropping one.
    """
    spec = {
        "paths": {
            "/a": {"get": {"tags": ["orgs"], "summary": "Get info", "responses": {}}},
            "/b": {"get": {"tags": ["orgs"], "summary": "Get info", "responses": {}}},
            "/c": {
                "get": {
                    "tags": ["fleet orgs"],
                    "summary": "Hidden op",
                    "responses": {},
                    "x-hidden": True,
                }
            },
        }
    }
    docs_json = {
        "navigation": {
            "pages": [
                {
                    "group": "REST API",
                    "openapi": {
                        "source": "langsmith/spec.json",
                        "directory": "langsmith/api",
                    },
                }
            ]
        }
    }
    files: list[File] = [
        {"path": "docs.json", "content": json.dumps(docs_json)},
        {"path": "langsmith/spec.json", "content": json.dumps(spec)},
        {"path": "langsmith/page.mdx", "content": "---\ntitle: Page\n---\n\nBody.\n"},
    ]
    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()
        slugs = [slug for _, slug, _ in builder._openapi_entries()]

    assert slugs == ["langsmith/api/orgs/get-info", "langsmith/api/orgs/get-info-1"]


def test_llms_txt_splits_large_sections_into_section_indexes() -> None:
    """Test that a large section becomes linked section files, not root bulk.

    AFDocs passes `llms-txt-size` only under 50,000 characters, and its
    coverage walker descends exactly one level into linked .txt files, so
    section indexes must sit one hop from the root and must not nest further.
    """
    files: list[File] = [
        {
            "path": f"langsmith/page-{i:03d}.mdx",
            "content": (
                f"---\ntitle: Page {i}\ndescription: {'x' * 250}\n---\n\nBody.\n"
            ),
        }
        for i in range(400)
    ]
    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()

        root = (fs.build_dir / "llms.txt").read_text(encoding="utf-8")
        sections = sorted(
            p.name for p in (fs.build_dir / "langsmith").glob("llms*.txt")
        )

        # Root stays under the pass threshold and delegates to section files.
        assert len(root) < 50_000
        assert sections, "expected at least one section index"
        for name in sections:
            section = (fs.build_dir / "langsmith" / name).read_text(encoding="utf-8")
            assert len(section) < 50_000
            assert "llms.txt" not in section.replace("# ", ""), "must not nest deeper"
            assert f"({builder._SITE_URL}/langsmith/{name})" in root

        # Every page is listed exactly once across root plus sections.
        listed = re.findall(r"\((https://\S+?\.md)\)", root)
        for name in sections:
            body = (fs.build_dir / "langsmith" / name).read_text(encoding="utf-8")
            listed += re.findall(r"\((https://\S+?\.md)\)", body)
        assert len(listed) == len(set(listed)) == 400


def test_llms_full_txt_splits_languages_and_inlines_snippets() -> None:
    """Test that llms-full.txt splits language corpora and expands snippets.

    Mintlify expands snippet imports when it renders, so a corpus built from
    the raw build tree would silently drop content from every page that
    imports one. The root file must also open with the site title as an H1.
    """
    files: list[File] = [
        {"path": "docs.json", "content": json.dumps({"name": "Test Docs"})},
        {
            "path": "snippets/shared-block.mdx",
            "content": "UNIQUE_SNIPPET_CONTENT\n",
        },
        {
            "path": "oss/guide.mdx",
            "content": (
                "---\ntitle: Guide\n---\n\n"
                "import SharedBlock from '/snippets/shared-block.mdx';\n\n"
                "Intro.\n\n<SharedBlock />\n"
            ),
        },
        {"path": "langsmith/core.mdx", "content": "---\ntitle: Core\n---\n\nCore.\n"},
    ]
    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()

        root = (fs.build_dir / "llms-full.txt").read_text(encoding="utf-8")
        py = (fs.build_dir / "oss/python/llms-full.txt").read_text(encoding="utf-8")
        js = (fs.build_dir / "oss/javascript/llms-full.txt").read_text(encoding="utf-8")

    # Root opens with the site title and points at the language corpora.
    assert root.startswith("# Test Docs")
    assert "oss/python/llms-full.txt" in root
    assert "oss/javascript/llms-full.txt" in root

    # Language pages live in their own corpus, not the root.
    assert "Source: https://docs.langchain.com/oss/python/guide" in py
    assert "Source: https://docs.langchain.com/oss/python/guide" not in root
    assert "Source: https://docs.langchain.com/langsmith/core" in root

    # Snippets are inlined, and the import line itself is gone.
    assert "UNIQUE_SNIPPET_CONTENT" in py
    assert "UNIQUE_SNIPPET_CONTENT" in js
    assert "import SharedBlock" not in py


def _write_index(build_dir: Path, name: str, body: str) -> None:
    """Write an llms index file into a build directory for validator tests."""
    path = build_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_validate_llms_indexes_accepts_a_well_formed_index() -> None:
    """Test that the validator passes a root plus section index that is correct."""
    with file_system([]) as fs:
        fs.build_dir.mkdir(parents=True, exist_ok=True)
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        site = builder._SITE_URL
        _write_index(
            fs.build_dir,
            "llms.txt",
            f"# Site\n\n- [A]({site}/a.md)\n- [Section]({site}/oss/llms.txt)\n",
        )
        _write_index(fs.build_dir, "oss/llms.txt", f"# Site\n\n- [B]({site}/b.md)\n")

        builder._validate_llms_indexes(2)  # does not raise


def test_validate_llms_indexes_rejects_oversized_root() -> None:
    """Test that a root over the truncation threshold fails the build."""
    with file_system([]) as fs:
        fs.build_dir.mkdir(parents=True, exist_ok=True)
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        padding = "x" * builder._LLMS_MAX
        _write_index(
            fs.build_dir,
            "llms.txt",
            f"# Site\n\n{padding}\n- [A]({builder._SITE_URL}/a.md)\n",
        )

        with pytest.raises(ValueError, match="over the 50,000 threshold"):
            builder._validate_llms_indexes(1)


def test_validate_llms_indexes_rejects_second_level_nesting() -> None:
    """Test that a section index linking to further .txt files fails.

    Coverage walkers descend one level, so pages behind a second hop drop out
    of the index entirely.
    """
    with file_system([]) as fs:
        fs.build_dir.mkdir(parents=True, exist_ok=True)
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        site = builder._SITE_URL
        _write_index(
            fs.build_dir, "llms.txt", f"# Site\n\n- [S]({site}/oss/llms.txt)\n"
        )
        _write_index(
            fs.build_dir,
            "oss/llms.txt",
            f"# Site\n\n- [A]({site}/a.md)\n- [Deeper]({site}/oss/py/llms.txt)\n",
        )

        with pytest.raises(ValueError, match="descend only one level"):
            builder._validate_llms_indexes(1)


def test_validate_llms_indexes_rejects_duplicate_and_missing_pages() -> None:
    """Test that a page listed twice, or a page count mismatch, fails."""
    with file_system([]) as fs:
        fs.build_dir.mkdir(parents=True, exist_ok=True)
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        site = builder._SITE_URL
        _write_index(
            fs.build_dir, "llms.txt", f"# Site\n\n- [S]({site}/oss/llms.txt)\n"
        )
        _write_index(
            fs.build_dir,
            "oss/llms.txt",
            f"# Site\n\n- [A]({site}/a.md)\n- [A again]({site}/a.md)\n",
        )

        with pytest.raises(ValueError, match="listed more than once"):
            builder._validate_llms_indexes(1)

        _write_index(fs.build_dir, "oss/llms.txt", f"# Site\n\n- [A]({site}/a.md)\n")
        with pytest.raises(ValueError, match="but 5 were built"):
            builder._validate_llms_indexes(5)


def test_page_body_rejects_snippet_imports_outside_the_build_tree() -> None:
    """Test that a traversing snippet import cannot read files outside build/.

    Snippet import paths come from MDX text, which is editable in a pull
    request, and CI commits build/ to a pushed preview branch. Path joins do
    not collapse "..", so an unvalidated import would publish any readable
    file on the build host.
    """
    files: list[File] = [
        # A real snippet, so build/snippets/ exists and ".." can actually
        # traverse out of it. Without this the read fails for the wrong reason
        # and the test passes even when the containment check is removed.
        {"path": "snippets/real.mdx", "content": "Legitimate snippet.\n"},
        {
            "path": "langsmith/evil.mdx",
            "content": (
                "---\ntitle: Evil\n---\n\n"
                "import Leak from '/snippets/../../secret.txt';\n\n"
                "Body.\n\n<Leak />\n"
            ),
        },
    ]
    with file_system(files) as fs:
        secret = fs.temp_dir / "secret.txt"
        secret.write_text("TOP_SECRET_TOKEN_VALUE", encoding="utf-8")

        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()

        page = fs.build_dir / "langsmith/evil.mdx"
        body = builder._page_body(page)
        corpus = (fs.build_dir / "llms-full.txt").read_text(encoding="utf-8")

    # The traversing import is dropped, not followed.
    assert "TOP_SECRET_TOKEN_VALUE" not in body
    assert "TOP_SECRET_TOKEN_VALUE" not in corpus
    # The page itself still renders, minus the rejected import.
    assert "Body." in body


def test_resolve_within_blocks_escapes_and_allows_children() -> None:
    """Test the containment helper directly, including symlink-free traversal."""
    with file_system([]) as fs:
        fs.build_dir.mkdir(parents=True, exist_ok=True)
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        (fs.build_dir / "snippets").mkdir(parents=True, exist_ok=True)
        (fs.build_dir / "snippets/ok.mdx").write_text("fine", encoding="utf-8")
        (fs.temp_dir / "outside.txt").write_text("nope", encoding="utf-8")

        root = fs.build_dir / "snippets"
        inside = builder._resolve_within(fs.build_dir / "snippets/ok.mdx", root)
        escape = builder._resolve_within(
            fs.build_dir / "snippets/../../outside.txt", root
        )

    assert inside is not None
    assert escape is None


def test_section_indexes_are_always_named_llms_txt() -> None:
    """Test that oversized sections split by directory, never by filename.

    Mintlify serves the exact filename llms.txt at any path but 404s on
    anything else, so numbered variants like llms-2.txt are silently
    unreachable and every page in them drops out of coverage.
    """
    # Enough pages across real subdirectories to force a split.
    files: list[File] = [
        {
            "path": f"langsmith/{area}/page-{i:03d}.mdx",
            "content": f"---\ntitle: {area} {i}\n---\n\nBody.\n",
        }
        for area in ("alpha", "beta", "gamma")
        for i in range(250)
    ]
    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()

        indexes = sorted(
            p.relative_to(fs.build_dir).as_posix()
            for p in fs.build_dir.rglob("llms*.txt")
            if p.name != "llms-full.txt"
        )
        root = (fs.build_dir / "llms.txt").read_text(encoding="utf-8")

    assert len(indexes) > 1, "expected the section to split"
    # Every index, at every depth, is named exactly llms.txt.
    for path in indexes:
        assert path.endswith("llms.txt"), path
        assert "llms-" not in path, f"numbered index would 404: {path}"
    # And each split index is reachable in one hop from the root.
    for path in indexes:
        if path != "llms.txt":
            assert f"({builder._SITE_URL}/{path})" in root
