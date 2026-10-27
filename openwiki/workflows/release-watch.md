---
type: automated documentation workflow
title: Documentation Release Watch
description: Managed Deep Agent workflow that researches eligible product releases and prepares evidence-backed, one-feature documentation handoffs. It documents the tool-enforced source and exact-base checks, the remaining validation boundary, and post-PR Linear lifecycle synchronization.
tags: [documentation, releases, managed-deep-agents, automation, linear, github]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-22T08:20:38.024Z
sources:
  - id: openwiki-source-192dd6007b37a6bb76dc7586
    resource: repo://.github/workflows/sync-linear-issue-from-pr.yml
  - id: openwiki-source-15059b0f9cd678e06d6faff0
    resource: repo://docs-release-watch/agent.py
  - id: openwiki-source-1a32e32add6db9b89b6d15bc
    resource: repo://docs-release-watch/identity.py
  - id: openwiki-source-d282f31d82e34c26a1df41a1
    resource: repo://docs-release-watch/instructions.md
  - id: openwiki-source-ac1d4c62086c683f572e37b8
    resource: repo://docs-release-watch/memory.py
  - id: openwiki-source-12c8fb32a02de9dce773720f
    resource: repo://docs-release-watch/README.md
  - id: openwiki-source-7343358ab26816c0490e183e
    resource: repo://docs-release-watch/schedules/daily_deepagents_check.py
  - id: openwiki-source-80699156d95c578d363ff7bc
    resource: repo://docs-release-watch/schedules/daily_deepagents_code_check.py
  - id: openwiki-source-08108374c068c41a2942873f
    resource: repo://docs-release-watch/schedules/daily_deepagentsjs_check.py
  - id: openwiki-source-644335efc60c7f4dd134c6a8
    resource: repo://docs-release-watch/schedules/daily_openwiki_check.py
  - id: openwiki-source-e6eae428bbd7391551a06823
    resource: repo://docs-release-watch/skills/deepagents-code/SKILL.md
  - id: openwiki-source-76a91b0964e7aa4532a1ed44
    resource: repo://docs-release-watch/skills/deepagents/SKILL.md
  - id: openwiki-source-456a8fa820b05327b670caaf
    resource: repo://docs-release-watch/skills/deepagentsjs/SKILL.md
  - id: openwiki-source-8a71339160c9deb013c657f4
    resource: repo://docs-release-watch/skills/openwiki/SKILL.md
  - id: openwiki-source-6d70aabf6818feb460142a35
    resource: repo://docs-release-watch/skills/release-research/SKILL.md
  - id: openwiki-source-995bd0bfbf33ddbc4b1edfb0
    resource: repo://docs-release-watch/skills/ship-docs-update/SKILL.md
  - id: openwiki-source-ded8a20999ec9d794fa86ab9
    resource: repo://docs-release-watch/tests/test_evidence.py
  - id: openwiki-source-a8cf0b3622fff481f5e15c41
    resource: repo://docs-release-watch/tools/credentials.py
  - id: openwiki-source-e156e784c871fd69445c469b
    resource: repo://docs-release-watch/tools/docs_edit.py
  - id: openwiki-source-c7d8544c9a3ccf7d999db067
    resource: repo://docs-release-watch/tools/evidence.py
  - id: openwiki-source-98da08303623382d6a9ad5e8
    resource: repo://docs-release-watch/tools/github_prs.py
  - id: openwiki-source-e2669050caa928b17793a350
    resource: repo://docs-release-watch/tools/linear_issues.py
  - id: openwiki-source-2b522af6f26794f2e71ccb4e
    resource: repo://docs-release-watch/tools/products.py
  - id: openwiki-source-0a04d5d3ade1211f24c16b3b
    resource: repo://docs-release-watch/tools/releases.py
  - id: openwiki-source-ee7ce52fc98a340b33669667
    resource: repo://docs-release-watch/tools/source.py
  - id: openwiki-source-eab62bc712c4650a5ee3e7d3
    resource: repo://scripts/sync_linear_issue_from_pr.py
generated: { by: "openwiki/0.4.3", at: "2026-10-22T08:20:38.024Z" }
---

# Documentation Release Watch

`docs-release-watch` is a Managed Deep Agent that turns verified documentation gaps in selected product releases into reviewable handoffs. It covers OpenWiki, Deep Agents Python, Deep Agents Code, and Deep Agents JS. The agent does not merge or publish documentation: its delivery is a Linear issue and a **draft** PR for human review.

The workflow separates read-only release research from the shipping agent's Linear and GitHub write tools. That separation, however, is not a complete transactional workflow: creating the issue precedes creating the PR, so a later failure can leave an issue without a PR; operators must reconcile using returned URLs and release-tracking memory.

## Coverage and eligibility

