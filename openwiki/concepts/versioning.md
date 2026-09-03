---
type: concept
title: Language Versioning Strategy
description: How the build system creates separate Python and JavaScript documentation from shared sources using conditional blocks and link rewriting.
tags: [versioning, language-branching, documentation-pipeline, conditional-rendering, link-rewriting]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# Language Versioning Strategy

The documentation build system employs a sophisticated multi-branch strategy that creates language-specific variants of documentation from a single source tree. Rather than maintaining separate source files for Python and JavaScript, the build system uses conditional markers and link rewriting to produce distinct outputs for each language.

## Three Versioning Patterns

The system manages documentation through three distinct patterns, each suited to different product types:

### 1. OSS Dual-Version (Python + JavaScript)

**Applies to:** LangChain, LangGraph, and most Deep Agents documentation in `/src/oss/`.

Source files like `/src/oss/langgraph/overview.mdx` are built twice, once for each language:

- `/build/oss/python/langgraph/overview.mdx` — processed with `target_language="python"`
- `/build/oss/javascript/langgraph/overview.mdx` — processed with `target_language="js"`

Each build is independent; the same markdown source receives language-specific preprocessing:

- `:::python` blocks are kept in Python builds and removed from JavaScript builds
- `:::js` blocks are kept in JavaScript builds and removed from Python builds  
- Links rewritten `/oss/concepts/...` become `/oss/python/concepts/...` (for Python) or `/oss/javascript/concepts/...` (for JavaScript)
- Snippet imports like `from '/snippets/example.mdx'` are redirected to `/snippets/python/example.mdx` or `/snippets/javascript/example.mdx`

**Entry point:** `_build_langgraph_version()` in `pipeline/core/builder.py` orchestrates both Python and JavaScript builds for OSS versioned content.

### 2. OSS Language-Agnostic

**Applies to:** Deep Agents Code (`/src/oss/deepagents/code/`) and OpenWiki (`/src/oss/openwiki/`).

These products are explicitly not versioned by language. A single source directory produces one output:

- `/src/oss/deepagents/code/...` → `/build/oss/deepagents/code/...` (no python/javascript split)
- `/src/oss/openwiki/...` → `/build/oss/openwiki/...` (no python/javascript split)

The build system identifies language-agnostic files through `is_unversioned_oss_file()`. Unversioned content is processed once with `target_language="python"` (as a default), and:

- Links to unversioned products remain unprefixed: `/oss/deepagents/code/...` or `/oss/openwiki/...`
- These paths are explicitly excluded from OSS link rewriting via checks in `_rewrite_oss_links()`
- Other versioned OSS pages that reference unversioned products use unprefixed URLs (e.g., `/oss/deepagents/code/overview` not `/oss/python/deepagents/code/overview`)

**Entry point:** `_build_unversioned_oss_code()` and `_build_unversioned_oss_openwiki()` in `pipeline/core/builder.py`.

### 3. LangSmith Unversioned with Managed Deep Agents Exception

**Applies to:** LangSmith product documentation in `/src/langsmith/` (except Managed Deep Agents).

Most LangSmith documentation is unversioned—a single source file builds once:

- `/src/langsmith/deployment.mdx` → `/build/langsmith/deployment.mdx`

However, Managed Deep Agents pages (`managed-deep-agents*.mdx` files in `/src/langsmith/`) are a special case. These pages source in unversioned LangSmith but emit to language-specific routes:

- `/src/langsmith/managed-deep-agents-overview.mdx` → 
  - `/build/langsmith/python/managed-deep-agents-overview.mdx`
  - `/build/langsmith/javascript/managed-deep-agents-overview.mdx`

This allows Managed Deep Agents documentation to provide language-specific code examples and tool references.

**Redirect strategy:** The unversioned URLs (`/langsmith/managed-deep-agents-*`) do not exist in the build output. Instead, `docs.json` contains redirects that route unversioned requests to the Python language route:

```json
{
  "source": "/langsmith/managed-deep-agents-overview",
  "destination": "/langsmith/python/managed-deep-agents-overview"
}
```

This ensures that:
- Existing links to `/langsmith/managed-deep-agents-*` continue to work
- Documentation navigation never exposes orphaned pages outside the Managed Deep Agents navigation structure  
- Default behavior is Python, with JavaScript as an alternate choice

**Entry points:** `is_managed_deep_agents_file()` and `_build_managed_deep_agents_variants()` in `pipeline/core/builder.py` detect and route Managed Deep Agents pages.

## Conditional Block Syntax

Language-specific content is marked with fence-style conditionals:

```markdown
:::python
This section is only shown to Python users.
:::

:::js
This section is only shown to JavaScript users.
:::
```

### How Conditionals Are Resolved

