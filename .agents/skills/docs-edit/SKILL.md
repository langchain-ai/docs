---
name: docs-edit
description: Edit a docs page that already has an open pull request, or revise a page in place. Covers checking out the PR's own branch instead of cutting a new one, forked cross-repository PRs, reading the real diff, checking the edit against related pages, and the verification to run before handing off. Use when asked to edit, revise, fix, or review changes on a named PR, branch, or existing page.
---

# Edit an existing docs page or PR

The failure this skill prevents: an agent asked to "fix the wording on PR 1234"
cuts a fresh branch, commits there, and opens a second pull request against a
teammate's work. Land edits on the branch that already exists.

## Step 1. Check out the PR's own branch

When the request names a PR, by number or URL, work on that PR's head branch.

```bash
gh pr view <n> --json number,title,headRefName,baseRefName,author,isCrossRepository,files
git status --porcelain          # must be clean; stop and ask if it is not
git fetch origin <headRefName>
git checkout <headRefName>      # tracks origin/<headRefName>
```

Use plain `git checkout <branch>`. Do not use `git checkout -b`, `--no-track`,
or a worktree: each produces a net-new branch, and committing there opens a
second PR against someone else's work.

A local branch whose name merely mentions the PR is not the same branch. Confirm
that `git rev-parse HEAD` matches the `headRefOid` from `gh pr view` before
editing, and that the branch has an upstream:

```bash
git rev-parse --abbrev-ref @{upstream}   # fails when the branch tracks nothing
```

Cut a new branch only when the edits are your own and no open PR exists to land
them on, or when the user asks for one. Branch from the latest `origin/main`,
never from a stale local `main`.

### Cross-repository PRs

When `isCrossRepository` is `true`, the branch lives on a fork. Use `gh pr
checkout <n>`, which configures the fork remote, and confirm push access before
committing. Without it, the edits are stranded locally.

## Step 2. Read the real diff

```bash
gh pr diff <n>
```

Prefer this over `git diff main...HEAD`. A stale local `main` silently inflates
that diff with unrelated commits, and a branch that already merged `main` once
inflates it further. To compare against the live base instead, fetch first and
use `git diff origin/main...HEAD`.

## Step 3. Edit

`AGENTS.md` holds the rules that apply to every edit: the style guide,
frontmatter, syntax, and the navigation map. Two that matter most here:

- Match the conventions of the file you are editing. Do not restructure,
  combine, or split pages unless asked.
- Never fabricate examples, field names, UI labels, or policy details. Verify
  each factual claim against the source it describes, and state plainly what you
  could not verify.

For voice and sentence rhythm while drafting, use the `docs-team-voice` skill. For
adding, moving, renaming, or deleting a page, including navigation and
redirects, use `add-docs-page`. When the edit is really a question of which page
the content belongs on, use `docs-restructure`.

### Verify claims against source, not against other docs

A sibling docs page is not a source. It is another claim, written by someone who
may have been guessing too, and two docs pages that agree can both be wrong.
Check the implementation:

```bash
gh api -X GET search/code -f q='LANGSMITH_GATEWAY repo:langchain-ai/langchain' \
    --jq '.total_count, (.items[]?|.path)'
gh api repos/langchain-ai/langchain/contents/<path> --jq .content | base64 -d
```

Python and TypeScript live in separate repositories and drift apart, so a table
with a Python column and a TypeScript column needs both checked:
`langchain-ai/langchain`, `langchain-ai/langchainjs`, and for some providers a
dedicated repository such as `langchain-ai/langchain-google`. A package's
`CHANGELOG.md` gives the version a feature landed in, which is what a minimum
version column needs.

State plainly what you could not verify. "I could not confirm the Baseten row;
no gateway references in either candidate repository" is a useful review note.
Silently keeping an unverified claim is not.

### Read the pages around the one you are editing

A page is one of several that cover the same feature. Others reach it from
another angle: a CLI reference, a permissions table, a list of Chat surfaces, a
setup guide, the pages that link to it. An edit made to one page in isolation
leaves the set contradicting itself.

Before editing, find the related pages:

```bash
grep -rliE "<feature name>|<page-slug>" src --include='*.mdx'
grep -n "<page-slug>" src/docs.json
```

Read each one, then check for:

- **Contradictions.** The edited page and a related one give different setup
  steps, defaults, or requirements. For example, a feature page that sets
  `LANGSMITH_API_KEY` while the CLI page recommends `langsmith auth login`.
  Settle it against source, then fix whichever page is wrong.
- **Duplication.** A procedure the edited page restates from the page that owns
  it. Link to the owner instead. When choosing the owner is the real question,
  use `docs-restructure`.
- **Missing entry points.** A page that lists every surface, command group, or
  permission area of a product should mention the feature and link to it.
- **Navigation placement.** A page filed in a group that does not match its
  subject. Report it; do not move the page unless asked.

A related page tells you what to check, not what is true. When two pages
disagree, the source decides, as described in the section above.

Keep edits to related pages small: a cross-link, a corrected fact, or a short
entry that points at the owner page. Anything larger is a restructure, so ask
first.

### Never hand-edit generated files

These are written by a generator. Editing them looks like it works, then a
scheduled run reverts it, and for the changelogs the edit has already gone out
over RSS:

| File | Generated by |
|------|--------------|
| `src/langsmith/changelog.mdx` | `changelog-weekly` skill, from langchainplus fragments |
| `src/langsmith/self-hosted-changelog.mdx` | the helm changelog bot |
| `src/langsmith/langsmith-platform-openapi.json` | `.github/workflows/refresh-langsmith-openapi.yml` |
| `src/langsmith/agent-server-openapi.json` | PRs from the `langgraph-api` repository |
| `src/snippets/deepagents-eval-category-matrix.mdx` | `scripts/refresh_deepagents_category_matrix.py` |
| `src/snippets/langsmith/mda-oauth-catalog.mdx` | `scripts/refresh_mda_oauth_catalog.py` |
| `build/` | `make build` |

When one of these carries the problem you were asked to fix, fix the generator
or the upstream source and say so. Do not edit the output.

### When an instruction reverses an earlier one

Reviewers change their minds, and on a long thread they will ask for a format
they previously rejected. Converting a table to a list and then back wastes a
round and loses the reasoning both times.

When an instruction contradicts one you already applied, say so before applying
it: name the earlier instruction, the change you made for it, and ask which to
keep. Two reversals on the same element mean the requirement is unclear, not
that the format is wrong.

## Step 4. Verify before handing off

```bash
make lint_prose FILES="<changed files>"
```

Run `make broken-links` as well when links, page names, or navigation entries
changed. For a prose review against the style guide, use the `docs-review`
skill.

## Step 5. Report

Say which branch the edits are on and whether it is the PR's own branch. Name
the related pages you changed, and the ones you read and left alone. If
anything could not be verified, list it. Do not push or force-push unless the
user asks.
