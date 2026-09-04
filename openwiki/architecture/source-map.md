---
type: architectural reference
title: Source Directory Map
description: Directory structure of /src and how it maps to navigation items, tabs, and URL routes in the Mintlify documentation site.
tags: [documentation, build, navigation, source-map, architecture]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

## Overview

The `/src` directory contains all manually authored documentation for the LangChain docs site (`docs.langchain.com`), deployed via Mintlify. This page maps source directories to their corresponding navigation locations, URL routes, and the shared assets required to render them.

## Key principle: Navigation labels diverge from directory names

Directory structure constrains URLs and influences navigation structure, but source paths do not perfectly mirror navigation labels. For example:
- The directory `/src/langsmith/fleet/` maps to the "No-code agents" menu item in the site navigation
- Files named `managed-deep-agents*.mdx` in `/src/langsmith/` map to the "Managed Deep Agents" tab in the Build menu, with language-prefixed routes

Always use `src/docs.json` as the source of truth for navigation structure and page routing, not the directory names.

## Build process

The Mintlify build pipeline reads source files from `/src`, executes preprocessors (including language-versioning and link resolution), and outputs the build artifacts to `/build`. The `/build` directory is deployed to Mintlify and should never be edited manually. See [build-system.md](/openwiki/architecture/build-system.md) for details on the pipeline architecture.

## Shared assets

These directories are accessible across all documentation sections:

| Path | Purpose | Format |
|------|---------|--------|
| `/src/images/` | Documentation images, diagrams, screenshots | PNG, JPG, SVG |
| `/src/images/brand/` | Logos, favicons, brand assets | PNG, SVG |
| `/src/images/providers/` | Integration provider icons (dark/ and light/ variants) | SVG |
| `/src/style.css` | Custom CSS for Mintlify theme | CSS |
| `/src/docs.json` | Mintlify configuration and navigation structure | JSON |
| `/src/fonts/` | TWK Lausanne web fonts | WOFF2 |

## Documentation products and menu structure

The site has two products in its navigation, each containing multiple menu items and tabs:

### AGENT DEVELOPMENT LIFECYCLE

Five menu items: **Home**, **Build**, **Test**, **Deploy**, **Monitor**.

#### Home
- **Source:** `src/index.mdx` (single page)
- **URL:** `/` (root)

#### Build
- **Structure:** Two language dropdowns (Python, TypeScript), each with 10 tabs
- **Language versioning:** Most tabs contain language-split content; two tabs (Managed Deep Agents and OpenWiki) are exceptions
- **URL pattern:** `/oss/python/...` or `/oss/javascript/...` (language-versioned); `/oss/openwiki/...` (unversioned)

| Tab | Source directory | URL prefix |
|-----|------------------|-----------|
| Overview | `src/build-overview.mdx` | `/build-overview` |
| Deep Agents | `src/oss/deepagents/` | `/oss/{python,javascript}/deepagents/` |
| Managed Deep Agents | `src/langsmith/managed-deep-agents*.mdx` | `/langsmith/{python,javascript}/managed-deep-agents-...` (language-prefixed routes; unversioned URLs redirect to Python) |
| LangChain | `src/oss/langchain/` | `/oss/{python,javascript}/langchain/` |
| LangGraph | `src/oss/langgraph/` | `/oss/{python,javascript}/langgraph/` |
| OpenWiki | `src/oss/openwiki/` | `/oss/openwiki/...` (no language split; conditional fences resolve against Python branch) |
| Integrations | `src/oss/{python,javascript}/integrations/` | `/oss/{python,javascript}/integrations/...` |
| Learn | Various in `src/oss/` | `/oss/{python,javascript}/...` (tutorials, conceptual overviews, resources) |
| Reference | `src/oss/reference/` | `/oss/{python,javascript}/reference/...` |
| Contribute | `src/oss/contributing/` | `/oss/{python,javascript}/contributing/...` |

