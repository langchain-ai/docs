---
name: deepagents
description: Analyze Deep Agents Python library releases against LangChain Deep Agents docs and prepare one-feature documentation updates.
---

# Deep Agents docs release skill

Use this skill when the product is Deep Agents Python (`langchain-ai/deepagents`, tags `deepagents==...`). For TypeScript releases from `langchain-ai/deepagentsjs`, use the `deepagentsjs` skill. For Deep Agents Code, use `deepagents-code`. Do not use this skill for Managed Deep Agents.

## Sources of truth

- Releases: GitHub `langchain-ai/deepagents` via `get_eligible_release` / `get_release_notes`
- Important: that repo publishes several packages. For this product, only tags that start with `deepagents==` count (not `deepagents-code==`, `deepagents-acp==`, or `langchain-quickjs==`).
- Docs paths in `langchain-ai/docs`:
  - `src/oss/deepagents/` library pages
  - Exclude `src/oss/deepagents/code/` (Deep Agents Code is a separate product)
  - Navigation for Deep Agents in `src/docs.json`
  - Docs style authority: root `AGENTS.md` in `langchain-ai/docs` (read via `get_docs_file` before drafting)
- Changelog entry pages:
  - `src/oss/deepagents/changelog-py.mdx`
  - `src/oss/deepagents/changelog-js.mdx`

## What usually needs docs

Prioritize user-facing changes:

- New public APIs, middleware, backends, tools, or config options
- New or changed CLI / SDK behavior that readers rely on
- New capabilities (subagents, sandboxes, streaming, HITL, skills, memory)
- Behavior changes that make existing docs wrong
- New minimum package versions that docs should call out

Usually skip docs for:

- Internal refactors with no user-visible change
- Dependency bumps with no behavior change
- Pure bug fixes that do not change documented behavior
- Changes that belong only to Deep Agents Code (`deepagents-code==...` releases)

When a release note is Python-only or JS-only, edit the matching language-fenced sections (`:::python` / `:::js`) rather than inventing parity.

When unsure, open a small clarifying ticket/PR only if a reader of the current docs would be misled.

## Workflow for one Deep Agents release

The main agent must run **phase 1** through the `release-research` subagent first (diff + source investigation). This skill guides **phase 2** shipping and judgment details the subagent also uses.

1. After research returns features with `needs_docs: true`, read `/memories/agent/deepagents-releases.md` and skip any already recorded for that tag.
2. Call `get_docs_file` on `AGENTS.md` and read it in full. Then call `get_docs_file` for Deep Agents pages named in the research report. Stay out of `src/oss/deepagents/code/`.
3. For each remaining feature:
   - Edit surgically from the page `get_docs_file` content, following the docs repo `AGENTS.md`. Prefer `:::python` sections; leave `:::js` alone unless the change is shared.
   - Prefer updating the owning page over creating a new page. If a new page is required, also plan the `src/docs.json` navigation update.
   - Load the `ship-docs-update` skill and ship that feature alone with the research report's `evidence` as `evidence_json`.
4. After shipping, append the release tag, feature name, Linear URL, and PR URL to `/memories/agent/deepagents-releases.md`.
5. Keep `/memories/agent/AGENTS.md` short: last processed Deep Agents tag and date, alongside other products.

## Memory format

Use cold memory file `/memories/agent/deepagents-releases.md`:

```md
# Deep Agents release tracking

## deepagents==0.7.24
- feature: async subagent fork mode
  - linear: https://linear.app/...
  - pr: https://github.com/langchain-ai/docs/pull/...
```
