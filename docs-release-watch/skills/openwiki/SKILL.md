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
  - Docs style authority: root `AGENTS.md` in `langchain-ai/docs` (read via `get_docs_file` before drafting)
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

The main agent must run **phase 1** through the `release-research` subagent first (diff + source investigation). This skill guides **phase 2** shipping and judgment details the subagent also uses.

1. After research returns features with `needs_docs: true`, read `/memories/agent/openwiki-releases.md` and skip any already recorded for that tag.
2. Call `get_docs_file` on `AGENTS.md` and read it in full. Then call `get_docs_file` for OpenWiki pages named in the research report.
3. For each remaining feature:
   - Edit surgically from the page `get_docs_file` content, following the docs repo `AGENTS.md`.
   - If a new page is required, also plan the `src/docs.json` navigation update.
   - Load the `ship-docs-update` skill and ship that feature alone with the research report's `evidence` as `evidence_json`.
4. After shipping, append the release tag, feature name, Linear URL, and PR URL to `/memories/agent/openwiki-releases.md`.
5. Keep `/memories/agent/AGENTS.md` short: last processed OpenWiki tag and date only.

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
