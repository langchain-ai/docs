---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation or tooling request to its durable owner, the relevant repository workflow, and the smallest validation boundary. Use this map before editing so generated output and externally owned surfaces are not changed directly.
tags: [quickstart, documentation, tooling, validation, repository]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-19T08:25:25.748Z
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
generated: { by: "openwiki/0.4.3", at: "2026-10-19T08:25:25.748Z" }
---

# Repository Wiki Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com), not the generated SDK reference at [reference.langchain.com](https://reference.langchain.com/python/). First identify the durable input. A sidebar label, rendered page, generated table, endpoint reference, changelog, or `build/` file may be a result, not the safe file to edit.

Read `AGENTS.md` before changing content. It defines repository-wide authoring constraints: work in authored `src/`, never edit `build/`, update `src/docs.json` when adding a page, use Markdown-free descriptions and Tabler icons, and test examples. Procedures that apply only to particular tasks belong in `.agents/skills/`; run `make skills` in a Claude Code worktree to link them into `.claude/skills/`. A change to a script, workflow, Make target, check, scheduled job, or skill also requires the `docs-tooling-notion` follow-up before handoff.

## Start locally

The project requires Python 3.13 or later. From the repository root:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes Python dependency groups, installs project npm dependencies and the global Mintlify CLI, then links skills. `make dev` builds unless `--skip-build` is supplied, watches `src/`, and serves `build/` through Mintlify at <http://localhost:3000>; it stops instead of serving stale output when the initial build fails. The installed `docs` command is the pipeline CLI behind the Make development and build wrappers; use it for `dev`, `build`, `mv`, and migration operations. `mint` is the separate CLI used for preview and rendered-site checks.

## Task-routing map

| Requested change | Durable owner—not the derived surface | Read first | Smallest useful validation |
| --- | --- | --- | --- |
| Existing prose, MDX, images, styles, or reusable snippets | The applicable authored input under `src/` | [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) | Review the source change; run prose or link validation when it changes either boundary. |
| Add, move, rename, retire, or expose a page | Source page, `src/docs.json` navigation, and redirects | [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) | Build, then `make broken-links-with-anchors`. |
| Source family, public route, language variant, or menu placement | Route-emitting source and `src/docs.json` are independent owners | [Source Directory Map](/openwiki/architecture/source-map.md) | Inspect every emitted route; check redirects and links. |
| Shared or language-specific OSS content | Applicable `src/oss/` family and conditional fences | [Versioned Content Workflow](/openwiki/workflows/versioned-content.md) | `make check-cross-refs`, then inspect affected language variants. |
| `@[ref]`, MDX link, redirect, or anchor | Authored link/page and source link map | [Cross-References and Links](/openwiki/operations/cross-references.md) | `make check-cross-refs` for references, or `make broken-links-with-anchors` for rendered routes. |
| Builder, preprocessor, CLI, Make target, helper, or pipeline test | `pipeline/`, `scripts/`, or `Makefile` plus its focused tests | [Documentation Build System](/openwiki/architecture/build-system.md) and [Builder and Pipeline Tests](/openwiki/testing/builder-tests.md) | `make test TEST_FILE=tests/unit_tests/path_or_test.py`. |
| GitHub workflow, CI check, scheduled job, secret-bearing automation, or failure triage | `.github/workflows/` and the script it invokes | [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) | Run the invoked local check; preserve its event, permission, and credential boundary. |
| Runnable example or displayed extracted snippet | Executable source in `src/code-samples/` | [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md) | `make test-code-samples FILES="src/code-samples/..."`, then `make code-snippets`. |
| Integration listing or provider table | Guide `integration:` frontmatter / external-listing YAML, or `packages.yml` and its generator | [Source Directory Map](/openwiki/architecture/source-map.md) | Validate listing URLs or regenerate the table and review the diff. |
| Cloud or Fleet changelog | The changelog workflow, upstream state, and review PR | [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md) | Its focused deterministic tests; do not directly publish generated content. |
| LangSmith or Agent Server OpenAPI input, or deployment-generated endpoint pages | Committed/remote specification and `src/docs.json` declaration | [Reference Documentation Integrations](/openwiki/integrations/reference-docs.md) | `make check-openapi` where applicable. |
| API reference at `reference.langchain.com` | The external reference-documentation build | [Reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml) | File or route the issue; this repository has no reference build output. |
| Release-driven OpenWiki or Deep Agents documentation update | `docs-release-watch/` product registry, product skill, schedule, and source docs path | [Documentation Release Watch](/openwiki/workflows/release-watch.md) | Exercise the applicable agent path with its credentials; review the resulting draft PR. |

## Ownership rules that prevent unsafe edits

`src/docs.json` is the Mintlify navigation and site-configuration source of truth, but it does not choose a content family or emit routes. The builder clears and recreates `build/`. Most OSS content becomes Python and JavaScript variants; language-owned OSS subtrees emit only their matching family. OpenWiki and Deep Agents Code are unversioned exceptions, ordinary LangSmith content is unversioned, and Managed Deep Agents source emits language-prefixed variants. Menu labels are not reliable ownership clues: **Build** mixes OSS and LangSmith, **No-code agents** is Fleet, and **Deep Agents Code** appears under Products and setup.

