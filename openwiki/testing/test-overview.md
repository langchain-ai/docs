---
type: validation guide
title: Testing and Validation Overview
description: Map each documentation change to the smallest meaningful local check, generated-site validation, or credentialed CI boundary. Covers unit tests, Python and prose quality gates, cross-references, generated files, links, code samples, deprecated patterns, and CI ownership.
tags: [testing, validation, ci, documentation, code-samples]
verified:
  - by: openwiki/0.4.3
    at: 2026-11-09T08:07:38.321Z
sources:
  - id: openwiki-source-5c124605ed6e394bffee862c
    resource: repo://.github/workflows/_check-links.yml
  - id: openwiki-source-f35e7c44cc1805709393a581
    resource: repo://.github/workflows/_lint.yml
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-692d56c7e73dca0d6d880109
    resource: repo://.github/workflows/check-deprecated.yml
  - id: openwiki-source-21617d8a6b2b570989a7c900
    resource: repo://.github/workflows/check-version-claims.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-97746d8f3662d803e625550e
    resource: repo://.github/workflows/test-code-samples.yml
  - id: openwiki-source-ded8a20999ec9d794fa86ab9
    resource: repo://docs-release-watch/tests/test_evidence.py
  - id: openwiki-source-71ee7a4afbd2d6aa7b29f3d1
    resource: repo://htmltest-mint-export.yml
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-0a0a6c8d7a88288e6b6b9b5b
    resource: repo://scripts/check_cross_refs.py
  - id: openwiki-source-99b53585619b83f258314f8b
    resource: repo://scripts/check_version_claims.py
  - id: openwiki-source-2654e40275744504b4ca7e2b
    resource: repo://scripts/code_sample_tracing.py
  - id: openwiki-source-fd0cb9d6fca56bf4963559e9
    resource: repo://scripts/extract_code_snippets.py
  - id: openwiki-source-560bf24db9566b97ee19e383
    resource: repo://scripts/generate_code_snippet_mdx.py
  - id: openwiki-source-d22c99c9d9abf854bbf1a047
    resource: repo://scripts/generate_egress_ip_tables.py
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-11d4965febd3986495e06a17
    resource: repo://src/code-samples/langsmith/create-an-agent.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-5d310b0d0e3f7a2baf5a473a
    resource: repo://tests/changelog-navigation.test.js
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
  - id: openwiki-source-607673c5c40214b511f9e0a7
    resource: repo://tests/unit_tests/test_check_version_claims.py
  - id: openwiki-source-30a490be0964e690a58135e7
    resource: repo://tests/unit_tests/test_egress_ip_inventory.py
  - id: openwiki-source-b68d7bad2afd9a38e8c331d5
    resource: repo://tests/unit_tests/test_generate_code_snippet_mdx.py
  - id: openwiki-source-71e085db64c5296fd9b80141
    resource: repo://tests/unit_tests/test_otel_endpoints.py
  - id: openwiki-source-7be0fdefc402d868b9f2fdca
    resource: repo://tests/unit_tests/test_refresh_integration_downloads.py
  - id: openwiki-source-b631fb59f417cefbd356f03e
    resource: repo://tests/unit_tests/test_test_code_samples.py
  - id: openwiki-source-98a4de3472710de1bf3ccb4f
    resource: repo://tests/unit_tests/test_url_stub_noindex.py
generated: { by: "openwiki/0.4.3", at: "2026-11-09T08:07:38.321Z" }
---

## Choose the smallest meaningful boundary

Each layer proves a different contract. Start with the focused unit test or static check for the code or source convention changed. Add generated-site validation when a change can affect routes, imports, redirects, anchors, navigation, or OpenAPI input. Run credentialed samples only when an example crosses a provider or service boundary. A unit-test pass does not prove a rendered site, a reachable external URL, or a provider integration; a live run does not replace deterministic assertions about a transformation.

