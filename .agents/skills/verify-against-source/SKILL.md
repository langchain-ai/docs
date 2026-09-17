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
- **Read the library source.** `gh api repos/langchain-ai/<repo>/contents/<path>
  --jq '.content' | base64 -d`, or `gh api "search/code?q=<symbol>+repo:langchain-ai/<repo>"`
  to locate the file first. Settles what a type is, what a default is, and which
  branch actually runs.
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
| LangSmith SDK | [langchain-ai/langsmith-sdk](https://github.com/langchain-ai/langsmith-sdk) | The client libraries, public |
| LangSmith platform | langchain-ai/langchainplus (private) | `smith-backend/` (Python API), `smith-go/` (Go services), `smith-frontend/` (UI labels and flows), `host-backend/`, `lc_config/` for settings and their defaults |
| Agent Server | langchain-ai/langgraph-api (private) | Not in the OSS langgraph repo. Also the source of the Agent Server OpenAPI spec PRs |
| Helm charts | [langchain-ai/helm](https://github.com/langchain-ai/helm) | `charts/langsmith/values.yaml` for defaults, `templates/_helpers.tpl` for the value-to-environment-variable mapping |
| OpenEvals | [langchain-ai/openevals](https://github.com/langchain-ai/openevals) | Prebuilt evaluators |

Two traps worth naming:

- **A private repo is still readable through `gh`.** `gh api` works on
  langchainplus and langgraph-api with the usual credentials. GitHub code search
  is unreliable on the larger ones, so fall back to the git trees API and fetch
  a path directly.
- **langchain-ai/deployments is archived.** Its GitOps content moved into
  langchainplus. A skill, script, or note that still points at it is stale.

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
- **A version or model identifier from memory.** Fetch it. The repository's own
  internal consensus is evidence about the repository, not about the provider.
  For model IDs specifically, see the Model references section of `AGENTS.md`.

## Step 4. Record what you checked, and what you could not

Name the file and symbol in the pull request body, not just the conclusion. A
reviewer can then disagree with the evidence rather than with an assertion.

State the gaps in the same place. Common ones that no amount of source reading
closes:

- **A UI string.** Source gives you a field and a component; only the running
  product gives you the rendered label. Describe the behavior rather than
  quoting a label you have not seen.
- **The model-dependent half of a sample.** Say that CI has yet to run it.
- **A beta surface.** `langchain.mcp` and similar namespaces can move under a
  page that was accurate when written.

Writing "not verified: the visible label of this control" is a better outcome
than a confident sentence a reader discovers is wrong.

## Related

`AGENTS.md` holds the rules that apply to every edit, including never
fabricating an example and testing code before publishing it. Use
`docs-code-samples` when the claim belongs in a runnable sample rather than in
prose, and `docs-review` for the style pass once the facts are settled.
