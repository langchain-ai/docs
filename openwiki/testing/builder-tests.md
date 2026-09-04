---
type: Test Suite Architecture
title: Builder Tests and File Handling
description: Comprehensive test suite for DocumentationBuilder covering file categorization, versioning, preprocessing, and multi-language link rewriting.
tags: [file-handling, versioning, preprocessing, markdown, link-rewriting, test-utilities]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
  - id: openwiki-source-0d0e77eb273a56717af74faa
    resource: repo://tests/unit_tests/utils.py
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

## Overview

The DocumentationBuilder test suite (`tests/unit_tests/test_builder.py`) validates the core documentation pipeline's responsibility: copying files from source to build directories while categorizing them by language, version, and shared status. This page documents the key test patterns, file handling mechanisms, and special cases that make the builder the orchestrator of multi-language, multi-product documentation.

## Core Responsibilities

The DocumentationBuilder class orchestrates several distinct responsibilities:

1. **File copying and categorization**: Determines whether each file is versioned (built for both Python and JavaScript), unversioned (built once), shared (images, snippets), or product-specific.
2. **Conditional rendering**: Processes `:::python` and `:::js` fence blocks, preserving target-language content and stripping others.
3. **Link rewriting**: Rewrites `/oss/` links to include language segments (`/oss/python/` or `/oss/javascript/`), with exceptions for unversioned products and image paths.
4. **Snippet rewriting**: Points MDX imports of snippets to language-specific copies (`/snippets/python/...` or `/snippets/javascript/...`).
5. **Markdown preprocessing and metadata injection**: Adds edit links (except home and snippets), converts `.md` to `.mdx`, and handles YAML-to-JSON conversion.

## File Extension Handling

The builder's `copy_extensions` set defines which file types are supported:

```python
{".mdx", ".md", ".json", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".mp4", ".webm", 
 ".yml", ".yaml", ".css", ".js", ".jsx", ".tsx", ".txt", ".woff2", ".woff", ".ttf", ".html"}
```

Test `test_builder_initialization` verifies this set contains all expected extensions. Files not in this set are silently skipped during build operations.

### Markdown (.md, .mdx) Special Handling

- `.md` files are converted to `.mdx` during output (`_process_markdown_file`).
- Markdown content undergoes preprocessing: cross-reference resolution, conditional block filtering, and link rewriting.
- An "Edit Source" link is appended to pages (except the root `index.mdx` and files in `/snippets/`).

### YAML-to-JSON Conversion

Files named `docs.yml` are automatically converted to `docs.json` during the build. This is handled by `_convert_yaml_to_json`, which parses the YAML using `yaml.safe_load` and emits JSON.

## Test Fixtures and Utilities

### FileSystem Context Manager

The `file_system(files: list[File])` context manager from `tests/unit_tests/utils.py` creates isolated test environments:

- Creates a temporary directory with `src/` and `build/` subdirectories.
- Populates `src/` with test files from a list of `File` TypedDicts.
- Cleans up automatically on exit.
- Provides methods: `list_build_files()`, `build_file_exists(path)`.

```python
with file_system([
    File(path="oss/index.mdx", content="# Welcome"),
    File(path="images/logo.png", bytes=b"PNG_DATA")
]) as fs:
    builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
    builder.build_all()
    assert fs.build_file_exists("oss/python/index.mdx")
```

### File Type

Files are specified as `TypedDict` with `path` (relative path), and either `content` (UTF-8 string) or `bytes` (binary data).

## Initialization Tests

`test_builder_initialization` verifies:
- `src_dir` and `build_dir` are set correctly.
- `copy_extensions` includes all expected file extensions.
- `snippet_component_extensions` contains `.jsx` and `.tsx`.
- `language_url_names` maps `"python"` → `"python"` and `"js"` → `"javascript"`.

## Versioned File Building Tests

### Basic Versioning (OSS Files)

Files under `oss/` are built for both Python and JavaScript versions:

- Source: `oss/index.mdx` → Output: `oss/python/index.mdx` and `oss/javascript/index.mdx`.
- Each version receives preprocessing with its target language.

