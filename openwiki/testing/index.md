# Files

- [Builder Test Boundaries](builder-tests.md) - Guidance for testing DocumentationBuilder route selection, docs.json-sensitive OSS variants, Markdown rewrites, snippets, and copy safety. It distinguishes deterministic unit contracts from generated-site and deployment review.
- [Conditional Rendering Tests](conditional-rendering.md) - Test build-time selection of Python and JavaScript Markdown branches, scoped autolinks, and language-specific page and snippet artifacts. Covers preprocessing order and focused suites for conditional content and link transformations.
- [Testing Overview](test-overview.md) - Select validation by the contract a documentation change affects. Deterministic local checks cover transformations and generated output, while CI-only checks cover credentials, services, and external destinations.
