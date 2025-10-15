# LangChain Python Reference Documentation

This directory contains the source code and build process for the Python reference documentation site, hosted at [`reference.langchain.com/python`](https://reference.langchain.com/python). This site serves references for LangChain, LangGraph, LangSmith, and LangChain integration packages (such as [`langchain-anthropic`](https://pypi.org/project/langchain-anthropic/), [`langchain-openai`](https://pypi.org/project/langchain-openai/), etc.).

The site is built using [MkDocs](https://www.mkdocs.org/) with the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme and the [mkdocstrings](https://mkdocstrings.github.io/) plugin for generating API reference documentation from docstrings. See all config options in the [`mkdocs.yml`](./mkdocs.yml) file.

The `docs/` directory contains the markdown files for the site, with the main entry point being `index.md`. At build time, the stubs provided in each file are substituted with the generated API reference documentation by `mkdocstrings`. This allows us to architect content ordering, layout, etc. in markdown, while still generating the API reference documentation automatically from the source code. Consequently, to make content changes to the API references themselves, you need to make changes in the source code (e.g., docstrings, class/method names, etc.) and then rebuild the site.

---

## Contributing

As these docs are built from the source code, the best way to contribute is to make changes in the source code itself. This can include:

- Improving docstrings
- Adding missing docstrings
- Fixing typos
- etc.

---

## TODO

This site is currently being migrated from a previous Sphinx-based implementation, so there are still some rough edges to be smoothed out. Here are some known issues and potential improvements:

- [ ] For methods that are from base classes, indicate it is inherited from such and link to the base class
- [ ] [Backlinks](https://mkdocstrings.github.io/python/usage/configuration/general/#backlinks)
- [ ] [More xref](https://github.com/analog-garage/mkdocstrings-python-xref)
- [ ] [Modernize annotations](https://mkdocstrings.github.io/python/usage/configuration/signatures/#modernize_annotations)
- [ ] [Inheritance diagrams](https://mkdocstrings.github.io/python/usage/configuration/general/#show_inheritance_diagram)
- [ ] Consider using [inherited docstrings](https://mkdocstrings.github.io/griffe/extensions/official/inherited-docstrings/)
- [ ] Pydantic object refs preloading so that we link to them? Should find their tree and load it in (like we did for old LC)
- [ ] Post-processing step to link out to imports from code blocks
  - [ ] Maybe there's a plugin?
- [ ] Fix `navigation.path` feature/plugin in `mkdocs.yml` not working
- [ ] Resolve Griffe errors
- [ ] Set up CI to fail on unexpected Griffe warnings
- [ ] "Module last updated" auto-generation for module pages using source file commit timestamps or the MkDocs plugin [git-revision-date-localized](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin)
- [ ] Fix search magnifying glass icon color in dark mode
- [ ] Copy page support (need to add a post-processing step to generate markdown files to serve alongside the API reference docs)
- [ ] Language switcher (JS/TS)
- [ ] [Social cards](https://squidfunk.github.io/mkdocs-material/setup/setting-up-social-cards/)
- [ ] [Google Analytics](https://mrkeo.github.io/setup/setting-up-site-analytics)
- [ ] [Versioning?](https://mrkeo.github.io/setup/setting-up-versioning)
- [ ] [Show keyboard shortcut in search window](https://github.com/squidfunk/mkdocs-material/issues/2574#issuecomment-821979698) - also add cmd + k to match Mintlify

---

## Paths

For packages that live in the `langchain-ai/langchain` monorepo, the path to the package should exist at `https://reference.langchain.com/python/{PACKAGE}/` where `PACKAGE` is the package name as defined in the `pyproject.toml` file, with hyphens replaced by underscores. For example, the `langchain-openai` package should be documented at `https://reference.langchain.com/python/langchain_openai/`.

## Local Development

### Setup

This project supports two installation modes:

1. **Development mode** (`pyproject.dev.toml`) - Uses local editable installs from cloned repositories
2. **Production mode** (`pyproject.toml`) - Uses git sources directly

### Development Workflow

For local development with live source code:

```bash
# 1. Ensure repos are cloned in the expected structure (see below)

# 2. Switch to development mode and install
make dev-install

# 3. Serve the docs locally
make serve-docs

# Check current configuration anytime
make config-status
```

When you edit source code in the local repositories, changes will be reflected immediately since packages are installed as editable.

**How it works:** The `make dev-install` command:

1. Switches `pyproject.toml` to use local editable installs (via `switch-config.sh`)
2. Backs up the production config to `pyproject.prod.toml`
3. Installs all packages from local repos with `uv sync`

### Production/CI Workflow

For production builds or CI:

```bash
# Switch to production mode and install
make prod-install

# Build the documentation
make build
```

**How it works:** The `make prod-install` command:

1. Restores `pyproject.toml` to use git sources
2. Installs all packages from git with `uv sync --link-mode=copy`

### Manual Configuration Switching

You can also use the script directly:

```bash
# Switch to development mode
./switch-config.sh dev

# Switch to production mode
./switch-config.sh prod

# Check current mode
./switch-config.sh status
```

### Required Repository Structure

The `pyproject.dev.toml` file expects repositories to be cloned in this structure:

```txt
/some-parent-folder/
  ├── docs/                  # This repository
  │   └── reference/python/
  ├── langchain/             # Main LangChain monorepo
  ├── langgraph/             # Main LangGraph monorepo
  ├── langchain-community/
  ├── langchain-mcp-adapters/
  ├── langchain-datastax/
  ├── langchain-ai21/
  ├── langchain-aws/
  ├── langchain-azure/
  ├── langchain-cerebras/
  ├── langchain-cohere/
  ├── langchain-ibm/
  ├── langchain-elastic/
  ├── langchain-google/
  ├── langchain-milvus/
  ├── langchain-mongodb/
  ├── langchain-neo4j/
  ├── langchain-nvidia/
  ├── langchain-pinecone/
  ├── langchain-postgres/
  ├── langchain-redis/
  ├── langchain-sema4/
  ├── langchain-snowflake/
  ├── langchain-tavily/
  ├── langchain-together/
  ├── langchain-unstructured/
  ├── langchain-upstage/
  ├── langchain-weaviate/
  ├── langgraph-supervisor-py/
  └── langgraph-swarm-py/
```

If you only need to work on specific packages, you can comment out the others in `pyproject.dev.toml`.

