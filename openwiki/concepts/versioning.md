---
type: documentation route model
title: Documentation Routes and Language Versioning
description: Explains how source ownership, docs.json navigation, and preprocessing determine generated documentation routes and language variants. Covers shared OSS eligibility, unversioned products, Managed Deep Agents, redirects, and language switching.
tags: [documentation-pipeline, routes, language-versioning, redirects]
verified:
  - by: openwiki/0.4.3
    at: 2026-11-03T08:13:57.434Z
sources:
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-da820a9dbbf8f16f1502a5c0
    resource: repo://src/langsmith/agent-registry.mdx
  - id: openwiki-source-8f9788c0e6c9b97da9716e3a
    resource: repo://src/langsmith/managed-deep-agents-quickstart.mdx
  - id: openwiki-source-17cda5e480a486a133aa3e81
    resource: repo://src/langsmith/managed-deep-agents-runtime.mdx
  - id: openwiki-source-243c6e17a513bece229a34b9
    resource: repo://src/language-toggle.js
  - id: openwiki-source-838cde2da1a05c117501b824
    resource: repo://src/oss/deepagents/async-subagents.mdx
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
  - id: openwiki-source-f260e53bc2ed7f10cc38d28f
    resource: repo://tests/unit_tests/test_conditional_fences.py
generated: { by: "openwiki/0.4.3", at: "2026-11-03T08:13:57.434Z" }
---

# Documentation Routes and Language Versioning

`DocumentationBuilder` turns `src/` into the disposable `build/` tree. Source ownership establishes a page's route family; `src/docs.json` supplies reader navigation and redirects and additionally selects the output-language set for **shared OSS Markdown**. It is copied as a shared file and does not itself emit a page.

Do not conflate these separate contracts:

1. **Source family** determines route shape and the preprocessing target.
2. **Navigation** controls where readers find a route and, only for shared OSS Markdown, can select a single emitted language.
3. **Redirects** preserve retired public URLs. They neither create artifacts nor assign source ownership.
4. **The language switcher** is client-side navigation between recognized route prefixes. It neither verifies artifacts nor creates them.
5. **A route language is not a package-version claim.** `/oss/python/` and `/oss/javascript/` identify the output target. Dependency versions, compatibility, and package release policy require separate evidence.

Source placement alone is therefore insufficient evidence for a public route: confirm that the builder emits it and that `docs.json` navigates to it or redirects to it as intended.

## Route decision model

```mermaid
flowchart TD
    Source["Authored source under src"] --> Family{"Source family"}
    Family --> Shared["Shared OSS Markdown"]
    Shared --> Nav{"Listed in exactly one OSS navigation"}
    Nav -->|"Yes"| OneShared["Emit one matching OSS route"]
    Nav -->|"No"| BothShared["Emit Python and JavaScript routes"]
    Family --> Owned["oss/python or oss/javascript"]
    Owned --> OwnedRoute["Emit matching route without ownership segment"]
    Family --> Product["OpenWiki or Deep Agents Code"]
    Product --> PlainProduct["Emit one unprefixed OSS product route"]
    Family --> Ordinary["Ordinary LangSmith"]
    Ordinary --> PlainLangSmith["Emit one unprefixed LangSmith route"]
    Family --> Managed["Direct Managed Deep Agents MDX"]
    Managed --> ManagedRoutes["Emit Python and JavaScript LangSmith routes"]
```

The builder's source-family and navigation decision. Navigation selects a shared-OSS language set; elsewhere it projects existing routes into menus and supplies redirects.

