---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation or tooling request to its durable owner, the relevant repository workflow, and the smallest validation boundary. Use this map before editing so generated output and externally owned surfaces are not changed directly.
tags: [quickstart, documentation, tooling, validation, repository]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-16T08:20:25.784Z
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
  - id: openwiki-source-6e6efa1569f158fcdb678ef0
    resource: repo://pipeline/cli.py
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
generated: { by: "openwiki/0.4.3", at: "2026-10-16T08:20:25.784Z" }
---

# Repository Wiki Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com), not the generated SDK reference at [reference.langchain.com](https://reference.langchain.com/python/). Start by locating the durable owner of the requested change. A rendered page, sidebar label, generated table, changelog, endpoint reference, or `build/` file can be a result rather than an authoring target.

Read `AGENTS.md` before editing. It is the repository-wide authoring guide: manually authored documentation belongs in `src/`, frontmatter descriptions contain no Markdown, new pages require `src/docs.json`, Tabler icons are required, and examples must be tested. Task-specific procedures live in `.agents/skills/`; `make skills` links that canonical tree into `.claude/skills/` for Claude Code. Use `docs-tooling-notion` before handoff whenever a script, workflow, Make target, PR check, scheduled job, or skill changes.

## Start locally

The project requires Python 3.13 or later. Run the standard setup and preview from the repository root:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes all Python dependency groups, installs project npm dependencies and the global Mintlify CLI. `make dev` performs an initial build, watches `src/`, and serves `build/` through Mintlify at <http://localhost:3000>. It exits when the initial build fails. Use `uv run docs dev --skip-build` only when an appropriate existing `build/` tree is available. The installed `docs` console script is the Python pipeline CLI; it provides `dev`, `build`, `mv`, and migration commands, while `mint` is the separate Mintlify CLI used for preview and rendered-site checks.

## Route the request before editing

| Requested change | Durable owner | First maintained guide | Smallest meaningful validation |
| --- | --- | --- | --- |
| Existing authored prose, MDX, reusable snippet, image, or style | Applicable authored input under `src/` | [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) | Focused prose check; add rendered link checking for routes or links. |
| Add, move, rename, retire, or expose a page | Source under `src/` **and** explicit `src/docs.json` navigation and redirects | [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) | Build plus `make broken-links-with-anchors`. |
| Source family, public route, language variant, menu placement, redirect, or OpenAPI declaration | Route-emitting source and `src/docs.json` are separate owners | [Source Directory Map](/openwiki/architecture/source-map.md) | Inspect all emitted routes; run link and redirect checks. |
| Shared or language-specific OSS content | The applicable `src/oss/` family and its conditional fences | [Versioned Content Workflow](/openwiki/workflows/versioned-content.md) | `make check-cross-refs`, then validate affected variants. |
| Build routing, preprocessing, CLI, Make target, helper, or pipeline test | `pipeline/`, `scripts/`, or `Makefile`, with focused tests | [Documentation Build System](/openwiki/architecture/build-system.md), [Builder and Pipeline Tests](/openwiki/testing/builder-tests.md) | `make test TEST_FILE=tests/unit_tests/path_or_test.py`. |
| GitHub workflow, CI check, scheduled job, secret-bearing automation, or failure triage | `.github/workflows/` and its invoked scripts | [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) | The focused local command; preserve event and credential boundaries. |
| Runnable example or extracted displayed snippet | Executable source in `src/code-samples/` | [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md) | `make test-code-samples FILES="src/code-samples/..."`, then `make code-snippets`. |
| `@[ref]` API reference, MDX link, redirect, or anchor | Authored page/link and source link map | [Cross-References and Links](/openwiki/operations/cross-references.md) | `make check-cross-refs` or `make broken-links-with-anchors`, as applicable. |
| Integration discovery, download, or featured listing | Hosted-guide `integration:` frontmatter or `scripts/data/integration_external_docs.yaml` | [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md) | `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`, then regenerate. |
| Provider overview table | `packages.yml` or `pipeline/tools/partner_pkg_table.py` | [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md) | Regenerate the overview and review its diff. |
| Cloud or Fleet changelog | Weekly changelog workflow, upstream PRs, rollout state, and review PR | [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md) | Its focused deterministic tests; use the workflow for publication. |
| LangSmith platform OpenAPI input | Scheduled refresh workflow and processor | [LangSmith OpenAPI Refresh](/openwiki/workflows/langsmith-openapi-refresh.md) | `make check-openapi`; do not hand-edit the transformed spec. |
| API endpoint reference declared in Mintlify | Committed specification, remote Control Plane specification, and `src/docs.json` declaration | [Reference Documentation Integrations](/openwiki/integrations/reference-docs.md) | `make check-openapi` where applicable; recognize endpoints are deployment-generated. |
| API reference at `reference.langchain.com` | External reference build | [Reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml) | Route the issue; this repository has no reference build output. |

## Keep the ownership planes separate

