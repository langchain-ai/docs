# Files

- [GitHub Actions and CI/CD](github-actions.md) - How repository automation separates untrusted pull-request validation from credentialed and write-capable maintenance. Covers CI gates, live code samples, generated documentation, integration intake, and standing refresh pull requests.
- [Mintlify Integration](mintlify.md) - Mintlify renders the generated LangChain documentation tree and uses docs.json as its renderer-facing site contract. This page explains the build, navigation, OpenAPI, validation, preview, and production publication boundaries.
- [NPM Snippet Components](npm-snippets.md) - How @langchain/docs-sandbox components are overlaid into generated documentation, consumed by MDX, and verified at the builder and Mintlify boundary.
- [Reference Documentation Integration](reference-docs.md) - Defines the boundary between externally operated SDK reference sites, scoped semantic links, and OpenAPI inputs that Mintlify turns into LangSmith endpoint documentation. Covers refresh ownership and validation limits for generated routes.
