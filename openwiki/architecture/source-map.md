---
type: architectural reference
title: Source, Navigation, and Output Map
description: How authored documentation, snippets, assets, OpenAPI inputs, and Mintlify configuration flow from src through preprocessing into versioned and unversioned documentation routes.
tags: [documentation, build, navigation, source-map, architecture]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-06T08:18:19.246Z
sources:
  - id: openwiki-source-5153f86e64d6ee0b305f72b3
    resource: repo://.github/workflows/refresh-langsmith-openapi.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
generated: { by: "openwiki/0.4.3", at: "2026-09-06T08:18:19.246Z" }
---

## Purpose and ownership

`src/` is the authored documentation tree for `docs.langchain.com`; `build/` is regenerated output that Mintlify deploys. Do not edit `build/`. The Python pipeline owns the transformation from source to output, while `src/docs.json` owns the Mintlify site settings, navigation tree, OpenAPI registrations, and redirect table. Consequently, a safe content change that adds, moves, or retires a page updates both its source path and the corresponding `docs.json` entry or redirect in the same change.

The important distinction is **source location versus site placement**. A source directory gives the builder a route shape, but navigation labels and placement come from `docs.json`. For example, `src/langsmith/fleet/` retains `langsmith/fleet` routes while appearing as **No-code agents**.

## Build boundary and route derivation

`DocumentationBuilder.build_all()` clears `build/`, emits the Python and JavaScript OSS trees, emits the two unversioned OSS products, emits LangSmith content, emits special Managed Deep Agents variants, then copies shared files and generates the `llms.txt` outputs. MDX processing applies the normal preprocessors, selects language fences, rewrites relevant links and snippet imports, and adds source-edit links to ordinary source pages. It accepts a bounded set of documentation, asset, configuration, and font extensions; `TEMPLATE.mdx` and unsupported files are skipped.

| Authored input | Build output and behavior |
| --- | --- |
| `src/oss/` shared framework and common content | Processed twice into `build/oss/python/…` and `build/oss/javascript/…`. `:::python` and `:::js` select the matching branch. |
| `src/oss/python/` and `src/oss/javascript/` | Included only in their matching language build, with the language source-directory segment removed from the emitted path. |
| `src/langsmith/` | Emitted once under `build/langsmith/…`, processed with the Python branch for conditional content. |
| `src/langsmith/managed-deep-agents*.mdx` | Exception: emitted only as `build/langsmith/python/…` and `build/langsmith/javascript/…`; no unversioned page is created. |
| `src/oss/openwiki/` and `src/oss/deepagents/code/` | Exceptions: each is emitted once at its unversioned `build/oss/…` path and uses the Python conditional branch. |
| Root pages, `docs.json`, `snippets/`, images, fonts, `.well-known`, CSS, and JavaScript | Shared rather than language-duplicated. Snippets have additional language-specific copies for versioned consumers. |

For a normal shared OSS source such as `src/oss/langchain/mcp/index.mdx`, the output route is `/oss/python/langchain/mcp/` or `/oss/javascript/langchain/mcp/`. In-page absolute `/oss/` links are rewritten to the current language unless they already name a language, point to images, or target the unversioned OpenWiki or Deep Agents Code paths. This keeps a shared source’s internal links within the selected documentation version.

The builder only walks regular files that resolve under the intended source root; it skips symlinks. This is a security boundary: a repository symlink must not cause host files to be copied into published output.

## Navigation is a separate contract

`docs.json` uses two products and nested `menu` items, tabs or language dropdowns, groups, and page identifiers. The identifiers name **built** routes, so its OSS entries include `oss/python/…` and `oss/javascript/…` even though many authored files live in the shared `src/oss/` tree. The configuration also provides public compatibility routes through `redirects`; filesystem-derived output alone is not the full URL contract.

### Agent Development Lifecycle

The first product has **Home**, **Build**, **Test**, **Deploy**, and **Monitor**.

- **Home** is `src/index.mdx` at `/`.
- **Build** has Python and TypeScript dropdowns, each with ten tabs: Overview, Deep Agents, Managed Deep Agents, LangChain, LangGraph, OpenWiki, Integrations, Learn, Reference, and Contribute. It combines root, OSS, and Managed Deep Agents sources rather than matching one source directory.
- **Test**, **Deploy**, and **Monitor** are unversioned `/langsmith/…` routes. Their pages are predominantly flat files in `src/langsmith/`, organized in navigation by function rather than by a matching directory hierarchy.
- Deploy’s **Reference** group declares Agent Server API and Control Plane API; Monitor’s **Reference** tab declares LangSmith REST API.

### Products and Setup

The second product contains **LangSmith setup**, **LLM Gateway**, **No-code agents**, **Engine**, and **Deep Agents Code**. LangSmith setup has six tabs (Overview, Account, Cloud, BYOC, Self-hosted, Govern). The remaining menu items are flat page/group lists. The relevant source-to-navigation exceptions are:

