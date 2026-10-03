# Files

- [GitHub Actions and CI/CD](github-actions.md) - GitHub Actions separates untrusted pull-request validation, metadata-only pull-request-target policy, and maintainer-authorized or scheduled repository writers. This page explains the CI gates and review-PR lifecycles for integration metadata and the LangSmith public OpenAPI artifact.
- [Mintlify Integration](mintlify.md) - Mintlify renders the generated documentation tree and deployment-time OpenAPI references for docs.langchain.com. This page defines repository ownership, route configuration, operational handoffs, and the limits of local validation.
- [NPM Snippet Components](npm-snippets.md) - Describes how @langchain/docs-sandbox supplies interactive documentation components to the generated build tree, including overlay precedence, output paths, degraded-install behavior, and test boundaries.
- [Reference Documentation Integration](reference-docs.md) - Defines the boundary between externally operated SDK reference sites, scoped semantic links, and OpenAPI inputs that Mintlify turns into LangSmith endpoint documentation. Covers ownership, refresh operations, and the limits of local validation.
