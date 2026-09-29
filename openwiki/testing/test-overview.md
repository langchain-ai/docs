---
type: validation guide
title: Testing Overview
description: A change-oriented map for choosing isolated tests, source and rendered-document checks, generated-file validation, live code-sample execution, and deployed llms.txt coverage. Use it to match a change to its dependency boundary and interpret CI failures accurately.
tags: [testing, pytest, ci, documentation, code-samples, versioning]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-29T08:22:38.059Z
sources:
  - id: openwiki-source-5c124605ed6e394bffee862c
    resource: repo://.github/workflows/_check-links.yml
  - id: openwiki-source-f35e7c44cc1805709393a581
    resource: repo://.github/workflows/_lint.yml
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-477c95c54c9043bc75d26802
    resource: repo://.github/workflows/check-llms-urls.yml
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
  - id: openwiki-source-9c06bd9d7d25770709e07c7c
    resource: repo://.mise.toml
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
  - id: openwiki-source-6b3ad04031a04803eb901844
    resource: repo://scripts/check_external_versions.py
  - id: openwiki-source-7c3064080adf2cb0048e51fc
    resource: repo://scripts/check_llms_urls.py
  - id: openwiki-source-99b53585619b83f258314f8b
    resource: repo://scripts/check_version_claims.py
  - id: openwiki-source-2654e40275744504b4ca7e2b
    resource: repo://scripts/code_sample_tracing.py
  - id: openwiki-source-bd35b3b527f9ad0799d45497
    resource: repo://scripts/data/external_versions.yaml
  - id: openwiki-source-560bf24db9566b97ee19e383
    resource: repo://scripts/generate_code_snippet_mdx.py
  - id: openwiki-source-c1655a468cf6a1dff9722eb1
    resource: repo://scripts/install-vale.sh
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-583acf631f9a33a5389a3fde
    resource: repo://scripts/version_claims_ignore.txt
  - id: openwiki-source-6a4f3df816b7f7f45b6ac5b1
    resource: repo://src/code-samples/conftest.py
  - id: openwiki-source-e0401fc6d5f2a13d30455bd9
    resource: repo://src/code-samples/package.json
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
  - id: openwiki-source-a10b62517b8302a8d4cf3b31
    resource: repo://tests/unit_tests/test_check_external_versions.py
  - id: openwiki-source-607673c5c40214b511f9e0a7
    resource: repo://tests/unit_tests/test_check_version_claims.py
  - id: openwiki-source-b68d7bad2afd9a38e8c331d5
    resource: repo://tests/unit_tests/test_generate_code_snippet_mdx.py
  - id: openwiki-source-71e085db64c5296fd9b80141
    resource: repo://tests/unit_tests/test_otel_endpoints.py
  - id: openwiki-source-7be0fdefc402d868b9f2fdca
    resource: repo://tests/unit_tests/test_refresh_integration_downloads.py
  - id: openwiki-source-1695beda93a0ca504f038424
    resource: repo://tests/unit_tests/test_skills.py
  - id: openwiki-source-1eb6a61d042052ba1402c2eb
    resource: repo://uv.lock
generated: { by: "openwiki/0.4.3", at: "2026-09-29T08:22:38.059Z" }
---

## Choose the validation boundary

Validation is split by dependency boundary. Start with the narrowest check that can prove the change, then add checks when it affects generated output, remote data, a deployed service, or an executable example. A passing socket-isolated unit test does not prove a registry response, rendered Mintlify output, or a live provider call.

| Change | Focused command | What it validates | Boundary |
| --- | --- | --- | --- |
| Python pipeline, parser, skill, or checker behavior | `make test TEST_FILE=tests/unit_tests/test_builder.py` | Deterministic contracts in temporary/local fixtures | Isolated unit test |
| Python environment or dependency change | `uv sync --group test` | The locked test environment can be installed | Local dependency resolution |
| Prose in a document | `make lint_prose FILES="src/path/page.mdx"` | Vale terminology and style rules | Prose lint |
| Build, redirect, anchor, or OpenAPI change | `make broken-links-with-anchors` and `make check-openapi` | The generated `build/` tree consumed by Mint | Rendered-document check |
| Source `@[ref]` mapping | `make check-cross-refs` | References resolve in every applicable build scope | Source structural check |
| Integration external-document metadata | `uv run python scripts/refresh_integration_downloads.py --check-docs-urls` | `docs_url` values are safe link targets | Deterministic metadata check |
| Package version claim | `uv run python scripts/check_version_claims.py --files src/path/page.mdx` | A documented release is available from its selected registry | Registry network check |
| Upstream-mirrored requirement | `uv run python scripts/check_external_versions.py --only <id>` | A registered page value matches its GitHub source | Upstream network check |
| Runnable example | `make test-code-samples FILES="src/code-samples/..."` | A real program runs with its language environment, credentials, and services | Live sample |
| Deployed `llms.txt` coverage | `python3 scripts/check_llms_urls.py` | Every deployed sitemap page is reachable from the served index hierarchy | Hosted-site network check |

