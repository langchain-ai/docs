---
name: ship-docs-update
description: Open one Linear DOC ticket and one draft docs PR for a single documentation feature.
---

# Ship one docs update

Use this skill when you are ready to create tracking and a draft PR for exactly one feature.

## One feature only

- One Linear issue
- One draft pull request
- One focused branch
- No unrelated edits in the same PR

If a release contains multiple features, call this workflow once per feature. If you notice unrelated changes that should be made, file a new Linear issue instead.

## Steps

1. Write a complete file set for the feature as full file contents (not patches). Include every file that must change for that feature alone.
2. Create the Linear issue with `create_linear_issue`:
   - `team_key="DOC"`
   - Title: concise, feature-scoped (for example "Document OpenWiki Copilot CLI integration")
   - Description: release tag, why docs must change, files to touch, acceptance criteria
   - Pass `product` and `release_tag`
   - The tool assigns the issue to the Linear API key owner (Naomi) automatically
3. Create the draft PR with `create_draft_docs_pr`:
   - Branch: `docs/<product>-<version>-<feature-slug>`
   - Title matches the issue scope
   - Body links the Linear issue URL and names the triggering release
   - `files_json` is a JSON array of `{ "path": "...", "content": "..." }`
4. Record the Linear URL and PR URL in product memory before starting the next feature.

## PR body template

```md
## Summary
- <one sentence on the docs change>
- Triggered by <product> <release tag>

## Linear
<issue url>

## Test plan
- [ ] Preview the changed pages
- [ ] Confirm claims against the release notes / upstream source
- [ ] Run `make lint_prose FILES="<changed mdx paths>"` when possible
```

## Do not

- Bundle multiple features into one issue or PR
- Modify `docs-release-watch/` in the docs PR
- Put secrets, tokens, or `.env` contents into issues or PRs
- Mark the PR ready for review; leave it as a draft
