# Files

- [Builder Test Boundaries](builder-tests.md) - Guidance for testing DocumentationBuilder route selection, docs.json-sensitive OSS variants, Markdown rewrites, snippets, and copy safety. It distinguishes deterministic unit contracts from generated-site and deployment review.
- [Conditional Rendering Tests](conditional-rendering.md) - Test the validated :::python and :::js preprocessing contract, including literal escaped markers, compact closers, diagnostics, and language-specific build artifacts. Use focused fence tests for structural failures and builder tests for emitted output.
- [Testing and Validation Overview](test-overview.md) - Map documentation and pipeline changes to the smallest deterministic check, generated-site validation, or credentialed CI boundary that proves the affected contract. Covers unit tests, generated content, links, prose, egress inventories, code samples, release-watch logic, and CI-only checks.
