---
type: validation guide
title: Testing Overview
description: Change-oriented guidance for selecting deterministic tests, generated-document checks, credentialed code-sample runs, remote OpenAPI refreshes, and hosted-site validation. It explains what each passing boundary does and does not establish.
tags: [testing, pytest, ci, documentation, code-samples, openapi]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-02T08:21:54.688Z
sources:
  - id: openwiki-source-5c124605ed6e394bffee862c
    resource: repo://.github/workflows/_check-links.yml
  - id: openwiki-source-f35e7c44cc1805709393a581
    resource: repo://.github/workflows/_lint.yml
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-5153f86e64d6ee0b305f72b3
    resource: repo://.github/workflows/refresh-langsmith-openapi.yml
  - id: openwiki-source-97746d8f3662d803e625550e
    resource: repo://.github/workflows/test-code-samples.yml
  - id: openwiki-source-71ee7a4afbd2d6aa7b29f3d1
    resource: repo://htmltest-mint-export.yml
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-17f3856bce97f37118963062
    resource: repo://pipeline/preprocessors/handle_auto_links.py
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-0a0a6c8d7a88288e6b6b9b5b
    resource: repo://scripts/check_cross_refs.py
  - id: openwiki-source-2654e40275744504b4ca7e2b
    resource: repo://scripts/code_sample_tracing.py
  - id: openwiki-source-560bf24db9566b97ee19e383
    resource: repo://scripts/generate_code_snippet_mdx.py
  - id: openwiki-source-697851c98229599f97376bfb
    resource: repo://scripts/process_langsmith_openapi.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-6a4f3df816b7f7f45b6ac5b1
    resource: repo://src/code-samples/conftest.py
  - id: openwiki-source-e0401fc6d5f2a13d30455bd9
    resource: repo://src/code-samples/package.json
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
  - id: openwiki-source-b68d7bad2afd9a38e8c331d5
    resource: repo://tests/unit_tests/test_generate_code_snippet_mdx.py
  - id: openwiki-source-2ecfcd33b729fccd843ab705
    resource: repo://tests/unit_tests/test_handle_auto_links.py
generated: { by: "openwiki/0.4.3", at: "2026-10-02T08:21:54.688Z" }
---

## Choose the validation boundary

Start with the narrowest check that can prove the change, then add a boundary when it changes generated output, a link map, an external registry or specification, a credentialed example, or deployed content. These checks complement one another: a socket-isolated unit test cannot prove a provider call, and a successful live sample cannot prove that all generated documentation links resolve.

| Change | Focused command | Passing result proves | It does not prove |
| --- | --- | --- | --- |
| Pipeline, parser, builder, link-map, or generator behavior | `make test TEST_FILE=tests/unit_tests/test_builder.py` | A local, fixture-controlled contract | A registry, provider, deployed page, or remote API works |
| Code-sample TypeScript dependency or generated CodeGroup rule | `make test TEST_FILE=tests/unit_tests/test_generate_code_snippet_mdx.py` | Dependency floors and source-tree generation invariants | That a real provider request succeeds |
| MCP or other `@[ref]` reference/map change | `make test TEST_FILE=tests/unit_tests/test_handle_auto_links.py` and `make check-cross-refs` | Resolver behavior and source references in applicable scopes | The rendered destination is reachable |
| Build, redirect, anchor, or committed OpenAPI artifact | `make broken-links-with-anchors` and `make check-openapi` | The generated `build/` tree passes Mint checks | The live upstream OpenAPI endpoint is current |
| LangSmith platform OpenAPI refresh | `uv run python scripts/process_langsmith_openapi.py --input /path/to/openapi.json --write` | A supplied or allowlisted remote spec is processed deterministically into the committed artifact | That Mint renders every generated endpoint page as intended |
| Runnable code sample | `make test-code-samples FILES="src/code-samples/..."` | The selected program ran in its real language environment with supplied services and credentials | That skipped rate-limited samples ran, or all documentation output is valid |
| Package version assertion | `uv run python scripts/check_version_claims.py --files src/path/page.mdx` | The selected registry reports the stated release | Compatibility beyond published availability |
| Upstream-mirrored version | `uv run python scripts/check_external_versions.py --only <id>` | A configured source matches its GitHub upstream | An unreadable upstream synchronized |
| Hosted `llms.txt` coverage | `python3 scripts/check_llms_urls.py` | Sitemap pages are reachable through served indexes | A local build or source edit fixed the deployment |

```mermaid
flowchart TD
  Change["Change"] --> Unit["Deterministic local checks"]
  Unit --> Local["Fixtures source and generated artifacts"]
  Change --> Rendered["Build and Mint checks"]
  Rendered --> Build["Disposable build tree"]
  Change --> Remote["Remote refresh or registry check"]
  Remote --> Network["Registry GitHub or LangSmith API"]
  Change --> Live["Credentialed sample execution"]
  Live --> Services["Providers and PostgreSQL"]
  Change --> Hosted["Served site coverage"]
  Hosted --> Site["Deployed indexes and sitemap"]
```