`test_build_all_supported_files` confirms:
- LangGraph OSS files create `/oss/python/` and `/oss/javascript/` outputs.
- LangGraph Platform files (unversioned product) go to `/langgraph-platform/` (no language split).
- LangChain Labs files (unversioned product) go to `/labs/` (no language split).
- Shared files (images, JSON) are not duplicated per language.

### Unversioned OSS Products

Two OSS products are built once (no python/javascript duplication):

1. **Deep Agents Code** (`oss/deepagents/code/`): Shipped at `/oss/deepagents/code/`.
   - Test: `test_unversioned_oss_code_builds_once`
   - Detection: `is_unversioned_oss_file()` returns `True` for paths where `parts[0] == "oss"`, `parts[1] == "deepagents"`, `parts[2] == "code"`.

2. **OpenWiki** (`oss/openwiki/`): Shipped at `/oss/openwiki/`.
   - Test: `test_unversioned_oss_openwiki_builds_once`
   - Detection: `is_unversioned_oss_file()` returns `True` for paths where `parts[0] == "oss"` and `parts[1] == "openwiki"`.

Both use `"python"` as the target language for conditional block processing, but links within them are not prefixed with `/python/` or `/javascript/`.

### LangSmith (Unversioned)

LangSmith pages under `langsmith/` are built once at `langsmith/` with `target_language="python"`.

**Special Case: Managed Deep Agents**

Pages matching `langsmith/managed-deep-agents*.mdx` emit language-specific routes only:
- Output: `langsmith/python/managed-deep-agents-*.mdx` and `langsmith/javascript/managed-deep-agents-*.mdx`
- No unversioned `langsmith/managed-deep-agents-*.mdx` is created (would be orphaned).
- Test: `test_build_all_creates_managed_deep_agents_language_routes`

## Link Rewriting Tests

### OSS Link Rewriting

`_rewrite_oss_links(content: str, target_language: str | None)` transforms `/oss/` links:

- **Versioned targets**: `/oss/langgraph/` → `/oss/python/langgraph/` (for `target_language="python"`).
- **Test**: `test_rewrite_oss_links_inserts_language`

### Preservation of Already-Prefixed Links

Links that already specify a language are left unchanged:

- Input: `/oss/python/langchain/overview` with `target_language="python"` → Output: `/oss/python/langchain/overview` (no double-prefix).
- **Test**: `test_rewrite_oss_links_preserves_existing_language`
- **Rationale**: Unversioned pages (e.g., LangSmith) may contain cross-links to both Python and JavaScript versions.

### Unversioned Product Exceptions

Deep Agents Code and OpenWiki links skip language insertion:

- `/oss/deepagents/code/` → `/oss/deepagents/code/` (unchanged).
- `/oss/openwiki/` → `/oss/openwiki/` (unchanged).
- **Test**: `test_rewrite_oss_links_preserves_deepagents_code` and `test_rewrite_oss_links_preserves_openwiki` (implicit in unversioned tests).

### Image Path and None-Target Skipping

Image paths (`/oss/images/...`) and `None` target language are not rewritten:

- Input: `<img src="/oss/images/diagram.png" />` → Output: unchanged.
- **Test**: `test_rewrite_oss_links_skips_images_and_none`

### Managed Deep Agents Link Rewriting

`_rewrite_managed_deep_agents_links(content: str, target_language: str | None)` adds language to `/langsmith/managed-deep-agents` links:

- `/langsmith/managed-deep-agents-quickstart` with `target_language="python"` → `/langsmith/python/managed-deep-agents-quickstart`.
- Already-prefixed links are left alone.
- **Test**: `test_rewrite_managed_deep_agents_links_inserts_language`

## Snippet Handling Tests

### Snippet Import Rewriting

`_rewrite_snippet_imports_for_language(content: str, target_language: str)` points MDX imports to language-specific snippet copies:

- `from '/snippets/shared-block.mdx'` with `target_language="python"` → `from '/snippets/python/shared-block.mdx'`.
- Already-prefixed imports are left unchanged.
- **Test**: `test_rewrite_snippet_imports_for_language`

### Snippet Copy Mechanism

