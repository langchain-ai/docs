---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation or tooling change to its durable owner, local command, focused validation, and detailed repository workflow. Use this page to avoid editing generated output or treating navigation as route generation.
tags: [quickstart, documentation, development, validation, mintlify]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-08T08:23:51.982Z
sources:
  - id: openwiki-source-5c124605ed6e394bffee862c
    resource: repo://.github/workflows/_check-links.yml
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-b481a230af378c0c50ed9994
    resource: repo://pipeline/commands/dev.py
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-17f3856bce97f37118963062
    resource: repo://pipeline/preprocessors/handle_auto_links.py
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-0a0a6c8d7a88288e6b6b9b5b
    resource: repo://scripts/check_cross_refs.py
  - id: openwiki-source-fd0cb9d6fca56bf4963559e9
    resource: repo://scripts/extract_code_snippets.py
  - id: openwiki-source-560bf24db9566b97ee19e383
    resource: repo://scripts/generate_code_snippet_mdx.py
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
generated: { by: "openwiki/0.4.3", at: "2026-10-08T08:23:51.982Z" }
---

# Repository Wiki Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com), not the SDK reference site at [reference.langchain.com](https://reference.langchain.com/python/). Start with a durable input, usually content in `src/`, site configuration, metadata, or generator code. Do not edit `build/`: every full build removes and recreates it. Report a problem with the external reference site through the [reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml).

## Start with the repository rules

Read `AGENTS.md` before changing documentation. It contains the repository-wide rules, including these non-negotiable constraints:

- Author manually maintained pages under `src/`, not `build/`.
- Add every new page to `src/docs.json`.
- Use frontmatter descriptions without Markdown, Tabler icons, and tested code examples.
- Use a task-specific procedure from `.agents/skills/` when it matches the work. Run `make skills` to link those skills into `.claude/skills/` for Claude Code.

The project requires Python 3.13 or later, Node.js, and `uv`.

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes every Python dependency group, installs project npm dependencies and the global Mintlify CLI, then links Claude Code skills. `make dev` builds first, watches `src/`, and serves `build/` with `mint dev --port 3000`; open <http://localhost:3000>. It exits rather than serving stale output if the initial build fails. Use `uv run pipeline dev --skip-build` only when an appropriate generated tree already exists.

For the preview loop, incremental behavior, and recovery, see [Local Development](/openwiki/workflows/local-development.md). For CLI inputs, outputs, and safety boundaries, see [CLI Tools](/openwiki/operations/cli-tools.md).

## Choose the durable owner

A visible documentation change may cross four separate planes: authored source, emitted route, Mintlify navigation or redirects, and deployment-generated API reference. They are related, but they are not interchangeable.

| Change | Edit first | Then use |
| --- | --- | --- |
| Add, move, rename, retire, or place a page in navigation | The appropriate `src/` source family and `src/docs.json` | [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) |
| Determine the owner of a route or language variant | The source family, not the reader-facing menu label | [Source Directory Map](/openwiki/architecture/source-map.md) and [Changing Versioned Content](/openwiki/workflows/versioned-content.md) |
| Change shared OSS content | `src/oss/`; fence language-specific material with `:::python` or `:::js` | [Source Directory Map](/openwiki/architecture/source-map.md) |
| Change Python- or TypeScript-owned OSS content | `src/oss/python/` or `src/oss/javascript/` | [Changing Versioned Content](/openwiki/workflows/versioned-content.md) |
| Change OpenWiki or Deep Agents Code | `src/oss/openwiki/` or `src/oss/deepagents/code/` | [Source Directory Map](/openwiki/architecture/source-map.md) |
| Change LangSmith, LLM Gateway, Fleet, Engine, Managed Deep Agents, or sandbox documentation | The applicable `src/langsmith/` subtree or flat page family | [Source Directory Map](/openwiki/architecture/source-map.md) |
| Change navigation labels, order, redirects, or OpenAPI declarations | `src/docs.json`, independently of source-tree layout | [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) |
| Change pipeline, preprocessing, or route emission | `pipeline/` and focused tests | [Testing Overview](/openwiki/testing/test-overview.md) |

`src/docs.json` is the Mintlify site-configuration and navigation source of truth. Its two product menus organize the agent development lifecycle and product/setup material; menu labels do not reliably identify the source directory. In particular, Build combines OSS and LangSmith content, Fleet appears as **No-code agents**, and Deep Agents Code has its own product/setup menu. Find a page by source ownership, then place or redirect its public route explicitly in `src/docs.json`.

