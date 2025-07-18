# Documentation Build Pipeline

This repository contains the documentation build pipeline for LangChain projects. 
It converts markdown and notebook files into a format suitable for [Mintlify](https://mintlify.com/docs) documentation sites.

## Directory Structure

```
src/                  # Source documentation files (edit these)
build/                # Generated output files (do not edit)
pipeline/             # Build pipeline source code
tests/                # Test files for the pipeline
Makefile              # Build automation
README.md             # This file
```

## Contributing

### Quick Start

1. **Clone and navigate to the docs directory:**
   ```bash
   git clone [repository-url]
   cd docs
   ```

2. **Install dependencies using Make (recommended):**
   ```bash
   make install
   ```
   This installs `uv` and sets up the Python virtual environment automatically.

3. **Start development mode:**
   ```bash
   make dev
   ```
   This watches for changes in `src/` and automatically rebuilds content in `build/`.

4. **Edit documentation files:**
   - All source files are in the `src/` directory
   - Edit `.md`, `.mdx`, or `.ipynb` files as needed
   - Changes are automatically rebuilt when using `make dev`

### Alternative: Manual Setup

If you prefer to manage the virtual environment manually:

1. **Install uv:**
   ```bash
   # Install uv from https://docs.astral.sh/uv/
   ```

2. **Set up Python virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate
   uv sync --all-groups
   ```

3. **Use the docs CLI tool:**
   ```bash
   docs --help
   docs migrate [path]  # can be directory or file, updates in place
   ```

### Why Use the Makefile?

The Makefile provides convenient commands that handle virtual environment activation automatically, so you don't need to manually activate/deactivate the venv each time. All Make commands automatically use the correct Python environment.

### Important Rules

- **Only edit files in `src/`** - The `build/` directory is automatically generated
- **Use Mintlify syntax** - See [Mintlify documentation](https://mintlify.com/docs) for formatting guidelines
- **Test your changes** - Use `make dev` to preview changes locally

### Available Commands

#### Make Commands (Recommended)
- `make install` - Install all dependencies and set up virtual environment
- `make dev` - Start development mode with file watching and live rebuild
- `make build` - Build documentation to `./build` directory  
- `make test` - Run the test suite
- `make lint` - Check code style and formatting
- `make format` - Auto-format code
- `make clean` - Remove build artifacts
- `make help` - Show all available commands

#### docs CLI Tool (Advanced)

For advanced usage, you can use the `docs` CLI tool directly (requires manual venv activation):

- **`docs migrate <path>`** - Convert markdown/notebook files to Mintlify format
  - `--dry-run` - Preview changes without writing files
  - `--output <path>` - Specify output location (default: in-place)

- **`docs mv <old_path> <new_path>`** - Move files and update cross-references
  - `--dry-run` - Preview changes without moving files

- **`docs dev`** - Start development mode with file watching
  - `--skip-build` - Skip initial build and use existing build directory

- **`docs build`** - Build documentation files
  - `--watch` - Watch for file changes after building

### Development Workflow

1. Edit files in `src/`
2. Run `make dev` to start the development server
3. The build system will automatically detect changes and rebuild
4. Preview your changes in the generated `build/` directory

### File Formats

- **Markdown files** (`.md`, `.mdx`) - Standard documentation content
- **Jupyter notebooks** (`.ipynb`) - Converted to markdown during build
- **Assets** - Images and other files are copied to the build directory

### Documentation Syntax

This project uses [Mintlify](https://mintlify.com/docs) for documentation generation. Key features:

- **Frontmatter** - YAML metadata at the top of files
- **Components** - Special Mintlify components for enhanced formatting
- **Code blocks** - Syntax highlighting and copy functionality
- **Navigation** - Automatic sidebar generation from file structure

Refer to the [Mintlify documentation](https://mintlify.com/docs) for detailed syntax and component usage.

### Testing

Run the test suite to ensure your changes don't break existing functionality:

```bash
make test
```

### Code Quality

Before submitting changes, ensure your code passes linting:

```bash
make lint
make format
```