#### Test
- **Source:** All files flat in `src/langsmith/`
- **Tabs:** Get started, Datasets & Experiments, Evaluators, Annotation Queues, Test from Playground, Test from Studio
- **URL pattern:** `/langsmith/...` (flat routing, no language or versioning)
- **Key files:** `evaluation*.mdx`, `dataset*.mdx`, `evaluator*.mdx`, `annotation*.mdx`, `studio.mdx`, `pytest.mdx`, `harbor-integrations.mdx`

#### Deploy
- **Source:** All files flat in `src/langsmith/`
- **Tabs:** Get started, Agent Server, Deploy to Cloud, Deploy to Self-hosted, Prompt & Context Hub, Sandboxes
- **URL pattern:** `/langsmith/...` (flat routing)
- **Key files:** `deployment*.mdx`, `agent-server*.mdx`, `deploy-*.mdx`, `prompt-*.mdx`, `sandbox*.mdx`
- **OpenAPI-generated sections:**
  - Agent Server API: generated from `src/langsmith/agent-server-openapi.json` → `/langsmith/agent-server-api/`
  - Control Plane API: generated from remote spec → `/api-reference/`

#### Monitor
- **Source:** All files flat in `src/langsmith/`
- **Tabs:** Overview, Trace, Debug, Observe, Reference
- **URL pattern:** `/langsmith/...` (flat routing)
- **Key files:** `observability*.mdx`, `trace-*.mdx`, `export-traces.mdx`, `dashboards.mdx`, `alerts.mdx`, `online-evaluations*.mdx`
- **OpenAPI-generated section:**
  - LangSmith REST API: generated from `src/langsmith/langsmith-platform-openapi.json` → `/langsmith/smith-api/`

### PRODUCTS AND SETUP

Five menu items: **LangSmith setup**, **LLM Gateway**, **No-code agents**, **Engine**, **Deep Agents Code**.

#### LangSmith setup
- **Source:** All files flat in `src/langsmith/`
- **Tabs:** Overview, Account, Cloud, BYOC, Self-hosted, Govern
- **URL pattern:** `/langsmith/...` (flat routing)
- **Key files:** `platform-setup.mdx`, `billing.mdx`, `cloud.mdx`, `byoc*.mdx`, `self-host*.mdx`, `administration-overview.mdx`, `user-management.mdx`, `rbac.mdx`, `abac.mdx`

#### LLM Gateway
- **Source:** `src/langsmith/llm-gateway*.mdx` (flat in langsmith)
- **Navigation structure:** No tabs; groups within flat navigation
- **URL pattern:** `/langsmith/llm-gateway...`

#### No-code agents
- **Navigation label:** "No-code agents" (displayed in UI)
- **Source directory:** `src/langsmith/fleet/`
- **Groups:** Get started, Configure, Tools and automation, Advanced, Additional resources
- **URL pattern:** `/langsmith/fleet/...`
- **Key files:** `fleet/index.mdx`, `fleet/quickstart.mdx`, `fleet/essentials.mdx`, `fleet/tools.mdx`, `fleet/slack-app.mdx`, `fleet/code.mdx`

#### Engine
- **Source:** `src/langsmith/engine*.mdx` (flat in langsmith)
- **URL pattern:** `/langsmith/engine...`

#### Deep Agents Code
- **Navigation label:** "Deep Agents Code" (displayed under Products and Setup)
- **Source directory:** `src/oss/deepagents/code/`
- **Groups:** Configuration (flat navigation, no language split)
- **URL pattern:** `/oss/deepagents/code/...`
- **Note:** Unversioned despite living under `/src/oss/deepagents/`; conditional fences resolve against Python branch

## Open source documentation structure

### Language-versioned OSS tabs

Most OSS documentation is split by programming language. A single MDX source with language-specific fences (`:::python` and `:::js`) generates both Python and TypeScript versions of a page.

