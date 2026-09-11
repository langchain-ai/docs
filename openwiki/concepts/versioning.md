---
type: versioning strategy
title: Language Versioning Strategy
description: How source classification, build-time language rendering, emitted public routes, and docs.json navigation cooperate for shared OSS documentation, intentional unversioned products, and Managed Deep Agents.
tags: [versioning, documentation-pipeline, navigation, routes, conditional-rendering]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-09T08:21:02.265Z
sources:
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
generated: { by: "openwiki/0.4.3", at: "2026-09-09T08:21:02.265Z" }
---

# Language Versioning Strategy

Language versioning is a build and navigation model, not a filesystem naming convention. A source location determines how `DocumentationBuilder` renders a file; that render produces an emitted public route; and `src/docs.json` independently decides which emitted routes appear in Mintlify navigation or redirect from retired routes. Keep these three surfaces distinct and synchronized.

## Source classification and emitted routes

| Authored source domain | Emitted public route family | Navigation consequence |
| --- | --- | --- |
| Most `src/oss/` content, including LangChain, LangGraph, Deep Agents, concepts, reference, and contributing material | `/oss/python/...` and `/oss/javascript/...` | Add the corresponding emitted route under the Python or TypeScript Build dropdown. |
| `src/oss/python/` or `src/oss/javascript/` | Only the matching `/oss/python/...` or `/oss/javascript/...` route, with the source-language directory removed | Put the route only in its matching dropdown. |
| `src/oss/deepagents/code/` | `/oss/deepagents/code/...` | One language-agnostic product route; do not add a language prefix. |
| `src/oss/openwiki/` | `/oss/openwiki/...` | One language-agnostic product route, listed as the same unprefixed routes in both Build dropdowns. |
| Ordinary `src/langsmith/` content | `/langsmith/...` | Place it in its applicable LangSmith or lifecycle navigation group, which is not language-split. |
| A direct `src/langsmith/managed-deep-agents*.mdx` page | `/langsmith/python/...` and `/langsmith/javascript/...` | List each emitted route in the Managed Deep Agents tab of its corresponding Build dropdown. |

For example, `src/oss/langgraph/overview.mdx` emits two artifacts, while `src/oss/python/integrations/chat/example.mdx` participates only in the Python pass and emits as `/oss/python/integrations/chat/example`. Do not make generated source copies merely to resemble an emitted route.

```mermaid
flowchart TD
    Source["Source file under src"] --> Domain{"Classify source domain"}
    Domain --> Oss["Most OSS content"]
    Oss --> Py["Emit oss python route"]
    Oss --> Js["Emit oss javascript route"]
    Domain --> Product["OpenWiki or Deep Agents Code"]
    Product --> OneOss["Emit unprefixed OSS route"]
    Domain --> Smith["Ordinary LangSmith"]
    Smith --> OneSmith["Emit unprefixed LangSmith route"]
    Domain --> Mda["Managed Deep Agents page"]
    Mda --> MdaPy["Emit LangSmith Python route"]
    Mda --> MdaJs["Emit LangSmith JavaScript route"]
    Py --> Nav["docs.json navigation entry"]
    Js --> Nav
    OneOss --> Nav
    OneSmith --> Nav
    MdaPy --> Nav
    MdaJs --> Nav
    classDef process fill:#E5F4FF,stroke:#006DDD,stroke-width:2px,color:#030710
    classDef decision fill:#FDF3FF,stroke:#7E65AE,stroke-width:2px,color:#504B5F
    classDef output fill:#EBD0F0,stroke:#885270,stroke-width:2px,color:#441E33
    class Source,Oss,Product,Smith,Mda process
    class Domain decision
    class Py,Js,OneOss,OneSmith,MdaPy,MdaJs,Nav output
```

This flow shows the ownership boundary: classification selects artifacts and routes; `docs.json` exposes or redirects those routes rather than generating them.

## Build lifecycle and transformation order

`build_all()` clears and recreates `build/`, then builds Python OSS, JavaScript OSS, unversioned Deep Agents Code, unversioned OpenWiki, ordinary LangSmith content, and Managed Deep Agents variants. It then copies shared files, copies npm snippet components, and generates `llms.txt` and `llms-full.txt`. A clean full build therefore eliminates stale output before the derived indexes inspect the final route tree.

For Markdown and MDX, the render pipeline first runs standard preprocessing (including cross-reference and conditional handling), then scopes MDX snippet imports for a language target, rewrites OSS links, and finally rewrites Managed Deep Agents links. Internal targets are `python` and `js`; `js` maps to the public `javascript` route segment.

`build_file()` follows the same classification for an individual file: ordinary OSS creates both variants, the two unversioned OSS products create one artifact, and a Managed Deep Agents file creates two language artifacts. Shared and root-level inputs copy once. It raises `AssertionError` when asked to build a file that does not exist. Prefer a full build after broad route or navigation changes because it also removes stale output and refreshes derived artifacts.

## Shared OSS and language-specific source directories

Shared OSS sources are the normal dual-version case. A shared page is rendered once for the `python` target at `/oss/python/...` and once for the `js` target at `/oss/javascript/...`. An unqualified absolute OSS link can consequently follow the current artifact.

The `src/oss/python/` and `src/oss/javascript/` subtrees are a different contract: the builder includes a file only in the matching pass and removes that leading source-language directory from the output path. Use them for material that genuinely exists in one language, not for a copy of shared content.

## Intentional unversioned OSS products

