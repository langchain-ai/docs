---
type: continuous-integration-workflows
title: GitHub Actions and CI/CD
description: Continuous integration and deployment workflows for PR checks, documentation builds, testing, and scheduled tasks with secrets management.
tags: [ci-cd, github-actions, automation, testing, deployment, quality-assurance]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-5c124605ed6e394bffee862c
    resource: repo://.github/workflows/_check-links.yml
  - id: openwiki-source-f35e7c44cc1805709393a581
    resource: repo://.github/workflows/_lint.yml
  - id: openwiki-source-4d9cccca7700db7220ec055e
    resource: repo://.github/workflows/_test.yml
  - id: openwiki-source-ef6344124ed2f526c8578c0b
    resource: repo://.github/workflows/check-pr-imports.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-9db08afb765c73035414b518
    resource: repo://.github/workflows/lint-prose.yml
  - id: openwiki-source-f2608d0d515da097485b6ec5
    resource: repo://.github/workflows/publish.yml
  - id: openwiki-source-5153f86e64d6ee0b305f72b3
    resource: repo://.github/workflows/refresh-langsmith-openapi.yml
  - id: openwiki-source-97746d8f3662d803e625550e
    resource: repo://.github/workflows/test-code-samples.yml
  - id: openwiki-source-5ee763b2f4cade1e8b64a3c3
    resource: repo://.markdownlint.json
  - id: openwiki-source-4d1645cb6317345817452838
    resource: repo://.pre-commit-config.yaml
  - id: openwiki-source-635a4d4537a9628cdea912c0
    resource: repo://.vale.ini
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-697851c98229599f97376bfb
    resource: repo://scripts/process_langsmith_openapi.py
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

## Overview

This repository uses GitHub Actions to automate continuous integration, testing, documentation builds, deployments, and scheduled maintenance tasks. All workflows are defined in `.github/workflows/` and follow a consistent pattern: PR checks must pass before merge, and successful merges to `main` trigger documentation deployment to the Mintlify platform.

## Core CI Pipeline

The main CI workflow (`ci.yml`) runs on pull requests and pushes to `main`, with concurrency control to cancel outdated runs in favor of newer ones.

### PR Checks

All of the following checks must pass before a PR can merge:

**Linting and Code Quality**
- **Ruff** (Python): Lints and formats Python code across the repository, configured to check all rules with selective per-file exceptions defined in `pyproject.toml`. Runs via the `_lint.yml` reusable workflow.
- **Codespell**: Validates spelling across source files, excluding code samples and generated content.
- **Vale**: Prose linting that enforces style, grammar, and terminology rules from `.vale.ini`, which applies LangChain-specific and industry-standard styles. The `lint-prose.yml` workflow runs on changed markdown files in PRs.

**Testing**
- **pytest**: Core test suite runs with socket communication disabled (except Unix sockets) via `pytest --disable-socket`. Tests are located in `tests/` and configured in `pyproject.toml`. The `_test.yml` reusable workflow handles execution.

**Documentation and Link Integrity**
- **Link validation**: The `_check-links.yml` reusable workflow builds documentation using `make build`, then validates all internal and external links using Mintlify's link checker. Anchor validation ensures links to specific sections are valid.
- **OpenAPI spec validation**: Mintlify checks the validity of the LangSmith OpenAPI specification.
- **Merge conflict detection**: Scans for unresolved merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
- **Cross-reference validation**: Custom checks ensure docs.json entries exist for all referenced pages.
- **External docs URLs**: Validates URL schemes in integration_external_docs.yaml.
- **Generated file integrity**: Verifies that regenerated files (e.g., partner package tables) match checked-in versions, with bypass capability via `bypass-auto-check` label.

**Import Validation**
- **Import mappings** (`check-pr-imports.yml`): Ensures Python imports use correct packages, preventing obsolete `langchain_core` direct imports. Generates mappings if missing and validates against base branch.

