---
type: architectural reference
title: Source Directory Map
description: Authoritative map of authored documentation domains to Mintlify navigation, generated routes, language variants, shared snippets and assets, and OpenAPI-backed reference sections.
tags: [documentation, build, navigation, source-map, mintlify]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-07T08:24:09.165Z
sources:
  - id: openwiki-source-5153f86e64d6ee0b305f72b3
    resource: repo://.github/workflows/refresh-langsmith-openapi.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-697851c98229599f97376bfb
    resource: repo://scripts/process_langsmith_openapi.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
generated: { by: "openwiki/0.4.3", at: "2026-09-07T08:24:09.165Z" }
---

## Scope and source of truth

`src/` is the authored documentation tree for `docs.langchain.com`; `build/` is disposable preprocessed output that Mintlify deploys. Edit source files and regenerate the output—never patch `build/`.

`src/docs.json` is the authoritative navigation specification. Its page strings are extensionless paths in the **generated** tree (for example, `oss/python/langchain/mcp/index`), while its nested products, menu items, dropdowns, tabs, and groups determine where those routes appear. Therefore, a source directory is useful for locating content, but it is not a substitute for checking `docs.json` before adding, moving, or removing a page.

The distinction matters because names deliberately diverge: `src/langsmith/fleet/` is presented as **No-code agents**, and the Build menu combines OSS and LangSmith routes.

## Route generation model

```text
src MDX, assets, docs.json
          |
          v
DocumentationBuilder preprocesses and copies files
          |
          +-- OSS shared sources --> build/oss/python/... and build/oss/javascript/...
          +-- OSS language folders --> matching language tree only
          +-- OpenWiki and Deep Agents Code --> unversioned OSS routes
          +-- LangSmith --> build/langsmith/...
          +-- Managed Deep Agents --> build/langsmith/python/... and .../javascript/...
          +-- shared assets, snippets, docs.json --> copied shared locations
          |
          v
Mintlify reads build/docs.json for navigation, redirects, and OpenAPI sections
```

The builder first replaces `build/`, then emits Python and JavaScript OSS variants, the two unversioned OSS products, ordinary LangSmith content, Managed Deep Agents variants, and shared files. MDX is preprocessed before it is written: language fences are resolved for the target, unqualified `/oss/` links acquire the target language prefix, and unversioned product links remain unprefixed. This makes a route a build artifact rather than a direct promise that every source path has the same URL.

### Language-versioned OSS

Most files below `src/oss/` are emitted twice:

| Authored location | Generated route family | Use it for |
| --- | --- | --- |
| `src/oss/langchain/` | `/oss/python/langchain/...`, `/oss/javascript/langchain/...` | Shared LangChain documentation; use `:::python` and `:::js` fences where content differs. |
| `src/oss/langgraph/` | `/oss/python/langgraph/...`, `/oss/javascript/langgraph/...` | Shared LangGraph documentation. |
| `src/oss/deepagents/` except `code/` | `/oss/python/deepagents/...`, `/oss/javascript/deepagents/...` | Shared Deep Agents documentation. |
| `src/oss/python/` | `/oss/python/...` only | Python-only integrations, migrations, releases, and related pages. |
| `src/oss/javascript/` | `/oss/javascript/...` only | TypeScript-only integrations, migrations, releases, and related pages. |
| Other versioned OSS material such as `concepts/`, `reference/`, `contributing/`, `learn.mdx`, policies, and common errors | Both `/oss/python/...` and `/oss/javascript/...` | Content shared by the two Build dropdowns. |

For example, `src/oss/langchain/mcp/index.mdx` is authored once but is listed in the Python Build navigation as `oss/python/langchain/mcp/index`; the same builder rule makes a JavaScript variant. Do not hard-code an unprefixed `/oss/langchain/...` link in a versioned page and assume it remains unprefixed—preprocessing selects the route appropriate to that output variant.

Two OSS subtrees are explicit exceptions: `src/oss/openwiki/` builds once at `/oss/openwiki/...`, and `src/oss/deepagents/code/` builds once at `/oss/deepagents/code/...`. Both are preprocessed with the Python fence branch; links to these unversioned roots are deliberately excluded from `/oss/` language-prefix rewriting.

### LangSmith and Managed Deep Agents

Ordinary `src/langsmith/` files, including `fleet/`, build at `/langsmith/...` with the Python fence branch. The navigation, rather than a flat filename convention, places these pages in Test, Deploy, Monitor, LangSmith setup, LLM Gateway, Engine, or No-code agents.

`managed-deep-agents*.mdx` directly under `src/langsmith/` are a special case. They are excluded from ordinary LangSmith output and generated twice at `/langsmith/python/managed-deep-agents-...` and `/langsmith/javascript/managed-deep-agents-...`. The builder also rewrites unversioned Managed Deep Agents links inside each variant to the matching language route. `docs.json` supplies redirects from legacy/unversioned Managed Deep Agents URLs to the Python routes, preventing orphaned unversioned pages.

### Snippets, assets, and shared files

`src/snippets/` contains reusable MDX and local component content. Snippet files are copied as shared files and also get language-specific processed copies under `build/snippets/python/` and `build/snippets/javascript/`; imports from a versioned page are rewritten to those copies. Snippet links must be written as carefully chosen absolute paths because the snippet can be consumed from pages at different depths. Snippets intentionally do not receive the generated “Edit this page” footer.

