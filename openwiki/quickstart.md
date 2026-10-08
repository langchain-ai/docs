---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation or tooling change to its durable owner, local command, focused validation, and detailed repository wiki procedure. Use this page to avoid editing generated output or treating navigation as route generation.
tags: [quickstart, documentation, development, validation, mintlify]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-07T08:23:22.147Z
sources:
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
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-2d6fb565fec243c560da8729
    resource: repo://src/code-samples/package-lock.json
  - id: openwiki-source-e0401fc6d5f2a13d30455bd9
    resource: repo://src/code-samples/package.json
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
generated: { by: "openwiki/0.4.3", at: "2026-10-07T08:23:22.147Z" }
---

# Repository Wiki Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com), not the SDK reference site at [reference.langchain.com](https://reference.langchain.com/python/). Begin with a durable input—usually content under `src/`, configuration, metadata, or generator code. Never edit `build/`: a full build deletes and recreates it. Report problems with the external reference site through the [reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml).

## Start here

Read `AGENTS.md` before changing documentation. It is the repository-wide authoring guide; task-specific procedures live in `.agents/skills/`. Run `make skills` if Claude Code needs links to those skills in `.claude/skills/`.

The project requires Python 3.13 or later, Node.js, and `uv`.

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes Python dependency groups, installs project npm dependencies and the global Mintlify CLI, and links Claude Code skills. `make dev` performs a full build, watches `src/`, and runs `mint dev --port 3000` from `build/`; open <http://localhost:3000>. It stops rather than serving stale output when the initial build fails. Use `uv run pipeline dev --skip-build` only when a suitable generated tree already exists.

For the edit–preview loop, incremental behavior, recovery, and raw Mint command working-directory rule, see [Local Development](/openwiki/workflows/local-development.md).

## Choose the durable owner

A public documentation change can involve four distinct planes: authored source, emitted route, explicit Mintlify navigation or redirects, and deployment-generated API reference. They are related but not interchangeable.

| Change | Edit first | Then consult |
| --- | --- | --- |
| New, moved, retired, or renamed page; menu placement; redirect | The selected `src/` source family and `src/docs.json` | [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) |
| Which source family produces a public route | The source family, not the reader-facing menu name | [Source Directory Map](/openwiki/architecture/source-map.md) |
| Shared OSS content | `src/oss/`; use `:::python` or `:::js` for target-specific material | [Source Directory Map](/openwiki/architecture/source-map.md) and [Testing Overview](/openwiki/testing/test-overview.md) |
| Python- or TypeScript-owned OSS content | `src/oss/python/` or `src/oss/javascript/` | [Source Directory Map](/openwiki/architecture/source-map.md) |
| OpenWiki or Deep Agents Code | `src/oss/openwiki/` or `src/oss/deepagents/code/` | [Source Directory Map](/openwiki/architecture/source-map.md) |
| Ordinary LangSmith content or Managed Deep Agents | `src/langsmith/`; check whether the page is a Managed Deep Agents language variant | [Source Directory Map](/openwiki/architecture/source-map.md) |
| Navigation, labels, ordering, redirect, or OpenAPI declaration | `src/docs.json`, independently of source-tree layout | [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) |
| Pipeline, preprocessing, or route-emission behavior | `pipeline/` plus focused tests | [Source Directory Map](/openwiki/architecture/source-map.md) and [Testing Overview](/openwiki/testing/test-overview.md) |

`src/docs.json` is the site-configuration and navigation source of truth; it is not a scan of emitted files. A manually authored page normally needs an explicit navigation entry, while a route move also needs compatibility redirects. For shared OSS references, an unfenced `@[ref]` must resolve in both language scopes; put language-specific API names in `:::python` or `:::js` blocks and run `make check-cross-refs`.

The builder clears `build/`, emits Python and JavaScript OSS variants, emits OpenWiki and Deep Agents Code without a language split, emits ordinary LangSmith content, emits Managed Deep Agents language variants, and copies shared inputs. Treat the resulting tree as preview and validation evidence, never as an authoring surface.

## Regenerate rather than patch a derivative

When the visible file is derived, change its input or generator and regenerate it.

- **Provider overview:** `src/oss/python/integrations/providers/overview.mdx` is generated from `packages.yml` by `pipeline/tools/partner_pkg_table.py`. Update the metadata or generator, run `uv run python pipeline/tools/partner_pkg_table.py`, and commit the result. CI rejects a drifted overview.
- **Runnable examples and snippets:** `src/code-samples/` is executable source; generated snippets under `src/snippets/code-samples/` are not. Run the affected sample and `make code-snippets`. TypeScript samples share `src/code-samples/package.json` and its lockfile. Follow [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md).
- **Integration discovery:** hosted-guide `integration:` frontmatter and `scripts/data/integration_external_docs.yaml` feed listings. Validate before writing with `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`, then follow [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md).
- **OpenAPI endpoint reference:** Mintlify generates configured endpoint pages at deployment. Change the specification or `src/docs.json` declaration, not endpoint MDX or local build output. Use [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) for the local and deployment boundary.

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

`make test` runs pytest with network sockets disabled except Unix sockets. Live code samples may instead require credentials, providers, or local services; a skip or unavailable service is not equivalent to deterministic validation. A link or OpenAPI check builds first, so it tests the generated tree rather than an unbuilt source edit.

Core CI runs on pushes to `main`, pull requests, and manual dispatch. It includes tests, lint, link/OpenAPI validation, cross-reference and external documentation-URL checks, and generated-file drift checks. For fork safety, trusted writers, sample tracing, and CI failure triage, see [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md).

## Finish a change safely

1. Confirm the edit is in authored input, metadata, configuration, or generator policy—not `build/` or a hosted rendering.
2. Identify the emitted route family before changing menu navigation; update `src/docs.json` and redirects explicitly when applicable.
3. Regenerate and review every derivative after changing its durable input.
4. Inspect every language or unversioned route variant that the source family owns.
5. Run focused checks first, then build, link, or deployment-facing checks for the boundary crossed. Record unavailable credentials or services.

## Task-routing map

- [Source Directory Map](/openwiki/architecture/source-map.md) — source ownership, route families, navigation, redirects, and deployment-generated reference.
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) — safe page creation, moves, retirement, navigation, redirects, and generated surfaces.
- [Local Development](/openwiki/workflows/local-development.md) — setup, preview loop, full versus incremental build, and recovery.
- [CLI Tools](/openwiki/operations/cli-tools.md) — command inputs, outputs, and operational safety boundaries.
- [Testing Overview](/openwiki/testing/test-overview.md) — focused, rendered, credentialed, remote, and hosted validation.
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md) — executable examples, snippet generation, traces, and refresh automation.
- [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md) — integration metadata through generated discovery listings.
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) — CI gates, fork trust boundaries, and scheduled writers.
