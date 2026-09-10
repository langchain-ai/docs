---
name: docs-review
description: Review changed docs prose against Vale and the AGENTS.md style guide, reporting findings with the rule each one breaks. Use after authoring or editing a page and before committing, or to review a PR, a branch, or the current diff.
argument-hint: "[PR number or URL | branch | nothing for uncommitted or current-branch changes]"
allowed-tools: Bash(git:*), Bash(gh pr:*), Bash(gh api:*), Bash(make lint_prose:*), Read, Grep, Glob
license: MIT
metadata:
  author: langchain
  version: "1.0"
---

# Review docs prose

Review documentation prose that changed in `$ARGUMENTS`, or in the working tree
and current branch if that is empty.

Two rules govern this whole skill:

- **Review the diff, not the page.** Prose that was already there is not in
  scope, however much you would have written it differently.
- **Skip rules that do not clearly apply.** A short report of real findings is
  the goal. Do not stretch a rule to reach a finding, and do not restructure
  prose that is already fine.

## Step 1. Resolve the target

Run `git fetch origin` first so `main` is current. Resolve in this order:

1. **A number or GitHub PR URL** means a PR. Get the branch with
   `gh pr view <n> --json headRefName`.
2. **A branch name** is used directly.
3. **Empty, with uncommitted changes present** means the working tree. Take the
   files from `git status --porcelain` plus
   `git diff --name-only --diff-filter=d origin/main...HEAD`. No checkout, no
   worktree: the files are already in front of you. This is the mode that runs
   after an authoring skill.
4. **Empty, with a clean tree** means the current `HEAD` against `main`:
   `git diff --name-only --diff-filter=d origin/main...HEAD`.

Narrow to `src/**/*.mdx` and `src/**/*.md`. If nothing changed, say so and stop.
Never review anything under `build/`.

**For modes 1 and 2, check out the target before inspecting anything.** Your
working tree is almost certainly on a different branch, and linting it silently
reports on the wrong content.

For a PR, check the branch out in the main working tree so any edit that follows
lands on the open branch:

```bash
git stash list            # confirm nothing is about to be lost
git status --porcelain    # must be clean; stop and ask if it is not
git fetch origin <branch>
git checkout <branch>     # tracks origin/<branch>
```

Use `git checkout <branch>`, not `git checkout -b` or a `--no-track` branch. A
new branch is only correct when the review is of `main`, or when the user asks
for a separate branch of their own edits. Confirm the checkout by grepping for a
string the diff added.

For a review with no edits to follow, a detached worktree is also fine:

```bash
git worktree add --detach <scratch-dir>/review-wt origin/<branch>
```

Do all reading and linting inside it, and `git worktree remove --force` it when
the review is done.

State the target, the resolved SHA or "working tree", and the file count before
going further.

## Step 2. Run Vale

In the main checkout, `make lint_prose FILES="<files>"` is enough. Vale's binary
is gitignored, so a fresh worktree does not have it and `make lint_prose` there
fails with `.bin/vale: No such file or directory`. From a worktree, call the main
checkout's binary by path so it picks up `.vale.ini`:

```bash
cd <worktree> && <main-checkout>/.bin/vale --glob='!**/node_modules/**' <files>
```

Vale is deterministic and CI blocks on it, so its output is not a judgment call.
Report every violation with its file and line. If invoked with `--fix`, correct
them; otherwise list them.

Vale covers terminology, contractions, first person, future tense, Oxford
commas, spaced em dashes, navigation-path arrows, and heading case. **Do not
spend model judgment re-checking what Vale already checks**, with one exception:
Vale does not scan inside JSX components such as `<Note>` and `<Tip>`, so a clean
run is not proof that content inside them complies. Grep the added lines in those
blocks for the mechanical rules yourself.

## Step 3. Check structure against the style guide

Read the "Structure conventions" section of `AGENTS.md` in the repository root,
then check the changed hunks against it. For each finding, quote the rule you are
applying.

