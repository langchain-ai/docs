# Files

- [Builder Tests](builder-tests.md) - Focused, offline tests for DocumentationBuilder routing, Markdown preprocessing, shared inputs, snippets, source containment, and generated build-output invariants. Covers when an output assertion is sufficient and when to add a built-site check.
- [Conditional Rendering Tests](conditional-rendering.md) - Test the build-time renderer for Python and JavaScript conditional Markdown blocks, including preprocessing order, fence edge cases, and language-specific build artifacts.
- [Testing Overview](test-overview.md) - Change-oriented validation guidance for deterministic tests, generated documentation, credentialed samples, remote onboarding checks, trusted scheduled automation, and release-watch changes. Choose the narrowest boundary that proves a change, then add the boundary-specific checks it requires.