| Change | Deterministic local check | CI-only or network-dependent check | Boundary proved |
| --- | --- | --- | --- |
| Python pipeline, parser, builder, or generator | Owning `tests/unit_tests/test_*.py`, then `make test` for a wider change | None normally | Fixture-controlled transformation behavior, not remote services. |
| Authored MDX package floor or pin | `uv run python scripts/check_version_claims.py --files src/path/to/page.mdx` | Changed-document version-claim workflow | The literal `>=` or `==` version was published on its routed registry, not that it is the correct feature floor. |
| Formatting, types, spelling, or prose style | `make lint`; `make lint_prose FILES="src/..."` | None | Static quality or Vale style, not rendering, factual correctness, or runtime behavior. |
| `@[Name]` cross-reference and language scope | `make check-cross-refs` | CI repeats it | Source references resolve in applicable scopes, not final route reachability. |
| Authored route, redirect, navigation, anchor, or Agent Server OpenAPI input | `make broken-links-with-anchors`; `make check-openapi` | Hosted preview when deployment behavior matters | Freshly generated Mint tree, including routes, redirects, and anchors; not a deployed site. |
| Generated provider overview | `uv run python pipeline/tools/partner_pkg_table.py`, then inspect the diff | `check-generated-files` regenerates and diffs the owned file | The generated file agrees with its script and package metadata; manual edits are rejected. |
| Deprecated example pattern | Inspect the added-line diff for `create_react_agent` | `check-deprecated.yml` on eligible pull requests | New Python, Markdown, MDX, or notebook additions do not reintroduce the blocked pattern. |
| Egress IP inventory or its rendered tables | `uv run python scripts/generate_egress_ip_tables.py --check` | None required | The canonical JSON, its content-derived version, and both marked table blocks agree; a full build additionally proves publication. |
| OTLP setup prose | `make test TEST_FILE=tests/unit_tests/test_otel_endpoints.py` | None | Documentation syntax and Python exporter endpoint resolution, not trace ingestion by a live workspace. |
| Snippet markers or generated snippet MDX | Focused generator test, then `make code-snippets` and review the diff | None | Extractor/generator consistency; samples are not executed. |
| Runnable LangSmith sample | `make test-code-samples FILES="src/code-samples/langsmith/..."` | Same-repository PR or scheduled/manual sample workflow when it needs credentials | Local fixture compatibility or execution against available credentials and services. |
| Exported static-site external URLs | `make export-htmltest` where Mint export and network access are available | A suitable repeatable environment | External destinations in the exported subset only, not internal routes or fragments. |

```mermaid
flowchart TD
  Artifact["Changed artifact"] --> Kind{"What contract changed?"}
  Kind -->|"Python transformation"| Unit["Focused unit test"]
  Kind -->|"Format type spelling prose"| Static["make lint or lint_prose"]
  Kind -->|"Reference or deprecated pattern"| Source["check-cross-refs or check-deprecated"]
  Kind -->|"Snippet or runnable sample"| Sample["code-snippets or test-code-samples"]
  Kind -->|"Route navigation link OpenAPI"| Site["Build and Mint checks"]
  Kind -->|"Generated provider file"| Generated["Regenerate and diff"]
  Unit --> Wider["make test when scope is broad"]
  Static --> Review["Review result"]
  Source --> Review
  Sample --> Boundary{"Needs credentials or service?"}
  Site --> Review
  Generated --> Review
  Boundary -->|"no"| Review
  Boundary -->|"yes"| CI["Credentialed or networked CI boundary"]
  CI --> Review
  Wider --> Review
```

*Validation routes from the changed artifact to its owning deterministic check, then expands to generated output or remote boundaries only when required.*

## Core local gates

`make test` runs pytest with Internet sockets disabled while allowing Unix sockets; pytest discovers tests under `tests`, uses automatic asyncio mode, and defaults its asyncio fixture loop scope to a function. Tests that ordinarily make HTTP calls therefore need mocks or local test doubles.

