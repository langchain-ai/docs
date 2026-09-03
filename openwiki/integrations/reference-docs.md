---
type: integration
title: API Reference Integration
description: How documentation links to generated API reference on reference.langchain.com and how OpenAPI specifications are managed.
tags: [api-reference, openapi, cross-references, reference.langchain.com, link-maps]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-759309714d08144a07e1b2e0
    resource: repo://.github/ISSUE_TEMPLATE/04-reference-docs.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-17f3856bce97f37118963062
    resource: repo://pipeline/preprocessors/handle_auto_links.py
  - id: openwiki-source-dca59d03b9433eea9242c2e4
    resource: repo://pipeline/preprocessors/link_map.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

## Overview

The LangChain documentation on `docs.langchain.com` integrates with auto-generated API reference hosted separately at `reference.langchain.com`. This page explains the relationship between the two sites, how cross-references work, and how OpenAPI specifications are versioned and updated.

**Key facts:**
- API reference is **generated and deployed outside this repository** for both [Python](https://reference.langchain.com/python/) and [JavaScript/TypeScript](https://reference.langchain.com/javascript/)
- Documentation links to reference via semantic cross-references like `@[StateGraph]`, resolved at build time
- Three OpenAPI specifications power LangSmith API documentation: one committed locally (Agent Server), one refreshed daily (LangSmith REST API), and one fetched at deploy time (Control Plane)
- Issues with reference.langchain.com are reported via a dedicated issue template; fixes happen in the reference docs repo, not here

## Cross-Reference Links to Reference.langchain.com

### Semantic Link Syntax

Authors write language-agnostic cross-references in markdown using the `@[ClassName]` syntax. These are resolved during the preprocessing pipeline to actual URLs on `reference.langchain.com`:

```markdown
Use @[StateGraph] to define your graph structure.
```

Becomes (for Python scope):

```markdown
Use [StateGraph](https://reference.langchain.com/python/langgraph/graph/state/StateGraph) to define your graph structure.
```

### Link Map Resolution

The preprocessor resolves cross-references using `SCOPE_LINK_MAPS`, which is built from `LINK_MAPS` in `pipeline/preprocessors/link_map.py`. The link map contains:

- **Python scope** (`"python"`): Maps to `https://reference.langchain.com/python/`
- **JavaScript scope** (`"js"`): Maps to `https://reference.langchain.com/javascript/`

Each scope maps symbol names (like `"StateGraph"`, `"ChatOpenAI"`, `"@[traceable]"`) to their reference page paths.

**Resolution behavior:**
- Scope is determined by language-specific conditional fences (`:::python` or `:::js`) in the markdown
- If a cross-reference is not found in the scope's link map, an info-level warning is logged and the reference is left unchanged (appears as literal `@[ClassName]` text)
- Some symbols are scope-agnostic and point to absolute URLs (e.g., cross-scope references like `"ModelProfile"` which has no JS equivalent, pointing to the Python reference)

### Custom Titles

Cross-references support custom titles:

```markdown
@[Custom Title][StateGraph]
```

Resolves to:

```markdown
[Custom Title](https://reference.langchain.com/python/langgraph/graph/state/StateGraph)
```

<!-- openwiki: broken internal link [url] file "url" does not exist. Fix the href or restore the target, then delete this comment. -->
Backticks are automatically preserved: `@[`CustomClass`]` becomes `[`CustomClass`](url)`.

## OpenAPI Specifications

Three OpenAPI specifications power API reference sections embedded in the docs site:

| Section | Location in Nav | Spec source | Generated under | Status |
|---------|-----------------|-------------|-----------------|--------|
| **Agent Server API** | Deploy → Get started → Reference | `src/langsmith/agent-server-openapi.json` | `/langsmith/agent-server-api/` | Committed locally |
| **Control Plane API** | Deploy → Get started → Reference | `https://api.host.langchain.com/openapi.json` | `/api-reference/` | Fetched at deploy time |
| **LangSmith REST API** | Monitor → Reference | `src/langsmith/langsmith-platform-openapi.json` | `/langsmith/smith-api/` | Refreshed daily |

### Agent Server OpenAPI

**Source:** `src/langsmith/agent-server-openapi.json` (committed to this repo)

**Updates:** Updated by PRs from the `langgraph-api` repository, titled `Update Agent ServerOpenAPI spec for API version X.Y.Z`. The spec captures the HTTP interface for the agent server.

**Validation:** Run `make check-openapi` before merging to ensure the spec is valid.

### Control Plane API

**Source:** `https://api.host.langchain.com/openapi.json` (no local file; fetched at deploy time)

**Updates:** The spec is fetched dynamically from the control plane service on every deployment. No local versioning.

**Rationale:** The control plane is a managed service; its API evolves independently of the docs repository.

### LangSmith REST API

**Source:** `src/langsmith/langsmith-platform-openapi.json` (committed to this repo)

**Updates:** Refreshed daily via GitHub Actions workflow (`.github/workflows/refresh-langsmith-openapi.yml`). The workflow:
1. Fetches the latest spec from the LangSmith platform
2. Runs `scripts/process_langsmith_openapi.py` to normalize it
3. Opens or appends to a standing `chore/refresh-langsmith-openapi` PR

**Important:** Do not edit this file by hand. It is overwritten automatically.

**Validation:** Run `make check-openapi` before merging to ensure the spec is valid.

## Building and Testing

### Local Development

During `make dev` or `make build`, Mintlify generates endpoint documentation pages from the OpenAPI specs at build time. These pages exist only in the `build/` output, not in the source tree.

### Broken Links Filtering

The `make broken-links` target runs Mintlify's link checker but filters out false positives:

- **Excluded by pattern:** `/langsmith/agent-server-api/`, `/api-reference/` (these are Mintlify-generated pages, not local files)
- **Snippet files:** Also excluded as they are imported with language-specific rewrites

The filtering is applied by `scripts/filter_mint_broken_links.py` after the Mintlify check completes.

### Validation

Before merging PRs that touch OpenAPI specs, always run:

```bash
make check-openapi
```

This validates that all three specs are syntactically correct JSON Schema / OpenAPI 3.1.0 documents.

## Reporting Issues with reference.langchain.com

Issues with **generated API reference content** (missing pages, broken links, incorrect type signatures) are reported to the **reference docs issue template** in this repo:

[Open a reference docs issue](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml)

This template routes the issue to maintainers who coordinate with the reference docs generation pipeline, which runs in a separate repository.

**Common issues:**
- Missing class or function pages
- Incorrect docstring rendering
- Broken or misleading type signatures
- Outdated content

**Note:** These issues are routed *from* this docs repo *to* the reference docs maintainers. The actual fixes happen in the reference generation tooling, not in source files here.

## Configuration and Maintenance

### Link Map Maintenance

The `LINK_MAPS` list in `pipeline/preprocessors/link_map.py` must be updated whenever:

1. **New symbols are added** to any LangChain, LangGraph, LangSmith, or Deep Agents packages
2. **Symbol paths change** on reference.langchain.com (e.g., module reorganizations)
3. **Cross-scope references** need to be maintained (e.g., Python-only symbols referenced in JS-scoped builds should point to the Python reference)

Each link map entry includes:
- **`host`**: The base URL for the reference site (with trailing slash)
- **`scope`**: The language scope (`"python"` or `"js"`)
- **`links`**: A dict mapping symbol names to relative paths under the host

### Related Files

| File | Purpose |
|------|---------|
| `pipeline/preprocessors/link_map.py` | Source of truth for cross-reference mappings |
| `pipeline/preprocessors/handle_auto_links.py` | Resolves `@[ClassName]` syntax in markdown |
| `pipeline/preprocessors/markdown_preprocessor.py` | Orchestrates preprocessing including cross-reference resolution |
| `src/langsmith/agent-server-openapi.json` | Committed OpenAPI spec for Agent Server |
| `src/langsmith/langsmith-platform-openapi.json` | Committed OpenAPI spec for LangSmith REST API (auto-refreshed) |
| `.github/workflows/refresh-langsmith-openapi.yml` | Daily refresh job for LangSmith spec |
| `scripts/process_langsmith_openapi.py` | Normalizes and processes the LangSmith spec |
| `scripts/filter_mint_broken_links.py` | Filters OpenAPI-generated pages from broken link reports |

## Invariants and Expectations

1. **Cross-references resolve at build time:** All `@[ClassName]` references are converted to markdown links during preprocessing. Authors never hardcode URLs to reference.langchain.com.

2. **OpenAPI specs are valid:** All committed specs pass `make check-openapi` validation. Specs are committed as valid JSON Schema / OpenAPI 3.1.0 documents.

3. **API reference is external:** The reference site is generated and deployed outside this repo. Issues with reference content (missing pages, broken links) are reported via the reference docs issue template, not fixed here.

4. **Local breaks are filtered:** `make broken-links` does not fail on Mintlify-generated pages that exist only in the build output (`/langsmith/agent-server-api/`, `/api-reference/`).

5. **LangSmith spec is auto-refreshed:** `src/langsmith/langsmith-platform-openapi.json` is automatically refreshed daily and should never be manually edited.

## Related Documentation

- **[Markdown Preprocessing Pipeline](/openwiki/concepts/preprocessing.md):** Details on conditional rendering, cross-reference resolution, and other transformations
- **[Build System](/openwiki/architecture/build-system.md):** Overview of the complete documentation build pipeline
- **[Link Rewriting and Versioning](/openwiki/concepts/versioning.md):** How language-specific links are rewritten during builds
