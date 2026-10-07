---
type: contributor guide
title: Quickstart
description: Set up a local documentation preview, identify the durable input for a change, and choose the validation and operational guidance that applies to it.
tags: [quickstart, documentation, development, validation, mintlify]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-06T08:22:08.206Z
sources:
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
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
  - id: openwiki-source-eb7a028ac20098c574b90426
    resource: repo://scripts/assemble_changelog.py
  - id: openwiki-source-0a0a6c8d7a88288e6b6b9b5b
    resource: repo://scripts/check_cross_refs.py
  - id: openwiki-source-697851c98229599f97376bfb
    resource: repo://scripts/process_langsmith_openapi.py
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-2d6fb565fec243c560da8729
    resource: repo://src/code-samples/package-lock.json
  - id: openwiki-source-e0401fc6d5f2a13d30455bd9
    resource: repo://src/code-samples/package.json
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
generated: { by: "openwiki/0.4.3", at: "2026-10-06T08:22:08.206Z" }
---

# Quickstart

This repository builds the Mintlify site at [docs.langchain.com](https://docs.langchain.com). It does **not** build the generated SDK reference site at [reference.langchain.com](https://reference.langchain.com/python/). Start with an owned input—normally content beneath `src/`, site configuration, metadata, or generator code—not a derivative. In particular, never edit `build/`: each full build removes and recreates it. Report problems with the external reference site through the [reference documentation issue template](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml).

## Set up a local preview

The project requires Python 3.13 or later, Node.js, and `uv`.

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
make dev
```

`make install` synchronizes all Python dependency groups, installs the repository's npm dependencies and the global Mintlify CLI, and links authoring skills for Claude Code. Open <http://localhost:3000> when the server starts.

`make dev` performs an initial build, watches `src/`, and runs `mint dev --port 3000` from `build/`. It exits if that initial build fails, avoiding a preview of stale output. Use `uv run pipeline dev --skip-build` only when an appropriate generated tree already exists; use `make build` to recreate one.

Read `AGENTS.md` before changing documentation. It is the repository-wide authoring guide. Task procedures are in `.agents/skills/`; `make skills` links them into `.claude/skills/` for Claude Code. In particular, use the page-editing and review procedures when applicable; a changed script, workflow, Make target, check, or skill also requires the `docs-tooling-notion` procedure.

## Decide what to edit

A public page has separate **source ownership**, **emitted route**, **Mintlify navigation**, and sometimes **deployment-generated reference** responsibilities. `src/docs.json` owns site configuration, navigation, redirects, and OpenAPI declarations; it is not a scan of the source tree. Add a navigation entry when adding a manually authored page, but determine the source family and output route first.

| Requested change | Durable owner | Key consequence |
| --- | --- | --- |
| Shared OSS documentation | `src/oss/` | Builds Python and JavaScript output. Scope language-specific prose and API references with `:::python` or `:::js`. |
| Python- or TypeScript-owned OSS content | `src/oss/python/` or `src/oss/javascript/` | Emits only the matching language route. |
| OpenWiki or Deep Agents Code | `src/oss/openwiki/` or `src/oss/deepagents/code/` | Emits one unversioned OSS route. |
| Ordinary LangSmith documentation | `src/langsmith/` | Emits one unversioned `/langsmith/...` route. |
| Managed Deep Agents source | Direct `src/langsmith/managed-deep-agents*.mdx` file | Emits Python and JavaScript variants; legacy unversioned URLs redirect to Python. |
| Menu placement, redirects, or OpenAPI declaration | `src/docs.json` | Update independently of route emission. |
| Reusable prose or static assets | `src/snippets/`, `src/images/`, `src/fonts/`, or another shared source input | Change the reusable input and verify consumers. |

A full builder run clears `build/`, creates OSS Python and JavaScript variants, creates the unversioned OpenWiki and Deep Agents Code output, creates ordinary LangSmith output and Managed Deep Agents variants, then copies shared files. The [Source Directory Map](/openwiki/architecture/source-map.md) explains the ownership and route rules; [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) gives the safe page, navigation, redirect, and move procedure.

For a shared OSS cross-reference, an unfenced `@[ref]` must resolve in both language scopes. Put language-specific API names in the respective conditional branch, update the relevant map when required, and run `make check-cross-refs`.

## Regenerate derived content at its input

Do not treat generated files or hosted rendering as alternate authored sources.

- **Provider overview:** `src/oss/python/integrations/providers/overview.mdx` is generated from `packages.yml` by `pipeline/tools/partner_pkg_table.py`. Change the metadata or generator, then regenerate and commit the result:

  ```bash
  uv run python pipeline/tools/partner_pkg_table.py
  ```

  CI regenerates it and fails when the committed file differs.

- **Runnable samples and snippets:** `src/code-samples/` is executable source. `make code-snippets` extracts it through the ignored `src/code-samples-generated/` intermediate and writes committed MDX snippets under `src/snippets/code-samples/`; do not edit those snippets by hand. TypeScript samples use one shared `src/code-samples/package.json` and lockfile, so update both when their runtime dependencies change. Follow [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md).

- **Integration listings:** hosted-guide `integration:` frontmatter and `scripts/data/integration_external_docs.yaml` feed discovery tables. Check the permitted documentation URLs, then regenerate the tables:

  ```bash
  uv run python scripts/refresh_integration_downloads.py --check-docs-urls
  uv run python scripts/refresh_integration_downloads.py --write
  ```

  The validator permits HTTP(S) and site-relative paths beginning with one `/`; it rejects protocol-relative and unsafe-scheme URLs. See [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md).

- **OpenAPI reference:** Mintlify creates configured endpoint pages during deployment, rather than from authored endpoint MDX. For Agent Server, change the specification or its `src/docs.json` declaration and run `make check-openapi`. `src/langsmith/langsmith-platform-openapi.json` is instead a committed generated input: its processor fetches only the allowlisted LangSmith host (or accepts a local input), filters public documentation content, normalizes titles and tag groups, and writes only with `--write`. Do not hand-edit it; follow [LangSmith Platform OpenAPI Refresh](/openwiki/workflows/langsmith-openapi-refresh.md) and inspect a deployment-facing surface for rendered endpoints.

- **Changelog publication:** `scripts/assemble_changelog.py` produces a reviewable Cloud/Fleet update from sibling-repository fragments. Its committed ledger changes only with `--record`, after the rendered entries are reviewed. The [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md) describes its rollout gate, state, and focused tests.

## Validate the boundary you changed

Run the smallest check that can establish the relevant guarantee, then add build or hosted validation when the change crosses that boundary.

| Change | Focused command | What it checks |
| --- | --- | --- |
| Pipeline, builder, preprocessor, or generator | `make test TEST_FILE=tests/unit_tests/path_or_test.py` | Socket-isolated pytest behavior; omit `TEST_FILE` for the unit-test tree. |
| Cross-reference or language-conditional content | `make check-cross-refs` | Source `@[ref]` resolution in the required scopes. |
| Prose | `make lint_prose FILES="src/path/to/page.mdx"` | Repository-pinned Vale checks. |
| Python tooling and spelling | `make lint` | Ruff format/check, `ty`, and Codespell. |
| Routes, links, anchors, or redirects | `make broken-links-with-anchors` | Fresh build plus Mint link, anchor, and redirect checks. |
| Agent Server OpenAPI | `make check-openapi` | Mintlify validation of the built specification. |
| Executable sample or generated snippet | `make test-code-samples FILES="src/code-samples/..."`; `make code-snippets` | Runs selected sources (or all samples when `FILES` is omitted), then regenerates snippets. |
| Integration URL metadata | `uv run python scripts/refresh_integration_downloads.py --check-docs-urls` | Allowed `docs_url` syntax, not remote reachability. |

`make test` disables network sockets except Unix sockets. Code samples can instead need credentials, providers, or local services, so a skipped or unavailable remote run is not equivalent to a deterministic test. Likewise, deployment-generated OpenAPI endpoints and served `llms.txt` indexes require deployment-facing evidence; editing `build/` cannot validate or repair them. See [Testing Overview](/openwiki/testing/test-overview.md) for the complete change-to-validation map.

Core CI runs for pushes to `main`, pull requests, and manual dispatch. Its reusable test workflow invokes `make test`; CI also runs lint and link workflows plus merge-conflict, cross-reference, external documentation-URL, and generated-file checks. CI and other automation have distinct trust boundaries for untrusted pull requests, metadata-only fork handling, and trusted scheduled writers; see [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md).

## Before opening a pull request

1. Confirm that the edit changes an authored source, configuration, metadata record, or generator policy—not `build/` or hosted output.
2. Identify the emitted route family before changing navigation; update `src/docs.json` and redirects separately when needed.
3. Regenerate and review derived files after changing their durable inputs.
4. Inspect every route variant owned by the source family.
5. Run focused tests first, then build or deployment-facing checks appropriate to the changed boundary. State any unavailable credential, provider, or service dependency.

## Task-routing map

- [Source Directory Map](/openwiki/architecture/source-map.md) — source ownership, emitted routes, navigation, and deployment-generated reference surfaces.
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md) — add, move, retire, redirect, or regenerate a documentation page.
- [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md) — hosted and external integration metadata through generated discovery tables.
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md) — executable sample ownership, shared dependencies, extraction, and snippets.
- [LangSmith Platform OpenAPI Refresh](/openwiki/workflows/langsmith-openapi-refresh.md) — curated platform-spec ingestion and its review-PR lifecycle.
- [LangSmith Changelog Publication](/openwiki/workflows/changelog-publication.md) — reviewable Cloud/Fleet changelog assembly and publication state.
- [Testing Overview](/openwiki/testing/test-overview.md) — deterministic, generated-output, remote, credentialed, and hosted-site validation.
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md) — CI gates, fork safety, and trusted automation.
