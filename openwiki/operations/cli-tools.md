---
type: reference
title: CLI Tools Reference
description: Complete documentation of the `docs` Python CLI and supporting commands for building, developing, migrating, and maintaining documentation.
tags: [cli, build, development, migration]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-6e6efa1569f158fcdb678ef0
    resource: repo://pipeline/cli.py
  - id: openwiki-source-41f7c907e42a5efd3b3405cd
    resource: repo://pipeline/commands/build.py
  - id: openwiki-source-b481a230af378c0c50ed9994
    resource: repo://pipeline/commands/dev.py
  - id: openwiki-source-636af982f42ea94123d2d7e9
    resource: repo://pipeline/core/watcher.py
  - id: openwiki-source-0267a6f0fe0840056f8e4f6b
    resource: repo://pipeline/tools/docusaurus_parser.py
  - id: openwiki-source-8d071ef0669cd8d2d79c6c15
    resource: repo://pipeline/tools/links.py
  - id: openwiki-source-a210b0c642944a7ad93f3b40
    resource: repo://pipeline/tools/parser.py
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

## Overview

The LangChain documentation pipeline provides a Python CLI (`docs`) that wraps and automates the core documentation operations. These commands handle building documentation, starting development servers with file watching, migrating legacy formats to Mintlify, and refactoring documentation structure while maintaining cross-references.

The `docs` CLI is the entry point defined in `pyproject.toml` at `pipeline.cli:main`. Make targets in the `Makefile` wrap these commands for convenience.

## Quick Reference

| Command | Purpose | Key Options |
|---------|---------|------------|
| `docs dev` | Start development mode with file watching and hot reload | `--skip-build`, `--watch` |
| `docs build` | Build all documentation to `/build` | `--watch` |
| `docs migrate <path>` | Convert MkDocs markdown to Mintlify format | `--dry-run`, `--output` |
| `docs migrate-docusaurus <path>` | Convert Docusaurus markdown to Mintlify format | `--dry-run`, `--output` |
| `docs mv <old> <new>` | Move a file and update all cross-references | `--dry-run` |

## Command Invocation

### Via Make

```bash
make dev          # uv run pipeline dev
make build        # uv run pipeline build
```

### Via Python CLI

```bash
uv run pipeline dev
uv run pipeline build
uv run pipeline migrate <path>
```

After `make install`, the `docs` command may be available directly:

```bash
docs dev
docs build
docs migrate <path>
```

## Commands

### `docs dev` — Development Mode

Starts the development server with automatic file watching and live reload.

**Behavior:**
1. Performs an initial build of all documentation (unless `--skip-build` is set)
2. Starts a file watcher on the `src/` directory that automatically rebuilds changed files
3. Launches the Mintlify dev server at `http://localhost:3000` with hot reload
4. Forwards logs from the Mint dev server to the console
5. Continues watching for changes until interrupted (Ctrl+C)

**Options:**

- `--skip-build`: Skip the initial build step and use an existing `/build` directory. Useful for resuming development after an interruption. Warns if `/build` does not exist.
- `--watch` (legacy): Documented but effectively superseded by default behavior; file watching is implicit in `dev`.

**Flow:**
- Invokes `build_command()` unless skipped
- Creates a `FileWatcher` instance monitoring `src/` → `build/`
- Spawns a subprocess running `mint dev --port 3000` in the `/build` directory
- Uses `asyncio.wait()` with `FIRST_COMPLETED` to detect when either the watcher or Mint process exits abnormally
- On Ctrl+C: cleanly shuts down the watcher, terminates Mint (with a 5-second timeout before forced kill), and cancels all tasks

**Use:**
```bash
make dev
# or
uv run pipeline dev --skip-build
```

**Note:** `mint` is Mintlify's separate global npm binary. The `docs` CLI orchestrates it; it is not bundled with the Python package.

---

### `docs build` — Build Documentation

Builds all documentation from source to the `/build` directory for deployment or offline use.

**Behavior:**
1. Validates that the `src/` directory exists
2. Creates the `/build` directory if it does not exist
3. Initializes a `DocumentationBuilder` instance
4. Processes all source files through the build pipeline
5. Writes preprocessed `.mdx` files and assets to `/build`
6. Returns exit code 0 on success, 1 on failure

**Options:**

- `--watch` (legacy): Enables file watching after the initial build. Rarely used; `docs dev` is the preferred way to enable watching.

**Implementation:**
- Entry point: `pipeline.commands.build:build_command`
- Orchestrated by `DocumentationBuilder` (`pipeline.core.builder`)
- Runs once and exits (unless `--watch` is specified)
- Each run performs a **full rebuild** — no incremental caching

