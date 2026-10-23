# Files

- [Builder Tests](builder-tests.md) - Focused tests for DocumentationBuilder routing, source transformation, shared assets, snippets, and failure boundaries. Use isolated source and build trees to assert emitted artifacts and their final content.
- [Conditional Rendering Tests](conditional-rendering.md) - Test build-time selection of Python and JavaScript Markdown branches, scoped autolinks, and language-specific page and snippet artifacts. Covers preprocessing order and focused suites for conditional content and link transformations.
- [Testing and Validation Overview](test-overview.md) - Select the narrowest check that proves a documentation or tooling change, then add rendered-output or live-service validation only when the change crosses that boundary. This matrix distinguishes deterministic tests, source policy checks, generated-site checks, and credentialed sample runs.