During the build, the `_apply_conditional_rendering()` function in `pipeline/preprocessors/markdown_preprocessor.py` processes these blocks based on `target_language`:

- When building Python output, `:::python` blocks are kept and `:::js` blocks are removed entirely
- When building JavaScript output, `:::js` blocks are kept and `:::python` blocks are removed entirely
- If neither language matches a block, the block is left unchanged (treated as unsupported)
- Content between the opening fence (`:::language`) and closing fence (`:::`) is kept or removed as a unit

### Escaping Conditional Markers

Conditionals can be escaped with a leading backslash for documentation that needs to show the syntax itself:

```markdown
\:::python
This will appear in output as literal :::python
\:::
```

Escaped markers are unescaped during processing, so the output contains the original fence syntax.

### Important Properties

- Conditional blocks may be indented and are matched at the same indentation level
- Content inside regular code fences (triple backticks or tildes) is never processed for conditional logic
- Nested conditionals are not supported; the innermost `:::` (non-escaped) closes the current block
- If a conditional is malformed (unclosed), a build exception is logged

## Link Rewriting During Build

Link rewriting ensures that documentation links point to the correct language-versioned route.

### OSS Link Versioning

The `_rewrite_oss_links()` method rewrites absolute `/oss/` paths to include language prefixes for versioned products.

**Transformation:**
```
/oss/langgraph/overview → /oss/python/langgraph/overview (Python build)
/oss/langgraph/overview → /oss/javascript/langgraph/overview (JavaScript build)
```

**Exceptions (links are left unchanged):**
- Links that already specify a language: `/oss/python/...` or `/oss/javascript/...`
- Language-agnostic products: `/oss/deepagents/code/...` or `/oss/openwiki/...`
- Links containing "images": `/oss/images/...`

This prevents double-prefixing (producing broken URLs like `/oss/python/python/...`) and preserves unprefixed routes for language-agnostic products.

**Applied to:**
<!-- openwiki: broken internal link [/oss/path] file "/oss/path" does not exist. Fix the href or restore the target, then delete this comment. -->
- Markdown links: `[text](/oss/path)`
- HTML links: `<a href="/oss/path">`
- HTML anchors: `<div id="/oss/path">`

### Managed Deep Agents Link Rewriting

The `_rewrite_managed_deep_agents_links()` method rewrites links within Managed Deep Agents pages to target their language-specific routes.

**Transformation:**
```
/langsmith/managed-deep-agents-overview → /langsmith/python/managed-deep-agents-overview (Python build)
/langsmith/managed-deep-agents-overview → /langsmith/javascript/managed-deep-agents-overview (JavaScript build)
```

This is applied only to Managed Deep Agents files (files matching the pattern `managed-deep-agents*.mdx` in `/src/langsmith/`). It rewrites internal cross-references so that a Managed Deep Agents page links to other Managed Deep Agents pages via the same language route.

### Snippet Component Import Rewriting

Snippets are reusable markdown fragments. When versioned pages import snippets, they must import language-specific copies:

**Before rewriting:**
```mdx
import MySnippet from '/snippets/my-snippet.mdx'
```

**After rewriting (Python build):**
```mdx
import MySnippet from '/snippets/python/my-snippet.mdx'
```

**After rewriting (JavaScript build):**
```mdx
import MySnippet from '/snippets/javascript/my-snippet.mdx'
```

The `_rewrite_snippet_imports_for_language()` method uses regex to detect unversioned snippet imports and insert the language name. Already-prefixed imports (containing "python/" or "javascript/" in the path) are left unchanged to prevent double-rewriting.

**Applied only to:** Versioned OSS pages (files built for both Python and JavaScript). Unversioned pages continue to import from the base snippet path.

## Build Process for Versioned Content

When `DocumentationBuilder.build_all()` is invoked, the system executes these stages in order:

1. **Clear `/build/` directory** to ensure a clean build from source
2. **Build Python version** of all OSS content (`oss/python/...`)
3. **Build JavaScript version** of all OSS content (`oss/javascript/...`)
4. **Build unversioned OSS products** (Deep Agents Code, OpenWiki)
5. **Build unversioned LangSmith content** (except Managed Deep Agents)
6. **Build Managed Deep Agents language routes** (`langsmith/python/...`, `langsmith/javascript/...`)
7. **Copy shared files** (images, `docs.json`, styles, fonts)
8. **Copy npm snippet components** from the `@langchain/docs-sandbox` package
9. **Generate `llms.txt` and `llms-full.txt`** for AI agent consumption

Each build stage processes markdown through the same preprocessing pipeline:

```python
content = preprocess_markdown(content, file_path, target_language=target_language)
```

The preprocessing applies conditional rendering, cross-reference resolution, and link rewriting in sequence, as defined in `/openwiki/concepts/preprocessing.md`.

