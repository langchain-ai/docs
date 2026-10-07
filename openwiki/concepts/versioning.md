---
type: documentation route model
title: Versioned Documentation and Routes
description: Explains how the documentation builder selects source families and emits Python, JavaScript, and language-agnostic routes. Covers build-time rendering, link and snippet rewriting, MCP authoring ownership, Mintlify navigation, and compatibility redirects.
tags: [documentation-pipeline, routes, language-versioning, redirects]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-07T08:23:22.147Z
sources:
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-17f3856bce97f37118963062
    resource: repo://pipeline/preprocessors/handle_auto_links.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-d67d5f0a5ce9fbed759bdc27
    resource: repo://src/langsmith/managed-deep-agents-deploy.mdx
  - id: openwiki-source-6b12999ebb2ff36651ec757c
    resource: repo://src/langsmith/managed-deep-agents-mcp-endpoint.mdx
  - id: openwiki-source-243c6e17a513bece229a34b9
    resource: repo://src/language-toggle.js
  - id: openwiki-source-4d3d0f53cb13c1c1b72f3662
    resource: repo://src/oss/javascript/langchain/mcp-v1.mdx
  - id: openwiki-source-c6258cab179201344bfb89d2
    resource: repo://src/oss/javascript/migrate/langchain-mcp-adapters.mdx
  - id: openwiki-source-d1c9b8a212b3f593c4e2fcfd
    resource: repo://src/oss/langchain/mcp/connections.mdx
  - id: openwiki-source-867d24ecd094a73112272b9b
    resource: repo://src/oss/langchain/mcp/index.mdx
  - id: openwiki-source-3b99ef795fb96770516215eb
    resource: repo://src/oss/langchain/mcp/tools.mdx
  - id: openwiki-source-0bbd982f783595e2d0ac49ae
    resource: repo://src/oss/langgraph/interrupts.mdx
  - id: openwiki-source-5fb3e6d5f1b7fba58bbcc170
    resource: repo://src/oss/python/migrate/langchain-mcp-adapters.mdx
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
generated: { by: "openwiki/0.4.3", at: "2026-10-07T08:23:22.147Z" }
---

# Versioned Documentation and Routes

`DocumentationBuilder` derives generated documentation routes from source paths under `src/`. `src/docs.json` separately configures public Mintlify navigation and redirects. Its entries must name routes that the builder emits, but a menu entry neither creates a page nor determines its source owner. Treat **source ownership**, **emitted routes**, **navigation**, and **compatibility redirects** as separate contracts.

## Route families and build lifecycle

| Source family | Emitted route(s) | Preprocessing target |
| --- | --- | --- |
| Ordinary `src/oss/` content, including Deep Agents outside `code/` | `/oss/python/...` and `/oss/javascript/...` | `python` and `js` |
| `src/oss/python/...` or `src/oss/javascript/...` | Only the matching route family, without the source-language directory | Matching target |
| `src/oss/deepagents/code/...` | `/oss/deepagents/code/...` | `python` fallback |
| `src/oss/openwiki/...` | `/oss/openwiki/...` | `python` fallback |
| Ordinary `src/langsmith/...` | `/langsmith/...` | `python` fallback |
| Direct `src/langsmith/managed-deep-agents*.mdx` files | `/langsmith/python/...` and `/langsmith/javascript/...` | `python` and `js` |

```mermaid
flowchart TD
    Source["Source under src"] --> Family{"Path family"}
    Family --> Oss["Ordinary OSS"]
    Oss --> OssPy["OSS Python route"]
    Oss --> OssJs["OSS JavaScript route"]
    Family --> Product["OpenWiki or Deep Agents Code"]
    Product --> PlainProduct["Unprefixed OSS route"]
    Family --> Smith["Ordinary LangSmith"]
    Smith --> PlainSmith["Unprefixed LangSmith route"]
    Family --> Managed["Managed Deep Agents"]
    Managed --> ManagedPy["LangSmith Python route"]
    Managed --> ManagedJs["LangSmith JavaScript route"]
    ManagedPy --> Mintlify["Navigation and redirects"]
    ManagedJs --> Mintlify
```

This is builder routing by source path. Mintlify configuration follows it; it is not an ownership classifier.

A full `build_all()` removes and recreates `build/`, builds ordinary OSS for Python and JavaScript, then unversioned Deep Agents Code, OpenWiki, ordinary LangSmith, and Managed Deep Agents variants. It then copies shared files and npm snippet components. Clearing output prevents stale artifacts after a full build.

`build_file()` applies the same policy to one existing source file: ordinary OSS emits twice except under the two unversioned product roots; ordinary LangSmith emits once; and a Managed Deep Agents page emits twice. Shared and root-level files copy once. A missing requested file raises `AssertionError`.