Look for these, and nothing else:

- **A new section or page that does not open with a one-sentence definition** of
  what the thing is or does, followed by the benefit, then the task. Skip when
  the section continues directly from the one above it.
- **Steps introduced without a colon lead-in**, or steps that are not imperative.
  Skip for a list that is not a procedure.
- **Three or more options, parameters, or permissions written as prose** where
  `- **Term**: Explanation.` would carry them. Skip for fewer than three.
- **A feature or class linked on repeat mentions**, or a first mention that is
  not linked. Skip when the repeat is far enough down the page to be a genuine
  re-entry.
- **A permission, plan tier, or preview requirement stated after the steps it
  governs** rather than before them.
- **A hard constraint hedged** ("it is generally not possible to change this")
  where the guide calls for a flat fact ("Once set, it cannot be changed.").

Pointer phrasing is deliberately absent from that list. Both the long form ("For
more information, see [Page]") and the short form ("See [Page]") are
established. Do not convert between them in either direction.

## Step 4. Check the style guide items Vale cannot see

Read the "Style guide" section of `AGENTS.md`. Vale enforces the mechanical half.
These are the rules that need reading:

- **Passive voice** where the actor is known. "Feedback is treated as a signal"
  hides who treats it. Skip when the actor is genuinely irrelevant or unknown.
- **Filler and hedging**: "Note that", "Specifically", "simply", "easily",
  "just", "very", "basically", "obviously". Cut the word, keep the sentence.
- **Product versus common noun capitalization.** A capitalized feature name that
  appears nowhere else in the file, or that disagrees with the UI label used
  elsewhere on the same page, is the tell. Grep the file for the term's other
  casings before reporting.
- **Bold in body text** beyond UI labels. Match what the rest of the page does
  rather than an abstract standard.
- **Repetition inside the diff.** The same list of items enumerated twice in one
  short section, or a sentence restating the one above it.
- **Link text** that does not describe its destination, and two different labels
  pointing at the same anchor.
- **Version minimums written with `>=` in prose.** The convention is "v0.153.4 or
  later"; `>=` belongs only in package specifiers such as `langsmith>=0.3.13`.

Measure before reporting a convention violation. If you are about to say a
heading form or phrasing is wrong, grep the repository for how often it already
appears. A form used widely is established practice, not a defect, however much
the guide seems to prohibit it. Report the count either way.

## Step 5. Check the mechanics the diff implies

Only when the diff triggers them:

- A new page: is it in `src/docs.json`, in the right product, tab, and group?
- A renamed or deleted page: are inbound links and the `docs.json` entry both
  updated?
- New internal links: root-relative, and free of `/python/` or `/javascript/`?
- A new code block: does it carry a real language tag, and are imports sorted?
- A page or heading that changed URL: is there a redirect?

The `add-docs-page` skill covers all five in detail. Point at it rather than
restating the procedure in a finding.

## Step 6. Report

Group by file. For each finding:

```txt
src/langsmith/example.mdx:42
Rule: "State requirements and constraints up front"
The admin permission requirement appears after step 3, but governs all of them.
Suggested: move it above the numbered list.
```

End with a one-line verdict: what blocks merge (Vale violations, missing nav
entry, broken link) versus what is a suggestion.

If nothing turns up, say that plainly. "No findings" is a valid and useful
result, and is more useful than a manufactured one.

## Running after an authoring skill

`add-docs-page` invokes this skill at its verification step, in working-tree
mode, on the files it just changed. Two constraints keep that useful:

- **Review finished edits, not drafts.** Findings on a half-written section go
  stale as soon as writing resumes, and reporting them trains the reader to
  ignore the report. Run after the edit is complete and before the commit.
- **Scope to the files the authoring pass touched.** Do not widen to the rest of
  the branch. If other files changed earlier and also want review, say so and
  let the user ask.
