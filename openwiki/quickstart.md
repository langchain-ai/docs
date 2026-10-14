---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation change to its durable source, configuration, generator, workflow, or external owner before choosing validation. Use this repository-specific map to avoid editing generated surfaces and to find the maintained guidance for product documentation work.
tags: [quickstart, documentation, mintlify, validation, repository]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-14T08:21:39.311Z
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
generated: { by: "openwiki/0.4.3", at: "2026-10-14T08:21:39.311Z" }
---

# Repository Wiki Quickstart

This repository builds the Mintlify documentation site at [docs.langchain.com](https://docs.langchain.com), not the generated SDK reference at [reference.langchain.com](https://reference.langchain.com/python/). Begin by locating the durable owner of a change. A rendered page, sidebar label, generated table, changelog, or endpoint page can be evidence of a result, but is not necessarily an authoring target.

> Verify factual product claims, examples, API names, UI labels, and policy details against their owning implementation or product source—not neighboring documentation. Related pages help identify what to check, but do not establish that a claim is true.

## Start a local preview

Read `AGENTS.md` first. It contains repository-wide authoring rules; `.agents/skills/` contains procedures for specific tasks. Run `make skills` to make those procedures available to Claude Code through `.claude/skills/`. For authored MDX, keep frontmatter descriptions free of Markdown, use Tabler icons, and test code examples before including them.

The project requires Python 3.13 or later, Node.js, and `uv`:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` syncs Python dependency groups, installs project npm dependencies and the Mintlify CLI, and links skills. `make dev` builds before it starts, watches `src/`, and serves `build/` through Mintlify at <http://localhost:3000>. It exits when the initial build fails. Use `uv run docs dev --skip-build` only when a suitable existing `build/` tree is already present.

## Classify the change before editing

| Requested change | Durable owner | First follow-up |
| --- | --- | --- |
| Revise a normal documentation page, reusable snippet, image, or style | The applicable manually authored input under `src/` | Follow authoring rules, verify product facts at their source, and test included examples. |
| Add, move, rename, retire, or expose a page | The selected `src/` source **and** `src/docs.json` | Update explicit navigation and necessary redirects. See [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md). |
| Change site settings, menu labels/order, redirects, or an OpenAPI declaration | `src/docs.json` | Treat navigation as configuration, not a directory scan or route generator. |
| Change build routing, preprocessing, a generator, or a CLI behavior | `pipeline/`, `scripts/`, or `Makefile`, with focused tests | Use [Testing Overview](/openwiki/testing/test-overview.md) and invoke the tooling-documentation procedure required by `AGENTS.md` for tooling changes. |
| Change a runnable example or an extracted snippet | Executable source in `src/code-samples/` | Run the affected sample, then regenerate derived snippets. |
| Change an integration listing | Hosted integration `integration:` frontmatter or `scripts/data/integration_external_docs.yaml` | Validate URLs, regenerate, and review the derivative. See [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md). |
| Change Cloud or Fleet changelog wording or state | The weekly changelog pipeline and its upstream merged-PR/rollout inputs | Do not hand-author a normal changelog update; see [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md). |
| Change a self-hosted changelog | The helm changelog bot or its upstream release process | Do not edit `src/langsmith/self-hosted-changelog.mdx` as ordinary prose. |
| Fix `reference.langchain.com` SDK reference | The external reference build | This repository does not build it; use the [reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml). |

## Keep source ownership separate from navigation

`src/docs.json` is the source of truth for Mintlify configuration and navigation. It does not determine where a page is authored or how the builder emits it. Menu labels are reader-facing taxonomy: the Build menu mixes OSS and LangSmith content, **No-code agents** is the Fleet documentation cluster, and **Deep Agents Code** is a product/setup item.

The builder clears and recreates `build/`. It emits most shared OSS content as Python and JavaScript variants; language-owned OSS sources emit only their matching variant. Ordinary LangSmith content is unversioned. OpenWiki and Deep Agents Code are unversioned OSS exceptions, while direct Managed Deep Agents source files produce language-prefixed variants. Therefore, choose the source family before adding a navigation entry, and inspect every output family that the source owns.

For shared OSS `@[ref]` cross-references, an unfenced reference must resolve for both Python and JavaScript. Put an API name available in only one scope inside a `:::python` or `:::js` fence, then run `make check-cross-refs`.

For the complete source-to-route model, including redirects and deployment-generated API reference, see [Source Directory Map](/openwiki/architecture/source-map.md). [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) turns that model into a page-change procedure.

## Do not edit derived documentation

`build/` is generated preview and deployment input: never edit it. The same rule applies to derived product surfaces. Change the upstream input or generator, regenerate, and review the resulting diff.

| Derived surface | Change instead | Regenerate or validate |
| --- | --- | --- |
| `src/oss/python/integrations/providers/overview.mdx` | `packages.yml` or `pipeline/tools/partner_pkg_table.py` | `uv run python pipeline/tools/partner_pkg_table.py`; CI rejects drift. |
| `src/code-samples-generated/` and `src/snippets/code-samples/` | `src/code-samples/` | Test the sample, then run `make code-snippets`. |
| Integration download/featured snippets | Hosted-guide frontmatter or external-listing YAML | `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`, then regenerate with `--write` when appropriate. |
| `src/langsmith/changelog.mdx` and `src/snippets/langsmith/fleet-changelog.mdx` | Weekly changelog pipeline and upstream PR/rollout state | Use the scheduled/manual changelog process and review PR. |
| `src/langsmith/self-hosted-changelog.mdx` | Helm changelog automation | Route the fix to the owning release automation. |
| `src/langsmith/langsmith-platform-openapi.json` | Its refresh workflow/processor and external specification | Do not hand-edit the transformed specification. |
| Mintlify-generated OpenAPI endpoint pages | The declared OpenAPI specification or `src/docs.json` declaration | Endpoint pages are generated during deployment, not normal authored pages or local build output. |

`src/langsmith/agent-server-openapi.json` is also not ordinary prose: it is updated by PRs from the `langgraph-api` repository. Use `make check-openapi` to validate the Agent Server specification.

## Choose focused validation

Run the smallest check that exercises the boundary changed, then add build-oriented validation for route, navigation, redirect, or rendered-site changes.

| Changed boundary | Start with | What it establishes |
| --- | --- | --- |
| Pipeline, builder, preprocessor, generator, or workflow helper | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | Pytest runs with network sockets disabled except Unix sockets; mock network behavior in unit tests. |
| Shared or conditional `@[ref]` content | `make check-cross-refs` | Source references resolve in their applicable language scope. |
| Documentation prose | `make lint_prose FILES="src/path/to/page.mdx"` | Runs the pinned Vale workflow for the selected file. |
| Python tooling, formatting, types, or spelling | `make lint` | Runs Ruff formatting/lint checks, `ty`, and source spelling checks. |
| Route, redirect, link, or anchor | `make broken-links-with-anchors` | Builds first, then checks links, anchors, and redirect destinations, filtering known generated-reference and standalone-snippet noise. |
| Agent Server OpenAPI | `make check-openapi` | Builds first and validates the configured Agent Server specification. |
| Runnable code sample and displayed snippet | `make test-code-samples FILES="src/code-samples/..."` followed by `make code-snippets` | Executes selected source samples, then refreshes derived snippet artifacts. |

Core CI runs for pull requests, pushes to `main`, and manual dispatch. It runs reusable test, lint, and link/OpenAPI jobs and separately checks merge markers, cross-references, external integration URLs, and provider-overview drift. The credentialed code-sample workflow runs for relevant pull requests, manual dispatch, and monthly schedules; it skips fork pull requests because samples may need repository secrets. See [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) for CI trust boundaries and failure triage.

## Finish a change safely

1. Confirm that the edit belongs to authored content, configuration, metadata, generator policy, workflow, or an external owner—not a generated result.
2. Verify every factual assertion and example against its owning source. Do not infer behavior from nearby docs or sidebar placement.
3. For a page or product update, identify source ownership and every emitted route family before changing `src/docs.json`; add redirects deliberately when public paths change.
4. Regenerate affected derivatives, inspect the result, and run the focused source check before build/link validation.
5. For workflow, script, Makefile, check, or skill changes, complete the tooling-documentation follow-up required by `AGENTS.md`.

## Continue in the maintained hierarchy

- [Source Directory Map](/openwiki/architecture/source-map.md): source families, emitted routes, navigation projections, redirects, and generated references.
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md): safe page creation, moves, retirement, navigation, redirects, and generated-surface ownership.
- [Agent Authoring Skills](/openwiki/operations/agent-skills.md): canonical task procedures and derived instruction surfaces.
- [Testing Overview](/openwiki/testing/test-overview.md): focused unit, source, generated-output, rendered, and credentialed validation.
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md): CI gates, previews, automation trust boundaries, and scheduled writers.
- [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md): weekly Cloud/Fleet generation, held state, review, and separate self-hosted releases.
- [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md): integration metadata, safe external URLs, generated tables, and contributor intake.
