---
name: release-research
description: Investigate an eligible product release against source diffs and current docs. Read-only. Returns a feature list with evidence; does not open tickets or PRs.
---

# Release research (read-only)

Use this skill only inside the `release-research` subagent. You investigate. You do not ship.

## Goal

For one product, decide which user-facing features in the eligible release need documentation updates, with citations from the product repo at that tag.

## Steps

1. Call `get_eligible_release` for the product with defaults (`min_age_days=7`, `max_age_days=30`). Only releases in that window are in scope, including on a first run with empty memory. Stop if nothing is eligible. Prefer the newest candidate; do not walk older tags outside the window.
2. Read product memory (`/memories/agent/<product>-releases.md`) and skip features already tracked for that tag.
3. Call `get_release_diff` for the eligible tag (omit `base_tag` so it resolves the previous same-prefix release). Treat the commit list and changed files as the primary signal.
4. Call `get_release_notes` only as secondary context. Notes are leads, not ground truth.
5. For each candidate feature from the diff, call `get_product_source_file` at the head tag and confirm the API, flag, command, default, or behavior exists.
6. Call `check_docs_coverage` with the candidate symbols/flags and concrete docs page paths (for example `src/oss/deepagents/customization.mdx`). If every needle already appears and the existing wording is still correct, put the feature under `skipped` with reason "already documented".
7. Call `get_docs_file` on pages that might need updates when coverage is missing or wording looks wrong.
8. Return a single research report. Do not call Linear or PR tools (you do not have them).

## Research report format

Return JSON (as your final message text) with this shape:

```json
{
  "product": "deepagentsjs",
  "head_tag": "deepagents@1.14.2",
  "base_tag": "deepagents@1.14.1",
  "features": [
    {
      "name": "FilesystemMiddleware offloadBinaryContent",
      "needs_docs": true,
      "reason": "New public option; docs Full stack and Override sections omit it.",
      "docs_paths": ["src/oss/deepagents/customization.mdx"],
      "evidence": {
        "source_repo": "langchain-ai/deepagentsjs",
        "source_tag": "deepagents@1.14.2",
        "items": [
          {
            "path": "libs/deepagents/src/middleware/filesystem.ts",
            "symbol": "offloadBinaryContent"
          }
        ]
      },
      "diff_files": [
        "libs/deepagents/src/middleware/filesystem.ts"
      ]
    }
  ],
  "skipped": [
    {
      "name": "internal test harness rename",
      "reason": "No user-facing API or docs impact."
    }
  ]
}
```

Set `needs_docs` to false (or put the item under `skipped`) when source shows no user-facing change, when `check_docs_coverage` shows the symbols are already present and correct, or when docs already cover it.

## Do not

- Open Linear issues or draft PRs
- Invent symbols that are not in `get_product_source_file` or the diff
- Recommend docs for pure refactors, dependency bumps, or internal-only changes
- Bundle unrelated capabilities into one feature entry
