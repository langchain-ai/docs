---
type: architecture reference
title: Source Directory Map
description: Maps documentation source families and docs.json projections to emitted routes, explicit Mintlify navigation and redirects, deployment-generated API reference, and current LangSmith and OSS product clusters. Use it to identify the source of truth for a route, menu placement, redirect, or generated reference change.
tags: [documentation, routing, navigation, mintlify]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-14T08:21:39.311Z
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
  - id: openwiki-source-a27620f1abc3e0bbef984219
    resource: repo://src/langsmith/llm-gateway-credits.mdx
  - id: openwiki-source-95a114643a70288e7f5458da
    resource: repo://src/langsmith/llm-gateway-how-it-works.mdx
  - id: openwiki-source-d67d5f0a5ce9fbed759bdc27
    resource: repo://src/langsmith/managed-deep-agents-deploy.mdx
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
  - id: openwiki-source-3e471962a1ecd6495d5d8fdd
    resource: repo://src/langsmith/self-host-smithdb-features.mdx
  - id: openwiki-source-c52470905e74b4e82e1c1ae5
    resource: repo://src/langsmith/self-host-smithdb-install.mdx
  - id: openwiki-source-64bcd09aa388b45f25ea6da5
    resource: repo://src/langsmith/self-host-smithdb.mdx
  - id: openwiki-source-222b22691fa5b319ecd2ae6f
    resource: repo://src/oss/deepagents/code/configuration.mdx
  - id: openwiki-source-f79b8bced12e446a4f7394de
    resource: repo://src/oss/deepagents/code/remote-sandboxes.mdx
  - id: openwiki-source-031ab3cc5ad2aa3eb2de459c
    resource: repo://src/oss/deepagents/memory.mdx
  - id: openwiki-source-c6258cab179201344bfb89d2
    resource: repo://src/oss/javascript/migrate/langchain-mcp-adapters.mdx
  - id: openwiki-source-867d24ecd094a73112272b9b
    resource: repo://src/oss/langchain/mcp/index.mdx
  - id: openwiki-source-57d888befacccdf3384bf1e6
    resource: repo://src/oss/langgraph/persistence.mdx
  - id: openwiki-source-e9105e813a1bc86fe40c7444
    resource: repo://src/oss/langgraph/stores.mdx
  - id: openwiki-source-4d9644891221cf29cff85bfb
    resource: repo://src/oss/python/integrations/chat/index.mdx
  - id: openwiki-source-40800c01aa5ea143782c9738
    resource: repo://src/oss/python/integrations/document_loaders/index.mdx
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
generated: { by: "openwiki/0.4.3", at: "2026-10-14T08:21:39.311Z" }
---

`src/` is authored input, not the published-site hierarchy. Keep four ownership planes separate:

1. **Route emission:** `DocumentationBuilder` preprocesses source families and writes disposable build routes.
2. **Navigation and compatibility:** `src/docs.json` explicitly defines Mintlify labels, groups, ordering, redirects, and OpenAPI declarations.
3. **Deployment-generated reference:** Mintlify generates endpoint pages from declared OpenAPI specifications at deployment.
4. **Product documentation:** ordinary MDX explains a product, but its directory does not determine its product label or navigation placement.

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

This diagram shows the independent publication inputs: emitting an MDX route does not add navigation, and an OpenAPI endpoint page is not authored MDX. Do not treat `build/` as durable source.

## Builder-owned route emission

A full build deletes and recreates the build directory, renders OSS for Python and JavaScript, renders special unversioned and LangSmith families, then copies shared inputs. MDX is preprocessed; supported non-MDX files are copied. Source discovery rejects symlinks and files that resolve outside the collection root, preventing a committed link from copying host data into build artifacts.

| Authored family | Emitted route family | Ownership rule |
| --- | --- | --- |
| Shared `src/oss/` content, including Deep Agents except Code | `/oss/python/...` and `/oss/javascript/...` | Render twice, selecting conditional content for each target. |
| `src/oss/python/` or `src/oss/javascript/` | Only its corresponding language tree | The language directory is removed in output; the opposite pass skips it. |
| `src/oss/openwiki/` | `/oss/openwiki/...` | Render once with the Python conditional branch. |
| `src/oss/deepagents/code/` | `/oss/deepagents/code/...` | Render once with the Python conditional branch. |
| Ordinary `src/langsmith/` | `/langsmith/...` | Render once, unversioned, with the Python conditional branch. |
| Direct `src/langsmith/managed-deep-agents*.mdx` | `/langsmith/python/...` and `/langsmith/javascript/...` | Excluded from ordinary LangSmith output and rendered for each language. |
| `src/snippets/`, images, fonts, `docs.json`, JS, and CSS | Shared emitted inputs | Support content and site runtime; they do not infer navigation. |

Preprocessing scopes unqualified MDX snippet imports under `/snippets/python/` or `/snippets/javascript/` and rewrites eligible `/oss/` links. Images, already-qualified links, and the unversioned OpenWiki and Deep Agents Code roots remain unprefixed.

