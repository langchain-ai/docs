# Files

- [GitHub Actions and CI/CD](github-actions.md) - Repository automation separates untrusted pull-request validation from metadata-only pull-request-target automation and trusted secret-backed or repository-writing maintenance. This page maps the CI gates, generated documentation refreshes, integration intake, and review-PR lifecycle.
- [Mintlify Integration](mintlify.md) - Mintlify consumes the generated documentation tree and its docs.json contract to render, validate, preview, export, and publish the documentation site. This page defines the local and deployment-time boundaries, especially for generated OpenAPI routes.
- [npm Snippet Components](npm-snippets.md) - Explains the dependency-owned UI-component overlay and the separate pipeline that extracts reusable code-sample MDX. Covers precedence, language routing, safe editing boundaries, and refresh commands.
- [Reference Documentation Integration](reference-docs.md) - Defines the boundary between externally operated SDK reference sites, scoped semantic links, and OpenAPI inputs that Mintlify turns into LangSmith endpoint documentation. Covers refresh ownership and validation limits for generated routes.
