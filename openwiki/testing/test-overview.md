---
type: validation guide
title: Testing Overview
description: Change-oriented validation guidance for socket-isolated unit tests, generated-document checks, and credentialed live code-sample execution. It explains CI selection, sample timeouts, PostgreSQL and provider setup, trace-link refreshes, and failure triage.
tags: [testing, pytest, ci, documentation, code-samples, opentelemetry]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-11T08:21:01.441Z
sources:
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-751a704f6f25787856371177
    resource: repo://.github/workflows/test-code-samples-linear.yml
  - id: openwiki-source-97746d8f3662d803e625550e
    resource: repo://.github/workflows/test-code-samples.yml
  - id: openwiki-source-71ee7a4afbd2d6aa7b29f3d1
    resource: repo://htmltest-mint-export.yml
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-0a0a6c8d7a88288e6b6b9b5b
    resource: repo://scripts/check_cross_refs.py
  - id: openwiki-source-2654e40275744504b4ca7e2b
    resource: repo://scripts/code_sample_tracing.py
  - id: openwiki-source-560bf24db9566b97ee19e383
    resource: repo://scripts/generate_code_snippet_mdx.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-6a4f3df816b7f7f45b6ac5b1
    resource: repo://src/code-samples/conftest.py
  - id: openwiki-source-71e085db64c5296fd9b80141
    resource: repo://tests/unit_tests/test_otel_endpoints.py
  - id: openwiki-source-1695beda93a0ca504f038424
    resource: repo://tests/unit_tests/test_skills.py
generated: { by: "openwiki/0.4.3", at: "2026-09-11T08:21:01.441Z" }
---

## Choose validation by boundary

The repository deliberately separates deterministic, socket-isolated unit tests from generated-document checks and executable samples that are expected to contact real services. Select the narrowest check that covers the change. A pass in one boundary does not establish a pass in another.

| Change | Run locally | What a pass establishes | Important limit |
| --- | --- | --- | --- |
| Pipeline, parser, preprocessor, watcher, skill, or authored OTel contract | `make test` | Isolated behavior and repository structural contracts | Network sockets are disabled. |
| Built documentation, internal links, or anchors | `make broken-links-with-anchors` | A freshly built tree passes Mint's filtered link and anchor check | This is not a source-reference or live URL check. |
| Source `@[ref]` references | `make check-cross-refs` | Each eligible reference resolves in every rendering scope | Generated code-sample snippets are excluded. |
| Provider overview or external integration metadata | Run its generator or `uv run python scripts/refresh_integration_downloads.py --check-docs-urls` | Generated output is current, or URL schemes are safe | URL-scheme validation makes neither requests nor writes. |
| Mint export external resources | `make export-htmltest` | Configured external resources in an export pass htmltest | Internal paths and hashes are intentionally disabled. |
| Runnable example | `make test-code-samples [FILES="..."]` | The selected program exits successfully in its actual toolchain and environment | It may need credentials, PostgreSQL, and live providers. |

```mermaid
flowchart TD
  Change["Documentation or code change"] --> Unit["make test"]
  Unit --> Offline["Socket-isolated unit contracts"]
  Change --> Build["Build and Mint checks"]
  Build --> Links["Built links and anchors"]
  Change --> RefCheck["make check-cross-refs"]
  RefCheck --> Maps["Source link-map scopes"]
  Change --> Generated["Generated metadata checks"]
  Generated --> SafeURL["Offline docs URL scheme validation"]
  Change --> Samples["make test-code-samples"]
  Samples --> Live["Live providers credentials and PostgreSQL"]
  Live --> Trace["Optional trace manifest and snippet links"]
```

This boundary diagram distinguishes offline assertions and generated-document checks from deliberately live sample execution and its optional trace-publication path.

## Socket-isolated pytest suite

Run the core suite with:

```bash
make test
```

`TEST_FILE` defaults to `tests/unit_tests`; for example, run `make test TEST_FILE=tests/unit_tests/test_skills.py` while changing agent-skill contracts. The target runs `uv run pytest --disable-socket --allow-unix-socket $(TEST_FILE) -vv`. Pytest discovers `test_*.py` and `test_*`, uses asyncio auto mode with function-scoped fixture loops, reports extra outcomes, and shows the five slowest tests. Install the test group with `uv sync --group test`.