`make lint` runs Ruff formatting and lint checks in diff mode over the configured Python-file scope, `ty check`, and Codespell over `src`, making it a static-quality gate separate from runtime tests and documentation generation. `make lint_prose` installs the configured Vale binary and checks either specified files or `src`, excluding `node_modules` and `src/code-samples`; it is a prose style gate rather than a rendering or factual-correctness check.

`make lint_md` is a separate optional Markdownlint command: it scans Markdown and MDX below `src` only when the `markdownlint` executable is installed. It is not part of `make lint`.

The main CI workflow runs reusable test, lint, and documentation-link workflows on pull requests, pushes to `main`, and manual dispatch, and separately runs merge-marker, source cross-reference, integration `docs_url`, and generated-provider-overview checks. The reusable test and lint jobs synchronize the test dependency group; the link job also installs Node 22 and Mint before running the generated-tree checks. The main workflow cancels an older run for the same workflow/ref when a newer push arrives; its focused checks have five-minute timeouts, while reusable test, lint, and link jobs have 20-minute timeouts.

### Version claims and deprecated patterns

The changed-document workflow is a read-only pull-request gate for changes to authored `src/**/*.mdx`, the checker, its ignore file, or its workflow. It finds the merge base, passes changed MDX files to `scripts/check_version_claims.py --files`, and skips Python setup and registry requests if that set is empty. It fails only when a successfully resolved PyPI or npm package does not contain a named version; registry outages and unavailable lookups are unresolved notes rather than false failures.

The checker routes scoped names to npm and extras to PyPI, then uses the nearest inline language label, `:::python`/`:::js` fences, and language path before defaulting to PyPI. It checks exact pins and truncated series floors, groups duplicate locations, and ignores exact configured exceptions before lookups. Focused tests protect this precedence, safe package-name handling, lookup failure semantics, and PyPI/npm payload parsing. Do not use a successful check as evidence that a feature was introduced at the stated floor.

`check-deprecated.yml` runs on pull requests targeting `main` when Python, Markdown, MDX, or the workflow changes. It checks only added lines in the PR merge diff (with two commits fetched) and fails if the deprecated `create_react_agent` string is newly added; it does not claim that every existing occurrence has been removed. The job has read-only contents permission, disables persisted checkout credentials, and has a five-minute timeout.

## Generated documentation and navigation

`DocumentationBuilder.build_all()` reconstructs the generated tree with Python and JavaScript OSS variants, unversioned Deep Agents Code and OpenWiki content, Managed Deep Agents language variants, shared assets, and npm snippet components; its Markdown processing rewrites language-sensitive links and snippet imports before output is written. Focused builder tests protect generated navigation topology by checking language-prefix rewriting, single unversioned OpenWiki output, language-scoped snippet imports, and rejection of source symlinks so build collection cannot copy content outside the source tree.

`src/docs.json` is the Mintlify site configuration, including navigation, so changes to its navigation or route configuration require generated-site validation rather than only source-level tests. The builder uses `src/docs.json` navigation routes beneath `oss/python/` and `oss/javascript/` to decide which language copies of shared OSS pages to emit; a route listed in neither language falls back to both copies, and an absent or invalid configuration also falls back to both. Test a navigation edit with the focused builder suite as well as `make broken-links-with-anchors`.

`make check-cross-refs` validates source `@[ref]` markers by scanning Markdown and MDX under `src`, skipping code fences, escaped references, generated code-sample snippets, and `node_modules`; unfenced shared OSS references must resolve in every applicable language scope. It is narrower than a site build and cannot prove a final route, redirect, fragment, or external destination.

`make broken-links-with-anchors` rebuilds documentation and runs Mint's broken-link checker from `build/` with anchor and redirect checking, while `make check-openapi` rebuilds then checks `langsmith/agent-server-openapi.json`; the reusable documentation workflow runs both on Node 22 and Mint 4.2.1181. The same workflow also runs `make check-mdx` to fail on unknown components and foreign syntax. `test_url_stub_noindex.py` requires every MDX page with `url:` frontmatter to set `noindex: true` so redirect-only sidebar stubs stay out of Mintlify discovery outputs including `llms.txt` and the sitemap.

