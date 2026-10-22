---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation or tooling change to its durable owner, relevant workflow, and proportionate validation. Use this map to distinguish authored inputs from generated, deployment-owned, and externally owned surfaces.
tags: [quickstart, documentation, tooling, validation, repository]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-21T08:20:13.723Z
sources:
  - id: openwiki-source-5c124605ed6e394bffee862c
    resource: repo://.github/workflows/_check-links.yml
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-67b847f2c6d57526390e4981
    resource: repo://.github/workflows/check-integration-repos.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-5153f86e64d6ee0b305f72b3
    resource: repo://.github/workflows/refresh-langsmith-openapi.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-ac1d4c62086c683f572e37b8
    resource: repo://docs-release-watch/memory.py
  - id: openwiki-source-12c8fb32a02de9dce773720f
    resource: repo://docs-release-watch/README.md
  - id: openwiki-source-644335efc60c7f4dd134c6a8
    resource: repo://docs-release-watch/schedules/daily_openwiki_check.py
  - id: openwiki-source-2b522af6f26794f2e71ccb4e
    resource: repo://docs-release-watch/tools/products.py
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
  - id: openwiki-source-bbd7fe20e2563e842ee80a78
    resource: repo://scripts/check_integration_repos.py
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
generated: { by: "openwiki/0.4.3", at: "2026-10-21T08:20:13.723Z" }
---

# Repository Wiki Quickstart

