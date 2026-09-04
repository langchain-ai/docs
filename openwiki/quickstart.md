---
type: guide
title: Quickstart
description: Entry point for engineers joining the docs repository. Learn the repository's purpose, major sections, and key development tasks.
tags: [quickstart, getting-started, workflows, setup, documentation]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# Quickstart

Welcome to the LangChain documentation repository! This page orients you to the repository structure, major domains, and common development tasks.

## What Is This Repository?

This repository builds and hosts documentation for LangChain products. It has two main responsibilities:

1. **Build and deploy `docs.langchain.com`** — A Mintlify-based documentation site that consolidates documentation for LangChain, LangGraph, LangSmith, Deep Agents, and OpenWiki. The `/build` directory contains the final Mintlify output ready for deployment.

2. **Provide source documentation** — Engineers and writers work in `/src` to create and maintain markdown and MDX files. The build pipeline preprocesses, versions, and transforms these sources into the final documentation output.

## Quick Setup

Get your development environment running in minutes:

```bash
# Clone the repository
git clone https://github.com/langchain-ai/docs.git
cd docs

# Install dependencies (Python, Node.js, and the Mintlify CLI)
make install

# Start local development server
make dev
```

After `make dev` completes, open `http://localhost:3000` to preview the documentation locally.

## Repository Structure

```
docs/
├── src/                           # All manually authored content
│   ├── docs.json                  # Mintlify navigation and site config
│   ├── index.mdx                  # Home page
│   ├── langsmith/                 # LangSmith product docs
│   ├── oss/                       # Open source docs (LangChain, LangGraph, Deep Agents, OpenWiki)
│   ├── snippets/                  # Reusable MDX components
│   └── images/                    # Documentation images and icons
├── pipeline/                      # Python build pipeline and preprocessors
│   ├── core/                      # Core builder and watcher classes
│   ├── commands/                  # CLI commands (build, dev, migrate)
│   └── preprocessors/             # Markdown preprocessing (links, versioning, UTM)
├── build/                         # Generated Mintlify output (do NOT edit)
├── tests/                         # Test suite (pytest)
└── Makefile                       # Build targets and commands
```

## The Five Major Sections

The documentation is organized into five main areas for engineers and writers:

### 1. **Architecture & Design** — How the build system works
Learn how the documentation pipeline preprocesses source files, creates language-specific variants, and generates final output.

- [**Build System Architecture**](/openwiki/architecture/build-system.md) — Pipeline overview, content branching strategy (Python/JavaScript), and preprocessing stages
- [**Source Directory Map**](/openwiki/architecture/source-map.md) — Visual guide to `/src` structure and how it maps to output routes

### 2. **Core Concepts** — Key technical ideas
Understand the versioning strategy, preprocessing pipeline, and how conditional content works.

- [**Language Versioning Strategy**](/openwiki/concepts/versioning.md) — How Python and JavaScript documentation are created from shared sources
- [**Markdown Preprocessing Pipeline**](/openwiki/concepts/preprocessing.md) — Cross-references, conditional rendering, link rewriting, and UTM parameters

### 3. **Integration Points** — External systems
See how this repository integrates with Mintlify, GitHub Actions, NPM packages, and external API reference sites.

- [**Mintlify Integration**](/openwiki/integrations/mintlify.md) — Site rendering, deployment, and component usage
- [**GitHub Actions and CI/CD**](/openwiki/integrations/github-actions.md) — Workflows, PR checks, and deployment pipelines
- [**NPM Snippet Components**](/openwiki/integrations/npm-snippets.md) — Reusable React/TypeScript snippet components
- [**API Reference Integration**](/openwiki/integrations/reference-docs.md) — Linking to reference.langchain.com and managing API specs

### 4. **Operations & Workflows** — Day-to-day tasks
Step-by-step guides for common development activities: adding pages, writing versioned content, understanding CLI tools, and using cross-reference links.

- [**Local Development Workflow**](/openwiki/workflows/local-development.md) — Clone, install, and develop locally
- [**Writing Versioned Content**](/openwiki/workflows/versioned-content.md) — Best practices for Python/JavaScript conditional content
- [**Adding and Modifying Pages**](/openwiki/operations/adding-pages.md) — Creating new pages and moving existing ones
- [**CLI Tools Reference**](/openwiki/operations/cli-tools.md) — The `docs` Python CLI (dev, build, migrate, mv)
- [**Cross-Reference Links**](/openwiki/operations/cross-references.md) — Using `@[ClassName]` syntax for resilient API links

### 5. **Testing** — Quality assurance
Understand the test suite, how to run tests, and how to test conditional content and preprocessing.

- [**Testing Overview**](/openwiki/testing/test-overview.md) — Test suite structure, categories, and how to run tests
- [**Builder Tests**](/openwiki/testing/builder-tests.md) — Testing file versioning, preprocessing, and directory structure
- [**Testing Conditional Rendering**](/openwiki/testing/conditional-rendering.md) — Validating Python and JavaScript variants