**Code Sample Testing**
- **Code samples** (`test-code-samples.yml`): Tests executable code samples in `src/code-samples/` by running them against live dependencies. Tests run on schedule (weekly), manual trigger, and on PR changes to code samples. Secrets (API keys) are only available on non-fork PRs to prevent credential leaks.

## Documentation Build and Deployment

### Build Process

Documentation is built by running `make build`, which:
1. Calls `pipeline build` (the pipeline CLI)
2. Generates the `/build` directory from `/src` source files
3. Includes extraction of code snippets and generation of supplementary content

### Deployment Pipeline

The `publish.yml` workflow automatically deploys built documentation on successful merges to `main`:

1. **Build**: Creates the `/build` directory with all generated documentation
2. **Verify**: Confirms the build directory exists and is non-empty
3. **Prepare**: Copies `/build` into a `/public/build` directory structure
4. **Publish**: Uses `peaceiris/actions-gh-pages@v4` to push to the `prod` branch with `GITHUB_TOKEN`, which Mintlify monitors for deployment

The deployment uses the default `GITHUB_TOKEN` (no external secrets required for the push itself).

## Scheduled Tasks

### LangSmith OpenAPI Spec Refresh

The `refresh-langsmith-openapi.yml` workflow runs daily at 10:00 AM UTC and can be triggered manually:

1. **Fetch**: Calls `scripts/process_langsmith_openapi.py --write` to fetch the latest OpenAPI spec from `api.smith.langchain.com`
2. **Post-process**: The script filters fleet and internal endpoints (adds `x-hidden: true`) and injects human-readable group tags for Mintlify auto-generated pages
3. **Manage PR**: Creates or updates a standing refresh PR (`chore/refresh-langsmith-openapi`) by:
   - Reusing an existing PR if one is open, appending a new commit
   - Creating a fresh PR from `main` if none exists
   - Skipping commit and PR operations if the spec has not changed

This automation ensures API documentation stays synchronized with the live platform without manual intervention.

## Lint Configuration

### Markdown Linting (`.markdownlint.json`)

Default rules enabled with selective exceptions:
- Disables rules for: MD001 (heading hierarchy), MD013 (line length), MD025 (multiple top-level headings), MD033 (inline HTML), MD041 (first line heading), MD051 (link fragments)

### Prose Linting (`.vale.ini`)

Applies style validation to all markdown and MDX files:
- **Styles**: LangChain, proselint, vale, write-good
- **Skip scopes**: Frontmatter (YAML) is excluded from validation
- **Block ignores**: Code blocks are excluded to avoid linting code comments
- **Min alert level**: Errors only (warnings ignored)

The configuration enforces clear, inclusive, professional writing with strong attention to terminology consistency.

### Python Linting (via `pyproject.toml`)

**Ruff** configuration:
- Line length: 88 characters
- Select all rules with exceptions for complexity checks (C901, PLR0912, PLR0915) and comma handling (COM812)
- Per-file exclusions for scripts, generated content, and test fixtures
- Test files allow assertions, private member access, and magic values

**Codespell** configuration:
- Uses ignore list from `src/.codespellignore`
- Skips code samples, generated files, SVG, and JSON files

**Pytest** configuration:
- Async mode: auto
- Async default scope: function
- Reports all test outcomes with verbose output
- Displays slowest 5 tests for performance analysis

## Local Development and Pre-commit Hooks

### Pre-commit Framework

The `.pre-commit-config.yaml` defines local hooks via `prek` (installed through `mise`):

**Hooks**:
- `check-removed-pages-redirects`: Verifies that removed docs.json pages have redirect entries
- `vale`: Runs prose linting on changed markdown files, mirroring the CI check
- `broken-links-with-anchors`: Manual-stage hook for full link validation before pushing

Install local hooks:
```bash
mise install
prek install --hook-type pre-commit --hook-type pre-push
```

Run the expensive broken-links check manually:
```bash
prek run --hook-stage manual broken-links-with-anchors --all-files
```

