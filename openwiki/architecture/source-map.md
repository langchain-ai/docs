---
type: architecture reference
title: Source Directory Map
description: Maps authored documentation and configuration to emitted routes, explicit Mintlify navigation and redirects, deployment-generated API reference, and current LangSmith and OSS product surfaces. Use it to select the source of truth for a page, URL, product placement, or generated reference change.
tags: [documentation, routing, navigation, mintlify]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-08T08:23:51.982Z
sources:
  - id: openwiki-source-5153f86e64d6ee0b305f72b3
    resource: repo://.github/workflows/refresh-langsmith-openapi.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-697851c98229599f97376bfb
    resource: repo://scripts/process_langsmith_openapi.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-661abd9305024589f43ce542
    resource: repo://src/langsmith/agents.mdx
  - id: openwiki-source-3225362f66429aee81d6a0d9
    resource: repo://src/langsmith/application-structure.mdx
  - id: openwiki-source-4e258b7fd0aee5e7df6fba88
    resource: repo://src/langsmith/control-plane.mdx
  - id: openwiki-source-4256c14336d0eb39aed5e217
    resource: repo://src/langsmith/data-plane.mdx
  - id: openwiki-source-171a529de8fb1df84c71f554
    resource: repo://src/langsmith/engine-overview.mdx
  - id: openwiki-source-17568d22d2c267ddd66b7112
    resource: repo://src/langsmith/engine-self-hosted.mdx
  - id: openwiki-source-4ff8c4b0bbaf0272bf625605
    resource: repo://src/langsmith/fleet/essentials.mdx
  - id: openwiki-source-a27620f1abc3e0bbef984219
    resource: repo://src/langsmith/llm-gateway-credits.mdx
  - id: openwiki-source-95a114643a70288e7f5458da
    resource: repo://src/langsmith/llm-gateway-how-it-works.mdx
  - id: openwiki-source-43ff65f03831177d52580c83
    resource: repo://src/langsmith/managed-deep-agents-overview.mdx
  - id: openwiki-source-17cda5e480a486a133aa3e81
    resource: repo://src/langsmith/managed-deep-agents-runtime.mdx
  - id: openwiki-source-0ab5b536400c44173ebccd67
    resource: repo://src/langsmith/managed-deep-agents-sandboxes.mdx
  - id: openwiki-source-fa546764ecaebb51fc64437e
    resource: repo://src/langsmith/sandboxes.mdx
  - id: openwiki-source-dc010f4c5f7e636c2056fa1d
    resource: repo://src/langsmith/self-host-sandbox-architecture.mdx
  - id: openwiki-source-76ace04efd84c2823e3cc7c6
    resource: repo://src/langsmith/tuned-evaluators.mdx
  - id: openwiki-source-f79b8bced12e446a4f7394de
    resource: repo://src/oss/deepagents/code/remote-sandboxes.mdx
  - id: openwiki-source-c6258cab179201344bfb89d2
    resource: repo://src/oss/javascript/migrate/langchain-mcp-adapters.mdx
  - id: openwiki-source-867d24ecd094a73112272b9b
    resource: repo://src/oss/langchain/mcp/index.mdx
  - id: openwiki-source-4d9644891221cf29cff85bfb
    resource: repo://src/oss/python/integrations/chat/index.mdx
  - id: openwiki-source-40800c01aa5ea143782c9738
    resource: repo://src/oss/python/integrations/document_loaders/index.mdx
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
generated: { by: "openwiki/0.4.3", at: "2026-10-08T08:23:51.982Z" }
---

`src/` is authored input, not the site hierarchy. Keep four ownership planes separate:

1. **Route emission:** `DocumentationBuilder` reads source families, preprocesses MDX, and writes disposable output routes.
2. **Navigation and compatibility:** `src/docs.json` explicitly supplies Mintlify menu labels, grouping, ordering, OpenAPI declarations, and redirects.
3. **Deployment-generated reference:** Mintlify consumes declared OpenAPI specifications and generates endpoint pages at deployment.
4. **Product documentation:** ordinary source pages explain the product; their location does not choose their reader-facing product label or menu placement.

```mermaid
flowchart TD
    Source["Authored src content"] --> Builder["DocumentationBuilder"]
    Builder --> Routes["Emitted routes"]
    Config["src/docs.json"] --> Navigation["Mintlify navigation and redirects"]
    Config --> Specs["OpenAPI declarations"]
    Specs --> Reference["Deployment-generated endpoint reference"]
    Routes --> Published["Published documentation"]
    Navigation --> Published
    Reference --> Published
```

This shows the independent inputs to the published site: route emission does not create navigation, and generated endpoint reference is not an authored MDX route. Never treat `build/` as durable source.

## Emission families and boundaries

A full build deletes and recreates the build directory, renders OSS for Python and JavaScript, then renders special unversioned and LangSmith families and copies shared assets. Supported non-MDX inputs are copied; MDX is preprocessed; `TEMPLATE.mdx` is skipped. Source collection rejects symlinks and anything resolving outside its collection root, preventing a committed source link from leaking host files into artifacts.

