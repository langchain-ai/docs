# Persistence Docs Rework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the monolithic `persistence.mdx` into three focused pages — a conceptual landing page, a checkpointers page (including custom checkpointer guide), and a stores page (including custom store guide) — with the conformance suite surfaced prominently and clear memory/state framing throughout.

**Architecture:** Three shared `.mdx` source files in `src/oss/langgraph/`. The pipeline renders each under both `oss/python/langgraph/<page>` and `oss/javascript/langgraph/<page>`. Custom checkpointer and custom store subsections are Python-only (wrapped in `:::python` fences). `build-custom.mdx` in Integrations becomes a redirect stub.

**Tech Stack:** MDX, Mintlify, `make lint_prose` (Vale), `make broken-links`

---

## File map

| Action | File | Responsibility |
|--------|------|----------------|
| **Rewrite** | `src/oss/langgraph/persistence.mdx` | ~50-line conceptual landing: state/checkpointer/store relationship, short-term vs long-term memory framing, links to checkpointers + stores |
| **Create** | `src/oss/langgraph/checkpointers.mdx` | Full checkpointer content extracted from `persistence.mdx` + custom checkpointer subsection from `build-custom.mdx` |
| **Create** | `src/oss/langgraph/stores.mdx` | Full store content extracted from `persistence.mdx` + custom store subsection (new) |
| **Modify** (redirect stub) | `src/oss/python/integrations/checkpointers/build-custom.mdx` | Replace body with pointer `<Tip>` to `checkpointers.mdx#build-a-custom-checkpointer` |
| **Modify** | `src/oss/python/integrations/checkpointers/index.mdx` | Update "build custom" link to `checkpointers.mdx#build-a-custom-checkpointer` |
| **Modify** | `src/docs.json` | Add Persistence sub-group (3 pages) in Python + JS Capabilities; add redirect for `build-custom`; remove `build-custom` from Integrations nav |
| **Modify** (bulk) | ~40 files with `persistence#` anchor links | Update `#memory-store` → `/stores`, `#checkpoints`/`#threads`/`#checkpointer-libraries` → `/checkpointers#…` |

---

## Task 1: Rewrite `persistence.mdx` as landing page

**Files:**
- Modify: `src/oss/langgraph/persistence.mdx`

Completely replace the file body. No imports needed (they move to stores.mdx).

- [ ] **Step 1: Write the new file**

```mdx
---
title: Persistence
description: LangGraph's persistence layer gives agents short-term memory through checkpointers and long-term memory through stores.
---

LangGraph agents maintain a **state** object that nodes read from and write to during execution. The persistence layer saves that state so agents can resume after interruptions, remember past interactions, and share information across conversations.

There are two complementary systems:

**Checkpointers** save the full graph state at each execution step, organized into **threads**. A thread is a sequence of runs sharing the same state history — typically a single conversation or task session. Checkpointers give agents short-term, thread-scoped memory: the agent can pause and resume, support human-in-the-loop review, replay past states, and recover from failures.

**Stores** persist arbitrary data outside of any thread, accessible across all conversations. Stores give agents long-term memory: user preferences, accumulated knowledge, and facts that should survive beyond a single session.

When you compile a graph with both a checkpointer and a store, the checkpointer tracks what the agent did in this conversation; the store holds what the agent knows about the user across all conversations.

| | Checkpointer | Store |
|--|--|--|
| Scope | Single thread | Cross-thread |
| Memory type | Short-term | Long-term |
| Saves | Full graph state snapshot at each step | Key-value items in namespaced collections |
| Use for | Resume, human-in-the-loop, time travel, fault tolerance | User preferences, facts, shared knowledge |

<Info>
**Agent Server handles persistence automatically**
When using the [Agent Server](/langsmith/agent-server), you do not need to implement or configure checkpointers or stores manually. The server handles all persistence infrastructure behind the scenes.
</Info>

<CardGroup cols={2}>
  <Card title="Checkpointers" icon="database" href="/oss/langgraph/checkpointers">
    Thread-scoped state persistence. Required for human-in-the-loop, time travel, and fault-tolerant execution.
  </Card>
  <Card title="Stores" icon="folders" href="/oss/langgraph/stores">
    Cross-thread long-term memory. Use for user preferences, accumulated knowledge, and shared context.
  </Card>
</CardGroup>
```

