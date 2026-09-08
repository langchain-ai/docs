# Files

- [GitHub Actions and CI/CD](github-actions.md) - GitHub Actions separates checkout-safe pull-request validation from credentialed publishing, refresh, integration-listing, and OpenWiki automation. This page explains triggers, write boundaries, generated PRs, and failure triage.
- [Mintlify Integration](mintlify.md) - Mintlify renders the generated LangChain documentation tree, defines its site-facing configuration through docs.json, and is the production and preview publication target. This page covers the handoff from the build pipeline, local Mint CLI operations, OpenAPI sections, and export validation boundaries.
- [NPM Snippet Components](npm-snippets.md) - How the builder overlays sandbox components from @langchain/docs-sandbox into generated documentation, how MDX pages consume them, and how to validate the resulting output.
- [Reference Documentation Integration](reference-docs.md) - Explains the boundary between hand-authored documentation, separately generated SDK reference sites, semantic SDK links, and deployment-generated OpenAPI pages.