| Authored family | Emitted route family | Ownership rule |
| --- | --- | --- |
| Shared `src/oss/` content | `/oss/python/...` and `/oss/javascript/...` | Render twice, resolving conditional content per target language. |
| `src/oss/python/` or `src/oss/javascript/` | Only the matching language tree | The source-language segment is removed from the output; the opposite pass skips it. |
| `src/oss/openwiki/` | `/oss/openwiki/...` | Render once with the Python conditional branch. |
| `src/oss/deepagents/code/` | `/oss/deepagents/code/...` | Render once with the Python conditional branch. |
| Ordinary `src/langsmith/` | `/langsmith/...` | Render once as unversioned LangSmith content with the Python branch. |
| Direct `src/langsmith/managed-deep-agents*.mdx` | `/langsmith/python/...` and `/langsmith/javascript/...` | Excluded from the ordinary LangSmith pass and rendered per language. |
| `src/snippets/`, images, fonts, `docs.json`, JS, and CSS | Shared emitted inputs | These support pages or site runtime; they are not inferred as navigation. |

For language output, preprocessing selects conditional blocks, scopes unqualified MDX snippet imports under `/snippets/python/` or `/snippets/javascript/`, and rewrites eligible `/oss/` links. It leaves images, already-qualified links, OpenWiki, and Deep Agents Code unprefixed because those products have single route roots.

### Unversioned and language-specific exceptions

OpenWiki and Deep Agents Code are unversioned OSS products, not Python/TypeScript route trees. `docs.json` projects the same OpenWiki routes into both Build language dropdowns; that is two menu placements for one output. Deep Agents Code is instead a Products and setup item, with overview, quickstart, CLI, approval, goals, plugin, extension, memory, remote-sandbox, subagent, provider, and configuration routes all rooted at `/oss/deepagents/code/`. Compatibility redirects map former language-prefixed Deep Agents Code URLs to those single routes.

Managed Deep Agents is the inverse exception. Its one authored `managed-deep-agents*.mdx` family produces Python and JavaScript variants, which the two Build dropdowns navigate independently. Unversioned legacy Managed Deep Agents URLs redirect to Python. Do not add a duplicate unversioned MDX page; test both variants and redirects when changing this family.

## `docs.json`: navigation, redirects, and product naming

`src/docs.json` is authoritative for the sidebar, not a source-tree scan. An emitted page may be absent from a menu; conversely, a redirect is a compatibility rule rather than emitted content. Adding an `index.mdx` or moving a file does not establish reader-facing placement—add or update the explicit route in `docs.json` and manage redirect entries separately.

### Build and the shared MCP surface

Python and TypeScript Build menus have deliberately different integration group structures. Python includes **Integrations by component**, while TypeScript uses different broad groupings. Component landing pages therefore require a deliberately placed, language-qualified navigation route.

The MCP overview source at `src/oss/langchain/mcp/` is shared: the builder emits it in both language trees and each language menu points to its own emitted route. Its conditional branches own language-specific instructions. In contrast, `src/oss/javascript/migrate/langchain-mcp-adapters.mdx` is JavaScript-owned: it emits and appears only at the JavaScript migration route. Keep cross-language conceptual content shared; keep adapter migration behavior in the JavaScript source family.

### LangSmith route ownership and reader-facing labels

Ordinary `src/langsmith/` files stay at unversioned `/langsmith/...` routes even when navigation labels differ from their source directory.

| Source / route family | Current `docs.json` projection |
| --- | --- |
| `langsmith/agents.mdx` and related environment, navigation, creation, UI, and deployment pages | Products and setup → LangSmith setup → Overview → **Agent-based workspaces** (Beta) |
| `langsmith/application-structure.mdx` | Deploy → Agent Server → **Develop your application** |
| `langsmith/sandboxes.mdx` plus snapshots, service URLs, downloads, auth proxy, mounts, permissions, CLI, SDK, and Harbor routes | Deploy → **Sandboxes** tab |
| `langsmith/self-host-sandbox-architecture.mdx`, scaling, and operations | A separate **Sandboxes** group in the self-hosted setup navigation; not children of the Deploy Sandboxes tab |
| `langsmith/fleet/` | Products and setup → **No-code agents** |
| `langsmith/llm-gateway*.mdx` | Products and setup → **LLM Gateway** (Beta) |
| `langsmith/engine*.mdx` | Products and setup → **Engine** |
| `langsmith/managed-deep-agents*.mdx` | Build → language-specific **Managed Deep Agents** tabs |
| `oss/deepagents/code/` | Products and setup → **Deep Agents Code** |

These labels expose product boundaries, not merely renamed folders:

