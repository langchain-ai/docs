---
type: validation guide
title: Testing Overview
description: Change-oriented validation guidance for socket-isolated unit tests, version-claim checks, generated-document gates, and credentialed live code-sample execution. It distinguishes deterministic contracts from registry and upstream-network validation and explains their failure semantics.
tags: [testing, pytest, ci, documentation, code-samples, opentelemetry, versioning]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-17T08:22:51.028Z
sources:
  - id: openwiki-source-21617d8a6b2b570989a7c900
    resource: repo://.github/workflows/check-version-claims.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-0976291f8216a4c7151f20a7
    resource: repo://.github/workflows/refresh-external-versions.yml
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
  - id: openwiki-source-6b3ad04031a04803eb901844
    resource: repo://scripts/check_external_versions.py
  - id: openwiki-source-99b53585619b83f258314f8b
    resource: repo://scripts/check_version_claims.py
  - id: openwiki-source-2654e40275744504b4ca7e2b
    resource: repo://scripts/code_sample_tracing.py
  - id: openwiki-source-bd35b3b527f9ad0799d45497
    resource: repo://scripts/data/external_versions.yaml
  - id: openwiki-source-560bf24db9566b97ee19e383
    resource: repo://scripts/generate_code_snippet_mdx.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-583acf631f9a33a5389a3fde
    resource: repo://scripts/version_claims_ignore.txt
  - id: openwiki-source-6a4f3df816b7f7f45b6ac5b1
    resource: repo://src/code-samples/conftest.py
  - id: openwiki-source-a10b62517b8302a8d4cf3b31
    resource: repo://tests/unit_tests/test_check_external_versions.py
  - id: openwiki-source-607673c5c40214b511f9e0a7
    resource: repo://tests/unit_tests/test_check_version_claims.py
  - id: openwiki-source-71e085db64c5296fd9b80141
    resource: repo://tests/unit_tests/test_otel_endpoints.py
  - id: openwiki-source-1695beda93a0ca504f038424
    resource: repo://tests/unit_tests/test_skills.py
generated: { by: "openwiki/0.4.3", at: "2026-09-17T08:22:51.028Z" }
---

## Choose validation by boundary

The repository deliberately separates deterministic, socket-isolated unit tests from built-document checks, registry and upstream-network checks, and executable samples that are expected to contact real services. Select the narrowest check that covers the change. A pass in one boundary does not establish a pass in another.

| Change | Run locally | What a pass establishes | Important limit |
| --- | --- | --- | --- |
| Pipeline, parser, preprocessor, watcher, skill, version-checker, or authored OTel contract | `make test` | Isolated behavior and repository structural contracts | Network sockets are disabled. |
| Package versions named in documentation | `uv run python scripts/check_version_claims.py --files src/path/page.mdx` | The named package release exists on its resolved registry | Published existence is not proof that the floor is sufficient for a feature. |
| Requirement deliberately mirrored from another project | `uv run python scripts/check_external_versions.py --only <id>` | The registered page value equals the registered upstream source | This is an upstream-network check, not socket-isolated unit testing. |
| Built documentation, internal links, or anchors | `make broken-links-with-anchors` | A freshly built tree passes Mint's filtered link and anchor check | This is not a source-reference or live URL check. |
| Source `@[ref]` references | `make check-cross-refs` | Each eligible reference resolves in every rendering scope | Generated code-sample snippets are excluded. |
| Provider overview or external integration metadata | Run its generator or `uv run python scripts/refresh_integration_downloads.py --check-docs-urls` | Generated output is current, or URL schemes are safe | URL-scheme validation makes neither requests nor writes. |
| Mint export external resources | `make export-htmltest` | Configured external resources in an export pass htmltest | Internal paths and hashes are intentionally disabled. |
| Runnable example | `make test-code-samples [FILES="..."]` | The selected program exits successfully in its actual toolchain and environment | It may need credentials, PostgreSQL, and live providers. |