| Authored source family | Full-build output | Rendering target |
| --- | --- | --- |
| Shared `src/oss/` Markdown, excluding special and owned trees | One or both of `/oss/python/...` and `/oss/javascript/...` | `python` and/or `js` |
| `src/oss/python/...` | `/oss/python/...`, removing `python/` from the source remainder | `python` |
| `src/oss/javascript/...` | `/oss/javascript/...`, removing `javascript/` from the source remainder | `js` |
| `src/oss/deepagents/code/...` | `/oss/deepagents/code/...` | `python` |
| `src/oss/openwiki/...` | `/oss/openwiki/...` | `python` |
| Ordinary `src/langsmith/...` | `/langsmith/...` | `python` |
| Direct `src/langsmith/managed-deep-agents*.mdx` | `/langsmith/python/...` and `/langsmith/javascript/...` | `python` and `js` |

### Shared OSS navigation selection

For shared `.md` and `.mdx` pages, the builder recursively collects `/oss/python/...` and `/oss/javascript/...` navigation routes from `docs.json`, caching them until the file modification time changes. A page listed in exactly one language emits only that variant. A page listed in both languages—or neither—emits both. Non-Markdown shared files always emit for both targets.

A directory navigation entry can mean `dir/index`, but cannot select that shared index for a language when `src/oss/<language>/dir.mdx` or `.md` owns the corresponding directory route. Language-owned directories are ownership boundaries, not full-build menu controls: their files emit only into their matching tree with the ownership segment removed. If `docs.json` is absent or invalid, the safe fallback is both shared-OSS variants.

`build_all()` recreates `build/`, emits ordinary OSS variants, both unversioned OSS products, ordinary LangSmith, Managed Deep Agents variants, shared files, and npm snippets. Source collection skips symlinks and files resolving outside the requested root, so source-tree links cannot place host files in build artifacts.

## Conditional content and transformations

Shared sources may contain `:::python` and `:::js` blocks. For the selected target, a closed matching block contributes its content without fences and a closed nonmatching supported block is removed. Escaped `\:::` becomes literal `:::`. Unsupported labels are retained by the renderer, but all conditional-looking fences are structurally validated first.

Broken fences fail preprocessing with `ValueError`: nested opens, stray closes, and unclosed blocks are rejected with line-specific diagnostics. A closer may carry following text, including a compact close-and-open form. The renderer remains a whole-document regular-expression transform rather than a code-fence-aware Markdown parser, so authors should keep blocks balanced and non-nested and escape a marker that must be displayed literally.

For Markdown and MDX the transformation order is:

1. Resolve `@[]` autolinks using the target as the default scope.
2. Add UTM parameters to LangSmith CTA links.
3. Validate and apply conditional rendering.
4. Scope eligible snippet imports to the target language.
5. Rewrite eligible OSS links, then Managed Deep Agents links.

The internal `js` target maps to the `javascript` URL segment. A `.md` source writes an `.mdx` artifact.

### Links and snippets

Eligible absolute `/oss/...` Markdown destinations and quoted `href` values gain `/oss/python/` or `/oss/javascript/`. Image paths, already-prefixed routes, and `/oss/deepagents/code` and `/oss/openwiki` routes remain unchanged. Thus an unversioned product or ordinary LangSmith page rendered with the Python target defaults ordinary OSS links to Python without prefixing a link back into an unversioned product.

Bare Managed Deep Agents links are rewritten to the current target; an already-prefixed link remains pinned. Shared Markdown snippets have Python and JavaScript copies under `build/snippets/python/` and `build/snippets/javascript/`, each conditionally rendered with absolute rewritten links. Language-targeted pages import those copies; already scoped imports remain unchanged. The original snippet path is a Python-targeted default for unversioned consumers.

## Unversioned products and Managed Deep Agents

Deep Agents Code and OpenWiki are explicit OSS exceptions. Each emits once under `/oss/deepagents/code/...` or `/oss/openwiki/...`; Python conditional selection affects content but does not create a Python URL. OSS link rewriting preserves these families while prefixing eligible ordinary OSS links.

Both Python and TypeScript Build dropdowns project the same unprefixed OpenWiki routes. The switcher hides its dropdown on `/oss/openwiki` and descendants. Deep Agents Code is likewise unversioned; `docs.json` retains compatibility redirects from former Python and JavaScript Code roots and wildcard descendants to the unprefixed Code family. These provisions preserve URLs, not content artifacts.