## Build and Make Targets

Key `Makefile` targets used by CI workflows:

- `make build`: Builds documentation via `pipeline build`
- `make lint`: Runs ruff, type checking, and codespell
- `make test`: Runs pytest with socket disabled
- `make lint_prose`: Runs Vale with optional `FILES` parameter
- `make broken-links`: Checks for broken links (excludes OpenAPI-generated pages and snippet files)
- `make broken-links-with-anchors`: Checks links including anchor validation
- `make check-openapi`: Validates OpenAPI spec syntax with Mintlify

## Secrets Management

### GitHub Secrets

- **GITHUB_TOKEN**: Automatically provided by GitHub Actions; used for PR operations, pushing to branches, and creating releases. Not stored as an explicit secret.
- **API keys** (external services): Not required for core CI/CD pipelines. Code sample tests receive provider keys only when running on non-fork PRs.

### Security Best Practices

- **Never commit credentials**: All secrets are managed via GitHub's encrypted secret store
- **Fork PR isolation**: Secrets are not exposed to PRs from forks to prevent credential leakage through workflow logs
- **Public branches**: The `prod` branch (deployment target) is public and may not contain sensitive data

## Failure Scenarios and Debugging

### Common Failure Causes

**Broken links**: Lint check identifies missing or malformed links, anchor references, and external URL validity. Re-run `make broken-links-with-anchors` locally to reproduce.

**Missing cross-references**: The `check-cross-refs` job ensures all pages referenced in narrative text exist in docs.json.

**Formatting violations**: Ruff, Vale, or markdownlint report style issues with inline annotations on the PR. Run `make lint` and `make lint_prose` locally to fix.

**Missing docs.json entries**: Generated content or renamed files must have corresponding docs.json entries for navigation.

**Test failures**: Pytest reports failures with stack traces. Run `make test` locally with `pytest --disable-socket` to debug. The socket disable flag prevents accidental external network calls.

**Import issues**: The `check-pr-imports` workflow identifies incorrect package imports. Review scripts/import_mappings.json and run scripts/check_pr_imports.py to validate.

### Debugging Workflow Runs

- View logs in the GitHub Actions UI for any failed job
- Inspect the "Annotations" tab for inline lint feedback
- For link issues, examine `filter_mint_broken_links.py` output to distinguish real vs. ignored broken links
- Code sample failures log the full execution output including error messages from external services

## Related Workflows and Tools

- **Code sample testing**: `test-code-samples.yml` executes documentation examples against live environments
- **PR enhancement workflows**: Additional workflows provide PR comments, labeling, and import validation
- **OpenWiki integration**: The system supports integration with external documentation frameworks through carefully managed build outputs and metadata
- **Mintlify platform**: Deployment target that consumes `/build` artifacts and serves the final documentation site

## Integration Points

### Incoming

- GitHub pushes to `main` and pull requests trigger CI pipelines
- Scheduled cron jobs for daily OpenAPI refresh and weekly code sample tests
- Manual workflow dispatch for on-demand builds and deployments

### Outgoing

- Documentation built to `/build` is published to the `prod` branch
- OpenAPI refresh PRs created to the main repository
- PR comments, labels, and annotations provide feedback to developers
- Mintlify platform deployment consumes the published branch

## Configuration and Operations

**Environment variables** in workflows:
- `UV_FROZEN`: Locks uv to a specific dependency resolution (prevents unexpected updates in CI)
- `RUFF_OUTPUT_FORMAT`: Set to `github` for inline PR annotations
- `PYTHONPATH`: Set to repository root when running pipeline commands

**Concurrency**: The CI workflow uses GitHub's concurrency feature to cancel outdated runs, reducing CI queue time and resource usage.

**Timeouts**: Workflows have conservative timeout limits (typically 5–20 minutes per job) to fail fast on hangs or infinite loops.

**Python versioning**: Tests and linting run on Python 3.13 (minimum and maximum supported versions defined in pyproject.toml).
