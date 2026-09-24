# Files

- [GitHub Actions and CI/CD](github-actions.md) - How repository automation separates untrusted pull-request validation from credentialed or write-capable jobs. Covers CI, code-sample testing and trace refreshes, GitHub mutations, scheduled maintenance, and Linear escalation boundaries.
- [Mintlify Integration](mintlify.md) - Mintlify renders the generated LangChain documentation tree and uses docs.json as its renderer-facing site contract. This page explains the build, navigation, OpenAPI, validation, preview, and production publication boundaries.
- [NPM Snippet Components](npm-snippets.md) - How the builder overlays sandbox components from @langchain/docs-sandbox into generated documentation, how MDX pages consume them, and how to validate the resulting output.
- [Reference Documentation Integration](reference-docs.md) - Defines the boundary between semantic SDK links, externally operated API reference sites, and OpenAPI inputs that Mintlify turns into LangSmith endpoint documentation at deployment. Covers refresh automation and checks designed for generated routes.
