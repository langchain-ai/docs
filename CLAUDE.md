> **Keep in sync:** `AGENTS.md` and `CLAUDE.md` contain identical guidelines. If you update one, update the other.

# LangChain Documentation Guidelines

Documentation for LangChain products hosted on Mintlify. These guidelines apply to manually authored docs only—not `**/reference/**` directories or build artifacts.

## Critical rules

1. **Always ask for clarification** rather than making assumptions
2. **Never use markdown in frontmatter `description`** — breaks SEO
3. **Never edit `reference/` directory** — auto-generated
4. **Always update `src/docs.json`** when adding new pages
5. **Use Tabler icons only** — not FontAwesome
6. **Test code examples** before including them

## Quick reference

| What | Where/How |
|------|-----------|
| LangSmith docs | `src/langsmith/` |
| Open source docs | `src/oss/` (LangChain, LangGraph, DeepAgents) |
| Python integrations | `src/oss/python/integrations/` |
| JS integrations | `src/oss/javascript/integrations/` |
| Reusable snippets | `src/snippets/` |
| Images | `src/images/` |
| Provider icons | `src/images/providers/` |
| Navigation config | `src/docs.json` |
| Build system | `pipeline/` |
| Icon library | Tabler — <https://tabler.io/icons> |
| Mintlify components | <https://mintlify.com/docs/components> |
| Mintlify MCP server | `npx add-mcp https://www.mintlify.com/docs/mcp` |

## Repository structure

```txt
docs/
├── src/                        # All manually authored content
│   ├── docs.json               # Mintlify config + navigation
│   ├── index.mdx               # Home page
│   ├── style.css               # Custom CSS
│   ├── langsmith/              # LangSmith product docs
│   ├── oss/                    # Open source docs
│   │   ├── langchain/          #   LangChain framework
│   │   ├── langgraph/          #   LangGraph framework
│   │   ├── deepagents/         #   Deep Agents
│   │   ├── python/             #   Python-specific (integrations, migrations, releases)
│   │   ├── javascript/         #   TypeScript-specific (integrations, migrations, releases)
│   │   ├── integrations/       #   Shared integration content
│   │   ├── concepts/           #   Conceptual overviews
│   │   └── contributing/       #   Contribution guides
│   ├── snippets/               # Reusable MDX snippets
│   │   ├── langsmith/          #   LangSmith snippets
│   │   ├── oss/                #   OSS snippets
│   │   └── code-samples/       #   Embedded code samples
│   ├── images/                 # Documentation images
│   │   ├── brand/              #   Logos, favicons
│   │   └── providers/          #   Provider icons (dark/ and light/ variants)
│   └── fonts/                  # TWK Lausanne font files
├── pipeline/                   # Python build system & preprocessors
├── build/                      # Build output — do not edit
├── scripts/                    # Helper utilities
└── tests/                      # Pipeline tests
```

## Navigation map

Navigation is defined in `src/docs.json`. The site has 4 products (Home, LangSmith, LangSmith Fleet, Open source). When adding pages, find the correct product/tab/group below, then update the matching section in `docs.json`.

### Home

Single page (`src/index.mdx`). No tabs.

### LangSmith (`src/langsmith/`)

7 tabs, all files in `src/langsmith/`:

| Tab | Groups |
|-----|--------|
| Get started | Account administration (Workspace setup, Users & access control, Billing & usage), Tools, Additional resources |
| Observability | Tracing setup, Configuration & troubleshooting, Viewing & managing traces, Automations, Feedback & evaluation, Monitoring & alerting, Data type reference |
| Evaluation | Datasets, Set up evaluations, Analyze experiment results, Annotation & human feedback, Common data types |
| Prompt engineering | Create and update prompts, Tutorials |
| Agent deployment | Agent server, Core capabilities, Develop agents, Deployment guides, Studio, Auth & access control, Server customization |
| Platform setup | Overview, Hybrid, Self-hosted (by cloud provider, Setup guides, Enable features, Configuration, External services, Auth, Observability, Scripts) |
| Reference | LangSmith Deployment (Agent Server API, Control Plane API), Releases |

