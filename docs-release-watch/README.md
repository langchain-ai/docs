# docs-release-watch

Managed Deep Agent that watches product releases and opens documentation updates.

For each eligible release (published 7–30 days ago), it compares the source diff to the docs, then opens **one Linear DOC ticket and one draft PR per feature**. The 30-day cap keeps first runs from backfilling older history.

Current product coverage:

| Product | Tag prefix | Docs | Schedule (Mon/Wed/Fri, PT) |
| --- | --- | --- | --- |
| OpenWiki | (any) | `src/oss/openwiki/` | 09:00 |
| Deep Agents (Python) | `deepagents==` | `src/oss/deepagents/` (excludes `code/`) | 09:30 |
| Deep Agents Code | `deepagents-code==` | `src/oss/deepagents/code/` | 10:00 |
| Deep Agents JS | `deepagents@` | `src/oss/deepagents/` (excludes `code/`, prefer `:::js`) | 10:30 |

To add another product: register it in `tools/products.py`, add `skills/<name>/SKILL.md`, and add a `schedules/` prompt.

## Layout

```text
docs-release-watch/
  agent.py
  instructions.md
  memory.py
  identity.py
  sandbox/
  schedules/
    daily_openwiki_check.py
    daily_deepagents_check.py
    daily_deepagents_code_check.py
    daily_deepagentsjs_check.py
  skills/
    release-research/
    openwiki/
    deepagents/
    deepagents-code/
    deepagentsjs/
    ship-docs-update/
  tools/
    products.py
    releases.py
    evidence.py
    source.py
    docs_edit.py
    linear_issues.py
    github_prs.py
    credentials.py
  tests/
```

## Prerequisites

- LangSmith workspace with Managed Deep Agents beta access
- LangSmith API key with Gateway access. Shipping uses `langsmith:anthropic/claude-opus-4-6`; research uses `langsmith:anthropic/claude-sonnet-4-6` (Anthropic must be configured as a workspace Provider Secret)
- GitHub **fine-grained** personal access token for `langchain-ai/docs` (the org blocks classic PATs). Needs Contents read/write and Pull requests read/write. Authorize SSO for `langchain-ai` if prompted.
- Linear API key with **Read** and **Write** (or Create issues) on team `DOC`. New issues are assigned to the API key owner. Override with `LINEAR_ASSIGNEE_ID` if needed.

## Local setup

```bash
cd docs-release-watch
uv sync
```

Fill `.env` (names only shown here):

```text
LANGSMITH_API_KEY=
GITHUB_TOKEN=
LINEAR_API_KEY=
MDA_DEV_DOCS_GITHUB=
MDA_DEV_DOCS_LINEAR=
```

`ANTHROPIC_API_KEY` is not required while the model uses LLM Gateway.

For `mda dev`, agent-owned connections resolve from `MDA_DEV_<SLUG>`:

- `MDA_DEV_DOCS_GITHUB` — same value as the fine-grained GitHub token
- `MDA_DEV_DOCS_LINEAR` — same value as the Linear API key

The tools also accept `GITHUB_TOKEN` / `LINEAR_API_KEY` as fallbacks.

Run locally:

```bash
uv run mda dev
```

In Studio, send:

```text
Run the OpenWiki docs release check.
```

Schedules do not fire under `mda dev`. Use the schedule prompt above to exercise the same path.

## Deploy

Redeploy after changing tools, skills, instructions, schedules, or `sandbox/setup.sh` (the sandbox snapshot rebakes from `setup.sh`):

```bash
uv run mda deploy
```

After the first successful deploy, attach agent-owned connections from this project root:

```bash
uv run mda connections create docs-github --secret-from-env GITHUB_TOKEN
uv run mda connections create docs-linear --secret-from-env LINEAR_API_KEY
```

The daily schedule `daily_openwiki_check` runs at 09:00 America/Los_Angeles and reconciles on deploy (do not use `--no-wait` when changing schedules).

## Extending to another product

1. Add a product entry in `tools/products.py`.
2. Add `skills/<product>/SKILL.md` with docs paths and judgment rules.
3. Add or extend a schedule prompt that names that product.
4. Redeploy.

## Anti-hallucination controls

Runs in two phases:

1. **Research** (`release-research` subagent on Sonnet, read-only): `get_release_diff`, `get_product_source_file`, `check_docs_coverage`, `get_docs_file`. Returns a JSON feature list. No Linear or PR tools.
2. **Ship** (main agent on Opus): only features from that report. Read docs `AGENTS.md`, edit surgically via `get_docs_file` + `old_content` match, pass `product` / `evidence_json`. Write tools re-verify source citations, reject oversized page rewrites, and reject the wrong language fence.

Release notes are secondary leads. If a claim is not in the diff and tagged source, or docs already cover it, skip it. Never claim a ticket or PR without a tool-returned URL.

## Safety

- `.env` is gitignored and never archived into the deployment bundle.
- Draft PRs only; humans review before merge.
- One feature per Linear issue and PR.
- Memory stores tracking URLs only, never credentials.