**Language-split directories:**
- `src/oss/python/` → Python-specific pages at `/oss/python/...`
- `src/oss/javascript/` → TypeScript-specific pages at `/oss/javascript/...`
- `src/oss/langchain/`, `src/oss/langgraph/`, `src/oss/deepagents/` → Shared frameworks with conditional fences

**Framework directories (shared, language-split by fences):**
- `src/oss/langchain/` → Mapped to Build tab "LangChain" in both Python and TypeScript dropdowns
- `src/oss/langgraph/` → Mapped to Build tab "LangGraph" in both Python and TypeScript dropdowns
- `src/oss/deepagents/` → Mapped to Build tab "Deep Agents" in both Python and TypeScript dropdowns

### Exception: Flat (non-language-split) OSS directories

Two OSS sections ship unversioned at single URL paths with conditional fences resolving against the Python branch:

1. **OpenWiki** (`src/oss/openwiki/`)
   - URL: `/oss/openwiki/...`
   - Navigation: Build tab → Learn (conceptual content group)
   - Used for: Architecture, operations, and CLI reference documentation

2. **Deep Agents Code** (`src/oss/deepagents/code/`)
   - URL: `/oss/deepagents/code/...`
   - Navigation: Products and Setup menu → "Deep Agents Code" item
   - Used for: Implementation and configuration reference

### Shared OSS content sections

| Directory | Purpose | Navigation location | URL pattern |
|-----------|---------|-------------------|-------------|
| `src/oss/concepts/` | Conceptual overviews (products, memory, context) | Build → Learn → Conceptual overviews | `/oss/{python,javascript}/concepts/...` |
| `src/oss/learn.mdx` | Learn tab overview/index | Build → Learn | `/oss/{python,javascript}/learn` |
| `src/oss/integrations/` | Shared integration reference content | Build → Integrations (shared) | `/oss/integrations/...` |
| `src/oss/reference/` | API reference entry pages (link to reference.langchain.com) | Build → Reference | `/oss/{python,javascript}/reference/...` |
| `src/oss/contributing/` | Contribution guides | Build → Contribute | `/oss/{python,javascript}/contributing/...` |
| `src/oss/release-policy.mdx`, `src/oss/security-policy.mdx`, `src/oss/versioning.mdx` | Release and security policy pages | Build → Reference | `/oss/{python,javascript}/...` |
| `src/oss/common-errors.mdx` | Error reference | Build → Reference | `/oss/{python,javascript}/common-errors` |

### Integrations structure

- **Python integrations:** `src/oss/python/integrations/` → `/oss/python/integrations/...`
- **TypeScript integrations:** `src/oss/javascript/integrations/` → `/oss/javascript/integrations/...`
- **Groups:** Popular Providers, Integrations by component (language-specific grouping)

### Version-specific release and migration content

- **Python releases:** `src/oss/python/releases/` → `/oss/python/releases/...`
- **Python migrations:** `src/oss/python/migrate/` → `/oss/python/migrate/...`
- **TypeScript releases:** `src/oss/javascript/releases/` → `/oss/javascript/releases/...`
- **TypeScript migrations:** `src/oss/javascript/migrate/` → `/oss/javascript/migrate/...`

## Reusable snippet library

**Path:** `src/snippets/`

Snippets are partial MDX files that are imported into multiple pages, providing code examples, configuration blocks, or shared explanatory content. Snippets undergo special link preprocessing; when writing links in snippets, use careful path segments to ensure correct resolution when imported into pages at varying depths.

| Directory | Purpose | Consumer sections |
|-----------|---------|------------------|
| `src/snippets/langsmith/` | LangSmith-specific code examples and patterns | Test, Deploy, Monitor tabs |
| `src/snippets/oss/` | OSS framework examples and patterns | Build tab tabs (LangChain, LangGraph, Deep Agents) |
| `src/snippets/code-samples/` | Embedded testable code samples | Various pages |