Ordinary LangSmith files emit once below `/langsmith/` using the Python target. Managed Deep Agents is the exception: a direct top-level `managed-deep-agents*.md` or `.mdx` file is recognized by a single-file build and emits both language variants; the ordinary LangSmith pass excludes it. The full-build variant pass discovers only direct `.mdx` files, so a page intended for full-build discovery must be direct and use `.mdx`.

`docs.json` projects parallel Python and TypeScript Managed Deep Agents tabs. Both contain beta-tagged **Get started**, **Agent capabilities**, and **Build and deploy** groups; the capability list includes Identity and a nested Channels group, while the deployment list includes Custom frontend. The current quickstart demonstrates why two outputs are needed: its `mda init` commands differ by target. The runtime page also uses language fences for native type names and its absent-sandbox value. Unversioned overview aliases and listed unversioned per-page URLs redirect to Python; that default does not remove JavaScript artifacts.

For example, the shared Async subagents source carries Python and JavaScript conditional content and is listed under Delegation in both language projections. It is one source intentionally rendered as a route pair, not two independently authored pages.

Agent Registry is not a versioned counterpart of Managed Deep Agents. It is an ordinary `/langsmith/agent-registry` page in **Products and setup → LangSmith setup → Agent-based workspaces**, alongside environments, navigation, creation, UI building, and deployment. It describes an organization-wide registry and stable agent identifiers and environments rather than a language-specific package route.

## Reader language selection

The language-toggle script recognizes only `/oss/python/` ↔ `/oss/javascript/` and `/langsmith/python/` ↔ `/langsmith/javascript/`. On a Python, TypeScript, or JavaScript selection it records the current path, hash, intended target, and timestamp in `sessionStorage`. If a counterpart prefix is computable, the capture-phase click handler navigates directly and preserves the hash; otherwise the pending record can survive the menu's reload and is considered on the next navigation.

Pending switches expire after eight seconds and are consumed at most once. An unprefixed page has no computed counterpart, so Mintlify's landing-page navigation remains in control. The selector does not prove that a paired artifact exists: validate generated artifacts, navigation references, and redirects independently.

## Change and verify safely

1. Choose source ownership before editing navigation. Use `oss/python` or `oss/javascript` for intrinsically SDK-specific pages. Use shared OSS plus language navigation membership only when one shared source needs selective output.
2. Update both navigation projections for a paired route. For an unversioned product, intentionally reference its unprefixed route in each relevant projection. Keep package versions and support statements in their own versioned-content evidence rather than deriving them from a route.
3. Add redirects only for externally supported or retired URLs, and point each at an emitted route. A redirect cannot substitute for creating an artifact.
4. Keep conditional fences balanced, non-nested, and escaped when literal. Treat a preprocessing `ValueError` as an authoring error rather than expecting a partial artifact.
5. Run a clean full build. Assert required artifacts and prohibited sibling artifacts, especially for single-language shared pages, unversioned products, and Managed Deep Agents pages.
6. Inspect both target outputs for fenced content, scoped snippet imports, OSS links, and Managed Deep Agents links. Run `make broken-links-with-anchors`; after changing `@[]` references, run `make check-cross-refs`.
7. Extend focused builder tests for source classification, navigation-derived selection, transformations, and route shape. Test switcher changes separately for both prefix pairs, hash preservation, reload fallback, expiry, and unversioned exceptions.

## See also

- [Build system](/openwiki/architecture/build-system.md)
- [Preprocessing](/openwiki/concepts/preprocessing.md)
- [Mintlify integration](/openwiki/integrations/mintlify.md)
- [Adding pages](/openwiki/operations/adding-pages.md)
- [Changing versioned content](/openwiki/workflows/versioned-content.md)
