> **Keep in sync:** `AGENTS.md` and `CLAUDE.md` contain identical guidelines. If you update one, update the other.
>
> Four files derive from this one, for agents that do not read `CLAUDE.md` or `AGENTS.md`. When you change a section listed below, update its copies in the same PR:
>
> - **Style guide** (through Product and feature name capitalization) is mirrored verbatim in `.cursor/rules/docs-style.mdc` and `.github/instructions/docs-style.instructions.md`. Both are path-scoped to `src/**/*.mdx`, so they load only when a page is edited.
> - **Critical rules, Repository structure, Quick reference, Frontmatter, and Syntax** are summarized in `.cursorrules` and `.github/copilot-instructions.md`.

# LangChain Documentation Guidelines

Documentation for LangChain products hosted on Mintlify. These guidelines apply to manually authored content under `src/`, not Mintlify `build/` output.

## Critical rules

1. **Always ask for clarification** rather than making assumptions
2. **Never fabricate** examples, JSON snippets, policy details, or use case descriptions — use only content from the user or existing source files
3. **Never use markdown in frontmatter `description`** — breaks SEO
4. **Never edit `build/`** — Mintlify build output (regenerate with `make build` or `make dev`)
5. **Always update `src/docs.json`** when adding new pages
6. **Use Tabler icons only** — not FontAwesome
7. **Test code examples** before including them

## Quick reference