The builder clears `build/`, produces Python and JavaScript OSS route variants, produces OpenWiki and Deep Agents Code without a language split, produces ordinary LangSmith content, and produces language-prefixed Managed Deep Agents variants. Navigation does not determine that emission behavior. Treat the generated tree as preview and validation evidence, never as an authoring surface.

For shared OSS `@[ref]` cross-references, an unfenced reference must resolve in both Python and JavaScript scopes. Put an API name that exists only in one scope in a `:::python` or `:::js` block, then run `make check-cross-refs`.

## Regenerate derivatives

When a visible file is derived, change its input or generator and regenerate it.

- **Provider overview:** `src/oss/python/integrations/providers/overview.mdx` is generated from `packages.yml` by `pipeline/tools/partner_pkg_table.py`. Update the metadata or generator, run `uv run python pipeline/tools/partner_pkg_table.py`, and commit the result. CI rejects drift.
- **Runnable examples and snippets:** `src/code-samples/` contains executable source. `make code-snippets` extracts marked snippets into `src/code-samples-generated/` and generates the imported MDX in `src/snippets/code-samples/`; neither generated location is the authored input. Test a changed sample with `make test-code-samples FILES="src/code-samples/..."`, then regenerate. TypeScript samples share `src/code-samples/package.json` and its committed lockfile. Follow [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md).
- **Integration listings:** hosted integration frontmatter and `scripts/data/integration_external_docs.yaml` feed generated listings. Validate URLs before regeneration with `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`. See [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md).
- **OpenAPI endpoint reference:** Mintlify generates configured endpoint pages during deployment. Change the specification or its `src/docs.json` declaration, not endpoint MDX or local build output. Use [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) for the local and deployment boundary.

## Run the smallest meaningful check

| Changed boundary | First command | Detailed guidance |
| --- | --- | --- |
| Pipeline, builder, preprocessor, or generator | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | [Testing Overview](/openwiki/testing/test-overview.md) |
| Source `@[ref]` or conditional content | `make check-cross-refs` | [Testing Overview](/openwiki/testing/test-overview.md) |
| Prose | `make lint_prose FILES="src/path/to/page.mdx"` | [Testing Overview](/openwiki/testing/test-overview.md) |
| Python tooling or spelling | `make lint` | [CLI Tools](/openwiki/operations/cli-tools.md) |
| Route, redirect, link, or anchor | `make broken-links-with-anchors` | [Testing Overview](/openwiki/testing/test-overview.md) |
| Agent Server OpenAPI | `make check-openapi` | [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) |
| Runnable example and displayed snippet | `make test-code-samples FILES="src/code-samples/..."` and `make code-snippets` | [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md) |

`make test` runs pytest with network sockets disabled except Unix sockets. Link and OpenAPI checks build first, so they validate generated output, redirects, and links rather than an unbuilt source edit. Core CI runs on pushes to `main`, pull requests, and manual dispatch; it runs tests, linting, built link and OpenAPI validation, cross-reference and external-integration URL checks, and generated-file drift checks. See [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) for CI behavior and failure triage.

## Finish safely

1. Confirm that the edit is authored input, metadata, configuration, or generator policy, not `build/` or a hosted rendering.
2. Identify the source family and emitted route variants before changing navigation. Update `src/docs.json` and redirects explicitly when needed.
3. Regenerate every affected derivative and inspect every language or unversioned route family that source owns.
4. Run focused source checks first, then run build, link, or deployment-facing validation for the boundary crossed. Record unavailable credentials or services.

## Task-routing map

- [Source Directory Map](/openwiki/architecture/source-map.md): Source ownership, route families, navigation, redirects, and generated references.
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md): Page creation, moves, retirement, navigation, redirects, and generated surfaces.
- [CLI Tools](/openwiki/operations/cli-tools.md): Make targets, the `docs` CLI, and operational safety boundaries.
- [Testing Overview](/openwiki/testing/test-overview.md): Focused, rendered, credentialed, remote, and hosted validation.
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md): Executable examples, snippet generation, traces, and refresh automation.
- [Changing Versioned Content](/openwiki/workflows/versioned-content.md): Shared, language-owned, unversioned, and Managed Deep Agents content.
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md): CI gates, trust boundaries, and sample workflows.