The product registry owns the release-watch boundary. For each product it supplies its upstream repository, documentation paths and exclusions, product skill, release-tag prefix, source-diff prefixes, language scope, and product-specific memory file.

| Product key | Upstream repository and tag filter | Documentation boundary | Language scope |
| --- | --- | --- | --- |
| `openwiki` | `langchain-ai/openwiki`; any tag | `src/oss/openwiki/` | Shared |
| `deepagents` | `langchain-ai/deepagents`; `deepagents==` | `src/oss/deepagents/`, excluding `code/` | Python |
| `deepagents-code` | `langchain-ai/deepagents`; `deepagents-code==` | `src/oss/deepagents/code/` | Shared |
| `deepagentsjs` | `langchain-ai/deepagentsjs`; `deepagents@` | `src/oss/deepagents/`, excluding `code/` | JavaScript |

The tag and source-prefix filters matter because the Deep Agents release feeds serve multiple packages. Runs must use the requested product key and its matching skill, rather than infer scope from a repository name or release notes. Product skills identify user-facing candidates such as public APIs, commands, configuration, integrations, or behavior that makes existing documentation inaccurate; they normally skip internal refactors, dependency-only work, and behavior-neutral changes.

`get_eligible_release` fetches up to 100 releases, discards drafts and prereleases, applies the product's tag prefix, and chooses the newest release published **7 to 30 days** before the current UTC time. It also returns the preceding eligible release when one exists. The bounded window prevents a first run from backfilling old history; no candidate means no handoff.

## Research before shipping

`agent.py` gives the main shipping agent read and write tools, but gives `release-research` only the read-tool set. The main-agent instructions require that subagent before either write tool. The report must compare the eligible tag to a previous same-prefix tag where available, filter the changed files to the product source prefixes, confirm candidates in source at the head tag, and inspect concrete current documentation paths before setting `needs_docs: true`. Release notes are leads, not proof.

```mermaid
flowchart TD
  Start["Schedule or manual product request"] --> Memory["Read tracking memory"]
  Memory --> Research["Read-only release-research subagent"]
  Research --> Select["Select release in 7 to 30 day window"]
  Select --> Diff["Compare tags and confirm tagged source"]
  Diff --> Coverage["Check concrete current docs"]
  Coverage --> Gate{"Feature needs docs and is untracked"}
  Gate -->|"no"| Idle["Report outcome and stop"]
  Gate -->|"yes"| Base["Read docs AGENTS.md and exact base files"]
  Base --> Issue["Create one evidence-backed Linear issue"]
  Issue --> Draft["Create one evidence-backed draft PR"]
  Draft --> Record["Record returned URLs in product memory"]
  Draft --> Event["GitHub pull request lifecycle event"]
  Event --> SyncGate{"Same repo, secret, and Closes DOC-N link"}
  SyncGate -->|"yes"| Linear["GitHub Actions synchronizes Linear status"]
  SyncGate -->|"no"| Skip["No Linear lifecycle update"]
```

*Research establishes the handoff; after PR creation, GitHub Actions is the separate boundary that may synchronize the linked Linear issue's lifecycle.*

If research finds no qualifying feature, the instructions require a brief result and no ticket or PR. The shipping skill similarly requires reading the docs repository `AGENTS.md` and every target file in the same run. A new page additionally needs the applicable `src/docs.json` navigation update.

## Write-path safeguards and remaining boundary

### Enforced before remote issue or PR creation

Both `create_linear_issue` and `create_draft_docs_pr` require non-empty `evidence_json`: an upstream owner/repository, release tag, and at least one source path with a symbol or quote. Each write path fetches every cited tagged file and rejects an absent path or a symbol/quote not found there. It appends a **Source evidence** section when the supplied body lacks one.

The draft-PR tool also parses every requested edit and normalizes line endings. For each path, it re-fetches the requested base branch (default `main`): an existing file's `old_content` must equal the current base content exactly, while a new file must have empty `old_content`. It rejects missing bases, no-op edits, and paths under `docs-release-watch/`. Only after evidence and every exact-base comparison pass does it create the Git blobs, tree, commit, branch, and a PR against `langchain-ai/docs` with `draft: true`.

These are the safeguards actually wired into `create_draft_docs_pr`. Evidence verification and exact-base comparison occur before its Git write sequence, but the issue and PR remain separate remote operations and there is no rollback if the PR step fails.

### Guidance and helpers that are not PR-tool enforcement

`tools/docs_edit.py` has useful helpers: existing-file edits above 35% line churn fail, and a Python- or JS-scoped change cannot alter the other language fence. They are tested in isolation, but `create_draft_docs_pr` neither imports nor invokes them. Its signature also has no `product` or language-scope input. Therefore a caller can create a draft PR that exceeds the churn limit or alters an out-of-scope language fence; treat the skill's surgical-edit and language-fence directions as workflow guidance, not a tool-enforced gate.

