# Files

- [Builder Test Boundaries](builder-tests.md) - Guidance for testing DocumentationBuilder route selection, docs.json-sensitive OSS variants, Markdown rewrites, snippets, and copy safety. It distinguishes deterministic unit contracts from generated-site and deployment review.
- [Conditional Rendering Tests](conditional-rendering.md) - Test the validated :::python and :::js preprocessing contract, including literal escaped markers, compact closers, diagnostics, and language-specific build artifacts. Use focused fence tests for structural failures and builder tests for emitted output.
- [Testing Overview](test-overview.md) - Select validation by the contract a documentation change affects. Deterministic local checks cover transformations and generated output, while CI-only checks cover credentials, registry lookups, services, and external destinations.
