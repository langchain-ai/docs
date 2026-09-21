# Files

- [GitHub Actions and CI/CD](github-actions.md) - How repository automation separates untrusted pull-request validation from credentialed and write-capable maintenance. Covers CI gates, live code samples, generated documentation, integration intake, and standing refresh pull requests.
- [Mintlify Integration](mintlify.md) - Mintlify consumes the generated documentation tree and its docs.json contract to render, validate, preview, export, and publish the documentation site. This page defines the local and deployment-time boundaries, especially for generated OpenAPI routes.
- [npm Snippet Components](npm-snippets.md) - Explains the dependency-owned UI-component overlay and the separate pipeline that extracts reusable code-sample MDX. Covers precedence, language routing, safe editing boundaries, and refresh commands.
- [Reference Documentation Integration](reference-docs.md) - Defines the boundary between externally operated SDK reference sites, scoped semantic links, and OpenAPI inputs that Mintlify turns into LangSmith endpoint documentation. Covers refresh ownership and validation limits for generated routes.