| Source | Navigation label | Published route family |
| --- | --- | --- |
| `src/langsmith/fleet/` | No-code agents | `/langsmith/fleet/…` |
| `src/langsmith/llm-gateway*.mdx` | LLM Gateway | `/langsmith/llm-gateway…` |
| `src/langsmith/engine*.mdx` | Engine | `/langsmith/engine…` |
| `src/oss/deepagents/code/` | Deep Agents Code | `/oss/deepagents/code/…` |

Do not infer the nav destination merely from a filename or source directory: locate its intended product/menu/tab/group in `docs.json`, then use the built identifier appropriate for that section.

## Versioned and unversioned OSS content

Most OSS documentation is authored once in shared framework directories—`src/oss/langchain/`, `src/oss/langgraph/`, and `src/oss/deepagents/`—or in common directories such as `concepts/`, `reference/`, and `contributing/`; it is emitted into both language trees. Language-specific material instead resides in `src/oss/python/` or `src/oss/javascript/`, especially integrations, releases, and migration guides.

Two products deliberately do not participate in that split:

1. **OpenWiki**: `src/oss/openwiki/` publishes at `/oss/openwiki/…` and appears as the OpenWiki Build tab.
2. **Deep Agents Code**: `src/oss/deepagents/code/` publishes at `/oss/deepagents/code/…` and appears under Products and Setup.

Both build against Python conditional content and retain unprefixed links to their own route family. A link from either product to ordinary shared OSS content becomes a Python URL, for example `/oss/python/deepagents/quickstart`. Redirects also preserve older language-prefixed Deep Agents CLI/Code URLs by forwarding them to the unversioned Deep Agents Code routes.

Managed Deep Agents is the inverse exception: its sources live under `src/langsmith/`, but its output is language-prefixed. `managed-deep-agents*.mdx` is built for both targets; links to an unversioned Managed Deep Agents URL are rewritten to the current variant during build. `docs.json` redirects legacy unversioned URLs to the Python variant, so no orphaned unversioned output is served.

## Reusable snippets and assets

`src/snippets/` holds reusable MDX and local JSX/TSX components. Snippets are imported into pages rather than treated as ordinary final pages, so the builder does not append the standard source footer to them. For versioned pages, ordinary absolute MDX imports from `/snippets/…` are rewritten to `/snippets/python/…` or `/snippets/javascript/…`; the matching copies ensure nested consumers resolve their imports and language-sensitive links correctly. Write absolute links in snippets carefully—relative paths can resolve differently for consumers at different depths.

Shared presentation resources include `src/images/` (with `brand/` and `providers/`), `src/fonts/`, and `src/style.css`; `docs.json` references these with site-root paths such as `/images/…`, `/fonts/…`, and `/style.css`. The builder copies these shared resources without OSS language duplication.

## OpenAPI inputs and generated references

Mintlify generates operation pages for the OpenAPI registrations in `docs.json`; they are not authored as MDX files. The three registrations are:

| Section | Spec source | Generated route directory | Navigation location |
| --- | --- | --- | --- |
| Agent Server API | `src/langsmith/agent-server-openapi.json` | `/langsmith/agent-server-api/` | Deploy → Get started → Reference |
| Control Plane API | `https://api.host.langchain.com/openapi.json` | `/api-reference/` | Deploy → Get started → Reference |
| LangSmith REST API | `src/langsmith/langsmith-platform-openapi.json` | `/langsmith/smith-api/` | Monitor → Reference |

The committed LangSmith platform spec identifies the LangSmith API and its `X-Api-Key` authentication requirement. Its refresh workflow runs daily, invokes `scripts/process_langsmith_openapi.py --write`, and opens or updates one standing refresh PR; do not hand-edit the generated spec. `make check-openapi` validates the Agent Server spec after a build. Since Mintlify creates OpenAPI endpoint pages at deploy time rather than as local MDX output, the broken-link workflow filters those expected local false positives.

## Change and verification procedure

1. Put authored MDX and supporting files in the source location that matches their build semantics—not merely the desired sidebar label.
2. Add or update the correct `docs.json` page identifier under the intended product/menu/tab/group. Use an OpenAPI block rather than fictitious MDX endpoint pages for generated API reference.
3. For shared OSS MDX, author both language branches with `:::python` and `:::js` as needed; put language-exclusive pages in the matching `src/oss/python/` or `src/oss/javascript/` tree. Do not move OpenWiki or Deep Agents Code into those trees.
4. When moving or replacing a public page, preserve public URLs with a `docs.json` redirect. Managed Deep Agents requires language-prefixed destination routes.
5. Run `make build` (or `make dev`) to regenerate and inspect `build/`; use `make broken-links` for built-link validation. Use `make check-openapi` after relevant spec changes and targeted builder tests for route/link-rewrite changes.

Focused regression coverage in `tests/unit_tests/test_builder.py` verifies dual-language output, the two unversioned exceptions, language-aware link and snippet rewriting, Managed Deep Agents routes, and symlink rejection. These tests are the primary guardrails when changing the source-to-output mapping.

For preprocessing mechanics, see [Preprocessing](/openwiki/concepts/preprocessing.md); for language versions, see [Versioning](/openwiki/concepts/versioning.md); for page placement, see [Adding pages](/openwiki/operations/adding-pages.md); and for sample ownership, see [Code samples](/openwiki/workflows/code-samples.md).