- [ ] **Step 2: Lint**

```bash
make lint_prose FILES="src/oss/langgraph/persistence.mdx"
```

- [ ] **Step 3: Commit**

```bash
git add src/oss/langgraph/persistence.mdx
git commit -m "docs: rewrite persistence.mdx as conceptual landing page"
```

---

## Task 2: Create `checkpointers.mdx`

**Files:**
- Create: `src/oss/langgraph/checkpointers.mdx`

Assemble from two sources: (1) checkpointer content extracted from `persistence.mdx`, (2) custom checkpointer guide adapted from `build-custom.mdx`. No imports needed.

**Content extracted from `persistence.mdx`** (copy these sections verbatim):

| Section | Source lines |
|---------|-------------|
| Intro paragraph, image, Agent Server info box, LangSmith tip | 12–23 |
| "Why use persistence" (rename heading to "Why use checkpointers") | 25–34 |
| "Core concepts" through end of Checkpoint namespace | 36–202 |
| "Get and update state" through end of Update state | 204–581 |
| "Optimize checkpoint storage" | 1139–1149 |
| "Checkpointer libraries" + "Checkpointer interface" | 1151–1198 |
| "Serializer" (Python-only section) | 1200–1250 |

**Custom checkpointer content** from `build-custom.mdx`:

Take the full body of `build-custom.mdx` (lines 7–444), prefix it with `## Build a custom checkpointer`, and demote all its H2 headings to H3, H3 to H4.

- [ ] **Step 1: Create file with frontmatter**

```mdx
---
title: Checkpointers
description: LangGraph checkpointers save graph state as checkpoints at each step, enabling persistence, human-in-the-loop, and fault-tolerant execution.
---
```

- [ ] **Step 2: Paste extracted persistence.mdx content**

Copy lines 12–581 and 1139–1250 from `persistence.mdx`. Change the heading `## Why use persistence` to `## Why use checkpointers`.

- [ ] **Step 3: Add conformance tip in the custom section intro**

After the `## Build a custom checkpointer` heading and before `### Overview`, insert:

```mdx
:::python
<Tip>
Validate your implementation as you build using the [conformance test suite](#testing-with-the-conformance-suite). It covers all five base methods and extended capabilities including delta channels. Run it in CI before shipping.
</Tip>
:::
```

- [ ] **Step 4: Paste `build-custom.mdx` content as demoted headings**

Copy lines 7–438 from `build-custom.mdx`. Change heading levels:
- `##` → `###`
- `###` → `####`
- `####` → `#####`

Replace the existing "## Next steps" at the end with:

```mdx
### Next steps

- [Checkpointer integrations](/oss/integrations/checkpointers/index) — available backends to reference or extend
- [Stores](/oss/langgraph/stores) — cross-thread long-term memory
- [Add a custom checkpointer to Agent Server](/langsmith/custom-checkpointer) — deploying your implementation
```

- [ ] **Step 5: Lint**

```bash
make lint_prose FILES="src/oss/langgraph/checkpointers.mdx"
```

Fix all violations.

- [ ] **Step 6: Commit**

```bash
git add src/oss/langgraph/checkpointers.mdx
git commit -m "docs: add checkpointers.mdx with custom checkpointer subsection"
```

---

## Task 3: Create `stores.mdx`

**Files:**
- Create: `src/oss/langgraph/stores.mdx`

**Content from `persistence.mdx`**: lines 583–1137 (the entire "Memory store" section), plus the six snippet imports from lines 5–10.

**Custom store subsection**: new content (Python-only) documenting how to implement `BaseStore`. Before writing, look up the exact method signatures:

```bash
python3 -c "
import inspect
from langgraph.store.base import BaseStore
print(inspect.getsource(BaseStore))
"
```

- [ ] **Step 1: Create file with frontmatter and imports**

```mdx
---
title: Stores
description: LangGraph stores provide cross-thread long-term memory, complementing per-thread checkpointer persistence.
---

import StoreListNamespaceSearchPy from '/snippets/code-samples/store-list-namespace-search-py.mdx';
import StoreListNamespaceSearchJs from '/snippets/code-samples/store-list-namespace-search-js.mdx';
import StoreListNamespacePaginatePy from '/snippets/code-samples/store-list-namespace-paginate-py.mdx';
import StoreListNamespacePaginateJs from '/snippets/code-samples/store-list-namespace-paginate-js.mdx';
import StoreListNamespaceListPy from '/snippets/code-samples/store-list-namespace-list-py.mdx';
import StoreListNamespaceListJs from '/snippets/code-samples/store-list-namespace-list-js.mdx';
```

