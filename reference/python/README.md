# LangChain Python Reference Documentation

This directory contains the source code and build process for the Python reference documentation site, hosted at [`reference.langchain.com/python`](https://reference.langchain.com/python). This site serves references for LangChain, LangGraph, LangGraph Platform, and LangChain integration packages (such as [`langchain-anthropic`](https://pypi.org/project/langchain-anthropic/), [`langchain-openai`](https://pypi.org/project/langchain-openai/), etc.).

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

- [ ] Code block admonitions
- [ ] URLs
- [ ] Code snippet double backticks
- [ ] See if it's possible to make our types clickable (like the Python ones)
- [ ] Post-processing step to link out to imports from code blocks
  - [ ] Maybe there's a plugin?
- [ ] Fix `navigation.path` feature/plugin in `mkdocs.yml` not working
- [ ] Fix search magnifying glass icon color in dark mode
- [ ] Consider using [inherited docstrings](https://mkdocstrings.github.io/griffe/extensions/official/inherited-docstrings/)
- [ ] Hyperlink deprecation messages in LangGraph docs (source code)
- [ ] Copy page support (may need to be post-processing step to generate markdown files)
- [ ] Language switcher
- [ ] [Social cards](https://squidfunk.github.io/mkdocs-material/setup/setting-up-social-cards/)
- [ ] [Google Analytics](https://mrkeo.github.io/setup/setting-up-site-analytics)
- [ ] [Versioning?](https://mrkeo.github.io/setup/setting-up-versioning)
- [ ] [Show keyboard shortcut in search window](https://github.com/squidfunk/mkdocs-material/issues/2574#issuecomment-821979698)

---

## Paths

For packages that live in the `langchain-ai/langchain` monorepo, the path to the package should exist at `https://reference.langchain.com/python/{PACKAGE}/` where `PACKAGE` is the package name as defined in the `pyproject.toml` file, with hyphens replaced by underscores. For example, the `langchain-openai` package should be documented at `https://reference.langchain.com/python/langchain_openai/`.

## Local Development

`langchain-ai/` org repositories that needed to be cloned locally for local reference doc generation:

```txt
langchain
langchain-community
langchain-mcp-adapters
langchain-datastax
langchain-ai21
langchain-aws
langchain-azure
langchain-cerebras
langchain-cohere
langchain-ibm
langchain-elastic
langchain-google
langchain-milvus
langchain-mongodb
langchain-neo4j
langchain-nvidia
langchain-pinecone
langchain-postgres
langchain-redis
langchain-sema4
langchain-snowflake
langchain-together
langchain-unstructured
langchain-upstage
langchain-weaviate
langgraph
langgraph-supervisor-py
langgraph-swarm-py
```