## Build Output Structure

After a full build, the `/build/` directory reflects the versioning strategy:

```
build/
├── oss/
│   ├── python/           # Versioned OSS (Python branch)
│   │   ├── langchain/
│   │   ├── langgraph/
│   │   ├── concepts/
│   │   └── ...
│   ├── javascript/       # Versioned OSS (JavaScript branch)
│   │   ├── langchain/
│   │   ├── langgraph/
│   │   ├── concepts/
│   │   └── ...
│   ├── deepagents/
│   │   └── code/        # Language-agnostic (single copy)
│   └── openwiki/        # Language-agnostic (single copy)
├── langsmith/           # Unversioned LangSmith
│   ├── python/          # Managed Deep Agents Python route
│   │   └── managed-deep-agents-*.mdx
│   ├── javascript/      # Managed Deep Agents JavaScript route
│   │   └── managed-deep-agents-*.mdx
│   └── other files...
├── snippets/            # Shared snippets with language variants
│   ├── python/
│   ├── javascript/
│   └── base copies...
├── images/              # Shared (single copy)
├── docs.json            # Shared navigation and redirects
└── ...
```

## Operational Responsibilities and Entry Points

### DocumentationBuilder class (`pipeline/core/builder.py`)

- **`build_all()`** – Orchestrates the complete build pipeline, clearing the build directory and invoking all versioning stages in order.
- **`build_file(file_path)`** – Routes a single file to the appropriate builder method based on its source path:
  - OSS files → `_build_oss_file()` (creates Python and JavaScript variants, with exceptions for unversioned products)
  - LangSmith files → `_build_unversioned_file()` (with special handling for Managed Deep Agents)
  - Shared files → `_build_shared_file()` (images, docs.json, etc.)
- **`is_unversioned_oss_file(file_path)`** – Returns `True` for files in `/oss/deepagents/code/` or `/oss/openwiki/` that must not be duplicated.
- **`is_managed_deep_agents_file(file_path)`** – Returns `True` for files matching `managed-deep-agents*.mdx` in `/src/langsmith/`.
- **`_rewrite_oss_links(content, target_language)`** – Rewrites `/oss/` links to include language prefixes for versioned builds.
- **`_rewrite_managed_deep_agents_links(content, target_language)`** – Rewrites internal Managed Deep Agents links to language-prefixed routes.
- **`_rewrite_snippet_imports_for_language(content, target_language)`** – Rewrites snippet imports to point to language-specific copies.

### Preprocessing functions (`pipeline/preprocessors/`)

- **`preprocess_markdown(content, file_path, target_language, default_scope)`** – Main entry point for all markdown transformations; applies conditional rendering, cross-reference resolution, UTM decoration, and calls link rewriting methods.
- **`_apply_conditional_rendering(md_text, target_language)`** – Resolves `:::python` and `:::js` conditional blocks based on the target language.

### Data and Configuration

- **`language_url_names`** dictionary in `DocumentationBuilder` – Maps internal language keys ("python", "js") to full URL names ("python", "javascript").
- **`docs.json`** – Contains redirects for Managed Deep Agents unversioned URLs to their Python routes.

## State and Lifecycle

### Per-Build State

Each call to `build_all()` is independent:

1. The build directory is completely cleared at the start
2. Files are processed sequentially (or with progress tracking for multiple files)
3. Preprocessing state (target_language, default_scope) flows through each file's transformation pipeline
4. The final output structure is written and stable until the next build

### Invariants

- **No duplicate link rewriting:** Link rewriting is idempotent—already-rewritten paths (those containing "python/" or "javascript/" prefixes) are not rewritten again
- **Conditional block closure:** Unescaped `:::` markers always close the most recent conditional block
- **Language consistency:** Within a single build pass, all files receive the same `target_language`, ensuring consistent behavior
- **Shared file stability:** Images, fonts, and site configuration (`docs.json`) are copied once and shared across all versions

## Extension Points

The versioning system can be extended:

- **Add language-agnostic products:** Extend `is_unversioned_oss_file()` to recognize new product paths that should not be versioned
- **Add Managed Deep Agents variants:** Modify `is_managed_deep_agents_file()` to match additional file patterns if new product families require language-specific routes
- **Add language-specific link rewriting rules:** Extend `_rewrite_oss_links()` or create new rewriting methods for products with custom routing requirements

## Related Concepts

- **Preprocessing Pipeline** (`/openwiki/concepts/preprocessing.md`): Details on how conditional rendering, cross-reference resolution, and other transformations work in sequence
- **Build System Architecture** (`/openwiki/architecture/build-system.md`): Comprehensive overview of the build process, file handling, and output structure
- **Markdown Preprocessing** (`/openwiki/concepts/preprocessing.md`): Layer-by-layer explanation of all transformation stages
