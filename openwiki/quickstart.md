---
type: task-routing guide
title: Quickstart
description: Start here to route documentation changes to the correct source, generation, build, validation, and CI workflow. Covers local setup, navigation, preprocessing, executable samples, and integration catalog maintenance.
tags: [quickstart, documentation, workflows, build, validation]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-06T08:18:19.246Z
sources:
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-97746d8f3662d803e625550e
    resource: repo://.github/workflows/test-code-samples.yml
  - id: openwiki-source-4de47c60d7e3210385c34d35
    resource: repo://.github/workflows/update-package-downloads.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
generated: { by: "openwiki/0.4.3", at: "2026-09-06T08:18:19.246Z" }
---

# Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com) from authored files in `src/`. It covers LangChain, LangGraph, LangSmith, Deep Agents, and OpenWiki. `reference.langchain.com` is a separate, externally built API-reference site; do not look for its build output here.

## Start a local preview

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes Python dependencies, installs Node dependencies, and installs the Mint CLI. `make dev` runs the pipeline development command; use the Mintlify preview at `http://localhost:3000`. Edit `src/`, never `build/`: the pipeline regenerates `build/`, which Mintlify deploys.

## Choose the task, then its owner

| If you need to… | Start here | Key boundary |
| --- | --- | --- |
| Understand source locations, emitted routes, assets, or `docs.json` navigation | [Source, Navigation, and Output Map](/openwiki/architecture/source-map.md) | Source path and sidebar placement are separate contracts; `docs.json` names built routes and owns redirects. |
| Change build routing, language variants, or generated output | [Build System Architecture](/openwiki/architecture/build-system.md) | `pipeline/` transforms `src/` into `build/`; ordinary OSS content has Python and JavaScript variants, while OpenWiki and Deep Agents Code are unversioned exceptions. |
| Author `@[...]` references, conditional prose, CTA links, or imports | [Markdown Transformation and Cross-Reference Semantics](/openwiki/concepts/preprocessing.md) | Preprocessing resolves references and conditionals, then applies route and snippet-import rewrites; validate references from source rather than waiting for a build diagnostic. |
| Add, move, or retire a page | [Adding, Moving, and Retiring Documentation Pages](/openwiki/operations/adding-pages.md) | Update navigation and public redirects as well as source; use `uv run docs mv <old> <new>` for a move with link updates. |
| Make a runnable example appear as a documentation snippet | [Executable Code Samples to Embedded Snippets](/openwiki/workflows/code-samples.md) | The runnable program in `src/code-samples/` is the source of truth; generated snippet components are derived output. |
| Change providers, package metadata, or integration download tables | [Integration Catalog and Download-Data Generation](/openwiki/workflows/integration-catalog.md) | Update catalog inputs and regenerate outputs; do not hand-edit generated provider or download tables. |
| Select tests and validation for a change | [Testing and Validation Strategy](/openwiki/testing/test-overview.md) | Unit tests, build/link checks, generated catalogs, and live samples have intentionally different network and secret policies. |
| Understand PR checks and recurring automation | [GitHub Actions, CI, and Scheduled Maintenance](/openwiki/integrations/github-actions.md) | Core CI is separate from credentialed sample execution and scheduled maintenance that creates reviewable updates. |

## The normal content-change loop

1. Locate the authored page under `src/` and its destination in `src/docs.json`. Navigation labels do not necessarily match source directories.
2. Make the source change. For shared OSS pages, account for both Python and JavaScript output; use `:::python` and `:::js` only where content or references differ. Do not language-split OpenWiki or Deep Agents Code pages.
3. Use semantic `@[Reference]` links when an API symbol is in the link map. Run `make check-cross-refs` after changing those references or their map entries.
4. Build and validate the emitted site. Run focused tests first, then build-dependent checks when routes, imports, links, navigation, or OpenAPI inputs change.
5. Review generated changes rather than editing output. Commit source and the generated artifacts that the owning workflow requires.

The build order matters: `DocumentationBuilder` clears `build/`, emits versioned and unversioned content, copies shared resources, and produces Mintlify-ready output. Markdown processing resolves scoped references and conditional content before build-route rewrites select the target language. See [Build System Architecture](/openwiki/architecture/build-system.md) and [Markdown Transformation and Cross-Reference Semantics](/openwiki/concepts/preprocessing.md) before changing those behaviors.

