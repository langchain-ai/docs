---
name: openwiki
description: Analyze OpenWiki releases against LangChain OpenWiki docs and prepare one-feature documentation updates.
---

# OpenWiki docs release skill

Use this skill when the product is OpenWiki.

## Sources of truth

- Releases: `https://github.com/langchain-ai/openwiki/releases` via `get_eligible_release` / `get_release_notes`
- Docs paths in `langchain-ai/docs`:
  - `src/oss/openwiki/` (all OpenWiki pages)
  - Navigation entries for OpenWiki in `src/docs.json`
  - Shared guidance in root `AGENTS.md`
- Changelog page in docs: `src/oss/openwiki/changelog.mdx` (points at GitHub releases)

## What usually needs docs

Prioritize user-facing changes:

- New CLI commands, flags, or subcommands
- New coding-agent integrations or providers
- New modes, workflows, or config surfaces
- Behavior changes that make existing docs wrong
- New requirements (Node version, auth, permissions)

Usually skip docs for:

- Internal refactors with no user-visible change
- Dependency bumps with no behavior change
- Pure bug fixes that do not change documented behavior

When unsure, open a small clarifying ticket/PR only if a reader of the current docs would be misled.

## Workflow for one OpenWiki release

1. Call `get_eligible_release` with `product="openwiki"` and `min_age_days=7`.
2. Read `/memories/agent/openwiki-releases.md` (create it if missing). Skip features already recorded for that tag.
3. Load the release notes. Split the notes into discrete features (one user-facing capability each).
4. In the sandbox, clone or refresh `https://github.com/langchain-ai/docs.git` and read the OpenWiki pages that might be affected.
5. For each feature that needs a docs change:
   - Draft the MDX edits (follow `AGENTS.md`: frontmatter, no markdown in `description`, Tabler icons only, sentence-case headings, no contractions, no first person).
   - If a new page is required, also plan the `src/docs.json` navigation update.
   - Load the `ship-docs-update` skill and ship that feature alone.
6. After shipping, append the release tag, feature name, Linear URL, and PR URL to `/memories/agent/openwiki-releases.md`.
7. Keep `/memories/agent/AGENTS.md` short: last processed OpenWiki tag and date only.

## Memory format

Use cold memory file `/memories/agent/openwiki-releases.md`:

```md
# OpenWiki release tracking

## v0.7.0
- feature: GitHub Copilot CLI integration
  - linear: https://linear.app/...
  - pr: https://github.com/langchain-ai/docs/pull/...
- feature: entra auth configuration
  - linear: https://linear.app/...
  - pr: https://github.com/langchain-ai/docs/pull/...
```
