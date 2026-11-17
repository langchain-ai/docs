---
name: verify-against-source
description: Check that a code sample, API signature, default, or behavior claim in the docs is actually true, by running it or reading the product source. Covers which repository owns each product, how to reach the private ones, running the part of a sample that needs no API key, and what to say about a claim you could not verify. Use when writing or reviewing a page that asserts how LangChain, LangGraph, Deep Agents, or LangSmith behaves, and when a PR describes behavior without citing where it was checked.
---

# Verify a claim against the source

The failure this skill prevents: a page states a default, a precedence order, or
a field name that reads plausibly, passes Vale and the link checker, and is
wrong. Nothing in CI checks whether a sentence about product behavior is true.
A reviewer who knows the product catches some of it; the rest reaches readers.

Published docs, a README, and a model's recollection are all secondary sources.
Prefer evidence you produced in this session.

## Step 0. Check that the PR does what it says

When reviewing a PR, start with what it claims to document, before any single
sentence. The PR description is a claim, not a fact.

1. Find the product change behind the PR: a product PR, release, or issue
   linked from the description, or the commits in the owning repository (Step 2)
   that match the feature name.
2. List what a reader needs from that change: the behavior, its defaults, the
   permissions or plan tier it requires, its limits, its version floor, and
   whether it exists in both Python and TypeScript.
3. Compare the list against the diff. Anything the product change ships that
   the page leaves out is a gap. A gap a reader would hit is `major`. A page
   that describes something the product change does not do is `must_fix`.

Answer three questions, each with evidence:

- Does the diff document the change the description names?
- Does it cover the defaults, requirements, and limits a reader needs?
- Does any statement in the diff contradict the product change?

When no product change can be found, say so in `not_checked`. Do not infer
what the feature should do from the docs diff alone.

## Step 1. Pick the strongest evidence available

Work down this list and stop at the first rung you can actually reach. Each rung
is weaker than the one above it.

- **Run the sample.** `make test-code-samples`, or scope it with
  `FILES="src/code-samples/langchain/foo.py"`. This is the only method that
  proves a sample works end to end. It needs provider API keys in the
  environment, so it often fails locally and runs in CI instead.
- **Run the half that needs no model.** Most claims are about a library's
  behavior, not the model's. Stand up the real object in a scratch script and
  print what it returns. A local MCP server, an adapter, a parser, or a store
  needs no API key, and the answer it gives is exact rather than inferred.
- **Read the library source.** Locate the file with the git trees API, then
  fetch it:

  ```bash
  gh api "repos/langchain-ai/<repo>/git/trees/HEAD?recursive=1" \
    --jq '.tree[].path' | grep -i '<symbol or feature>'
  gh api "repos/langchain-ai/<repo>/contents/<path>" --jq '.content' | base64 -d
  ```

  Do not use `search/code`: it rate-limits quickly and returns nothing on the
  larger private repositories. Source settles what a type is, what a default
  is, and which branch actually runs.
- **Check the installed package.** `uv run python -c "from x import Y"` confirms
  an import path resolves at the version this repo pins, which source on `main`
  cannot tell you.
- **Look up the signature.** The `reference-langchain` MCP server exposes
  `search_api` and `get_symbol` over reference.langchain.com. Right for "what
  are the parameters of X", not for "what does X do at runtime".

## Step 2. Know which repository owns the claim