All LangSmith files are flat in `src/langsmith/` (no per-tab subdirectories except `fleet/` and `images/`).

### LangSmith Fleet (`src/langsmith/fleet/`)

Flat groups (no tabs):

- Get started
- Configure
- Tools and automation
- Advanced
- Additional resources

### Open source (`src/oss/`)

2 language dropdowns (Python, TypeScript), each with 7 tabs sharing the same names. Groups listed below are for the Python dropdown; TypeScript groups differ in some tabs (noted with *).

| Tab | Directory | Groups |
|-----|-----------|--------|
| Deep Agents | `src/oss/deepagents/` | Get started, Deployment, Core capabilities, Frontend, Protocols, Command line interface |
| LangChain | `src/oss/langchain/` | Get started, Core components, Middleware, Frontend, Advanced usage, Agent development, Deploy with LangSmith |
| LangGraph | `src/oss/langgraph/` | Get started, Capabilities, Production, Frontend, LangGraph APIs |
| Integrations* | `src/oss/python/integrations/` or `src/oss/javascript/integrations/` | Popular Providers, Integrations by component (TS: "General integrations, RAG integrations") |
| Learn* | `src/oss/` (various) | Tutorials, Conceptual overviews, Additional resources (TS adds: "LangChain Academy") |
| Reference | `src/oss/reference/` | Reference, Errors, Releases, Policies — auto-generated, do not edit |
| Contribute | `src/oss/contributing/` | Contribution guides, integration authoring |

## Local development

See [Contributing to documentation](/oss/contributing/documentation) for setup instructions.

## Frontmatter

Every MDX file requires:

```yaml
---
title: Clear, concise page title
description: SEO summary — no markdown allowed (no links, backticks, formatting)
---
```

**Integration page descriptions:** `"Integrate with the ClassName type using LangChain Python."`

- Example: `"Integrate with the ChatOpenAI chat model using LangChain Python."`

## Syntax

### Language-specific content

Use `:::python` or `:::js` fences for language-specific content. Pages with these fences generate separate Python and JavaScript versions.

```txt
:::python
Python-only content here
:::
```

### Code highlighting

```python
highlighted = True  # [!code highlight]
added = True        # [!code ++]
removed = True      # [!code --]
```

### API reference links

Use `@[ClassName]` to auto-link to API docs. Defined in `pipeline/preprocessors/link_map.py`.

**Use for:** First mention of SDK classes/methods (`@[ChatOpenAI]`, `@[StateGraph]`, `@[create_agent]`)

**Don't use for:** Repeated mentions, general concepts, or when a descriptive link is clearer

## Assets

**Images:** Store in `src/images/`. Use descriptive filenames and alt text.

**Icons:** Use Tabler names only (`icon="home"`, `icon="brand-github"`). For missing icons, use SVG path: `icon="/images/providers/name.svg"`

Common Tabler names: `home` (not house), `tool` (not wrench), `player-play` (not play), `bulb` (not lightbulb), `alert-triangle` (not exclamation-triangle)

## Components

| Component | Use for |
|-----------|---------|
| `<Tabs>` / `<Tab>` | Python/JS examples |
| `<Steps>` / `<Step>` | Numbered instructions |
| `<Accordion>` | Collapsible content |
| `<CodeGroup>` | Tabbed code blocks |
| `<Card>` / `<CardGroup>` | Navigation/overview links only (not for highlighting points) |
| `<Note>`, `<Tip>`, `<Warning>`, `<Info>` | Callouts |

## Style guide