- [ ] **Step 2: Add intro**

```mdx
Stores let agents persist information across threads — user preferences, accumulated knowledge, and facts that should survive beyond a single conversation. Unlike [checkpointers](/oss/langgraph/checkpointers), which save the full graph state scoped to one thread, stores hold arbitrary key-value data accessible from any thread.
```

- [ ] **Step 3: Paste extracted content**

Copy lines 583–1137 from `persistence.mdx`. Remove the leading `## Memory store` heading and opening paragraph (replaced by the intro above). Keep everything from `### Basic usage` onward.

- [ ] **Step 4: Add custom store subsection**

After the main content, add:

```mdx
## Build a custom store

:::python

To use a storage backend other than the built-in implementations, subclass @[BaseStore] and implement its required methods. The built-in @[InMemoryStore] is the simplest reference implementation.

### Base contract

Look up the exact method signatures before implementing:

```python
import inspect
from langgraph.store.base import BaseStore
print(inspect.getsource(BaseStore))
```

All five async methods are required. Sync counterparts (`put`, `get`, `delete`, `search`, `list_namespaces`) are optional but recommended for compatibility with sync graph execution.

| Method | Description |
|--------|-------------|
| `aput(namespace, key, value, index=None)` | Store or overwrite a single item |
| `aget(namespace, key)` | Retrieve a single item by key; return `None` if missing |
| `adelete(namespace, key)` | Delete a single item |
| `asearch(namespace_prefix, *, query=None, filter=None, limit=10, offset=0)` | Search items under a namespace prefix; optionally by semantic query |
| `alist_namespaces(*, prefix=None, suffix=None, max_depth=None, limit=100, offset=0)` | List namespaces matching a prefix/suffix pattern |

### Namespace design

Namespaces are tuples of strings, e.g. `("user_id", "memories")`. Store implementations must support:

- **Prefix matching**: `asearch(("alice",))` returns items under `("alice",)` and `("alice", "memories")` and any other sub-namespace.
- **Exact key lookup**: `aget(("alice", "memories"), "some-key")` must be O(1) or close to it.

For SQL backends, a common schema:

```sql
CREATE TABLE store_items (
    namespace   TEXT[] NOT NULL,
    key         TEXT NOT NULL,
    value       JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (namespace, key)
);

CREATE INDEX ON store_items USING gin(namespace);
```

### Serialization

Store values are plain Python dicts — no special serializer is required. Serialize with `json.dumps` / `json.loads` or a JSONB column directly. Do not store raw Python objects that are not JSON-serializable.

### Semantic search support

If your backend supports vector search, implement the `query` parameter on `asearch`:

- Accept a `query: str | None` argument.
- When `query` is not `None`, embed it and rank results by cosine similarity.
- Results should include a `score` field on each `Item` when `query` is provided.

If your backend does not support vector search, raise `NotImplementedError` when `query` is passed.

### Testing

No conformance suite exists yet for custom stores. Test your implementation against @[InMemoryStore] as the reference:

```python
import pytest
from langgraph.store.memory import InMemoryStore
from your_module import YourStore

@pytest.fixture
async def store():
    async with YourStore.create() as s:
        yield s

@pytest.fixture
async def reference():
    return InMemoryStore()

async def test_put_and_get(store, reference):
    ns = ("test", "ns")
    for s in [store, reference]:
        await s.aput(ns, "k1", {"val": 1})
        item = await s.aget(ns, "k1")
        assert item is not None
        assert item.value == {"val": 1}

async def test_delete(store, reference):
    ns = ("test", "ns")
    for s in [store, reference]:
        await s.aput(ns, "k1", {"val": 1})
        await s.adelete(ns, "k1")
        assert await s.aget(ns, "k1") is None

async def test_search_prefix(store, reference):
    for s in [store, reference]:
        await s.aput(("user", "memories"), "m1", {"text": "likes pizza"})
        results = await s.asearch(("user",))
        assert any(r.key == "m1" for r in results)