```mermaid
flowchart TD
  Change["Documentation or code change"] --> Unit["make test"]
  Unit --> Offline["Socket-isolated unit contracts"]
  Change --> Package["Package version checker"]
  Package --> Registry["PyPI or npm availability"]
  Change --> Mirror["External version checker"]
  Mirror --> Upstream["GitHub upstream comparison"]
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

This boundary diagram distinguishes offline assertions from checks that deliberately query package registries, upstream GitHub sources, or live sample dependencies.

## Socket-isolated pytest suite

Run the core suite with:

```bash
make test
```

`TEST_FILE` defaults to `tests/unit_tests`; for example, run `make test TEST_FILE=tests/unit_tests/test_check_version_claims.py` while changing version-claim parsing. The target runs `uv run pytest --disable-socket --allow-unix-socket $(TEST_FILE) -vv`. Pytest discovers `test_*.py` and `test_*`, uses asyncio auto mode with function-scoped fixture loops, reports extra outcomes, and shows the five slowest tests. Install the test group with `uv sync --group test`.

Socket isolation is an invariant: unit tests must use mocks, temporary files, or permitted Unix sockets rather than opening a network connection. In particular, checker unit tests mock registry and GitHub retrieval; they validate parsing, selection, safety, rewrites, and outcome classification without making PyPI, npm, or GitHub requests. The `file_system` context manager creates disposable `src/` and `build/` trees for filesystem tests.

### Focused contracts

- **Builder:** `test_builder.py` covers copying supported source files, ignoring unsupported extensions, preserving directory structure, preprocessing, and Python/JavaScript builds. See [Builder Tests](/openwiki/testing/builder-tests.md).
- **Parser, rendering, autolinks, and watcher:** retain coverage for Markdown AST and emitted syntax, front matter, headings, code blocks, admonitions, tabs, conditionals, source lines, language-scoped `@[Reference]` replacement, and ignored editor backup/temporary files. Fenced and escaped text must remain protected.
- **Cross-reference checker:** source scanning skips code-sample snippets and `node_modules`, ignores fenced code and escaped references, and requires an unfenced shared OSS reference to resolve for every applicable scope.
- **Agent skills:** structural tests require every `.agents/skills/` directory to have valid matching frontmatter, real referenced repository paths and Make targets, and catalogue rows that agree with the tree. See [Agent Authoring Skills](/openwiki/operations/agent-skills.md).
- **Package claims:** test resolver precedence using ambiguous names that exist in both ecosystems, shortened-series matching, exact pins, ignore-file parsing, and registry outage classification. Mock payloads rather than relying on registry state.
- **External mirrors:** test exact-one page matching, digit-only rewrites, registry input containment and allowlists, upstream retrieval, and the different check- and write-mode exits. The committed-registry test ensures every registered target page exists and its pattern has exactly one match.
- **Integration metadata:** the issue-form parser maps `###` sections without evaluating values, validates required and language-specific package metadata, and returns a nonzero CLI exit for invalid input. `docs_url` tests preserve safe HTTP(S) and site-relative URL handling.

### OpenTelemetry documentation contract

`tests/unit_tests/test_otel_endpoints.py` scans every `.mdx` file below `src`. A generic `OTEL_EXPORTER_OTLP_ENDPOINT` must not carry a `/v1/traces`, `/v1/metrics`, or `/v1/logs` suffix; the HTTP exporter appends its signal path. In documents containing Collector exporters, a full traces URL must use `traces_endpoint`, not generic `endpoint`.

Its runtime cases remain offline: isolated environment dictionaries instantiate `OTLPSpanExporter`, attach it to a `TracerProvider` and `SimpleSpanProcessor`, and mock session `post`. They establish that a trace-specific URL is used unchanged and a generic base gains exactly one `/v1/traces` suffix. Preserve both the authored and mocked-transport contracts when changing [Trace with OpenTelemetry](../../src/langsmith/trace-with-opentelemetry.mdx).

## Package-version claims

`scripts/check_version_claims.py` checks whether versions explicitly named in `src/**/*.mdx` were published. It scans `>=` floors and `==` pins, including extras and npm-scoped names. This is an **availability** check only: it must not upgrade a documented floor, decide when a feature landed, or infer that a published release is sufficient. Those compatibility decisions remain with the feature owner.

### Resolve the registry before looking up a release

A bare name may have unrelated PyPI and npm histories. For each specifier, the checker chooses an ecosystem in this order: npm `@scope/` syntax, Python extras, the nearest same-line Python or JavaScript label, an enclosing `:::python` or `:::js` block, page-path context (including a JavaScript-only page override), then PyPI by default. It groups claims by package and queries those packages concurrently. An exact release passes when it is published; a truncated floor such as `>=0.7` passes when a published version begins `0.7.`, but `1.1` does not match `1.14`.

```mermaid
flowchart TD
  Spec["Specifier in an MDX page"] --> Syntax{"Scope or extras"}
  Syntax -->|"npm scope"| Npm["npm"]
  Syntax -->|"Python extras"| Pypi["PyPI"]
  Syntax -->|"neither"| Context["Label fence or page path"]
  Context -->|"JavaScript"| Npm
  Context -->|"Python or default"| Pypi
  Npm --> Lookup["Fetch published releases"]
  Pypi --> Lookup
  Lookup --> Result{"Claimed version exists"}
  Result -->|"yes"| Available["Pass availability check"]
  Result -->|"no"| Unpublished["Nonzero unpublished-version failure"]
  Lookup --> Unresolved["Unresolved lookup note"]
```