This map separates deterministic local evidence from remote, live-service, and hosted-site evidence.

## Deterministic unit and build checks

The project requires Python `>=3.13.0,<4.0.0`; local mise selects Python 3.13 and uv 0.9.26. Install the test group, then use the focused test before the full suite:

```bash
uv sync --group test
make test
make test TEST_FILE=tests/unit_tests/test_builder.py
```

`make test` invokes pytest with `--disable-socket` and permits Unix sockets. Pytest uses automatic asyncio mode and function-scoped asyncio fixture loops. Internet-facing behavior must be mocked in this boundary; a socket failure means a test crossed its isolation boundary, not that a remote service is unavailable. Reusable test, lint, and documentation-link workflows synchronize the test group with `UV_FROZEN=true`, so CI does not silently update `uv.lock`.

### Focused contracts for documentation changes

- **Builder changes:** `tests/unit_tests/test_builder.py` covers the supported copy extensions, an empty source tree, and copying a local TSX snippet component into `build/snippets`. The builder clears and recreates `build/`, so follow a passing focused test with a build-oriented check when routing or output policy changes.
- **Autolinks and MCP maps:** `tests/unit_tests/test_handle_auto_links.py` verifies scoped autolinks outside fenced code, preserves markers inside backtick or tilde fences (including extended and unclosed fences), and unescapes rather than resolves `\@[...]`. The source gate scans authored Markdown below `src`, skips generated code-sample snippets and `node_modules`, and requires an unfenced shared OSS reference to resolve in every build scope. Put Python-only and TypeScript-only MCP symbols in their respective conditional branch, then run both the focused resolver test and `make check-cross-refs`. See [Documentation Preprocessing](/openwiki/concepts/preprocessing.md) and [Cross-References](/openwiki/operations/cross-references.md).
- **Generated snippets and TypeScript dependencies:** The snippet-generator tests protect the distinction between an agent's routable model string and provider-specific chat or embedding model IDs. They also enforce `google:` and camel-case `googleSearch` in TypeScript, `google_genai:` in Python, and a declared and locked `@langchain/google` version of at least 0.2.6. When changing an MCP-related TypeScript package, `tsx`, or a sample dependency, update `src/code-samples/package.json` and its lockfile together, run this focused test, then execute the affected live sample if its path actually uses the changed package.
- **Other deterministic metadata:** The integration `docs_url` validator makes no network calls or writes; it accepts HTTP(S) and single-leading-slash paths while rejecting unsafe or missing values. The provider overview is generated: CI regenerates it and rejects a diff, so change `packages.yml` or its generator rather than editing the overview directly.

`make test-code-samples` installs the ESM package environment below `src/code-samples` before starting the runner. It declares `tsx` and the shared TypeScript dependencies, so it is the dependency owner for TypeScript examples rather than each sample file.

### Rendered documentation is a separate boundary

`make build` creates the disposable `build/` tree. `make broken-links-with-anchors` builds it, checks anchors and redirects through Mint, and filters documented generated-OpenAPI and standalone-snippet noise; `make check-openapi` validates `build/langsmith/agent-server-openapi.json`. The reusable documentation workflow runs those commands with Node 22 after installation. A passing source-map or unit test does not show that route rewrites, anchors, redirect targets, or Mint's OpenAPI validation work.

`make export-htmltest` is a further external-link boundary. The Mint export is incomplete, so htmltest deliberately disables internal-path and hash checks while checking external URLs, with four concurrent HTTP requests and a 30-second timeout.

## LangSmith platform OpenAPI: refresh, process, validate

The committed public artifact is `src/langsmith/langsmith-platform-openapi.json`. `scripts/process_langsmith_openapi.py` either reads `--input` locally or fetches only `https://api.smith.langchain.com/openapi.json`; it writes only with `--write`, otherwise it previews JSON on stdout. The network fetch has a 30-second timeout and rejects hosts outside its allowlist.

Processing is intentionally idempotent: it hides operations tagged for fleet/internal use or matching configured health/internal path rules, standardizes operation summaries (including visible non-sandbox v2 labels), adds or updates top-level tags, applies human-readable `x-group` values, and orders tags by the configured group order. This is a curation step for Mint's public endpoint navigation, not schema validation.

```mermaid
flowchart TD
  Input["Local input or allowlisted live spec"] --> Process["Apply public-documentation policy"]
  Process --> Hide["Hide internal and fleet operations"]
  Process --> Labels["Normalize summaries and groups"]
  Hide --> Artifact["Committed platform OpenAPI JSON"]
  Labels --> Artifact
  Artifact --> Mint["Build tree OpenAPI validation"]
  Refresh["Daily or manual workflow"] --> Input
  Refresh --> Review["One refresh pull request when artifact differs"]
```

This flow distinguishes remote-spec freshness, deterministic policy transformation, and Mint validation of the resulting build artifact.

