---
name: docs-edit
description: Edit a docs page that already has an open pull request, or revise a page in place. Covers checking out the PR's own branch instead of cutting a new one, forked cross-repository PRs, reading the real diff, and the verification to run before handing off. Use when asked to edit, revise, fix, or review changes on a named PR, branch, or existing page.
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
redirects, use `add-docs-page`.

## Step 4. Verify before handing off

```bash
make lint_prose FILES="<changed files>"
```

Run `make broken-links` as well when links, page names, or navigation entries
changed. For a prose review against the style guide, use the `docs-review`
skill.

## Step 5. Report

Say which branch the edits are on and whether it is the PR's own branch. If
anything could not be verified, list it. Do not push or force-push unless the
user asks.
