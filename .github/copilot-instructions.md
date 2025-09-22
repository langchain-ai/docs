# LangChain's unified documentation overview

This repository encompasses the comprehensive documentation for LangChain's products and services, all hosted on the Mintlify platform. The documentation is divided into sections for each product. This is a shared set of guidelines to ensure consistency and quality across all content.

## Folder structure

All documentation lives in the `src/` folder, with the following structure:

- `/oss`: Documentation for the open-source LangChain and LangGraph framework
    - `/python`: Python-specific integrations and release notes
    - `/javascript`: JS/TS-specific integrations and release notes
    - `/langchain`: Docs on core components, advanced usage, and production usage of LangChain
    - `/langgraph`: Docs on capabilities, production usage, and APIs in LangGraph
    - `/reference`: Links out to reference docs for both LangChain and LangGraph
    - `/contributing`: Guidelines on contributing to the docs, codebase, and submit integrations
    - `/images`: Shared images used across OSS docs
    - `/concepts`: Shared concepts used across OSS docs
    - The root contains product/language agnostic meta-info such as our versioning & release policy and the releases page.
- `/langsmith`: Documentation for LangSmith, including quickstarts, observability, evaluation, prompt engineering, self hosting, and administration.
- `/langgraph-platform`: Documentation for the LangGraph Platform, including quickstarts, features, guides on building & deploying using the platform, management & administration, and reference docs.
- `/labs`: Home to LangChain's experimental AI products, including deep agents, open SWE, and Open Agent Platform
- `/images`: Shared images used across all docs
- `/snippets`: Shared code snippets used across all docs

## Libraries and frameworks

Documentation is written for Mintlify's MDX syntax and uses Mintlify components. For questions, refer to the Mintlify docs (either via MCP, if available), or at the [Mintlify documentation](https://docs.mintlify.com/docs/introduction).

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

## Custom code language fences

We have implemented custom code language fences for Python and Javascript. They are used to tag content that is specific to that language. Use either `:::python` or `:::js` to tag content that is specific to that language. Both are closed with the `:::` fence.

If any code fences like this exist on the code page, then two outputs (one for each language) will be created. For example, if this syntax is on the page in `/concepts/foo.mdx`, two pages will be created at `/python/concepts/foo.mdx` and `/javascript/concepts/foo.mdx`.

For implementation details, see `pipeline/preprocessors/markdown_preprocessor.py`.

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

## Do not

- Skip frontmatter on any MDX file
- Use absolute URLs for internal links
- Include untested code examples
- Make assumptions - always ask for clarification

