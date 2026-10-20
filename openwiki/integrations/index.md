# Files

- [GitHub Actions and CI Automation](github-actions.md) - Describes repository CI, event trust boundaries, and review-gated GitHub Actions writers. Covers maintainer-gated integration submissions, weekly changelog proposals, credentials, concurrency, and human review.
- [Mintlify Integration and Link Validation](mintlify.md) - Mintlify renders the repository's generated documentation tree and creates selected deployment-time artifacts for docs.langchain.com. This page explains its configuration, generated-output boundary, local link validation and exclusions, OpenAPI behavior, previews, and exports.
- [NPM Snippet Components](npm-snippets.md) - How local JSX and TSX snippet components and allowlisted @langchain/docs-sandbox artifacts reach the built documentation site. Explains their distinct build, language-routing, and refresh behavior relative to MDX and generated code-sample snippets.
- [Reference Documentation Boundaries](reference-docs.md) - Separates the externally generated SDK API reference from this repository's Mintlify OpenAPI sections. Explains ownership, specification lifecycles, local validation boundaries, and filtered link-check results.