The trusted refresh workflow runs daily at 10:00 UTC and can be dispatched manually. It processes the live spec, preserves the resulting file while checking out or creating `chore/refresh-langsmith-openapi`, and opens or appends to one review PR only when that artifact differs. Review the generated diff for newly exposed, hidden, renamed, or regrouped operations; do not treat a successful fetch as proof that public endpoint pages rendered correctly. Run `make check-openapi` and the documentation link check for that separate build boundary. See [LangSmith OpenAPI Refresh](/openwiki/workflows/langsmith-openapi-refresh.md).

## Credentialed live code samples

```bash
make test-code-samples
make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
```

The runner discovers Python, TypeScript, Java, Kotlin, Go, and shell samples under `src/code-samples`; `FILES` selects a space-separated subset and an unset value runs all eligible files except `__pycache__` and `node_modules`. The default timeout is 1,200 seconds and `CODE_SAMPLE_TIMEOUT_SECONDS` overrides it. Python runs through `uv`, TypeScript through `npx tsx`, Go through `go run`, shell through `bash`, and Java/Kotlin through JBang pinned to Java 21. Python and JBang use the repository root; TypeScript, Go, and shell use `src/code-samples` to resolve their shared environments.

```mermaid
flowchart TD
  Select["Select eligible samples"] --> Run["Run language command"]
  Run --> Result{"Process result"}
  Result -->|"passed"| Trace{"Tracing enabled"}
  Trace -->|"no"| Pass["Passed"]
  Trace -->|"yes"| Collect["Collect LangSmith trace"]
  Collect --> TraceResult{"Collection succeeded"}
  TraceResult -->|"yes"| Pass
  TraceResult -->|"no"| Fail["Runner fails"]
  Result -->|"rate limited"| Retry["Retry up to three attempts"]
  Retry --> Skip["Record skipped after retries"]
  Result -->|"other failure"| Fail
```

This is live integration evidence, not a deterministic unit test. In particular, a rate-limit skip is not a successful execution.

The workflow does not run on fork pull requests because examples can require provider secrets. Internal PRs run only changed eligible samples; monthly scheduled and manual runs test all samples, enable tracing, and have 90 minutes rather than the PR job's 60. CI supplies provider credentials, toolchains, and a pgvector PostgreSQL service through `POSTGRES_URI`. The PostgreSQL helper prefers that URI before attempting a testcontainer, Docker, or a default local connection, and clears shared store and migration tables before setup.

A detected LangSmith 429 gets at most three attempts with 15-second delays; a persistent rate limit is recorded as skipped without a nonzero exit, while other failures fail the runner. With tracing enabled, a passed sample is followed by trace collection, and collection failure fails the runner. Only a one-snippet source with a qualifying recent agent root run receives a public manifest URL; generated snippet MDX adds a trace card only when that URL exists. Successful full runs can regenerate snippets and update a standing trace-refresh PR. See [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md).

## Remote and hosted checks

Package-version and external-version checks are network checks, not unit tests. The package checker resolves `>=` floors and `==` pins against PyPI or npm using syntax and context. It distinguishes confirmed unavailable releases from unresolved inputs such as timeouts, malformed responses, unsafe names, or private packages. The changed-document workflow runs only for changed MDX under `src`; its scheduled full sweep is advisory. The external-version checker validates an allowlisted configuration before comparing page values to GitHub content. Check mode fails for drift or unreadable entries; write mode can report unreadable upstream sources yet finish so resolvable changes can be reviewed.

Hosted `llms.txt` coverage is also deliberately outside the local build. The checker crawls the served root index and same-site nested `/_llms/` Markdown indexes, normalizes Markdown and `/index` URLs, and fails when sitemap URLs are unreachable through that hierarchy. Its weekly, credential-free workflow checks the deployed default site. A failure is a deployment/Mintlify coverage gap, not evidence that an authored source file or the local builder failed.

## CI triage

- **Socket, fixture, or focused-test failure:** repair the deterministic contract or its mock; do not diagnose it as a provider outage.
- **`UV_FROZEN` or sync failure:** reconcile declarations and `uv.lock`.
- **Cross-reference failure:** add/correct the scoped map key or fence the language-specific reference. A passing source gate does not validate final rendered URLs.
- **Generated snippet/dependency failure:** update the shared TypeScript declaration and lockfile or preserve the generator's language/model invariant; follow with the affected live sample when appropriate.
- **Mint link, anchor, redirect, or OpenAPI failure:** reproduce against the build tree. It is separate from source preprocessing and remote-spec refresh.
- **OpenAPI refresh diff:** review policy effects and run build validation; a fetched spec is remote input, not a guarantee of rendered public documentation.
- **Live sample failure:** inspect credentials, current provider behavior, service readiness, toolchains, and the sample. A green run with skips requires later execution of the skipped samples.
- **Hosted `llms.txt` failure:** investigate served indexes and sitemap/deployment state rather than editing a generated hosted artifact.

## Related documentation

- [Documentation Preprocessing](/openwiki/concepts/preprocessing.md)
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md)
- [Cross-References](/openwiki/operations/cross-references.md)
- [Quickstart](/openwiki/quickstart.md)
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md)
- [LangSmith OpenAPI Refresh](/openwiki/workflows/langsmith-openapi-refresh.md)