| What | Where/How |
|------|-----------|
| LangSmith docs | `src/langsmith/` |
| Open source docs | `src/oss/` (LangChain, LangGraph, Deep Agents) |
| Python integrations | `src/oss/python/integrations/` |
| JS integrations | `src/oss/javascript/integrations/` |
| Reusable snippets | `src/snippets/` |
| Images | `src/images/` |
| Provider icons | `src/images/providers/` |
| Navigation config | `src/docs.json` |
| Build system | `pipeline/` |
| Icon library | Tabler — <https://tabler.io/icons> |
| Mintlify components | <https://mintlify.com/docs/components> |
| API reference site | [reference.langchain.com](https://reference.langchain.com/python/) — built outside this repo; [report reference docs issues](https://github.com/langchain-ai/docs/issues/new?template=04-reference-docs.yml) |
| Mintlify MCP server | `npx add-mcp https://www.mintlify.com/docs/mcp` |

## Project structure

This project uses Mintlify for documentation. Key files: `src/docs.json` (navigation + site config), MDX files with YAML frontmatter for page metadata. When making multi-file docs changes, always update `src/docs.json` navigation and any redirect mappings. Custom CSS lives in `src/style.css`.

```txt
docs/
├── src/                        # All manually authored content
│   ├── docs.json               # Mintlify config + navigation
│   ├── index.mdx               # Home page
│   ├── style.css               # Custom CSS
│   ├── langsmith/              # LangSmith product docs
│   │   └── fleet/              #   Fleet (nav label: "No-code agents")
│   ├── oss/                    # Open source docs
│   │   ├── langchain/          #   LangChain framework
│   │   ├── langgraph/          #   LangGraph framework
│   │   ├── deepagents/         #   Deep Agents
│   │   │   └── code/           #     Deep Agents Code (unversioned, no language split)
│   │   ├── openwiki/           #   OpenWiki (unversioned, no language split)
│   │   ├── python/             #   Python-specific (integrations, migrations, releases)
│   │   ├── javascript/         #   TypeScript-specific (integrations, migrations, releases)
│   │   ├── integrations/       #   Shared integration content
│   │   ├── concepts/           #   Conceptual overviews
│   │   ├── contributing/       #   Contribution guides
│   │   └── reference/          #   Reference tab entry pages (link to reference.langchain.com)
│   ├── snippets/               # Reusable MDX snippets
│   │   ├── langsmith/          #   LangSmith snippets
│   │   ├── oss/                #   OSS snippets
│   │   └── code-samples/       #   Embedded code samples
│   ├── images/                 # Documentation images
│   │   ├── brand/              #   Logos, favicons
│   │   └── providers/          #   Provider icons (dark/ and light/ variants)
│   ├── code-samples/           # Testable standalone code samples (see make test-code-samples)
│   └── fonts/                  # TWK Lausanne font files
├── pipeline/                   # Python build system & preprocessors
├── build/                      # Build output — do not edit
├── scripts/                    # Helper utilities and automation scripts
└── tests/                      # Pipeline tests
```

## Navigation map

Navigation is defined in `src/docs.json`. The site has 2 products, each a `menu` of items rather than a flat tab list. When adding pages, find the correct product → menu item → tab → group below, then update the matching section in `docs.json`.

Product and menu names in `docs.json` do not match source directory names. Lifecycle stages mix LangSmith and OSS content: the Build menu draws from both `src/oss/` and `src/langsmith/`, and Test, Deploy, and Monitor all draw from `src/langsmith/`. Locate pages by directory, not by product name.

### AGENT DEVELOPMENT LIFECYCLE

Five menu items: Home, Build, Test, Deploy, Monitor.

#### Home

Single page (`src/index.mdx`).

#### Build

Two language dropdowns (Python, TypeScript) with the same 10 tabs each. Most content is language-versioned from `src/oss/`; two tabs are exceptions.

| Tab | Source | Groups |
|-----|--------|--------|
| Overview | `src/build-overview.mdx` | Single page |
| Deep Agents | `src/oss/deepagents/` | Get started, Deployment (Going to production), Execution environment, Context management, Delegation, Steering, Frontend (Patterns), Protocols |
| Managed Deep Agents | `src/langsmith/managed-deep-agents*.mdx` | Get started, Agent definition (Channels), Build and deploy |
| LangChain | `src/oss/langchain/` | Get started, Core components, Middleware, Frontend (Patterns → Generative UI, Integrations), Advanced usage (Multi-agent), Agent development (Test), Production |
| LangGraph | `src/oss/langgraph/` | Get started, Capabilities, Production, Frontend, LangGraph APIs (Graph API, Functional API) |
| OpenWiki | `src/oss/openwiki/` | Modes, Integrations, Visualize, CLI reference, Customize, Providers, Automate updates, Changelog |
| Integrations | `src/oss/python/integrations/` or `src/oss/javascript/integrations/` | Python: Popular Providers, Integrations by component. TypeScript: Popular Providers (OpenAI, Anthropic, Google, AWS, Microsoft), General integrations, RAG integrations |
| Learn | `src/oss/` (various) | Tutorials (Deep Agents, LangChain, Multi-agent, LangGraph), Conceptual overviews, Additional resources. TypeScript adds LangChain Academy |
| Reference | `src/oss/reference/` | Reference, Releases (Releases, Migration guides), Policies — short entry pages linking to reference.langchain.com |
| Contribute | `src/oss/contributing/` | Contribute (Integrations) |

Two Build tabs are not language-versioned in the usual way:

- **Managed Deep Agents** lives in `src/langsmith/`, not `src/oss/`. Files named `managed-deep-agents*.mdx` emit only language-prefixed routes (`/langsmith/python/...` and `/langsmith/javascript/...`). The unversioned `/langsmith/managed-deep-agents*` URLs redirect to the Python routes via `docs.json`.
- **OpenWiki** ships one set of pages at `/oss/openwiki/...` with no language split. Conditional fences resolve against the Python branch.

#### Test

Six tabs, all files flat in `src/langsmith/`:

| Tab | Groups |
|-----|--------|
| Get started | No groups |
| Datasets & Experiments | Datasets (Create a dataset), Run an evaluation, Evaluation techniques (Define evaluation target, Scoring methods, Experiment configuration, Multimodal evaluations), Analyze experiment results, Tutorials, Common data types |
| Evaluators | Evaluator types (UI, SDK), Frameworks & integrations, Improve evaluators |
| Annotation Queues | Feedback |
| Test from Playground | No groups |
| Test from Studio | No groups |

#### Deploy

Six tabs, all files flat in `src/langsmith/`:

| Tab | Groups |
|-----|--------|
| Get started | Deployment components, Develop & test, Frameworks and platforms (Full-stack web apps), Reference (Agent Server API, Control Plane API, Related) |
| Agent Server | Develop your application (Set up dependencies, Persistence), Capabilities (Assistants, Runs, Double-texting), How to build, Auth & access control (Custom auth tutorial), Server customization (Replace built-in backends, Extend the HTTP server, Headers and logging) |
| Deploy to Cloud | Deployment guide, Reference |
| Deploy to Self-hosted | Configure, Reference |
| Prompt & Context Hub | Prompts (Create and manage prompts, Connect to models), Context Hub, Tutorials |
| Sandboxes | No groups |

The Get started tab's Reference group holds two OpenAPI-generated sections. See [Reference docs](#reference-docs) below.

#### Monitor

Five tabs, all files flat in `src/langsmith/`:

| Tab | Groups |
|-----|--------|
| Overview | Single page |
| Trace | Tracing setup (Integrations → LLM providers, Agent frameworks, Voice AI frameworks, Developer tools; Manual instrumentation), Configuration & troubleshooting (Project & environment settings, Advanced tracing techniques, Data & privacy, Troubleshooting guides) |
| Debug | Viewing & managing traces, Bulk export trace data, Messages view, Data type reference |
| Observe | Monitoring & alerting, Online evaluators, Automations |
| Reference | SmithDB SDK migration, LangSmith REST API |

The Reference tab's LangSmith REST API group is OpenAPI-generated. See [Reference docs](#reference-docs) below.

### PRODUCTS AND SETUP

Five menu items. Only LangSmith setup has tabs; the rest are flat group lists.

#### LangSmith setup

Six tabs, all files flat in `src/langsmith/`:

| Tab | Groups |
|-----|--------|
| Overview | Single page |
| Account | Billing & usage |
| Cloud | Reference |
| BYOC | No groups |
| Self-hosted | Get started by cloud provider, Deploy with Terraform (AWS, GCP, Azure), Setup guides (Manage an installation), Configuration, Connect external services, Platform auth & access control, Self-hosted observability, Hybrid, Scripts, Reference |
| Govern | Organization (Workspace setup), Users & access control, Tools, Auditing, Data & compliance, Additional resources (FAQ) |

#### Other menu items

| Menu item | Source | Groups |
|-----------|--------|--------|
| LLM Gateway | `src/langsmith/llm-gateway*.mdx` | Core capabilities, Administration and governance, Advanced |
| No-code agents | `src/langsmith/fleet/` | Get started, Configure, Tools and automation, Advanced, Additional resources |
| Engine | `src/langsmith/engine*.mdx` | No groups |
| Deep Agents Code | `src/oss/deepagents/code/` | Configuration |

"No-code agents" is the nav label for Fleet. The source directory and URLs still use `fleet`.

"Deep Agents Code" ships one set of pages at `/oss/deepagents/code/...` with no language split, even though it sits under `src/oss/deepagents/`. Conditional fences resolve against the Python branch.

### Source directory summary

Because nav names and directories diverge, use this to go from a file to its place in the nav:

| Source | Appears under |
|--------|---------------|
| `src/index.mdx` | Lifecycle → Home |
| `src/oss/deepagents/` (except `code/`) | Build → Deep Agents |
| `src/oss/deepagents/code/` | Products and setup → Deep Agents Code |
| `src/oss/langchain/` | Build → LangChain |
| `src/oss/langgraph/` | Build → LangGraph |
| `src/oss/openwiki/` | Build → OpenWiki |
| `src/oss/{python,javascript}/integrations/` | Build → Integrations |
| `src/oss/reference/` | Build → Reference |
| `src/oss/contributing/` | Build → Contribute |
| `src/langsmith/managed-deep-agents*.mdx` | Build → Managed Deep Agents |
| `src/langsmith/fleet/` | Products and setup → No-code agents |
| `src/langsmith/*.mdx` (everything else) | Test, Deploy, Monitor, or LangSmith setup, depending on subject |

### Reference docs

Three OpenAPI-generated sections. Mintlify generates the endpoint pages at deploy time, so they do not exist in the local `build/` output — `make broken-links` filters them as false positives.

| Section | Nav location | Spec source | Generated under |
|---------|--------------|-------------|-----------------|
| Agent Server API | Deploy → Get started → Reference | `src/langsmith/agent-server-openapi.json` (committed) | `/langsmith/agent-server-api/` |
| Control Plane API | Deploy → Get started → Reference | `https://api.host.langchain.com/openapi.json` (fetched at deploy time, no local file) | `/api-reference/` |
| LangSmith REST API | Monitor → Reference | `src/langsmith/langsmith-platform-openapi.json` (committed) | `/langsmith/smith-api/` |

`src/langsmith/langsmith-platform-openapi.json` is refreshed daily by `.github/workflows/refresh-langsmith-openapi.yml`, which runs `scripts/process_langsmith_openapi.py` and opens or appends to a standing `chore/refresh-langsmith-openapi` PR. Do not edit it by hand.

`src/langsmith/agent-server-openapi.json` is updated by PRs from the `langgraph-api` repository, titled `Update Agent ServerOpenAPI spec for API version X.Y.Z`. Validate either spec with `make check-openapi`.

## Local development

See [Contributing to documentation](/oss/contributing/documentation) for setup instructions.

### Command-line tools

Two distinct binaries drive local work. Do not assume `mint` is the only command just because the `Makefile` targets shell out to it: `docs` is a first-class, preferred entry point installed separately via Python:

- **`docs`**: The primary CLI, a Python console script (`docs = "pipeline.cli:main"` in `pyproject.toml`) installed into the virtualenv by `uv sync` (the first step of `make install`). Provides `docs dev`, `docs build`, `docs migrate`, and `docs mv`. The `make` targets wrap this CLI. If `docs` is not found after `make install`, relaunch your shell (or activate the venv) so `.venv/bin/docs` lands on `PATH`.
- **`mint`**: Mintlify's CLI, a separate global npm binary (`npm install -g mint@latest`). The build targets shell out to it for `mint dev`, `mint broken-links`, and `mint export`.

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

### Version-added admonitions

When documenting new features, APIs, or behavior that requires a minimum package or CLI version, add a version-added admonition near the first mention of the feature. Use a `<Note>` callout with a concise requirement, for example: `Feature name requires \`package>=x.y.z\`.`

For language-specific requirements, wrap the note in the relevant `:::python` or `:::js` fence. Include separate notes when Python and TypeScript packages have different minimum versions.

## Mermaid diagram styling

Use these `classDef` colors (from LangChain brand palette) for all mermaid diagrams. See `.github/brand-guidelines.md` for the full brand color reference.

| Role | classDef value |
|------|---------------|
| **process** (blue) | `fill:#E5F4FF,stroke:#006DDD,stroke-width:2px,color:#030710` |
| **trigger** (green) | `fill:#F6FFDB,stroke:#6E8900,stroke-width:2px,color:#2E3900` |
| **decision** (purple) | `fill:#FDF3FF,stroke:#7E65AE,stroke-width:2px,color:#504B5F` |
| **output** (plum) | `fill:#EBD0F0,stroke:#885270,stroke-width:2px,color:#441E33` |
| **alert** (peach) | `fill:#F8E8E6,stroke:#B27D75,stroke-width:2px,color:#634643` |
| **neutral** (muted blue) | `fill:#F2FAFF,stroke:#40668D,stroke-width:2px,color:#2F4B68` |

When using `%%{init}%%` theme variables, use: `lineColor:'#40668D'`, `primaryColor:'#E5F4FF'`, `primaryTextColor:'#030710'`, `primaryBorderColor:'#006DDD'`.

Do not use Tailwind default colors, Material Design colors, or other off-brand palettes in mermaid diagrams.

## Style guide

Follow [Google Developer Documentation Style Guide](https://developers.google.com/style).

**Do:**

- Match existing conventions in the file you are editing — do not restructure, combine, or split pages unless explicitly asked
- Reference existing pages for style patterns when creating new content
- Be concise — cut filler words and wordy phrases ("to" not "in order to", "because" not "due to the fact that", "can" not "has the ability to")
- Second-person imperative present tense ("Run the following code…")
- Active voice ("The function returns a list" not "A list is returned by the function")
- Sentence-case headings starting with active verb, not gerund ("Add a tool" not "Adding a tool")
- American English spelling
- Oxford commas in lists ("traces, datasets, and experiments")
- Descriptive link text ("[View the tracing docs](/langsmith/tracing)" not "click [this link](/langsmith/tracing)")
- Add cross-links where applicable
- Use `@[ClassName]` link map for API references
- Use `:::python`/`:::js` fencing on OSS docs
- Language tags on all code blocks (use actual language, not `output`)
- Sort imports in all code snippets (stdlib, third-party, local)
- Use `.content_blocks` instead of `.content` when accessing message content in LangChain code snippets
- Test code examples and links before publishing

**Don't:**

- Skip frontmatter
- Use absolute URLs for internal links
- Use markdown in description fields
- Use `/python/` or `/javascript/` in links (resolved by build pipeline)
- Use model aliases — use full identifiers (e.g., `claude-sonnet-4-6`)
- Use FontAwesome icon names
- Use nested double quotes in component attributes — use `default="['a', 'b']"` not `default='["a", "b"]'`
- Use contractions ("do not" not "don't", "cannot" not "can't", "it is" not "it's")
- Use first person ("we", "I", "our", "let's") — write in second person or use the product name as subject
- Use future tense ("The function returns X" not "The function will return X")
- Use weasel words or filler (avoid "simply", "easily", "just", "very", "basically", "obviously")
- Use H5 or H6 headings
- Start headings with articles ("Add a tool" not "The tool setup guide")
- Use em dashes — prefer commas, colons, or separate sentences instead. Only use an em dash when no alternative reads naturally
- Add spaces around em dashes — write `word—word` not `word — word` (`make lint_prose` enforces this)
- Use excessive bold/italics in body text
- Start bulleted list items with a lowercase letter — always capitalize the first word
- Include "key features" lists
- Use horizontal lines (`---`) to separate sections — use headings instead
- Apply bold to UI element names unless existing docs already do so
- Misspell product names — use "prebuilt" (not "pre-built"), "Deep Agents" (not "DeepAgents"), "PyPI" (not "PyPi"), "URL" (not "url")
- Skip `make lint_prose` — always run it on changed files before committing and fix all violations

### Structure conventions

Match these patterns, drawn from established pages, when authoring new content:

- **Open with definition, then benefit, then task** — start a section (and the page) with a one-sentence statement of what the feature is or does, follow with a sentence on what it enables for the reader, then give the procedure or detail. When a page has a sibling variant (for example, a paid or self-hosted version), link it in the opening lines.
- **Introduce procedures with a colon lead-in** — precede steps with a phrase such as "To add a channel:", then a numbered list (or the `<Steps>` component) of imperative steps. State a step's result as a follow-on line when it matters ("The Add User modal displays."). Flag optional steps inline with "(Optional)". For long, multi-stage tasks, use `### Step N. <verb>` headings.
- **Use bold-led definition lists for options** — for parameters, permissions, secrets, or enumerated types, write `- **Term**: Explanation.` and end each explanation with a period.
- **Link on first mention, and point forward at section ends** — link a feature, class, or term on first mention only, not on repeats. Two pointer forms are established, and neither is canonical, so do not mass-convert one into the other. Use the long form ("For more information, see [Page](/path)") at section ends and for standalone pointers. Use the short form ("See [Page](/path)") where the pointer trails an already-complete thought, such as an FAQ answer or a table cell, and especially in a run where nearly every item ends in a pointer. Close substantial pages with a `## See also` list of related links.
- **State requirements and constraints up front** — put permission, plan tier, or preview requirements before the steps they govern ("Adding MCP servers requires admin permissions."). Write hard constraints as plain facts ("Once an agent identity is set, it cannot be changed.").

### Model references

Always use the latest generally available (GA) models when referencing LLMs in docstrings and illustrative code snippets. Avoid preview or beta identifiers unless the model has no GA equivalent. Outdated model names signal stale code and confuse users.

Before writing or updating model references, verify current model IDs against the provider's official docs. Do not rely on memorized or cached model names — they go stale quickly.

### Release stage names

LangSmith ships features through three release stages: alpha, beta, and generally available (GA). See [Release stages](/langsmith/release-stages) for what each stage means.

These are common nouns, not proper nouns. Write them lowercase in prose, including parenthetical and inline status markers:

- Lowercase mid-sentence and in markers: "available in beta", "is in beta", "(beta)", "the feature is in alpha".
- Capitalize only where normal sentence case requires it: the first word of a sentence or heading ("Beta is optional.", "## Beta").
- Keep the literal product UI label capitalized when quoting it as a tag: the `Beta` tag, frontmatter `tag: "Beta"`. The same applies to a stage name standing alone as a table cell's only label.
- Spell out "generally available" on first use, then use "GA". GA is always uppercase.
- Do not change code identifiers, package version identifiers (`1.0.0b1`), or literal CLI output that contains "Beta".

### Product and feature name capitalization

Capitalize a word when it refers to a **product or brand name**. Use lowercase when it refers to a **common noun** — a thing you build, an instance, or a type.

**Capitalize** product and brand names:

- LangChain, LangGraph, LangSmith, Deep Agents, Fleet, Engine

**Lowercase** common nouns (things you create, instances, or types):

- "Create a dashboard" (dashboard = a thing you build, not a product name)
- "a deep agent created using Deep Agents" (the first "deep agent" is a common noun; "Deep Agents" is the product name)
- "Run an experiment", "View your traces", "Manage your projects"
- "Build agents across the agent development lifecycle" (the lifecycle is a process, not a product; marketing materials capitalize it, docs do not)
- "LangChain provides the open agent engineering platform" (the phrase describes what LangChain provides; it is not a product name)

When in doubt, ask: is this word the product's proper name, or is it describing a thing the user creates or works with? If the latter, use lowercase.

Spell out "agent development lifecycle" in prose. Do not use the "ADLC" acronym, which appears in marketing materials but not in the documentation.

Reserve "the platform" for LangSmith. LangChain is the open agent engineering ecosystem, not a platform. Marketing's short blurb ("an open agent engineering platform") compresses the whole company into a single noun to fit the character limits of a search result. Docs have the room to be precise, so do not carry that phrasing onto pages.

## Adding pages

1. Create MDX file with required frontmatter in the correct directory (see navigation map above)
2. Update `src/docs.json` to add the page to the correct product → tab → group
3. For new groups, include an index page: `"pages": ["group/index", "group/page"]`

### Common workflows

**Add a new LangSmith doc:**

1. Create `src/langsmith/<name>.mdx` with frontmatter
2. Decide which lifecycle stage the page belongs to, then find the matching menu item in `src/docs.json`: `navigation.products[0].menu` holds Home, Build, Test, Deploy, and Monitor; `navigation.products[1].menu` holds LangSmith setup, LLM Gateway, No-code agents, Engine, and Deep Agents Code
3. Add the page path (e.g., `"langsmith/<name>"`) to the correct group's `pages` array

**Add a new integration page (Python):**

1. Create `src/oss/python/integrations/<component>/<provider>.mdx`
2. Add the page to the component's index page (`src/oss/python/integrations/<component>/index.mdx`); only edit `src/docs.json` when creating a brand-new component group
3. Use description format: `"Integrate with the ClassName type using LangChain Python."`
4. If the provider has an overview page at `src/oss/python/integrations/providers/<provider>.mdx`, add or update a section there linking to the new page (`/oss/integrations/<component>/<provider>`)

**Add a new integration page (TypeScript):**

1. Create `src/oss/javascript/integrations/<component>/<provider>.mdx`
2. Add the page to the component's index page (`src/oss/javascript/integrations/<component>/index.mdx`); only edit `src/docs.json` when creating a brand-new component group
3. If the provider has an overview page at `src/oss/javascript/integrations/providers/<provider>.mdx`, add or update a section there linking to the new page (`/oss/integrations/<component>/<provider>`)

**Add a reusable snippet:**

1. Create `src/snippets/<product>/<name>.mdx`
2. Import it below the frontmatter of the consuming page: `import PascalCaseName from '/snippets/<product>/<name>.mdx';`
3. Render it where the content belongs: `<PascalCaseName />`

Use the import form, not Mintlify's `<Snippet file="..." />`. The build pipeline rewrites snippet imports to language-specific copies under `/snippets/{python,javascript}/` (`_rewrite_snippet_imports_for_language` in `pipeline/core/builder.py`), and that rewrite only matches `from '/snippets/...'` imports. Every snippet reference in `src/` uses the import form.

## Debugging

When investigating a bug or unexpected behavior, always start by reading the relevant code and logs before forming a hypothesis. Do not assume something is working or ask the user to confirm — verify it yourself first.

### CI broken-links failures

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

## Helper scripts

### Refresh Deep Agents eval matrix

The model-by-eval-category table on `/oss/python/deepagents/models` is generated by `scripts/refresh_deepagents_category_matrix.py`. The script pulls `category_scores` from the latest successful [Evals - GHA](https://github.com/langchain-ai/deepagents/actions/workflows/evals.yml) runs in `langchain-ai/deepagents` and writes the table to `src/snippets/deepagents-eval-category-matrix.mdx` (imported by `src/oss/deepagents/models.mdx`). Run it whenever new eval results land and the published table is out of date.

Setup and run:

```bash
export GITHUB_TOKEN="$(gh auth token)"  # needs Actions: Read on langchain-ai/deepagents; SSO-authorize for langchain-ai
uv run python scripts/refresh_deepagents_category_matrix.py --write
```

Notes:

- For the latest `(model, category)` value per cell, the script walks runs newest-first and keeps the first hit. Models with fewer than four of the six fixed categories filled are dropped (`MIN_FILLED_CATEGORIES`).
- Only models explicitly listed in `INCLUDED_MODELS` (in the script) appear in the table. To surface a new model, add its `provider:model` key there.
- The fixed columns are defined by `FIXED_CATEGORY_COLUMNS` in the script (`unit_test` is intentionally excluded).
- Without `--write`, the script prints the table to stdout for inspection.
- After regenerating, commit only `src/snippets/deepagents-eval-category-matrix.mdx`. Do not edit that snippet by hand.

## Pre-commit linting

Always run `make lint_prose` (Vale) before handing off or committing doc changes. CI blocks on it. Common offenders: em-dashes with surrounding spaces (` — ` → `—`, enforced by `LangChain.DashesSpaces`), terminology, style.

Scope to changed files for speed: `make lint_prose FILES="src/path/to/file.mdx"` (or pass space-separated paths). Run with no `FILES` arg to lint all of `src/`.

The Vale version is pinned once, in `.mise.toml`. The `Makefile`, `scripts/install-vale.sh`, and the `lint-prose` workflow all read it from there, so local runs use the same engine as CI. Bump it only in `.mise.toml`. Do not hardcode a version in any of the three call sites.

Also run `make broken-links` when adding or renaming links, pages, or nav entries.

## Changelog / Release notes

When extracting data from PRs or changelogs, use the "Release Note:" section in PR bodies, not PR titles. Always verify the data source format before processing.

## Pull requests

- Explain the "why" of changes
- Highlight areas needing careful review
- Disclose AI agent involvement in description