CI's generated-file job regenerates `src/oss/python/integrations/providers/overview.mdx` with `pipeline/tools/partner_pkg_table.py` and fails on any diff, directing changes to the generator or package metadata instead of the generated file. It skips for a named automated package-download update or a `bypass-auto-check` label; otherwise it uses Python 3.13 and the test dependency group.

## Inventory and endpoint correctness

The egress IP inventory is a generated-publication contract. `scripts/generate_egress_ip_tables.py` accepts only schema version 1 with a nonempty version and address list; each entry must contain exactly service, cloud, region, and a globally routable IPv4 `/32`. It limits services to the two owning pages, clouds to GCP or AWS, regions to US, EU, or APAC, and rejects duplicate entries. The canonical inventory version is a SHA-256 digest of sorted address data.

Running the generator normally updates the inventory version and the one delimited generated block in each owning page. `--check` instead reports inventory-version or table drift and fails without writing. The focused suite mutates fixtures to prove invalid entries and duplicate addresses fail, stale JSON or table output is detected, regeneration converges, and a full `DocumentationBuilder` build copies the JSON bytes exactly once to the unversioned `build/langsmith/egress-ip-addresses.json` artifact. Edit the JSON and regenerate tables; do not hand-edit a rendered table.

OpenTelemetry endpoint tests scan every authored MDX file for two configuration errors: a generic `OTEL_EXPORTER_OTLP_ENDPOINT` must not already include `/v1/traces`, `/v1/metrics`, or `/v1/logs`, and collector exporter YAML must use `traces_endpoint` rather than `endpoint` when its value ends in `/v1/traces`. They also create a real Python OTLP HTTP exporter with a mocked session: `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` is used unchanged, while a generic base endpoint gains exactly one `/v1/traces` suffix. This protects endpoint construction and documentation conventions without contacting LangSmith.

## Generated snippets and runnable samples

`make code-snippets` extracts marked snippets and generates MDX without executing them, whereas `make test-code-samples` executes selected or eligible samples; trace-enabled full runs may regenerate snippet MDX after sample execution. The extractor line-parses supported language markers, strips `:remove:` regions, and writes normalized Bluehawk-compatible extracted files; `CODE_SNIPPET_SOURCES` limits processing to supported files below `src/code-samples` and replaces output only for those selected source stems.

The snippet-MDX generator expands only routable Python or TypeScript agent model strings into provider CodeGroups, preserving embedding and provider-specific chat model identifiers; focused tests enforce those exclusions, language-specific Google provider syntax, and a compatible resolved `@langchain/google` version. CI validates integration `docs_url` metadata with `scripts/refresh_integration_downloads.py --check-docs-urls`; the generator permits HTTP(S) and single-leading-slash site-relative URLs and rejects unsafe schemes.

The code-sample runner accepts supported executable files beneath `src/code-samples`, runs Python, TypeScript, Go, shell, Java, and Kotlin with their corresponding toolchains, and applies a per-sample timeout controlled by `CODE_SAMPLE_TIMEOUT_SECONDS` (1,200 seconds by default). It retries recognized rate limits using configurable attempts and backoff, reports exhausted rate limits as skips, while non-rate-limit failures make the command fail. `CODE_SAMPLE_PATHS` restricts both discovered samples and explicit `FILES` to directories below `src/code-samples`; focused tests verify that a CI product leg can receive all modified paths while retaining only its own files and that out-of-tree filters cannot widen execution. Runs default to four workers but serialize known shared-fixture groups. When tracing is enabled, trace collection is locked and failures collecting a trace warn without converting an already successful sample into a suite failure.

The `create-an-agent.py` executable sample directs a real LangSmith `Client` to a loopback HTTP fixture, asserts the create and retrieve requests and returned environment values, and removes fixture-only setup and assertions from extracted snippets; it validates local SDK request/response compatibility rather than a live LangSmith agent integration.

## CI-only sample boundary and exports

