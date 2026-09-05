---
type: operations guide
title: Adding and Modifying Documentation Pages
description: Step-by-step workflow for creating new documentation pages, moving existing files, updating navigation, and maintaining valid links across the LangChain documentation site.
tags: [documentation, operations, navigation, workflow, build-system]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-6e6efa1569f158fcdb678ef0
    resource: repo://pipeline/cli.py
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
  - id: openwiki-source-8d071ef0669cd8d2d79c6c15
    resource: repo://pipeline/tools/links.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-a39cb5ba9006abfe6280b6f8
    resource: repo://src/oss/openwiki/cli-reference.mdx
  - id: openwiki-source-7471cbec862ab43f765444c7
    resource: repo://src/oss/openwiki/overview.mdx
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# Adding and Modifying Documentation Pages

This page guides you through adding new pages to docs.langchain.com, moving existing pages, and maintaining navigation structure and cross-references. It covers the three distinct content branches maintained by the build system, helps you choose the right page type, and explains how to use CLI tools to automate link updates.

## Page types and content branches

The LangChain documentation operates three content branches with different versioning strategies. Choose the appropriate type based on your content:

### Type 1: OSS versioned (Python and JavaScript)

**When to use:** Content for LangChain, LangGraph, or most Deep Agents documentation where Python and JavaScript developers need separate guidance.

**Characteristics:**
- Single source file with language-specific blocks (`:::python` and `:::js` fences)
- Builds into two separate URLs: `/oss/python/...` and `/oss/javascript/...`
- Language-specific links are rewritten automatically during the build
- Conditional content resolved against the Python branch when not specified

**Where pages live:** `/src/oss/langchain/`, `/src/oss/langgraph/`, `/src/oss/deepagents/` (most content)

**Example:** A LangChain integration guide lives once at `/src/oss/langchain/integrations/openai.mdx` and appears at both `/oss/python/langchain/integrations/openai` and `/oss/javascript/langchain/integrations/openai` with language-specific content blocks shown or hidden per user's language dropdown.

### Type 2: OSS language-agnostic (unversioned)

**When to use:** Content that applies to all programming languages equally, such as OpenWiki operations guides, architecture documentation, or product features not tied to a specific language implementation.

**Characteristics:**
- Single source file with no language splitting (no `:::python` / `:::js` fences required)
- Builds to one URL without language prefix: `/oss/openwiki/...` or `/oss/deepagents/code/...`
- Links to these pages from versioned content are not rewritten; use the unversioned URL directly
- Conditional blocks resolve against the Python branch if present

**Where pages live:** `/src/oss/openwiki/` and `/src/oss/deepagents/code/`

**Example:** OpenWiki's CLI reference lives at `/src/oss/openwiki/cli-reference.mdx` and appears only once at `/oss/openwiki/cli-reference` regardless of language selection.

### Type 3: LangSmith unversioned

**When to use:** Product documentation for LangSmith features, setup, monitoring, or deployment that applies across the platform.

**Characteristics:**
- Single source file building to one unversioned URL: `/langsmith/...`
- Exception: Managed Deep Agents pages (`managed-deep-agents*.mdx`) branch into `/langsmith/python/...` and `/langsmith/javascript/...` language routes
- No language splitting in most LangSmith content

**Where pages live:** `/src/langsmith/` (flat directory structure)

**Example:** LangSmith's evaluation guide lives at `/src/langsmith/evaluation-overview.mdx` and appears at `/langsmith/evaluation-overview` (unversioned).

## File structure and naming conventions

### Directory organization

```
/src/
├── oss/
│   ├── langchain/          # Framework (shared; versioned by language)
│   ├── langgraph/          # Framework (shared; versioned by language)
│   ├── deepagents/         # Framework (shared; versioned by language)
│   │   └── code/           # Unversioned deep agents code documentation
│   ├── openwiki/           # Unversioned OpenWiki documentation
│   ├── python/             # Python-only content
│   │   └── integrations/   # Python integration guides
│   ├── javascript/         # JavaScript/TypeScript-only content
│   │   └── integrations/   # JavaScript integration guides
│   └── concepts/           # Shared conceptual overviews (versioned)
├── langsmith/              # Product documentation (flat; unversioned except Managed Deep Agents)
└── images/                 # Shared images (copied once to build)
```

### Naming patterns

- **Framework pages:** `/src/oss/langchain/feature-name.mdx`
- **Unversioned pages:** `/src/oss/openwiki/feature-name.mdx`
- **Language-specific content:** Use `/src/oss/python/` or `/src/oss/javascript/` for content that applies to only one language
- **Grouped pages:** Create subdirectories for related pages, e.g., `/src/langsmith/deploy/kubernetes.mdx` and `/src/langsmith/deploy/aws.mdx` both appear under "Deploy" in navigation

