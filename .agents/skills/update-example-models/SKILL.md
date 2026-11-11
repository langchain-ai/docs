---
name: update-example-models
description: Roll a provider example model ID across LangChain docs (for example gpt-5.5 to gpt-6.1-sol). Covers verifying the official GA ID, updating content and code samples, regenerating snippet MDX, updating the CodeGroup generator and its unit tests, onboarding and eval allowlists, and what to leave historical. Use when asked to bump, update, or replace an OpenAI, Anthropic, Google, or other LLM model ID in docs examples, or when reviewing a model-ID bulk update PR.
license: MIT
metadata:
  author: langchain
  version: "1.0"
---

# Update example model IDs

The failure this skill prevents: a bulk string replace updates hundreds of MDX
and sample files, CI looks green, and the next `make code-snippets` rewrites
OpenAI CodeGroup tabs back to the old ID because the generator table was never
touched. Or the replace invents a non-existent ID (`gpt-6.1`,
`gpt-6.1-2026-04-23`) because the new product name was guessed from the old
one.

`AGENTS.md` already requires latest GA model IDs in illustrative snippets. This
skill is the procedure for changing them safely. Link to
[AGENTS.md](../../../AGENTS.md) for style; do not restate the style guide.

## Step 1. Verify the official ID

Before writing any file, confirm the exact model ID against the provider's
current docs. Do not infer the new ID by editing the old string.

| Check | Why |
|-------|-----|
| Exact API ID (`gpt-6.1-sol`, not `gpt-6.1`) | Product marketing names often omit the tier suffix |
| GA, not preview/beta | Docs default to GA unless the feature has no GA equivalent |
| Snapshot list | Dated IDs like `gpt-5.5-2026-04-23` do not become `gpt-6.1-2026-04-23` by arithmetic; use a listed snapshot or the floating GA ID |
| Parameter compatibility | Reasoning models may reject `temperature` unless effort is `none`; some IDs do not support `none` |

