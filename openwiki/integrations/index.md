# Files

- [GitHub Actions and CI/CD](github-actions.md) - How this repository separates untrusted pull-request validation from narrowly scoped workflows that label, comment, create review requests, or use scheduled credentials. Covers CI, PR-facing automation, external integration intake, and the weekly Mint export check.
- [Mintlify Integration](mintlify.md) - Mintlify renders the generated LangChain documentation tree, defines its site-facing configuration through docs.json, and is the production and preview publication target. This page covers the handoff from the build pipeline, local Mint CLI operations, OpenAPI sections, and export validation boundaries.
- [NPM Snippet Components](npm-snippets.md) - How the builder overlays sandbox components from @langchain/docs-sandbox into generated documentation, how MDX pages consume them, and how to validate the resulting output.
- [Reference Documentation Integration](reference-docs.md) - Explains the boundary between authored documentation, external SDK reference sites, semantic SDK links, and deployment-generated LangSmith OpenAPI pages. Covers ownership, refresh automation, and the focused checks that protect those boundaries.