## Create a new page: Step-by-step

### Step 1: Choose the page type

Determine whether your content is **versioned OSS**, **unversioned OSS**, or **LangSmith** by reviewing the categories above.

### Step 2: Create the MDX file

Create your page file with required YAML frontmatter:

```mdx
---
title: Your Page Title
sidebarTitle: Short Title (optional; appears in nav)
description: One or two sentences describing what this page covers.
keywords: ["keyword1", "keyword2"]
mode: wide  # (optional; use 'wide' for full-width layouts)
---

# Your Page Title

Page content here...
```

**Important:**
- Do not include `generated`, `verified`, `sources`, `timestamp`, or OpenWiki control fields in frontmatter—OpenWiki owns those
- Keep the description short; markdown in descriptions breaks SEO
- For OSS versioned pages, use `:::python` and `:::js` fences to split language-specific content

### Step 3: Place the file in the correct directory

Based on your page type:

- **OSS versioned:** `/src/oss/langchain/`, `/src/oss/langgraph/`, or `/src/oss/deepagents/` (for most content)
- **OSS unversioned:** `/src/oss/openwiki/` or `/src/oss/deepagents/code/`
- **LangSmith:** `/src/langsmith/`

### Step 4: Update navigation in docs.json

Open `/src/docs.json` and add a new entry in the correct menu → tab → group structure.

**Find the right location:** Use `/openwiki/architecture/source-map.md` as your navigation reference. It maps every directory to its position in the docs.json structure.

**Add the page entry:**

```json
{
  "group": "Group Name",
  "pages": [
    "path/from/src/to/file",
    "another-page"
  ]
}
```

Path format: `oss/openwiki/cli-reference` (no `/src/` prefix, no file extension).

**Example:** To add a new OpenWiki page called "Deployment" under the "Operations" group in the OpenWiki tab:

1. Find "OpenWiki" tab in docs.json (line ~533)
2. Add or find the "Operations" group within its pages
3. Insert: `"oss/openwiki/deployment"` (file created at `/src/oss/openwiki/deployment.mdx`)

### Step 5: Test the build locally

```bash
make dev
```

This starts a local Mintlify server at `http://localhost:3000`. Browse to your new page and verify:

- The page renders correctly
- Navigation shows your new page in the right location and group
- Links work (both internal and external)
- Language-specific content (if applicable) shows/hides properly
- Code blocks render cleanly

### Step 6: Run link checks before merging

```bash
make build
make broken-links
```

This builds the documentation and checks for broken links. The script filters out false positives (OpenAPI-generated pages) automatically. Fix any genuine broken links before merging.

## Move or rename a page: Using the CLI tool

The `docs mv` command automatically moves a file and updates all cross-references in the codebase, ensuring no links break.

### Syntax

```bash
python pipeline/cli.py mv <old-path> <new-path> [--dry-run]
```

### Example: Rename and reorganize a page

Move a page from `src/langsmith/evaluation.mdx` to `src/langsmith/deploy/evaluation.mdx`:

```bash
python pipeline/cli.py mv src/langsmith/evaluation.mdx src/langsmith/deploy/evaluation.mdx
```

The tool will:

1. Move the file on disk
2. Scan the entire documentation tree for links pointing to the old location
3. Update relative links in markdown and jupyter notebook files
4. Update links within the moved file itself if its directory changed (relative paths to sibling files need adjustment)
5. Print a summary of all changes made

### Preview changes with --dry-run

Before committing, preview what the tool will do:

```bash
python pipeline/cli.py mv src/langsmith/evaluation.mdx src/langsmith/deploy/evaluation.mdx --dry-run
```

This shows all link rewrites without modifying any files.

### Important: Update navigation after moving

The `docs mv` command handles **file system moves and link updates only**—it does **not** update `docs.json`. After moving a page:

1. Update the path in `/src/docs.json` navigation structure
2. Test with `make dev` to verify the page appears in its new location in the navigation menu
3. Run `make broken-links` to confirm no links are broken

## Writing links in source files

### When linking to unversioned content from versioned pages

OpenWiki and Deep Agents Code pages are unversioned. When linking to them from a versioned page (Python or JavaScript), use the unprefixed URL:

```markdown
<!-- openwiki: broken internal link [/oss/openwiki/cli-reference] file "/oss/openwiki/cli-reference" does not exist. Fix the href or restore the target, then delete this comment. -->
[See our operations guide](/oss/openwiki/cli-reference)
```