## Key Tasks

### Task: Set Up Local Development
**Purpose**: Start previewing changes instantly as you write.

```bash
make install        # Install all dependencies
make dev            # Start development server at localhost:3000
```

The dev server watches for changes in `/src/` and automatically rebuilds and refreshes the browser.

**Related**: [Local Development Workflow](/openwiki/workflows/local-development.md)

### Task: Understand Versioning
**Purpose**: Know why some content appears in Python docs and other content in JavaScript docs.

The build system creates two separate documentation sites from a shared source:
- **Python docs**: `oss/python/...` (via build preprocessing)
- **JavaScript docs**: `oss/javascript/...` (via build preprocessing)

Language-specific blocks (`::: and :::js`) are processed during the build. Shared content (images, integrations, concepts) is copied once.

**Related**: [Language Versioning Strategy](/openwiki/concepts/versioning.md), [Writing Versioned Content](/openwiki/workflows/versioned-content.md)

### Task: Build and Test
**Purpose**: Ensure your changes work correctly before opening a pull request.

```bash
make build                       # Build to /build directory
make test                        # Run all tests
make lint_prose                  # Check writing style
uv run pytest tests/ -vv         # Run tests with verbose output
```

All tests must pass before merging. PR checks run these commands automatically via GitHub Actions.

**Related**: [Testing Overview](/openwiki/testing/test-overview.md), [Build System Architecture](/openwiki/architecture/build-system.md)

### Task: Add or Move Pages
**Purpose**: Create new documentation pages and keep links working when you move existing pages.

```bash
# Use the CLI to move files and update cross-references automatically
uv run docs mv src/oss/old-path.mdx src/oss/new-path.mdx

# Then update src/docs.json navigation to reflect the new location
```

**Related**: [Adding and Modifying Pages](/openwiki/operations/adding-pages.md), [CLI Tools Reference](/openwiki/operations/cli-tools.md)

### Task: Use Cross-References for API Links
**Purpose**: Create resilient links to API documentation that update automatically.

Instead of hardcoded URLs, use the `@[ClassName]` syntax:

```markdown
The @[StateGraph] class is used to build LangGraph applications.
```

The build system resolves this to the correct reference documentation URL for the target language (Python or JavaScript).

**Related**: [Cross-Reference Links](/openwiki/operations/cross-references.md), [Build System Architecture](/openwiki/architecture/build-system.md)

## Common Commands

| Command | Purpose |
|---------|---------|
| `make dev` | Start local dev server with file watching (localhost:3000) |
| `make build` | Build documentation to `/build` directory |
| `make test` | Run test suite |
| `make install` | Install all dependencies |
| `make lint_prose` | Check writing style with Vale |
| `make format` | Auto-format Python code |
| `uv run docs build` | Build with custom options |
| `uv run docs dev` | Start dev server (alias for `make dev`) |
| `uv run docs mv <old> <new>` | Move file and update cross-references |
| `uv run docs migrate <path>` | Convert Docusaurus/MkDocs to Mintlify format |

See the [Makefile](/Makefile) for the complete list.

## Important Conventions

1. **Never edit `/build/`** — This directory is generated by the build pipeline. Always edit files in `/src/`.

2. **Always update `src/docs.json`** — When adding new pages, update the Mintlify navigation configuration so they appear in the sidebar.

3. **Test before opening a PR** — Run `make test` and `make build` locally to catch issues early.

4. **Use Tabler icons only** — The documentation uses Tabler icons (`https://tabler.io/icons`). FontAwesome icons are not supported.

5. **Write versioned content carefully** — Use `::: and :::js blocks to branch content. See [Writing Versioned Content](/openwiki/workflows/versioned-content.md) for best practices.

## Getting Help

- **Architecture questions**: See [Build System Architecture](/openwiki/architecture/build-system.md)
- **How to add a page**: See [Adding and Modifying Pages](/openwiki/operations/adding-pages.md)
- **Tests not passing**: See [Testing Overview](/openwiki/testing/test-overview.md)
- **Conditional content issues**: See [Testing Conditional Rendering](/openwiki/testing/conditional-rendering.md)
- **Link questions**: See [Cross-Reference Links](/openwiki/operations/cross-references.md)
- **CLI questions**: See [CLI Tools Reference](/openwiki/operations/cli-tools.md)

## Next Steps

1. **Run `make install` and `make dev`** to start the local development server
2. **Read [Local Development Workflow](/openwiki/workflows/local-development.md)** for detailed setup steps
3. **Explore the [Build System Architecture](/openwiki/architecture/build-system.md)** to understand how the pipeline works
4. **Check out [Writing Versioned Content](/openwiki/workflows/versioned-content.md)** if you're working on language-specific documentation

Happy documenting! 🦜
