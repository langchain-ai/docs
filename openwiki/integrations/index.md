# Files

- [GitHub Actions and CI/CD](github-actions.md) - Repository automation separates untrusted pull-request validation from metadata-only pull-request-target automation and trusted secret-backed or repository-writing maintenance. This page maps the CI gates, generated documentation refreshes, integration intake, and review-PR lifecycle.
- [Mintlify Integration](mintlify.md) - Mintlify renders the generated documentation tree and applies the docs.json presentation contract. This page distinguishes local generated-tree validation from deployment-time OpenAPI generation, publishing, previews, and LangSmith specification refreshes.
- [npm Snippet Components](npm-snippets.md) - Explains the dependency-owned UI-component overlay and the separate pipeline that extracts reusable code-sample MDX. Covers precedence, language routing, safe editing boundaries, and refresh commands.
- [Reference Documentation Integration](reference-docs.md) - Defines the boundary between externally operated SDK reference sites, scoped semantic links, and OpenAPI inputs that Mintlify turns into LangSmith endpoint documentation. Covers refresh ownership and validation limits for generated routes.