### Route exceptions

**OpenWiki** and **Deep Agents Code** have one unversioned OSS route family. `docs.json` can place a single OpenWiki route in both Build language dropdowns, but those are two menu references, not two outputs. Deep Agents Code is instead a Products and setup item.

**Managed Deep Agents** is the inverse: one direct `langsmith/managed-deep-agents*.mdx` source family produces Python and JavaScript routes. Its Build tabs point to the corresponding variant, while legacy unversioned Managed Deep Agents URLs redirect to Python. Do not add an unversioned MDX copy; test both variants and the redirects.

## `docs.json`: explicit navigation, redirects, and generated reference

`src/docs.json` is the sidebar source of truth, not a directory scan. A built route can be unlisted; a redirect is a compatibility rule rather than content. Adding or moving `index.mdx` therefore does not establish reader-facing placement. Update the explicit navigation route and any necessary redirect separately.

### Build menus and shared OSS content

Python and TypeScript Build integration menus intentionally use different group structures. Component landing pages need explicit language-qualified placement. The shared `src/oss/langchain/mcp/` source emits for both language trees and is listed in both menus; conditional branches carry language-specific instructions. Conversely, `src/oss/javascript/migrate/langchain-mcp-adapters.mdx` is JavaScript-only in both output and navigation.

### LangSmith and product projections

Ordinary `src/langsmith/` content emits unversioned even when its public product label differs from the source directory. The projection below is user-facing taxonomy, not a reason to move authored files.

| Source or route cluster | Current `docs.json` projection |
| --- | --- |
| `langsmith/agents.mdx` and related environment, navigation, creation, UI, and deployment pages | Products and setup → LangSmith setup → Overview → **Agent-based workspaces** (Beta) |
| `langsmith/application-structure.mdx` | Deploy → Agent Server → **Develop your application** |
| `langsmith/sandboxes.mdx`, snapshots, service URLs, downloads, auth proxy, mounts, permissions, CLI, SDK, and Harbor pages | Deploy → **Sandboxes** tab |
| `langsmith/enable-self-hosted-sandboxes.mdx` plus architecture, scaling, operations, and egress-proxy pages | Products and setup → LangSmith setup → self-hosted **Additional features → Enable Sandboxes** |
| `langsmith/self-host-smithdb*.mdx` | Dedicated self-hosted **SmithDB** group |
| `langsmith/llm-gateway*.mdx` | Products and setup → **LLM Gateway** (Beta), with Get started, Core capabilities, Administration and governance, and Advanced groups |
| `langsmith/fleet/` | Products and setup → **No-code agents**, with Get started, Configure, Tools and automation, Advanced, and Additional resources groups |
| `langsmith/engine*.mdx` | Products and setup → **Engine** |
| `langsmith/managed-deep-agents*.mdx` | Build → language-specific **Managed Deep Agents** tabs |
| `oss/deepagents/code/` | Products and setup → **Deep Agents Code**, with an expanded Configuration root and child pages |

### Deployment-generated API reference

The three OpenAPI declarations create endpoint reference pages at deployment. Their overview/reference landing pages are authored routes; the endpoint pages are Mintlify-generated and are not local build artifacts.

| Surface | Specification input | Generated location |
| --- | --- | --- |
| Agent Server API | Committed `src/langsmith/agent-server-openapi.json` | `langsmith/agent-server-api` |
| Control Plane API | `https://api.host.langchain.com/openapi.json` | Mintlify default location |
| LangSmith REST API | Committed `src/langsmith/langsmith-platform-openapi.json` | `langsmith/smith-api` |

The LangSmith REST specification is a committed post-processed publication input. Its processor allow-lists the live LangSmith host, hides Fleet, internal, sandbox-internal, and health operations, assigns and orders readable tag groups, and normalizes visible operation titles. The daily refresh runs the processor; when the committed specification is unchanged it makes no commit, and otherwise it appends to the open `chore/refresh-langsmith-openapi` pull request.

## Product clusters and operational boundaries

### Agent Server and application structure

`application-structure.mdx` documents the deployable application contract: a configuration file (`langgraph.json`), graph implementation, dependency definition, and optional `.env`. `langgraph.json` selects dependencies, graphs, environment variables, and related deployment settings; multiple graph IDs can share one deployment's dependencies, environment, and image, and Agent Server creates a default assistant for each graph.

Control-plane and data-plane pages are ordinary unversioned LangSmith sources but describe a directional operational relationship: the control plane stores desired deployment state, while the data-plane listener polls its APIs and reconciles deployments, revisions, and deletion. The control plane never opens a direct connection to the data plane.

### LLM Gateway and Fleet

The standard LLM Gateway authenticates and authorizes the caller, resolves route and upstream credential, evaluates governance policies, translates formats when needed, invokes the provider, and records trace and usage metadata. Direct model access retains authentication, credential resolution, policy enforcement, and tracing while skipping translation. Gateway Credits use LangChain-hosted models through the standard gateway with a LangSmith API key and no provider secret; provider-prefixed model IDs use configured bring-your-own-provider secrets.

