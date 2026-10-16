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
  - Shared guidance in root `AGENTS.md`
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

1. Call `get_eligible_release` with `product="deepagents"` and `min_age_days=7`.
2. Read `/memories/agent/deepagents-releases.md` (create it if missing). Skip features already recorded for that tag.
3. Load the release notes. Split the notes into discrete features (one user-facing capability each).
4. In the sandbox, clone or refresh `https://github.com/langchain-ai/docs.git` and read the Deep Agents pages that might be affected. Stay out of `src/oss/deepagents/code/` unless the feature clearly belongs there and you are explicitly covering Deep Agents Code.
5. For each feature that needs a docs change:
   - Draft the MDX edits (follow `AGENTS.md`: frontmatter, no markdown in `description`, Tabler icons only, sentence-case headings, no contractions, no first person).
   - Prefer updating the owning page over creating a new page. If a new page is required, also plan the `src/docs.json` navigation update.
   - Load the `ship-docs-update` skill and ship that feature alone.
6. After shipping, append the release tag, feature name, Linear URL, and PR URL to `/memories/agent/deepagents-releases.md`.
7. Keep `/memories/agent/AGENTS.md` short: last processed Deep Agents tag and date, alongside other products.

## Memory format

Use cold memory file `/memories/agent/deepagents-releases.md`:

```md
# Deep Agents release tracking

## deepagents==0.7.24
- feature: async subagent fork mode
  - linear: https://linear.app/...
  - pr: https://github.com/langchain-ai/docs/pull/...
```
