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

```
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
- Use model aliases — use full identifiers (e.g., `claude-sonnet-4-5-20250929`)
- Use FontAwesome icon names
- Use nested double quotes in component attributes — use `default="['a', 'b']"` not `default='["a", "b"]'`
- Use H5 or H6 headings
- Use excessive bold/italics in body text
- Include "key features" lists
- Use horizontal lines
## Adding pages

1. Create MDX file with required frontmatter
2. Update `src/docs.json` to add to navigation
3. For new groups, include index: `"pages": ["group/index", "group/page"]`

## Pull requests

- Explain the "why" of changes
- Highlight areas needing careful review
- Disclose AI agent involvement in description