```

### Next steps

- [Add a custom store to Agent Server](/langsmith/custom-store) — deploying your implementation
- [Build a custom checkpointer](/oss/langgraph/checkpointers#build-a-custom-checkpointer) — implementing the checkpointer counterpart

:::
```

- [ ] **Step 5: Lint**

```bash
make lint_prose FILES="src/oss/langgraph/stores.mdx"
```

- [ ] **Step 6: Commit**

```bash
git add src/oss/langgraph/stores.mdx
git commit -m "docs: add stores.mdx with custom store subsection"
```

---

## Task 4: Update `docs.json`

**Files:**
- Modify: `src/docs.json`

- [ ] **Step 1: Add Persistence sub-group to Python Capabilities**

Find `navigation.products[3].dropdowns[0].tabs[2].pages[2]` (the Python Capabilities group). Replace the bare `"oss/python/langgraph/persistence"` entry with a sub-group at the top of `pages`:

```json
{
  "group": "Persistence",
  "pages": [
    "oss/python/langgraph/persistence",
    "oss/python/langgraph/checkpointers",
    "oss/python/langgraph/stores"
  ]
}
```

Full Capabilities group becomes:

```json
{
  "group": "Capabilities",
  "pages": [
    {
      "group": "Persistence",
      "pages": [
        "oss/python/langgraph/persistence",
        "oss/python/langgraph/checkpointers",
        "oss/python/langgraph/stores"
      ]
    },
    "oss/python/langgraph/durable-execution",
    "oss/python/langgraph/fault-tolerance",
    "oss/python/langgraph/event-streaming",
    "oss/python/langgraph/streaming",
    "oss/python/langgraph/interrupts",
    "oss/python/langgraph/use-time-travel",
    "oss/python/langgraph/add-memory",
    "oss/python/langgraph/use-subgraphs"
  ]
}
```

- [ ] **Step 2: Add Persistence sub-group to JS Capabilities**

Find `navigation.products[3].dropdowns[1].tabs[2].pages[2]` (JS Capabilities). Same treatment:

```json
{
  "group": "Capabilities",
  "pages": [
    {
      "group": "Persistence",
      "pages": [
        "oss/javascript/langgraph/persistence",
        "oss/javascript/langgraph/checkpointers",
        "oss/javascript/langgraph/stores"
      ]
    },
    "oss/javascript/langgraph/durable-execution",
    "oss/javascript/langgraph/event-streaming",
    "oss/javascript/langgraph/streaming",
    "oss/javascript/langgraph/interrupts",
    "oss/javascript/langgraph/use-time-travel",
    "oss/javascript/langgraph/add-memory",
    "oss/javascript/langgraph/use-subgraphs"
  ]
}
```

- [ ] **Step 3: Remove `build-custom` from Integrations Checkpointers group**

Find `navigation.products[3].dropdowns[0].tabs[3].pages[3]` (Integrations by component → Checkpointers). Change:

```json
{
  "group": "Checkpointers",
  "pages": [
    "oss/python/integrations/checkpointers/index",
    "oss/python/integrations/checkpointers/build-custom"
  ]
}
```

To:

```json
{
  "group": "Checkpointers",
  "pages": [
    "oss/python/integrations/checkpointers/index"
  ]
}
```

- [ ] **Step 4: Add redirect for retired `build-custom` URL**

In the `redirects` array, append:

```json
{
  "source": "oss/python/integrations/checkpointers/build-custom",
  "destination": "oss/python/langgraph/checkpointers"
}
```

- [ ] **Step 5: Commit**

```bash
git add src/docs.json
git commit -m "docs: update docs.json nav for persistence rework"
```

---

## Task 5: Retire `build-custom.mdx`, update `index.mdx`

**Files:**
- Modify: `src/oss/python/integrations/checkpointers/build-custom.mdx`
- Modify: `src/oss/python/integrations/checkpointers/index.mdx`

- [ ] **Step 1: Replace `build-custom.mdx` with redirect stub**

```mdx
---
title: Build a custom checkpointer
description: Implement BaseCheckpointSaver for a custom storage backend, including delta channel support.
---

<Tip>
This guide has moved. See the [custom checkpointer](/oss/langgraph/checkpointers#build-a-custom-checkpointer) section of the Checkpointers page for the full implementation guide.
</Tip>
```