**Use:**
```bash
make build
# or
uv run pipeline build
```

**Output:**
- All preprocessed files written to `/build` (never edit this directory directly)
- Build artifacts include navigation configuration and assets

---

### `docs migrate <path>` — MkDocs to Mintlify Conversion

Converts MkDocs-formatted markdown files to Mintlify format. Supports single files, directories, and batch processing.

**Supported file types:**
- `.md`, `.markdown` (converted in place or to `--output` location)
- `.ipynb` (Jupyter notebooks; converted to `.md`)

**Options:**

- `--dry-run`: Print converted markdown to stdout without writing files. Useful for previewing changes.
- `--output <path>`: Write converted files to a directory or single file. If not provided, updates files in place.

**Behavior:**
1. Validates that the input path exists
2. Recursively finds all `.md`, `.markdown`, and `.ipynb` files in the directory (or uses a single file if provided)
3. For each file:
   - Reads the source content
   - Parses the markdown using `pipeline.tools.parser:to_mint()`
   - Removes `.md` / `.markdown` suffix from internal links
   - In dry-run mode: prints to stdout with file headers
   - Otherwise: writes to output location, creating directories as needed
4. Cleans up original `.ipynb` files if converted in place (since they become `.md` files)
5. Reports migration results (success/failure counts for batch operations)

**Processing:**
- MkDocs custom syntax (admonitions `!!!`, tabs `===`, etc.) is converted to Mintlify equivalents
- Admonitions map to Mintlify `<Note>`, `<Warning>`, `<Tip>`, `<Danger>`, `<Info>` callouts
- Tabs (`===`) convert to Mintlify `<Tabs>` and `<Tab>` components
- Blockquotes and lists are preserved
- Parse errors are logged with file context (no full stack traces)

**Use:**
```bash
# Preview changes without writing
uv run pipeline migrate docs/ --dry-run

# Convert in place
uv run pipeline migrate docs/

# Convert to a new directory
uv run pipeline migrate docs/ --output ../converted-docs/

# Convert a single file
uv run pipeline migrate docs/index.md --output docs/index.new.md
```

---

### `docs migrate-docusaurus <path>` — Docusaurus to Mintlify Conversion

Converts Docusaurus-formatted markdown to Mintlify format. Extends `migrate` to handle Docusaurus-specific syntax.

**Supported file types:**
- `.md`, `.markdown`, `.mdx` (MDX files are converted to `.md` unless `--output` specifies otherwise)
- `.ipynb` (Jupyter notebooks)

**Options:**

- `--dry-run`: Print converted markdown to stdout without writing files
- `--output <path>`: Write converted files to a directory or single file

**Behavior:**
1. Validates input path
2. Recursively finds all `.md`, `.markdown`, `.mdx`, and `.ipynb` files
3. For each file:
   - Extracts Docusaurus frontmatter (YAML)
   - Parses the body using `pipeline.tools.docusaurus_parser:convert_docusaurus_to_mintlify()`
   - Converts Docusaurus-specific MDX components and syntax
   - Generates Mintlify-compatible frontmatter
   - Removes `.md` suffixes from internal links
   - Writes or prints the result

**Processing:**
- **Admonitions:** Docusaurus admonitions (`::: note`, etc.) → Mintlify callouts
- **Tabs:** Docusaurus tabbed content → Mintlify `<Tabs>` / `<Tab>`
- **Imports:** Docusaurus `import` statements are processed or removed
- **Code blocks:** Language-specific syntax is normalized
- **Links:** Asset and documentation links are adjusted for Mintlify paths
- **Frontmatter:** Maps Docusaurus YAML (title, description, etc.) to Mintlify equivalents

**Use:**
```bash
# Preview conversion
uv run pipeline migrate-docusaurus docs/ --dry-run

# Convert in place
uv run pipeline migrate-docusaurus docs/

# Convert to output directory
uv run pipeline migrate-docusaurus docs/ --output ../mintlify-docs/
```

---

### `docs mv <old_path> <new_path>` — Move Files with Reference Updates

Moves a documentation file and automatically rewrites all cross-references pointing to it throughout the documentation tree.

**Options:**

- `--dry-run`: Preview the changes without moving files or rewriting links. Shows what would be updated.

**Behavior:**
1. Validates that the old path exists
2. Scans all `.md`, `.markdown`, `.mdx`, and `.ipynb` files in the documentation root
3. For each file containing a link to the old path:
   - Calculates the relative path from that file to the new location
   - Updates all instances of the old link to the new link
   - Adjusts internal links within the moved file itself to account for its new parent directory
