# LangChain's unified documentation overview

This repository encompasses the comprehensive documentation for LangChain's products and services, hosted on the Mintlify platform. The documentation is divided into sections for each product. This is a shared set of guidelines to ensure consistency and quality across all content.

## Scope

**These instructions apply to manually authored documentation only. They do NOT apply to:**

- Files in `**/reference/**` directories (auto-generated API reference documentation)
- Build artifacts and generated files

For reference documentation, see `.github/instructions/reference-docs.instructions.md`.

## Working relationship

- You can push back on ideas-this can lead to better documentation. Cite sources and explain your reasoning when you do so
- ALWAYS ask for clarification rather than making assumptions
- NEVER lie, guess, or make up information

## Project context

- Format: MDX files with YAML frontmatter. Mintlify syntax.
- Config: docs.json for navigation, theme, settings
- Components: Mintlify components

## Content strategy

- Document just enough for user success - not too much, not too little
- Prioritize accuracy and usability of information
- Make content evergreen when possible
- Search for existing information before adding new content. Avoid duplication unless it is done for a strategic reason. Reference existing content when possible
- Check existing patterns for consistency
- Start by making the smallest reasonable changes

## docs.json

- Refer to the [docs.json schema](https://mintlify.com/docs.json) when building the docs.json file and site navigation
- If adding a new group, ensure the root `index.mdx` is included in the `pages` array like:

```json
{
  "group": "New group",
  "pages": ["new-group/index", "new-group/other-page"]
}
```

If the trailing `/index` (no extension included) is omitted, the Mintlify parser will raise a warning even though the site will still build.

## Frontmatter requirements for pages

- title: Clear, descriptive, concise page title
- description: Concise summary for SEO/navigation

## Custom code language fences

We have implemented custom code language fences for Python and JavaScript/TypeScript. They are used to tag content that is specific to that language. Use either `:::python` or `:::js` to tag content that is specific to that language. Both are closed with the `:::` fence.

If any code fences like this exist on the code page, then two outputs (one for each language) will be created. For example, if this syntax is on the page in `/concepts/foo.mdx`, two pages will be created at `/python/concepts/foo.mdx` and `/javascript/concepts/foo.mdx`.

For implementation details, see `pipeline/preprocessors/markdown_preprocessor.py`.

## Snippets

Snippet files in `src/snippets/` are reusable MDX content that can be imported into multiple pages. These snippets undergo special link preprocessing during the build process that converts absolute `/oss/` links to relative paths.

**Important:** When writing links in snippets, be careful about path segments. Read the docstrings and comments in `pipeline/core/builder.py` method `_process_snippet_markdown_file` (lines 807-872) to understand how snippet link preprocessing works and why certain path structures are required.

## Style guide

In general, follow the [Google Developer Documentation Style Guide](https://developers.google.com/style). You can also access this style guide through the [Vale-compatible implementation](https://github.com/errata-ai/Google).

- Second-person voice ("you")
- Prerequisites at start of procedural content
- Test all code examples before publishing
- Match style and formatting of existing pages
- Include both basic and advanced use cases
- Language tags on all code blocks
- Alt text on all images
- Root relative paths for internal links
- Correct spelling
- Correct grammar
- Sentence-case for headings
- Ensure American English spelling

## Do not

- Do not skip frontmatter on any MDX file
- Do not use absolute URLs for internal links
- Do not review code blocks (denoted by ```), as they are often not full snippets
- Do not include untested code examples
- Do not make assumptions - always ask for clarification
- Do not include localization in relative links (e.g., `/python/` or `/javascript/`) - these are resolved automatically by the build pipeline
- Do not use model aliases (e.g., "claude-sonnet-4-5") in code examples; always use full model names / identifiers (e.g., "claude-sonnet-4-5-20250929")
- Do not use nested double quotes in Mintlify component attributes (e.g., `default='["a", "b"]'`). This causes escape characters to render in the frontend. Instead, use single quotes inside double quotes: `default="['a', 'b']"`

For questions, refer to the Mintlify docs (either via MCP, if available), or at the [Mintlify documentation](https://docs.mintlify.com/docs/introduction).

## Pull request guidelines

- Describe the "why" of the changes, why the proposed solution is the right one.
- Highlight areas of the proposed changes that require careful review.
- Always add a disclaimer to the PR description mentioning how AI agents are involved with the contribution.
