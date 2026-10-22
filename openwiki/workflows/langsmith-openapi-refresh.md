---
type: generated API publication workflow
title: LangSmith OpenAPI Refresh
description: Documents the scheduled, reviewed refresh that turns the LangSmith service OpenAPI document into the committed input for Mintlify's LangSmith REST API reference. Covers transformation policy, constrained remote ingestion, standing-PR lifecycle, validation limits, and ownership boundaries.
tags: [langsmith, openapi, automation, github-actions, mintlify, security]
sources:
  - id: openwiki-source-5153f86e64d6ee0b305f72b3
    resource: repo://.github/workflows/refresh-langsmith-openapi.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-49f717adb7cc59501f5c17ac
    resource: repo://scripts/filter_mint_broken_links.py
  - id: openwiki-source-697851c98229599f97376bfb
    resource: repo://scripts/process_langsmith_openapi.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-38d325b9c51f3c8dfd528917
    resource: repo://tests/unit_tests/test_filter_mint_broken_links.py
generated: { by: "openwiki/0.4.3", at: "2026-10-21T08:20:13.723Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-10-21T08:20:13.723Z
---

# LangSmith OpenAPI Refresh

The LangSmith REST API reference is published from the generated, committed `src/langsmith/langsmith-platform-openapi.json`. It is **not** an authored MDX endpoint tree: `src/docs.json` supplies that file to Mintlify's `langsmith/smith-api` directory, and Mintlify generates endpoint routes at deployment. Do not edit the generated specification or deployment-generated endpoint pages by hand.

This is distinct from the SDK API reference at [reference.langchain.com](https://reference.langchain.com/python/), which is generated and deployed outside this repository. The related Agent Server API uses a different committed OpenAPI input and route directory; it is not maintained by this refresh workflow.

## Ownership and trust boundary

| Concern | Owner | Safe maintenance action |
| --- | --- | --- |
| Upstream API description | `https://api.smith.langchain.com/openapi.json` | Fix service-owned content upstream when appropriate. |
| Public-reference policy | `scripts/process_langsmith_openapi.py` | Adjust the explicit hide, grouping, title, or ordering rules and regenerate. |
| Generated deployment input | `src/langsmith/langsmith-platform-openapi.json` | Review and merge the refresh PR; never manually patch the JSON. |
| Refresh and GitHub write authority | `.github/workflows/refresh-langsmith-openapi.yml` | Preserve its narrow path staging, no-diff exit, and standing-PR behavior. |
| Endpoint-page rendering | Mintlify deployment configured by `src/docs.json` | Inspect a deployed preview or production site; generated endpoint pages are not MDX sources. |

`src/docs.json` separately declares the Agent Server input, `src/langsmith/agent-server-openapi.json`, under `langsmith/agent-server-api`. Agent Server updates arrive in specification-update PRs from `langgraph-api`, rather than through the platform processor or its schedule. Route an Agent Server specification issue to that externally maintained update path.

The processor accepts network input only from `api.smith.langchain.com`. It defaults to `https://api.smith.langchain.com/openapi.json`; an unallowlisted parsed hostname raises an error before a request. A local `--input` file is the controlled alternative for reproduction and policy work.

```mermaid
flowchart TD
    Trigger["Daily schedule or manual dispatch"] --> Fetch["Fetch allowlisted LangSmith spec"]
    Local["Controlled local JSON input"] --> Process["Process public documentation policy"]
    Fetch --> Process
    Process --> Artifact["Generated committed platform spec"]
    Artifact --> Diff{"Specification differs"}
    Diff -->|"no"| Stop["Exit without commit"]
    Diff -->|"yes"| Standing["Create or update standing review PR"]
    Standing --> Mint["Mintlify deployment"]
    Mint --> Routes["Generated REST endpoint routes"]
```

This flow shows the constrained upstream input, curated JSON, review gate, and deployment-generated endpoint routes.

The GitHub Actions job is a trusted writer, not a pull-request workflow. It runs on `ubuntu-latest` with a 15-minute timeout and only `contents: write` and `pull-requests: write` permissions, checks out shallow history, provisions Python 3.13 through the repository uv action, and runs the processor with `--write`. Its write phase stages only `src/langsmith/langsmith-platform-openapi.json`; the review PR is the approval boundary for a changing remote specification.

## Public-documentation shaping

`process_spec()` mutates a loaded upstream OpenAPI object. The CLI serializes the result as UTF-8 JSON with two-space indentation and a trailing newline. It skips path-level OpenAPI metadata while iterating operations. The transformation deliberately curates what Mintlify exposes:

- **Hide non-public operations.** It sets `x-hidden: true` on operations carrying configured Fleet, product-feedback, internal/infrastructure, administration/debug, or metrics tags, and on configured health and internal path rules. It also hides matching top-level tag entries.
- **Normalize operation titles.** Every operation gets a summary, falling back to `METHOD path`, sentence-cased while preserving configured acronyms and proper nouns. Backend `[Beta]` and trailing `V2` wording become consistent trailing `(Beta)` and `(v2)` markers. Visible non-sandbox `/v2/` operations receive `(v2)`; configured run operations use canonical title overrides. Existing markers are removed before markers are reapplied, making title processing idempotent.
- **Build navigation metadata.** The processor creates a top-level `tags` list if absent, updates known tags with human-readable `x-group` values, adds tag objects for tags found only on operations, and sorts them by the configured group order. Unknown groups sort alphabetically after ordered groups.

The policy lives in the processor constants: `HIDDEN_TAGS`, `HIDDEN_PATHS`, `HIDDEN_PATH_PREFIXES`, `TAG_GROUPS`, `GROUP_ORDER`, and the v2/title tables. Add or remove a public category there rather than editing a generated operation or tag in the JSON artifact.

## Entrypoints and local operation

Run from the repository root. A default invocation obtains the current remote source; a local input avoids the network fetch. Without `--write`, the processor prints the complete transformed JSON to standard output. `--output` overrides the default generated-artifact path.

```bash
uv run python scripts/process_langsmith_openapi.py --write
```

```bash
uv run python scripts/process_langsmith_openapi.py --input /path/to/openapi.json
```

```bash
uv run python scripts/process_langsmith_openapi.py --input /path/to/openapi.json --write
```

Treat a local write as regeneration of a derived artifact, not permission to curate its JSON manually. For an unexpected exposure, omission, label, or sidebar group, change the authoritative upstream specification or processor policy, rerun it, and review the complete diff. Never edit `build/`; the documentation pipeline regenerates it.

## Daily refresh and review-PR lifecycle

The workflow runs daily at 10:00 UTC and supports `workflow_dispatch`. It writes the freshly processed artifact in the initial checkout, copies it to the runner's temporary directory, and restores the checked-out artifact. It then queries GitHub for an open PR whose head is `chore/refresh-langsmith-openapi`:

1. If one exists, it fetches that branch shallowly and resets the local branch to it. Otherwise, it creates the branch from the checkout.
2. It restores the newly generated artifact from temporary storage onto that branch and compares only that path.
3. With no diff, it exits without a commit or PR change.
4. With a diff, it commits the generated file. An existing PR receives an appended commit and normal push. Without an open PR, the workflow force-pushes the standing branch—safe because no open PR references it—and creates a PR against `main`.

This maintains at most one outstanding refresh PR instead of creating a daily queue. Reviewers should treat its generated diff as a proposed public API reference change: check newly visible or hidden operations, title/version labels, and tag groups. The PR is the human review boundary between trusted remote ingestion and the committed Mintlify input.

## Validation limits and failures

A disallowed fetch hostname raises `ValueError`; a network, TLS, timeout, or JSON-decoding failure prevents a candidate from being produced. The workflow shell uses `set -euo pipefail`, so checkout, push, or PR failures stop the step. A no-diff result is a successful no-op, not a failed refresh.

There is no repository command that proves Mintlify rendered every LangSmith REST endpoint page. `make check-openapi` currently validates only the Agent Server specification, not the committed LangSmith REST input. The normal link checks pass Mint output through `scripts/filter_mint_broken_links.py`, which explicitly removes reports containing `/langsmith/smith-api` because that route family is generated at deployment rather than present in the local build. Inspect a Mintlify preview or deployed site for the rendered REST endpoint surface; use the processor command to verify transformation and the refresh PR to verify the candidate change.

### Focused test boundary

The focused unit coverage in this area is the link-report filter test, which preserves the exemption for generated OpenAPI-route reports while retaining ordinary broken-link failures. Run it with:

```bash
make test TEST_FILE=tests/unit_tests/test_filter_mint_broken_links.py
```

It does not exercise remote fetches, the processor transformation policy, GitHub branch/PR operations, or deployment-generated API routes. Use a controlled local processor run and generated-diff review for transformation changes; use the scheduled/manual workflow and a Mintlify preview or deployed site for those integration boundaries.

## Safe change checklist

1. Do not hand-edit `src/langsmith/langsmith-platform-openapi.json`, deployment-generated endpoint routes, or `build/`.
2. Keep remote fetches restricted to `api.smith.langchain.com`; use `--input` for a controlled local candidate.
3. Modify hiding, grouping, title, or ordering rules in `scripts/process_langsmith_openapi.py`, then regenerate and review the complete diff.
4. Preserve the workflow's single generated path, no-diff exit, and one-standing-PR lifecycle when changing automation.
5. Route Agent Server input changes to its own externally maintained update process and SDK-reference issues to the external reference site.
6. Review a refresh PR as a public API documentation change, then inspect a Mintlify preview or production site for endpoint rendering.

## Related pages

- [GitHub Actions and CI Automation](/openwiki/integrations/github-actions.md)
- [Mintlify Integration](/openwiki/integrations/mintlify.md)
- [Reference Documentation Boundaries](/openwiki/integrations/reference-docs.md)
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md)
- [Testing Overview](/openwiki/testing/test-overview.md)
