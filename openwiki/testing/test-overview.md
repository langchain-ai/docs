---
type: guide
title: Testing Overview
description: Understand the test suite structure, categories, and how to run tests locally and in CI pipelines for the documentation pipeline.
tags: [testing, pytest, CI, quality-assurance]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-635a4d4537a9628cdea912c0
    resource: repo://.vale.ini
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
  - id: openwiki-source-c2764a7369c8fbf3e49da6f8
    resource: repo://tests/unit_tests/test_check_cross_refs.py
  - id: openwiki-source-2ecfcd33b729fccd843ab705
    resource: repo://tests/unit_tests/test_handle_auto_links.py
  - id: openwiki-source-1e48075742e124afeca28fef
    resource: repo://tests/unit_tests/test_parser.py
  - id: openwiki-source-16b92823fdcb07d686f2e27f
    resource: repo://tests/unit_tests/test_watcher.py
  - id: openwiki-source-0d0e77eb273a56717af74faa
    resource: repo://tests/unit_tests/utils.py
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

## Overview

The documentation pipeline includes a comprehensive test suite organized by functionality area. Tests validate the build process, markdown parsing, link handling, and file system watching. All tests must pass before merging to main via GitHub Actions.

## Test Suite Structure

Tests are located in `/tests/unit_tests/` and use **pytest** as the testing framework. The test suite is organized by major functional areas:

### Test Categories

#### Builder Tests (`test_builder.py`)
Tests the `DocumentationBuilder` class, which is responsible for copying and processing source documentation files to the build directory. Key responsibilities tested:

- File extension support and filtering
- Directory structure preservation during copy operations
- Versioned builds (Python and JavaScript language variants)
- File preprocessing and markdown handling
- File metadata preservation

Key test modules cover:
- Builder initialization and configuration
- Building from empty directories
- Handling of markdown, media, and configuration files
- Support for TSX/JSX snippet components
- Extension filtering (supported vs. unsupported file types)

#### Parser Tests (`test_parser.py`)
Tests the markdown parser (`pipeline.tools.parser.Parser`) that parses markdown syntax into an abstract syntax tree (AST) and converts to output formats. Coverage includes:

- Heading and paragraph parsing
- Front matter extraction and handling
- Code block detection and preservation
- Admonition/accordion elements (Python `???` syntax to Mintlify format)
- Tab/conditional blocks (Tabs component)
- Line number tracking for source mapping

#### Autolinks Tests (`test_handle_auto_links.py`)
Tests the autolink preprocessor that transforms `@[Reference]` syntax into markdown links while respecting code blocks. Key behaviors:

- Autolink replacement outside code blocks
- Code block protection (backticks, tildes, extended fences)
- Language-scoped link resolution (Python vs. JavaScript)
- Conditional fence handling (:::python, :::js)
- Escaped autolink preservation
- Empty line handling and output fidelity

#### File Watcher Tests (`test_watcher.py`)
Tests the `DocsFileHandler` class which monitors the source directory for file changes during development mode. Validates:

- Backup file filtering (files ending with `~`)
- Temporary file exclusion (`.bak`, `.orig`, `.swp`, `.tmp`)
- Valid file recognition (documentation, media, configuration)
- Edge cases (tildes in filenames, hidden files, multiple extensions)

#### Cross-Reference Tests (`test_check_cross_refs.py`)
Tests the cross-reference validation system that ensures `@[ref]` syntax resolves to known identifiers. Validates:

- Scope-based resolution (Python, JavaScript, shared)
- Code block and escaped reference protection
- Titled ref format (`@[title][ref]`)
- Language-specific and language-shared file scope detection

#### Additional Test Files

- **`test_lexer.py`**: Markdown token recognition and fence detection
- **`test_check_pr_imports.py`**: Import validation for pull request changes
- **`test_check_removed_pages_redirects.py`**: Redirect configuration for removed pages
- **`test_utm_links.py`**: UTM parameter handling in links
- **`test_filter_mint_broken_links.py`**: Broken link filtering for output validation
- **`test_refresh_integration_downloads.py`**: Integration package download counts

## Running Tests

### Local Execution

Run all tests:
```bash
make test
```

Run tests with verbose output:
```bash
uv run pytest tests/ -vv
```

Run specific test file:
```bash
uv run pytest tests/unit_tests/test_builder.py -vv
```

Run specific test:
```bash
uv run pytest tests/unit_tests/test_builder.py::test_builder_initialization -vv
```

### pytest Configuration

The test suite uses `pytest` with socket isolation enabled via `--disable-socket` flag (set in Makefile). This prevents accidental network calls during tests.

