---
type: architecture
title: Markdown Preprocessing Pipeline
description: Multi-stage transformation of markdown source into final output through conditional rendering, cross-references, link rewriting, UTM decoration, and snippet import rewriting.
tags: [build, markdown, cross-references, conditional-rendering, link-rewriting, utm-tracking]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-17f3856bce97f37118963062
    resource: repo://pipeline/preprocessors/handle_auto_links.py
  - id: openwiki-source-dca59d03b9433eea9242c2e4
    resource: repo://pipeline/preprocessors/link_map.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
  - id: openwiki-source-3ae8d89866d72418f1bdab6b
    resource: repo://pipeline/preprocessors/utm_links.py
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

## Overview

The markdown preprocessing pipeline applies a sequence of six transformation layers to documentation source files before they are written to the build directory. Each layer solves a specific problem: rendering language-specific content, resolving semantic references, maintaining links in versioned products, supporting language-specific imports, tracking conversion links, and preserving source editability.

Preprocessing is orchestrated by `preprocess_markdown()` in `pipeline/preprocessors/markdown_preprocessor.py` and invoked from the `DocumentationBuilder` in `pipeline/core/builder.py` for every markdown/MDX file during the build. Parse errors, missing link references, and other failures are logged with file and line context; build exceptions abort the entire build.

## Pipeline Layers

### Layer 1: Conditional Rendering

Markdown may contain conditional blocks for language-specific content:

```markdown
:::python
This section is only shown to Python users.
:::

:::js
This section is only shown to JavaScript users.
:::
```

The `_apply_conditional_rendering()` function processes these blocks based on a `target_language` parameter ("python" or "js"). Blocks matching the target language are retained; non-matching blocks are removed entirely. Escaped blocks (with a leading backslash `\:::`) are treated as literal text and unescaped in the output.

**Key properties:**
- Conditional blocks may be nested or indented.
- If `target_language` is invalid (neither "python" nor "js"), a `ValueError` is raised.
- Unsupported language specifiers (neither "python" nor "js") are left unchanged.
- Content inside regular code fences (``` or ~~~) is never affected.

### Layer 2: Cross-Reference Resolution

Authors write semantic references like `@[StateGraph]` instead of hardcoding URLs. These are resolved to actual links based on the current scope (typically "python" or "js").

The `replace_autolinks()` function transforms `@[link_name]` patterns using scope-specific link maps. Supports two formats:

<!-- openwiki: broken internal link [url] file "url" does not exist. Fix the href or restore the target, then delete this comment. -->
- `@[link_name]` → `[link_name](url)`
<!-- openwiki: broken internal link [url] file "url" does not exist. Fix the href or restore the target, then delete this comment. -->
- `@[Custom Title][link_name]` → `[Custom Title](url)`

<!-- openwiki: broken internal link [url] file "url" does not exist. Fix the href or restore the target, then delete this comment. -->
Optional backticks in the link name become part of the title: `@[`CustomClass`]` → `[`CustomClass`](url)`.

**Resolution behavior:**
- Scope is determined at the top level by a "python" or "js" conditional fence, or defaults to `default_scope`.
- The current scope persists across lines until a new conditional fence is encountered.
- Scope changes inside code fences (``` or ~~~) do not affect line processing—the code fence state takes precedence.
- Links not found in the scope's link map are logged as info-level warnings and left unchanged.
- The "global" scope defaults to "python" (with an error-level log).

Link mappings live in `SCOPE_LINK_MAPS`, derived from `LINK_MAPS` in `pipeline/preprocessors/link_map.py`. Mappings exist for "python" and "js" scopes and reference both OSS and managed product APIs (Deep Agents, LangSmith agents/middleware).

### Layer 3: UTM Link Decoration

Conversion-oriented links to `smith.langchain.com` (signup, agent onboarding pages) are tagged with UTM parameters at build time; functional links (settings, hub, traces) are left untouched.

The `add_utm_to_cta_links()` function identifies markdown links `[text](https://smith.langchain.com/path)` and, if the path is a CTA path ("", "/", "/agents", "/agents/"), appends UTM query parameters:

- `utm_source=docs`
- `utm_medium=cta`
- `utm_campaign=langsmith-signup`
- `utm_content=<derived-from-file-path>`

The `utm_content` value is derived from the file path: e.g., `src/langsmith/home.mdx` becomes `langsmith-home`.