Examples:
- `src/snippets/chat-model-tabs.mdx` – Chat model initialization examples (Python + TypeScript)
- `src/snippets/embeddings-tabs-py.mdx` – Embeddings API examples
- `src/snippets/deepagents-sandbox-basic-py.mdx` – Deep Agents sandbox setup

## Managed Deep Agents special routing

Files named `managed-deep-agents*.mdx` in `src/langsmith/` are treated specially:
- They generate language-prefixed routes: `/langsmith/python/managed-deep-agents-...` and `/langsmith/javascript/managed-deep-agents-...`
- They appear in the Build tab "Managed Deep Agents" (with language dropdown)
- Unversioned URLs like `/langsmith/managed-deep-agents-overview` redirect to the Python routes via `src/docs.json` configuration

Example files:
- `src/langsmith/managed-deep-agents-overview.mdx` → `/langsmith/python/managed-deep-agents-overview` and `/langsmith/javascript/managed-deep-agents-overview`

## Navigation control: /src/docs.json

The `src/docs.json` file is the Mintlify configuration and navigation specification. It:

1. **Defines site configuration:** Theme, colors, fonts, favicon, header/footer links, navbar
2. **Specifies navigation structure:** Products → menu items → tabs → groups → pages
3. **Controls URL routing:** Maps page entries to source file paths
4. **Configures OpenAPI specs:** Registers OpenAPI-generated reference sections
5. **Redirects:** Manages URL redirects for unversioned paths (e.g., managed-deep-agents unversioned → Python versioned)

**Critical invariant:** When adding, moving, or removing pages, you must update `src/docs.json` to reflect the change in navigation and URL routing. Pages not referenced in `docs.json` will not appear in the site navigation or be properly routed, even if the source file exists.

## Two-way relationship: URLs and directory structure

**Directory structure → URLs (enforced by Mintlify):**
- File paths determine default URL slugs
- `/src/oss/langchain/install.mdx` → `/oss/langchain/install` (or with language prefix if language-split)
- Language-specific directories use the language in the URL path

