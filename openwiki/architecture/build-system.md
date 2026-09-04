---
type: architecture
title: Build System Architecture
description: The documentation pipeline transforms source files in /src into language-versioned build output through preprocessing, link rewriting, and content branching.
tags: [build-system, pipeline, preprocessing, content-versioning]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-17f3856bce97f37118963062
    resource: repo://pipeline/preprocessors/handle_auto_links.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# Build System Architecture

The documentation build pipeline transforms source files in `/src/` into Mintlify-compatible output in `/build/`. It implements a sophisticated content branching strategy that creates language-specific variants (Python and JavaScript) for most open-source content while maintaining unversioned pages for product documentation and language-agnostic resources.

## Overview: Three Content Branches

The build system manages three distinct content branches, each with different versioning and language-handling strategies:

1. **OSS versioned (Python/JavaScript)**: LangChain, LangGraph, and most Deep Agents docs branch into `/build/oss/python/` and `/build/oss/javascript/` routes with language-specific preprocessing.

2. **OSS language-agnostic**: Deep Agents Code (`/src/oss/deepagents/code/`) and OpenWiki (`/src/oss/openwiki/`) ship as single sets at `/build/oss/deepagents/code/` and `/build/oss/openwiki/` without duplication.

3. **LangSmith unversioned**: Unversioned product documentation in `/src/langsmith/` builds once to `/build/langsmith/`, except Managed Deep Agents which create Python and JavaScript language routes at `/langsmith/python/` and `/langsmith/javascript/`.

Shared assets—images, snippets, styles, configuration—copy once to the root `/build/` directory.

## Build Process and Entry Points

The build system is initialized through `pipeline/core/builder.py`, which orchestrates the full pipeline:

```python
builder = DocumentationBuilder(src_dir=Path("src"), build_dir=Path("build"))
builder.build_all()
```

`build_all()` executes these major stages in order:

1. **Clears `/build/`** to ensure a clean slate
2. **Builds versioned OSS content** separately for Python and JavaScript
3. **Builds unversioned OSS products** (Deep Agents Code, OpenWiki)
4. **Builds unversioned LangSmith content**
5. **Builds Managed Deep Agents language routes**
6. **Copies shared files** (images, docs.json, snippets, fonts)
7. **Copies npm snippet components** from `@langchain/docs-sandbox`
8. **Generates llms.txt and llms-full.txt** for AI agent consumption

Individual files can be built with `builder.build_file(file_path)` or collections with `builder.build_files(file_paths)`, useful for incremental builds during development.

## Preprocessing Pipeline

All markdown and MDX files pass through a preprocessing pipeline that applies four transformations in sequence:

### 1. Cross-Reference Resolution (@[LinkName])

Custom markdown syntax `@[LinkName]` (e.g., `@[StateGraph]`) is transformed to proper markdown links via `replace_autolinks()`. The transformation depends on scope context—python, js, or global:

```markdown
@[StateGraph]
```

becomes:

```markdown
[StateGraph](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.StateGraph)
```

The link target is resolved through scope-specific link maps (`SCOPE_LINK_MAPS`) that map common API names to their documentation URLs. Missing links are logged but do not fail the build.

### 2. Conditional Rendering (:::python / :::js)

Language-specific content blocks are processed based on the target language:

```markdown
:::python
This content appears only in Python builds
:::

:::js
This content appears only in JavaScript builds
:::
```