For shared OSS `@[ref]` references, an unfenced reference must resolve for both Python and JavaScript. Put language-only names in `:::python` or `:::js` blocks. `make check-cross-refs` enforces that source-level rule.

Never patch an output just to make the rendered result look right:

| Derived surface | Change instead | Follow-through |
| --- | --- | --- |
| `build/` | Authored `src/`, configuration, or pipeline input | Rebuild; the next full build deletes manual output edits. |
| `src/oss/python/integrations/providers/overview.mdx` | `packages.yml` or `pipeline/tools/partner_pkg_table.py` | Run `uv run python pipeline/tools/partner_pkg_table.py`; CI rejects drift. |
| `src/code-samples-generated/` and `src/snippets/code-samples/` | `src/code-samples/` | Test source, run `make code-snippets`, and review generated MDX. |
| Integration discovery/download listings | Hosted-guide frontmatter or `scripts/data/integration_external_docs.yaml` | Run `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`, then regenerate. |
| LangSmith Cloud/Fleet changelogs or platform OpenAPI JSON | Their owned workflow, processor, and upstream state | Use the workflow; do not hand-edit generated input. |
| Mintlify endpoint pages | OpenAPI declaration and its committed or remote specification | They are generated at deployment, not in local `build/`. |

The Agent Server specification is maintained by update PRs from `langgraph-api`; the platform specification is refreshed through its workflow. The SDK API-reference site is a separate external build.

## Choose the narrowest validation boundary

Start with the check that proves the changed contract, then add build or rendered-route checks only when a boundary is crossed.

| Change boundary | Start with | What it covers |
| --- | --- | --- |
| Pipeline code, builder, preprocessor, generator, or helper | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | Focused pytest contract; network sockets are disabled except Unix sockets. |
| General Python tooling | `make test`; add `make lint` for tooling changes | Test suite; lint checks formatting, lint, types, and source spelling. |
| Shared or conditional `@[ref]` content | `make check-cross-refs` | Resolution in each applicable source scope. |
| Authored prose | `make lint_prose FILES="src/path/to/page.mdx"` | Selected Vale rules. |
| Route, redirect, link, or anchor | `make broken-links-with-anchors` | Builds first, then checks links, anchors, and redirect destinations. |
| Agent Server OpenAPI specification | `make check-openapi` | Mintlify OpenAPI validation of built input. |
| Runnable sample and generated display snippet | `make test-code-samples FILES="src/code-samples/..."` then `make code-snippets` | Source execution before generated-snippet refresh. |

Core CI runs on pull requests, pushes to `main`, and manual dispatch. It runs reusable test, lint, and rendered link/OpenAPI checks, plus merge-marker, cross-reference, external integration URL, and provider-overview drift checks. The code-sample workflow is separately scoped to relevant pull requests, manual runs, and a monthly schedule; it skips fork pull requests because some samples require secrets.

The daily **OpenWiki Update** workflow is a separate trusted writer: it uses a full-history checkout so OpenWiki can compare against its last documented commit, runs `openwiki code --update`, and creates a PR limited to `openwiki`, `AGENTS.md`, and its own workflow. Treat its write permissions and OpenAI/LangSmith secrets as operational boundaries, not as credentials a normal content change needs.

## Release-watch automation

`docs-release-watch` is a Managed Deep Agent deployment, not a GitHub Actions release publisher. It watches OpenWiki plus Deep Agents Python, Deep Agents Code, and Deep Agents JS releases. For an eligible release published at least seven days earlier, a product schedule loads that product's skill, compares release notes with the configured docs paths, and creates one Linear DOC issue plus one **draft** docs PR for each untracked user-facing feature. Product-specific tag prefixes prevent shared release feeds from crossing product boundaries.

Its durable memory is shared at agent scope and stores tracking URLs rather than credentials; the repository cautions that shared memory is untrusted input. Local and deployed runs need LangSmith Gateway access plus GitHub and Linear connections. Draft-only output and human review are the final publication boundary. To cover a new product, add its registry entry, product skill, schedule prompt, and redeploy.

## Continue by domain

- [Local Development Workflow](/openwiki/workflows/local-development.md): setup, preview, rebuilding, and environment failures.
- [Source Directory Map](/openwiki/architecture/source-map.md): source owners, routes, navigation, and generated surfaces.
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md): page lifecycle and public-route changes.
- [Documentation Build System](/openwiki/architecture/build-system.md) and [Language Versions and Route Variants](/openwiki/concepts/versioning.md): build control flow and language routing.
- [Agent Authoring Skills](/openwiki/operations/agent-skills.md): the invariant-versus-procedure split and skill selection.
- [Testing Overview](/openwiki/testing/test-overview.md): a fuller change-to-validation matrix.
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md): checks, trusted automation, and permissions.
- [Documentation Release Watch](/openwiki/workflows/release-watch.md): schedules, agent tools, memory, and review boundaries.
