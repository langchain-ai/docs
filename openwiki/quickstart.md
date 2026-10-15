---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation change to its durable source, configuration, generator, workflow, or external owner before selecting validation. Use this repository-specific map to avoid generated surfaces and find the maintained guidance for documentation work.
tags: [quickstart, documentation, mintlify, validation, repository]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-15T08:21:56.046Z
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
generated: { by: "openwiki/0.4.3", at: "2026-10-15T08:21:56.046Z" }
---

# Repository Wiki Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com), not the generated SDK reference at [reference.langchain.com](https://reference.langchain.com/python/). Start by identifying the durable owner of a requested change. A rendered page, sidebar label, generated table, changelog, or endpoint page may be a result rather than an authoring target.

Read `AGENTS.md` before editing. It supplies repository-wide rules: work in authored `src/` content, use plain-text frontmatter descriptions and Tabler icons, update `src/docs.json` for a new page, and test examples before including them. Verify product facts and examples against their owning implementation or product source, not adjacent documentation.

## Set up a local preview

The project requires Python 3.13 or later. `make install` synchronizes Python dependency groups, installs project npm dependencies and the global Mintlify CLI, then links authoring skills for Claude Code.

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make dev` performs an initial build, watches `src/`, and serves `build/` through Mintlify at <http://localhost:3000>. It exits if the initial build fails. Use `uv run docs dev --skip-build` only when an appropriate existing `build/` tree is available.

`AGENTS.md` is the global guide; task-specific procedures live in `.agents/skills/`. Run `make skills` to link that canonical tree into `.claude/skills/` for Claude Code. Use the relevant procedure—for example, `add-docs-page` for page lifecycle, `docs-edit` for an existing PR, `docs-code-samples` for executable examples, and `verify-against-source` for factual claims. A change to a script, workflow, Make target, check, scheduled job, or skill also requires the `docs-tooling-notion` follow-up before handoff.

## Route the request before editing

| Requested change | Durable owner | Next step |
| --- | --- | --- |
| Ordinary documentation, reusable MDX, images, or styles | The applicable authored input under `src/` | Verify facts at their source and validate the affected boundary. |
| Add, move, rename, retire, or expose a page | Source under `src/` **and** `src/docs.json` | Update explicit navigation and needed redirects. See [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md). |
| Menu labels, ordering, site settings, redirects, or OpenAPI declarations | `src/docs.json` | Treat navigation as explicit configuration, not a directory scan. |
| Build routing, preprocessing, generator, or CLI behavior | `pipeline/`, `scripts/`, or `Makefile` plus focused tests | Start with [Testing Overview](/openwiki/testing/test-overview.md). |
| Runnable example or displayed extracted snippet | Source in `src/code-samples/` | Test source first, then run `make code-snippets`; do not author generated snippets. |
| Integration discovery listing | Hosted-guide `integration:` frontmatter or `scripts/data/integration_external_docs.yaml` | Validate URLs with `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`, then regenerate as needed. |
| Cloud or Fleet changelog | Weekly changelog pipeline and its upstream PR/rollout inputs | Do not hand-edit it; see [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md). |
| Self-hosted changelog | Helm changelog automation or its release input | Do not treat `src/langsmith/self-hosted-changelog.mdx` as ordinary prose. |
| SDK reference at `reference.langchain.com` | External reference build | Use the [reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml). |

## Keep ownership, routes, and navigation separate

`src/docs.json` is the source of truth for Mintlify site configuration and navigation, but it does not choose an authored source directory or make the builder emit a route. Menu labels are reader-facing taxonomy: Build mixes OSS and LangSmith content, **No-code agents** is the Fleet cluster, and **Deep Agents Code** is a product/setup item.

A full build removes and recreates `build/`. Most shared OSS content produces Python and JavaScript routes; language-owned OSS produces only the corresponding route family. Ordinary LangSmith content is unversioned. OpenWiki and Deep Agents Code are unversioned OSS exceptions, while direct Managed Deep Agents sources produce language-prefixed variants. Select the source family first, then inspect every emitted route family and add the appropriate explicit navigation entries.

For shared OSS `@[ref]` cross-references, an unfenced reference must resolve in both Python and JavaScript scopes. Put names available in only one scope inside `:::python` or `:::js` blocks and run `make check-cross-refs`.

For the route model, redirects, source-family exceptions, and deployment-generated API reference, see [Source Directory Map](/openwiki/architecture/source-map.md). For the operational page lifecycle, see [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md).

## Do not edit generated surfaces

Never edit `build/`; the builder recreates it. Change an upstream input or generator, regenerate, and review the resulting diff.

| Derived surface | Change instead | Regenerate or validate |
| --- | --- | --- |
| `src/oss/python/integrations/providers/overview.mdx` | `packages.yml` or `pipeline/tools/partner_pkg_table.py` | Run `uv run python pipeline/tools/partner_pkg_table.py`; CI rejects drift. |
| `src/code-samples-generated/` and `src/snippets/code-samples/` | `src/code-samples/` | Test the source and run `make code-snippets`. |
| Integration download and featured outputs | Hosted frontmatter or external-listing YAML | Validate URLs, regenerate, and review. |
| `src/langsmith/changelog.mdx` and `src/snippets/langsmith/fleet-changelog.mdx` | Weekly changelog pipeline and upstream state | Use the scheduled or manual workflow and review PR. |
| `src/langsmith/self-hosted-changelog.mdx` | Helm changelog automation | Route the correction to its release owner. |
| `src/langsmith/langsmith-platform-openapi.json` | Refresh workflow and processor input | Do not hand-edit the transformed specification. |
| Mintlify OpenAPI endpoint pages | Declared specification and `src/docs.json` | These pages are generated at deployment, not in the local build. |

`src/langsmith/agent-server-openapi.json` is likewise not ordinary prose: PRs from `langgraph-api` update it. Run `make check-openapi` for the configured Agent Server specification.

## Choose focused validation

Run the smallest check that proves the changed boundary, then add rendered-route validation for navigation, redirects, anchors, or site output.

| Changed boundary | Start with | What it establishes |
| --- | --- | --- |
| Pipeline, builder, preprocessor, generator, or workflow helper | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | Pytest runs with network sockets disabled except Unix sockets. |
| Shared or conditional `@[ref]` content | `make check-cross-refs` | References resolve in applicable language scope. |
| Documentation prose | `make lint_prose FILES="src/path/to/page.mdx"` | Vale checks selected prose with the repository's pinned workflow. |
| Python tooling or source spelling | `make lint` | Formatting, lint, type, and spelling checks run. |
| Route, redirect, link, or anchor | `make broken-links-with-anchors` | It builds first, then checks links, anchors, and redirect destinations. |
| Runnable sample and displayed snippet | `make test-code-samples FILES="src/code-samples/..."` then `make code-snippets` | The selected source runs before derived artifacts refresh. |

Core CI runs on pull requests, pushes to `main`, and manual dispatch. It runs test, lint, and link/OpenAPI work, plus cross-reference, external integration-URL, and generated-provider-overview checks. The credentialed code-sample workflow runs for eligible pull requests, manual dispatch, and monthly schedules; fork pull requests are skipped because samples can require repository secrets. See [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) for trust boundaries and failure triage.

## Finish safely

1. Confirm that the edit belongs to authored content, configuration, generator input, workflow, or an external owner—not a generated result.
2. Verify factual assertions and examples against their owner.
3. For a page change, determine every emitted route before updating `src/docs.json`; add redirects deliberately when public paths change.
4. Regenerate derivatives, review their diff, and run focused checks before build and link validation.
5. Complete the tooling-documentation follow-up for changes to repository tooling.

## Continue in the maintained hierarchy

- [Source Directory Map](/openwiki/architecture/source-map.md): source families, routes, navigation, redirects, and generated references.
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md): page creation, moves, retirement, navigation, redirects, and ownership.
- [Agent Authoring Skills](/openwiki/operations/agent-skills.md): global versus task-specific authoring guidance.
- [Testing Overview](/openwiki/testing/test-overview.md): focused unit, generated-output, rendered, and credentialed validation.
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md): CI gates, trusted writers, and scheduled automation.
- [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md): weekly Cloud/Fleet lifecycle and review gate.
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md): executable source, extracted snippets, traces, and CI refresh behavior.