```mermaid
flowchart TD
  Change["Change"] --> Unit["Isolated unit tests"]
  Unit --> Contracts["Local contracts and fixtures"]
  Change --> Build["Built-document checks"]
  Build --> Rendered["Mint build, links, anchors, OpenAPI"]
  Change --> Registry["Registry and upstream checks"]
  Registry --> Remote["PyPI, npm, GitHub sources"]
  Change --> Live["Live code samples"]
  Live --> Services["Providers, credentials, PostgreSQL"]
  Change --> Hosted["Hosted llms coverage"]
  Hosted --> Served["Served indexes and sitemap"]
```

This flow separates local contracts from generated documents, remote sources, live services, and the deployed site; success at one boundary is not evidence for another.

## Toolchain and isolated tests

The project requires Python `>=3.13.0,<4.0.0`. Local mise selects Python 3.13 and uv 0.9.26, while `pyproject.toml` accepts uv 0.9.26 or newer. Change dependency declarations first, resolve with uv, and commit the resulting `uv.lock` update rather than treating the lockfile as an independent requirements source.

For normal development, use `mise trust && mise install`, then:

```bash
uv sync --group test
make test
make test TEST_FILE=tests/unit_tests/test_builder.py
```

`make test` runs `uv run pytest --disable-socket --allow-unix-socket $(TEST_FILE) -vv`. Pytest uses automatic asyncio mode and function-scoped asyncio fixture loops, with verbose reporting and five slowest-test durations. Unit tests must mock Internet-facing dependencies; Unix sockets remain allowed. A socket violation is a test-boundary failure, not evidence that an external service is down.

The reusable test, lint, and documentation-link workflows install the test group with `UV_FROZEN=true`, so CI does not silently refresh a stale lockfile. The reusable test and link workflows also set `UV_NO_SYNC=true`; their explicit `uv sync --group test` step is the controlled installation point.

### Focused local contracts

- **Builder.** `tests/unit_tests/test_builder.py` checks the supported copy-extension set, an empty source tree, and copying a local TSX snippet component to `build/snippets`. Use it when changing copy policy. A full builder run removes and recreates `build/`, emits Python and JavaScript OSS variants plus unversioned content, then copies shared assets and package snippet components. Follow a builder change with a rendered-document check. See [Builder tests](/openwiki/testing/builder-tests.md).
- **Agent skills.** Skill tests require a matching kebab-case directory/frontmatter identity, supported frontmatter, valid referenced paths and Make targets, and exact catalogues in `README.md` and `AGENTS.md`.
- **Cross references and endpoint prose.** The cross-reference checker ignores code samples, `node_modules`, fenced code, and escaped references, but shared OSS references must resolve in every build scope. The OpenTelemetry test rejects signal paths in generic `OTEL_EXPORTER_OTLP_ENDPOINT`; Collector-exporter trace URLs belong in `traces_endpoint`.
- **Integration `docs_url` metadata.** `--check-docs-urls` makes no network calls and writes nothing. It accepts `https://`, `http://`, and a single-leading-slash site-relative path, while rejecting missing values, protocol-relative URLs, and unsafe schemes. Main CI runs this validator as a separate read-only job.
- **Code-snippet MDX rules.** `tests/unit_tests/test_generate_code_snippet_mdx.py` guards the generated Deep Agents model tabs and language-specific sample invariants without running providers: embeddings and provider-specific chat constructors stay unchanged, TypeScript uses `google:` and camel-case `googleSearch`, Python retains `google_genai:`, and both the declared and locked `@langchain/google` versions must include the required tool-configuration fix. Use these tests when changing code-sample dependencies, model rewriting, or generated CodeGroup behavior.

