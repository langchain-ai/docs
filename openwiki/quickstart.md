---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation or tooling request to its durable owner, the relevant repository workflow, and the smallest validation boundary. Use this map before editing so generated output and externally owned surfaces are not changed directly.
tags: [quickstart, documentation, tooling, validation, repository]
sources:
  - id: openwiki-source-5c124605ed6e394bffee862c
    resource: repo://.github/workflows/_check-links.yml
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-6d4b4e707b8d60b6ccfa3425
    resource: repo://.github/workflows/openwiki-update.yml
  - id: openwiki-source-97746d8f3662d803e625550e
    resource: repo://.github/workflows/test-code-samples.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-d282f31d82e34c26a1df41a1
    resource: repo://docs-release-watch/instructions.md
  - id: openwiki-source-ac1d4c62086c683f572e37b8
    resource: repo://docs-release-watch/memory.py
  - id: openwiki-source-12c8fb32a02de9dce773720f
    resource: repo://docs-release-watch/README.md
  - id: openwiki-source-2b522af6f26794f2e71ccb4e
    resource: repo://docs-release-watch/tools/products.py
  - id: openwiki-source-0a04d5d3ade1211f24c16b3b
    resource: repo://docs-release-watch/tools/releases.py
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
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
generated: { by: "openwiki/0.4.3", at: "2026-10-17T08:17:43.098Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-10-17T08:17:43.098Z
---

# Repository Wiki Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com), not the generated SDK reference at [reference.langchain.com](https://reference.langchain.com/python/). Before changing a rendered page, sidebar label, generated table, changelog, endpoint reference, or `build/` file, identify its durable owner: it may be an output rather than authored input.

Read `AGENTS.md` first. It defines repository-wide authoring rules: work in manually authored `src/` content, keep frontmatter descriptions free of Markdown, use Tabler icons, update `src/docs.json` for new pages, and test examples. Procedures that apply only to a class of task live in `.agents/skills/`; run `make skills` to link them for Claude Code. A change to a script, workflow, Make target, PR check, scheduled job, or skill also requires the `docs-tooling-notion` follow-up before PR handoff.

## First local preview

The project requires Python 3.13 or later. From the repository root:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes every Python dependency group, installs project npm dependencies and the global Mintlify CLI, then links skills. `make dev` runs an initial build, watches `src/`, and runs `mint dev --port 3000` from `build/`; preview is at <http://localhost:3000>. It stops rather than serving stale content if the initial build fails. Use `uv run docs dev --skip-build` only if a suitable existing `build/` tree is intentional.

The installed `docs` console script dispatches to `pipeline.cli:main`. Its primary maintenance commands are `dev`, `build`, `mv` (move a file while updating cross-references), `migrate`, and `migrate-docusaurus`. `mint` is a separate Mintlify CLI used by preview and rendered-site checks. For setup, recovery, and incremental-build behavior, see [Local Development Workflow](/openwiki/workflows/local-development.md).

## Route the task

| Request | Durable owner and first guide | Start validation with |
| --- | --- | --- |
| Edit authored prose, MDX, a reusable snippet, image, or style | The applicable input under `src/`; [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) | Focused prose check; add rendered link checking if routes or links change. |
| Add, move, rename, retire, or expose a page | Source under `src/`, explicit `src/docs.json` navigation, and redirects when a published path changes; [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) | Build and `make broken-links-with-anchors`. |
| Decide source family, emitted route, language variant, menu placement, redirect, or endpoint declaration | Source ownership and navigation are separate; [Source Directory Map](/openwiki/architecture/source-map.md) and [Language Versions and Route Variants](/openwiki/concepts/versioning.md) | Inspect every affected route, then validate links and redirects. |
| Change pipeline behavior, a CLI command, Make target, preprocessor, or helper | `pipeline/`, `scripts/`, or `Makefile`; [Developer CLI Tools](/openwiki/operations/cli-tools.md) | `make test TEST_FILE=tests/unit_tests/path_or_test.py`. |
| Change CI, a scheduled job, a secret-bearing workflow, OpenWiki automation, or PR-writing automation | `.github/workflows/` and its invoked tools; [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) | The focused local command and event/credential review. |
| Change an executable example or a displayed extracted snippet | Authored executable source in `src/code-samples/`; [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md) | `make test-code-samples FILES="src/code-samples/..."`, then `make code-snippets`. |
| Change `@[ref]`, an MDX link, redirect, or anchor | Authored link and source link map; [Cross-References and Links](/openwiki/operations/cross-references.md) | `make check-cross-refs` or `make broken-links-with-anchors`, as applicable. |
| Change an integration listing, provider overview, or package download data | Hosted integration frontmatter, `scripts/data/integration_external_docs.yaml`, `packages.yml`, or their generator; [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md) | URL validation or generator regeneration, then review the diff. |
| Change a LangSmith changelog or API specification | Its owner workflow and upstream input; [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md) or [LangSmith OpenAPI Refresh](/openwiki/workflows/langsmith-openapi-refresh.md) | The workflow's focused tests or `make check-openapi`; do not hand-edit generated input. |
| Investigate a mature OpenWiki, Deep Agents, Deep Agents Code, or Deep Agents JS release for missing documentation | `docs-release-watch/`; [Release-Watch Documentation Agent](/openwiki/workflows/release-watch.md) | Follow the agent's product skill and release gate; review the resulting draft PR. |
| Fix API reference at `reference.langchain.com` | External reference build | Use the [reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml); this repository has no reference build output. |

## Ownership boundaries that prevent wrong edits

`src/docs.json` is the Mintlify site configuration and navigation source of truth. It does not select an authored source directory or emit routes. The builder clears `build/` on a full build, then emits Python and JavaScript OSS variants, unversioned OpenWiki and Deep Agents Code content, unversioned LangSmith content, language-prefixed Managed Deep Agents variants, and shared files. Treat `build/` as disposable output.

Choose a source family from filesystem ownership, not a reader-facing menu label. The Build menu mixes OSS and LangSmith content; **No-code agents** is sourced from Fleet; **Deep Agents Code** is a Products and setup item. Shared OSS cross-references must resolve in both language scopes unless placed in `:::python` or `:::js` fences. See [Source Directory Map](/openwiki/architecture/source-map.md) for route ownership and [Versioned Content Workflow](/openwiki/workflows/versioned-content.md) for the two-language contract.

Do not manually change these derived surfaces:

| Derived surface | Change or operate instead |
| --- | --- |
| `build/` | The authored `src/` input, configuration, or pipeline, then rebuild. |
| `src/oss/python/integrations/providers/overview.mdx` | `packages.yml` or `pipeline/tools/partner_pkg_table.py`, then run `uv run python pipeline/tools/partner_pkg_table.py`. |
| `src/code-samples-generated/` and `src/snippets/code-samples/` | `src/code-samples/`, then test and run `make code-snippets`. |
| Integration listing/download output | Hosted guide `integration:` frontmatter or external-listing YAML, then validate and regenerate. |
| LangSmith changelog and transformed OpenAPI files | Their dedicated update workflows and upstream owners. |
| Mintlify OpenAPI endpoint pages | The committed or remote specification plus `src/docs.json`; deployment, not the local build, generates endpoint pages. |

## Automation and release-watch boundaries

Core CI runs for pushes to `main`, pull requests, and manual dispatch. It calls reusable test, lint, and built link/OpenAPI validation and independently checks unresolved merge-conflict markers, source cross-references, external integration documentation URL schemes, and provider-overview generator drift. The code-sample workflow is intentionally separate: it runs for relevant non-fork PRs, manual dispatch, and a monthly schedule; forks are skipped because some examples require secrets.

OpenWiki refresh is another separate automation domain. `.github/workflows/openwiki-update.yml` runs daily at 08:00 UTC or manually, checks out full history so `openwiki code --update` can compare against the last documented commit, and opens an `openwiki/update` PR limited to `openwiki`, `AGENTS.md`, and that workflow. It has write permissions and uses repository secrets for its model and optional LangSmith connections/tracing; changes must preserve those trust boundaries.

`docs-release-watch/` is a Managed Deep Agent, not a GitHub Actions workflow. It watches four registered product domains and applies a seven-day maturity gate to non-prerelease releases, with tag prefixes separating package feeds. For a verified documentation gap, it loads the product skill, inspects only the configured documentation paths, creates exactly one Linear DOC issue and one draft docs PR per feature, and records procedural tracking only. Draft PRs remain subject to normal human review. The agent's deployment-shared memory is an untrusted shared-input boundary: it must not contain credentials or grant authority.

## Use the narrowest meaningful validation

Start with the check that proves the changed contract; add regeneration, build, or rendered-route validation only when the change crosses that boundary. [Testing Overview](/openwiki/testing/test-overview.md) explains the full matrix.

| Changed boundary | Command or review | What it proves |
| --- | --- | --- |
| Pipeline, builder, preprocessor, or generator | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | Focused pytest behavior with network sockets disabled except Unix sockets. |
| General Python tooling | `make test`; add `make lint` for Python/tooling changes | Test suite, then formatting, lint, types, and source spelling. |
| Shared or conditional `@[ref]` | `make check-cross-refs` | References resolve in each applicable source scope. |
| Authored prose | `make lint_prose FILES="src/path/to/page.mdx"` | Selected Vale rules on the changed text. |
| Route, redirect, link, or anchor | `make broken-links-with-anchors` | Builds first, then checks links, anchors, and redirect destinations. |
| Agent Server OpenAPI input | `make check-openapi` | Mintlify validation of the built specification. |
| Runnable sample and its displayed snippet | `make test-code-samples FILES="src/code-samples/..."` then `make code-snippets` | The selected source executes before generated snippet output refreshes. |

## Continue by domain

- [Source Directory Map](/openwiki/architecture/source-map.md): authored inputs, generated output, navigation, routes, and deployment-time surfaces.
- [Agent Authoring Skills](/openwiki/operations/agent-skills.md): canonical task procedures and installation paths.
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md): CI gates, scheduled jobs, PR writers, and credential boundaries.
- [Testing Overview](/openwiki/testing/test-overview.md): focused, generated-output, rendered-site, and credentialed validation.
- [Release-Watch Documentation Agent](/openwiki/workflows/release-watch.md): product registry, safe lifecycle, deployment, and extension procedure.
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md), [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md), and [LangSmith OpenAPI Refresh](/openwiki/workflows/langsmith-openapi-refresh.md): generator-owned workflows.