This flow shows selection and published-version checking, not a decision about the appropriate feature floor.

### Failure semantics and exceptions

A registry timeout, malformed response, private/unavailable package, or unsafe package name is **unresolved**. It is reported as a note and is not silently treated as a published version; equally, it is not misreported as an unpublished-version failure. Only a successful registry lookup that lacks the claimed release is a ghost-version failure. `scripts/version_claims_ignore.txt` provides reviewed exact-specifier exceptions for intentional sentinel floors and placeholder examples; prefer correcting a claim to adding a standing exception.

Use `--files` to reproduce a changed-document gate, and `--advisory-only` to report findings while returning zero:

```bash
uv run python scripts/check_version_claims.py --files src/langsmith/evaluators.mdx
uv run python scripts/check_version_claims.py --advisory-only
```

The read-only pull-request workflow triggers for documentation and checker-related changes, derives changed `.mdx` files below `src/` from the merge-base diff, and runs the checker only when that set is nonempty. It blocks a PR only for versions proven never published. The Monday full sweep runs in advisory mode because it also catches untouched pages whose lookups later stop resolving without making the schedule red.

## Mirrored upstream requirements

A mirrored requirement is different from a package floor: the documentation intentionally repeats a version another project owns and must equal its source. `scripts/data/external_versions.yaml` is the state owner. Each entry has a stable ID and label, one target page below `src/`, a target regex with a named `version` capture that matches exactly once, and either a GitHub file plus source regex or a GitHub latest-release source. Do not register a feature floor here: an upstream source cannot determine whether a local feature needs a newer minimum.

Before retrieval or writing, `scripts/check_external_versions.py` rejects pages outside `src/`, unsafe repository slugs and source paths, unknown source types, and patterns without the named capture. It reads a file at upstream `HEAD` or a latest release tag, compares that value with the one page match, and can replace only the captured version digits. A version-only rewrite preserves surrounding text, URLs, flags, and prerequisites but cannot validate them semantically.

```mermaid
flowchart TD
  Entry["external_versions.yaml entry"] --> Validate["Validate page and source inputs"]
  Validate --> Documented["Find one page version"]
  Validate --> Fetch["Fetch GitHub file or release"]
  Documented --> Compare{"Versions equal"}
  Fetch --> Compare
  Compare -->|"yes"| Sync["In sync"]
  Compare -->|"no"| Drift["Report drift"]
  Drift --> Mode{"Write mode"}
  Mode -->|"no"| CheckFail["Nonzero check result"]
  Mode -->|"yes"| Rewrite["Replace captured digits only"]
  Fetch --> Unreadable["Report unresolved entry"]
```

This flow distinguishes an equality contract with an upstream source from the package registry's published-release check.

Run a read-only comparison or limit it to an entry during diagnosis:

```bash
uv run python scripts/check_external_versions.py
uv run python scripts/check_external_versions.py --only codex-cli
uv run python scripts/check_external_versions.py --write
```

Without `--write`, drift and unreadable entries produce a nonzero result. With `--write`, resolvable drift is rewritten, but upstream outages and other unreadable entries are reported and do not stop remaining entries from being prepared for review. Thus an unavailable upstream source is unresolved, never silently considered synchronized or published. Review every rewrite against upstream because only digits changed.

The trusted refresh workflow runs Monday at 08:00 UTC or manually with repository write and pull-request permissions. It supplies a GitHub token to `--write`, does nothing when `src/` has no diff, and otherwise maintains one `chore/refresh-external-versions` pull request by appending to its open branch or creating it. The generated PR specifically requires human review of the surrounding requirement, including changed flags or peer dependencies.

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

Start triage from the relevant row in the matrix. Treat a unit-test socket error as a test-boundary violation, a generated diff as an update-to-source-or-generator task, and a sample failure as a potentially live-environment problem. Treat a version-check unresolved result as an observation requiring a later lookup, not evidence that a version exists. Treat a rate-limit skip as unexecuted work—not a passing example—and use the workflow run URL for a scheduled-run escalation.

## Related documentation

- [Language Versioning Strategy](/openwiki/concepts/versioning.md)
- [Build system](/openwiki/architecture/build-system.md)
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md)
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md)
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md)
- [Builder Tests](/openwiki/testing/builder-tests.md)
