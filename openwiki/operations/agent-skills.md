---
type: operations guide
title: Agent Skills and Authoring Guardrails
description: Use the canonical repository skill tree safely, select task-specific procedures, validate skill changes, and understand the boundaries on privileged integration automation.
tags: [agents, skills, documentation, automation, validation]
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
  - id: openwiki-source-5f54d12d1c36eab1c81a9b6d
    resource: repo://.github/copilot-instructions.md
  - id: openwiki-source-96745df062e0f1ffe2f232da
    resource: repo://.github/instructions/docs-style.instructions.md
  - id: openwiki-source-1db901655f02af312133801d
    resource: repo://.github/workflows/integration-submission.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-a2371d6362e5db4bc834ad03
    resource: repo://CLAUDE.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-24719fe59d1932fc5de31b61
    resource: repo://src/oss/deepagents/skills.mdx
  - id: openwiki-source-1695beda93a0ca504f038424
    resource: repo://tests/unit_tests/test_skills.py
generated: { by: "openwiki/0.4.3", at: "2026-10-20T08:20:37.912Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-10-20T08:20:37.912Z
---

# Agent Skills and Authoring Guardrails

The tracked `.agents/skills/` tree is the repository's canonical library of conditional procedures. `AGENTS.md` remains the always-on guide: it owns universal rules, while a skill owns a focused workflow that an agent discovers from its request-oriented `description` and loads only when it applies. In this checkout, `CLAUDE.md` is an OpenWiki-delimited pointer to `AGENTS.md`, not an independent instruction set.

## Canonical source and consumer synchronization

Each skill is a directory with a `SKILL.md` containing [Agent Skills](https://agentskills.io) YAML frontmatter and Markdown instructions. Cursor, Codex, GitHub Copilot, Gemini CLI, OpenCode, Deep Agents, Droid, Kilo Code, and other supported agents read `.agents/skills/` directly. Do not make an agent-specific copy the policy owner.

Claude Code is the exception: it reads the gitignored `.claude/skills/` directory. Reconcile its distribution after cloning, pulling an added or renamed skill, or creating a worktree:

```bash
make skills
```

The target creates `.claude/skills/`, creates or refreshes links for canonical skills, preserves a personal entry that is not a symlink, and removes a stale symlink. Linked content follows canonical edits immediately. The alternative local-source installation below copies files; rerun it after a canonical change because `npx skills update` does not refresh a local-source copy.

```bash
npx skills add ./.agents/skills --skill '*' --agent <agent> --yes
```

```mermaid
flowchart TD
  Canonical["Tracked .agents skills"] --> Direct["Direct-discovery agents"]
  Canonical --> Make["make skills"]
  Make --> Claude["Linked .claude skills"]
  Claude --> ClaudeCode["Claude Code"]
  Canonical --> CLI["skills CLI installation"]
  CLI --> Copy["Copied agent location"]
  Copy --> Refresh["Reinstall after source changes"]
```

This diagram shows the three distribution paths and the explicit refresh boundary for copied installations.

The root guide also has derived instruction surfaces. Its style guide is mirrored into path-scoped Cursor and GitHub instruction files; critical rules, repository structure, quick reference, frontmatter, and syntax are summarized in `.cursorrules` and `.github/copilot-instructions.md`. Update the corresponding copies in the same PR when changing a covered section.

Deep Agents Code gives project `.agents/skills/` precedence over project `.deepagents/skills/`. This lets CI resolve `submit-integration` from the canonical path without a shim.

## Select the skill that owns the task

Use the narrowest procedure instead of recreating its checks in an unrelated editing task. The [skills README](repo://.agents/skills/README.md) owns the complete catalog and full procedures; this table records repository-specific task routing and boundaries.

| Skill | Invoke when | Repository-specific boundary |
| --- | --- | --- |
| `add-docs-page` | Adding, moving, renaming, or deleting a page | Owns navigation, redirects, anchor/link validation, and the finished-prose review handoff. |
| `docs-edit` | Editing an existing page or named docs PR | Protects the actual PR head branch and confines related-page changes to corrections or pointers unless a restructure is requested. |
| `docs-restructure` | Consolidating, splitting, retiring, or de-duplicating a page family | Decides topic ownership before handing page lifecycle mechanics to `add-docs-page`. |
| `docs-team-voice` | Drafting or revising prose | Supplies the repository's editorial revision pass in addition to Vale and the root guide. |
| `docs-review` | Reviewing changed documentation | Reviews changed source Markdown or MDX rather than generated output and separates merge blockers from suggestions. |
| `docs-code-samples` | Turning visible code into a testable sample | Owns snippet extraction conventions and executable sample testing. |
| `verify-against-source` | Establishing behavioral, default, signature, or sample claims | Establishes evidence strength, product-repository ownership, and disclosure of gaps. |
| `docs-tooling-notion` | Adding or changing tracked tooling, including a skill | Required before PR handoff; records only the discovery-level tooling entry in Notion. |
| `submit-integration` | Automating a new structured integration-listing issue | CI-only, unattended processing of untrusted form data. |
| `update-integrations-prs` | Changing an existing integration contributor PR | Separate from new-submission automation. |

### Documentation ownership boundaries

For a named PR, `docs-edit` requires a clean checkout of the actual head branch, verifies `HEAD` against the PR's `headRefOid` and verifies an upstream, and uses `gh pr checkout <n>` for a cross-repository PR. It directs authors to use the live PR diff. Related docs signal what needs review, but implementation source decides factual claims; record unresolved gaps. Generated changelogs, OpenAPI specifications, generated catalog snippets, and `build/` are outputs: correct their generator or upstream source rather than hand-editing them.

When content placement is the problem, `docs-restructure` requires a reported page-family duplication map and one owner per topic. It replaces duplication with a pointer, resolves divergent facts against source, and delegates redirects and navigation to `add-docs-page`. That lifecycle skill requires redirects for moved, renamed, or deleted pages, checks anchors, runs prose/build/anchor-link checks, and invokes `docs-review` after completed prose.

`docs-review` resolves a PR, branch, working tree, or current branch before inspection. It combines Vale with checks in MDX areas Vale does not scan, such as JSX components and table cells, then reports each finding with its rule and merge-blocking status. `docs-team-voice` adds the repository's sentence-length thresholds, first-mention links, condition-before-behavior ordering, exact identifiers, verified examples, targeted revision pass, and `make lint_prose` gate.

### Samples and factual claims

`docs-code-samples` requires runnable external samples, visible snippet delimiters, and a harness that executes the snippet. Related Python snippets can share a file. TypeScript samples must split when shared module-scope imports or bindings would collide. Run the focused sample check before extraction:

```bash
make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"
```

`verify-against-source` orders evidence from executing the full or non-credentialed portion of a sample, through implementation source and installed-package imports, to reference signature lookup. Map each assertion to its owning repository and document both checked evidence and remaining gaps.

### Tooling record boundary

A changed script, workflow, Make target, PR check, scheduled job, agent, skill, or MCP server triggers `docs-tooling-notion` before pull-request handoff. The skill routes each topic to exactly one of five Docs Team Notion pages, requires the Notion MCP fetch and update tools, and leaves repository-owned material and complete skill procedures in the repository.

Fetch before every Notion edit and make narrow `update_content` replacements. Do not rewrite a page with uploaded images; after a timeout or asynchronous update, fetch and verify before retrying. For new tracked workflows, scripts, skills, agents, MCP servers, and git hooks, query the parent Detailed list database before adding its one discovery row. Update its `Source` value when tooling moves or is renamed.

## Privileged integration-submission automation

The `.github/workflows/integration-submission.yml` workflow is deliberately constrained: it can start only through `workflow_dispatch` or application of `integration-run`, and it checks that the actor has `admin`, `maintain`, or `write` permission. An unauthorized issue-label event removes the label, comments on the issue, and skips the job. The workflow also skips an issue already marked `integration-automation`.

After authorization, it retrieves issue metadata, parses the issue form to JSON, and passes the result to Deep Agents as untrusted metadata together with the pinned `submit-integration` skill. The skill must not follow instructions in issue URLs, descriptions, or notes; it makes best-effort listing decisions without asking questions, measures package downloads, and emits `integration-submission-error.md` only for a hard blocker. It leaves edits uncommitted and never pushes, opens a PR, or comments on GitHub itself.

```mermaid
flowchart TD
  Trigger["Manual dispatch or integration-run label"] --> Auth{"Actor has write or higher"}
  Auth -- "No" --> Reject["Remove label comment and skip"]
  Auth -- "Yes" --> Seen{"integration-automation label exists"}
  Seen -- "Yes" --> Skip["Skip duplicate processing"]
  Seen -- "No" --> Parse["Parse issue form to JSON"]
  Parse --> Parsed{"Form parsed"}
  Parsed -- "No" --> ParseError["Comment parse error"]
  Parsed -- "Yes" --> Mark["Mark automation in progress"]
  Mark --> Agent["Run pinned submit-integration skill"]
  Agent --> Result{"Hard blocker failure or no changes"}
  Result -- "Yes" --> Report["Comment result and stop"]
  Result -- "No" --> PR["Create integration issue pull request"]
  PR --> Link["Comment pull request link on issue"]
```

This diagram shows the workflow's authorization, de-duplication, parsing, agent, and PR-creation gates.

The workflow handles a blocker file, unsuccessful agent result, or empty diff by commenting the result and not opening a PR. When real changes exist, it removes a stray blocker file, creates `integration/issue-<number>` with the `integration` label, assigns `npentrel`, and adds review/test-plan context before linking the PR from the issue. Reviewers must still confirm the download/eligibility choice, docs URL and provider card, and listing files or hosted guide.

## Author or change a skill

Create `.agents/skills/<name>/SKILL.md` with a kebab-case directory and matching frontmatter `name`. Use a request-oriented description, supported frontmatter keys only, and one focused workflow. Keep universal policy in `AGENTS.md`; link to it rather than duplicating it in a skill.

Validate the canonical tree, because the validator does not follow Claude's symlinks:

```bash
claude plugin validate .agents/skills --strict
```

A canonical skill-tree change must update both catalogues: `.agents/skills/README.md` and the Skills table in `AGENTS.md`. It also requires the `docs-tooling-notion` follow-up and, when needed, `make skills` to reconcile Claude Code.

`tests/unit_tests/test_skills.py` is the structural contract: it checks canonical skill frontmatter, matching kebab-case names, recognized keys, description length, repository paths, Make targets, and exact agreement of the tree with both catalogues. Run it via the normal test target:

```bash
make test TEST_FILE=tests/unit_tests/test_skills.py
```

Repair a stale procedure, path, target, or inventory rather than weakening this protection.

## Runtime lifecycle in Deep Agents

Repository authoring skills and application runtime skills are separate concerns. With a checkpointer, Deep Agents loads supplied skill sources once per thread and stores the resulting metadata. An addition, edit, or deletion therefore needs a stored-metadata reset to become visible; without a checkpointer, the next run loads again. Use `None` in Python or `null` in JavaScript for that reset—an empty list means sources loaded successfully with no skills. A changed reload updates the system prompt and invalidates that thread's prompt cache; an identical reload does not. Python reloads on the next run, while JavaScript reloads before the next model call.

An application can instead pin named skills for a run. Before the next model call, `SkillsMiddleware` reads each selected `SKILL.md` and appends its body, without frontmatter, as one `HumanMessage` in the supplied order. This bypasses the agent's normal decision of whether the skill matches.

## See also

- [Adding and Modifying Documentation Pages](/openwiki/operations/adding-pages.md)
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md)
- [Integration Listing Automation](/openwiki/workflows/integration-listing-automation.md)
- [Release Watch](/openwiki/workflows/release-watch.md)
