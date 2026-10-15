# Files

- [Builder Tests](builder-tests.md) - Focused, offline tests for DocumentationBuilder routing, Markdown preprocessing, shared inputs, snippets, source containment, and generated build-output invariants. Covers when an output assertion is sufficient and when to add a built-site check.
- [Conditional Rendering Tests](conditional-rendering.md) - Test guidance for the build-time `:::python` and `:::js` renderer, including its regex fence semantics, scoped autolinks, code-fence boundary, and language-specific artifacts.
- [Testing Overview](test-overview.md) - Change-oriented validation for deterministic pipeline tests, generated documentation, credentialed code samples, onboarding-model checks, and CI-only remote boundaries. Use the narrowest check that establishes the changed contract, then add boundary checks where required.