The link is **not** rewritten to `/oss/python/openwiki/...` or `/oss/javascript/openwiki/...`—it remains `/oss/openwiki/...`.

### When using relative links in snippets

Snippet files in `/src/snippets/` undergo special link preprocessing. If your page imports a snippet with language-specific content, use relative paths carefully:

```markdown
<Snippet file="/snippets/common-setup.mdx" />
```

During the build, versioned pages that import snippets are redirected to language-specific copies (`/snippets/python/common-setup.mdx` or `/snippets/javascript/common-setup.mdx`) automatically. Avoid paths like `../snippets/...` in snippets themselves; use absolute paths from `/snippets/`.

### Cross-reference linking (@[Name] syntax)

Use `@[ApiName]` syntax for automatic API reference links (resolved during preprocessing):

```markdown
See @[StateGraph] for details on state management.
```

This is converted to a link pointing to the LangGraph reference during the build. Missing cross-references log warnings but do not fail the build.

## Language-specific content blocks

For OSS versioned pages, use fenced blocks to show different content to Python and JavaScript developers:

```markdown
:::python
Python-specific installation example:

```bash
pip install langchain
```
:::

:::js
JavaScript installation example:

```bash
npm install langchain
```
:::
```

**Rules:**
- Content outside any fence appears in both versions
- Each fence type (`:::python` and `:::js`) can appear multiple times in the file
- Escape fence markers with `\:::` if you need to display the syntax itself in documentation
- For content that mentions different features, show the relevant version to each audience

## Handling images and assets

All images should live in `/src/images/`:

```
/src/images/
├── brand/              # Logos, favicons
├── providers/          # Integration provider icons (dark/ and light/ variants)
└── [feature-name]/     # Feature-specific screenshots or diagrams
```

**Reference images in Markdown:**

```markdown
![Alt text](/images/feature-name/screenshot.png)
```

Images copy once to `/build/images/` and are served from the root URL path `/images/`.

## Common workflows

### Add a new integration guide

1. Create `/src/oss/python/integrations/providers/acme-provider.mdx` for Python-specific content, or
2. Create `/src/oss/langchain/integrations/acme.mdx` and use `:::python` and `:::js` blocks if both languages are relevant
3. Add to docs.json under Build → Integrations → Popular Providers (or Integrations by component)
4. Include a title, description, installation steps, and basic usage examples
5. Test with `make dev` and verify the provider appears in both Python and JavaScript dropdowns (if applicable)

### Create a conceptual overview page

1. Create `/src/oss/concepts/your-concept.mdx` (shared between Python and JavaScript)
2. Use language-specific blocks (`:::python` and `:::js`) if the concept has different implementations
3. Add to docs.json under Build → Learn → [Appropriate category]
4. Test the page renders and links resolve correctly

### Start a new LangSmith feature guide

1. Create `/src/langsmith/feature-name.mdx` (unversioned)
2. Add to docs.json under the appropriate menu item (Test, Deploy, Monitor, or Setup)
3. Use `/langsmith/...` URLs when linking to your new page from other pages
4. No language splitting needed unless it's a Managed Deep Agents page (which branches into Python/JavaScript)

### Reorganize documentation groups

1. Decide which pages move and to which groups
2. Update their paths in `/src/docs.json` within the same tab's group structure
3. If pages physically move directories, use `docs mv` and then update docs.json
4. Run `make dev` to verify the new structure
5. Run `make broken-links` to catch any missed updates

## Verification checklist before merging

- [ ] File created with valid YAML frontmatter (title, description, keywords)
- [ ] File placed in the correct source directory (`src/oss/`, `src/langsmith/`, etc.)
- [ ] Page entry added to `/src/docs.json` in the correct menu → tab → group
- [ ] All internal links work: `make dev` and manual browsing
- [ ] Language-specific content (if applicable) uses `:::python` and `:::js` blocks correctly
- [ ] Run `make build && make broken-links` and fix any genuine broken links
- [ ] If page was moved using `docs mv`, verify docs.json was updated separately
- [ ] Images have alt text and correct paths starting with `/images/`
- [ ] For versioned OSS pages: verified page appears in both Python and JavaScript language dropdowns

## See also

- `/openwiki/architecture/source-map.md` — Detailed navigation map and directory structure reference
- `/openwiki/architecture/build-system.md` — How the build pipeline transforms source to deployed docs
- `/openwiki/concepts/versioning.md` — Details on language versioning and conditional rendering
- `/AGENTS.md` — Documentation style guide and critical rules (kept in sync with `CLAUDE.md`)
- `/README.md` — Quick reference for available make commands and repository structure