When building for Python, `::: content appears and :::js blocks are removed. Escaped blocks (`\:::`) are preserved as literal text for display in documentation about the syntax itself.

### 3. Link Rewriting

Three types of link rewrites occur during preprocessing:

- **OSS link versioning** (`_rewrite_oss_links`): `/oss/concepts/...` becomes `/oss/python/concepts/...` or `/oss/javascript/concepts/...` during language-specific builds. Language-agnostic products (Deep Agents Code, OpenWiki) are skipped and retain unprefixed routes.

- **Managed Deep Agents routing** (`_rewrite_managed_deep_agents_links`): Files in `/langsmith/managed-deep-agents*.mdx` rewrite their internal links to language-prefixed routes (`/langsmith/python/...` or `/langsmith/javascript/...`) during Python/JavaScript builds.

- **Snippet import redirection** (`_rewrite_snippet_imports_for_language`): Versioned pages that import snippets with `from '/snippets/component.mdx'` are redirected to language-specific copies at `/snippets/python/component.mdx` or `/snippets/javascript/component.mdx`.

### 4. UTM Tracking and Edit Links

LangSmith CTA links receive UTM tracking parameters for analytics. All pages (except home, snippets, and root-level templates) receive "Edit this page on GitHub" and "File an issue" footer links pointing to the source file.

## File Building Strategy

The `build_file()` method routes files based on their path:

- **`/src/oss/*` files**: Duplicate for Python and JavaScript unless they are language-agnostic (Deep Agents Code, OpenWiki). Each version receives independent preprocessing.

- **`/src/langsmith/*` files**: Build once, except Managed Deep Agents pages (`managed-deep-agents*.mdx`) which spawn Python and JavaScript variants.

- **Shared files** (images, docs.json, snippets, fonts, CSS, JS): Copy once to `/build/`. Snippet markdown files receive special treatment—they are emitted in three forms:
  - Python-prefixed copy at the original snippet path (default for unversioned importers)
  - Language-specific copy at `/snippets/python/...`
  - Language-specific copy at `/snippets/javascript/...`

- **Root-level files** (index.mdx, build-overview.mdx, use-these-docs.mdx, playground.mdx): Share across all versions.

## File Extension Handling

The builder supports the following file extensions:

- **Markdown and MDX**: `.md`, `.mdx` — preprocessed with conditional rendering, cross-reference resolution, and link rewriting
- **Data and config**: `.json`, `.yml`, `.yaml` — copied directly (YAML files named `docs.yml` are converted to `.json`)
- **Media and assets**: `.svg`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.mp4`, `.webm`, `.txt`, `.html`
- **Styling and scripting**: `.css`, `.js`
- **Web components**: `.jsx`, `.tsx`
- **Fonts**: `.woff2`, `.woff`, `.ttf`

Files without these extensions are skipped. Template files (`TEMPLATE.mdx`) are never copied.

## Shared Files Classification

The `is_shared_file()` method identifies files that must not be duplicated across language versions:

- **Snippets**: Any file under `/src/snippets/` (though snippet markdown receives language-specific processing within shared storage)
- **Images and assets**: Directories `images/`, `.well-known/`, `fonts/`
- **Styles and scripts**: All `.css` and `.js` files in `/src/`
- **Site configuration**: `docs.json`
- **Root pages**: `index.mdx`, `build-overview.mdx`, `use-these-docs.mdx`, `playground.mdx`

## Versioning Strategy and Language-Agnostic Products

Most OSS content is versioned by language—a single source page in `/src/oss/concepts/foo.mdx` produces two build artifacts:

- `/build/oss/python/concepts/foo.mdx` (with :::python blocks kept, :::js removed)
- `/build/oss/javascript/concepts/foo.mdx` (with :::js blocks kept, :::python removed)

**Language-agnostic products** (Deep Agents Code and OpenWiki) bypass versioning:

- `/src/oss/deepagents/code/**/*.mdx` → `/build/oss/deepagents/code/**/*.mdx` (one copy)
- `/src/oss/openwiki/**/*.mdx` → `/build/oss/openwiki/**/*.mdx` (one copy)

Links to these products remain unprefixed (`/oss/deepagents/code/...` and `/oss/openwiki/...`) in all contexts, and conditional blocks use the Python branch.

**Managed Deep Agents** represents a special case: source files live in `/src/langsmith/managed-deep-agents*.mdx` but build to:

- `/build/langsmith/python/managed-deep-agents*.mdx`
- `/build/langsmith/javascript/managed-deep-agents*.mdx`

The unversioned `/langsmith/managed-deep-agents*` URLs redirect to Python routes via `docs.json` configuration, so Mintlify does not serve orphaned pages outside the Managed Deep Agents navigation.

## Output Structure

The output directory `/build/` mirrors the following structure after a full build:

```
build/
├── oss/
│   ├── python/              # Versioned OSS (Python branch)
│   │   ├── langchain/
│   │   ├── langgraph/
│   │   ├── python/
│   │   ├── concepts/
│   │   ├── integrations/
│   │   └── ...
│   ├── javascript/          # Versioned OSS (JavaScript branch)
│   │   ├── langchain/
│   │   ├── langgraph/
│   │   ├── javascript/
│   │   ├── concepts/
│   │   ├── integrations/
│   │   └── ...
│   ├── deepagents/
│   │   └── code/            # Language-agnostic Deep Agents Code
│   └── openwiki/            # Language-agnostic OpenWiki
├── langsmith/               # Unversioned LangSmith (except Managed Deep Agents)
│   ├── python/              # Managed Deep Agents Python route
│   │   └── managed-deep-agents*.mdx
│   ├── javascript/          # Managed Deep Agents JavaScript route
│   │   └── managed-deep-agents*.mdx
│   └── fleet/
├── snippets/                # Shared snippets with language variants
│   ├── python/
│   ├── javascript/
│   └── *.mdx
├── images/                  # Shared images
├── fonts/                   # Shared fonts
├── docs.json                # Mintlify navigation and site config
├── index.mdx                # Shared home page
├── build-overview.mdx       # Shared overview
├── style.css                # Shared styles
└── llms.txt                 # LLM-friendly index (split corpus)
```

## Safety and Security

The builder implements several safeguards:

- **Symlink rejection**: Files that are symlinks are skipped, preventing symlink-based path escapes into system directories like `/proc/`.
- **Path containment validation**: When resolving relative paths from MDX or docs.json (which are user-editable), the builder verifies that resolved paths stay within the build tree via `_resolve_within()`.
- **Read-only build artifacts**: The CI/CD system does not allow direct edits to `/build/` and regenerates output from source with every push.

## Snippet Component Handling

The build copies npm snippet components from `@langchain/docs-sandbox` after processing source snippets, overwriting any source-tree versions. This ensures builds always use the latest published React components:

- `@langchain/docs-sandbox/dist/PatternEmbed.jsx` → `/build/snippets/pattern-embed.jsx`
- `@langchain/docs-sandbox/dist/ExampleEmbed.jsx` → `/build/snippets/example-embed.jsx`
- `@langchain/docs-sandbox/dist/ChatLangChainEmbed.js` → `/build/ChatLangChainEmbed.js`

## Configuration and Extension

The builder accepts a source and build directory path on initialization. Key configuration:

- **Language mapping**: Internal language keys ("python", "js") map to full URL names ("python", "javascript") via `language_url_names`.
- **Supported file extensions** are defined in `copy_extensions` and include markdown, images, code, styles, and web components.
- **Shared directories** (`images`, `fonts`, `.well-known`) and shared root files are defined in `is_shared_file()` and can be modified to extend or restrict what is duplicated.

The system is deterministic—rebuilding from the same source always produces identical output.

## Related Concepts

- **Preprocessing** (`/openwiki/concepts/preprocessing.md`): Details on conditional rendering, cross-reference resolution, and custom syntax transformations.
- **Versioning** (`/openwiki/concepts/versioning.md`): Strategy for language branching and how product versions are maintained.
- **Source mapping** (`/openwiki/architecture/source-map.md`): How source files map to build artifacts and URL routes.
