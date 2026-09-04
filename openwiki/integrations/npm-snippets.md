---
type: integration
title: NPM Snippet Components
description: Reusable React/TypeScript components from @langchain/docs-sandbox that enable interactive features like pattern visualizations and code sandboxes in MDX documentation pages.
tags: [npm-package, snippet-components, react-components, build-system, mdx-integration]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-5b54a58d1b51cd490b0e7162
    resource: repo://package.json
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-13bb4a68b3327e33785edf79
    resource: repo://src/oss/langchain/frontend/branching-chat.mdx
  - id: openwiki-source-1d8e4cd1c107f61094b773fd
    resource: repo://src/oss/langchain/frontend/integrations/copilotkit.mdx
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# NPM Snippet Components

Snippet components are reusable React/TypeScript UI components published in the `@langchain/docs-sandbox` npm package. They provide interactive visualizations and embedded experiences that enhance documentation pages with live demonstrations, pattern diagrams, and code sandboxes.

## Package and Components

The `@langchain/docs-sandbox` package (version ^0.0.23 or later in `package.json`) contains compiled `.jsx` and `.js` files that expose React components for use in MDX documentation.

### Available Components

The build system copies two main component categories:

**Snippet Components** — copied to `/build/snippets/`:
- `PatternEmbed.jsx`: Renders interactive flow diagrams and pattern visualizations (e.g., branching chat, custom stream channels, tool calling patterns)
- `ExampleEmbed.jsx`: Embeds interactive code examples and live sandboxes (e.g., CopilotKit, OpenUI, Assistant UI integration examples)

**Build-Root Components** — copied to `/build/`:
- `ChatLangChainEmbed.js`: A specialized chat interface component served at the site root for use across multiple pages

The exact set of components is defined in `DocumentationBuilder._NPM_SNIPPET_FILES` and `DocumentationBuilder._NPM_BUILD_FILES` class variables in `pipeline/core/builder.py`. This mapping ensures npm package files are renamed and placed correctly during the build process.

## How Snippet Components Work in MDX

### Import Pattern

MDX pages import snippet components directly by path:

```jsx
import { PatternEmbed } from "/snippets/pattern-embed.jsx"

<PatternEmbed pattern="branching-chat" />
```

Or for example embeds:

```jsx
import { ExampleEmbed } from "/snippets/example-embed.jsx"

<ExampleEmbed example="copilotkit" minHeight={700} />
```

### Component Props

Each component accepts configuration props:

- `PatternEmbed`: accepts `pattern` (string identifier), and other rendering options
- `ExampleEmbed`: accepts `example` (string identifier), `minHeight` (pixel height), and other sizing options

The actual pattern and example definitions (HTML/CSS/data structures) are bundled within the npm package and resolved by component name at render time.

### Usage Example

A typical use case is documenting frontend patterns:

```jsx
---
title: Branching Chat
---

Conversations with AI agents are rarely linear...

import { PatternEmbed } from "/snippets/pattern-embed.jsx"

<PatternEmbed pattern="branching-chat" />

This pattern treats conversations as a checkpointed timeline...
```

The component renders in the Mintlify dev server during development and in the published documentation build.

## Build Process Integration

### Installation and Copying

When the documentation build runs (`builder.build_all()`), the build process:

1. **Installs npm dependencies** via `npm install`, which populates `node_modules/@langchain/docs-sandbox/`
2. **Copies npm snippet components** in the `_copy_npm_snippets()` stage by reading from `node_modules/@langchain/docs-sandbox/dist/`
3. **Maps dist filenames to build locations** using the `_NPM_SNIPPET_FILES` and `_NPM_BUILD_FILES` dicts
4. **Overwrites source-tree versions** so the build always uses the latest published npm package versions

### Fallback Behavior

The builder includes local fallback versions of components in `/src/snippets/`. If the npm package is not installed, these fallbacks are copied instead. However, npm package versions (when installed) always overwrite fallbacks, ensuring reproducible builds with published component versions.