Key pytest configuration (from `pyproject.toml`):
- **Python files**: `test_*.py` naming convention
- **Test functions**: `test_*` naming convention
- **Asyncio mode**: `auto` (automatic fixture scope detection)
- **Default output**: Verbose (`-v`), with test outcome reports (`-ra`) and slowest tests display (`--durations=5`)

### Test Dependencies

Install test dependencies:
```bash
uv sync --group test
```

Test group includes:
- `pytest>=9.0.3`
- `pytest-asyncio>=0.25.3`
- `pytest-mock>=3.14.0`
- `pytest-socket>=0.7.0` (prevents network calls)
- `pytest-timeout>=2.3.1`

## CI/CD Integration

### GitHub Actions Workflow

Tests run on every pull request and push to main via the CI workflow (`.github/workflows/ci.yml`). The test job:

1. **Triggers**: Pull requests, pushes to main, manual workflow dispatch
2. **Python version**: 3.13 (minimum and maximum supported versions tested)
3. **Timeout**: 20 minutes
4. **Concurrency**: Cancels previous runs for the same PR/branch to avoid redundant testing

### CI Test Job

The `test` job in `ci.yml` calls the reusable workflow `.github/workflows/_test.yml`, which:
1. Sets up Python 3.13 and uv package manager
2. Installs test dependencies
3. Runs `make test` (executes `uv run pytest --disable-socket --allow-unix-socket tests/ -vv`)

### Failure Conditions

Tests must pass before merging. CI fails if:
- Any test assertion fails
- Socket/network calls are attempted (caught by `--disable-socket`)
- Test timeout (20 minutes) is exceeded

## Linting and Validation

Beyond unit tests, CI runs several validation checks:

### Code Linting

```bash
make lint
```

Runs:
- **ruff format**: Code formatting check
- **ruff check**: Linting rules enforcement
- **mypy**: Type checking
- **codespell**: Spelling validation

**CI check**:
```bash
make format-check
```

### Prose Linting

```bash
make lint_prose
```

Validates markdown prose against Vale style rules defined in `.vale.ini` and `AGENTS.md`. Enforces:
- LangChain style guide (terminology, tone, accessibility)
- proselint, vale, and write-good rules
- Excludes code blocks and code-samples directory

### Link Validation

```bash
make broken-links          # Basic link validation
make broken-links-with-anchors  # Including anchor fragments
```

Validates links in built documentation using Mintlify's lint tool. CI excludes:
- OpenAPI-generated pages
- Snippet files (processed separately)
- Known false positives (filtered by `scripts/filter_mint_broken_links.py`)

### Code Sample Testing

```bash
make test-code-samples
```

Validates code snippets in `src/code-samples` directory. CI runs this on multiple versions in parallel via `test-code-samples.yml`.

### Cross-Reference Validation

```bash
make check-cross-refs
```

Ensures all `@[ref]` references in source markdown resolve to known identifiers. CI runs this as a separate job.

## Test Utilities

### FileSystem Context Manager

Located in `tests/unit_tests/utils.py`, provides a temporary file system for testing:

```python
from tests.unit_tests.utils import file_system, File

with file_system([
    File(path="index.mdx", content="# Hello"),
    File(path="image.png", bytes=b"PNG_DATA")
]) as fs:
    builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
    builder.build_all()
    assert fs.build_file_exists("index.mdx")
```

The context manager creates:
- Temporary directory with `src/` and `build/` subdirectories
- Auto-cleanup on exit
- Methods for listing files and checking existence

## Test Coverage

The test suite validates critical paths:

- **Build process**: File copying, extension filtering, versioning
- **Markdown parsing**: Syntax recognition, AST construction, format conversion
- **Link processing**: Autolink replacement, code block protection, cross-references
- **File system handling**: Watcher filtering, temporary file exclusion
- **Integration**: End-to-end markdown to output conversion

No network calls are permitted during testing (enforced by `--disable-socket` flag).

## Related Documentation

- [Builder Tests](/openwiki/testing/builder-tests.md): Detailed builder test reference
- [Local Development](/openwiki/workflows/local-development.md): Development setup and workflow

## Key Invariants

1. **All tests must pass before merge**: CI enforces this requirement on pull requests
2. **Socket isolation**: Tests cannot make network calls (pytest-socket enforcement)
3. **Versioned builds**: Documentation is built in separate Python and JavaScript variants
4. **Code block protection**: Preprocessors must preserve content inside fenced code blocks
5. **Cross-reference validation**: All `@[ref]` syntax must resolve to known identifiers