Language-owned OSS directories filter a dual build rather than appear in the final route. In a Python pass, `src/oss/javascript/...` is skipped, and vice versa. The selected `python` or `javascript` source component is removed before output: `src/oss/python/concepts/example.mdx` emits at `/oss/python/concepts/example`, not a doubled path.

The provider catalogue at `src/oss/python/integrations/providers/all_providers.mdx` is therefore Python-only. Source ownership does not exempt a page from target transforms: bare internal OSS links in a language-owned page are still scoped to the matching language output. Choose an owned subtree because content belongs to that SDK, not because its navigation should appear in a particular language menu.

Ordinary LangSmith documents are emitted once below `/langsmith/`, excluding Managed Deep Agents files, and use the Python preprocessing target. That target is a rendering default; it does not make every ordinary LangSmith page Python documentation. Full-build collection rejects symlinks, including links to regular files, and resolved paths outside its root, preventing a source-tree link from placing host files in an artifact.

## Transforming an emitted Markdown page

For Markdown and MDX, the builder applies standard preprocessing first. If an output has a language target, it then scopes Markdown snippet imports, rewrites OSS links, and rewrites Managed Deep Agents links, in that order. Internal target `js` becomes the public route segment `javascript`; `.md` output is written with an `.mdx` suffix.

```mermaid
flowchart LR
    Input["Markdown or MDX source"] --> Prep["Standard preprocessing"]
    Prep --> Target{"Language target exists"}
    Target -->|"yes"| Imports["Scope snippet imports"]
    Target -->|"no"| Output["Write artifact"]
    Imports --> OssLinks["Rewrite OSS links"]
    OssLinks --> ManagedLinks["Rewrite Managed Deep Agents links"]
    ManagedLinks --> Output
```

This shows the transformation order for a generated Markdown artifact.

Use `:::python` and `:::js` only for content that differs by target. Conditional rendering keeps matching content without its fences and removes the other supported block. Escaped `\:::` becomes literal `:::`; unsupported labels and unclosed blocks remain unchanged. The renderer is regex-based rather than code-fence-aware, so escape a literal conditional marker instead of relying on a Markdown code fence to protect it.

Autolinks are resolved before conditional blocks are selected. The autolink preprocessor recognizes the active conditional fence as a scope, otherwise it uses the target as its default scope, and it deliberately ignores regular Markdown code fences. Keep SDK-specific `@[...]` references inside their corresponding branch. The shared LangGraph interrupts page follows this pattern for target-specific imports and `interrupt` behavior.

An unqualified absolute OSS link such as `/oss/deepagents/overview` becomes `/oss/python/deepagents/overview` or `/oss/javascript/deepagents/overview` in a targeted artifact. Rewriting skips image URLs, already-prefixed URLs, and the language-agnostic Deep Agents Code and OpenWiki roots. In targeted MDX, an import from `/snippets/component.mdx` likewise becomes `/snippets/python/component.mdx` or `/snippets/javascript/component.mdx`; an already scoped import remains unchanged.

Shared Markdown snippets are emitted as Python and JavaScript copies with target-specific preprocessing and rewritten absolute links. The original snippet path is a Python-targeted default for unversioned importers; targeted pages import their matching copy. This avoids links whose correctness depends on a consumer's nesting depth.

## Shared and language-owned MCP content

The current LangChain MCP section demonstrates when one source should serve both SDKs. The shared sources in `src/oss/langchain/mcp/`—the overview, tools, and connections pages—contain `:::python` and `:::js` sections and build into both OSS language families. Bare internal `/oss/langchain/mcp...` links are rewritten to the reader's route family. Their paired Mintlify **MCP** groups currently expose `index`, `tools`, `connections`, and `auth` under both Python and JavaScript **Advanced usage** navigation. The shared source and the two navigation entries are separate requirements: confirm the emitted routes before changing either menu branch.

Put common MCP concepts, parallel structure, and SDK-specific fenced units in the shared subtree. The overview, for example, selects the SDK's package setup, API spelling, and migration destination; the connections and tools pages select lifecycle, tool discovery, and error-handling guidance for each SDK. This makes one route suffix yield two concrete routes without copying the common explanation.

Migration content is intentionally language-owned. `src/oss/python/migrate/langchain-mcp-adapters.mdx` emits only at `/oss/python/migrate/langchain-mcp-adapters`, while `src/oss/javascript/migrate/langchain-mcp-adapters.mdx` emits only at `/oss/javascript/migrate/langchain-mcp-adapters`. The JavaScript guide covers the 1.x-to-2.0 adapter upgrade, including `MCPAdapter`, `servers`, protocol modes, strict configuration validation, and the server-name tool-prefix default. The Python guide instead describes migration from the standalone package into `langchain.mcp` and FastMCP. Do not move these guides into shared content merely because they share a route suffix.

