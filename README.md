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

1. **Install dependencies:**
 
   Install `uv` https://docs.astral.sh/uv/
   ```bash
   make install
   ```

2. **Start development mode:**
   ```bash
   make dev
   ```
   This watches for changes in `src/` and automatically rebuilds content in `build/`.

   This was cobbled together quickly and may not work well for all edits. 
   If it's getting stuck, kill the process and restart it.

   Alternatively, you can `make build`, and launch `mint` inside the `build/` directory 
   to preview changes.


3. **Build documentation:**
   ```bash
   make build
   ```
   Generates compiled .mdx files in the `build/` directory.

### Important Rules

- **Only edit files in `src/`** - The `build/` directory is automatically generated
- **Use Mintlify syntax** - See [Mintlify documentation](https://mintlify.com/docs) for formatting guidelines
- **Test your changes** - Use `make dev` to preview changes locally

### Available Commands

#### Make Commands
- `make dev` - Start development mode with file watching and live rebuild
- `make build` - Build documentation to `./build` directory  
- `make install` - Install all dependencies
- `make clean` - Remove build artifacts
- `make test` - Run the test suite
- `make lint` - Check code style and formatting
- `make format` - Auto-format code
- `make help` - Show all available commands

#### docs CLI Tool

The `docs` command (installed as `uv run docs`) provides additional functionality:

- **`docs migrate <path>`** - Convert markdown/notebook files to Mintlify format
  - `--dry-run` - Preview changes without writing files
  - `--output <path>` - Specify output location (default: in-place)

- **`docs mv <old_path> <new_path>`** - Move files and update cross-references
  - `--dry-run` - Preview changes without moving files

These can be used directly using the `Makefile` or via the `docs` CLI tool:

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