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
| API reference (auto-generated) | `reference/` — do not edit |
| Build system | `pipeline/` |
| Icon library | Tabler — https://tabler.io/icons |
| Mintlify components | https://mintlify.com/docs/components |
| Mintlify MCP server | `npx add-mcp https://www.mintlify.com/docs/mcp` |

## Repository structure

```txt
docs/
├── src/                        # All manually authored content
│   ├── docs.json               # Mintlify config + navigation (88KB)
│   ├── index.mdx               # Home page
│   ├── style.css               # Custom CSS
│   ├── langsmith/              # LangSmith product docs (~324 MDX files)
│   ├── oss/                    # Open source docs (~1800 MDX files)
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
├── reference/                  # Auto-generated API reference — do not edit
├── build/                      # Build output — do not edit
├── scripts/                    # Helper utilities
└── tests/                      # Pipeline tests
```

## Navigation map

Navigation is defined in `src/docs.json`. The site has 4 products. When adding pages, find the correct product/tab/group below, then update the matching section in `docs.json`.

### Home

Single page (`src/index.mdx`). No tabs.

### LangSmith (`src/langsmith/`)

7 tabs, all files in `src/langsmith/`:

| Tab | Groups | Key files/directories |
|-----|--------|----------------------|
| Get started | Account administration (Workspace setup, Users & access control, Billing & usage), Tools, Additional resources (Data & compliance, FAQ) | `home.mdx`, `create-account-api-key.mdx`, `rbac.mdx`, `abac.mdx` |
| Observability | Tracing setup (Integrations, Manual instrumentation), Configuration & troubleshooting, Viewing & managing traces, Automations, Feedback & evaluation, Monitoring & alerting, Data type reference | `tracing/`, `observability/` |
| Evaluation | Datasets, Set up evaluations (Run, Types, Frameworks, Techniques, Tutorials), Analyze experiment results, Annotation & human feedback | `evaluation/` |
| Prompt engineering | Create and update prompts, Tutorials | `prompt-engineering/` |
| Agent deployment | Configure app, Deployment guides, App development, Studio, Auth & access control, Server customization | `agent-deployment/` |
| Platform setup | Overview, Hybrid, Self-hosted (by cloud provider, Setup guides, Enable features, Configuration, External services, Auth, Observability, Scripts) | `self-hosted/`, `self-hosted-changelog.mdx` |
| Reference | LangSmith Deployment (Agent Server API, Control Plane API), Releases | `reference/` |

### Agent Builder (`src/langsmith/`)

Flat groups (no tabs), files in `src/langsmith/agent-builder/`:

- Get started
- Tools and integrations
- Advanced
- Additional resources

### Open source (`src/oss/`)

2 language dropdowns (Python, TypeScript), each with 7 identical tabs:

| Tab | Directory | Notes |
|-----|-----------|-------|
| Deep Agents | `src/oss/deepagents/` | Get started, Core capabilities, Streaming, Protocols, CLI |
| LangChain | `src/oss/langchain/` | Get started, Core components, Middleware, Advanced usage, Multi-agent |
| LangGraph | `src/oss/langgraph/` | Get started, Capabilities, Production, Graph API, Functional API |
| Integrations | `src/oss/python/integrations/` or `src/oss/javascript/integrations/` | Per-provider pages |
| Learn | `src/oss/` (various) | Tutorials, Conceptual overviews |
| Reference | `reference/` | Auto-generated — do not edit |
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
- Use excessive bold/italics in body text
- Include "key features" lists
- Use horizontal lines

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

## Pull requests

- Explain the "why" of changes
- Highlight areas needing careful review
- Disclose AI agent involvement in description