Likewise, `src/oss/javascript/langchain/mcp-v1.mdx` is JavaScript-owned and emits only to `/oss/javascript/langchain/mcp-v1`. Its `:::js` warning sends 1.x readers to the shared MCP documentation and the JavaScript migration guide; its `:::python` branch is removed in the JavaScript artifact. Source placement controls output multiplicity, not discoverability: add a legacy or migration page to only the navigation branch whose emitted route exists.

## Unversioned OSS products

Deep Agents Code and OpenWiki are explicit exceptions to ordinary OSS duplication. They emit once at unprefixed roots, and `python` is used only as a deterministic conditional-rendering fallback. Links within those roots remain unprefixed; a bare link from either product to ordinary OSS resolves to the Python OSS route.

`docs.json` lists the same unprefixed OpenWiki routes in the OpenWiki tab of both the Python and TypeScript Build dropdowns. The language-toggle script hides the switcher on `/oss/openwiki` because no alternate language route exists. Deep Agents Code is likewise unversioned regardless of where Mintlify navigation places it.

## Managed Deep Agents variants

Managed Deep Agents is the LangSmith exception. A direct child of `src/langsmith/` named `managed-deep-agents*` with a `.md` or `.mdx` extension is classified as a variant page for an individual build. It produces Python and JavaScript artifacts, each with target-specific conditional content, snippets, and rewritten OSS and Managed Deep Agents links; it does not produce an unversioned artifact.

Author internal family links as bare `/langsmith/managed-deep-agents...` URLs when they should follow the reader's target. This applies to Markdown links and quoted `href` values, as used by the current MCP endpoint and deployment pages. For a language-targeted artifact, the final rewrite inserts `python` or `javascript`; an already-prefixed URL is deliberately left unchanged. Thus one source can link within its own output family, whereas an ordinary LangSmith page built with the Python target resolves a bare Managed Deep Agents URL to Python.

The dedicated full-build discovery pass only selects direct `managed-deep-agents*.mdx` files. Although the individual-file classifier accepts `.md`, the full pass does not emit a `.md` page. Use a direct `.mdx` file for a Managed Deep Agents page that must appear in a full build.

### Navigation and compatibility

The Python and TypeScript Build dropdowns each contain a **Managed Deep Agents** tab. Both enumerate corresponding language-prefixed suffixes in **Get started**, **Agent capabilities** with a nested **Channels** group, and **Build and deploy**; the latter includes the MCP endpoint. When adding a new variant, add matching entries to both tabs only after confirming both emitted routes exist.

Unversioned `/langsmith/managed-deep-agents...` URLs are compatibility inputs, not generated pages. `docs.json` redirects current unversioned routes—including overview, quickstart, channels, deployment, CLI, identity, MCP connectors, and other family pages—to Python. It also maps historical aliases such as `managed-deep-agents-invoke`, `-sdk`, `-api`, older channel paths, and connector paths to Python destinations. These redirects preserve inbound links and establish Python as the legacy default; they do not replace JavaScript artifacts or navigation.

When adding or moving a Managed Deep Agents page:

1. Create a direct `src/langsmith/managed-deep-agents*.mdx` source file.
2. Use bare internal family URLs where the link should track output language; use a prefixed URL only to intentionally pin a language.
3. Confirm both generated routes, then add matching Python and TypeScript navigation entries in `src/docs.json`.
4. Add or update an unversioned-to-Python redirect for a public, renamed, or legacy URL.
5. Run a full build and inspect both variants, including conditional branches, links, and snippet imports.

## Verification and safe changes

Builder regression tests cover unversioned Deep Agents Code and OpenWiki output and links, scoped snippet imports, and Managed Deep Agents dual output. The Managed Deep Agents fixture verifies language-specific links and conditional snippet content while confirming that no unversioned artifact is emitted. Other tests cover bare Markdown-link and quoted-`href` Managed Deep Agents rewrites and reject source-tree symlinks.

For a route change, modify source rather than `build/`; decide the source family before touching navigation; and use a full build when removing or moving pages. Inspect both emitted language variants where relevant, then verify that `docs.json` navigation names actual routes and that redirects are compatibility mappings rather than substitute pages.

## See also

- [Source map](/openwiki/architecture/source-map.md)
- [Preprocessing](/openwiki/concepts/preprocessing.md)
- [Adding pages](/openwiki/operations/adding-pages.md)
- [Test overview](/openwiki/testing/test-overview.md)
- [Changing versioned content](/openwiki/workflows/versioned-content.md)