**Navigation structure → URL visibility (via docs.json):**
- `docs.json` determines which pages appear in navigation and tabs
- A page can exist on the filesystem but be invisible if not listed in `docs.json`
- `docs.json` redirects map unversioned URLs to versioned ones (e.g., Fleet's managed-deep-agents)

**Result:** You cannot achieve a URL structure that contradicts the filesystem layout. Navigation labels in `docs.json` may diverge from directory names (e.g., "No-code agents" ← `fleet/`), but the URL path structure follows directory names.

## Content organization patterns

### LangSmith content (setup, observability, deployment)
All content lives flat in `/src/langsmith/` with no subdirectories except:
- `/src/langsmith/fleet/` – No-code agents documentation
- `/src/langsmith/images/` – LangSmith-specific images

Files are named descriptively by topic:
- `observability*.mdx`, `trace-*.mdx` → Monitor menu
- `deployment*.mdx`, `deploy-*.mdx` → Deploy menu
- `evaluation*.mdx`, `dataset*.mdx` → Test menu
- `administration*.mdx`, `user-management.mdx` → LangSmith setup → Govern tab
- `self-host*.mdx` → LangSmith setup → Self-hosted tab

### OSS content (frameworks and integrations)
Organized by framework and language:
- `/src/oss/langchain/` – LangChain-specific pages
- `/src/oss/langgraph/` – LangGraph-specific pages
- `/src/oss/deepagents/` – Deep Agents-specific pages
- `/src/oss/python/` – Python-specific implementations
- `/src/oss/javascript/` – TypeScript-specific implementations
- `/src/oss/concepts/` – Conceptual overviews
- `/src/oss/contributing/` – Contribution documentation

### URL and navigation mismatch reference

| Source directory | Navigation label | URL segment |
|---|---|---|
| `src/langsmith/fleet/` | "No-code agents" | `/langsmith/fleet/` |
| `src/oss/openwiki/` | "OpenWiki" (under Learn) | `/oss/openwiki/` |
| `src/oss/deepagents/code/` | "Deep Agents Code" | `/oss/deepagents/code/` |
| `src/langsmith/managed-deep-agents*.mdx` | "Managed Deep Agents" tab | `/langsmith/{python,javascript}/managed-deep-agents-...` |

## Adding and moving pages

When adding or moving pages:

1. **Create/move the source file** in the appropriate `/src/` directory
2. **Add an entry in `src/docs.json`** under the correct product → menu item → tab → group
3. **Use language-specific directory structure** if content is language-split (`src/oss/python/`, `src/oss/javascript/`)
4. **Use unversioned paths** if content is shared (`src/oss/openwiki/`, `src/oss/deepagents/code/`)
5. **Run the build** (`make dev` or `make build`) to validate routing
6. **Test links** to ensure conditional fences and cross-references resolve correctly

For detailed procedures, see [adding-pages.md](/openwiki/operations/adding-pages.md).

## Code generation and OpenAPI specs

Three OpenAPI-generated reference sections exist; their specs and generated routes are tracked in `src/docs.json`:

| Section | Spec source | Generated directory | Controlled by |
|---------|-------------|-------------------|--------------|
| Agent Server API | `src/langsmith/agent-server-openapi.json` | `/langsmith/agent-server-api/` | Deploy → Get started → Reference group |
| Control Plane API | Remote: `https://api.host.langchain.com/openapi.json` | `/api-reference/` | Deploy → Get started → Reference group |
| LangSmith REST API | `src/langsmith/langsmith-platform-openapi.json` | `/langsmith/smith-api/` | Monitor → Reference tab |

- `langsmith-platform-openapi.json` is refreshed daily by a GitHub Actions workflow and is not edited by hand
- `agent-server-openapi.json` is updated by PRs from the langgraph-api repository
- Both specs can be validated with `make check-openapi`

See [build-system.md](/openwiki/architecture/build-system.md) for details on the preprocessing pipeline.

## Summary of directory-to-navigation mappings

```
/src/
├── index.mdx                         → AGENT DEVELOPMENT LIFECYCLE → Home
├── build-overview.mdx                → Build → Overview tab
├── docs.json                         → Navigation and routing control (all pages)
├── style.css                         → Global styles
├── images/                           → Shared image assets
├── fonts/                            → Web fonts
├── snippets/                         → Reusable MDX content
├── langsmith/                        → Test, Deploy, Monitor, Setup menu items (flat files)
│   ├── fleet/                        → Products and Setup → No-code agents
│   ├── managed-deep-agents*.mdx      → Build → Managed Deep Agents tab (language-prefixed routes)
│   ├── llm-gateway*.mdx              → Products and Setup → LLM Gateway
│   ├── engine*.mdx                   → Products and Setup → Engine
│   └── images/                       → LangSmith-specific images
├── oss/
│   ├── langchain/                    → Build → LangChain tab (language-split)
│   ├── langgraph/                    → Build → LangGraph tab (language-split)
│   ├── deepagents/                   → Build → Deep Agents tab (language-split)
│   │   └── code/                     → Products and Setup → Deep Agents Code (unversioned)
│   ├── openwiki/                     → Build → OpenWiki tab / Learn (unversioned)
│   ├── concepts/                     → Build → Learn → Conceptual overviews (language-split)
│   ├── learn.mdx                     → Build → Learn overview (language-split)
│   ├── reference/                    → Build → Reference tab (language-split)
│   ├── contributing/                 → Build → Contribute tab (language-split)
│   ├── python/
│   │   ├── integrations/             → Build → Integrations tab
│   │   ├── releases/                 → Build → Reference → Releases
│   │   └── migrate/                  → Build → Reference → Migration guides
│   ├── javascript/
│   │   ├── integrations/             → Build → Integrations tab
│   │   ├── releases/                 → Build → Reference → Releases
│   │   └── migrate/                  → Build → Reference → Migration guides
│   └── images/                       → OSS-specific images
```