Fleet is the documentation cluster for no-code agents, not a builder source family. Its current navigation separates onboarding and templates, workspace and agent configuration, tools and automation, code/MCP/webhook/auth advanced material, and access, self-hosting, and changelog resources. Do not infer Fleet ownership from an adjacent sidebar label: its authored files remain under `src/langsmith/fleet/` and emit through the ordinary unversioned LangSmith pass.

### Sandboxes: distinct product surfaces

- **LangSmith Sandboxes** are isolated managed resources for risky code and filesystem work. The landing page owns user-facing SDK, CLI, snapshots, service URLs, auth proxy, mounts, permissions, and availability guidance. Restricted egress applies by default to non-Enterprise organizations and organizations that request it; the managed allowlist still blocks destinations added only to sandbox proxy configuration.
- **Managed Deep Agents sandboxes** are a deployment-owned integration with LangSmith Sandboxes. The `sandbox/` declaration enables the capability, and reuse is one sandbox per durable thread.
- **Deep Agents Code remote sandboxes** keep the local `dcode` LLM loop, memory, and tool dispatch local while filesystem and command calls run in the remote sandbox. This is not Managed Deep Agents hosting.
- **Self-hosted Sandboxes** are an infrastructure cluster under the self-hosted Additional features path. `sandbox-host` pods manage Firecracker microVMs on dedicated KVM-capable nodes, while shared storage makes persistent state independent of a node. A rolling host restart is not live migration; clients must tolerate interruption and reconnection.

### Managed Deep Agents and Deep Agents Code

Managed Deep Agents runs the OSS Deep Agents harness but shifts compilation and managed infrastructure to the `mda` CLI and runtime. Runtime server information contains verified caller identity, whereas client-provided context is not an authorization source. `mda deploy` compiles a project into a managed LangGraph app, syncs deploy-owned instructions and skills to Context Hub, uploads compiled source, and triggers a hosted Agent Server deployment that includes its API and MCP endpoint. Deployment routes instructions and skills to deploy-owned context, non-reserved `.env` values to hosted secrets without archiving them, project source to a `.mda/build` archive, and schedules to LangSmith cron jobs after deployment; CI needs a target-region API key because noninteractive deployment cannot use browser sign-in.

Deep Agents Code is an unversioned terminal-agent cluster. Its general settings resolve from administrator-owned `managed_config.toml`, `DEEPAGENTS_CODE_` overrides, canonical environment variables where applicable, user `config.toml`, then defaults; provider credentials use a separate resolver. The profile root is a trust boundary: `DEEPAGENTS_HOME` is captured from the inherited environment before dotenv loading, and project dotenv files cannot change it. The configuration navigation makes `configuration` a root whose credentials, config-file, hooks, and MCP-tools pages are children.

### SmithDB and OSS persistence

SmithDB is an opt-in columnar trace datastore for self-hosted LangSmith that uses object storage and per-pod disk cache and can serve ingestion and queries alongside ClickHouse. Its rollout is staged through service deployment, dual ingestion, optional historical migration, and query cutover; dual ingestion alone does not enable SmithDB-gated features, which require queries to use SmithDB.

LangGraph checkpointers persist graph state per thread, whereas stores hold application-defined key-value data across threads; Agent Server handles both persistence mechanisms when hosting a graph. Deep Agents long-term memory is filesystem-backed: backends determine where memory files are stored and who may access them, while short-term conversation memory is thread-scoped state.

## Safe change procedure

1. Start with the public URL and classify it as emitted MDX, navigation, redirect, or deployment-generated reference.
2. For ordinary OSS content, verify both Python and JavaScript output. For OpenWiki and Deep Agents Code, verify the single unversioned output and preserve unprefixed links.
3. Update `src/docs.json` explicitly for labels, placement, order, redirects, and OpenAPI declarations. The builder does not infer them.
4. For Managed Deep Agents, verify both language outputs and unversioned-to-Python redirects.
5. Keep LangSmith product content in `src/langsmith/`; use `docs.json` to project it as Gateway, No-code agents, Engine, managed Sandboxes, or self-hosted features.
6. Distinguish managed Sandbox usage, Managed Deep Agents integration, Deep Agents Code remote tools, OSS sandbox backends, and self-hosted sandbox infrastructure before editing.
7. Change endpoint reference through its OpenAPI input and declaration, never through generated endpoint MDX. Review the processor and refresh workflow for LangSmith REST changes.
8. Extend focused `tests/unit_tests/test_builder.py` coverage when source-family routing, preprocessing, special-family behavior, or source-tree safety changes.

## Related pages

- [Build system](/openwiki/architecture/build-system.md)
- [Preprocessing](/openwiki/concepts/preprocessing.md)
- [Versioning](/openwiki/concepts/versioning.md)
- [Reference docs](/openwiki/integrations/reference-docs.md)
- [Adding pages](/openwiki/operations/adding-pages.md)
- [LangSmith OpenAPI refresh](/openwiki/workflows/langsmith-openapi-refresh.md)