OpenWiki and Deep Agents Code are explicit exceptions within `src/oss/`. They build once at `/oss/openwiki/...` and `/oss/deepagents/code/...`, respectively, with `python` selected as the deterministic fallback target for conditional content. This fallback does not make either product Python documentation, and their own links remain unprefixed.

An unqualified link from either unversioned product to ordinarily versioned OSS content is nevertheless rendered with that Python target: `/oss/deepagents/quickstart` becomes `/oss/python/deepagents/quickstart`. This is a default-target link decision, not a second copy of the unversioned product.

## Managed Deep Agents: unversioned source, dual output

Managed Deep Agents is a LangSmith routing exception. A direct `.md` or `.mdx` file in `src/langsmith/` whose name begins `managed-deep-agents` is recognized as a Managed Deep Agents page. Ordinary LangSmith emission excludes recognized pages, avoiding an unversioned artifact that would be orphaned outside the Managed Deep Agents navigation.

The dedicated full-build pass discovers `managed-deep-agents*.mdx` files and emits Python and JavaScript artifacts. `build_file()` recognizes either `.md` or `.mdx`, so a Managed Deep Agents `.md` can be emitted when built individually but is not discovered by the bulk variant glob. Use `.mdx` for pages that must participate in a normal full build.

Each language artifact receives its matching conditional content, scoped snippet imports, OSS links, and unqualified Managed Deep Agents cross-links. For example, the shared quickstart includes `:::python` and `:::js` setup commands plus unprefixed `/langsmith/managed-deep-agents-...` links; the two renders select the matching commands and point those links to the current language route.

`docs.json` supplies the public default for unversioned and historical Managed Deep Agents URLs: configured redirects send them to Python routes. Separately, its Python and TypeScript Build dropdowns contain language-specific Managed Deep Agents entries. When adding, renaming, or removing a page, keep the source naming rule, both emitted route entries, and any legacy redirects synchronized.

## Conditional content contract

Use `:::python` and `:::js` only where a shared source needs different material:

```markdown
:::python
Python-only content.
:::

:::js
JavaScript-only content.
:::
```

For the selected target, preprocessing removes the fences and retains the matching block content; it removes a nonmatching supported block completely. Unsupported labels and unclosed blocks remain unchanged. Opening and closing markers must have matching indentation. Escape a literal marker as `\:::` when the rendered page must display conditional syntax.

Conditional rendering is regex-based rather than code-fence-aware. Do not rely on a normal Markdown code fence to protect literal conditional-looking syntax, and do not nest conditionals: the first eligible closing marker ends the match. Escape both markers when documenting the syntax literally.

## Link and snippet rewrite contract

Author an unqualified absolute OSS link when its destination should follow the active language:

```mdx
<!-- openwiki: broken internal link [/oss/langgraph/overview] file "/oss/langgraph/overview" does not exist. Fix the href or restore the target, then delete this comment. -->
[LangGraph overview](/oss/langgraph/overview)
```

The Python artifact receives `/oss/python/langgraph/overview`; the JavaScript artifact receives `/oss/javascript/langgraph/overview`. The rewriter leaves already-prefixed routes, paths containing `images`, and the OpenWiki and Deep Agents Code roots unchanged. These guards prevent double-prefixes and preserve routes that have no language variants.

In a versioned page, import a Markdown snippet from its unprefixed source path:

```mdx
import Example from '/snippets/example.mdx'
```

The builder changes that import to `/snippets/python/example.mdx` or `/snippets/javascript/example.mdx`. Already scoped MDX imports are not rewritten, nor are JSX or TSX component imports. The language-scoped snippet copies allow consumers at different route depths to resolve snippets consistently.

Bare `/langsmith/managed-deep-agents...` links are likewise rewritten during a target-language render. Explicitly language-qualified links remain untouched, so use one only when the destination must intentionally be a particular variant rather than follow the current render.

## Navigation and safe changes

`src/docs.json` is navigation configuration, not the source tree. It independently assigns Python and TypeScript emitted routes to their Build dropdowns, including distinct Managed Deep Agents paths. The unprefixed OpenWiki family appears in both dropdowns even though it has one emitted artifact family. A route must exist in the generated output before a navigation entry can safely expose it.

When changing this model:

1. Choose the source domain from the intended public route and language behavior, not only from a navigation label.
2. Change authored content under `src/`; never patch generated `build/` output.
3. Add the extensionless **emitted route** to the correct `docs.json` product, menu, dropdown, tab, and group. Do not use a source path or an `.mdx` filename as a navigation route.
4. Preserve a public move with a `docs.json` redirect, including a language prefix when it is part of the retired URL.
5. Run `make build`, inspect both artifacts for versioned content, and run `make broken-links`. Update focused builder coverage when changing classification, route exemptions, snippet scoping, or Managed Deep Agents behavior.

## Focused regression coverage

`tests/unit_tests/test_builder.py` tests the boundary conditions most likely to regress: ordinary OSS prefix insertion, preservation of language-qualified and unversioned-product links, one-time output for the two unversioned OSS products, language-scoped MDX imports, and Managed Deep Agents dual output. The Managed Deep Agents fixture verifies matching page links, OSS links, scoped snippets, and conditional snippet content in both variants; it also verifies that unversioned Managed Deep Agents pages are not emitted.

## See also

- [Source directory map](/openwiki/architecture/source-map.md)
- [Markdown preprocessing pipeline](/openwiki/concepts/preprocessing.md)
- [Adding and modifying documentation pages](/openwiki/operations/adding-pages.md)
- [Writing versioned content](/openwiki/workflows/versioned-content.md)