The code-sample workflow skips fork pull requests because samples can require secrets, runs changed executable samples on same-repository pull requests and all samples on scheduled/manual runs, and provisions provider credentials, language toolchains, and a pgvector PostgreSQL service. It partitions samples into OSS and LangSmith matrix legs, fails when a top-level sample directory has no assigned leg, and limits tracing plus trace-refresh publication to the OSS leg on scheduled or manually dispatched runs. Runs are concurrency-cancelled per workflow/ref; pull-request runs have a 60-minute timeout and scheduled/manual full runs have a 150-minute timeout.

The workflow passes provider keys and gateway endpoints through environment variables, so local execution should not assume those credentials exist. It waits for PostgreSQL readiness before samples run. A sample step is allowed to continue so trace refresh can proceed, but a later job result still reports sample failures; persistent rate-limit cases are explicitly skipped by the runner rather than treated as successful executions.

Trace-link collection is limited to source files with exactly one valid snippet ID: the runner stamps that ID in `LANGSMITH_DOCS_SNIPPET`, and the collector requires the same metadata on a root run rather than selecting an arbitrary run from the time window. On scheduled or manual code-sample runs, the workflow regenerates snippet MDX only when the run was not cancelled, fewer than 20 samples failed, and trace links changed; it then opens or updates a dedicated trace-refresh pull request containing the trace manifest and generated snippet artifacts.

`make export-htmltest` runs Mint export before htmltest; the export requires a Mint CLI with `mint export`, Node 20 or 22, and an Enterprise plan, while htmltest intentionally checks external URLs only because the export omits many pages. The export htmltest configuration disables internal paths and hashes, so it cannot establish internal navigation or anchor correctness.

The changelog-navigation Node tests use an in-memory DOM to verify that the self-hosted changelog indexes only visible stable minor releases, preserves excluded headings, coalesces mutation updates, cleans up on page changes, and falls back to an inline index without a sidebar. The release-watch `test_evidence.py` suite uses synthetic payloads and source/page text to test evidence parsing, surgical edit validation, and source-claim matching; it does not exercise remote release, GitHub, or Linear integrations.

## Failure triage

- **Version-claim failure:** correct the literal package version or a routing/context error. Treat an unresolved-registry note as missing evidence, not proof that an unpublished version is valid.
- **Deprecated-pattern failure:** remove the newly added `create_react_agent` usage; the check is diff-based, so inspect the added lines rather than attempting an unrelated repository-wide cleanup.
- **Builder, navigation, or Mint failure:** inspect regenerated `build/`, route ownership, redirects, snippet imports, and fragments. Source-map and generated-site checks prove different invariants.
- **Generated-file failure:** change the owning generator or metadata, regenerate, and commit the resulting generated output.
- **Egress failure:** fix the canonical JSON or its allowed values, run `python scripts/generate_egress_ip_tables.py`, and commit the resulting inventory/table changes.
- **OTLP endpoint failure:** use a base URL with `OTEL_EXPORTER_OTLP_ENDPOINT`, or use the signal-specific traces variable or `traces_endpoint` when supplying `/v1/traces`.
- **Sample failure or skip:** distinguish a nonzero program failure from an exhausted rate-limit skip, then inspect credentials, provider behavior, PostgreSQL readiness, timeout, and the selected toolchain. A skip is not a pass.
- **Export htmltest failure:** treat it as external-destination evidence only; use Mint checks for internal paths and anchors.

## Related guides

- [GitHub Actions](/openwiki/integrations/github-actions.md) explains the workflow and reusable-job integration boundary.
- [Mintlify Integration](/openwiki/integrations/mintlify.md) covers Mint configuration and generated-site behavior.
- [CLI Tools](/openwiki/operations/cli-tools.md) lists repository command-line tooling.
- [Builder Tests](/openwiki/testing/builder-tests.md) and [Conditional Rendering](/openwiki/testing/conditional-rendering.md) cover focused deterministic test boundaries.
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md) explains extraction, execution, tracing, and generated artifacts.
