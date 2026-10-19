# Files

- [Builder and Pipeline Tests](builder-tests.md) - Focused offline tests for builder routing, preprocessing, parser conversion, helper tools, and watcher behavior. Use artifact assertions for deterministic contracts, then add a generated-site check when a change affects Mintlify-visible output.
- [Conditional Rendering Tests](conditional-rendering.md) - Test build-time selection of Python and JavaScript Markdown branches, scoped autolinks, and language-specific page and snippet artifacts. Covers the preprocessing order and fence cases that determine observable output.
- [Testing Overview](test-overview.md) - Change-oriented validation guidance for deterministic tests, generated documentation, credentialed samples, remote onboarding checks, and trusted scheduled automation. Choose the narrowest boundary that proves a change, then add the boundary-specific checks it requires.
