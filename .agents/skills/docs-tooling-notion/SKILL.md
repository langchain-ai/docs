---
name: docs-tooling-notion
description: Document new or changed docs-team tooling on the Notion tooling pages. Decides which of the five pages owns the topic, what belongs in the repo instead of Notion, and how to edit safely through the Notion MCP server. Use when a script, workflow, agent, skill, or MCP server is added or changed and the internal tooling docs need updating.
license: MIT
metadata:
  author: langchain
  version: "1.0"
---

# Document tooling in Notion

The docs team's internal tooling documentation is five Notion pages under Docs
Team. This skill routes a change to the one page that owns it, then edits that
page without tripping the known Notion failure modes.

Requires the Notion MCP server (`notion-fetch`, `notion-update-page`).

## Rule one: one home per topic

Every topic lives on exactly one page. Duplicates drift, and drift is worse than
a long page. Before writing anything, search the other four pages for the topic.
If it already appears somewhere, update it there instead of adding a second
copy.

## Step 1. Route the topic

| Page | ID | Owns |
|------|----|------|
| [Docs tooling and agents](https://app.notion.com/p/3ca808527b178153839bff0f2831914c) | `3ca808527b178153839bff0f2831914c` | Parent directory. Page table, "Owned elsewhere" list, quick-answers FAQ. |
| [Docs tech stack](https://app.notion.com/p/30c808527b178073876af57f7d87d8ca) | `30c808527b178073876af57f7d87d8ca` | The production site only: fencing, `src` versus `build`, build pipeline, navigation, integration docs. |
| [Local setup and quality gates](https://app.notion.com/p/3c8808527b1781dcbaf5d04834a843bf) | `3c8808527b1781dcbaf5d04834a843bf` | mise and prek setup, the `docs` and `mint` CLIs, Vale, git hooks, broken-link triage, the CI matrix, preview deployments, publishing. |
| [Docs automation and agents](https://app.notion.com/p/3c8808527b17815b81cbf92896b5c3ee) | `3c8808527b17815b81cbf92896b5c3ee` | Scheduled workflows and their cron times, the changelog agents, the #ask-docs intake agent, tracked skills, agent-instruction files, MCP servers. |
| [Reference docs](https://app.notion.com/p/3c9808527b1781858ebbe92914b02970) | `3c9808527b1781858ebbe92914b02970` | The three LangSmith OpenAPI sources, reference.langchain.com, the `@[ClassName]` link map. |

Most new tooling lands on **Docs automation and agents** (a workflow, script,
agent, skill, or MCP server) or **Local setup and quality gates** (anything a
contributor runs on their own machine or that gates a PR).

The changelog **system** is not owned by these pages. [LangSmith release
notes](https://app.notion.com/p/31b808527b178026943ac2b1ae244021) owns fragments,
the fragment schema, and both pipelines. Link to it; do not re-explain it. These
pages keep only the runbook: deployment IDs, HTTP routes, required environment
variables, and recovery paths.

## Step 2. Check whether it belongs in Notion at all

Do not write a Notion page for something the repo already documents where people
find it. Deliberately excluded: `IDE_SETUP.md`, `.github/brand-guidelines.md`,
`.github/pull_request_template.md`, `.github/CONTRIBUTING.md`, the issue
templates, and the navigation map, which lives only in `AGENTS.md` and
`CLAUDE.md` because the Notion copy went stale once already.

Skills are the same: a skill is its own authoritative reference. Name it on the
Notion page, say what it covers and the one or two facts a reader needs in order
to decide whether to open it, and stop there.

Untracked tooling is not team infrastructure. Anything under a gitignored path
is personal tooling and does not go on these pages.

## Step 3. Write it

Follow the `docs-team-voice` skill. Do not restate its rules here. The three that
get missed most often on Notion pages: no first person, no spaced em dashes, and
definition lists written as `- **Term**: Explanation.` with the colon outside the
bold and a period at the end.

Open a section with a one-sentence statement of what the thing is, then what it
enables, then the procedure. Close a substantial page with `## See also`.

## Step 4. Edit safely

Fetch the page with `notion-fetch` before every edit. Then use
`notion-update-page` with `command: "update_content"` and narrow
`content_updates` pairs rather than rewriting the page.

Five failure modes, each of which has already cost a debugging cycle:

- **`old_str` must match the stored indentation exactly.** Tables are stored
  with no leading tabs; callouts do use tabs. A mismatch fails with an
  indentation hint.
- **Never use `replace_content` on a page holding an uploaded image.** The
  fetched image URL is a short-lived signed S3 link, and rewriting the page body
  can break the image.
- **A timed-out or async update may already have applied.** Updates default to
  `allow_async: true`. Fetch the page and verify before retrying anything that
  appeared to fail, otherwise the retry duplicates the block.
- **Bold that contains inline code mid-sentence renders as stray asterisks.**
  Bold wrapping code entirely is fine. Reword so the two do not collide.
- **In-page anchor links do not resolve.** Notion addresses blocks by ID, not by
  heading slug. Reference sections by name in prose.

## Step 5. Close the loop

Update the parent page's page table when a page's scope changes, and repoint any
`## See also` entry that is now wrong. Report which page was edited and what was
deliberately left out, so the routing decision is reviewable.
