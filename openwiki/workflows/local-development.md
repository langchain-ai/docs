---
type: workflow guide
title: Local Development Workflow
description: Step-by-step guide to clone, set up, and work on the documentation repository locally, including development server setup, file watching, and build processes.
tags: [setup, development, environment, build-system, workflow]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-b481a230af378c0c50ed9994
    resource: repo://pipeline/commands/dev.py
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-636af982f42ea94123d2d7e9
    resource: repo://pipeline/core/watcher.py
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# Local Development Workflow

This page walks through setting up your local development environment for the LangChain documentation repository, starting the development server, and understanding how changes are detected, rebuilt, and served in the browser.

## Prerequisites and Dependencies

The repository requires Python 3.13+, Node.js, and the uv package manager.

**Check your environment:**

```bash
python --version    # Should be 3.13 or higher
node --version      # Required for npm packages
uv --version        # Python package manager
```

If you need Node.js or uv, install from:
- [Node.js](https://nodejs.org/)
- [uv documentation](https://docs.astral.sh/uv/getting-started/installation/)

## Clone and Initial Setup

Clone the documentation repository and install all dependencies:

```bash
git clone https://github.com/langchain-ai/docs.git && cd docs
```

Install Python and Node.js dependencies in one step:

```bash
make install
```

This command:
- Runs `uv sync --all-groups` to install Python dependencies (including build tools, testing frameworks, and linters)
- Runs `npm install` to install JavaScript/Node packages (including Mintlify CLI)
- Installs Mintlify CLI globally with `npm install -g mint@latest`

After installation, you may need to restart your shell for the `docs` command-line tool to be available in your PATH.

## Starting Development Mode

Begin active development with the one-command workflow:

```bash
make dev
```

Or use the Python CLI directly:

```bash
uv run pipeline dev
```

## What Happens When Development Mode Starts

The `dev` command orchestrates an integrated workflow:

1. **Initial build** (unless skipped): Processes all source files from `/src` through preprocessing, generates the version-specific output in `/build`, and prepares Mintlify configuration. This step validates the entire documentation structure before watching begins.

2. **File watcher starts**: A background file monitor watches `/src` recursively for changes to markdown, images, and configuration files. Supported file types include `.mdx`, `.md`, `.json`, `.svg`, `.png`, `.jpg`, `.css`, `.js`, and others.

3. **Mint dev server launches**: Mintlify's development server starts at `http://localhost:3000` with hot reload enabled. When build artifacts in `/build` change, the browser automatically refreshes to display the updated content.

4. **File changes are detected and rebuilt**: When you save a file in `/src`, the watcher detects the change, batches it with other rapid changes (0.2-second debounce window), and rebuilds only the affected files into `/build`. This rebuilding process:
   - Applies preprocessing (language splitting, link rewriting, etc.)
   - Updates navigation and cross-references if applicable
   - Maintains directory structure parity between `/src` and `/build`
   - Touches the rebuilt files to signal Mintlify that content has changed

5. **Browser hot-reloads**: Mintlify detects the touched files and refreshes the browser to show your changes within seconds.

### Development Mode Options

**Skip the initial build if you already have a `/build` directory:**

```bash
uv run pipeline dev --skip-build
```

This is useful when resuming development after an interruption. If `/build` does not exist, you'll see a warning; in that case, run `make dev` without the flag to perform a full build first.

## Making and Viewing Changes

### Edit markdown files

Edit `.mdx` or `.md` files in `/src`. The watcher detects changes immediately:

```bash
# Example: edit a file
vim src/oss/openwiki/overview.mdx
# Save the file → watcher rebuilds → browser auto-reloads at localhost:3000
```

Supported file extensions automatically trigger rebuilds: `.mdx`, `.md`, `.json`, `.svg`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.mp4`, `.webm`, `.yml`, `.yaml`, `.css`, `.js`, `.jsx`, `.tsx`, and fonts.

### Check your changes

Open `http://localhost:3000` in your browser. Navigate to the page you edited. Changes appear within 2–3 seconds of saving.

### Understand what gets rebuilt

The builder preprocesses files during the build:

- **Language splitting**: Files with `:::python` and `:::js` code fences are split into separate Python and JavaScript versions during build
- **Link rewriting**: Cross-references are rewritten to match the language version (e.g., links to `/oss/python/...` in the Python build)
- **Navigation updates**: `docs.json` navigation is applied to the site structure
- **Snippet preprocessing**: Reusable markdown snippets are imported and processed

All preprocessing happens during the build phase; source files in `/src` remain unchanged.

## Code Quality and Formatting

Before committing, verify code quality:

```bash
# Check formatting and style
make lint

# Auto-format Python code
make format

# Format-check without changes (for CI)
make format-check

# Lint markdown/MDX files
make lint_md

# Auto-fix markdown issues
make lint_md_fix

# Lint prose with Vale style guide
make lint_prose
```

The `make lint` command runs:
- `ruff format` and `ruff check` for Python code style
- Type checking with `ty`
- Spell checking with `codespell` on documentation in `/src`

### Prose linting with Vale

Install Vale on your system to lint writing style:

```bash
# macOS
brew install vale

# Other platforms: see https://vale.sh/docs/vale-cli/installation/
```

Then use VS Code or Cursor with the Vale extension for inline feedback:

1. Install the [Vale extension](https://marketplace.visualstudio.com/items?itemName=chrischinchilla.vale-vscode)
2. Configure the extension to use `.vale.ini` in the repository root
3. Set the Vale min alert level to `suggestion`

The project uses a specific Vale version pinned in `.mise.toml`; `make lint_prose` automatically installs and uses that version.

## Verifying Links and Building for Production

### Check for broken links

Before pushing changes, validate internal links:

```bash
make broken-links
```

This builds the documentation first, then checks for broken links in the generated site. It excludes OpenAPI-generated pages and code samples.

For a more thorough check including link anchors:

```bash
make broken-links-with-anchors
```

### Build for production

Generate the final production build in `/build` (used for deployment):

```bash
make build
```

This performs a full build without watching for changes. The resulting `/build` directory is what Mintlify deploys to `docs.langchain.com`.

**Important:** Never edit `/build` directly. All changes must be made in `/src`; the `/build` directory is regenerated from source every build.

## Testing and Validation

Run the test suite to catch regressions:

```bash
# Run all tests
make test

# Run specific test file
make test TEST_FILE=tests/unit_tests/test_builder.py
```

Tests are executed with `pytest --disable-socket` to prevent accidental network calls. Networking is allowed only for Unix sockets.

## Troubleshooting Development Issues

### `make dev` or `docs dev` not working

Ensure your environment is set up correctly:

1. Re-run installation: `make install`
2. Activate your virtual environment if using one
3. Verify all dependencies installed successfully
4. Check that Mintlify CLI is installed: `mint --version`

### Mintlify version errors

If you encounter parsing or compatibility errors, update Mintlify to the latest version:

```bash
mint update
# or
npm install -g mint@latest
```

Most `docs dev` issues are resolved by updating Mintlify.

### Mintlify `.venv` parsing error when running `mint broken-links`

**Problem:** Running `mint` commands from the project root causes parsing errors like:

```
Unable to parse .venv/lib/python3.13/site-packages/soupsieve-2.7.dist-info/licenses/LICENSE.md
```

**Root cause:** Mintlify tries to parse all files in the directory, including Python virtual environment files with invalid MDX syntax.

**Solutions (in order of preference):**

1. **Use safe Make commands** (recommended):
   ```bash
   make broken-links-with-anchors
   ```

2. **Run Mintlify from the build directory:**
   ```bash
   cd build
   mint broken-links
   ```

This ensures Mintlify only scans the final documentation, not the Python environment.

### "page doesn't exist" warning

If Mintlify warns that a page doesn't exist, ensure the page's index is correctly referenced in `src/docs.json`:

```json
{
  "group": "My Group",
  "pages": ["my-group/index", "my-group/other-page"]
}
```

Note the trailing `/index` with no file extension; omitting it causes Mintlify to raise a warning.

## Repository Structure

```
/src/                          # Source documentation (edit here)
├── oss/
│   ├── langchain/             # LangChain docs (versioned by language)
│   ├── langgraph/             # LangGraph docs (versioned by language)
│   ├── deepagents/            # Deep Agents docs (versioned by language)
│   │   └── code/              # Unversioned code docs
│   ├── openwiki/              # OpenWiki unversioned docs
│   ├── python/                # Python-only content
│   ├── javascript/            # JavaScript-only content
│   └── concepts/              # Shared conceptual overviews
├── langsmith/                 # LangSmith product docs
├── images/                    # Shared images
└── docs.json                  # Mintlify site configuration and navigation

/build/                        # Generated docs (DO NOT EDIT)
/Makefile                      # Make targets
/pipeline/                     # Build pipeline source code
├── commands/
│   ├── dev.py                 # Development mode orchestration
│   └── build.py               # Build command
├── core/
│   ├── builder.py             # File processing and build logic
│   └── watcher.py             # File system monitoring
└── preprocessors/             # Document preprocessing
```

## Next Steps

- **Add a page:** See [Adding and Modifying Documentation Pages](/openwiki/operations/adding-pages.md) for guidance on creating new documentation
- **Use CLI tools:** See [CLI Tools Reference](/openwiki/operations/cli-tools.md) for advanced build and migration commands
- **Understand the build:** Read `pipeline/core/builder.py` and `pipeline/commands/dev.py` to understand how files are processed and served