<!-- openwiki: broken internal link [<issue url>] file "<issue url>" does not exist. Fix the href or restore the target, then delete this comment. -->
Likewise, the shipping skill requires one feature, one focused branch, one Linear issue, and one draft PR, with a separate invocation for each feature in a multi-feature release. This is the handoff invariant to preserve, but neither write tool validates that the PR has exactly one feature or exactly one linked issue. The PR tool documents the required `Closes [DOC-N](<issue url>)` convention but does not parse or require it. A missing or malformed link can therefore create a draft PR successfully while preventing the later lifecycle sync.

## Linear handoff and post-PR lifecycle sync

For a feature, the skill orders the operations as Linear issue then draft PR. Issue creation resolves the requested team and assigns the authenticated Linear viewer by default; `LINEAR_ASSIGNEE_ID` is accepted only when it resolves to an active user. The issue description gets product and optional release metadata. The shipping workflow considers the handoff successful only if both tools returned a URL.

<!-- openwiki: broken internal link [<issue url>] file "<issue url>" does not exist. Fix the href or restore the target, then delete this comment. -->
The generated PR body is expected to contain `## Linear` with `Closes [DOC-N](<issue url>)`. This is an integration contract for `.github/workflows/sync-linear-issue-from-pr.yml`, not a call made by the Managed Deep Agent. The GitHub Action runs for PR opened, reopened, converted-to-draft, ready-for-review, and closed events. It has read-only GitHub permissions, a five-minute timeout, and an explicit same-repository gate, so fork PRs do not enter the job or receive `LINEAR_API_KEY`.

When the secret is present, the workflow supplies the PR title, body, state, draft flag, and merged flag to `scripts/sync_linear_issue_from_pr.py`. The script performs no update for an unlinked PR, resolves each recognized `DOC-N` issue and its team's workflow states, then chooses a preferred state name with a type fallback:

| PR condition | Preferred Linear state | Type fallback |
| --- | --- | --- |
| Open draft | In Progress | `started` |
| Open and ready for review | In Review | `started` |
| Merged | Done | `completed` |
| Closed without merge | Canceled | `canceled` |

The sync accepts the canonical linked form and plain `Closes DOC-N`; a bare Linear URL does not activate it. Missing `LINEAR_API_KEY`, an unlinked PR, an already-correct state, and a dry run are reported as skips. A missing suitable team state makes the script exit unsuccessfully; Linear HTTP, GraphQL, lookup, and update failures raise errors. The action can synchronize any same-repository PR following this convention, not only release-watch PRs.

## State, credentials, and operations

Durable memory is a deployment-shared, read/write tree at `/memories/agent/`. Its hot `AGENTS.md` loads on every run, while product tracking files are read on demand; content persists in LangSmith Context Hub across deployments. Store only procedural tracking—product, tag, feature, Linear URL, PR URL, and dates. Because all callers can influence later runs through this memory, treat it as untrusted input and keep tool authority and approvals outside it. Never store personal data, credentials, tokens, or secrets.

Callers authenticate with a LangSmith API key. GitHub and Linear tools first resolve agent-owned connections and then local environment fallbacks. Public GitHub release reads can continue anonymously when credentials are unavailable or rejected; documentation reads and GitHub writes require the GitHub credential.

The deployed schedules run Monday, Wednesday, and Friday in `America/Los_Angeles`:

| Product | Local time |
| --- | --- |
| OpenWiki | 09:00 |
| Deep Agents Python | 09:30 |
| Deep Agents Code | 10:00 |
| Deep Agents JS | 10:30 |

For local work, run `uv sync` and `uv run mda dev`. Schedules do not fire in development, so send the schedule prompt through Studio. Deploy or reconcile schedule changes with `uv run mda deploy`. To add coverage, add a registry entry, matching product skill, and schedule prompt, then redeploy.

## Tests and safe changes

`docs-release-watch/tests/test_evidence.py` provides focused tests for evidence shape and rendering, exact-base and no-op rejection, source-prefix filtering, line-churn calculation, and rejected wrong-fence edits. It does not call the end-to-end remote PR creation operation. In particular, it does not demonstrate that the isolated churn and fence helpers are invoked by the PR tool—source inspection shows they are not.

When changing this workflow, preserve the 7–30-day eligibility window, tagged-source evidence, exact-base edit check, draft-only handoff, and one-feature-one-issue-one-PR operating invariant. If making churn, language scope, or PR-to-issue linkage a hard guarantee, wire validation into `create_draft_docs_pr` and add an end-to-end test rather than relying on skills or prompts. For related boundaries, see [Repository Source Map](/openwiki/architecture/source-map.md), [GitHub Actions and CI Automation](/openwiki/integrations/github-actions.md), [agent skills](/openwiki/operations/agent-skills.md), [quickstart](/openwiki/quickstart.md), and [test overview](/openwiki/testing/test-overview.md).