`src/docs.json` is the Mintlify navigation and site-configuration source of truth, but navigation does not select the source directory or cause route emission. The builder recreates `build/` on every full build. Most OSS content produces Python and JavaScript variants; language-owned OSS subtrees produce only the matching route family. Ordinary LangSmith content is unversioned, while OpenWiki and Deep Agents Code are unversioned OSS exceptions and direct Managed Deep Agents sources produce language-prefixed variants.

Choose the source family before a reader-facing menu label. The Build menu mixes OSS and LangSmith content, **No-code agents** is Fleet, and **Deep Agents Code** is a Products and setup item. Then identify every emitted route, update the actual `docs.json` menu branch, and add redirects deliberately if a published path changes. See [Source Directory Map](/openwiki/architecture/source-map.md) for the full model and [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) for the operational procedure.

For shared OSS `@[ref]` cross-references, an unfenced reference must resolve in both Python and JavaScript scopes. Place a language-only API name in a `:::python` or `:::js` block and run the strict `make check-cross-refs` source gate.

## Do not edit a derived surface

Never edit `build/`: it is disposable Mintlify output. Change the upstream authored input or generator, regenerate, and review the diff.

| Derived surface | Edit or operate instead | Required follow-through |
| --- | --- | --- |
| `build/` | Authored `src/`, configuration, or pipeline input | Rebuild; do not preserve a manual output edit. |
| `src/oss/python/integrations/providers/overview.mdx` | `packages.yml` or `pipeline/tools/partner_pkg_table.py` | Run `uv run python pipeline/tools/partner_pkg_table.py`; CI rejects drift. |
| `src/code-samples-generated/` and `src/snippets/code-samples/` | `src/code-samples/` | Test source, run `make code-snippets`, and review generated MDX. |
| Integration listings or download outputs | Hosted integration frontmatter or external-listing YAML | Validate URLs, regenerate, and review. |
| `src/langsmith/changelog.mdx` and `src/snippets/langsmith/fleet-changelog.mdx` | Weekly changelog pipeline and its upstream state | Use scheduled/manual workflow and review PR. |
| `src/langsmith/self-hosted-changelog.mdx` | Helm changelog automation and release owner | Route the correction to its external workflow owner. |
| `src/langsmith/langsmith-platform-openapi.json` | Refresh workflow and processor input | Do not hand-edit the transformed specification. |
| Mintlify endpoint pages | Declared specification and `src/docs.json` | Generated at deployment, not in local build output. |

`src/langsmith/agent-server-openapi.json` is also externally maintained by update PRs from `langgraph-api`, not ordinary prose. Use `make check-openapi` to validate the configured Agent Server specification.

## Select the narrowest validation boundary

Start with the smallest check that proves the changed contract, then add regeneration or rendered-route validation only where the change crosses that boundary. [Testing Overview](/openwiki/testing/test-overview.md) explains what each level proves and what it does not.

| Changed boundary | Start with | What it proves |
| --- | --- | --- |
| Pipeline, builder, preprocessor, generator, or helper | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | A focused pytest contract with network sockets disabled except Unix sockets. |
| General Python tooling | `make test` and, when appropriate, `make lint` | Deterministic test suite; formatting, lint, types, and source spelling for `make lint`. |
| Shared or conditional `@[ref]` content | `make check-cross-refs` | References resolve in each applicable source scope. |
| Authored prose | `make lint_prose FILES="src/path/to/page.mdx"` | Selected Vale prose rules. |
| Route, redirect, link, or anchor | `make broken-links-with-anchors` | Builds first, then checks links, anchors, and redirect destinations. |
| Agent Server OpenAPI specification | `make check-openapi` | Mintlify OpenAPI validation of the built input. |
| Runnable sample and displayed snippet | `make test-code-samples FILES="src/code-samples/..."` then `make code-snippets` | The selected executable source runs before generated snippets refresh. |

Core CI runs on pull requests, pushes to `main`, and manual dispatch. It invokes test, lint, and link/OpenAPI workflows, and separately checks merge markers, cross-references, external integration URLs, and generated provider-overview drift. The credentialed code-sample workflow runs for eligible pull requests affecting `src/code-samples/`, manual dispatch, and a monthly schedule; it skips fork pull requests because some samples require repository secrets.

## Continue by domain

- [Local Development Workflow](/openwiki/workflows/local-development.md): installation, preview, rebuilding, and environment failures.
- [Source Directory Map](/openwiki/architecture/source-map.md): source owners, route variants, navigation, redirects, and generated references.
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md): page lifecycle and safe public-route changes.
- [Documentation Preprocessing](/openwiki/concepts/preprocessing.md) and [Language Versions and Route Variants](/openwiki/concepts/versioning.md): transformations and both-language invariants.
- [Developer CLI Tools](/openwiki/operations/cli-tools.md) and [Agent Authoring Skills](/openwiki/operations/agent-skills.md): supported commands and task procedures.
- [Testing Overview](/openwiki/testing/test-overview.md): unit, generated-output, rendered, credentialed, and automation validation.
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md): CI gates, trusted writers, and secret boundaries.
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md), [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md), and [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md): generator-owned operational workflows.