Vale has a single canonical pin in `.mise.toml`. `make lint_prose` installs that version through `scripts/install-vale.sh` and excludes `node_modules` and `src/code-samples`; update the mise pin rather than copying a version into a workflow. The installer validates the version, reuses a matching binary where possible, chooses supported Linux/macOS assets, and falls back to `go install` after a release-download failure.

## Rendered documentation and generated files

`make build` produces `build/`; Mint link and OpenAPI validation operate on that generated tree, not directly on `src`. `make broken-links-with-anchors` builds, checks anchors and redirects, filters known generated OpenAPI and standalone-snippet noise, and fails if relevant reported links remain. `make broken-links` omits anchor checking. The reusable documentation workflow uses Node 22, caches Mint, runs the anchor/redirect check, then runs `make check-openapi`.

`make export-htmltest` is a separate external-link boundary: it exports Mint documentation, unpacks the export, then runs htmltest. Because the export lacks a complete page set, its configuration disables internal path and internal-hash checks while checking external resources. It limits external HTTP concurrency to four and timeout to 30 seconds. A source or unit check is therefore not a substitute for this rendered/export validation.

The main CI workflow cancels superseded runs for the same workflow/ref and dispatches reusable test, lint, and link jobs on Python 3.13. It also checks conflict markers, source cross-references, safe external integration documentation URLs, and generated output. Its generated-file gate regenerates `src/oss/python/integrations/providers/overview.mdx` and fails on a diff: change `pipeline/tools/partner_pkg_table.py` or `packages.yml`, regenerate, and commit the result. Only the designated automated package-download update PR and the `bypass-auto-check` label bypass that gate.

## Registry and upstream network checks

`scripts/check_version_claims.py` treats explicit `>=` floors and `==` pins in MDX as published-availability assertions, not compatibility claims. It selects PyPI or npm from scoped syntax, extras, nearby labels, language fences, page context, and a PyPI default. Lookups are concurrent; exact releases must exist, while truncated series must be correctly delimited so `1.1` does not match `1.14`.

A timeout, malformed response, private or unsafe input, or unavailable registry lookup is **unresolved**, not confirmation that a version is published or unpublished. `scripts/version_claims_ignore.txt` is an exact-specifier exception mechanism for reviewed sentinel floors and placeholders; prefer correcting documentation to masking a claim. The pull-request workflow uses the merge base to run only for changed `src/**/*.mdx` files and has a 10-minute limit. The Monday full sweep is advisory-only, so an unavailable lookup or yanked release reports findings without failing the schedule.

External-version synchronization is a distinct equality contract. `scripts/data/external_versions.yaml` allowlists a `src` page, an exactly-once page pattern with a named version capture, and a GitHub file or latest-release source. Validation rejects unsafe configuration before fetching. Check mode fails for drift or unreadable inputs. Write mode replaces only captured version digits and continues past unreadable upstream sources, allowing a review to contain resolvable updates without claiming unavailable sources synchronized. The Monday 08:00 UTC/manual workflow can write and maintains at most one `chore/refresh-external-versions` pull request when `src` has a version-only diff.

## Credentialed live code samples

```bash
make test-code-samples
make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
```

The Make target installs the Node environment in `src/code-samples` when its `package.json` exists, then runs the sample runner with the repository on `PYTHONPATH`. The runner accepts Python, TypeScript, Java, Kotlin, Go, and shell files under `src/code-samples`. `FILES` is a space-separated explicit subset; without it, the runner discovers all eligible files except paths in `__pycache__` and `node_modules`.

Every sample has a default 1,200-second timeout, configurable through `CODE_SAMPLE_TIMEOUT_SECONDS`. Python runs with `uv run python`; TypeScript with `npx tsx`; Go with `go run`; shell with `bash`; Java and Kotlin with JBang on Java 21. Python and JBang run from the repository root, while TypeScript, Go, and shell run from `src/code-samples` so their shared environments resolve.

```mermaid
flowchart TD
  Select["Select sample files"] --> Execute["Run language command"]
  Execute --> Outcome{"Process passed"}
  Outcome -->|"yes"| Tracing{"Tracing enabled"}
  Tracing -->|"no"| Passed["Passed"]
  Tracing -->|"yes"| Collect["Collect LangSmith trace"]
  Collect --> Collected{"Collection succeeded"}
  Collected -->|"yes"| Passed
  Collected -->|"no"| Failed["Runner fails"]
  Outcome -->|"429 rate limit"| Retry["Retry up to three attempts"]
  Retry --> Skipped["Skipped after retries"]
  Outcome -->|"other failure"| Failed
```

