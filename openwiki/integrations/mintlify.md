---
type: integration
title: Mintlify Integration
description: Mintlify is the static site generator that transforms built documentation in /build/ into docs.langchain.com, with configuration via docs.json, theme via the aspen template, and deployment through CI/CD workflows.
tags: [mintlify, static-site-generator, deployment, site-configuration, theme]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-f2608d0d515da097485b6ec5
    resource: repo://.github/workflows/publish.yml
  - id: openwiki-source-5153f86e64d6ee0b305f72b3
    resource: repo://.github/workflows/refresh-langsmith-openapi.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-b481a230af378c0c50ed9994
    resource: repo://pipeline/commands/dev.py
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-554339f52225d7d8edff3ed0
    resource: repo://src/style.css
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# Mintlify Integration

Mintlify is the static site generator that builds and hosts [docs.langchain.com](https://docs.langchain.com). The LangChain documentation pipeline produces markdown and MDX files in the `/build/` directory, and Mintlify processes them using site configuration defined in `/src/docs.json` to render the final site.

## Role in the Documentation Pipeline

The LangChain documentation workflow has distinct phases:

1. **Build phase** (`pipeline build`): Transforms source files in `/src/` into language-versioned, preprocessed output in `/build/`
2. **Rendering phase** (Mintlify): Reads `/build/` and the site configuration in `docs.json`, renders the site locally during development or deploys to production
3. **Deployment phase** (GitHub Actions + Mintlify): GitHub Actions pushes built artifacts to the `prod` branch, which Mintlify monitors and automatically deploys

Mintlify's responsibilities are limited to rendering—it does not edit or preprocess source files, and documentation should never be edited directly in `/build/`.

## Site Configuration (docs.json)

Mintlify reads the site's complete configuration from `/build/docs.json` (generated from `/src/docs.json`). The schema must conform to [Mintlify's docs.json specification](https://mintlify.com/docs.json).

### Core Configuration Sections

**Theme and Styling:**
- **Theme**: Set to `aspen`, a Mintlify built-in theme that supports light/dark mode, custom fonts, and color customization
- **Colors**: Primary (`#161F34`), light accent (`#7FC8FF`), dark accent (`#006DDD`) 
- **Fonts**: TWK Lausanne (weight 700) for headings via `/fonts/TWKLausanne-700.woff2`, Inter for body text; additional weights are loaded via `/src/style.css`
- **Icons**: Tabler library (`https://tabler.io/icons`), not FontAwesome
- **Custom CSS**: `<link rel="stylesheet" href="/style.css">` injected into page `<head>`, allowing overrides of Mintlify defaults and custom component styling

**Navigation Structure:**
- **Products menu**: Two main navigation menus—"AGENT DEVELOPMENT LIFECYCLE" and "PRODUCTS AND SETUP"—each with menu items (Home, Build, Test, Deploy, Monitor, etc.)
- **Language dropdowns**: Most Build tab content offers Python and JavaScript dropdowns, each with separate tabs (Overview, Deep Agents, Managed Deep Agents, LangChain, LangGraph, OpenWiki, Integrations, Learn, Reference, Contribute)
- **Page hierarchy**: Groups and subgroups define collapsible navigation sections; pages reference build artifacts by path

**Contextual Actions:**
- **Copy, View**: Built-in Mintlify actions for copying page URL and opening source on GitHub
- **llms.txt**: Custom action linking to `https://docs.langchain.com/llms.txt` for AI agent consumption
- **ChatGPT, Claude, MCP, Cursor, VSCode**: Built-in integrations for accessing documentation in external tools

**Analytics and SEO:**
- **Google Tag Manager**: ID `GTM-MBBX68ST` for event tracking
- **Canonical URL**: `https://docs.langchain.com`
- **Google Site Verification**: Enables Search Console integration
- **Banner**: Dismissible announcement banner at page top (currently promoting Interrupt conference)

**Redirects:**
The `redirects` array in `docs.json` defines URL mappings for deprecated or reorganized pages. Two prominent patterns:

- **Managed Deep Agents unversioning**: Unversioned `/langsmith/managed-deep-agents*` URLs redirect to language-specific Python routes (`/langsmith/python/managed-deep-agents*`), preventing orphaned navigation entries in Mintlify
- **Build-level page routing**: `/oss/python/build-overview` and `/oss/javascript/build-overview` both redirect to `/build-overview`, which is shared across language versions

## Development Server (mint dev)

The development workflow integrates Mintlify's CLI:

```bash
make dev
```

This command:

1. **Builds source files** via `pipeline dev`, which watches `/src/` for changes and incrementally rebuilds to `/build/`
2. **Starts `mint dev`** in the `/build/` directory on port 3000
3. **Forwards file changes**: The watcher triggers rebuilds and instructs Mintlify to refresh

Mintlify's dev server provides:
- Hot reload on file changes
- Live preview of navigation, styling, and content
- Link validation and component preview

The `mint` CLI is a separate global npm binary installed via `npm install -g mint@latest`; it is not part of the Python virtualenv dependencies.

## Rendering Process

When Mintlify renders the site (locally or at deployment), it:

1. **Reads docs.json**: Parses navigation structure, theme, fonts, and configurations
2. **Loads markdown files**: Processes `.mdx` files from `/build/oss/`, `/build/langsmith/`, etc.
3. **Applies theme**: Uses Tabler icons, TWK Lausanne/Inter fonts, and custom CSS from `/src/style.css`
4. **Expands snippets**: Inline snippet imports (`import Snippet from '/snippets/component.mdx'`) are expanded into full page content
5. **Validates links**: Internal links are resolved against the docs.json navigation structure
6. **Generates OpenAPI reference pages**: Three OpenAPI specs generate endpoint documentation at deploy time:
   - Agent Server API (`src/langsmith/agent-server-openapi.json`) → `/langsmith/agent-server-api/`
   - Control Plane API (fetched from `https://api.host.langchain.com/openapi.json`) → `/api-reference/`
   - LangSmith REST API (`src/langsmith/langsmith-platform-openapi.json`) → `/langsmith/smith-api/`

## Deployment

### Build and Publish Workflow

The `publish.yml` GitHub Actions workflow runs on successful merges to `main`:

1. **Build**: Executes `make build` to generate `/build/` from `/src/`
2. **Verify**: Confirms `/build/` is non-empty
3. **Prepare**: Copies `/build/` into `/public/build/` directory structure
4. **Publish**: Uses `peaceiris/actions-gh-pages@v4` to push to the `prod` branch with `GITHUB_TOKEN`

The `prod` branch contains `/build/` artifacts under a `/build` subdirectory in the repo. Mintlify monitors this branch and automatically redeploys when changes are pushed.

### Redirection and Unversioned Routes

Unversioned URLs that should not appear in navigation (e.g., old API endpoints, deprecations) are handled via the `redirects` section in `docs.json`. Mintlify evaluates these redirects before serving a page, so users reaching an old URL are automatically sent to the canonical route without creating orphaned navigation entries.

**Example:** The unversioned `/langsmith/managed-deep-agents` URL does not exist in the navigation structure but redirects to `/langsmith/python/managed-deep-agents-overview`, preventing Mintlify from serving a broken page.

## Offline Export

Mintlify provides an offline export feature for generating a static ZIP archive of the documentation:

```bash
make export
```

This command:
1. Builds the documentation
2. Runs `mint export` from the `/build/` directory
3. Generates a ZIP file containing the complete offline documentation

The `mint export` command uses the Mintlify CLI to create a self-contained HTML/CSS/JS snapshot suitable for distribution.

## Fonts and Custom Styling

TWK Lausanne is a custom font loaded in two ways:

- **Primary weight (700)**: Loaded via `docs.json` configuration as the heading font
- **Additional weights** (250, 300, 350, 400, 600, Italic variants): Declared in `/src/style.css` using `@font-face` rules pointing to WOFF2 files in `/build/fonts/`

Mintlify applies the heading font to all `<h1>` through `<h6>` elements and Inter to body text. CSS cascade allows `/src/style.css` to override Mintlify's default styles for component appearance, spacing, and other custom branding.

## Icons and Components

The site uses **Tabler icons** exclusively (no FontAwesome). Icons are referenced in navigation items and callouts using Tabler's icon names:

```json
{
  "item": "Home",
  "icon": "home",
  "description": "Get started"
}
```

Mintlify resolves these names to SVG icons from Tabler's library and renders them inline. Custom MDX components (callouts, tabs, code blocks) are Mintlify built-ins, and additional React components are imported from `/snippets/` (e.g., `PatternEmbed.jsx`, `ExampleEmbed.jsx` from `@langchain/docs-sandbox`).

## Preview Branches and Testing

For PR previews, a separate `create-preview-branch.yml` workflow can be triggered to build documentation and push to a preview branch for staging review before merge.

## API Reference Generation at Deploy Time

The three OpenAPI specs are processed as follows:

- **Agent Server OpenAPI** (`src/langsmith/agent-server-openapi.json`): Committed to the repository; Mintlify reads it at build time and generates endpoint documentation. Updated by PRs from the `langgraph-api` repository.
- **Control Plane API**: Fetched at **deploy time** from `https://api.host.langchain.com/openapi.json`; not stored locally. Enables dynamic updates without PR commits.
- **LangSmith REST API** (`src/langsmith/langsmith-platform-openapi.json`): Refreshed daily by `.github/workflows/refresh-langsmith-openapi.yml`, which fetches from `api.smith.langchain.com`, filters fleet and internal endpoints, and opens a standing refresh PR.

## Assumptions and Invariants

- **Mintlify serves from `/build/`**: Direct edits to `/build/` are lost on the next build. The canonical source is always `/src/`.
- **docs.json pages must exist in build**: Mintlify validates navigation entries against actual files; missing pages cause rendering errors.
- **Redirects prevent orphaned pages**: Unversioned URLs not in navigation must have a matching redirect in `docs.json` to avoid broken routes.
- **Snippet imports are expanded**: Snippets are not served as standalone pages; they are inlined into importing pages at render time.
- **OpenAPI specs are valid JSON**: Mintlify validates OpenAPI specs during build; invalid syntax prevents deployment.

## Related Concepts

- **Build System** (`/openwiki/architecture/build-system.md`): How `/src/` is transformed into `/build/` with preprocessing, language versioning, and file duplication
- **GitHub Actions** (`/openwiki/integrations/github-actions.md`): CI/CD workflows that trigger builds, validate content, and deploy to Mintlify
- **Source Mapping** (`/openwiki/architecture/source-map.md`): How source files in `/src/` map to URLs, navigation entries, and build artifacts