- [ ] **Step 2: Update link in `index.mdx`**

Find:

```mdx
To implement your own checkpointer for a custom storage backend, see [Build a custom checkpointer](/oss/python/integrations/checkpointers/build-custom).
```

Replace with:

```mdx
To implement your own checkpointer for a custom storage backend, see [Build a custom checkpointer](/oss/langgraph/checkpointers#build-a-custom-checkpointer).
```

- [ ] **Step 3: Lint**

```bash
make lint_prose FILES="src/oss/python/integrations/checkpointers/build-custom.mdx src/oss/python/integrations/checkpointers/index.mdx"
```

- [ ] **Step 4: Commit**

```bash
git add src/oss/python/integrations/checkpointers/
git commit -m "docs: retire build-custom.mdx stub, update index xref"
```

---

## Task 6: Update cross-links across the repo

**Files:**
- ~40 MDX files with `persistence#` anchor links

Run each grep first to confirm the file list, then apply the sed.

- [ ] **Step 1: Fix `#memory-store` → `/stores`**

```bash
grep -rln "persistence#memory-store" src/ --include="*.mdx"
sed -i '' 's|/oss/langgraph/persistence#memory-store|/oss/langgraph/stores|g' \
  src/langsmith/agent-server.mdx \
  src/langsmith/control-plane.mdx \
  src/langsmith/data-plane.mdx \
  src/langsmith/configure-checkpointer.mdx \
  src/langsmith/custom-store.mdx \
  src/langsmith/semantic-search.mdx \
  src/langsmith/configure-ttl.mdx
```

- [ ] **Step 2: Fix `#checkpointer-libraries` → `checkpointers#checkpointer-libraries`**

```bash
grep -rln "persistence#checkpointer-libraries" src/ --include="*.mdx"
sed -i '' 's|/oss/langgraph/persistence#checkpointer-libraries|/oss/langgraph/checkpointers#checkpointer-libraries|g' \
  src/langsmith/control-plane.mdx \
  src/oss/langgraph/backward-compatibility.mdx
```

- [ ] **Step 3: Fix `#checkpoints`, `#threads`, `#pending-writes` → `checkpointers#…`**

```bash
grep -rln "persistence#checkpoints\|persistence#threads\|persistence#pending-writes" src/ --include="*.mdx"
sed -i '' \
  -e 's|/oss/langgraph/persistence#checkpoints|/oss/langgraph/checkpointers#checkpoints|g' \
  -e 's|/oss/langgraph/persistence#threads|/oss/langgraph/checkpointers#threads|g' \
  -e 's|/oss/langgraph/persistence#pending-writes|/oss/langgraph/checkpointers#pending-writes|g' \
  src/langsmith/same-thread.mdx \
  src/langsmith/quick-start-studio.mdx \
  src/langsmith/use-studio.mdx \
  src/langsmith/configure-ttl.mdx \
  src/oss/langgraph/functional-api.mdx \
  src/oss/langgraph/use-subgraphs.mdx \
  src/oss/langgraph/durable-execution.mdx
```

- [ ] **Step 4: Verify no remaining `persistence#` anchor links**

```bash
grep -rn "persistence#" src/ --include="*.mdx"
```

Any remaining hits should be for generic anchors that don't need updating. Fix any that point to relocated content.

- [ ] **Step 5: Lint changed files**

```bash
make lint_prose
```

- [ ] **Step 6: Commit**

```bash
git add src/
git commit -m "docs: update persistence anchor cross-links to new sub-pages"
```

---

## Task 7: Final validation

- [ ] **Step 1: Full lint**

```bash
make lint_prose
```

- [ ] **Step 2: Broken links**

```bash
make broken-links
```

Only `⎿` lines are real failures. File headers without `⎿` lines are OpenAPI false positives.

- [ ] **Step 3: Spot-check nav + content**

Confirm in the built site or local dev:
- Persistence landing shows table + two cards
- Checkpointers page has "Build a custom checkpointer" section with conformance tip visible near the top of that section
- Stores page has "Build a custom store" section
- Old `build-custom` URL redirects to Checkpointers
- Cross-links from LangSmith docs resolve correctly

- [ ] **Step 4: Final commit if needed**

```bash
git add -p
git commit -m "docs: fix lint/link violations from persistence rework"
```
