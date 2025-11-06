# LangChain Reference Docs

Reference documentation is not consolidated into our primary Mintlify website ([`docs.langchain.com`](https://docs.langchain.com)) due to limitations in the Mintlify platform. Instead, we deploy static documentation sites for our Python and JavaScript/TypeScript references.

Currently, a Vercel project serves the built HTML from the `dist/language` directories at [`reference.langchain.com/python`](https://reference.langchain.com/python) and [`reference.langchain.com/javascript`](https://reference.langchain.com/javascript).

See the [`reference/python/README.md`](./python/README.md) and [`reference/javascript/README.md`](./javascript/README.md) files for more information on how each are built and deployed.

## v0.3 Python HTML Reference Docs

The v0.3 Python HTML reference docs are served at `/v0.3/python` and are maintained as a git submodule pointing to the [`langchain-api-docs-html`](https://github.com/langchain-ai/langchain-api-docs-html) repository.

### Setup

On first clone or when the submodule is added, initialize it:

```bash
git submodule update --init --recursive
```

### Updating v0.3 Python HTML Reference Docs

```bash
cd reference/external/html-docs
git pull origin main
cd ../..
git add external/html-docs
git commit -m "Update v0.3 Python HTML reference docs"
```

### Build Process

The build script (`pnpm build:html-v03`) copies files from `external/html-docs/api_reference_build/html/` to `dist/v0.3/python/` during deployment.
