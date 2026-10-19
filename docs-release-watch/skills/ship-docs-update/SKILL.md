---
name: ship-docs-update
description: Open one Linear DOC ticket and one draft docs PR for a single documentation feature, grounded in product-source evidence.
---

# Ship one docs update

Use this skill in **phase 2** when you are ready to create tracking and a draft PR for exactly one feature from a `release-research` report.

## One feature only

- One Linear issue
- One draft pull request
- One focused branch
- No unrelated edits in the same PR

If the research report lists multiple features, call this workflow once per feature. Do not invent features that research did not list. If you notice unrelated changes that should be made, leave them for a later research pass instead of shipping them now.

## Preconditions (required)

Before calling any write tool:

1. This run already has a `release-research` JSON report, and this feature appears there with `needs_docs: true`.
2. You called `get_docs_file` on `AGENTS.md` in `langchain-ai/docs` and read it in full. That file is the style and structure authority for the PR. Do not confuse it with `/memories/agent/AGENTS.md` (hot memory status only).
3. You called `get_docs_file` for every docs path you will change and still have that exact content.
4. You prepared `evidence_json` from the research report's `evidence` object (the write tools re-fetch each path at the tag and refuse if the citation is missing):

```json
{
  "source_repo": "langchain-ai/deepagentsjs",
  "source_tag": "deepagents@1.14.2",
  "items": [
    {
      "path": "libs/deepagents/src/middleware/foo.ts",
      "symbol": "offloadBinaryContent"
    }
  ]
}
```

Each item needs `path` plus `symbol` or `quote`. Empty evidence is rejected.

## Steps

1. Edit surgically from the `get_docs_file` content, following the docs repo `AGENTS.md` (frontmatter, voice, no markdown in `description`, Tabler icons, sentence-case headings, no contractions, no first person, language fences, navigation rules, and the rest of that file). Change only the sections needed for this feature. Do not rewrite the rest of the page. Do not invent content for the other language fence.
2. Create the Linear issue with `create_linear_issue`:
   - `team_key="DOC"`
   - Title: concise, feature-scoped (for example "Document OpenWiki Copilot CLI integration")
   - Description: release tag, why docs must change, files to touch, acceptance criteria
   - Pass `product`, `release_tag`, and `evidence_json`
   - The tool assigns the issue to the Linear API key owner (Naomi) automatically
3. Create the draft PR with `create_draft_docs_pr`:
   - Branch: `docs/<product>-<version>-<feature-slug>`
   - Title matches the issue scope
   - Body links the Linear issue URL and names the triggering release
   - Pass the same `evidence_json`
   - Pass `product` so language-fence validation uses the registry scope (`python` / `js` / `shared`)
   - `files_json` is a JSON array of `{ "path": "...", "old_content": "...", "new_content": "..." }`
   - `old_content` must be the exact string returned by `get_docs_file` (empty string only for a brand-new file)
   - Keep the edit surgical: the tool rejects diffs that rewrite too much of an existing page or change the other language fence
4. Record the Linear URL and PR URL in product memory before starting the next feature. Only treat the ship as successful when both tools returned a `url`.

## PR body template

```md
## Summary
- <one sentence on the docs change>
- Triggered by <product> <release tag>

## Linear
<issue url>

## Source evidence
- Repo: `<owner>/<repo>`
- Tag: `<release tag>`
- `<path>`: `<symbol or short quote>`

## Test plan
- [ ] Preview the changed pages
- [ ] Confirm claims against the cited product source at the tag
- [ ] Run `make lint_prose FILES="<changed mdx paths>"` when possible
```

The write tools append a Source evidence section when the body omits one. Prefer writing it yourself so the citations stay next to the summary.

## Do not

- Bundle multiple features into one issue or PR
- Ship before calling the `release-research` subagent in this run
- Ship a feature that is not in the research report
- Draft docs without reading the docs repo `AGENTS.md` in this run
- Draft from release notes without reading product source at the tag
- Pass full page contents invented from memory (always start from `get_docs_file`)
- Omit `old_content` or invent a base that does not match `main`
- Ship without `evidence_json` that points at product source at the tag
- Modify `docs-release-watch/` in the docs PR
- Put secrets, tokens, or `.env` contents into issues or PRs
- Mark the PR ready for review; leave it as a draft
- Edit `:::python` sections for a JS-only feature, or `:::js` for a Python-only feature
- Claim success without a tool-returned Linear URL and PR URL