Shared snippets (under `/snippets/`) are emitted in three forms:

1. **Default path** (`/snippets/example.mdx`): Uses Python-prefixed absolute `/oss/python/` links for unversioned importers.
2. **Python copy** (`/snippets/python/example.mdx`): Uses `/oss/python/` links.
3. **JavaScript copy** (`/snippets/javascript/example.mdx`): Uses `/oss/javascript/` links.

The default copy allows unversioned pages (e.g., LangSmith) to import shared snippets without specifying a language; they get Python-prefixed links.

### Nested Consumer Test Case

`test_snippet_oss_links_are_language_prefixed_not_relative` prevents a critical regression: nested consumers (e.g., `oss/langchain/frontend/branching-chat`) must not resolve relative `../` paths to incorrect absolute paths.

- Shared snippet: `snippets/oss/requires-langgraph-server.mdx` imports a note linking to `/oss/langgraph/local-server`.
- Nested page imports the snippet: `oss/langchain/frontend/branching-chat.mdx`.
- Expected: Both use absolute `/oss/{lang}/langgraph/local-server` links (not relative paths).
- **Test**: Verifies default, Python, and JavaScript copies all receive correct absolute language-prefixed links.

## Shared File Handling Tests

### Shared File Definition

`is_shared_file(file_path: Path)` determines if a file is shared (not duplicated per language):

- **Always shared**: `docs.json`, root pages (`index.mdx`, `use-these-docs.mdx`, `playground.mdx`, `build-overview.mdx`), snippets, images, `.well-known`, fonts, `.js` and `.css` files.
- **Shared for OSS**: Shared files within `oss/` are copied once to the output root, not under `oss/python/` or `oss/javascript/`.

### TSX/JSX Snippets

Component files (`.jsx`, `.tsx`) in `/snippets/` are copied once to `build/snippets/example.tsx`.

- **Test**: `test_build_all_copies_tsx_snippets`

## Empty Directory and Unsupported File Tests

### Empty Directory

`test_build_all_empty_directory` verifies the builder completes without error when the source directory contains no files.

### Unsupported File Types

`test_build_all_unsupported_files` confirms that files with extensions not in `copy_extensions` are skipped:

- `.txt`, `.csv` are not copied.
- Only supported extensions (`.mdx`, `.md`, `.png`, etc.) appear in the output.

## Conditional Rendering Tests

The builder integrates with `preprocess_markdown()` to handle language-specific fence blocks:

```markdown
:::python
Python-only content.
:::

:::js
TypeScript-only content.
:::
```

When building with `target_language="python"`, the Python fence is kept and the JavaScript fence is removed. The `_process_markdown_content` method applies this preprocessing before link rewriting.

**Test coverage**: `test_build_all_creates_managed_deep_agents_language_routes` includes a snippet with conditional blocks and verifies each language version contains the correct content.

## Single and Multiple File Building Tests

### Single File Build

`test_build_single_file` and `test_build_nonexistent_file`:

- `build_file(path)` builds one file at the correct location.
- Building a nonexistent file raises `AssertionError`.

### Multiple File Build with Progress

`test_build_multiple_files`:

- `build_files(list[Path])` builds a list of files.
- Shows a progress bar when building multiple files (hidden in CI).
- Handles both single-file and multi-file cases.

## Safety Tests

### Symlink Rejection

`test_safe_source_files_skips_symlinks` verifies that `_safe_source_files()` rejects symlinks:

- Committed symlinks targeting files outside the source tree cannot leak host paths (e.g., `/proc/self/environ`).
- Symlinks are logged as warnings and excluded from the build.

## Index Generation Tests

### llms.txt Generation

`_generate_llms_txt()` produces a custom index that avoids Mintlify's 100,000-character truncation:

- **Test**: `test_build_all_writes_llms_txt`
- Indexes all pages with frontmatter metadata (title, description).
- Excludes pages marked `noindex: true` and snippet files.
- Section entries link to sub-indexes when a section grows too large.

### OpenAPI Entry Extraction

`_openapi_entries()` derives entries from OpenAPI specs in `docs.json`:

- Reads `docs.json` navigation configuration.
- Walks the config tree to find all `openapi` blocks.
- For each operation in the spec, generates a slug: `<directory>/<tag>/<summary>`.
- Handles duplicates with numeric suffixes (e.g., `get-info-1`).
- Skips hidden operations (`x-hidden: true`).

**Test**: `test_openapi_entries_skip_hidden_and_number_duplicates`

### Large Section Splitting

`test_llms_txt_splits_large_sections_into_section_indexes`:

- When a section exceeds `_LLMS_SECTION_BUDGET` (~40,000 characters), it is split into multiple indexed files.
- Each split lives at `<section>/llms.txt` so Mintlify can serve it and agents can resolve links.
- No nesting deeper than one level (coverage walkers only descend one hop).

### Full Text Corpus Generation

`_generate_llms_full_txt()` produces a complete-text index for agent ingestion:

- Splits language variants into separate files (`oss/python/llms-full.txt` and `oss/javascript/llms-full.txt`).
- Inlines snippet content (since Mintlify expands imports at render time).
- Test: `test_llms_full_txt_splits_languages_and_inlines_snippets`

## NPM Snippet Copying

`_copy_npm_snippets()` imports pre-built React components from the `@langchain/docs-sandbox` npm package:

- Overwrites source-tree versions (always uses latest published).
- Maps npm filenames to build paths:
  - `PatternEmbed.jsx` → `build/snippets/pattern-embed.jsx`
  - `ExampleEmbed.jsx` → `build/snippets/example-embed.jsx`
  - `ChatLangChainEmbed.js` → `build/ChatLangChainEmbed.js`

## Test Slug Functions

Two slug functions are tested:

### `_slugify(value: str)`

Converts text to URL-safe slugs (lowercase, hyphenate, strip):

- Drops apostrophes (matching Mintlify): `"Get the authenticated user's provider user ID"` → `"get-the-authenticated-users-provider-user-id"`.
- **Test**: `test_slugify_drops_apostrophes`

### `_tag_slug(value: str)`

Slugs OpenAPI tags, preserving underscores (unlike `_slugify`):

- `"annotation_queues"` → `"annotation_queues"` (underscore preserved).
- `"annotation-queues"` → `"annotation-queues"` (hyphen preserved).
- `"SCIM Tokens"` → `"scim-tokens"` (whitespace replaced, lowercase).
- **Test**: `test_tag_slug_preserves_underscores`

## Build Path Variants

The builder supports several build entry points:

- **`build_all()`**: Full pipeline (clears build dir, processes all files, copies shared files, generates indexes).
- **`build_file(path)`**: Single file with version-aware routing (OSS files build both versions, LangSmith builds once, etc.).
- **`build_files(list[Path])`**: Multiple files with progress bar.

## Integration with Preprocessing

The builder delegates markdown processing to `preprocess_markdown()` from `pipeline.preprocessors`:

- Applies cross-reference resolution (e.g., converting `@see{ClassName}` to links).
- Filters conditional blocks based on `target_language`.
- The builder then applies link rewriting and metadata injection afterward.

## Error Handling

The builder logs exceptions but does not halt:

- YAML parse errors in `_convert_yaml_to_json` are logged with the file path.
- File I/O errors in `_process_markdown_file` are logged but the build continues.
- Symlinks trigger warnings instead of errors.

## Key Test Coverage Checklist

✅ File extension filtering (supported vs. unsupported).
✅ Markdown to MDX conversion.
✅ YAML to JSON conversion.
✅ Versioned file splitting (OSS python/javascript).
✅ Unversioned product handling (Deep Agents Code, OpenWiki, LangGraph Platform).
✅ Link rewriting (bare `/oss/` → language-prefixed, already-prefixed preserved, exceptions for unversioned).
✅ Snippet rewriting (language-specific imports).
✅ Shared file detection (images, snippets, JSON, root pages).
✅ Conditional rendering (:::python and :::js blocks).
✅ Edit link injection (except home and snippets).
✅ Symlink rejection for security.
✅ llms.txt generation and splitting.
✅ OpenAPI entry extraction and slug normalization.
✅ NPM snippet copying.
✅ Single, multiple, and batch file building.
