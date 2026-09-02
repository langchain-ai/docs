---
name: update-integrations-prs
description: >-
  Process open LangChain docs integration PRs against the hosted-guide featuring
  policy (50K monthly downloads or maintainer feature override). Rebase an integration PR, convert to
  external YAML, feature an integration, or check package downloads for docs
  eligibility.
---

# Update integrations PRs

Process contributor integration docs PRs in `langchain-ai/docs` so they match the [hosted-guide eligibility rules](https://docs.langchain.com/oss/contributing/publish-langchain#eligibility-for-hosted-guides) from [#4865](https://github.com/langchain-ai/docs/pull/4865).

## Policy

| Case | Action |
|------|--------|
| **≥50K monthly downloads** (PyPI or npm) **or** maintainer feature override | Keep hosted MDX. Ensure correct `integration:` frontmatter. May set `highlight: true` in `packages.yml` and regenerate overview via `partner_pkg_table` (**never** hand-edit `overview.mdx`). |
| **Under 50K**, not featured | Remove hosted pages. Add YAML to `scripts/data/integration_external_docs.yaml`. Surface via downloads tables / `all_providers`. Prefer partner docs URLs. Keep `packages.yml` when there is a public LangChain-related package. |

Policy source: `src/oss/contributing/publish-langchain.mdx` and `src/oss/contributing/integrations-langchain.mdx`.

## Workflow checklist

Copy and track:

```
- [ ] Identify PR + package name(s)
- [ ] Report monthly downloads (PyPI and/or npm)
- [ ] Decide: hosted/feature vs external
- [ ] Rebase onto upstream/main (keep contributor commits)
- [ ] Apply conversion in a **separate** commit
- [ ] Verify net diff vs main
- [ ] Report result; do **not** push unless asked
```

### 1. Inspect the current branch

```bash
git branch --show-current
gh pr view --json number,title,url,author,maintainerCanModify,files,body
git diff --stat upstream/main...HEAD
```

Find the LangChain-related package name(s) from `packages.yml`, MDX install snippets, or registry metadata. Ignore unrelated packages with similar names.

### 2. Measure downloads

**PyPI** (last ~30 days, no mirrors):

```bash
curl -s "https://pypistats.org/api/packages/<pkg>/overall?mirrors=false" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); data=d.get('data',[]); last30=data[-30:] if len(data)>=30 else data; print(sum(x.get('downloads',0) for x in last30))"
curl -s "https://pypistats.org/api/packages/<pkg>/recent"
```

**npm** (last month):

```bash
curl -s "https://api.npmjs.org/downloads/point/last-month/<pkg>"
```

Report the number to the user before converting when they asked for downloads only.

### 3. Rebase

```bash
git fetch upstream main
git rebase upstream/main
```

- Keep contributor commits; put the conversion in a **new** commit after rebase.
- On heavy merge history, cherry-pick content commits onto `upstream/main`, then convert.
- Drop obsolete Card grids that main replaced with `IntegrationDownloads`.
- Drop redirects for pages that were never on `main`.
- Drop unrelated `packages.yml` download-count churn from bot commits.

### 4a. External conversion (under 50K)

1. **Delete** hosted MDX (component page and provider page if present).
2. **Add YAML** under the correct language + component in `scripts/data/integration_external_docs.yaml`:

   ```yaml
   - name: ClassOrDisplayName
     pypi: langchain-example   # or npm: "@org/pkg" under javascript:
     docs_url: https://partner.example/docs
   ```

   Prefer partner docs, then public GitHub/GitLab README, then PyPI/npm.
3. **Downloads snippet** (sort by `data-sort-value`): add a row to the matching `src/snippets/oss/*-*-downloads.mdx` (for example `python-sandboxes-downloads.mdx`). Match existing badge markup.
4. **`all_providers`**: card with external `href` (alphabetical). Use `icon="link"` or an existing provider icon.
5. **`packages.yml`**: append only for a public LangChain-related package. Ensure a trailing newline before appending. Omit `path: .`. Skip if the source repo is private or not a normal public VCS listing.
6. **Nav / redirects**: remove `docs.json` entries and redirects for deleted never-on-main pages. Do not add redirects for pages that never shipped.
7. **Deep Agents / indexes**: if the PR added provider cards that main no longer uses, prefer downloads tables and index grids; keep brief mentions only when main already lists providers that way.

Align listings with **partner docs**, not stale PR page counts.

### 4b. Hosted / featured path (≥50K or override)

1. Keep (or fix) hosted MDX; test code examples when touching them.
2. Frontmatter: follow templates under `src/oss/*/integrations/**/TEMPLATE.mdx`. Do not set `featured: true` unless a maintainer asked.
3. Prefer `langchain` imports over `langchain_core` when editing kept pages.
4. For featuring: set `highlight: true` in `packages.yml` only when asked; regenerate overview with the partner package table tool, do not hand-edit `overview.mdx`.
5. Update `src/docs.json` if adding a page that should stay.

### 5. Commit and handoff

- Conversion commit message focuses on why (threshold / external listing / feature).
- Show `git diff --stat upstream/main...HEAD` and downloads in the summary.
- Note `maintainerCanModify` for push later.
- **Do not push** unless the user asks. Use force-with-lease after rebase when pushing to the PR head.
- If `maintainerCanModify: false`, say so and ask whether to open a replacement PR.

## Hard rules

- Ask for clarification rather than assuming package identity or feature overrides.
- Never fabricate download counts, docs URLs, or package names.
- Never edit `build/`.
- Never hand-edit generated overview tables.
- When appending to `packages.yml`, ensure a trailing newline first.
- Run `make lint_prose FILES="..."` on changed MDX before handoff when prose changed.
- Follow repo git safety: no bare `git push`; no force to main; no commit unless asked (except when the user said "go" / "next branch" for this workflow, commit the conversion).

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| Wrong package (similar name on PyPI) | Confirm against install snippets and partner repo |
| Re-adding Card grids removed on main | Use `IntegrationDownloads` / YAML only |
| Redirects for never-shipped pages | Delete them |
| Duplicate table rows | Remove YAML if keeping hosted page |
| Private source repo | Skip incomplete `packages.yml` entry |
| JS + Python packages | Add both YAML sections / download rows when both exist |

## Reference

- Eligibility docs: `/oss/contributing/publish-langchain#eligibility-for-hosted-guides`
- YAML data: `scripts/data/integration_external_docs.yaml`
- Downloads snippets: `src/snippets/oss/*-downloads.mdx`
- Package registry: `packages.yml`
- Policy PR: https://github.com/langchain-ai/docs/pull/4865