This flow is live execution, not a deterministic test. A rate-limit skip is not a successful example execution.

### Live-sample CI and failure semantics

The code-sample workflow skips fork pull requests because provider secrets are unavailable. Pull requests run changed eligible sample files from the merge-base diff; scheduled monthly and manually dispatched runs execute all samples. It uses 60 minutes for PR runs and 90 minutes for full runs, provisions a `pgvector/pgvector:pg17` service, installs Python/uv, Node 20, Java 21/JBang, and Go, and supplies provider credentials plus `POSTGRES_URI`.

For PostgreSQL-backed samples, the local helper honors `POSTGRES_URI` before attempting a pgvector testcontainer, Docker, and a default local connection. Preparation drops shared store and migration tables before setup to prevent stale partial schemas leaking between examples.

A LangSmith-style 429 is retried up to three total attempts with 15-second waits. A sample still rate-limited after those attempts is recorded as skipped and does not cause a nonzero exit; other sample failures do. A green run containing skips therefore says the runner did not observe a failure, not that every skipped sample worked.

Scheduled/manual full runs enable `CODE_SAMPLE_TRACING`. After a successful process, trace collection is attempted; a collection failure makes the runner fail even though the sample process passed. Only a single-snippet source file with a qualifying recent agent root run gets a public manifest entry; multi-snippet files are recorded as skipped. Snippet generation adds a `View example trace` card only for a manifest URL. A successful full run and regeneration can open or update `chore/refresh-code-sample-traces`; a separate workflow opens a Linear issue only when a scheduled sample run fails or is cancelled. See [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md).

## Hosted `llms.txt` coverage

Mintlify generates the root `llms.txt` and, once it is large enough, nested `/_llms/` indexes; neither artifact is produced or checked into this repository. The hosted check therefore crawls the deployed site rather than a local build. It starts at `<base-url>/llms.txt`, follows only same-site Markdown links beneath `/_llms/`, normalizes page links by removing `.md` and `/index`, and compares the resulting page set with same-site URLs from `<base-url>/sitemap.xml`. Any sitemap page not reachable through the served indexes makes the command exit nonzero.

The checker defaults to `https://docs.langchain.com` and supports `--base-url` for another deployment. Each request uses a repository-specific user agent and a 30-second timeout; connection-style failures are retried three times with increasing one-, two-, and three-second waits, while HTTP errors fail immediately. When coverage is incomplete, inspect whether a custom `llms.txt` was added to the build and report a Mintlify-generated index gap rather than editing a generated hosted file.

The `Check llms.txt coverage` workflow runs every Monday at 07:13 UTC and may also be dispatched manually. It has read-only contents permission, no persisted checkout credentials, and a 10-minute job timeout; it runs `python3 scripts/check_llms_urls.py` against the served default site.

## CI triage

Interpret a failure at the boundary that produced it:

- A socket error means an isolated test attempted an impermissible network operation.
- A `UV_FROZEN` or sync failure means dependency declarations and `uv.lock` need reconciliation.
- A Mint link, anchor, redirect, or OpenAPI failure concerns generated documentation and should be reproduced with the corresponding built-document command.
- An invalid `docs_url` is unsafe or missing metadata; use an allowed absolute HTTP(S) URL or a site-relative `/path`.
- A generated provider-overview diff means update its generator or `packages.yml`, not the generated page by hand.
- An unresolved registry/upstream lookup is not proof of availability or synchronization; retry or investigate the remote source.
- A live-sample failure can reflect credentials, provider behavior, PostgreSQL readiness, toolchain setup, or the sample itself. A rate-limit skip requires later execution.
- An llms coverage failure means the deployed sitemap and served index hierarchy disagree. It is a deployment/Mintlify boundary, not a local generated-file failure.

## Related documentation

- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md)
- [Builder tests](/openwiki/testing/builder-tests.md)
- [Code Sample Lifecycle](/openwiki/workflows/code-sample-lifecycle.md)
- [Local Development Workflow](/openwiki/workflows/local-development.md)
