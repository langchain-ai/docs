---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation change to its durable input, configuration, generator, or external owner before choosing local commands and validation. Use this map to avoid editing generated output or confusing navigation with route generation.
tags: [quickstart, documentation, mintlify, validation, repository]
sources:
  - id: openwiki-source-5c124605ed6e394bffee862c
    resource: repo://.github/workflows/_check-links.yml
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-97746d8f3662d803e625550e
    resource: repo://.github/workflows/test-code-samples.yml
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
generated: { by: "openwiki/0.4.3", at: "2026-10-10T08:20:12.163Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-10-10T08:20:12.163Z
---

# Repository Wiki Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com). It does not build the generated SDK reference at [reference.langchain.com](https://reference.langchain.com/python/). Start with a durable input: authored source, navigation/configuration, metadata, or generator code. Do not edit `build/`; every full build deletes and recreates it. Report problems with the external reference site through the [reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml).

## Start here

Read `AGENTS.md` before changing content. It defines repository-wide authoring rules and directs task-specific work to `.agents/skills/`. Run `make skills` to link those skills into `.claude/skills/` for Claude Code. Ask for clarification rather than assume missing requirements, and ground examples, policy details, and use-case claims in supplied or existing source. When changing a script, workflow, Makefile target, PR check, scheduled job, or skill, invoke `docs-tooling-notion` before handoff.

The project requires Python 3.13 or later, Node.js, and `uv`:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes all Python dependency groups, installs project npm dependencies and the global Mintlify CLI, and links skills. `make dev` performs an initial build, watches `src/`, and serves the generated `build/` tree at <http://localhost:3000>. It stops if that initial build fails. Use `uv run pipeline dev --skip-build` only when an appropriate generated tree already exists.

## Route the change by owner

A page's source owner, emitted route family, Mintlify navigation, and deployment-generated reference surface are separate concerns. Reader-facing menu labels do not determine source ownership or builder behavior.

| If the task is to... | Change the durable owner | Follow-up |
| --- | --- | --- |
| Write or revise a maintained page | The applicable `src/` page, reusable snippet, or asset | Keep frontmatter descriptions free of Markdown, use Tabler icons, and test included examples. |
| Add, move, rename, retire, or place a page | Its `src/` source plus `src/docs.json` | Add navigation; update redirects for moved, renamed, or removed public paths. See [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md). |
| Find the correct source subtree or route family | The source family, not the menu label | See [Source Directory Map](/openwiki/architecture/source-map.md) and [Versioned Documentation and Routes](/openwiki/concepts/versioning.md). |
| Change site settings, menu order, labels, redirects, or OpenAPI declarations | `src/docs.json` | Navigation is explicit configuration, not route generation. |
| Change a processor, build rule, or emitted route | `pipeline/` and its focused tests | See [Testing Overview](/openwiki/testing/test-overview.md). |
| Change a runnable example or displayed extracted snippet | `src/code-samples/` | Test it, then regenerate snippets. See [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md). |
| Change an integration listing | Hosted integration frontmatter or `scripts/data/integration_external_docs.yaml` | Validate URLs and regenerate. See [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md). |
| Fix generated API reference at `reference.langchain.com` | The owning external reference build, not this repository | File the reference-documentation issue. |

`src/docs.json` is the Mintlify site-configuration and navigation source of truth. Add new pages there. Its two product menus organize the agent-development lifecycle and product/setup material, but labels are not a source map: Build mixes OSS and LangSmith content, Fleet is labeled **No-code agents**, and Deep Agents Code is a product/setup item.

The builder clears `build/` and emits Python and JavaScript OSS variants, unversioned OpenWiki and Deep Agents Code content, ordinary LangSmith content, language-prefixed Managed Deep Agents variants, and shared files. Source ownership and emitted route family are therefore independent of Mintlify navigation. Treat generated files as preview and validation evidence, not as an authoring surface.

For shared OSS `@[ref]` cross-references, an unfenced reference must resolve in both Python and JavaScript scopes. Put an API name that exists in only one scope inside a `:::python` or `:::js` block, then run `make check-cross-refs`.

## Regenerate instead of editing a derivative

When a visible file is derived, edit its input or generator and regenerate it:

- **Provider overview**: `src/oss/python/integrations/providers/overview.mdx` is generated by `pipeline/tools/partner_pkg_table.py` from `packages.yml`. Update the generator or metadata, run `uv run python pipeline/tools/partner_pkg_table.py`, and commit the result. CI rejects drift.
- **Runnable samples and snippets**: `src/code-samples/` is executable source. `make code-snippets` extracts marked blocks into `src/code-samples-generated/` and creates imported MDX in `src/snippets/code-samples/`; neither output is authored input. Test a changed sample first with `make test-code-samples FILES="src/code-samples/..."`, then regenerate.
- **Integration listings**: the listing generator combines hosted-guide `integration:` frontmatter with `scripts/data/integration_external_docs.yaml`. Check accepted documentation URLs before regeneration with `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`.
- **OpenAPI endpoint pages**: Mintlify generates configured endpoint reference during deployment. Change the specification or its `src/docs.json` declaration, not local build output. See [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md).

## Choose focused validation

| Changed boundary | Start with | Why |
| --- | --- | --- |
| Pipeline, builder, preprocessor, or generator | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | `make test` runs pytest with network sockets disabled except Unix sockets. |
| Source `@[ref]` or conditional content | `make check-cross-refs` | Rejects a shared unfenced reference that does not resolve for every emitted scope. |
| Page prose | `make lint_prose FILES="src/path/to/page.mdx"` | Runs the repository's pinned Vale workflow. |
| Python tooling or spelling | `make lint` | Checks formatting, linting, types, and source spelling. |
| Route, redirect, link, or anchor | `make broken-links-with-anchors` | Builds first, then checks links, anchors, and redirect destinations. |
| Agent Server OpenAPI | `make check-openapi` | Builds first and validates the configured Agent Server spec. |
| Runnable example and its rendered snippet | `make test-code-samples FILES="src/code-samples/..."` and `make code-snippets` | Executes the selected source sample, then refreshes its derived snippet artifacts. |

Core CI runs on pushes to `main`, pull requests, and manual dispatch. It runs tests, lint, built link and OpenAPI validation, strict cross-reference and external-integration URL checks, and the provider-overview drift check. The code-sample workflow runs for relevant pull requests, manually, and monthly; it skips fork pull requests because some samples need repository secrets. See [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) for CI behavior and failure triage.

## Finish safely

1. Confirm that the edit targets authored input, configuration, metadata, or generator policy—not `build/` or a hosted rendering.
2. Identify source ownership and emitted route variants before changing navigation. Update `src/docs.json` and redirects explicitly when needed.
3. Regenerate affected derivatives, then inspect every language or unversioned route family the source owns.
4. Run the smallest source check first. Run build, link, or deployment-facing validation when the change crosses that boundary.

## Task-routing map

- [Source Directory Map](/openwiki/architecture/source-map.md): source ownership, route families, navigation, redirects, and generated references.
- [Versioned Documentation and Routes](/openwiki/concepts/versioning.md): shared, language-owned, unversioned, and Managed Deep Agents content.
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md): page creation, moves, retirement, navigation, redirects, and deployment surfaces.
- [Testing Overview](/openwiki/testing/test-overview.md): focused, rendered, credentialed, remote, and hosted validation.
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md): executable examples, snippet generation, trace refresh, and sample automation.
- [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md): integration metadata, URL validation, and listing refresh.
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md): CI gates, trust boundaries, and sample workflows.
