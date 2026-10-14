# Files

- [GitHub Actions and CI/CD](github-actions.md) - Explains how this repository separates pull-request validation, metadata-only automation, and trusted workflow writers. Covers previews, changelog and integration automation, generated-documentation maintenance, and failure triage.
- [Mintlify Integration](mintlify.md) - Mintlify renders the generated documentation tree and deployment-time OpenAPI references for docs.langchain.com. This page defines repository ownership, route configuration, operational handoffs, and the limits of local validation.
- [NPM Snippet Components](npm-snippets.md) - Describes how @langchain/docs-sandbox supplies interactive documentation components to the generated build tree, including overlay precedence, output paths, degraded-install behavior, and test boundaries.
- [Reference Documentation Boundaries](reference-docs.md) - Distinguishes the externally operated SDK reference site from the three LangSmith OpenAPI inputs that Mintlify generates at deployment. Explains navigation, spec ownership, refresh automation, and validation boundaries.
