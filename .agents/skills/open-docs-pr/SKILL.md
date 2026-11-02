---
name: open-docs-pr
description: Open a pull request for finished docs changes. Covers cutting the branch from the latest origin/main, the lint and link gates, the commit, writing the PR description in the repo's short format with the AI disclosure line, pushing safely, and watching the PR checks until they pass. Use when asked to open, create, put up, or submit a docs PR, or after add-docs-page or docs-edit finishes an edit that has no PR yet.
---

# Open a docs pull request

This skill starts when the edit is finished and ends when the PR is open and
its checks are green. Editing a PR that already exists is `docs-edit`, not this
skill: pushing a second PR against a teammate's work is the failure that skill
prevents.

The rules every task follows live in `AGENTS.md`. This skill is the order to
apply them in.

## Step 1. Branch from the latest main

Never commit to `main`. Cut a new branch from a freshly fetched `origin/main`,
not from a local `main` that may be days old:

```bash
git fetch origin main
git switch -c <type>/<short-topic> --no-track origin/main
```

`--no-track` stops the branch from tracking `origin/main`, so a bare push
cannot land on `main`.

The main checkout may be shared with other agent sessions that switch branches
under you. Prefer a worktree inside the checkout:

```bash
git worktree add -b <type>/<short-topic> --no-track .claude/worktrees/<name> origin/main
```

A new worktree's `.mise.toml` is untrusted, so the first commit fails at the
Vale hook with `Config files in <dir>/.mise.toml are not trusted`. Run
`mise trust` once in the worktree. The `docs-edit` skill covers the permanent
fix. Run `make skills` in the worktree too if you use Claude Code.

## Step 2. Run the gates

Run each gate that applies to the change before committing. CI runs the same
ones, so a skipped gate becomes a red check later.

- **Prose review**: Run the `docs-review` skill on the changed pages. It covers
  the style-guide rules Vale cannot see. Skip it for a change with no prose.
- **Vale**: `make lint_prose FILES="<changed .mdx files>"`. Fix every error.
- **Links**: `make broken-links-with-anchors` when links, page names, anchors,
  or `src/docs.json` changed. Read only the indented `⎿` lines.
- **Code samples**: `make test-code-samples FILES="<changed samples>"` when a
  file under `src/code-samples/` changed.
- **Pipeline**: `make test` and `make lint` when `pipeline/`, `scripts/`, or
  `tests/` changed.

Note which gates you ran. The PR checklist asks for them.

## Step 3. Commit

Stage only the files the change touched, then check that nothing secret is
staged:

```bash
git diff --cached --name-only
```

Write the subject line in the form recent merged PRs use: `docs: ...` for
content, `docs(<product>): ...` when one product is involved, and `chore: ...`
for tooling. The body explains why, not what.

Do not add a `Co-Authored-By` trailer for an AI agent. A ruleset on `main`
rejects the Claude trailer at merge time, and squash merges carry branch commit
trailers into `main`.

## Step 4. Write the PR description

Use the sections in `.github/pull_request_template.md`: **Why**, **Changes**,
**Review notes**, **Related**, and the checklist. Fill each one in, and delete
any section that would be empty rather than leaving placeholder comments.

- **Why**: The problem the change solves, in two or three sentences.
- **Changes**: One bullet per meaningful change, naming the file or page.
- **Review notes**: Where to look hardest, decisions the reviewer may disagree
  with, and every claim you could not verify against source. A preview link
  goes here once the preview deploys.
- **Related**: Issues, PRs, Linear tickets, and Slack threads. Write
  `Closes [DOC-N](<linear url>)` to let `sync-linear-issue-from-pr.yml` move
  the Linear issue with the PR.
- **Checklist**: Tick only what you actually did in Step 2. Leave the rest
  unticked rather than claiming it.

End with one plain sentence that discloses AI involvement, for example
`Prepared with Claude Code.` Do not add the `🤖 Generated with [Claude Code](...)`
badge or any similar badge. The `check-pr-ai-attribution` check fails a PR
whose description carries one, because the squash merge would copy it into the
commit on `main`.

Write the description to a file and pass it with `--body-file`. A shell
heredoc inside `--body "$(...)"` breaks on apostrophes in some shells.

## Step 5. Push and open the PR

Confirm the remote is a `langchain-ai` repository, then push with an explicit
remote and branch. Never run a bare `git push`.

```bash
git remote get-url origin        # must be github.com/langchain-ai/docs
git push -u origin <branch>
gh pr create --base main --head <branch> --title "<subject>" --body-file <file>
```

Open it as a draft (`--draft`) if it is not ready for review.
`pr-welcome-comment.yml` requests reviewers from `.github/OWNERS` when the PR
leaves draft, so do not request reviewers by hand unless asked.

If you later push more commits, first check that the PR has not merged. A push
to a merged PR's branch lands nowhere:

```bash
gh pr view <n> --json state,mergedAt
```

## Step 6. Watch the checks

```bash
gh pr checks <n> --watch
```

For a failure, read the log with `gh run view <run-id> --log-failed`, fix the
cause on the same branch, and push again. Editing the PR description reruns the
description checks without a new commit.

For same-repo PRs, `create-preview-branch.yml` comments a preview URL. Forks do
not get one.

## Step 7. Record tooling changes

When the PR adds or changes a script, workflow, Makefile target, check,
scheduled job, or skill, invoke `docs-tooling-notion` before handing off.

## Report

Give the PR URL, the branch, the gates you ran and their results, the state of
the checks, and anything you could not verify.
