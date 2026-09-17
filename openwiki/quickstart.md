---
type: contributor guide
title: Quickstart
description: Set up a local documentation preview, identify the authored owner or generator for a change, and run focused validation without editing generated output.
tags: [quickstart, documentation, development, validation, mintlify]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-15T08:21:56.110Z
sources:
  - id: openwiki-source-9361c44d74c0e18006d0d76f
    resource: repo://.agents/skills/README.md
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
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
generated: { by: "openwiki/0.4.3", at: "2026-09-15T08:21:56.110Z" }
---

# Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com). Author documentation and configuration in `src/` and change automation in its generator or metadata source; the pipeline recreates the Mintlify-facing `build/` tree. **Never edit `build/`.** A full build removes it before emitting Python and JavaScript OSS variants, unversioned OpenWiki and Deep Agents Code content, LangSmith content, Managed Deep Agents variants, and shared files. `reference.langchain.com` is generated outside this repository; report problems with that site through its [reference-docs issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml).

```mermaid
flowchart LR
  Source["Authored source or generator input"] --> Build["make build or make dev"]
  Build --> Output["Generated build tree"]
  Output --> Preview["Mintlify preview"]
  Source --> Checks["Focused validation"]
```

The local loop transforms authored inputs into disposable preview output; validation should cover the boundary that changed.

## Set up and preview

The checkout requires Python 3.13 or later, Node.js, and `uv`. Install dependencies and start the normal local loop:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes all Python dependency groups, installs project npm dependencies and the global Mintlify CLI, and links skills for Claude Code. Open <http://localhost:3000>. `make dev` runs an initial build, watches `src/`, and starts `mint dev --port 3000` from `build/`. It exits if that initial build fails, rather than serving stale output. Use `uv run pipeline dev --skip-build` only when the existing build tree is known to be suitable; it warns if no build directory exists.

Use `make build` for a clean, one-shot reconstruction and inspect the affected emitted route after changing navigation, route ownership, shared assets, preprocessing, or a generator. For command options, watcher recovery, and direct CLI entrypoints, see [Local Development Workflow](/openwiki/workflows/local-development.md).

## Route the change

Read `AGENTS.md` first: it contains repository-wide authoring invariants and is byte-identical to `CLAUDE.md`. Then use the task-specific `SKILL.md` under `.agents/skills/`. Most supported agents discover that canonical directory directly; Claude Code needs `make skills` to maintain links under `.claude/skills/`.

| If you need to… | Edit or start from | Then verify |
| --- | --- | --- |
| Add, move, rename, remove, or redirect a page | The page source plus [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) | Update `src/docs.json` and the appropriate redirects as well as the page source; build and inspect the new or retired route. |
| Find the owner of a page or choose a language route | [Source Directory Map](/openwiki/architecture/source-map.md) | Choose the source by its route class, not its navigation label. Most OSS content has Python and JavaScript outputs; OpenWiki and Deep Agents Code are unversioned exceptions. |
| Change build routing, preprocessing, or output behavior | The implementation in `pipeline/` and [Build System Architecture](/openwiki/architecture/build-system.md) | Run focused unit tests, then build and inspect the output class affected. |
| Change GitHub automation or a CI failure | [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) | Reproduce the specific failed gate rather than relying on an unrelated check. |
| Add or revise a runnable example | `src/code-samples/`, the `docs-code-samples` skill, and [Testing Overview](/openwiki/testing/test-overview.md) | Execute the source sample, then regenerate its importable snippet output. |

`src/docs.json` is the Mintlify configuration, navigation, and redirect source of truth. Its product and menu labels do not necessarily match directory names, so locate the owner from the source map before editing. Page additions, moves, and removals must synchronize the source page, `src/docs.json`, and redirects for retired public routes.

## Change the owner, not a derivative

Some committed files are generated inputs or derivatives even though they are under `src/`:

- **Provider overview:** `src/oss/python/integrations/providers/overview.mdx` is generated from `packages.yml` and `pipeline/tools/partner_pkg_table.py`. Change one of those inputs, run `uv run python pipeline/tools/partner_pkg_table.py`, and commit the regenerated result. CI regenerates it and rejects a diff.
- **Code snippets:** files in `src/code-samples/` are runnable source. `make code-snippets` extracts them through `src/code-samples-generated/` and generates importable MDX under `src/snippets/code-samples/`; do not edit either derivative.
- **Other generated listings:** find their metadata or generator and use its documented regeneration path. [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) covers the page-lifecycle boundary.

For a changed runnable sample, run the narrowest sample first, then regenerate:

```bash
make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
make code-snippets
```

Without `FILES`, the sample runner selects supported Python, TypeScript, Java, Kotlin, Go, and shell files below `src/code-samples/`. Unlike unit tests, samples execute in their actual environment and can require provider credentials or PostgreSQL. Never commit credentials. CI skips fork pull requests, runs changed supported samples for internal pull requests, and reserves full execution, tracing, snippet generation, and trace-refresh pull requests for scheduled or manual runs after successful steps.

## Validate the boundary you changed

Build and inspect the affected route after an authored page, navigation, asset, shared input, or preprocessing change. Then select the narrowest additional check that reaches the changed contract.

| Boundary | Command | What it covers |
| --- | --- | --- |
| Pipeline, parser, watcher, skill, or repository behavior | `make test` | Pytest unit tests with network sockets disabled except Unix sockets. Narrow with `TEST_FILE=...`. |
| Finished prose | `make lint_prose FILES="src/path/to/page.mdx"` | Vale using the repository-pinned binary. |
| Python tooling and spelling | `make lint` | Ruff format/check, `ty`, and Codespell. |
| Built links and anchors | `make broken-links-with-anchors` | A fresh build and Mint's filtered link-and-anchor check. |
| Source `@[ref]` references | `make check-cross-refs` | References against source language-aware maps. |
| Runnable sample and its generated presentation | `make test-code-samples FILES="..."`; `make code-snippets` | Executable source plus refreshed snippet MDX. |
| Provider overview or external integration metadata | `uv run python pipeline/tools/partner_pkg_table.py`; `uv run python scripts/refresh_integration_downloads.py --check-docs-urls` | Current provider overview and safe external documentation URL schemes. |

Core CI runs on pushes to `main`, pull requests, and manual dispatch. It invokes unit tests, lint, and built-link checks and also has cross-reference, external integration URL, generated-file, and merge-conflict checks. A passing check in another row does not substitute for the one that exercises the changed boundary.

## Before opening a pull request

- Confirm every edit is to authored content, configuration, metadata, or a generator—not `build/` or another derivative.
- For a page lifecycle change, synchronize its source, exact `src/docs.json` placement, and redirects for retired routes.
- Run `make build` and inspect each affected output variant where the route model requires it.
- Record focused checks run and any limitation, especially credentials or external services needed by samples.

## Related pages

- [Build System Architecture](/openwiki/architecture/build-system.md)
- [Source Directory Map](/openwiki/architecture/source-map.md)
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md)
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md)
- [Testing Overview](/openwiki/testing/test-overview.md)
- [Local Development Workflow](/openwiki/workflows/local-development.md)