### Build Stage Order

NPM snippet copying occurs late in the build pipeline (after shared files are copied) to ensure npm versions take precedence:

1. Clear build directory
2. Build versioned OSS content (Python/JavaScript variants)
3. Build language-agnostic OSS products
4. Build unversioned LangSmith content
5. Build Managed Deep Agents language routes
6. Copy shared files (images, fonts, etc.) ← includes fallback snippets
7. **Copy npm snippet components** ← overwrites fallbacks with npm versions
8. Generate llms.txt and llms-full.txt

## Language-Specific Variant Handling

Snippet markdown files (`.mdx` files in `/src/snippets/`) are processed specially:

- **Default copy** (Python-prefixed): `/build/snippets/[filename].mdx`
- **Python variant**: `/build/snippets/python/[filename].mdx`
- **JavaScript variant**: `/build/snippets/javascript/[filename].mdx`

Versioned OSS pages that import snippets are automatically rewritten by `_rewrite_snippet_imports_for_language()` to point to language-specific copies:

```jsx
// Original import in source
import { ComponentTab } from "/snippets/component-tabs.mdx"

// Rewritten during JavaScript build
import { ComponentTab } from "/snippets/javascript/component-tabs.mdx"
```

However, JSX/TSX component files (like `pattern-embed.jsx`) are **not** language-versioned; a single version serves all build variants.

## Local Development and Testing

### Testing Components Locally

1. **Start the dev server**: Run Mintlify's dev server (typically `npm run dev` or similar)
2. **Components render live**: MDX pages that import snippet components render them in the browser as the server runs
3. **Hot reload**: Edit component props or MDX pages and observe changes in real-time

### Using Local or NPM Versions

- **During development**: If npm packages are not installed, local `/src/snippets/` components are used as fallbacks
- **After running `npm install`**: The npm package version takes precedence and is copied during the build
- **Publishing**: The build always copies npm versions, so component behavior is reproducible across environments

## Maintenance and Coordination

### Adding New Components

To add new snippet components:

1. **Develop in npm package**: Create and test the component in the `@langchain/docs-sandbox` repository
2. **Publish npm package**: Release a new version of `@langchain/docs-sandbox` to npm
3. **Update package.json**: Increment the `@langchain/docs-sandbox` version constraint in the docs `package.json`
4. **Run `npm install`**: Pull the new version into node_modules
5. **Update builder.py**: If the component is new, add an entry to `_NPM_SNIPPET_FILES` or `_NPM_BUILD_FILES` with the dist filename and destination name
6. **Import in MDX**: Use the component in pages with `import { ComponentName } from '/snippets/component-name.jsx'`

### Troubleshooting Missing Components

If components don't appear during build:

- **Check package.json**: Verify `@langchain/docs-sandbox` version is specified
- **Run npm install**: Ensure dependencies are installed: `npm install`
- **Verify dist files**: Check that files exist in `node_modules/@langchain/docs-sandbox/dist/`
- **Check builder mappings**: Confirm `_NPM_SNIPPET_FILES` or `_NPM_BUILD_FILES` contains the filename
- **Review build logs**: The build logs warnings if expected files are not found during `_copy_npm_snippets()`

## Integration with Documentation Architecture

Snippet components fit into the larger documentation pipeline:

- **Shared assets**: Components copy to shared build locations (`/build/snippets/` or `/build/`) once, not duplicated per language version
- **Preprocessing pipeline**: While component JSX is not preprocessed, MDX files that *import* components receive language-specific rewriting for correct import paths
- **Mintlify integration**: Components render as live React elements in Mintlify documentation, enabling interactive examples
- **Versioning strategy**: Components are language-agnostic but may be consumed by both Python and JavaScript documentation variants

See the [Build System Architecture](/openwiki/architecture/build-system.md) page for details on the full preprocessing pipeline and shared file handling.