Follow [Google Developer Documentation Style Guide](https://developers.google.com/style).

**Do:**

- Reference existing pages for style patterns when creating new content
- Be concise — no hyperbolic or redundant language
- Second-person imperative present tense ("Run the following code…")
- Sentence-case headings starting with active verb, not gerund ("Add a tool" not "Adding a tool")
- American English spelling
- Add cross-links where applicable
- Use `@[ClassName]` link map for API references
- Use `:::python`/`:::js` fencing on OSS docs
- Language tags on all code blocks (use actual language, not `output`)
- Sort imports in all code snippets (stdlib, third-party, local)
- Test code examples and links before publishing

**Don't:**

- Skip frontmatter
- Use absolute URLs for internal links
- Use markdown in description fields
- Use `/python/` or `/javascript/` in links (resolved by build pipeline)
- Use model aliases — use full identifiers (e.g., `claude-sonnet-4-6`)
- Use FontAwesome icon names
- Use nested double quotes in component attributes — use `default="['a', 'b']"` not `default='["a", "b"]'`
- Use H5 or H6 headings
- Overuse em dashes — prefer commas, colons, or separate sentences instead
- Do not add spaces around em dashes — write `word—word` not `word — word` (Vale enforces this)
- Use excessive bold/italics in body text
- Include "key features" lists
- Use horizontal lines

### Model references

Always use the latest generally available (GA) models when referencing LLMs in docstrings and illustrative code snippets. Avoid preview or beta identifiers unless the model has no GA equivalent. Outdated model names signal stale code and confuse users.

Before writing or updating model references, verify current model IDs against the provider's official docs. Do not rely on memorized or cached model names — they go stale quickly.

## Adding pages

1. Create MDX file with required frontmatter in the correct directory (see navigation map above)
2. Update `src/docs.json` to add the page to the correct product → tab → group
3. For new groups, include an index page: `"pages": ["group/index", "group/page"]`

### Common workflows

**Add a new LangSmith doc:**

1. Create `src/langsmith/<name>.mdx` with frontmatter
2. Find the correct tab and group in `src/docs.json` under `navigation.products[1]` (LangSmith)
3. Add the page path (e.g., `"langsmith/<name>"`) to that group's `pages` array

**Add a new integration page (Python):**

1. Create `src/oss/python/integrations/<provider>/<component>.mdx`
2. Add to `src/docs.json` under Open source → Python dropdown → Integrations tab
3. Use description format: `"Integrate with the ClassName type using LangChain Python."`

**Add a new integration page (TypeScript):**

1. Create `src/oss/javascript/integrations/<provider>/<component>.mdx`
2. Add to `src/docs.json` under Open source → TypeScript dropdown → Integrations tab

**Add a reusable snippet:**

1. Create `src/snippets/<product>/<name>.mdx`
2. Reference with `<Snippet file="<product>/<name>.mdx" />`

## Debugging CI broken-links failures

`make broken-links` runs `mint broken-links` then filters known false positives (OpenAPI-generated pages: `/langsmith/agent-server-api/`, `/api-reference/`, `../langchain/agents`). Output format:

```txt
found N broken links in M files

some-file.mdx                    ← file header (always printed)
 ⎿  /path/to/broken-target       ← indented = actual broken link

another-file.mdx                 ← no indented lines = all its links were filtered out (false positive)
```

**Shortcut:** Skip straight to `⎿` lines — those are the only real failures. File headers without `⎿` lines beneath them are OpenAPI pages that exist at deploy time but not locally.

**Common cause:** Page renamed/deleted but link and/or `src/docs.json` nav entry still references old name. Fix both the link in the MDX file AND the corresponding entry in `docs.json`.

To run locally: `make broken-links`

## Pre-commit linting

Always run `make lint_prose` (Vale) before handing off or committing doc changes. CI blocks on it. Common offenders: em-dashes with surrounding spaces (` — ` → `—`, enforced by `LangChain.DashesSpaces`), terminology, style.

Scope to changed files for speed: `make lint_prose FILES="src/path/to/file.mdx"` (or pass space-separated paths). Run with no `FILES` arg to lint all of `src/`.

Also run `make broken-links` when adding or renaming links, pages, or nav entries.

## Pull requests

- Explain the "why" of changes
- Highlight areas needing careful review
- Disclose AI agent involvement in description
