# LangChain Python Reference Documentation

This directory contains the source code and build process for the Python reference documentation site, hosted at [`reference.langchain.com/python`](https://reference.langchain.com/python). This site serves references for LangChain, LangGraph, LangSmith, and LangChain integration packages (such as [`langchain-anthropic`](https://pypi.org/project/langchain-anthropic/), [`langchain-openai`](https://pypi.org/project/langchain-openai/), etc.).

The site is built using [MkDocs](https://www.mkdocs.org/) with the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme and the [mkdocstrings](https://mkdocstrings.github.io/) plugin for generating API reference documentation from docstrings. See all config options in the [`mkdocs.yml`](./mkdocs.yml) file.

The `docs/` directory contains the markdown files for the site, with the main entry point being `index.md`. At build time, the stubs provided in each file are substituted with the generated API reference documentation by `mkdocstrings`. This allows us to architect content ordering, layout, etc. in markdown, while still generating the API reference documentation automatically from the source code. Consequently, to make content changes to the API references themselves, you need to make changes in the source code (e.g., docstrings, class/method names, etc.) and then rebuild the site.

---

## Contributing

As these docs are built from the source code, the best way to contribute is to **make changes in the source code** itself. This can include:

- Improving docstrings
- Adding missing docstrings
- Fixing typos
- etc.

You will notice that at the top of each page are two icons: one to view the page source, and the other to edit the page. The "view source" icon takes you to the markdown file for that page, while the "edit page" icon takes you to the relevant source code file in GitHub. Use these links to help you navigate to the right place to make your contributions.

---

## Cross-reference in your project

If you maintain a project that depends on LangChain or LangGraph and would like to reference classes, methods, functions, and more from these docs, you can do so! These pages include an `objects.inv` file that certain docs platforms, such as MkDocs, can use to automatically create links to these docs.

To reference these docs in your project, add the following to your `mkdocs.yml` file:

```yaml
mkdocstrings:
handlers:
    python:
    import:
        - https://reference.langchain.com/python/objects.inv
        - ... # any other inventories you want to include
```

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
- [ ] Fix TOC shadow overflow (started in `reference/python/docs/stylesheets/toc.css`) but was funky
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
2. Installs all packages from git with `uv sync`

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
  ├── langchain-tavily/      # (External org)
  ├── langchain-together/
  ├── langchain-unstructured/
  ├── langchain-upstage/
  ├── langchain-weaviate/
  ├── langgraph-supervisor-py/
  └── langgraph-swarm-py/
```

If you only need to work on specific packages, you can comment out the others in `pyproject.dev.toml`.

---

## MkDocs/mkdocstrings Python Cross-Reference Linking Syntax

### Basic Syntax

The general format for cross-references in mkdocstrings is:

```markdown
[display text][python.path.to.object]
```

If you want the object name as the display text, use backticks:

```markdown
[`object_name`][python.path.to.object]
```

### Linking to Different Python Objects

#### Modules

```markdown
[`langchain.agents`][langchain.agents]

# or

[agents module][langchain.agents]
```

#### Classes

```markdown
[`ChatOpenAI`][langchain_openai.ChatOpenAI]

# or

[the ChatOpenAI class][langchain_openai.ChatOpenAI]
```

#### Functions

```markdown
[`init_chat_model`][langchain.chat_models.init_chat_model]

# or

[initialization function][langchain.chat_models.init_chat_model]
```

#### Methods

```markdown
[`invoke`][langchain_openai.ChatOpenAI.invoke]

# or

[the invoke method][langchain_openai.ChatOpenAI.invoke]
```

#### Class Attributes

```markdown
[`temperature`][langchain_openai.ChatOpenAI.temperature]

# or

[the temperature attribute][langchain_openai.ChatOpenAI.temperature]
```

#### Function/Method Parameters

**Note:** Parameter linking requires the `parameter_headings` option to be enabled in the `mkdocstrings` config (in `mkdocs.yml`). This generates permalinks and TOC entries for each parameter, so don't disable it.

Use `(parameter_name)` syntax to link to specific parameters:

```markdown
[`model_provider`][langchain.chat_models.init_chat_model(model_provider)]

# or

[the model_provider parameter][langchain.chat_models.init_chat_model(model_provider)]
```

For method parameters:

```markdown
[`max_tokens`][langchain_openai.ChatOpenAI.invoke(max_tokens)]
```

For class `__init__` parameters (when using `merge_init_into_class`):

```markdown
[`temperature`][langchain_openai.ChatOpenAI(temperature)]
```

For variadic parameters:

```markdown
[`*args`][package.module.function(*args)]
[`**kwargs`][package.module.function(**kwargs)]
```

#### Return Values

Not directly linkable, but you can link to the return type class:

```markdown
Returns a [`ChatResult`][langchain_core.outputs.ChatResult] object.
```

#### Nested Classes

```markdown
[`Config`][langchain_core.runnables.Runnable.Config]
```

### Advanced Patterns

#### Linking Within Same Module

If you're documenting within the same module, you can use relative paths:

```markdown
See also [`.other_method`][.other_method]
```

#### Linking to Exceptions

```markdown
Raises [`ValueError`][ValueError] if input is invalid.
Raises [`CustomError`][my_package.exceptions.CustomError]
```

#### Linking to Type Aliases

```markdown
[`RunnableConfig`][langchain_core.runnables.config.RunnableConfig]
```

#### Multiple Links in Args Documentation

```python
def create_agent(
    model: BaseChatModel,
    tools: Sequence[BaseTool],
) -> AgentExecutor:
    """
    Create an agent executor.

    Args:
        model: A [`BaseChatModel`][langchain_core.language_models.BaseChatModel]
            instance. You can use [`init_chat_model`][langchain.chat_models.init_chat_model]
            to initialize from a string identifier (see the
            [`model_provider`][langchain.chat_models.init_chat_model(model_provider)]
            parameter for available providers).
        tools: A sequence of [`BaseTool`][langchain_core.tools.BaseTool] instances.
            Use the [`@tool`][langchain_core.tools.tool] decorator to create tools.

    Returns:
        An [`AgentExecutor`][langchain.agents.AgentExecutor] instance.
    """
```

### Best Practices

#### 1. Use Backticks for Code Identifiers

```markdown
✅ [`init_chat_model`][langchain.chat_models.init_chat_model]
❌ [init_chat_model][langchain.chat_models.init_chat_model]
```

#### 2. Use Full Paths for Clarity

```markdown
✅ [`BaseChatModel`][langchain_core.language_models.BaseChatModel]
❌ [`BaseChatModel`][BaseChatModel]  # May not resolve correctly
```

#### 3. Link to Public APIs Only

Only link to public, exported APIs that users should interact with. Avoid linking to internal implementation details (e.g., objects prefixed with `_`).

#### 4. Use Descriptive Text for Complex References

```markdown
✅ See the [`model_provider`][langchain.chat_models.init_chat_model(model_provider)]
   parameter for available providers.
❌ See [`model_provider`][langchain.chat_models.init_chat_model(model_provider)].
```

#### 5. Verify Links Build Correctly

Build and manually check the generated HTML to ensure links resolve correctly.

### Quick Reference Table

| Object Type | Syntax | Example |
|------------|--------|---------|
| Module | `[text][module.path]` | ``[`agents`][langchain.agents]`` |
| Class | `[text][module.Class]` | ``[`ChatOpenAI`][langchain_openai.ChatOpenAI]`` |
| Function | `[text][module.function]` | ``[`init_chat_model`][langchain.chat_models.init_chat_model]`` |
| Method | `[text][module.Class.method]` | ``[`invoke`][langchain_openai.ChatOpenAI.invoke]`` |
| Attribute | `[text][module.Class.attr]` | ``[`temperature`][langchain_openai.ChatOpenAI.temperature]`` |
| Function Param | `[text][module.function(param)]` | ``[`model_provider`][langchain.chat_models.init_chat_model(model_provider)]`` |
| Method Param | `[text][module.Class.method(param)]` | ``[`max_tokens`][langchain_openai.ChatOpenAI.invoke(max_tokens)]`` |
| Class Param | `[text][module.Class(param)]` | ``[`temperature`][langchain_openai.ChatOpenAI(temperature)]`` |

### Testing Links

To test if a link will work:

1. Check the object is in `__init__.py` exports
2. Verify the import path: `from module.path import Object`
3. Build docs with `--strict` mode
4. Check the generated HTML for broken links

```bash
mkdocs build --strict
mkdocs serve  # Preview at http://127.0.0.1:8000/
```

This syntax works with the `mkdocstrings` plugin for MkDocs using the Python handler. Adjust paths according to your package structure and exports.

