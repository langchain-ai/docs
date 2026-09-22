---
name: docs-restructure
description: Restructure documentation that spans several pages. Covers splitting a page that has grown too long, moving sections between pages, retiring a page, and fixing a topic documented in two places at once. Use when asked to streamline, simplify, consolidate, or reorganize docs, or when a page review keeps producing edits without the page getting shorter.
---

# Restructure docs across pages

The failure this skill prevents: an agent asked to "streamline this page" reorders
its sections, collapses them into accordions, retitles them, and tabulates them,
thirty times over, while the page gets longer. The page was never the problem.
Three of its sections already existed on sibling pages.

Single-page skills cannot see that. `add-docs-page` owns one page's lifecycle and
`docs-edit` owns one page's diff. This skill owns the question they cannot ask:
**is this content on the right page at all?**

`AGENTS.md` holds the navigation map, the style guide, and the frontmatter rules.
This skill covers the procedure around them and does not repeat them.

## Step 1. Establish the page family

A page almost never lives alone. Find its siblings before reading it closely:

```bash
ls src/langsmith/llm-gateway*.mdx          # a flat-file family
ls src/oss/deepagents/                     # a directory family
grep -n '"langsmith/llm-gateway' src/docs.json   # what the nav groups together
```

The nav grouping is the better signal when the two disagree: pages a reader
moves between are the pages whose content can be confused.

Then list every heading in the family, so you are working from the whole shape
rather than one file:

```bash
grep -n '^## ' src/langsmith/llm-gateway*.mdx
```

## Step 2. Build a duplication map before writing anything

This is the step that does the work. For each H2 in the page you were asked to
fix, search the rest of the family for the same content:

```bash
grep -rn 'LANGSMITH_GATEWAY' src/langsmith/ --include=*.mdx
grep -rn 'Use a regional gateway' src/ --include=*.mdx
```

Search for the distinctive noun, env var, or endpoint in the section, not for
its heading. Duplicated content is usually retitled, which is why heading
searches miss it.

Record for each section: **does this topic already live somewhere else, and
where?** Two copies that have drifted apart are the strongest finding available.
It means no page owns the topic, so both copies are edited independently and
readers get contradictions. In one real case the quickstart claimed TypeScript
support for three providers while the sibling page said "Python only."

Report the map before editing anything. "Three of these six sections duplicate
`llm-gateway-api-formats`" is the finding. The restructure is downstream of it.

## Step 3. Assign one home per topic

For each topic in the map, pick the single page that should own it:

- **Prefer a page that already exists.** A new page is warranted when the topic
  has no home and does not fit an existing one, not when it merely needs
  somewhere to go.
- **Prefer the page a reader would search for**, not the page the content
  happens to sit on.
- **Keep the most-linked URL.** Check before choosing, because inbound links
  decide which file survives a merge of two pages:

  ```bash
  grep -rn '(/langsmith/llm-gateway)' src/ --include=*.mdx | wc -l
  ```

  Folding content *into* the well-linked page and retiring the other one is
  usually cheaper than the reverse.

## Step 4. Cut, do not relocate

A section that duplicates a sibling gets **deleted** and replaced with one
sentence pointing at the owner. It does not get moved, collapsed into an
accordion, or shortened in place. An accordion still costs the reader the
decision of whether to open it.

Content that has no home yet moves. Content that has one is already written.

When you delete a section whose facts differ from the sibling's, the difference
is a bug in one of them. Resolve it against the source before deleting, or you
silently pick a winner. See `docs-edit` for the verification procedure.

## Step 5. Mechanics

Retiring, renaming, or creating a page means navigation entries, redirects, and
inbound links. `add-docs-page` covers all of it, including the anchor-stability
and snippet traps. Follow it rather than improvising here.

Two additional things a restructure breaks that a single-page edit does not:

- **Section anchors other pages link to.** Moving a section moves its anchor.
  Grep for `#the-anchor` across `src/` before the move and repoint every hit. A
  `<Step>` or `<Accordion>` can carry an explicit `id` to preserve a landing
  spot that is no longer a heading.
- **Cross-page pointers that now point at the wrong page.** After moving a
  topic, the sibling pages that used to reference its old location need
  repointing, not just the page you edited.

## Step 6. Verify

```bash
make lint_prose FILES="<changed files>"
make build
make broken-links-with-anchors
python3 scripts/check_removed_pages_redirects.py --base-ref origin/main src/docs.json
```

Read `broken-links-with-anchors` by skipping to the `⎿` lines; those are the
only real failures. Compare the count against the same command on `origin/main`
so a pre-existing baseline is not read as a regression.

Then review the prose with the `docs-review` skill, scoped to the files this
pass changed.

## Step 7. Report what moved

State, per page, what was **deleted**, what **moved**, and what was **added**,
with before and after line counts. A restructure that cannot show a page getting
shorter has not restructured anything, and the line counts are what show the
reviewer whether it did.

Name what you deleted rather than only what you wrote. A reviewer who asked for
a shorter page needs to see the cuts to agree with them.

## Scope

Stay inside the page family named in the request. A restructure surfaces
adjacent problems: stale model IDs, legacy version numbers, and the same
duplication one directory over. Report them, and **ask before widening the
sweep.** Fixing sixteen instances across a page family is a reasonable follow-on
inside one pull request. Fixing six hundred across the corpus is a separate pull
request and probably a tracked issue, because some instances are deliberate and
some live in generated files.

## Checklist

- [ ] Page family established from `src/docs.json`, not guessed from filenames.
- [ ] Duplication map built and reported before any edit.
- [ ] One owner chosen per topic; most-linked URL identified before merging pages.
- [ ] Duplicated sections deleted and replaced with a pointer, not relocated.
- [ ] Conflicting facts between copies resolved against source, not by picking one.
- [ ] Redirects, nav entries, inbound links, and section anchors all updated.
- [ ] Verification commands run, `⎿` count compared against `origin/main`.
- [ ] Report gives per-page before and after line counts.
- [ ] Anything outside the page family reported, not swept, unless asked.