Socket isolation is an invariant: unit tests must use mocks, temporary files, or permitted Unix sockets rather than opening a network connection. The `file_system` context manager creates disposable `src/` and `build/` trees for filesystem tests.

### Focused contracts

- **Builder:** `test_builder.py` covers copying supported source files, ignoring unsupported extensions, preserving directory structure, preprocessing, and Python/JavaScript builds. See [Builder Tests](/openwiki/testing/builder-tests.md).
- **Parser, rendering, autolinks, and watcher:** retain coverage for Markdown AST and emitted syntax, front matter, headings, code blocks, admonitions, tabs, conditionals, source lines, language-scoped `@[Reference]` replacement, and ignored editor backup/temporary files. Fenced and escaped text must remain protected.
- **Cross-reference checker:** source scanning skips code-sample snippets and `node_modules`, ignores fenced code and escaped references, and requires an unfenced shared OSS reference to resolve for every applicable scope.
- **Agent skills:** structural tests require every `.agents/skills/` directory to have valid matching frontmatter, real referenced repository paths and Make targets, and catalogue rows that agree with the tree. See [Agent Authoring Skills](/openwiki/operations/agent-skills.md).
- **Integration metadata:** the issue-form parser maps `###` sections without evaluating values, validates required and language-specific package metadata, and returns a nonzero CLI exit for invalid input. `docs_url` tests preserve safe HTTP(S) and site-relative URL handling.

### OpenTelemetry documentation contract

`tests/unit_tests/test_otel_endpoints.py` scans every `.mdx` file below `src`. A generic `OTEL_EXPORTER_OTLP_ENDPOINT` must not carry a `/v1/traces`, `/v1/metrics`, or `/v1/logs` suffix; the HTTP exporter appends its signal path. In documents containing Collector exporters, a full traces URL must use `traces_endpoint`, not generic `endpoint`.

Its runtime cases remain offline: isolated environment dictionaries instantiate `OTLPSpanExporter`, attach it to a `TracerProvider` and `SimpleSpanProcessor`, and mock session `post`. They establish that a trace-specific URL is used unchanged and a generic base gains exactly one `/v1/traces` suffix. Preserve both the authored and mocked-transport contracts when changing [Trace with OpenTelemetry](../../src/langsmith/trace-with-opentelemetry.mdx).

## Documentation, metadata, and export gates

`make broken-links-with-anchors` builds first, then runs Mint from `build/` with anchors enabled; filtering removes known deployment-generated OpenAPI and standalone-snippet noise, while remaining reported links fail the target. `make broken-links` omits anchors. The reusable CI link job uses Python 3.13 and Node 22, runs this target plus `make check-openapi`, and has a 20-minute limit.

`make check-cross-refs` is instead a source-level map check. It reports unresolved file, line, reference, and scope and exits 1. Generated provider-overview validation is another distinct gate: CI regenerates `src/oss/python/integrations/providers/overview.mdx` and fails on a diff, except for the defined automated-update or `bypass-auto-check` exemptions. Change the generator or `packages.yml`, regenerate, and commit the result rather than editing the overview by hand.

The external integration `docs_url` check is intentionally offline: it accepts HTTP(S) and single-slash site-relative URLs, rejects protocol-relative and unsafe schemes, and performs no requests or writes. Full integration-table generation is different: it merges hosted front matter with third-party rows and retrieves npm/PyPI download data over the network.

`make export-htmltest` makes a Mint export, unpacks it, and runs htmltest. Because an export lacks a complete page set, its configuration checks external URLs but disables internal paths and internal hashes; it limits external HTTP concurrency to four and timeout to 30 seconds. The scheduled htmltest workflow runs Monday at 08:00 UTC and can also be dispatched manually.

## Executable code samples

Run all eligible samples, or a space-separated subset, with:

```bash
make test-code-samples
make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
```

The runner selects `.py`, `.ts`, `.java`, `.kt`, `.go`, and `.sh` files below `src/code-samples`; an explicit `FILES` list is checked for existence, supported extension, and location, while an unset list recursively selects all eligible files outside `__pycache__` and `node_modules`. It runs Python through `uv`, TypeScript through `npx tsx`, Go through `go run`, shell through `bash`, and Java/Kotlin single-file scripts through JBang on Java 21. TypeScript, Go, and shell run from `src/code-samples` so shared dependencies resolve; Python and JBang run from the repository root. `src/code-samples/package.json` owns the Node dependencies used by that TypeScript execution path.