**Key properties:**
- Content inside code blocks (``` or ~~~ fences) is skipped.
- Existing query parameters are preserved and the UTM params are appended with "&".
- Non-smith.langchain.com URLs are unaffected.

### Layer 4: Link Rewriting for Versioned OSS Content

After core preprocessing, the builder rewrites absolute `/oss/` paths to include language prefixes when appropriate.

The `_rewrite_oss_links()` method in `DocumentationBuilder` transforms links like `/oss/langgraph/overview` → `/oss/python/langgraph/overview` (for Python target language). This allows version-specific builds to link to language-specific OSS content.

**Exceptions:** Links are left unchanged if they:
- Already specify a language (`/oss/python/...` or `/oss/javascript/...`)
- Reference language-agnostic paths (`/oss/deepagents/code/...` or `/oss/openwiki/...`)
- Contain "images"

### Layer 5: Snippet Import Path Rewriting

Snippets are short markdown fragments imported into pages. The build system generates language-specific copies at `build/snippets/{python|javascript}/...`. Versioned pages must import these language-prefixed copies.

The `_rewrite_snippet_imports_for_language()` method rewrites import statements:

```mdx
import MySnippet from '/snippets/my-snippet.mdx'
```

becomes (for Python target):

```mdx
import MySnippet from '/snippets/python/my-snippet.mdx'
```

Already-scoped imports (containing "python/" or "javascript/") are left unchanged.

### Layer 6: Source Edit Links

The builder appends GitHub edit and issue links to the end of markdown files, enabling readers to contribute corrections or improvements directly. These links are added by `_add_suggested_edits_link()` after all other preprocessing.

**Exceptions:** Links are not appended to:
- The home page (`index.mdx`)
- Snippet files (anything under "snippets" in the path)
- Files outside the `src/` directory

## Integration with Build

The preprocessing pipeline is invoked from two code paths:

1. **Regular markdown files:** `_process_markdown_file()` reads the source, calls `_process_markdown_content()` to apply all layers, and writes the result.

2. **Snippet files:** `_build_unversioned_file()` processes each snippet with every supported language, writing language-prefixed copies. Then it writes a Python-default copy at the base path.

The `target_language` parameter flows through the chain:
- `_process_markdown_content()` passes it to `preprocess_markdown()` for layers 1–3.
- After preprocessing returns, layers 4–5 are applied in `_process_markdown_content()`.
- Layer 6 is applied in `_process_markdown_file()` before writing.

## Error Handling

Parse errors and transformation failures are handled as follows:

- **Link resolution failures:** If a cross-reference like `@[UnknownClass]` is not found in the scope's link map, an info-level log is written with file and line context. The link is left unchanged (appears as literal `@[UnknownClass]` text).

- **Regex errors:** Invalid regex patterns in conditional block processing trigger an exception that is logged with the file path. The build continues (exception is caught), but the file's output is incomplete.

- **Build-time exceptions:** File I/O errors, decoding errors, and unexpected exceptions in `_process_markdown_content()` are caught, logged with context, and re-raised. This aborts the entire build.

The logging uses Python's standard `logging` module. Loggers are created per module (e.g., `__name__`).

## Key Invariants

1. **Code fence protection:** Content inside regular code blocks (``` or ~~~) is never processed for conditional rendering or cross-references. Scope changes inside code blocks do not apply.

2. **Order preservation:** Transformations occur in a strict order (layers 1–6). Each layer works on the output of the previous layer.

3. **Conditional block closure:** A `:::` fence without a language identifier closes the current conditional block and resets scope to the default. Nested blocks are not supported; the innermost `:::` closes the current block.

4. **Escaping:** Backslash-escaped markers (`\@[...]` and `\:::...`) are preserved as literal text by removing the escape character. Escaping is resolved in the final pass of each layer.

5. **Idempotence of rewrites:** The OSS link rewrite and snippet import rewrite are designed to not double-rewrite already-rewritten content (checking for "python/" or "javascript/" prefixes already present).

## Extension Points

The pipeline is extensible:

- **New scopes:** Add entries to `SCOPE_LINK_MAPS` in `link_map.py` to support new language/framework targets and their API reference links.
- **New CTA paths:** Extend `_CTA_PATHS` in `utm_links.py` to tag additional smith.langchain.com endpoints.
- **New transforms:** Insert new layers in `_process_markdown_content()` or after `preprocess_markdown()` returns.

## Configuration and Operations

**Environment variables:**

- `TARGET_LANGUAGE`: If not passed as a parameter to `preprocess_markdown()`, defaults to this environment variable (or "python" if unset).

**Link maps:**

The link map is a list of dictionaries mapping symbol names to URLs, grouped by host and scope. Currently defined scopes are "python" and "js", with hosts pointing to langchain.com reference docs and integration points. The map includes:
- Core LangChain modules (agents, tools, embeddings, messages)
- Deep Agents APIs (middleware, backends, graph)
- Third-party integrations (OpenAI, Anthropic, Google, etc.)
- Utility types and functions

**Versioning:**

The build system calls preprocessing separately for each language target (e.g., "python", "js"). Unversioned files (shared across all versions) receive the "python" default. This allows a single source page to produce multiple output versions with language-specific content and links.
