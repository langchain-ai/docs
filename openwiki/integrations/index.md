# Files

- [GitHub Actions and CI Automation](github-actions.md) - Explains CI validation, event trust boundaries, review-oriented automation, and the Mintlify preview-branch lifecycle. Covers least-privilege jobs, generated build handoffs, fork-safe behavior, and scheduled maintenance writers.
- [Mintlify Integration](mintlify.md) - Mintlify renders the repository's generated documentation tree and creates selected deployment-time artifacts for docs.langchain.com. This page explains the authored-source boundary, local validation, OpenAPI behavior, and trusted preview and production handoffs.
- [NPM Snippet Components](npm-snippets.md) - How local JSX and TSX snippet components and allowlisted @langchain/docs-sandbox artifacts reach the built documentation site. Explains their distinct build, language-routing, and refresh behavior relative to MDX and generated code-sample snippets.
- [API Reference and OpenAPI Surfaces](reference-docs.md) - Separates the externally generated SDK API reference from this repository's Mintlify OpenAPI sections. Explains OpenAPI input ownership, refresh and deployment lifecycles, validation boundaries, and safe authoring rules.