Every invocation inherits the caller environment and is bounded by `CODE_SAMPLE_TIMEOUT_SECONDS`, which defaults to **1,200 seconds per sample**. A timeout, missing executable, or nonzero exit is normally a sample failure. This runner is intentionally live—not an extension of `make test`—so diagnose provider credentials, service readiness, dependencies, and sample behavior separately from a socket-isolated test failure.

### CI selection, services, and credentials

The code-sample workflow runs for relevant pull requests, manual dispatch, and at 00:00 UTC on the first day of each month. It skips fork PRs because repository secrets are unavailable there. PR runs compute the merge-base diff and test only modified eligible sample files; scheduled and manual runs select all samples. The job allows 60 minutes for a PR and 90 minutes for full runs, independently of the per-sample timeout.

CI installs Python/uv, Node 20, Java 21/JBang, and the Go version declared by `src/code-samples/go.mod`. It provisions `pgvector/pgvector:pg17`, waits for the local port, and passes `POSTGRES_URI=postgresql://postgres:postgres@127.0.0.1:5432/postgres?sslmode=disable` to children along with Anthropic, LangSmith/gateway, OpenAI, Tavily, Google, and Daytona credentials. For local PostgreSQL-backed samples, `src/code-samples/conftest.py` first honors `POSTGRES_URI`; otherwise it attempts a pgvector testcontainer, then Docker, then the default local URI. Its store-preparation helper drops the shared store and migration tables before a fresh schema setup.

### Rate limits are skips, not executions

The runner recognizes output that combines `429` with a LangSmith rate-limit phrase. It retries up to three total attempts, waiting 15 seconds between attempts. If all attempts are rate-limited, it records the sample as skipped rather than failing the runner; failures for any other reason remain nonzero. Therefore, a green job with persistent rate-limit skips proves neither that those examples ran successfully nor that their output is current.

### Monthly trace collection and generated links

Scheduled and manual full runs set `CODE_SAMPLE_TRACING=1` and `LANGSMITH_PROJECT=docs-code-samples`. Successful samples then enable `LANGSMITH_TRACING`, and the runner attempts trace collection. A trace-collection error fails the run even if the sample command passed.

For a source file with exactly one `:snippet-start:` marker, collection polls LangSmith for a recent agent-like root run, shares the chosen run publicly, and records source path, URL, run/trace IDs, name, and update time under that snippet ID in `src/code-samples/trace-links.json`. Files with no marker or no qualifying agent run receive no link; multi-snippet files are recorded under `skipped_multi_snippet` and are deliberately excluded until split. `make code-snippets` loads that manifest while generating snippet MDX and appends or replaces a `View example trace` Card only when a URL is present.

After a successful full run and snippet regeneration, CI preserves the manifest and generated snippets, switches to `chore/refresh-code-sample-traces`, and opens or updates a pull request with changes to `src/code-samples/trace-links.json` and `src/snippets/code-samples`. This publication step has write and pull-request permissions; ordinary PR sample checks do not perform it. Locally, `make update-code-sample-traces` supplies tracing, runs the samples, and regenerates snippets; it requires `LANGSMITH_API_KEY`.

A separate `workflow_run` workflow watches scheduled **Test Code Samples** completions. If the scheduled run fails or is cancelled, it creates a Linear issue with the run URL using the configured Linear API key and team key. It does not create tickets for pull-request, manual, or successful scheduled runs.

## CI triage

`ci.yml` runs on pull requests, pushes to `main`, and manual dispatch; concurrency cancels an older run for the same workflow/ref. It invokes reusable test, lint, and documentation-link workflows on Python 3.13 and separately checks merge-conflict markers, cross-references, external integration URLs, and generated files.

Start triage from the relevant row in the matrix. Treat a unit-test socket error as a test-boundary violation, a generated diff as an update-to-source-or-generator task, and a sample failure as a potentially live-environment problem. Treat a rate-limit skip as unexecuted work—not a passing example—and use the workflow run URL for a scheduled-run escalation.

## Related documentation

- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md)
- [Agent Authoring Skills](/openwiki/operations/agent-skills.md)
- [CLI Tools](/openwiki/operations/cli-tools.md)
- [Quickstart](/openwiki/quickstart.md)
- [Builder Tests](/openwiki/testing/builder-tests.md)
