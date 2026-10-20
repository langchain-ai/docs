---
type: contributor guide
title: Repository Wiki Quickstart
description: Route a documentation or tooling request to its durable owner, relevant workflow, and proportionate validation. Use this map before editing so generated output and externally owned surfaces are not changed directly.
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
verified:
  - by: openwiki/0.4.3
    at: 2026-10-20T08:20:37.912Z
generated: { by: "openwiki/0.4.3", at: "2026-10-20T08:20:37.912Z" }
---

# Repository Wiki Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com), not the generated SDK reference at [reference.langchain.com](https://reference.langchain.com/python/). Begin by finding the durable input: a rendered page, sidebar item, generated table, endpoint reference, changelog, or `build/` file can be an outcome rather than the file to change.

## Start with the repository contract

Read `AGENTS.md` before editing. It applies to all authored `src/` content: do not edit generated `build/`, use Markdown-free frontmatter descriptions and Tabler icons, update `src/docs.json` when adding a page, and test examples before including them. Repository-wide rules live in `AGENTS.md`; task procedures live in `.agents/skills/`. Run `make skills` in every Claude Code worktree to link those skills into `.claude/skills/`. Changes to scripts, workflows, Make targets, checks, schedules, or skills also require the `docs-tooling-notion` follow-up before handoff.

The key ownership split is:

- **Authored documentation and configuration:** `src/` and `src/docs.json`.
- **Transformation and local commands:** `pipeline/`, `scripts/`, `Makefile`, and the installed `docs` CLI.
- **Generated or deployment-owned surfaces:** `build/`, generated tables and snippets, deployment-time OpenAPI endpoint pages, and the separately built API-reference site.
- **Automation:** `.github/workflows/` for repository CI and `docs-release-watch/` for the Managed Deep Agent that proposes release-driven documentation updates.

## Set up and preview

The project requires Python 3.13 or later. From the repository root:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes all Python dependency groups, installs project npm dependencies and the global Mintlify CLI, then links skills. `make dev` performs an initial build unless `--skip-build` is supplied, watches `src/`, and runs `mint dev --port 3000` from `build/`. It exits instead of starting a preview when the initial build fails. Open <http://localhost:3000> after startup.

`docs` is the Python console script behind the Make build and development wrappers. It offers `dev`, `build`, `mv`, and Markdown migration commands; `mint` is the separate Mintlify CLI used for preview and rendered-site checks. For setup details, watcher limitations, reset procedures, and Mint working-directory pitfalls, read [Local Development and Validation Workflow](/openwiki/workflows/local-development.md) and [Local Tooling and Commands](/openwiki/operations/cli-tools.md).

## Route the task

| Requested change | Durable owner—not the derived surface | Read first | Start validation with |
| --- | --- | --- | --- |
| Edit existing prose, MDX, assets, styles, or reusable content | The applicable authored input under `src/` | [Repository Source Map](/openwiki/architecture/source-map.md) | `make lint_prose FILES="src/..."` for prose; add route checks when applicable. |
| Add, move, rename, retire, or expose a page | Source page, `src/docs.json` navigation, and redirects | [Adding and Moving Documentation Pages](/openwiki/operations/adding-pages.md) | Build, then `make broken-links-with-anchors`. |
| Change source family, public route, language behavior, or menu placement | Route-emitting source and navigation are independent owners | [Language Variants and Route Ownership](/openwiki/concepts/versioning.md) | Inspect all emitted routes; check redirects and links. |
| Change shared or language-specific OSS content | Applicable `src/oss/` family and conditional fences | [Changing Versioned Content Safely](/openwiki/workflows/versioned-content.md) | `make check-cross-refs`, then inspect each affected variant. |
| Fix `@[ref]`, a page link, redirect, or anchor | Authored link/page and its source link map | [Cross-References and API Links](/openwiki/operations/cross-references.md) | `make check-cross-refs` for references; `make broken-links-with-anchors` for rendered routes. |
| Change builder, preprocessor, CLI, Make target, or helper | `pipeline/`, `scripts/`, or `Makefile`, plus focused tests | [Documentation Build System](/openwiki/architecture/build-system.md) | `make test TEST_FILE=tests/unit_tests/path_or_test.py`. |
| Change CI, a scheduled job, a secret-bearing action, or workflow integration | `.github/workflows/` and the invoked implementation | [GitHub Actions and CI Automation](/openwiki/integrations/github-actions.md) | Run its local check and preserve its event, permission, and credential boundary. |
| Change a runnable example or extracted display snippet | Executable source in `src/code-samples/` | [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md) | `make test-code-samples FILES="src/code-samples/..."`, then `make code-snippets`. |
| Change an integration listing or provider table | Hosted-guide `integration:` frontmatter, external-listing YAML, or `packages.yml` and generator | [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md) | Validate listing URLs or regenerate and review the diff. |
| Change a changelog, OpenAPI input, or endpoint-reference setup | Its workflow/specification and `src/docs.json` declaration | [Weekly Changelog Publication](/openwiki/workflows/changelog-publication.md) or [Reference Documentation Boundaries](/openwiki/integrations/reference-docs.md) | Use the workflow's focused tests or `make check-openapi`. |
| Report a problem at `reference.langchain.com` | The external reference-documentation build | [Reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml) | Route the issue; this repository has no reference build output. |
| Extend or operate release-driven OpenWiki/Deep Agents updates | `docs-release-watch/` registry, skills, schedule prompts, and tools | [Documentation Release Watch](/openwiki/workflows/release-watch.md) | Exercise the applicable agent path and review its draft PR. |

## Ownership rules that prevent unsafe edits

