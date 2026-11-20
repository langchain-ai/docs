## Why
<!-- The problem this change solves, in two or three sentences. -->

## Changes
<!-- One bullet per meaningful change, naming the page or file. -->
-

## Review notes
<!-- Where to look hardest, decisions a reviewer may disagree with, claims you could not verify, and the preview link. Delete this section if there is nothing to flag. -->

## Related
<!--
Issues, PRs, Linear tickets, or Slack threads. Delete this section if there are none.
External contributors: a new page, guide, or tutorial needs a linked issue that a maintainer approved and assigned to you. Typos and small fixes do not.
"Closes #123" closes a GitHub issue on merge. "Closes [DOC-123](<linear url>)" moves the Linear issue with this PR.
-->

## Checklist
<!-- Tick only what you did. Leave the rest unticked. -->
- [ ] I read the [contributing guidelines](https://docs.langchain.com/oss/contributing/documentation), including the [language policy](https://docs.langchain.com/oss/python/contributing/overview#language-policy)
- [ ] I checked the rendered pages locally with `docs dev` or on the preview deployment
- [ ] I ran every changed code example, or none changed
- [ ] `make lint_prose` passes on the changed files
- [ ] `make broken-links-with-anchors` passes, or no links, pages, or navigation changed
- [ ] I updated `src/docs.json` navigation and redirects, or no page was added, moved, or removed

<!-- If an AI agent helped, say so in one plain sentence here, for example "Prepared with Claude Code." Do not add a "Generated with" badge. -->