OpenAI model pages: [Models](https://developers.openai.com/api/docs/models).
Anthropic and Google: use each provider's current model list the same way.

Pick one **default example ID** for general agent/chat samples (today's OpenAI
default is `gpt-6.1-sol`). Keep separate IDs for:

- **Small / cheap examples** (for example `gpt-5.4-mini`, `gpt-6-luna`) when the
  page needs a lightweight model
- **Intentional failure / timeout fixtures** pinned on purpose
- **Historical names** in migration guides and changelogs

## Step 2. Inventory every place the old ID lives

A content-only grep under `src/` is not enough. Search the whole repo:

```bash
rg -n 'OLD_ID' \
  src/code-samples src/snippets scripts tests \
  .github .agents src --glob '!**/migrate/**'
```

Required stop list (update these when the ID is the **default example**):

| Location | Role |
|----------|------|
| `src/**/*.mdx` | Page examples and prose |
| `src/code-samples/**` | Testable sources |
| `src/snippets/code-samples/**` | Generated Mintlify snippets |
| `scripts/generate_code_snippet_mdx.py` | `DEEPAGENTS_QUICKSTART_{PY,TS}_MODEL_TABS` OpenAI (or other) tab |
| `tests/unit_tests/test_generate_code_snippet_mdx.py` | Asserts the generator's OpenAI tab ID |
| `scripts/data/onboarding_models.yaml` | LangSmith in-product onboarding allowlist (`preferred` / `current`) |
| `scripts/refresh_deepagents_category_matrix.py` | `INCLUDED_MODELS` for the Deep Agents eval table |
| `.github/workflows/integration-submission.yml` | Agent model used by that workflow |
| `src/.mintlify/skills/**` | Mintlify skill examples, if present |

Leave alone unless the task explicitly includes them:

- `src/oss/**/migrate/**` and changelog entries that record historical names
- Intentional fixtures called out in the PR or Linear issue
- Provider-specific product aliases only after verifying that product still
  accepts the bare name (ChatGPT Codex, Copilot, and gateway routes can differ
  from the OpenAI API ID)

## Step 3. Update in this order

1. **Generator and its unit tests first.** Change
   `DEEPAGENTS_QUICKSTART_*_MODEL_TABS` and every assertion that hardcodes the
   old OpenAI tab ID. Prove the risk:

   ```bash
   uv run python - <<'PY'
   from scripts.generate_code_snippet_mdx import (
       DEEPAGENTS_QUICKSTART_PY_MODEL_TABS,
       maybe_expand_deepagents_quickstart_codegroup,
   )
   print(DEEPAGENTS_QUICKSTART_PY_MODEL_TABS)
   sample = 'agent = create_deep_agent(model="openai:NEW_ID", tools=tools)\n'
   expanded, _ = maybe_expand_deepagents_quickstart_codegroup(
       sample, language="python", fence_lang="python"
   )
   assert expanded and 'openai:NEW_ID' in expanded
   assert 'openai:OLD_ID' not in expanded
   print("generator OK")
   PY
   uv run pytest tests/unit_tests/test_generate_code_snippet_mdx.py -q
   ```

2. **Code samples** under `src/code-samples/`. Prefer exact ID replaces. Do not
   invent dated snapshots. If a sample used `OLD_ID-YYYY-MM-DD` and the new
   model has no matching snapshot, switch to the floating GA ID.

3. **Regenerate snippets** so MDX tracks the samples and the generator:

   ```bash
   make code-snippets
   ```

   String-replacing `src/snippets/code-samples/**` without regenerating leaves
   the tree looking updated while the generator can still emit the old ID.

4. **Inline MDX** that is not driven by snippets. After the bulk replace, grep
   again for the **old ID**, for the **bare new stem** (for example `gpt-6.1`
   without `-sol`), and for **invented dated** forms.

5. **Allowlists.** In `onboarding_models.yaml`, add the new GA ID to `current`
   (and update `preferred` only when the preferred small/hello-world model
   changes). Keep the previous generation in `current` until the provider has
   superseded it twice. In `refresh_deepagents_category_matrix.py`, add the new
   `provider:model` keys when evals exist or are expected; do not delete old
   keys until the matrix no longer needs them.

## Step 4. Verify

```bash
# No stale default example ID outside migrate/changelog/intentional fixtures
rg -n 'OLD_ID' src scripts tests .github \
  --glob '!**/migrate/**' --glob '!**/*changelog*'

# No bare stem left behind by a half-finished rename
rg -n 'BARE_STEM' src scripts tests | rg -v 'BARE_STEM-FULL'

# Generator and unit tests
uv run pytest tests/unit_tests/test_generate_code_snippet_mdx.py -q

# Regenerated snippets match HEAD after make code-snippets
git status --porcelain src/snippets/code-samples

# Prose lint on hand-edited MDX
make lint_prose FILES="path/to/changed.mdx …"
```

`check-generated-files` in CI only validates the partner overview table. It
does **not** prove snippet MDX matches the generator. Rely on the generator
test and a local `make code-snippets` diff.

Run `make test-code-samples` on touched samples when credentials are available.
A LangSmith `409 Nothing to commit` on `push_prompt` is usually an idempotent
hub conflict, not a bad model ID.

## Step 5. PR hygiene

- Title and body must name the **exact** new ID (`gpt-6.1-sol`), not a marketing
  stem (`gpt-6.1`).
- Call out intentional exceptions (`gpt-5.4-mini`, migration guides, timeout
  fixtures).
- Disclose AI involvement in one plain sentence when an agent prepared the PR.
- Adding or changing this skill (or related scripts) also requires
  `docs-tooling-notion` before handoff.

## Anti-patterns

- Replacing only under `src/**/*.mdx` and skipping `scripts/` / `tests/`
- Guessing `NEW_ID` by editing `OLD_ID` character-by-character
- Mechanical dated-snapshot rewrites (`-YYYY-MM-DD` kept after a rename)
- Updating generated snippet MDX by hand and leaving the CodeGroup tab table
  stale
- Changing migration-guide or changelog historical IDs "for consistency"
- Relabeling eval matrices, suggested-models tables, capability floors
  (`gpt-5.5+`), or "supported models" lists: those are measured or product
  facts, not example IDs. Keep the old ID until new evidence exists; for the
  Deep Agents matrix, regenerate with
  `scripts/refresh_deepagents_category_matrix.py --write` after real evals
- Leaving prose link text on the old name after the href moves (for example
  "GPT-5.5 snapshot" pointing at `gpt-6.1-sol`)
  stale
- Changing migration-guide or changelog historical IDs "for consistency"
