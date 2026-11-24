---
type: operations guide
title: Agent Skills and Authoring Rules
description: Explains the always-on agent contract, canonical and mirrored instruction files, task-specific skills, Claude skill links, and the validation and tooling-documentation follow-up required for safe repository changes.
tags: [agents, skills, documentation, review, automation]
verified:
  - by: openwiki/0.4.3
    at: 2026-11-23T08:07:24.438Z
sources:
  - id: openwiki-source-18732c72f962c06354cb62db
    resource: repo://.agents/skills/add-docs-page/SKILL.md
  - id: openwiki-source-ddbddbe474c8dc57119458d7
    resource: repo://.agents/skills/docs-code-samples/SKILL.md
  - id: openwiki-source-b48b39ee604e5154ddb6fbad
    resource: repo://.agents/skills/docs-edit/SKILL.md
  - id: openwiki-source-a9c698a5d38546d584591637
    resource: repo://.agents/skills/docs-restructure/SKILL.md
  - id: openwiki-source-b372ee6d00ad6d446e0fc042
    resource: repo://.agents/skills/docs-review/SKILL.md
  - id: openwiki-source-a5534bfe9d1400e6ecbd306e
    resource: repo://.agents/skills/docs-team-voice/SKILL.md
  - id: openwiki-source-1694d3d0c97b7809ac846496
    resource: repo://.agents/skills/docs-tooling-notion/SKILL.md
  - id: openwiki-source-9361c44d74c0e18006d0d76f
    resource: repo://.agents/skills/README.md
  - id: openwiki-source-d0231ed4f359c0492aa150de
    resource: repo://.agents/skills/verify-against-source/SKILL.md
  - id: openwiki-source-f96dad653d7389511b4b22a3
    resource: repo://.cursor/rules/docs-style.mdc
  - id: openwiki-source-b4ad59e3499ed93df00886ad
    resource: repo://.cursorrules
  - id: openwiki-source-5f54d12d1c36eab1c81a9b6d
    resource: repo://.github/copilot-instructions.md
  - id: openwiki-source-96745df062e0f1ffe2f232da
    resource: repo://.github/instructions/docs-style.instructions.md
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-1695beda93a0ca504f038424
    resource: repo://tests/unit_tests/test_skills.py
generated: { by: "openwiki/0.4.3", at: "2026-11-23T08:07:24.438Z" }
---

# Agent Skills and Authoring Rules