This repository builds the Mintlify documentation site at [docs.langchain.com](https://docs.langchain.com). It does **not** build the generated SDK reference at [reference.langchain.com](https://reference.langchain.com/python/). Start by identifying the durable input: a rendered page, sidebar item, provider table, endpoint page, or file in `build/` may be an outcome rather than the file to edit.

## Start with the repository contract

Read `AGENTS.md` before editing. It applies to manually authored `src/` content: do not edit `build/`; use Markdown-free frontmatter descriptions and Tabler icons; add new pages to `src/docs.json`; and test examples before including them. Repository-wide guidance belongs in `AGENTS.md`; task procedures belong in `.agents/skills/`. Run `make skills` in each Claude Code worktree to link those procedures into `.claude/skills/`.

The durable ownership split is:

- **Authored site inputs:** `src/` pages, assets, snippets, code samples, and `src/docs.json` navigation and site configuration.
- **Transformation and local tools:** `pipeline/`, `scripts/`, `Makefile`, and the installed `docs` command.
- **Generated or deployment-owned surfaces:** disposable `build/` output, generated tables and snippets, and Mintlify OpenAPI endpoint pages.
- **External surface:** `reference.langchain.com` is built outside this repository. File its issue template rather than looking for a local reference build.
- **Automation:** `.github/workflows/` owns CI and scheduled repository work; `docs-release-watch/` is a separate Managed Deep Agent deployment for release-driven documentation proposals.

Changes to a script, workflow, Make target, PR check, scheduled job, or skill require the `docs-tooling-notion` follow-up before PR handoff.

## Set up and preview

The project requires Python 3.13 or later. From the repository root:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes all Python dependency groups, installs project npm dependencies and the global Mintlify CLI, and links skills. `make dev` performs an initial build unless `--skip-build` is supplied, watches `src/`, and runs `mint dev --port 3000` from `build/`. It stops rather than serving stale output when the initial build fails. Open <http://localhost:3000> after startup.

`docs` is the Python console script behind the Make development and build wrappers; it provides `dev`, `build`, `mv`, `migrate`, and `migrate-docusaurus`. `mint` is the separate Mintlify CLI used from generated `build/` content for preview and rendered-site checks. For command details and operating caveats, see [Local Tooling and Commands](/openwiki/operations/cli-tools.md).

## Route the task

| Requested change | Durable owner — not the derived surface | Read first | Start validation with |
| --- | --- | --- | --- |
| Edit prose, frontmatter, an asset, CSS, or a reusable fragment | Applicable authored input under `src/` | [Repository Source Map](/openwiki/architecture/source-map.md) | `make lint_prose FILES="src/..."`; build when route or rendering changes. |
| Add, move, rename, retire, or expose a page | Page source, `src/docs.json` navigation, and any redirects | [Adding and Moving Documentation Pages](/openwiki/operations/adding-pages.md) | Build, then `make broken-links-with-anchors`. |
| Change an OSS route family, shared content, or a language-specific API name | The source subtree and conditional scope, not the menu label | [Cross-References and API Links](/openwiki/operations/cross-references.md) | `make check-cross-refs`, then inspect each emitted variant. |
| Change a builder, preprocessor, CLI, Make target, or helper script | `pipeline/`, `scripts/`, or `Makefile`, with focused tests | [Local Tooling and Commands](/openwiki/operations/cli-tools.md) | `make test TEST_FILE=tests/unit_tests/path_or_test.py`. |
| Change CI, a scheduled action, or a secret-bearing integration | `.github/workflows/` and the implementation it invokes | [GitHub Actions and CI Automation](/openwiki/integrations/github-actions.md) | Run the focused local check; preserve event, permissions, and credential boundaries. |
| Change an executable example or displayed extract | Executable source in `src/code-samples/` | [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md) | `make test-code-samples FILES="src/code-samples/..."`, then `make code-snippets`. |
| Change an integration listing, provider overview, or integration repository metadata | Hosted-guide `integration:` frontmatter, `packages.yml`, or `scripts/data/integration_external_docs.yaml` | [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md) | Validate URLs or run the applicable generator and review its diff. |
| Change a LangSmith OpenAPI input or endpoint-reference setup | OpenAPI declaration/specification and its workflow | [LangSmith OpenAPI Refresh](/openwiki/workflows/langsmith-openapi-refresh.md) | `make check-openapi` for the Agent Server spec; review the generated-spec workflow for the platform spec. |
| Report an SDK API-reference defect | The external reference-documentation build | [Reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml) | Route the issue; this repository has no reference build output. |

## Ownership rules that prevent unsafe edits

`src/docs.json` is the Mintlify navigation and site-configuration source of truth, but navigation does not determine source ownership or emitted routes. The build clears and recreates `build/`. Most OSS documentation becomes Python and JavaScript variants; language-owned OSS subtrees emit only their matching family. OpenWiki and Deep Agents Code are unversioned exceptions, ordinary LangSmith content is unversioned, and Managed Deep Agents files emit language-prefixed variants. Menu labels are not reliable ownership clues: **Build** mixes OSS and LangSmith content, **No-code agents** is Fleet, and **Deep Agents Code** is a Products and setup item.

For a shared OSS `@[ref]`, an unfenced reference must resolve in both Python and JavaScript scopes. Put language-only names in `:::python` or `:::js` blocks; `make check-cross-refs` enforces this source-level rule.

| Derived or externally controlled surface | Change instead | Follow-through |
| --- | --- | --- |
| `build/` | Authored `src/`, configuration, or pipeline input | Rebuild; the next full build deletes manual output edits. |
| `src/oss/python/integrations/providers/overview.mdx` | `packages.yml` or `pipeline/tools/partner_pkg_table.py` | Run `uv run python pipeline/tools/partner_pkg_table.py`; CI rejects drift. |
| `src/code-samples-generated/` and `src/snippets/code-samples/` | `src/code-samples/` | Test source, run `make code-snippets`, and review generated MDX. |
| Integration download/listing tables | Hosted-guide frontmatter or `scripts/data/integration_external_docs.yaml` | Run `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`, then regenerate. |
| LangSmith platform spec | `scripts/process_langsmith_openapi.py` and its scheduled refresh | Do not hand-edit `src/langsmith/langsmith-platform-openapi.json`; review the standing refresh PR. |
| Mintlify endpoint pages | Their declaration and committed or remote OpenAPI specification | They are generated at deployment and are absent from local `build/`. |
| `reference.langchain.com` | Its external build and issue-routing process | Do not expect a local generator or output directory. |

The committed Agent Server spec is updated by PRs from `langgraph-api`. The platform spec is refreshed daily from `api.smith.langchain.com`, with fleet and internal endpoints filtered for public documentation; the workflow reuses one standing `chore/refresh-langsmith-openapi` PR while it remains open.

## Integration and automation boundary

Integration discovery combines hosted-guide `integration:` frontmatter with third-party records in `scripts/data/integration_external_docs.yaml`. The refresh tool has an explicit `--check-docs-urls` mode, and core CI runs it to enforce accepted documentation-URL schemes.

A separate weekly **Check integration repos** workflow scans third-party `packages.yml` GitHub links, skipping `langchain-ai/*`. When a GitHub home is gone, it may safely repair a confirmed third-party rename or permanent external-docs redirect; it leaves live GitLab projects or reachable partner documentation for attention. Only when there is no live VCS or partner-docs alternative does it fully delist the package and related listing surfaces. The workflow writes evidence to the job summary and opens or appends to one standing draft PR on `chore/dead-integration-repos`; its contents and pull-request write permissions are therefore an automation boundary requiring review.

## Choose the narrowest validation boundary

Start with the check that proves the changed contract, then add a build or rendered-route check when the change crosses that boundary.

| Change boundary | Start with | What it covers |
| --- | --- | --- |
| Pipeline code, builder, preprocessor, generator, or helper | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | Focused pytest contract; network sockets are disabled except Unix sockets. |
| General Python tooling | `make test`; add `make lint` for tooling changes | Unit tests; lint checks formatting, lint, types, and source spelling. |
| Shared or conditional `@[ref]` content | `make check-cross-refs` | Resolution in every applicable source scope. |
| Authored prose | `make lint_prose FILES="src/path/to/page.mdx"` | Selected Vale rules. |
| Route, redirect, link, or anchor | `make broken-links-with-anchors` | Builds first, then checks links, anchors, and redirect destinations. |
| Agent Server OpenAPI specification | `make check-openapi` | Mintlify OpenAPI validation of the built input. |
| Runnable sample and generated display snippet | `make test-code-samples FILES="src/code-samples/..."` then `make code-snippets` | Source execution before generated-snippet refresh. |

Core CI runs for pull requests, pushes to `main`, and manual dispatch. It invokes reusable test, lint, and rendered link/OpenAPI checks, and separately detects merge conflict markers, unresolved source cross-references, invalid external integration-doc URL schemes, and provider-overview generation drift.

## Release-watch automation

`docs-release-watch` is a Managed Deep Agent deployment, not a GitHub Actions publisher. It covers OpenWiki, Deep Agents Python, Deep Agents Code, and Deep Agents JS. For the newest eligible release published 7–30 days earlier, its product registry and matching skill drive source-and-documentation research. An untracked user-facing gap can produce one Linear `DOC` issue and one **draft** documentation PR per feature.

Deployment-shared agent memory is an explicitly untrusted input boundary. It holds tracking URLs rather than credentials; tools, not memory, hold authority, and human review of draft-only PRs is the publication boundary.

## Continue by domain

- [Repository Source Map](/openwiki/architecture/source-map.md): source owners, navigation, route families, generated surfaces, and automation boundaries.
- [Local Tooling and Commands](/openwiki/operations/cli-tools.md): installation, Python pipeline versus Mintlify CLI, Make targets, and rendered-site checks.
- [Testing and Validation Overview](/openwiki/testing/test-overview.md): change-to-check selection and validation limits.
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md): executable sample, extraction, rendering, and tracing workflow.
- [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md): metadata, generated displays, repository-health decisions, and draft-PR lifecycle.
- [LangSmith OpenAPI Refresh](/openwiki/workflows/langsmith-openapi-refresh.md): public OpenAPI ingestion, filtering, standing PR, and deployment boundary.
- [GitHub Actions and CI Automation](/openwiki/integrations/github-actions.md): CI triggers, scheduled jobs, permissions, secrets, and review boundaries.
