---
name: deepagentsjs
description: Analyze Deep Agents TypeScript releases against LangChain Deep Agents docs and prepare one-feature documentation updates for JS-facing content.
---

# Deep Agents JS docs release skill

Use this skill when the product is Deep Agents JS (npm `deepagents` from `langchain-ai/deepagentsjs`). For the Python library, use the `deepagents` skill. For Deep Agents Code, use `deepagents-code`.

## Sources of truth

- Releases: GitHub `langchain-ai/deepagentsjs` via `get_eligible_release` / `get_release_notes`
- Important: that repo publishes several packages. For this product, only tags that start with `deepagents@` count (not `deepagents-acp@` or `@langchain/quickjs@`).
- Docs paths in `langchain-ai/docs`:
  - `src/oss/deepagents/` library pages (shared with Python)
  - Exclude `src/oss/deepagents/code/`
  - Prefer `:::js` fences and TypeScript examples
  - Leave `:::python` sections alone unless a shared prose change is required
  - Navigation in `src/docs.json`
  - Docs style authority: root `AGENTS.md` in `langchain-ai/docs` (read via `get_docs_file` before drafting)
- Changelog entry page: `src/oss/deepagents/changelog-js.mdx`

## What usually needs docs

Prioritize user-facing changes:

- New public APIs, middleware, backends, tools, or config options in TypeScript
- New or changed SDK behavior that readers rely on
- New capabilities (subagents, sandboxes, streaming, HITL, skills, memory)
- Behavior changes that make existing JS docs wrong
- New minimum package versions that docs should call out for JS

Usually skip docs for:

- Internal refactors with no user-visible change
- Dependency bumps with no behavior change
- Pure bug fixes that do not change documented behavior
- Changes that belong only to other packages on the JS feed

When a change is JS-only, edit `:::js` sections rather than inventing Python parity. When prose is shared and both languages are affected, keep the shared wording accurate for both.

When unsure, open a small clarifying ticket/PR only if a reader of the current docs would be misled.

## Workflow for one Deep Agents JS release

The main agent must run **phase 1** through the `release-research` subagent first (diff + source investigation). This skill guides **phase 2** shipping and judgment details the subagent also uses.

1. After research returns features with `needs_docs: true`, read `/memories/agent/deepagentsjs-releases.md` and skip any already recorded for that tag.
2. Call `get_docs_file` on `AGENTS.md` and read it in full. Then call `get_docs_file` for Deep Agents pages named in the research report. Stay out of `src/oss/deepagents/code/`.
3. For each remaining feature:
   - Edit surgically from the page `get_docs_file` content, following the docs repo `AGENTS.md`. Prefer `:::js` sections; leave `:::python` alone unless the change is shared.
   - Prefer updating the owning page over creating a new page. If a new page is required, also plan the `src/docs.json` navigation update.
   - Load the `ship-docs-update` skill and ship that feature alone with the research report's `evidence` as `evidence_json`.
4. After shipping, append the release tag, feature name, Linear URL, and PR URL to `/memories/agent/deepagentsjs-releases.md`.
5. Keep `/memories/agent/AGENTS.md` short: last processed Deep Agents JS tag and date, alongside other products.

## Memory format

Use cold memory file `/memories/agent/deepagentsjs-releases.md`:

```md
# Deep Agents JS release tracking

## deepagents@1.14.2
- feature: browser entrypoint
  - linear: https://linear.app/...
  - pr: https://github.com/langchain-ai/docs/pull/...
```