Repository guidance has two layers. [`AGENTS.md`](https://github.com/langchain-ai/docs/blob/main/AGENTS.md) is the always-on contract. `.agents/skills/` contains conditional procedures that an agent loads when a task matches a skill description. Read the contract first, then invoke the narrowest applicable skill.

## Follow the instruction hierarchy

`AGENTS.md` owns rules that apply to every documentation task: do not fabricate facts or examples, keep frontmatter descriptions free of Markdown, do not edit `build/`, update navigation for new pages, use approved components and icons, and test code examples. It also owns repository structure, navigation, frontmatter, syntax, and style guidance.

`CLAUDE.md` only points agents to `AGENTS.md` for OpenWiki instructions. The Cursor and Copilot files mirror selected `AGENTS.md` sections for agents that do not read the root contract. The critical-rules, repository-structure, quick-reference, frontmatter, and syntax sections are summarized in `.cursorrules` and `.github/copilot-instructions.md`. The style guide is mirrored in the path-scoped Cursor and Copilot documentation-rule files. Change the authoritative section and its required mirrors together.

A skill owns a conditional workflow, not another copy of the global contract. Skills link to `AGENTS.md` rather than duplicating its rules. This boundary prevents a focused procedure from silently becoming a second, divergent policy.

## Discover and install skills

The tracked `.agents/skills/` tree is the canonical skill source for agents that discover it directly. Each skill lives at `.agents/skills/<name>/SKILL.md`. Its frontmatter `description` is the discovery interface; the body is the procedure loaded after a match.

Claude Code reads the gitignored `.claude/skills/` directory instead. Run this after cloning, pulling a skill addition or rename, or creating a worktree:

```bash
make skills
```

`make skills` creates symlinks from `.claude/skills/` to the canonical tree, keeps existing non-symlink personal entries, and removes broken links. The links reflect canonical edits immediately. The `skills` CLI copies a local source, so rerun its installation command after source changes:

```bash
npx skills add ./.agents/skills --skill '*' --agent <agent> --yes
```

```mermaid
flowchart TD
  Canonical["Tracked .agents/skills tree"] --> Direct["Agents with direct discovery"]
  Canonical --> MakeSkills["make skills"]
  MakeSkills --> ClaudeLinks["Symlinked .claude/skills tree"]
  ClaudeLinks --> Claude["Claude Code"]
  Canonical --> SkillsCli["skills CLI"]
  SkillsCli --> Copy["Copied installation"]
  Copy --> Refresh["Rerun after source changes"]
```

This flow separates the canonical source, live Claude links, and copied installations.

The canonical tree currently contains eleven skills: `add-docs-page`, `docs-code-samples`, `docs-edit`, `docs-restructure`, `docs-review`, `docs-team-voice`, `docs-tooling-notion`, `submit-integration`, `update-example-models`, `update-integrations-prs`, and `verify-against-source`. The README catalog, `AGENTS.md` Skills table, and structural tests must agree with that tree.

## Choose the owning procedure

Use one procedure for each kind of work:

| Task | Owning skill | Boundary |
| --- | --- | --- |
| Add, move, rename, or retire a page | `add-docs-page` | Selects the source family, navigation, redirects, source verification, and final review handoff. |
| Edit an existing documentation PR or page | `docs-edit` | Uses the PR's own head branch, checks cross-repository PRs with `gh pr checkout`, and repairs generated output through its generator or input. |
| Choose one owner across duplicated pages | `docs-restructure` | Maps the page family, assigns one topic owner, and replaces duplicate material with a pointer. Lifecycle mechanics remain with `add-docs-page`. |
| Draft or revise voice | `docs-team-voice` | Covers sentence shape, conditions, identifiers, links, and the revision pass. |
| Review changed prose | `docs-review` | Reviews the changed documentation diff, runs Vale, applies manual style checks, and reports the rule for each finding. |
| Verify behavior or a sample | `verify-against-source` | Ranks runnable samples, executable non-model code, owning source, installed packages, and reference signatures as evidence. |
| Extract runnable samples | `docs-code-samples` | Keeps reader-facing regions separate from harness-only removal regions and requires the visible body to execute before extraction. |
| Record changed tooling | `docs-tooling-notion` | Assigns one Notion home and updates the discovery row after a fetch-and-narrow update. |

`add-docs-page` makes page lifecycle explicit: new pages need navigation, moved or deleted pages need redirects, factual claims need product-source verification, and completed prose goes through `docs-review` before commit.

## Document tooling changes before handoff

Adding or changing a script under `scripts/`, a GitHub Actions workflow, Make target, PR check, scheduled job, agent, skill, or MCP server requires the `docs-tooling-notion` follow-up before pull-request handoff, whether or not anyone asks for it. This is a repository constraint, not an optional documentation improvement.

The procedure assigns each topic to one Notion home. Most workflows, scripts, agents, skills, and MCP servers belong on **Docs automation and agents**; local contributor commands and PR gates belong on **Local setup and quality gates**. It first checks whether the repository already documents the topic, fetches the chosen page before every edit, applies narrow `update_content` changes, and adds or updates the parent's Detailed list row with the source path. Skills remain authoritative in the repository; Notion records what exists and how to find it rather than copying the skill body.

## Review prose and product truth separately

`docs-review` is deliberately diff-scoped. It reads the whole changed page and relevant sibling pages, reviews changed lines and existing content made wrong by the change, runs Vale, applies manual checks, and reports each finding with its applicable rule. `docs-team-voice` handles sentence rhythm and wording; `verify-against-source` handles factual truth. Do not use a style review to settle a product default.

The repository currently tracks no `.agents/skills/docs-review/ci-mode.md` and no CI workflow that invokes `docs-review` or `verify-against-source`. The supported procedure resolves a PR, branch, or current working-tree diff, and it uses `git fetch origin` plus checkout for named branch or PR reviews. It does not describe a CI-only `HEAD_SHA`/`BASE_SHA`/`OUT` contract. Do not treat the former CI-mode guidance as current repository behavior.

```mermaid
sequenceDiagram
  participant Author as Author or reviewer
  participant Diff as Target diff
  participant Vale as Vale and manual checks
  participant Source as Product source
  participant Handoff as Review handoff
  Author->>Diff: Resolve PR, branch, or working tree
  Diff->>Vale: Inspect changed prose in context
  Diff->>Source: Verify behavior and samples separately
  Vale-->>Handoff: Report findings with rules
  Source-->>Handoff: Report evidence and gaps
```

This sequence shows that prose quality and product truth are separate review paths that meet at handoff.

## Validate skills and samples

Create a skill at `.agents/skills/<kebab-case-name>/SKILL.md`. The directory and frontmatter `name` must match, the name must be kebab-case, and the description must be nonempty and no longer than 1024 characters. Referenced repository paths and Make targets must exist.

Run the validator against the canonical tree, not Claude's symlink view:

```bash
claude plugin validate .agents/skills --strict
make test TEST_FILE=tests/unit_tests/test_skills.py
```

The structural tests enforce frontmatter and path validity, then require exact catalog agreement between the canonical tree, `.agents/skills/README.md`, and the `AGENTS.md` Skills table.

Runnable samples belong under `src/code-samples/<product>/`. Keep related Python snippets in one file when possible. Split TypeScript or JavaScript files when imports or module-scope bindings would collide, because the entire file executes during `make test-code-samples`.

Keep reader-facing code between language-specific `:snippet-start:` and `:snippet-end:` markers. Put test-only harness code in `:remove-start:` and `:remove-end:` regions. The visible snippet body must execute before any exit or blocking-call guard. Test the source file before extraction:

```bash
make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
make code-snippets
```

`make code-snippets` runs the extraction and MDX-generation pipeline after the source sample passes.

`verify-against-source` ranks evidence in this order: run the sample, run the non-model portion, read the owning library source, check the installed package, then consult reference signatures. Record the file or symbol checked and identify what remains unverified, such as a model-dependent path or runtime-generated UI label. A sibling documentation page is not product evidence.

## See also

- [Adding and Moving Documentation Pages](/openwiki/operations/adding-pages.md)
- [GitHub Actions Integration](/openwiki/integrations/github-actions.md)
- [Release Watch](/openwiki/workflows/release-watch.md)
- [OpenWiki quickstart](/openwiki/quickstart.md)