- **LLM Gateway** authenticates and authorizes standard calls, resolves route and credentials, evaluates governance policy, translates formats when required, invokes the provider, and records trace and usage metadata. Direct model access retains identity, credential, policy, and tracing operations while bypassing translation. Gateway Credits use a LangChain-hosted upstream credential and a LangSmith API key; provider-prefixed IDs use configured provider secrets.
- **Managed Deep Agents** is a hosted layer over the OSS Deep Agents harness, not a second agent framework. The `mda` CLI gives a managed runtime an agent definition; it supplies the backend, store, checkpointer, memory, skills, and system prompt before compiling it. Its runtime separates caller identity, application context, and verified channel delivery: use the verified runtime server information for authorization rather than client-supplied context. A declared managed sandbox uses LangSmith Sandboxes and is reused one per durable thread.
- **Deep Agents Code** is the unversioned OSS terminal product (`dcode`). Its remote-sandbox documentation describes a split execution model: the local process retains the LLM loop, memory, and tool dispatch, while filesystem and command tool calls target the selected remote sandbox. This is separate from the LangSmith-managed sandbox product and from Managed Deep Agents' deployment-owned backend.
- **Sandboxes** is the LangSmith managed-resource surface. The landing page covers managed sandbox resources and points users to snapshots, service URLs, auth proxy, mounts, permissions, CLI, SDK, and self-hosted enablement. The self-hosted architecture cluster documents a different operational model: `sandbox-host` pods operate Firecracker microVMs on dedicated KVM-capable nodes, while shared storage holds persistent state. It belongs with self-host operations even though it cross-links from the product landing page.
- **No-code agents** is the reader-facing Fleet product. Its agent sidebar configures channels, sharing, connections and approval mode, knowledge, schedules, and advanced settings; a tool can run automatically or wait for approval.
- **Engine** scans production traces on a dynamic schedule, clusters and prioritizes issues, then follows an issue loop of detection, diagnosis, proposed fix, matching-trace tracking, and reopening after recurrence. It can create ground-truth dataset examples from production inputs. The Engine menu contains overview, issue workflow, GitHub, notifications, security, and self-hosted pages.
- **Tuned Evaluators** remain ordinary LangSmith source content placed in Monitor. They select eligible threads, use LangChain-managed specialized judges, and attach feedback; organization enablement and compatible threaded messages gate creation, and disabling pauses rather than deletes saved configurations.

### Agent Server deployment planes

Control plane and data plane pages are ordinary unversioned LangSmith source, but explain a directional deployment boundary. The control plane stores deployment desired state and exposes APIs; the data-plane listener polls those APIs and reconciles Agent Server deployments, revisions, and deletion. The control plane never connects directly to the data plane. Place route and menu changes in `docs.json`; do not model this operational relationship by moving source files.

## Deployment-generated API reference

The three OpenAPI declarations in `docs.json` create endpoint reference at deployment. Their overview pages are ordinary authored routes, but endpoint pages are Mintlify-generated rather than MDX content and are not local build artifacts.

| Surface | Specification input | Generated location |
| --- | --- | --- |
| Agent Server API | Committed `src/langsmith/agent-server-openapi.json` | `langsmith/agent-server-api` |
| Control Plane API | `https://api.host.langchain.com/openapi.json` | Mintlify default location |
| LangSmith REST API | Committed `src/langsmith/langsmith-platform-openapi.json` | `langsmith/smith-api` |

The LangSmith REST specification is a committed post-processed publication input. Its processor allow-lists the live host, hides fleet, internal, and health operations, assigns and orders public tag groups, and normalizes operation titles. The daily workflow runs that processor, exits without a commit for an unchanged spec, and reuses the `chore/refresh-langsmith-openapi` pull request while it remains open.

## Safe change procedure

1. Begin with the intended public URL. Identify whether it is emitted MDX, an explicit navigation entry, a redirect, or deployment-generated reference.
2. For ordinary OSS content, check Python and JavaScript output. For OpenWiki and Deep Agents Code, check the single unversioned output and retain unprefixed links.
3. Edit `src/docs.json` explicitly for menu placement, labels, ordering, OpenAPI declarations, and redirects. Do not expect the builder to infer any of those.
4. For Managed Deep Agents, verify both language outputs and the unversioned-to-Python compatibility redirects.
5. Keep ordinary LangSmith source in `src/langsmith/`; use `docs.json` to express product positioning. This includes Engine, LLM Gateway, Fleet, control plane, data plane, and sandbox material.
6. When changing sandbox documentation, decide whether the reader needs managed-resource usage, Managed Deep Agents integration, Deep Agents Code remote tools, or self-hosted infrastructure. Those are linked but separately owned route clusters.
7. Change API endpoint reference through the applicable OpenAPI input and declaration—not endpoint MDX. Review processing and the refresh workflow for LangSmith REST changes.
8. Extend focused `tests/unit_tests/test_builder.py` coverage when modifying source-family routing, preprocessing/rewrite policy, special-family behavior, or source-tree safety.

## Related pages

- [Preprocessing](/openwiki/concepts/preprocessing.md)
- [Versioning](/openwiki/concepts/versioning.md)
- [Reference docs](/openwiki/integrations/reference-docs.md)
- [Adding pages](/openwiki/operations/adding-pages.md)
- [Quickstart](/openwiki/quickstart.md)