4. In dry-run mode: reports proposed changes
5. Otherwise: moves the file and rewrites all references

**Use:**
```bash
# Preview changes
uv run pipeline mv old/path.md new/path.md --dry-run

# Move and update references
uv run pipeline mv docs/old-guide.md docs/tutorials/new-guide.md
```

**Mechanics:**
<!-- openwiki: broken internal link [url] file "url" does not exist. Fix the href or restore the target, then delete this comment. -->
- Uses regex-based link matching to identify Markdown link syntax `[label](url)` and anchors
- Preserves link anchors (fragments like `#section-id`)
- Skips external links, `mailto:` links, and absolute paths
- Updates links in both `.md` and `.ipynb` notebook files
- Reports all link changes made

---

## Build Pipeline Architecture

### File Watcher

The `FileWatcher` (in `pipeline.core.watcher`) continuously monitors the `src/` directory:

- **Trigger:** File modifications, additions, or deletions
- **Action:** Queues the changed file for rebuild
- **Debouncing:** Handles rapid successive changes gracefully
- **Ignores:** Temporary files (`.swp`, `.tmp`), backup files (`.bak`, `~`), and hidden temporary files

### Documentation Builder

The `DocumentationBuilder` (in `pipeline.core.builder`) orchestrates the build process:

1. **Traverses** the `src/` directory tree
2. **Preprocesses** `.md` and `.mdx` files (frontmatter parsing, syntax normalization, snippet extraction)
3. **Converts** `.ipynb` notebooks to markdown
4. **Copies** processed files and assets to `/build`
5. **Generates** navigation configuration (`docs.json` for Mintlify)

### Output Structure

```
build/
  ├── docs.json           # Mintlify site configuration
  ├── langsmith/          # Preprocessed LangSmith docs
  ├── oss/                # Preprocessed LangChain, LangGraph, integrations docs
  ├── snippets/           # Reusable MDX content (language-prefixed subdirectories)
  └── assets/             # Images and other static files
```

Never edit `/build` directly; it is regenerated on each build.

---

## Error Handling

### Parse Errors

When `docs migrate` or `docs migrate-docusaurus` encounters a parsing error (e.g., malformed markdown):
- The error is logged with file path and line number context
- No full stack trace is printed (only the message)
- The file is marked as failed but processing continues
- Final summary reports success and failure counts

**Example:**
```
ERROR - Parse error while processing file: 'docs/guide.md', at line 42, ...
```

### Build Failures

If `docs dev` detects a build failure:
- Logs the error and exits with code 1
- The Mint dev server is not started
- User is prompted to fix the issue and retry

### Missing Dependencies

If `mint` is not installed:
- `docs dev` exits with code 1 and suggests running `make install` or installing Mintlify directly

---

## Configuration

### Logging

All CLI commands emit structured logs to stderr:
- **Level:** INFO by default
- **Format:** `LEVELNAME - message`
- Commands log informational progress, warnings for skipped files, and errors with context

### Entry Point

The `docs` command is registered in `pyproject.toml`:
```toml
[project.scripts]
docs = "pipeline.cli:main"
```

This makes the command available after `pip install` or `uv sync`.

---

## Related Pages

- [Local Development Workflow](/openwiki/workflows/local-development.md) — Setup and development practices
- [Adding Pages](/openwiki/operations/adding-pages.md) — Documentation content authoring

---

## Troubleshooting

### `docs dev` not working / running

**Symptom:** `docs dev` fails or `mint` dev server doesn't start

**Solutions:**
- Run `make install` to ensure all dependencies are installed
- Check that `mint` is globally installed: `npm install -g mint@latest`
- Run `make clean` and then `make dev` to rebuild from scratch
- Check for port conflicts: Mint expects port 3000 to be available

### Build directory is stale

**Symptom:** Changes to source files aren't reflected in the build

**Solutions:**
- Run `make clean && make dev` to rebuild from scratch
- Use `docs dev --skip-build` only after a successful build has been completed

### Migration producing empty or incorrect output

**Symptom:** `docs migrate` produces truncated or malformed output

**Solutions:**
- Run `docs migrate <path> --dry-run` to preview the output first
- Check for unsupported markdown syntax that the parser may not recognize
- Verify the source file encoding is UTF-8
- Review parse error messages for hints about problematic sections

### Links still broken after `docs mv`

**Symptom:** Cross-references weren't updated correctly

**Solutions:**
- Run `docs mv --dry-run` to verify the proposed changes before executing
- Check that the old path is actually referenced in your docs (use grep)
- For complex cases, manually verify a few key files in the build output
