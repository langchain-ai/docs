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
  - Shared guidance in root `AGENTS.md`
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

1. Call `get_eligible_release` with `product="deepagentsjs"` and `min_age_days=7`.
2. Read `/memories/agent/deepagentsjs-releases.md` (create it if missing). Skip features already recorded for that tag.
3. Load the release notes. Split the notes into discrete features (one user-facing capability each).
4. In the sandbox, clone or refresh `https://github.com/langchain-ai/docs.git` and read the Deep Agents pages that might be affected. Stay out of `src/oss/deepagents/code/`.
5. For each feature that needs a docs change:
   - Draft the MDX edits (follow `AGENTS.md`: frontmatter, no markdown in `description`, Tabler icons only, sentence-case headings, no contractions, no first person).
   - Prefer updating the owning page over creating a new page. If a new page is required, also plan the `src/docs.json` navigation update.
   - Load the `ship-docs-update` skill and ship that feature alone.
6. After shipping, append the release tag, feature name, Linear URL, and PR URL to `/memories/agent/deepagentsjs-releases.md`.
7. Keep `/memories/agent/AGENTS.md` short: last processed Deep Agents JS tag and date, alongside other products.

## Memory format

Use cold memory file `/memories/agent/deepagentsjs-releases.md`:

```md
# Deep Agents JS release tracking

## deepagents@1.14.2
- feature: browser entrypoint
  - linear: https://linear.app/...
  - pr: https://github.com/langchain-ai/docs/pull/...
```
