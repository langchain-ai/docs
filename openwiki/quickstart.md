---
type: contributor guide
title: Quickstart
description: Set up a local documentation preview, identify the authored owner or generator for a change, and run focused validation without editing generated output.
tags: [quickstart, documentation, development, validation, mintlify]
sources:
  - id: openwiki-source-9361c44d74c0e18006d0d76f
    resource: repo://.agents/skills/README.md
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-21617d8a6b2b570989a7c900
    resource: repo://.github/workflows/check-version-claims.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-0976291f8216a4c7151f20a7
    resource: repo://.github/workflows/refresh-external-versions.yml
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
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-6b3ad04031a04803eb901844
    resource: repo://scripts/check_external_versions.py
  - id: openwiki-source-99b53585619b83f258314f8b
    resource: repo://scripts/check_version_claims.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
generated: { by: "openwiki/0.4.3", at: "2026-09-17T08:22:51.028Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-09-17T08:22:51.028Z
---

# Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com). Author documentation and configuration in `src/`; use a generator or its metadata source when a file is derived. The pipeline recreates the Mintlify-facing `build/` tree, so **never edit `build/`**. A build clears that tree, emits Python and JavaScript OSS variants, keeps OpenWiki and Deep Agents Code unversioned, emits LangSmith and Managed Deep Agents content, and copies shared files. API reference at [reference.langchain.com](https://reference.langchain.com/python/) is built outside this repository; use its [issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml) to report a problem.

```mermaid
flowchart LR
  Source["Authored source or generator input"] --> Build["make build or make dev"]
  Build --> Output["Generated build tree"]
  Output --> Preview["Mintlify preview"]
  Source --> Checks["Focused validation"]
```

The local loop turns authored input into disposable preview output. Validate the boundary that changed.

## Set up and preview

The checkout requires Python 3.13 or later, Node.js, and `uv`.

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes all Python dependency groups, installs project npm dependencies and the global Mintlify CLI, and links Claude Code skills. Open <http://localhost:3000>. `make dev` makes an initial build, watches `src/`, and starts `mint dev --port 3000` from `build/`. It exits when the initial build fails, rather than serving stale output. Use `uv run pipeline dev --skip-build` only if the existing build is suitable; it warns when `build/` is absent. Use `make build` for a clean reconstruction, then inspect each affected emitted route. For command options and watcher recovery, see [Local Development Workflow](/openwiki/workflows/local-development.md).

## Route the task

Read `AGENTS.md` first for repository-wide rules; it and `CLAUDE.md` contain identical guidelines. Then invoke the procedure whose `SKILL.md` in `.agents/skills/` matches the task. Most agents read that canonical tree directly. Claude Code reads `.claude/skills/`, so `make skills` creates, refreshes, and removes its links without replacing personal non-link skills. The [Agent Authoring Skills](/openwiki/operations/agent-skills.md) page explains the always-on-rules versus task-procedure boundary.

| If you need to… | Start with | Focused next step |
| --- | --- | --- |
| Add, move, rename, remove, or redirect a page | `add-docs-page` and [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) | Update the authored page, `src/docs.json`, and redirects for retired routes; build and inspect the route. |
| Choose the owner or language route | [Source Map](/openwiki/architecture/source-map.md) | Select the source by route class, not by navigation label. Most OSS content has Python and JavaScript outputs; OpenWiki and Deep Agents Code do not. |
| Revise existing prose or restructure a topic | `docs-edit`, `docs-team-voice`, `docs-review`, or `docs-restructure` | Run the narrow prose or link check below. |
| Change a workflow, script, Make target, check, schedule, or skill | `docs-tooling-notion` and [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) | Document the tooling handoff, then reproduce its specific gate. |
| Add or change a runnable example | `docs-code-samples` and [Testing Overview](/openwiki/testing/test-overview.md) | Execute the source sample, then regenerate its snippet. |
| Assert an SDK/package version or mirror an upstream requirement | [Language Versioning Strategy](/openwiki/concepts/versioning.md) | Run the relevant version checker; do not turn a registry check into a feature-floor bump. |

`src/docs.json` is the Mintlify site configuration, navigation, and redirect source of truth. Its product labels need not match directories. **Every new authored page also requires a `src/docs.json` navigation update**; moves and removals also require redirect maintenance. Keep page lifecycle details in [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md), rather than copying them into a content change.

## Change the owner, not a derivative

Some committed files need a source-first change:

- **Provider overview:** `src/oss/python/integrations/providers/overview.mdx` is generated from `packages.yml` and `pipeline/tools/partner_pkg_table.py`. Change an input, run `uv run python pipeline/tools/partner_pkg_table.py`, and commit the result. CI regenerates it and rejects a diff.
- **Code snippets:** `src/code-samples/` holds runnable source. `make code-snippets` extracts it through `src/code-samples-generated/` and generates importable MDX under `src/snippets/code-samples/`; do not hand-edit either derivative.
- **External version mirrors:** `scripts/data/external_versions.yaml` registers a page pattern and an upstream GitHub source. The refresh automation can replace only the captured version digits, so review the surrounding requirement after a refresh.

For one changed sample, run it before generating its presentation:

```bash
make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
make code-snippets
```

The runner accepts supported Python, TypeScript, Java, Kotlin, Go, and shell files below `src/code-samples/`. Samples run in their real environment and may need provider credentials or PostgreSQL; never commit credentials. Fork pull requests skip this credential-bearing workflow. Internal pull requests run changed supported samples, while scheduled and manual runs test all samples, enable tracing, regenerate snippets, and create or update a trace-refresh PR only after successful testing and generation.

## Validate the changed boundary

Build and inspect affected routes after authored pages, navigation, shared assets, preprocessors, or generators. Then choose the narrowest check that exercises the changed contract.

| Boundary | Command | What it checks |
| --- | --- | --- |
| Pipeline, parser, watcher, or repository behavior | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | Pytest with network sockets disabled except Unix sockets. Omit `TEST_FILE` for the default unit-test tree. |
| Finished prose | `make lint_prose FILES="src/path/to/page.mdx"` | Vale with the repository-pinned binary. |
| Python tooling and spelling | `make lint` | Ruff format/check, `ty`, and Codespell. |
| Built links and anchors | `make broken-links-with-anchors` | Fresh build plus Mint filtered link-and-anchor validation. |
| Source `@[ref]` references | `make check-cross-refs` | Source language-aware reference maps. |
| Runnable sample and generated snippet | `make test-code-samples FILES="..."`; `make code-snippets` | Executable source and refreshed snippet MDX. |
| Package version claims in a changed page | `uv run python scripts/check_version_claims.py --files src/path/to/page.mdx` | Whether every named `>=` or `==` package version was published on the resolved PyPI or npm registry. |
| Upstream-owned mirrored requirement | `uv run python scripts/check_external_versions.py --only <id>` | Whether the registered page claim matches its upstream GitHub file or latest release. |
| Provider overview or external integration metadata | `uv run python pipeline/tools/partner_pkg_table.py`; `uv run python scripts/refresh_integration_downloads.py --check-docs-urls` | Generated provider overview and permitted external documentation URL schemes. |

The package-version pull-request gate runs when `src/**/*.mdx` changes. It derives changed MDX files from the merge base and fails only for a version that was never published; an old but published floor is informational, not an automatic upgrade request. Ecosystem selection uses package syntax, nearby language labels, language fences, and page route defaults, which matters for packages published on both registries. The scheduled full sweep is advisory so it can report unresolved or yanked claims without failing the schedule.

External mirrors are different: their registry entries identify an upstream owner and must match one page exactly. Every Monday at 08:00 UTC, plus on manual dispatch, the refresh workflow runs `scripts/check_external_versions.py --write`. If `src/` changes, it reuses an open `chore/refresh-external-versions` PR or creates one; reviewers must verify prose that the digit-only rewrite cannot assess.

Core CI runs on pushes to `main`, pull requests, and manual dispatch. It invokes unit tests, lint, and built-link checks, plus cross-reference, external integration URL, generated-file, and merge-conflict checks. A passing check in another row is not a substitute for the gate covering the change.

## Before opening a pull request

- Confirm edits target authored content, configuration, metadata, or a generator—not `build/` or a generated derivative.
- Synchronize every new page with `src/docs.json`; synchronize moves/removals with redirects.
- Build and inspect every output variant required by the route model.
- Run and record focused checks, including any unavailable credential or external-service dependency.
- For an automated version rewrite, confirm the upstream requirement beyond its version number.

## Related pages

- [Source Map](/openwiki/architecture/source-map.md)
- [Language Versioning Strategy](/openwiki/concepts/versioning.md)
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md)
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md)
- [Agent Authoring Skills](/openwiki/operations/agent-skills.md)
- [Testing Overview](/openwiki/testing/test-overview.md)
- [Local Development Workflow](/openwiki/workflows/local-development.md)