Shared site inputs include `src/docs.json`, `src/style.css`, `src/images/` (including `brand/` and dark/light `providers/` variants), and `src/fonts/`. The builder treats images, fonts, snippets, `.well-known` content, JavaScript, and CSS as shared rather than language-duplicated. It only copies supported file types and rejects source symlinks or files resolving outside the source subtree, so a committed link cannot cause arbitrary host files to enter build artifacts.

## Navigation map

The current `docs.json` navigation has two products.

### AGENT DEVELOPMENT LIFECYCLE

| Menu item | Navigation shape | Primary authored domain |
| --- | --- | --- |
| Home | One page | `src/index.mdx` |
| Build | Python and TypeScript dropdowns, each with 10 tabs | `src/oss/`, plus Managed Deep Agents from `src/langsmith/` |
| Test | Six unversioned LangSmith tabs | Flat `src/langsmith/` topic files |
| Deploy | Six unversioned LangSmith tabs | Flat `src/langsmith/` topic files and OpenAPI groups |
| Monitor | Five unversioned LangSmith tabs | Flat `src/langsmith/` topic files and the LangSmith REST API group |

Build's tabs are Overview, Deep Agents, Managed Deep Agents, LangChain, LangGraph, OpenWiki, Integrations, Learn, Reference, and Contribute. The language dropdown route entries—not only the source directory—are what bind a page to Python versus TypeScript. The source summary is:

- `oss/{python,javascript}/integrations/` supplies language-specific Integrations entries.
- `oss/langchain/`, `oss/langgraph/`, and `oss/deepagents/` contribute to their framework tabs and also to Learn where explicitly listed.
- `oss/openwiki/` appears in the unversioned OpenWiki tab in both dropdowns.
- `oss/reference/`, `oss/contributing/`, concepts, policies, releases, and migrations appear under the indicated Build tabs after generation.
- `langsmith/managed-deep-agents*.mdx` supplies the language-prefixed Managed Deep Agents tab and is also linked from each Deep Agents deployment group.

Test, Deploy, and Monitor do not have a language dropdown. Their pages are route strings under `langsmith/`, despite being organized in the UI by product activity rather than by a matching on-disk subdirectory.

### PRODUCTS AND SETUP

| Menu item | Navigation shape | Authored location and route family |
| --- | --- | --- |
| LangSmith setup | Six tabs | Flat `src/langsmith/` files at `/langsmith/...` |
| LLM Gateway | Flat grouped list | `src/langsmith/llm-gateway*.mdx` at `/langsmith/llm-gateway...` |
| No-code agents | Flat grouped list | `src/langsmith/fleet/` at `/langsmith/fleet/...` |
| Engine | Flat list | `src/langsmith/engine*.mdx` at `/langsmith/engine...` |
| Deep Agents Code | Flat list plus Configuration group | `src/oss/deepagents/code/` at `/oss/deepagents/code/...` |

“Fleet” is consequently a source and URL term, not the customer-facing menu label. Conversely, Deep Agents Code resides below a normally versioned framework directory but is intentionally a single unversioned product.

## OpenAPI-backed navigation

Mintlify generates endpoint pages from the OpenAPI declarations in `docs.json`; these pages are not authored as MDX files. Keep the spec path, `directory` where present, and containing navigation group synchronized.

| Section | Nav location | Spec source | Generated route root |
| --- | --- | --- | --- |
| Agent Server API | Deploy → Get started → Reference | `src/langsmith/agent-server-openapi.json` | `/langsmith/agent-server-api/` |
| Control Plane API | Deploy → Get started → Reference | `https://api.host.langchain.com/openapi.json` | `/api-reference/` |
| LangSmith REST API | Monitor → Reference | `src/langsmith/langsmith-platform-openapi.json` | `/langsmith/smith-api/` |

The daily `refresh-langsmith-openapi.yml` workflow runs `scripts/process_langsmith_openapi.py --write` and updates the committed LangSmith platform spec through a standing PR. The script fetches only its allow-listed API host, hides fleet/internal and other excluded operations with `x-hidden`, and adds human-readable group metadata. Do not hand-edit the refreshed spec. `make check-openapi` validates the Agent Server spec after building; local broken-link checks filter deployment-time OpenAPI pages because Mintlify, not the local builder, renders them.

## Safe change procedure

1. Choose the authored domain based on whether the page is shared OSS, language-specific OSS, unversioned OpenWiki/Deep Agents Code, Managed Deep Agents, or ordinary LangSmith content.
2. Add or move the source file, including required MDX frontmatter. For a shared versioned OSS page, use language fences instead of creating output-tree copies.
3. Update the exact `src/docs.json` product → menu item → dropdown or tab → group. Add redirects when moving a public route; source existence alone does not put a page in navigation.
4. For reusable content, add/import a snippet with absolute paths that will survive preprocessing in every consuming route depth.
5. Run `make build` (or `make dev` for a watcher) and inspect the generated route family. Run `make broken-links` for link validation, and `make check-openapi` when changing the Agent Server spec or its declaration.

Focused builder tests cover the exception boundaries that are easiest to regress: language insertion without duplicate prefixes, one-time OpenWiki and Deep Agents Code output, Managed Deep Agents dual routes and rewritten links, language-scoped snippet imports, and symlink containment. When changing routing rules, extend these tests instead of relying only on an output-directory inspection.

See [Build system](/openwiki/architecture/build-system.md) for preprocessing mechanics, [Preprocessing](/openwiki/concepts/preprocessing.md) for authored syntax, [Versioning](/openwiki/concepts/versioning.md) for language variants, [Reference docs](/openwiki/integrations/reference-docs.md) for generated reference ownership, and [Adding pages](/openwiki/operations/adding-pages.md) for contributor workflow details.