| Product | Repository | Where to look |
|---------|------------|---------------|
| LangChain | [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | `libs/langchain_v1/langchain/` for v1, `libs/core/` for core, `libs/partners/` for provider packages |
| LangGraph | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | `libs/langgraph/`, `libs/prebuilt/`, `libs/checkpoint*/`, `libs/cli/`, `libs/sdk-py/` and `libs/sdk-js/` |
| Deep Agents | [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | Also the source of the eval matrix the docs publish |
| LangSmith SDK | [langchain-ai/langsmith-python](https://github.com/langchain-ai/langsmith-python) and [langchain-ai/langsmith-javascript](https://github.com/langchain-ai/langsmith-javascript) | The Python and JavaScript client libraries |
| LangSmith platform | langchain-ai/langchainplus (private) | `smith-backend/` (Python API), `smith-go/` (Go services), `smith-frontend/` (UI labels and flows), `host-backend/`, `lc_config/` for settings and their defaults |
| Agent Server | langchain-ai/langchainplus (private), under `langgraph-api/` | Not in the OSS langgraph repo. Also the source of the Agent Server OpenAPI spec PRs |
| Helm charts | [langchain-ai/helm](https://github.com/langchain-ai/helm) | `charts/langsmith/values.yaml` for defaults, `templates/_helpers.tpl` for the value-to-environment-variable mapping |
| OpenEvals | [langchain-ai/openevals](https://github.com/langchain-ai/openevals) | Prebuilt evaluators |

Three traps worth naming:

- **A private repo is still readable through `gh`.** `gh api` works on
  langchainplus with the usual credentials. GitHub code search is unreliable on
  a repo that size, so fall back to the git trees API and fetch a path directly.
  Anything you read there is private evidence: keep it out of public text. See
  [Private evidence](#private-evidence).
- **langchain-ai/deployments and langchain-ai/langgraph-api are archived.**
  Their content moved into langchainplus. A skill, script, or note that still
  points at either one is stale.
- **An Agent Server change can ship in two release lines.** Releases are tagged
  `langgraph-api==<version>`. `main` carries the next minor version, and a fix
  cherry-picked onto the `langgraph-api/rc` branch ships one version earlier.
  To confirm a release includes a change, compare the PR's merge commit with
  the tag: `gh api "repos/langchain-ai/langchainplus/compare/<sha>...langgraph-api%3D%3D<version>" --jq .status`
  returns `ahead` or `identical` when the tag contains it.

A self-hosted LangSmith claim usually spans two repositories: the chart sets a
value, and the backend decides what to do with it. Check both before describing
precedence, because the chart alone does not tell you which setting wins.

## Step 3. Verify the claim, not the sentence

Read the code path that produces the behavior, rather than a name that sounds
like it. Three failures that recur:

- **A resolution order inferred from a settings table.** Find the query or the
  conditional that picks a value. An `ORDER BY`, a `COALESCE`, or an `or`
  expression is the precedence; a list of configurable fields is not.
- **A defensive pattern copied from another sample.** Check whether the guarded
  case can occur. If the constructor only builds an object when a field is
  present, a `.get` with a default is documenting a state that never exists.
- **A paraphrase verified instead of the literal.** When the page shows a JSON
  body, a resource name, an environment variable value, or a CLI output, check
  that exact text. A matching error message does not verify the shape of the
  body around it. A Helm-derived name or URL comes from the template, so read
  `_helpers.tpl` for every value it interpolates, such as the release name and
  port.
- **A claim inside a language fence checked for one language only.** Text
  outside `:::python` and `:::js` fences ships in both builds. Check it against
  both the Python and TypeScript packages. ASGI transport, for example, exists
  only in Python.
- **A UI label assumed from the docs.** Labels live in `smith-frontend`
  component source. Read the component and compare the button, field, and tab
  names the page quotes. Report a mismatch with the label as private evidence.
- **A version or model identifier from memory.** Fetch it. The repository's own
  internal consensus is evidence about the repository, not about the provider.
  For model IDs specifically, see the Model references section of `AGENTS.md`.

## Step 4. Record what you checked, and what you could not

Name the file and symbol in the pull request body, not just the conclusion. A
reviewer can then disagree with the evidence rather than with an assertion.

State the gaps in the same place. Common ones that no amount of source reading
closes:

- **A UI string built at runtime.** A static label in `smith-frontend` source
  can be checked (see Step 3). A label assembled from data, translated, or
  behind a feature flag cannot. Describe the behavior rather than quoting it.
- **The model-dependent half of a sample.** Say that CI has yet to run it.
- **A beta surface.** `langchain.mcp` and similar namespaces can move under a
  page that was accurate when written.

Writing "not verified: the visible label of this control" is a better outcome
than a confident sentence a reader discovers is wrong.

## Private evidence

This repository, its PRs, and its Actions logs are public. Source in
langchainplus, langgraph-api, or any other private repository is private.

- Do not put private file paths, symbols, code, flag names, or unreleased
  feature names in docs, commits, PR text, or review comments. Write the
  conclusion: "The default is 30 seconds, not 60 (checked against product
  source)."
- Public text may describe only behavior the change itself documents. A tool,
  option, limit, or behavior you learned from private source that the change
  does not mention stays out of public text, even with no path or name
  attached. "The product also ships a handoff tool the page omits" discloses
  an unreleased feature.
- Put the repository, path, symbol, and commit you read in a private channel,
  such as a Linear issue.

Never print private source in a CI log. Logs are public too.

## Related

`AGENTS.md` holds the rules that apply to every edit, including never
fabricating an example and testing code before publishing it. Use
`docs-code-samples` when the claim belongs in a runnable sample rather than in
prose, and `docs-review` for the style pass once the facts are settled.