## Commands by intent

| Intent | Command | Notes |
| --- | --- | --- |
| Install prerequisites | `make install` | Installs all dependency groups, Node packages, and Mint. |
| Preview while editing | `make dev` | Builds/watches the documentation and serves the local preview. |
| Create fresh output | `make build` | Regenerates `build/`. |
| Run deterministic pipeline tests | `make test` | Pytest runs with network sockets disabled; optionally narrow with `TEST_FILE=tests/unit_tests/test_builder.py`. |
| Check source API references | `make check-cross-refs` | Ensures `@[...]` resolves in each applicable language scope. |
| Validate built links and anchors | `make broken-links-with-anchors` | Builds first, then runs Mint from `build/` and filters documented false positives. |
| Validate the Agent Server OpenAPI input | `make check-openapi` | Builds first, then runs Mint's OpenAPI checker. |
| Check prose | `make lint_prose` | Installs and uses the Vale version pinned by repository configuration. |
| Run one executable example | `make test-code-samples FILES="src/code-samples/path/example.py"` | This is a live-runtime path, not a socket-isolated unit test. |
| Extract and generate sample snippets | `make code-snippets` | Produces tracked MDX snippets from marker-delimited executable sources. |

`make broken-links`, `make broken-links-with-anchors`, and `make check-openapi` own their required build step. Run `make build` directly when you need to inspect output or test a pipeline change independently.

## Executable samples: run, then generate

For a change beneath `src/code-samples/`, keep the complete executable program working before updating what readers see. The sample runner executes the source program; snippet markers select reader-facing fragments but do not alter runtime control flow. The generation flow is:

```bash
make test-code-samples FILES="src/code-samples/path/example.py"
make code-snippets
```

`make code-snippets` extracts marker-delimited fragments into a gitignored intermediate directory and generates MDX components under `src/snippets/code-samples/`. Update the importing authored page when a snippet ID, path, or language suffix changes, then run build/link validation. Samples may require provider keys, live services, or `POSTGRES_URI`; CI executes eligible same-repository PR samples with secrets and PostgreSQL, but skips fork PRs to protect those secrets.

## Integration catalog: change inputs, not tables

Two generated catalog families have different inputs:

- `packages.yml` drives the Python Popular providers overview. Regenerate it with `uv run python pipeline/tools/partner_pkg_table.py` after changing package metadata.
- Integration-page `integration:` frontmatter plus `scripts/data/integration_external_docs.yaml` drive language/component download snippets. Regenerate with `uv run python scripts/refresh_integration_downloads.py --write`; validate external documentation URL schemes with `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`.

The provider-overview regeneration is an ordinary PR drift check. Download data also has a weekly automation path that refreshes package counts and generated tables, then opens a PR when tracked output changes. External package services can be unavailable or rate-limited, so catalog refresh is not equivalent to an offline unit test.

## Before opening a PR

Use the smallest relevant checks, then expand to downstream checks when output is affected:

```bash
make test
make check-cross-refs
make broken-links-with-anchors
make check-openapi
```

Add `make test-code-samples FILES="..."` for changed samples and regenerate the appropriate catalog outputs for metadata or generator changes. GitHub Actions separately runs tests, linting, built-document link/OpenAPI validation, cross-reference checking, external-link safety, and provider-overview drift checks. Passing `make test` does not cover live samples; conversely, live samples are intentionally outside ordinary socket-isolated test execution.

## Non-negotiable conventions

- Author content in `src/`; treat `build/` and generated tables/snippets as outputs.
- Add a new navigable page to the appropriate `src/docs.json` product/menu/tab/group, using the correct built route. Preserve public moves with redirects.
- Use Tabler icons, not FontAwesome icons, and keep frontmatter descriptions free of Markdown.
- Test code examples before documenting them. Do not assume an extracted visible fragment was tested unless the executable path actually reaches it.
- Use the related pages above for the detailed contract before changing pipeline behavior, generated content, or CI.
