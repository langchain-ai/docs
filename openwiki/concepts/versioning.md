---
type: documentation route model
title: Versioned documentation and routes
description: Explains how the documentation builder turns source families into Python, JavaScript, or unversioned public routes, and how navigation and redirects keep those routes reachable.
tags: [documentation-pipeline, routes, language-versioning, redirects]
sources:
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-243c6e17a513bece229a34b9
    resource: repo://src/language-toggle.js
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
generated: { by: "openwiki/0.4.3", at: "2026-09-24T08:22:38.580Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-09-24T08:22:38.580Z
---

# Versioned documentation and routes

`DocumentationBuilder` derives public documentation routes from source paths under `src/`. It emits language variants where a page is shared by Python and JavaScript readers, and retains a single route where a product is intentionally language-agnostic. `src/docs.json` is a separate contract for navigation and redirects: it must point at emitted routes, but a navigation label does not establish a source file's ownership.

## Choose the source family

| Source family | Output routes | Target used for preprocessing |
| --- | --- | --- |
| Ordinary `src/oss/` content, including LangChain, LangGraph, and Deep Agents outside `code/` | `/oss/python/...` and `/oss/javascript/...` | `python` and `js` respectively |
| `src/oss/python/...` or `src/oss/javascript/...` | Only the matching output family, without the source-language path component | Matching target only |
| `src/oss/deepagents/code/...` | `/oss/deepagents/code/...` | `python` fallback |
| `src/oss/openwiki/...` | `/oss/openwiki/...` | `python` fallback |
| Ordinary `src/langsmith/...` | `/langsmith/...` | `python` fallback |
| Direct `src/langsmith/managed-deep-agents*.mdx` | `/langsmith/python/...` and `/langsmith/javascript/...` | `python` and `js` respectively |

```mermaid
flowchart TD
    Source["Source under src"] --> Family{"Path family"}
    Family --> Oss["Ordinary oss"]
    Oss --> OssPy["oss python route"]
    Oss --> OssJs["oss javascript route"]
    Family --> Product["OpenWiki or Deep Agents Code"]
    Product --> ProductRoute["Unprefixed oss route"]
    Family --> Smith["Ordinary langsmith"]
    Smith --> SmithRoute["Unprefixed langsmith route"]
    Family --> Managed["Managed Deep Agents"]
    Managed --> ManagedPy["langsmith python route"]
    Managed --> ManagedJs["langsmith javascript route"]
    OssPy --> Config["docs.json navigation"]
    OssJs --> Config
    ProductRoute --> Config
    SmithRoute --> Config
    ManagedPy --> Config
    ManagedJs --> Config
```

This diagram shows route branching by source path. Navigation grouping is configured afterwards and must not be used to infer the source family.

## Build lifecycle and routing rules

A full `build_all()` first deletes `build/`, then builds ordinary OSS for Python and JavaScript, the two unversioned OSS products, ordinary LangSmith content, and Managed Deep Agents variants. It then copies shared files and npm snippets and generates the `llms.txt` artifacts. Deleting the output tree is important: a full build cannot leave stale route artifacts behind.

`build_file()` applies the same routing policy to an individual existing file. An ordinary OSS file produces two artifacts, except for the two unversioned product roots. An ordinary LangSmith file builds once, while a Managed Deep Agents file builds twice. Root-level and shared files copy once. Building a missing file is a programming error and raises `AssertionError`.

For ordinary OSS, language-specific source directories are a filter rather than a route segment. During a Python pass, `src/oss/javascript/...` is skipped; during a JavaScript pass, `src/oss/python/...` is skipped. The selected directory name is removed before output, so `src/oss/python/concepts/example.mdx` emits at `/oss/python/concepts/example` rather than a doubled language path.

Ordinary LangSmith documents are emitted once below `/langsmith/`; they are processed with the Python target. This is a preprocessing default, not a statement that every LangSmith page is Python documentation.

## Transform one emitted page

For Markdown and MDX, the builder first runs standard preprocessing. For a language-targeted output, it then scopes Markdown snippet imports, rewrites OSS links, and rewrites Managed Deep Agents links. The builder maps its internal `js` target to `javascript` in public paths. A `.md` input is written as `.mdx`.

```mermaid
flowchart LR
    Input["Markdown or MDX source"] --> Prep["Standard preprocessing"]
    Prep --> Target{"Language target present"}
    Target -->|"yes"| Imports["Scope snippet imports"]
    Target -->|"no"| Output["Write artifact"]
    Imports --> OssLinks["Rewrite oss links"]
    OssLinks --> ManagedLinks["Rewrite Managed Deep Agents links"]
    ManagedLinks --> Output
```

This diagram shows the transform order for a generated Markdown artifact.

Use `:::python` and `:::js` fences only for content that genuinely differs by target. The conditional renderer keeps the matching block content without its fences and removes a nonmatching supported block. Escaped `\:::` becomes literal `:::`, while unsupported labels and unclosed blocks remain unchanged. It uses a regex and is not code-fence-aware, so escape literal conditional markers instead of assuming a Markdown code fence protects them.

An unqualified absolute OSS link such as `/oss/langgraph/overview` becomes `/oss/python/langgraph/overview` or `/oss/javascript/langgraph/overview` in a language-targeted build. The rewrite deliberately skips image URLs, already-prefixed URLs, and the language-agnostic Deep Agents Code and OpenWiki roots. In versioned MDX, an import from `/snippets/component.mdx` is similarly scoped to `/snippets/python/component.mdx` or `/snippets/javascript/component.mdx`; an already scoped import is left intact.

## Keep language-agnostic products unprefixed

Deep Agents Code and OpenWiki are explicit exceptions to the normal OSS split. Each is emitted once at its own unprefixed route root, and the Python branch is used only as the deterministic conditional-rendering fallback. Consequently, links within either root remain unprefixed, while an unqualified link from one of these pages to ordinary OSS is rendered to the Python OSS route.

OpenWiki appears in both the Python and TypeScript Build dropdowns using the same `/oss/openwiki/...` paths. The client-side language toggle hides itself for the OpenWiki route family because no corresponding language variant exists. Deep Agents Code is likewise unversioned at `/oss/deepagents/code/...`, regardless of where its navigation tab appears.

## Publish Managed Deep Agents variants and redirects

Managed Deep Agents is the LangSmith exception. A direct file immediately under `src/langsmith/` whose basename starts with `managed-deep-agents` and whose extension is `.md` or `.mdx` is classified as language-variant content. It does not produce an unversioned page; its Python and JavaScript artifacts receive their own conditional content, language-scoped snippet imports, OSS links, and Managed Deep Agents links.

The full-build discovery pass selects only `managed-deep-agents*.mdx`. Although an individual `.md` file matches the classifier and can be built directly, it is absent from the bulk pass. Use `.mdx` for Managed Deep Agents pages.

`docs.json` supplies separate Managed Deep Agents tabs with Python and JavaScript routes. It also maps current unversioned URLs, such as the overview, quickstart, local-development, and capability pages, plus historical paths, to the Python variants. This preserves inbound links while the generated pages remain only under language-prefixed routes. When adding or moving one of these pages, keep the filename convention, both navigation variants, and needed legacy redirects aligned.

## Verify route changes

The builder regression tests cover the unversioned Deep Agents Code and OpenWiki output and their link behavior, language-scoped snippet imports, and Managed Deep Agents dual output. The Managed Deep Agents fixture verifies target-specific links and conditional snippet content, including that unversioned artifacts are not emitted.

For a route change, edit source content rather than `build/`, choose the source family before adding navigation, and run a full build when removing or moving pages. Then inspect both generated language variants where applicable and check that `docs.json` navigation and redirects name the routes that the builder actually produces.

## See also

- [Source map](/openwiki/architecture/source-map.md)
- [Preprocessing](/openwiki/concepts/preprocessing.md)
- [Adding pages](/openwiki/operations/adding-pages.md)
- [Builder tests](/openwiki/testing/builder-tests.md)
- [Writing versioned content](/openwiki/workflows/versioned-content.md)
