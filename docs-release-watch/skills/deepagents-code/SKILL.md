---
name: deepagents-code
description: Analyze Deep Agents Code releases against LangChain Deep Agents Code docs and prepare one-feature documentation updates.
---

# Deep Agents Code docs release skill

Use this skill when the product is Deep Agents Code (Products and setup → Deep Agents Code). Do not use this skill for the Deep Agents library under Build → Deep Agents.

## Sources of truth

- Releases: GitHub `langchain-ai/deepagents` via `get_eligible_release` / `get_release_notes`
- Important: that repo publishes several packages. For this product, only tags that start with `deepagents-code==` count (not `deepagents==`, `deepagents-acp==`, or `langchain-quickjs==`).
- Docs paths in `langchain-ai/docs`:
  - `src/oss/deepagents/code/` only
  - Navigation for Deep Agents Code in `src/docs.json`
  - Docs style authority: root `AGENTS.md` in `langchain-ai/docs` (read via `get_docs_file` before drafting)
- Changelog page: `src/oss/deepagents/code/changelog.mdx` (points at the upstream code changelog)

Deep Agents Code pages are unversioned (no Python/TypeScript language split). Conditional fences still resolve against the Python branch.

## What usually needs docs

Prioritize user-facing changes:

- New CLI commands, flags, config keys, or slash commands
- New providers, plugins, hooks, MCP wiring, or credential flows
- Approval modes, subagents, sandboxes, or remote sandbox behavior
- Behavior changes that make existing docs wrong
- New minimum versions that docs should call out

Usually skip docs for:

- Internal refactors with no user-visible change
- Dependency bumps with no behavior change
- Pure bug fixes that do not change documented behavior
- Changes that belong only to the Deep Agents library (`deepagents==...` releases)

When unsure, open a small clarifying ticket/PR only if a reader of the current docs would be misled.

## Workflow for one Deep Agents Code release

The main agent must run **phase 1** through the `release-research` subagent first (diff + source investigation). This skill guides **phase 2** shipping and judgment details the subagent also uses.

1. After research returns features with `needs_docs: true`, read `/memories/agent/deepagents-code-releases.md` and skip any already recorded for that tag.
2. Call `get_docs_file` on `AGENTS.md` and read it in full. Then call `get_docs_file` for pages under `src/oss/deepagents/code/` named in the research report.
3. For each remaining feature:
   - Edit surgically from the page `get_docs_file` content, following the docs repo `AGENTS.md`.
   - Prefer updating the owning page over creating a new page. If a new page is required, also plan the `src/docs.json` navigation update under Deep Agents Code.
   - Load the `ship-docs-update` skill and ship that feature alone with the research report's `evidence` as `evidence_json`.
4. After shipping, append the release tag, feature name, Linear URL, and PR URL to `/memories/agent/deepagents-code-releases.md`.
5. Keep `/memories/agent/AGENTS.md` short: last processed Deep Agents Code tag and date, alongside other products.

## Memory format

Use cold memory file `/memories/agent/deepagents-code-releases.md`:

```md
# Deep Agents Code release tracking

## deepagents-code==0.1.84
- feature: remote sandboxes config
  - linear: https://linear.app/...
  - pr: https://github.com/langchain-ai/docs/pull/...
```