`src/docs.json` is the Mintlify navigation and site-configuration source of truth, but it neither selects a content family nor emits its routes. A build clears and recreates `build/`. Most OSS content emits Python and JavaScript variants; language-owned OSS subtrees emit only their matching family. OpenWiki and Deep Agents Code are unversioned exceptions, ordinary LangSmith content is unversioned, and Managed Deep Agents source files emit language-prefixed variants. Menu labels are not reliable ownership clues: **Build** mixes OSS and LangSmith content, **No-code agents** is Fleet, and **Deep Agents Code** is a Products and setup item.

For shared OSS `@[ref]` references, an unfenced reference must resolve for both Python and JavaScript. Put language-only names in `:::python` or `:::js` blocks. `make check-cross-refs` enforces that source-level rule.

| Derived surface | Change instead | Follow-through |
| --- | --- | --- |
| `build/` | Authored `src/`, configuration, or pipeline input | Rebuild; the next full build deletes manual output edits. |
| `src/oss/python/integrations/providers/overview.mdx` | `packages.yml` or `pipeline/tools/partner_pkg_table.py` | Run `uv run python pipeline/tools/partner_pkg_table.py`; CI rejects drift. |
| `src/code-samples-generated/` and `src/snippets/code-samples/` | `src/code-samples/` | Test source, run `make code-snippets`, and review generated MDX. |
| Integration download/listing tables | Hosted-guide frontmatter or `scripts/data/integration_external_docs.yaml` | Run `uv run python scripts/refresh_integration_downloads.py --check-docs-urls`, then regenerate. |
| Mintlify endpoint pages | OpenAPI declaration and its committed or remote specification | They are generated at deployment, not in local `build/`. |

The Agent Server specification is maintained by update PRs from `langgraph-api`; the platform specification is refreshed by its workflow. The SDK API-reference site is a separate external build.

## Choose the narrowest validation boundary

Start with the check that proves the changed contract, then add build or rendered-route checks when a boundary is crossed.

| Change boundary | Start with | What it covers |
| --- | --- | --- |
| Pipeline code, builder, preprocessor, generator, or helper | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | Focused pytest contract; network sockets are disabled except Unix sockets. |
| General Python tooling | `make test`; add `make lint` for tooling changes | Test suite; lint checks formatting, lint, types, and source spelling. |
| Shared or conditional `@[ref]` content | `make check-cross-refs` | Resolution in each applicable source scope. |
| Authored prose | `make lint_prose FILES="src/path/to/page.mdx"` | Selected Vale rules. |
| Route, redirect, link, or anchor | `make broken-links-with-anchors` | Builds first, then checks links, anchors, and redirect destinations. |
| Agent Server OpenAPI specification | `make check-openapi` | Mintlify OpenAPI validation of built input. |
| Runnable sample and generated display snippet | `make test-code-samples FILES="src/code-samples/..."` then `make code-snippets` | Source execution before generated-snippet refresh. |

Core CI runs on pull requests, pushes to `main`, and manual dispatch. It invokes reusable test, lint, and rendered link/OpenAPI checks, then separately checks merge markers, source cross-references, external integration documentation URLs, and generated provider-overview drift. The code-sample workflow is separately scoped to relevant pull requests, manual runs, and a monthly schedule; it skips fork pull requests because samples can require secrets.

The daily **OpenWiki Update** workflow is a separate trusted writer. It uses a full-history checkout so `openwiki code --update` can compare with its last documented commit, and creates a PR restricted to `openwiki`, `AGENTS.md`, and its own workflow. Its write permissions and OpenAI/LangSmith secrets are operational boundaries, not credentials needed for normal documentation work.

## Release-watch automation

`docs-release-watch` is a Managed Deep Agent deployment, not a GitHub Actions release publisher. It covers OpenWiki, Deep Agents Python, Deep Agents Code, and Deep Agents JS. For the newest eligible release published 7–30 days earlier, a product schedule uses the matching registry entry and skill to compare tagged source changes with configured documentation paths. Only an untracked, user-facing gap can produce one Linear `DOC` issue and one **draft** docs PR per feature.

The release-research subagent has read tools only; the shipping agent reads repository guidance and uses the remote write tools only after research. Evidence from tagged source and exact base-file content protect the handoff. Deployment-shared memory is an explicitly untrusted input boundary: it stores tracking URLs rather than credentials, while tool authority remains outside memory. Human review of draft-only PRs is the final publication boundary. To add a product, add its registry entry, product skill, schedule prompt, and redeploy.

## Continue by domain

- [Repository Source Map](/openwiki/architecture/source-map.md): source owners, navigation, routes, generated surfaces, and automation boundaries.
- [Documentation Build System](/openwiki/architecture/build-system.md): the full build, preprocessing, route families, snippets, and Mintlify handoff.
- [Local Development and Validation Workflow](/openwiki/workflows/local-development.md): installation, preview, rebuild limits, and Mint troubleshooting.
- [Adding and Moving Documentation Pages](/openwiki/operations/adding-pages.md): page lifecycle, navigation, redirects, and public routes.
- [Agent Skills and Authoring Guardrails](/openwiki/operations/agent-skills.md): repository rules, task procedures, and skill consumers.
- [Testing and Validation Overview](/openwiki/testing/test-overview.md): the complete change-to-check matrix and what each check cannot prove.
- [GitHub Actions and CI Automation](/openwiki/integrations/github-actions.md): event, permission, secret, and human-review boundaries.
- [Documentation Release Watch](/openwiki/workflows/release-watch.md): registry selection, research/ship separation, memory, schedules, and draft-PR handoff.
