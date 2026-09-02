# LangChain Documentation Guidelines

Documentation for LangChain products hosted on Mintlify. These guidelines apply to manually authored content under `src/`, not Mintlify `build/` output.

`AGENTS.md` in the repository root is the authoritative guide. Read it before making any non-trivial change. This file carries only the rules that apply to every task.

Prose style rules (voice, headings, terminology, page structure) live in `.github/instructions/docs-style.instructions.md` and load automatically when you edit `src/**/*.mdx`.

## Critical rules

1. **Always ask for clarification** rather than making assumptions
2. **Never fabricate** examples, JSON snippets, policy details, or use case descriptions — use only content from the user or existing source files
3. **Never use markdown in frontmatter `description`** — breaks SEO
4. **Never edit `build/`** — Mintlify build output (regenerate with `make build` or `make dev`)
5. **Always update `src/docs.json`** when adding new pages
6. **Use Tabler icons only** — not FontAwesome
7. **Test code examples** before including them
8. **Always run `make lint_prose`** on changed files before committing — CI blocks on it

## Repository structure

```txt
docs/
├── src/                        # All manually authored content
│   ├── docs.json               # Mintlify config + navigation
│   ├── index.mdx               # Home page
│   ├── style.css               # Custom CSS
│   ├── langsmith/              # LangSmith product docs
│   │   └── fleet/              #   Fleet (nav label: "No-code agents")
│   ├── oss/                    # Open source docs (LangChain, LangGraph, Deep Agents, OpenWiki)
│   ├── snippets/               # Reusable MDX snippets
│   ├── images/                 # Documentation images
│   └── fonts/                  # Font files
├── pipeline/                   # Python build system & preprocessors
├── build/                      # Build output — do not edit
├── scripts/                    # Helper utilities
└── tests/                      # Pipeline tests
```

For the navigation map (every product, menu item, tab, and group), see `AGENTS.md`. Navigation is defined in `src/docs.json` as 2 products: `AGENT DEVELOPMENT LIFECYCLE` (Home, Build, Test, Deploy, Monitor) and `PRODUCTS AND SETUP` (LangSmith setup, LLM Gateway, No-code agents, Engine, Deep Agents Code). Nav names do not match source directory names, so consult `AGENTS.md` before placing a new page.

## Quick reference

| What | Where/How |
|------|-----------|
| Navigation config | `src/docs.json` |
| Reusable snippets | `src/snippets/` |
| Provider icons | `src/images/providers/` |
| Icon library | Tabler, <https://tabler.io/icons> |
| Mintlify components | <https://mintlify.com/docs/components> |
| Auto-link syntax | `@[ClassName]`, defined in `pipeline/preprocessors/link_map.py` |

## Frontmatter

Every MDX file requires:

```yaml
---
title: Clear, concise page title
description: SEO summary — no markdown allowed (no links, backticks, formatting)
---
```

## Syntax

- Language-specific content: `:::python` or `:::js` fences (generates separate Python and TypeScript pages)
- Code highlighting: `# [!code highlight]`, `# [!code ++]`, `# [!code --]`
- API reference links: `@[ClassName]` for the first mention of SDK classes or methods
