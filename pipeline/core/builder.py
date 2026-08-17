"""Documentation builder implementation."""

import json
import logging
import os
import re
import shutil
from pathlib import Path
from typing import ClassVar

import yaml
from tqdm import tqdm

from pipeline.preprocessors import preprocess_markdown

_IS_CI = os.environ.get("CI", "").lower() in ("true", "1")

logger = logging.getLogger(__name__)


class DocumentationBuilder:
    """Builds documentation from source files to build directory.

    This class handles the process of copying supported documentation files
    from a source directory to a build directory, maintaining the directory
    structure and preserving file metadata.

    Attributes:
        src_dir: Path to the source directory containing documentation files.
        build_dir: Path to the build directory where files will be copied.
        copy_extensions: Set of file extensions that are supported for copying.
    """

    def __init__(self, src_dir: Path, build_dir: Path) -> None:
        """Initialize the DocumentationBuilder.

        Args:
            src_dir: Path to the source directory containing documentation files.
            build_dir: Path to the build directory where files will be copied.
        """
        self.src_dir = src_dir
        self.build_dir = build_dir
        self.snippet_component_extensions: set[str] = {".jsx", ".tsx"}

        # File extensions to copy directly
        self.copy_extensions: set[str] = {
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
            *self.snippet_component_extensions,
            ".txt",
            ".woff2",
            ".woff",
            ".ttf",
            ".html",
        }

        # Mapping of language codes to full names for URLs
        self.language_url_names = {
            "python": "python",
            "js": "javascript",
        }

    def build_all(self) -> None:
        """Build all documentation files from source to build directory.

        This method clears the build directory and creates version-specific builds
        for both Python and JavaScript documentation.

        The process includes:
        1. Clearing the existing build directory
        2. Building Python version with python/ prefix
        3. Building JavaScript version with javascript/ prefix
        4. Copying shared files (images, configs, etc.)

        Displays:
            Progress bars showing build progress for each version.
        """
        logger.debug(
            "Building versioned documentation from %s to %s",
            self.src_dir,
            self.build_dir,
        )

        # Clear build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)

        # Build LangGraph versioned content (oss/ -> oss/python/ and oss/javascript/)
        logger.debug("Building LangGraph Python version...")
        self._build_langgraph_version("oss/python", "python")

        logger.debug("Building LangGraph JavaScript version...")
        self._build_langgraph_version("oss/javascript", "js")

        # Language-agnostic OSS products (no python/javascript URL split)
        logger.debug("Building Deep Agents Code (unversioned)...")
        self._build_unversioned_oss_code()

        logger.debug("Building OpenWiki (unversioned)...")
        self._build_unversioned_oss_openwiki()

        logger.debug("Building LangSmith content...")
        self._build_unversioned_content("langsmith", "langsmith")

        logger.debug("Building Managed Deep Agents language variants...")
        self._build_managed_deep_agents_versions()

        # Copy shared files (docs.json, images, etc.)
        logger.debug("Copying shared files...")
        self._copy_shared_files()

        # Copy snippet components from @langchain/docs-sandbox npm package
        logger.debug("Copying npm snippet components...")
        self._copy_npm_snippets()

        # Emit a custom llms.txt so the index is not truncated at 100K characters
        logger.debug("Generating llms.txt...")
        self._generate_llms_txt()

        logger.debug("Generating llms-full.txt...")
        self._generate_llms_full_txt()

        logger.debug("New structure build complete")

    def _convert_yaml_to_json(self, yaml_file_path: Path, output_path: Path) -> None:
        """Convert a YAML file to JSON format.

        This method loads a docs.yml file using YAML safe_load and writes
        the corresponding docs.json file to the build directory.

        Args:
            yaml_file_path: Path to the source YAML file.
            output_path: Path where the JSON file should be written.
        """
        try:
            # Load YAML content
            with yaml_file_path.open("r", encoding="utf-8") as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)

            # Convert output path from .yml to .json
            json_output_path = output_path.with_suffix(".json")

            # Write JSON content
            with json_output_path.open("w", encoding="utf-8") as json_file:
                json.dump(yaml_content, json_file, indent=2, ensure_ascii=False)

        except yaml.YAMLError:
            logger.exception("Failed to parse YAML file %s", yaml_file_path)
            raise
        except Exception:
            logger.exception("Failed to convert %s to JSON", yaml_file_path)
            raise

    def _rewrite_oss_links(self, content: str, target_language: str | None) -> str:
        """Rewrite /oss/ links to include the target language.

        Args:
            content: The markdown content to process.
            target_language: Target language ("python" or "js") or None to skip.

        Returns:
            Content with rewritten links.
        """
        if not target_language:
            return content

        def rewrite_link(match: re.Match) -> str:
            """Rewrite a single link match."""
            pre = match.group(1)  # Everything before the URL
            url = match.group(2)  # The URL
            post = match.group(3)  # Everything after the URL

            # Only rewrite absolute /oss/ paths that don't contain 'images'.
            # Skip paths that already specify a language (e.g. links from
            # unversioned langsmith pages to /oss/python/... or
            # /oss/javascript/...), otherwise the language is inserted a second
            # time and produces broken URLs like /oss/python/python/...
            # Also skip language-agnostic OSS product paths (Deep Agents Code,
            # OpenWiki): those pages are not duplicated under python/javascript.
            if (
                url.startswith("/oss/")
                and "images" not in url
                and not url.startswith("/oss/python/")
                and not url.startswith("/oss/javascript/")
                and not url.startswith("/oss/deepagents/code/")
                and url != "/oss/deepagents/code"
                and not url.startswith("/oss/openwiki/")
                and url != "/oss/openwiki"
            ):
                parts = url.split("/")
                # Insert full language name after "oss"
                parts.insert(2, self.language_url_names[target_language])
                url = "/".join(parts)

            return f"{pre}{url}{post}"

        # Match markdown links and HTML links/anchors
        # This handles both [text](/oss/path) and <a href="/oss/path">
        pattern = r'(\[.*?\]\(|\bhref="|")(/oss/[^")\s]+)([")\s])'
        return re.sub(pattern, rewrite_link, content)

    def _rewrite_managed_deep_agents_links(
        self, content: str, target_language: str | None
    ) -> str:
        """Rewrite Managed Deep Agents links to the target language route."""
        if not target_language:
            return content

        language = self.language_url_names[target_language]

        def rewrite_link(match: re.Match) -> str:
            prefix, url, suffix = match.groups()
            relative_url = url.removeprefix("/langsmith/")
            return f"{prefix}/langsmith/{language}/{relative_url}{suffix}"

        pattern = (
            r'(\[.*?\]\(|\bhref="|")'
            r'(/langsmith/managed-deep-agents[^"\)\s]*)'
            r'(["\)\s])'
        )
        return re.sub(pattern, rewrite_link, content)

    def _add_suggested_edits_link(self, content: str, input_path: Path) -> str:
        """Add 'Edit Source' link to the end of markdown content.

        This method appends GitHub links with icons pointing to the source file,
        but only for files that are within the src/ directory.

        Args:
            content: The markdown content to process.
            input_path: Path to the source file.

        Returns:
            The content with the source links appended (if applicable).
        """
        try:
            # Only add links for files in the src/ directory
            relative_path = input_path.absolute().relative_to(self.src_dir.absolute())

            # Do not add source links on the home page (root index.mdx)
            if relative_path.parts == ("index.mdx",):
                return content

            # Snippet files are imported into other pages — never append page footers.
            if "snippets" in relative_path.parts:
                return content

            # Construct the GitHub URLs
            edit_url = (
                f"https://github.com/langchain-ai/docs/edit/main/src/{relative_path}"
            )
            issue_url = "https://github.com/langchain-ai/docs/issues/new/choose"

            # Create the callout section with Mintlify Callout component
            source_links_section = (
                "\n\n---\n\n"
                '<div className="source-links">\n'
                '<Callout icon="terminal-2">\n'
                "    [Connect these docs](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.\n"  # noqa: E501
                "</Callout>\n"
                '<Callout icon="edit">\n'
                f"    [Edit this page on GitHub]({edit_url}) "
                f"or [file an issue]({issue_url}).\n"
                "</Callout>\n"
                "</div>\n"
            )

            # Append to content
            return content.rstrip() + source_links_section

        except ValueError:
            # File is not within src_dir, return content unchanged
            return content
        except Exception:
            logger.exception("Failed to add source links for %s", input_path)
            # Return original content if there's an error
            return content

    def _rewrite_snippet_imports_for_language(
        self, content: str, target_language: str
    ) -> str:
        """Point MDX snippet imports at language-specific copies under /snippets/{lang}/.

        Snippet markdown is emitted as absolute, language-prefixed /oss/ links in
        ``build/snippets/{python|javascript}/...``. Versioned pages must import
        those copies so nested consumers (e.g. langchain/frontend/*) resolve
        correctly. Already-prefixed imports are left unchanged.

        Args:
            content: Markdown/MDX source that may contain snippet imports.
            target_language: Target language ("python" or "js").

        Returns:
            Content with rewritten snippet import paths.
        """
        lang_name = self.language_url_names[target_language]
        pattern = r"""(from\s+)(['"])(/snippets/[^'"]+\.mdx?)\2"""

        def rewrite_import(match: re.Match) -> str:
            """Rewrite a single snippet import if it is not already language-scoped."""
            prefix, quote, path = match.group(1), match.group(2), match.group(3)
            rest = path[len("/snippets/") :]
            if rest.startswith(("python/", "javascript/")):
                return match.group(0)
            return f"{prefix}{quote}/snippets/{lang_name}/{rest}{quote}"

        return re.sub(pattern, rewrite_import, content)

    def _process_markdown_content(
        self, content: str, file_path: Path, target_language: str | None = None
    ) -> str:
        """Process markdown content with preprocessing.

        This method applies preprocessing (cross-reference resolution and
        conditional blocks) to markdown content.

        Args:
            content: The markdown content to process.
            file_path: Path to the source file (for error reporting).
            target_language: Target language for conditional blocks ("python" or "js").

        Returns:
            The processed markdown content.
        """
        try:
            # First apply standard markdown preprocessing
            content = preprocess_markdown(
                content, file_path, target_language=target_language
            )

            if target_language:
                content = self._rewrite_snippet_imports_for_language(
                    content, target_language
                )

            content = self._rewrite_oss_links(content, target_language)
            return self._rewrite_managed_deep_agents_links(content, target_language)

        except Exception:
            logger.exception("Failed to process markdown content from %s", file_path)
            raise

    def _process_markdown_file(
        self, input_path: Path, output_path: Path, target_language: str | None = None
    ) -> None:
        """Process a markdown file with preprocessing and copy to output.

        This method reads a markdown file, applies preprocessing (cross-reference
        resolution and conditional blocks), and writes the processed content to
        the output path.

        Args:
            input_path: Path to the source markdown file.
            output_path: Path where the processed file should be written.
            target_language: Target language for conditional blocks ("python" or "js").
        """
        try:
            # Read the source markdown content
            with input_path.open("r", encoding="utf-8") as f:
                content = f.read()

            # Apply markdown preprocessing
            processed_content = self._process_markdown_content(
                content, input_path, target_language
            )

            # Add "Edit Source" link for files in src/ directory
            processed_content = self._add_suggested_edits_link(
                processed_content, input_path
            )

            # Convert .md to .mdx if needed
            if input_path.suffix.lower() == ".md":
                output_path = output_path.with_suffix(".mdx")

            # Write the processed content
            with output_path.open("w", encoding="utf-8") as f:
                f.write(processed_content)

        except Exception:
            logger.exception("Failed to process markdown file %s", input_path)
            raise

    def build_file(self, file_path: Path) -> None:
        """Build a single file to the appropriate location(s) in the build directory.

        This method handles versioned building for OSS content (creates both Python
        and JavaScript versions) and single-version building for other content.
        The directory structure and version-specific preprocessing are preserved.

        Args:
            file_path: Path to the source file to be built. Must be within
                the source directory.

        Raises:
            AssertionError: If the file does not exist.
        """
        if not file_path.is_file():
            msg = f"File does not exist: {file_path} this is likely a programming error"
            raise AssertionError(msg)

        relative_path = file_path.absolute().relative_to(self.src_dir.absolute())

        # Check if this is OSS content that needs versioned building
        if relative_path.parts[0] == "oss":
            self._build_oss_file(file_path, relative_path)
        # Check if this is unversioned content
        elif relative_path.parts[0] == "langsmith":
            self._build_unversioned_file(file_path, relative_path)
        # Handle shared files (images, docs.json, etc.)
        elif self.is_shared_file(file_path):
            self._build_shared_file(file_path, relative_path)
        # Handle root-level files
        else:
            self._build_simple_file(file_path, relative_path)

    def is_unversioned_oss_file(self, file_path: Path) -> bool:
        """Return True for OSS files that must not be duplicated per language.

        Deep Agents Code ships one set of pages at ``/oss/deepagents/code/...``.
        OpenWiki ships one set of pages at ``/oss/openwiki/...``.
        """
        try:
            relative_path = file_path.absolute().relative_to(self.src_dir.absolute())
        except ValueError:
            return False
        parts = relative_path.parts
        if (
            len(parts) >= 3
            and parts[0] == "oss"
            and parts[1] == "deepagents"
            and parts[2] == "code"
        ):
            return True
        return len(parts) >= 2 and parts[0] == "oss" and parts[1] == "openwiki"

    def _build_oss_file(self, file_path: Path, relative_path: Path) -> None:
        """Build an OSS file for both Python and JavaScript versions.

        Args:
            file_path: Path to the source file.
            relative_path: Relative path from src_dir.
        """
        # Skip shared files - they're handled separately
        if self.is_shared_file(file_path):
            self._build_shared_file(file_path, relative_path)
            return

        # Language-agnostic OSS pages (Deep Agents Code) build once
        if self.is_unversioned_oss_file(file_path):
            output_path = self.build_dir / relative_path
            # Use python for :::python / :::js fences; /oss/deepagents/code/
            # links stay unprefixed via _rewrite_oss_links.
            if self._build_single_file_to_path(file_path, output_path, "python"):
                logger.debug("Built unversioned OSS file: %s", relative_path)
            return

        # Build for both Python and JavaScript versions
        oss_relative = relative_path.relative_to(Path("oss"))  # Remove 'oss/' prefix

        # Build Python version
        python_output = self.build_dir / "oss" / "python" / oss_relative
        if self._build_single_file_to_path(file_path, python_output, "python"):
            logger.debug("Built Python version: oss/python/%s", oss_relative)

        # Build JavaScript version
        js_output = self.build_dir / "oss" / "javascript" / oss_relative
        if self._build_single_file_to_path(file_path, js_output, "js"):
            logger.debug("Built JavaScript version: oss/javascript/%s", oss_relative)

    def is_managed_deep_agents_file(self, file_path: Path) -> bool:
        """Return whether a source file is a Managed Deep Agents page."""
        try:
            relative_path = file_path.absolute().relative_to(self.src_dir.absolute())
        except ValueError:
            return False
        return (
            relative_path.parent == Path("langsmith")
            and relative_path.name.startswith("managed-deep-agents")
            and relative_path.suffix.lower() in {".md", ".mdx"}
        )

    def _build_managed_deep_agents_variants(self, file_path: Path) -> None:
        """Build Python and JavaScript routes for a Managed Deep Agents page."""
        relative_path = file_path.absolute().relative_to(self.src_dir.absolute())
        langsmith_relative = relative_path.relative_to("langsmith")
        for language, output_name in self.language_url_names.items():
            output_path = (
                self.build_dir / "langsmith" / output_name / langsmith_relative
            )
            if self._build_single_file_to_path(file_path, output_path, language):
                logger.debug(
                    "Built Managed Deep Agents %s version: %s",
                    output_name,
                    langsmith_relative,
                )

    def _build_managed_deep_agents_versions(self) -> None:
        """Build language-specific routes for all Managed Deep Agents pages."""
        langsmith_dir = self.src_dir / "langsmith"
        if not langsmith_dir.exists():
            return
        for file_path in langsmith_dir.glob("managed-deep-agents*.mdx"):
            self._build_managed_deep_agents_variants(file_path)

    def _build_unversioned_file(self, file_path: Path, relative_path: Path) -> None:
        """Build an unversioned file (langsmith).

        Managed Deep Agents pages only emit language-prefixed routes
        (``langsmith/python/...`` and ``langsmith/javascript/...``). The
        unversioned ``/langsmith/managed-deep-agents*`` URLs redirect to the
        Python routes via ``docs.json`` so Mintlify does not serve orphaned
        pages outside the Managed Deep Agents nav.

        Args:
            file_path: Path to the source file.
            relative_path: Relative path from src_dir.
        """
        if self.is_managed_deep_agents_file(file_path):
            self._build_managed_deep_agents_variants(file_path)
            return

        output_path = self.build_dir / relative_path
        if self._build_single_file_to_path(file_path, output_path, "python"):
            logger.debug("Built: %s", relative_path)

    def _build_shared_file(self, file_path: Path, relative_path: Path) -> None:
        """Build a shared file (images, docs.json, JS/CSS files).

        Args:
            file_path: Path to the source file.
            relative_path: Relative path from src_dir.
        """
        output_path = self.build_dir / relative_path
        if self._build_single_file_to_path(file_path, output_path, None):
            logger.debug("Built shared file: %s", relative_path)

    def _build_simple_file(self, file_path: Path, relative_path: Path) -> None:
        """Build a simple file (root-level files).

        Args:
            file_path: Path to the source file.
            relative_path: Relative path from src_dir.
        """
        output_path = self.build_dir / relative_path
        if self._build_single_file_to_path(file_path, output_path, None):
            logger.debug("Built: %s", relative_path)

    def _build_single_file_to_path(
        self, file_path: Path, output_path: Path, target_language: str | None
    ) -> bool:
        """Build a single file to a specific output path.

        Args:
            file_path: Path to the source file.
            output_path: Full output path where the file should be written.
            target_language: Target language for conditional blocks ("python" or "js").

        Returns:
            True if the file was built successfully, False if skipped.
        """
        # Skip template files
        if file_path.name == "TEMPLATE.mdx":
            return False

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle special case for docs.yml files
        if file_path.name == "docs.yml" and file_path.suffix.lower() in {
            ".yml",
            ".yaml",
        }:
            self._convert_yaml_to_json(file_path, output_path)
            return True

        # Handle supported file extensions
        if file_path.suffix.lower() in self.copy_extensions:
            # Handle markdown files with preprocessing
            if file_path.suffix.lower() in {".md", ".mdx"}:
                self._process_markdown_file(file_path, output_path, target_language)
                return True
            shutil.copy2(file_path, output_path)
            return True

        # File was skipped
        return False

    def _build_file_with_progress(self, file_path: Path, pbar: tqdm) -> bool:
        """Build a single file with progress bar integration.

        This method is similar to build_file but integrates with tqdm progress
        bar and returns a boolean result instead of printing messages.

        Args:
            file_path: Path to the source file to be built. Must be within
                the source directory.
            pbar: tqdm progress bar instance for updating the description.

        Returns:
            True if the file was copied, False if it was skipped.
        """
        # Skip template files
        if file_path.name == "TEMPLATE.mdx":
            return False

        relative_path = file_path.absolute().relative_to(self.src_dir.absolute())
        output_path = self.build_dir / relative_path

        # Update progress bar description with current file
        pbar.set_postfix_str(f"{relative_path}")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle special case for docs.yml files
        if file_path.name == "docs.yml" and file_path.suffix.lower() in {
            ".yml",
            ".yaml",
        }:
            self._convert_yaml_to_json(file_path, output_path)
            return True
        # Copy other supported files directly
        if file_path.suffix.lower() in self.copy_extensions:
            # Handle markdown files with preprocessing
            if file_path.suffix.lower() in {".md", ".mdx"}:
                if self.is_managed_deep_agents_file(file_path):
                    self._build_unversioned_file(file_path, relative_path)
                else:
                    self._process_markdown_file(file_path, output_path)
                return True
            shutil.copy2(file_path, output_path)
            return True
        return False

    def build_files(self, file_paths: list[Path]) -> None:
        """Build specific files by copying them to the build directory.

        This method processes a list of specific files, building only those
        that exist. Shows a progress bar when processing multiple files.

        Args:
            file_paths: List of Path objects pointing to files to be built.
                Only existing files will be processed.
        """
        existing_files = list(file_paths)

        if not existing_files:
            logger.info("No files to build")
            return

        if len(existing_files) == 1:
            # For single file, just build directly without progress bar
            self.build_file(existing_files[0])
            return

        # For multiple files, show progress bar
        copied_count = 0
        skipped_count = 0

        with tqdm(
            total=len(existing_files),
            desc="Building files",
            unit="file",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            dynamic_ncols=True,
            leave=False,
            disable=_IS_CI,
        ) as pbar:
            for file_path in existing_files:
                result = self._build_file_with_progress(file_path, pbar)
                if result:
                    copied_count += 1
                else:
                    skipped_count += 1
                pbar.update(1)

        logger.info(
            "✅ Build complete: %d files copied, %d files skipped",
            copied_count,
            skipped_count,
        )

    def _build_langgraph_version(self, output_dir: str, target_language: str) -> None:
        """Build LangGraph (oss/) content for a specific version.

        Args:
            output_dir: Output directory (e.g., "langgraph/python").
            target_language: Target language for conditional blocks ("python" or "js").
        """
        # Only process files in the oss/ directory
        oss_dir = self.src_dir / "oss"
        if not oss_dir.exists():
            logger.warning("oss/ directory not found, skipping LangGraph build")
            return

        all_files = [
            file_path
            for file_path in self._safe_source_files(oss_dir)
            if not self.is_shared_file(file_path)
        ]

        if not all_files:
            logger.info("No files found in oss/ directory for %s", output_dir)
            return

        # Process files with progress bar
        copied_count: int = 0
        skipped_count: int = 0

        with tqdm(
            total=len(all_files),
            desc=f"Building {output_dir} files",
            unit="file",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            dynamic_ncols=True,
            leave=False,
            disable=_IS_CI,
        ) as pbar:
            for file_path in all_files:
                # Calculate relative path from oss/ directory
                relative_path = file_path.relative_to(oss_dir)

                if relative_path.parts:
                    first_part = relative_path.parts[0]
                    if first_part in ("python", "javascript"):
                        # Map target_language to expected directory name
                        expected_dir = (
                            "python" if target_language == "python" else "javascript"
                        )
                        # Skip files that are for a different language
                        # (i.e. if we're building for python and we encounter
                        #  `oss/javascript/...`, skip it)
                        if first_part != expected_dir:
                            pbar.update(1)
                            continue
                        # Remove the language-specific directory from the path
                        # e.g., "python/concepts/low_level.md" > "concepts/low_level.md"
                        relative_path = Path(*relative_path.parts[1:])

                # Language-agnostic OSS products are built once under their
                # own paths (not duplicated into python/javascript trees).
                if relative_path.parts[:2] == ("deepagents", "code"):
                    pbar.update(1)
                    continue
                if relative_path.parts[:1] == ("openwiki",):
                    pbar.update(1)
                    continue

                # Build to output_dir/ (not `output_dir/oss/`)
                output_path = self.build_dir / output_dir / relative_path

                result = self._build_single_file(
                    file_path,
                    output_path,
                    target_language,
                    pbar,
                    f"{output_dir}/{relative_path}",
                )
                if result:
                    copied_count += 1
                else:
                    skipped_count += 1
                pbar.update(1)

        logger.info(
            "✅ %s complete: %d files copied, %d files skipped",
            output_dir,
            copied_count,
            skipped_count,
        )

    def _build_unversioned_oss_code(self) -> None:
        """Build Deep Agents Code once at ``oss/deepagents/code/``.

        These pages are language-agnostic (no python/javascript URL split).
        Conditional blocks use the Python branch; ``/oss/deepagents/code/``
        links are left unprefixed by ``_rewrite_oss_links``.
        """
        code_dir = self.src_dir / "oss" / "deepagents" / "code"
        if not code_dir.exists():
            logger.warning("oss/deepagents/code/ directory not found, skipping")
            return

        all_files = [
            file_path
            for file_path in self._safe_source_files(code_dir)
            if not self.is_shared_file(file_path)
        ]

        if not all_files:
            logger.info("No files found in oss/deepagents/code/")
            return

        copied_count = 0
        skipped_count = 0
        output_root = self.build_dir / "oss" / "deepagents" / "code"

        with tqdm(
            total=len(all_files),
            desc="Building oss/deepagents/code files",
            unit="file",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            dynamic_ncols=True,
            leave=False,
            disable=_IS_CI,
        ) as pbar:
            for file_path in all_files:
                relative_path = file_path.relative_to(code_dir)
                output_path = output_root / relative_path
                result = self._build_single_file(
                    file_path,
                    output_path,
                    "python",
                    pbar,
                    f"oss/deepagents/code/{relative_path}",
                )
                if result:
                    copied_count += 1
                else:
                    skipped_count += 1
                pbar.update(1)

        logger.info(
            "✅ oss/deepagents/code complete: %d files copied, %d files skipped",
            copied_count,
            skipped_count,
        )

    def _build_unversioned_oss_openwiki(self) -> None:
        """Build OpenWiki once at ``oss/openwiki/``.

        These pages are language-agnostic (no python/javascript URL split).
        Conditional blocks use the Python branch; ``/oss/openwiki/`` links are
        left unprefixed by ``_rewrite_oss_links``.
        """
        openwiki_dir = self.src_dir / "oss" / "openwiki"
        if not openwiki_dir.exists():
            logger.warning("oss/openwiki/ directory not found, skipping")
            return

        all_files = [
            file_path
            for file_path in self._safe_source_files(openwiki_dir)
            if not self.is_shared_file(file_path)
        ]

        if not all_files:
            logger.info("No files found in oss/openwiki/")
            return

        copied_count = 0
        skipped_count = 0
        output_root = self.build_dir / "oss" / "openwiki"

        with tqdm(
            total=len(all_files),
            desc="Building oss/openwiki files",
            unit="file",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            dynamic_ncols=True,
            leave=False,
            disable=_IS_CI,
        ) as pbar:
            for file_path in all_files:
                relative_path = file_path.relative_to(openwiki_dir)
                output_path = output_root / relative_path
                result = self._build_single_file(
                    file_path,
                    output_path,
                    "python",
                    pbar,
                    f"oss/openwiki/{relative_path}",
                )
                if result:
                    copied_count += 1
                else:
                    skipped_count += 1
                pbar.update(1)

        logger.info(
            "✅ oss/openwiki complete: %d files copied, %d files skipped",
            copied_count,
            skipped_count,
        )

    def _build_unversioned_content(self, source_dir: str, output_dir: str) -> None:
        """Build unversioned content (langsmith/).

        Args:
            source_dir: Source directory name (e.g., "langsmith").
            output_dir: Output directory name (same as source_dir).
        """
        src_path = self.src_dir / source_dir
        if not src_path.exists():
            logger.warning("%s/ directory not found, skipping", source_dir)
            return

        all_files = [
            file_path
            for file_path in self._safe_source_files(src_path)
            if not self.is_shared_file(file_path)
            # Managed Deep Agents emit language-prefixed routes only
            # (see `_build_managed_deep_agents_versions`).
            and not self.is_managed_deep_agents_file(file_path)
        ]

        if not all_files:
            logger.info("No files found in %s/ directory", source_dir)
            return

        # Process files with progress bar
        copied_count: int = 0
        skipped_count: int = 0

        with tqdm(
            total=len(all_files),
            desc=f"Building {output_dir} files",
            unit="file",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            dynamic_ncols=True,
            leave=False,
            disable=_IS_CI,
        ) as pbar:
            for file_path in all_files:
                # Calculate relative path from source directory
                relative_path = file_path.relative_to(src_path)
                # Build directly to output_dir/
                output_path = self.build_dir / output_dir / relative_path

                result = self._build_single_file(
                    file_path,
                    output_path,
                    "python",
                    pbar,
                    f"{output_dir}/{relative_path}",
                )
                if result:
                    copied_count += 1
                else:
                    skipped_count += 1
                pbar.update(1)

        logger.info(
            "✅ %s complete: %d files copied, %d files skipped",
            output_dir,
            copied_count,
            skipped_count,
        )

    def _build_single_file(
        self,
        file_path: Path,
        output_path: Path,
        target_language: str,
        pbar: tqdm,
        display_path: str,
    ) -> bool:
        """Build a single file with progress bar integration.

        Args:
            file_path: Path to the source file to be built.
            output_path: Full output path for the file.
            target_language: Target language for conditional blocks ("python" or "js").
            pbar: tqdm progress bar instance for updating the description.
            display_path: Path to display in progress bar.

        Returns:
            True if the file was copied, False if it was skipped.
        """
        # Skip template files
        if file_path.name == "TEMPLATE.mdx":
            return False

        # Update progress bar description with current file
        pbar.set_postfix_str(display_path)

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle special case for docs.yml files
        if file_path.name == "docs.yml" and file_path.suffix.lower() in {
            ".yml",
            ".yaml",
        }:
            self._convert_yaml_to_json(file_path, output_path)
            return True
        # Copy other supported files
        if file_path.suffix.lower() in self.copy_extensions:
            # Handle markdown files with preprocessing
            if file_path.suffix.lower() in {".md", ".mdx"}:
                self._process_markdown_file(file_path, output_path, target_language)
                return True
            shutil.copy2(file_path, output_path)
            return True
        return False

    def _build_version_file_with_progress(
        self, file_path: Path, version_dir: str, target_language: str, pbar: tqdm
    ) -> bool:
        """Build a single file for a specific version with progress bar integration.

        Args:
            file_path: Path to the source file to be built.
            version_dir: Directory name for this version (e.g., "python", "javascript").
            target_language: Target language for conditional blocks ("python" or "js").
            pbar: tqdm progress bar instance for updating the description.

        Returns:
            True if the file was copied, False if it was skipped.
        """
        relative_path = file_path.absolute().relative_to(self.src_dir.absolute())
        # Add version prefix to the output path
        output_path = self.build_dir / version_dir / relative_path

        # Update progress bar description with current file
        pbar.set_postfix_str(f"{version_dir}/{relative_path}")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle special case for docs.yml files
        if file_path.name == "docs.yml" and file_path.suffix.lower() in {
            ".yml",
            ".yaml",
        }:
            self._convert_yaml_to_json(file_path, output_path)
            return True
        # Copy other supported files
        if file_path.suffix.lower() in self.copy_extensions:
            # Handle markdown files with preprocessing
            if file_path.suffix.lower() in {".md", ".mdx"}:
                self._process_markdown_file(file_path, output_path, target_language)
                return True
            shutil.copy2(file_path, output_path)
            return True
        return False

    def _safe_source_files(self, root: Path) -> list[Path]:
        """Collect regular files under ``root``, rejecting symlinks.

        Symlinks are skipped even when they target regular files, so a
        committed symlink cannot pull host paths (for example
        ``/proc/self/environ``) into build artifacts. Resolved paths must
        stay under ``root``.
        """
        try:
            root_resolved = root.resolve()
        except OSError:
            logger.warning("Could not resolve source root %s", root)
            return []

        files: list[Path] = []
        for file_path in root.rglob("*"):
            if file_path.is_symlink():
                logger.warning("Skipping symlink in source tree: %s", file_path)
                continue
            if not file_path.is_file():
                continue
            try:
                file_path.resolve().relative_to(root_resolved)
            except ValueError:
                logger.warning(
                    "Skipping file that resolves outside %s: %s",
                    root,
                    file_path,
                )
                continue
            files.append(file_path)
        return files

    def is_shared_file(self, file_path: Path) -> bool:
        """Check if a file should be shared between versions rather than duplicated.

        Args:
            file_path: Path to check.

        Returns:
            True if the file should be shared, False if it should be version-specific.
        """
        relative_path = file_path.absolute().relative_to(self.src_dir.absolute())

        if file_path.name == "docs.json":
            return True

        # Root-level files that should be shared
        if len(relative_path.parts) == 1 and file_path.name in {
            "index.mdx",
            "use-these-docs.mdx",
            "playground.mdx",
            "build-overview.mdx",
        }:
            return True

        # Snippets are imported from MDX through /snippets/... paths. This
        # includes MDX snippets and local React components such as .tsx files.
        if "snippets" in relative_path.parts:
            return True

        # Directories whose contents should be shared
        shared_dirs = {"images", ".well-known", "fonts"}
        if shared_dirs & set(relative_path.parts):
            return True

        # JavaScript and CSS files should be shared (custom scripts/styles)
        return file_path.suffix.lower() in {".js", ".css"}

    # llms.txt sections, in emission order. Hand-authored docs come before
    # generated API reference so the most useful pages are read first.
    _LLMS_SECTIONS: ClassVar[list[tuple[str, str]]] = [
        ("oss/python", "Open source (Python)"),
        ("oss/javascript", "Open source (TypeScript)"),
        ("oss", "Open source"),
        ("langsmith/fleet", "LangSmith Fleet"),
        ("langsmith", "LangSmith"),
    ]

    _SITE_URL = "https://docs.langchain.com"

    # A section smaller than this stays in the root file rather than becoming a
    # separate fetch. Root stays far below the 50,000-character pass threshold.
    _LLMS_INLINE_MAX = 8_000

    # Per-section-file ceiling. Headroom under the 50,000-character threshold
    # so a section does not cross it as pages are added between splits.
    _LLMS_SECTION_BUDGET = 40_000

    # Size at which agent platforms start truncating an index. Every emitted
    # file has to stay under it, not just the root.
    _LLMS_MAX = 50_000

    # Page-path prefixes lifted out of the root llms-full.txt into their own
    # corpus file, with the label used to point at them from the root.
    _LLMS_FULL_SPLITS: ClassVar[list[tuple[str, str]]] = [
        ("oss/python", "Open source (Python)"),
        ("oss/javascript", "Open source (TypeScript)"),
    ]

    _SNIPPET_IMPORT = re.compile(
        r"^import\s+(\w+)\s+from\s+'(/snippets/[^']+)';[ \t]*\n?", re.MULTILINE
    )

    @staticmethod
    def _slugify(value: str) -> str:
        """Lowercase, hyphenate, and strip a string for use in a URL path.

        Apostrophes are dropped rather than turned into separators, matching
        Mintlify: "Get the authenticated user's provider user ID" slugs to
        ``...-users-provider-user-id``, not ``...-user-s-...``.
        """
        cleaned = re.sub(r"['’]", "", value.lower())
        return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", cleaned)).strip("-")

    @staticmethod
    def _tag_slug(value: str) -> str:
        """Slug an OpenAPI tag the way Mintlify does, preserving underscores.

        Mintlify lowercases the tag and replaces whitespace, but otherwise uses
        it verbatim. Underscores must survive: the LangSmith spec carries both
        ``annotation-queues`` and ``annotation_queues`` as distinct tags that
        render to different directories, so normalising them together would
        point at pages that do not exist.
        """
        return re.sub(r"[^a-z0-9_-]+", "-", value.lower()).strip("-")

    def _read_frontmatter(self, path: Path) -> dict:
        """Return the YAML frontmatter of an MDX file, or an empty dict."""
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return {}
        if not text.startswith("---"):
            return {}
        end = text.find("\n---", 3)
        if end == -1:
            return {}
        try:
            data = yaml.safe_load(text[3:end])
        except yaml.YAMLError:
            return {}
        return data if isinstance(data, dict) else {}

    def _openapi_entries(self) -> list[tuple[str, str, str]]:
        """Return (section, url, title) for every Mintlify-generated API page.

        Mintlify renders one page per OpenAPI operation under the group's
        ``directory``, slugged as ``<directory>/<tag>/<summary>``. Those pages
        never exist as MDX, so they have to be derived from the spec itself or
        they are missing from llms.txt entirely.
        """
        docs_json = self.build_dir / "docs.json"
        if not docs_json.exists():
            return []
        try:
            config = json.loads(docs_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.warning("Could not read docs.json for OpenAPI entries")
            return []

        # (section label, spec source path, output directory)
        groups: list[tuple[str, str, str]] = []

        def find_openapi(node: object) -> None:
            if isinstance(node, dict):
                mapping: dict[str, object] = {str(k): v for k, v in node.items()}
                spec = mapping.get("openapi")
                if isinstance(spec, dict):
                    fields: dict[str, object] = {str(k): v for k, v in spec.items()}
                    source = fields.get("source")
                    directory = fields.get("directory")
                    if isinstance(source, str) and isinstance(directory, str):
                        label = mapping.get("group")
                        groups.append(
                            (
                                label if isinstance(label, str) else "API reference",
                                source,
                                directory,
                            )
                        )
                for value in mapping.values():
                    find_openapi(value)
            elif isinstance(node, list):
                for item in node:
                    find_openapi(item)

        find_openapi(config.get("navigation"))

        entries: list[tuple[str, str, str]] = []
        for label, source, directory in groups:
            spec_path = self._resolve_within(self.build_dir / source, self.build_dir)
            if spec_path is None or not spec_path.exists():
                logger.warning("OpenAPI spec not found or outside build: %s", source)
                continue
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                logger.warning("Could not parse OpenAPI spec: %s", source)
                continue

            base = directory.strip("/")
            seen: set[str] = set()
            for item in spec.get("paths", {}).values():
                if not isinstance(item, dict):
                    continue
                for operation in item.values():
                    if not isinstance(operation, dict) or "responses" not in operation:
                        continue
                    # Mintlify renders no page for hidden operations.
                    if operation.get("x-hidden"):
                        continue
                    summary = operation.get("summary") or operation.get("operationId")
                    if not summary:
                        continue
                    tags = operation.get("tags") or ["default"]
                    slug = (
                        f"{self._tag_slug(str(tags[0]))}/{self._slugify(str(summary))}"
                    )
                    # Two operations can share a summary. Mintlify keeps both
                    # and disambiguates with a numeric suffix, so mirror that
                    # rather than dropping the second page.
                    unique, duplicate_index = slug, 0
                    while unique in seen:
                        duplicate_index += 1
                        unique = f"{slug}-{duplicate_index}"
                    seen.add(unique)
                    entries.append((label, f"{base}/{unique}", str(summary)))
        return entries

    @staticmethod
    def _resolve_within(candidate: Path, root: Path) -> Path | None:
        """Resolve *candidate* and return it only if it stays inside *root*.

        Paths that reach this point come from MDX text and docs.json, both of
        which are editable in a pull request. ``Path.__truediv__`` does not
        collapse ``..``, so joining an unvalidated path and reading it would
        let a crafted import escape the build tree. CI commits ``build/`` to a
        pushed preview branch, so anything read would be published.

        Returns:
            The resolved path, or None if it escapes *root* or cannot resolve.
        """
        try:
            resolved = candidate.resolve()
            resolved.relative_to(root.resolve())
        except (ValueError, OSError):
            return None
        return resolved

    @staticmethod
    def _common_directory(slugs: list[str]) -> str:
        """Return the deepest directory shared by every slug, or "" if none."""
        if not slugs:
            return ""
        parts = [slug.split("/")[:-1] for slug in slugs]
        shared = parts[0]
        for candidate in parts[1:]:
            keep = 0
            for a, b in zip(shared, candidate):
                if a != b:
                    break
                keep += 1
            shared = shared[:keep]
            if not shared:
                return ""
        return "/".join(shared)

    @staticmethod
    def _weigh(entries: list[tuple[str, str]]) -> int:
        """Return the byte size a set of index entries would occupy."""
        return sum(len(line) + 1 for _, line in entries)

    def _chunk_section(
        self, prefix: str, entries: list[tuple[str, str]]
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        """Split a section into index files that each stay under budget.

        Returns (directory prefix, entries) pairs. Every index is written as
        ``<prefix>/llms.txt``, because Mintlify serves that exact filename at
        any path but 404s on anything else: numbered variants like
        ``llms-2.txt`` are not served, which silently hid 802 pages from the
        coverage walker.

        An oversized section sheds its largest child directories into their own
        indexes until the remainder fits, rather than giving every child a file.
        That keeps the number of fetches an agent makes proportional to how
        much content there actually is.
        """
        if self._weigh(entries) <= self._LLMS_SECTION_BUDGET:
            return [(prefix, entries)]

        depth = len(prefix.split("/")) if prefix else 0
        children: dict[str, list[tuple[str, str]]] = {}
        remainder: list[tuple[str, str]] = []
        for slug, line in entries:
            parts = slug.split("/")
            if len(parts) > depth + 1:
                children.setdefault("/".join(parts[: depth + 1]), []).append(
                    (slug, line)
                )
            else:
                remainder.append((slug, line))

        if not children:
            # A flat directory cannot be subdivided further. Keep it whole:
            # oversized beats invisible, and the validator will flag it.
            return [(prefix, entries)]

        out: list[tuple[str, list[tuple[str, str]]]] = []
        # Shed the heaviest children first so the fewest files are created.
        for key in sorted(children, key=lambda k: -self._weigh(children[k])):
            if self._weigh(remainder) + self._weigh(children[key]) <= (
                self._LLMS_SECTION_BUDGET
            ):
                remainder += children[key]
            else:
                out += self._chunk_section(key, children[key])
        return [(prefix, remainder), *out] if remainder else out

    def _write_section_index(
        self, path: str, title: str, label: str, lines: list[str]
    ) -> None:
        """Write one section-level llms.txt."""
        destination = self._resolve_within(self.build_dir / path, self.build_dir)
        if destination is None:
            logger.warning("Refusing to write section index outside build: %s", path)
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join(
            [
                f"# {title}: {label}",
                "",
                f"> Markdown index of the {label} documentation.",
                "",
                f"## {label}",
                "",
                *lines,
                "",
            ]
        )
        destination.write_text(body, encoding="utf-8")

    def _validate_llms_indexes(self, expected_pages: int) -> None:
        """Check the generated indexes against the invariants agents rely on.

        These are properties of the emitted files, not of the code that emits
        them, so they catch drift the unit tests cannot: a root that creeps
        over the size threshold as pages are added, a section index that
        accidentally nests, or a page that lands in two indexes or none.

        Raises:
            ValueError: If any invariant is violated.
        """
        root_path = self.build_dir / "llms.txt"
        if not root_path.exists():
            return

        md_link = re.compile(r"\((https://\S+?\.md)\)")
        txt_link = re.compile(r"\((https://\S+?llms[\w-]*\.txt)\)")

        root = root_path.read_text(encoding="utf-8")
        problems: list[str] = []

        if len(root) > self._LLMS_MAX:
            problems.append(
                f"llms.txt is {len(root):,} characters, over the "
                f"{self._LLMS_MAX:,} threshold agents truncate at"
            )

        urls = md_link.findall(root)
        for url in txt_link.findall(root):
            relative = url.removeprefix(f"{self._SITE_URL}/")
            section_path = self._resolve_within(
                self.build_dir / relative, self.build_dir
            )
            if section_path is None or not section_path.exists():
                problems.append(f"{relative} is linked from llms.txt but missing")
                continue
            section = section_path.read_text(encoding="utf-8")
            if len(section) > self._LLMS_MAX:
                problems.append(
                    f"{relative} is {len(section):,} characters, over the "
                    f"{self._LLMS_MAX:,} threshold"
                )
            nested = txt_link.findall(section)
            if nested:
                problems.append(
                    f"{relative} links to {len(nested)} further .txt files; "
                    "coverage walkers descend only one level, so those pages "
                    "would drop out of the index"
                )
            urls += md_link.findall(section)

        duplicates = {url for url in urls if urls.count(url) > 1}
        if duplicates:
            sample = ", ".join(sorted(duplicates)[:3])
            problems.append(f"{len(duplicates)} pages listed more than once: {sample}")

        if len(set(urls)) != expected_pages:
            problems.append(
                f"indexes list {len(set(urls)):,} unique pages "
                f"but {expected_pages:,} were built"
            )

        if problems:
            detail = "\n  - ".join(problems)
            msg = f"Generated llms.txt indexes are invalid:\n  - {detail}"
            raise ValueError(msg)

        logger.info(
            "✅ llms.txt indexes valid: %d pages, root %d/%d characters",
            expected_pages,
            len(root),
            self._LLMS_MAX,
        )

    def _site_metadata(self) -> tuple[str, str]:
        """Return the site title and description from docs.json."""
        docs_json = self.build_dir / "docs.json"
        title, description = "Docs by LangChain", ""
        if docs_json.exists():
            try:
                config = json.loads(docs_json.read_text(encoding="utf-8"))
                title = config.get("name", title)
                description = config.get("description", "")
            except (OSError, json.JSONDecodeError):
                logger.warning("Could not read docs.json for site metadata")
        return title, description

    def _page_body(self, path: Path, depth: int = 0) -> str:
        """Return an MDX page's body with frontmatter stripped, snippets inlined.

        Mintlify expands snippet imports when it renders, so a corpus built
        from the raw build tree would silently drop content from the ~300
        pages that import snippets. Component props are ignored: the snippet
        body is the content, and the corpus is plain text.
        """
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                text = text[end + 4 :]
        if depth > 6:
            return text.strip()

        snippets_root = self.build_dir / "snippets"
        imports: dict[str, Path] = {}
        for name, target in self._SNIPPET_IMPORT.findall(text):
            snippet = self._resolve_within(
                self.build_dir / target.lstrip("/"), snippets_root
            )
            if snippet is None:
                logger.warning(
                    "Ignoring snippet import outside %s in %s: %s",
                    snippets_root,
                    path,
                    target,
                )
                continue
            imports[name] = snippet

        text = self._SNIPPET_IMPORT.sub("", text)
        for name, snippet in imports.items():
            body = self._page_body(snippet, depth + 1) if snippet.exists() else ""
            text = re.sub(rf"<{name}(?:\s[^/>]*)?\s*/>", lambda _, b=body: b, text)
        return text.strip()

    def _generate_llms_full_txt(self) -> None:
        """Write llms-full.txt, splitting language variants into their own files.

        The combined corpus is dominated by the Python and TypeScript renders
        of the same documentation. Keeping both in one file makes it far larger
        than long-context agents can ingest, so the TypeScript pages move to
        their own corpus and the root points at it.
        """
        title, description = self._site_metadata()
        buckets: dict[str, list[str]] = {"": []}
        for prefix, _ in self._LLMS_FULL_SPLITS:
            buckets[prefix] = []

        for mdx in sorted(self.build_dir.rglob("*.mdx")):
            relative = mdx.relative_to(self.build_dir)
            if relative.parts and relative.parts[0] == "snippets":
                continue
            meta = self._read_frontmatter(mdx)
            if meta.get("noindex") is True:
                continue
            slug = relative.with_suffix("").as_posix()
            name = str(
                meta.get("title")
                or meta.get("sidebarTitle")
                or slug.rsplit("/", 1)[-1].replace("-", " ").title()
            )
            key = next(
                (p for p, _ in self._LLMS_FULL_SPLITS if slug.startswith(f"{p}/")), ""
            )
            body = self._page_body(mdx)
            buckets[key].append(
                f"# {name}\nSource: {self._SITE_URL}/{slug}\n\n{body}\n\n"
            )

        # Generated API reference pages have no MDX to read, so record their
        # identity and let the index in llms.txt carry the detail.
        for _, slug, name in self._openapi_entries():
            buckets[""].append(f"# {name}\nSource: {self._SITE_URL}/{slug}\n\n")

        if not any(buckets.values()):
            logger.debug("No pages found, skipping llms-full.txt")
            return

        pointers = []
        for prefix, label in self._LLMS_FULL_SPLITS:
            if not buckets[prefix]:
                continue
            target = f"{prefix}/llms-full.txt"
            destination = self.build_dir / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                f"# {title}: {label}\n\n"
                f"> Full text of the {label} documentation.\n\n"
                + "\n".join(buckets[prefix]),
                encoding="utf-8",
            )
            pointers.append(f"- {label} documentation: {self._SITE_URL}/{target}")
            logger.info(
                "✅ %s written: %d pages, %d characters",
                target,
                len(buckets[prefix]),
                destination.stat().st_size,
            )

        # A custom llms-full.txt has to open with the site title as an H1, or
        # the first page heading in the corpus reads as the site title.
        header = [f"# {title}", ""]
        if description:
            header += [f"> {description}", ""]
        if pointers:
            header += [
                "Language-specific documentation is published as a separate corpus:",
                "",
                *pointers,
                "",
            ]
        content = "\n".join(header) + "\n" + "\n".join(buckets[""])
        (self.build_dir / "llms-full.txt").write_text(content, encoding="utf-8")
        logger.info(
            "✅ llms-full.txt written: %d pages, %d characters",
            len(buckets[""]),
            len(content),
        )

    def _generate_llms_txt(self) -> None:
        """Write a custom llms.txt listing every published page.

        Mintlify caps its auto-generated llms.txt at 100,000 characters and
        silently truncates past that, which drops several hundred pages. A
        custom file at the project root overrides the generated one and is not
        capped, so this emits the complete index instead.
        """
        docs_json = self.build_dir / "docs.json"
        title, description = "Docs by LangChain", ""
        if docs_json.exists():
            try:
                config = json.loads(docs_json.read_text(encoding="utf-8"))
                title = config.get("name", title)
                description = config.get("description", "")
            except (OSError, json.JSONDecodeError):
                logger.warning("Could not read docs.json for llms.txt metadata")

        # section label -> list of (slug, "- [Title](url)") pairs
        sections: dict[str, list[tuple[str, str]]] = {}
        # plain entry -> the same entry with its description, for the root file
        described_lines: dict[str, str] = {}
        page_count = 0

        for mdx in sorted(self.build_dir.rglob("*.mdx")):
            relative = mdx.relative_to(self.build_dir)
            if relative.parts and relative.parts[0] == "snippets":
                continue
            meta = self._read_frontmatter(mdx)
            if meta.get("noindex") is True:
                continue

            slug = relative.with_suffix("").as_posix()
            url = f"{self._SITE_URL}/{slug}.md"
            name = str(
                meta.get("title")
                or meta.get("sidebarTitle")
                or slug.rsplit("/", 1)[-1].replace("-", " ").title()
            )
            summary = str(meta.get("description") or "").replace("\n", " ").strip()

            label = "Docs"
            for prefix, section_label in self._LLMS_SECTIONS:
                if slug == prefix or slug.startswith(f"{prefix}/"):
                    label = section_label
                    break

            # Descriptions roughly double an entry. They stay in the root file,
            # where there is room, and are dropped from section indexes so more
            # pages fit per file and fewer files are needed.
            line = f"- [{name}]({url})"
            if summary:
                described_lines[line] = f"{line}: {summary[:300]}"
            sections.setdefault(label, []).append((slug, line))
            page_count += 1

        for group_label, api_slug, name in self._openapi_entries():
            sections.setdefault(group_label, []).append(
                (api_slug, f"- [{name}]({self._SITE_URL}/{api_slug}.md)")
            )
            page_count += 1

        if not page_count:
            logger.debug("No pages found, skipping llms.txt")
            return

        ordered = ["Docs", *[label for _, label in self._LLMS_SECTIONS]]
        ordered += [label for label in sections if label not in ordered]
        ordered = [label for label in ordered if sections.get(label)]

        inline: list[tuple[str, list[str]]] = []
        linked: list[tuple[str, str, int]] = []  # (label, section path, page count)

        for label in ordered:
            entries = sections[label]
            lines = [line for _, line in entries]
            size = sum(len(line) + 1 for line in lines)
            prefix = self._common_directory([slug for slug, _ in entries])
            # Small sections ride along in the root file. That keeps real .md
            # links in the canonical index for link sampling, and saves agents
            # a fetch for a handful of pages. A section with no shared
            # directory has nowhere to live but the root.
            if not prefix or size <= self._LLMS_INLINE_MAX:
                inline.append(
                    (label, [described_lines.get(line, line) for line in lines])
                )
            else:
                for section_prefix, chunk in self._chunk_section(prefix, entries):
                    if not chunk:
                        continue
                    path = f"{section_prefix}/llms.txt"
                    self._write_section_index(
                        path, title, label, [line for _, line in chunk]
                    )
                    linked.append((section_prefix, path, len(chunk)))

        out = [f"# {title}", ""]
        if description:
            out += [f"> {description}", ""]
        if linked:
            out += [
                "Each section index below lists the markdown version of every "
                "page in that section.",
                "",
                "## Section indexes",
                "",
            ]
            for section_prefix, path, count in sorted(linked):
                out.append(
                    f"- [/{section_prefix}]({self._SITE_URL}/{path}): {count} pages"
                )
            out.append("")
        for label, lines in inline:
            out += [f"## {label}", "", *lines, ""]

        content = "\n".join(out)
        (self.build_dir / "llms.txt").write_text(content, encoding="utf-8")
        logger.info(
            "✅ llms.txt written: %d pages, %d characters in root, %d section indexes",
            page_count,
            len(content),
            len(linked),
        )
        self._validate_llms_indexes(page_count)

    def _copy_shared_files(self) -> None:
        """Copy files that should be shared between versions."""
        # Collect shared files
        shared_files = [
            file_path
            for file_path in self._safe_source_files(self.src_dir)
            if self.is_shared_file(file_path)
        ]

        if not shared_files:
            logger.info("No shared files found")
            return

        copied_count = 0
        for file_path in shared_files:
            relative_path = file_path.absolute().relative_to(self.src_dir.absolute())
            output_path = self.build_dir / relative_path

            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if file_path.suffix.lower() in self.copy_extensions:
                # Handle markdown files with preprocessing for /oss/ link resolution
                if file_path.suffix.lower() in {".md", ".mdx"}:
                    # For snippet files, we need to handle URL rewriting differently
                    # Use a special marker-based approach for dynamic URL resolution
                    if "snippets" in relative_path.parts:
                        logger.debug(
                            "Processing snippet file with URL rewriting: %s",
                            relative_path,
                        )
                        self._process_snippet_markdown_file(file_path, output_path)
                    else:
                        # Regular markdown processing without language-specific rewrite
                        self._process_markdown_file(file_path, output_path, None)
                    copied_count += 1
                else:
                    shutil.copy2(file_path, output_path)
                    copied_count += 1

        logger.info("✅ Shared files copied: %d files", copied_count)

    # Maps npm dist filenames to their output names in build/snippets/
    _NPM_SNIPPET_FILES: ClassVar[dict[str, str]] = {
        "PatternEmbed.jsx": "pattern-embed.jsx",
        "ExampleEmbed.jsx": "example-embed.jsx",
    }

    # Maps npm dist filenames to their output names in build/ (served at site root).
    _NPM_BUILD_FILES: ClassVar[dict[str, str]] = {
        "ChatLangChainEmbed.js": "ChatLangChainEmbed.js",
    }

    def _copy_npm_snippets(self) -> None:
        """Copy snippet components from the @langchain/docs-sandbox npm package.

        Overwrites any source-tree versions already copied by _copy_shared_files
        so the build always uses the latest published component.
        """
        pkg_dist = (
            self.src_dir.parent
            / "node_modules"
            / "@langchain"
            / "docs-sandbox"
            / "dist"
        )
        if not pkg_dist.is_dir():
            logger.warning(
                "@langchain/docs-sandbox not installed — run `npm install` first"
            )
            return

        snippets_dir = self.build_dir / "snippets"
        snippets_dir.mkdir(parents=True, exist_ok=True)

        for src_name, dest_name in self._NPM_SNIPPET_FILES.items():
            src_file = pkg_dist / src_name
            if not src_file.is_file():
                logger.warning("Expected file not found in npm package: %s", src_file)
                continue
            dest_file = snippets_dir / dest_name
            shutil.copy2(src_file, dest_file)
            logger.debug("Copied npm snippet: %s → snippets/%s", src_name, dest_name)

        for src_name, dest_name in self._NPM_BUILD_FILES.items():
            src_file = pkg_dist / src_name
            if not src_file.is_file():
                logger.warning("Expected file not found in npm package: %s", src_file)
                continue
            dest_file = self.build_dir / dest_name
            shutil.copy2(src_file, dest_file)
            logger.info("Copied npm build file: %s → build/%s", src_name, dest_name)

    def _process_snippet_markdown_file(
        self, input_path: Path, output_path: Path
    ) -> None:
        """Process a snippet markdown file with language-aware URL resolution.

        Shared MDX snippets can be imported from pages at arbitrary nesting
        depth (e.g. ``oss/langchain/frontend/branching-chat``). Converting
        ``/oss/...`` links to a fixed ``../`` relative path only works for
        pages one level under ``/oss/{lang}/`` and breaks nested consumers.

        Instead, emit absolute language-prefixed copies under
        ``build/snippets/{python|javascript}/...``, and keep a Python-prefixed
        default at the original snippet path for unversioned importers.
        Versioned pages are pointed at the language-specific copies by
        ``_rewrite_snippet_imports_for_language``.

        Args:
            input_path: Path to the source snippet markdown file.
            output_path: Path where the default processed file should be written.
        """
        try:
            with input_path.open("r", encoding="utf-8") as f:
                content = f.read()

            if input_path.suffix.lower() == ".md":
                output_path = output_path.with_suffix(".mdx")

            snippets_root = self.build_dir / "snippets"
            relative_snippet = output_path.absolute().relative_to(
                snippets_root.absolute()
            )

            for lang_key, lang_name in self.language_url_names.items():
                lang_content = preprocess_markdown(
                    content, input_path, target_language=lang_key
                )
                lang_content = self._rewrite_oss_links(lang_content, lang_key)
                lang_content = self._rewrite_managed_deep_agents_links(
                    lang_content, lang_key
                )
                lang_output = snippets_root / lang_name / relative_snippet
                lang_output.parent.mkdir(parents=True, exist_ok=True)
                with lang_output.open("w", encoding="utf-8") as f:
                    f.write(lang_content)

            # Default path: Python-prefixed absolute links for unversioned pages.
            default_content = preprocess_markdown(
                content, input_path, target_language="python"
            )
            default_content = self._rewrite_oss_links(default_content, "python")
            default_content = self._rewrite_managed_deep_agents_links(
                default_content, "python"
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as f:
                f.write(default_content)

        except (OSError, UnicodeDecodeError):
            logger.exception(
                "File I/O or decoding error in snippet markdown file %s", input_path
            )
            raise
        except re.error:
            logger.exception("Regex error in snippet markdown file %s", input_path)
            raise
