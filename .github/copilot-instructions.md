# LangChain Documentation Guidelines

Documentation for LangChain products hosted on Mintlify. These guidelines apply to manually authored docs only—not `**/reference/**` directories or build artifacts.

## Critical rules

1. **Always ask for clarification** rather than making assumptions
2. **Never use markdown in frontmatter `description`** — breaks SEO
3. **Never edit `reference/` directory** — auto-generated
4. **Always update `src/docs.json`** when adding new pages
5. **Use Tabler icons only** — not FontAwesome
6. **Test code examples** before including them

## Repository structure

```
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
│   ├── images/                 # Documentation images
│   │   ├── brand/              #   Logos, favicons
│   │   └── providers/          #   Provider icons (dark/ and light/ variants)
│   └── fonts/                  # Font files
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

| Tab | Groups |
|-----|--------|
| Get started | Account administration (Workspace setup, Users & access control, Billing & usage), Tools, Additional resources |
| Observability | Tracing setup (Integrations, Manual instrumentation), Configuration & troubleshooting, Viewing & managing traces, Automations, Feedback & evaluation, Monitoring & alerting |
| Evaluation | Datasets, Set up evaluations (Run, Types, Frameworks, Techniques, Tutorials), Analyze experiment results, Annotation & human feedback |
| Prompt engineering | Create and update prompts, Tutorials |
| Agent deployment | Configure app, Deployment guides, App development, Studio, Auth & access control, Server customization |
| Platform setup | Overview, Hybrid, Self-hosted (by cloud provider, Setup guides, Enable features, Configuration, External services, Auth) |
| Reference | LangSmith Deployment APIs, Releases |

### Agent Builder (`src/langsmith/agent-builder/`)
Flat groups (no tabs): Get started, Tools and integrations, Advanced, Additional resources

### Open source (`src/oss/`)
2 language dropdowns (Python, TypeScript), each with 7 identical tabs:

| Tab | Directory |
|-----|-----------|
| Deep Agents | `src/oss/deepagents/` |
| LangChain | `src/oss/langchain/` |
| LangGraph | `src/oss/langgraph/` |
| Integrations | `src/oss/python/integrations/` or `src/oss/javascript/integrations/` |
| Learn | `src/oss/` (various) |
| Reference | `reference/` — auto-generated, do not edit |
| Contribute | `src/oss/contributing/` |

## Quick reference

| What | Where/How |
|------|-----------|
| Navigation config | `src/docs.json` |
| Reusable snippets | `src/snippets/` |
| Provider icons | `src/images/providers/` |
| Icon library | Tabler — https://tabler.io/icons |
| Mintlify components | https://mintlify.com/docs/components |
| Auto-link syntax | `@[ClassName]` — defined in `pipeline/preprocessors/link_map.py` |

## Frontmatter

Every MDX file requires:

```yaml
---
title: Clear, concise page title
description: SEO summary — no markdown allowed (no links, backticks, formatting)
---
```

## Syntax

- Language-specific content: `:::python` or `:::js` fences (generates separate Python/JS pages)
- Code highlighting: `# [!code highlight]`, `# [!code ++]`, `# [!code --]`
- API reference links: `@[ClassName]` for first mention of SDK classes/methods

## Style

Follow [Google Developer Documentation Style Guide](https://developers.google.com/style).

- Be concise — second-person imperative present tense
- Sentence-case headings with active verb, not gerund ("Add a tool" not "Adding a tool")
- American English spelling
- No markdown in description fields
- No absolute URLs for internal links
- No `/python/` or `/javascript/` in links (resolved by build pipeline)
- No FontAwesome icon names
- No H5 or H6 headings
