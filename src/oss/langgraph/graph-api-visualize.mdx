---
title: Visualize your graph
sidebarTitle: Visualize your graph
description: Render LangGraph graphs as Mermaid diagrams or PNG images for debugging and documentation.
---

import LanggraphGraphApiVisualizeGraphPy from '/snippets/code-samples/langgraph-graph-api-visualize-graph-py.mdx';
import LanggraphGraphApiVisualizeGraphJs from '/snippets/code-samples/langgraph-graph-api-visualize-graph-js.mdx';
import LanggraphGraphApiVisualizeMermaidPy from '/snippets/code-samples/langgraph-graph-api-visualize-mermaid-py.mdx';
import LanggraphGraphApiVisualizeMermaidJs from '/snippets/code-samples/langgraph-graph-api-visualize-mermaid-js.mdx';
import LanggraphGraphApiVisualizeGraphvizPy from '/snippets/code-samples/langgraph-graph-api-visualize-graphviz-py.mdx';

Render a compiled graph as Mermaid text or a PNG image to inspect topology and debug routing. For an interactive UI, use [LangSmith Studio](/langsmith/studio) with a [local server](/oss/langgraph/local-server).

:::python
You can visualize any compiled graph that exposes `get_graph()`, including @[`StateGraph`]. See the [Graph](https://reference.langchain.com/python/langgraph/graphs/) reference.
:::

:::js
You can visualize any compiled graph that exposes `getGraphAsync()`, including @[`StateGraph`].
:::

The examples below use the same small graph in both languages: two nodes, a conditional edge from `node1`, and a loop back from `node2`.

:::python

<LanggraphGraphApiVisualizeGraphPy />

:::

:::js

<LanggraphGraphApiVisualizeGraphJs />

:::

## Mermaid

Call `draw_mermaid()` on the drawable graph to get Mermaid syntax. Paste the string into any Mermaid renderer, or keep it in docs and PRs.

:::python

<LanggraphGraphApiVisualizeMermaidPy />

```
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	node1(node1)
	node2(node2)
	__end__([<p>__end__</p>]):::last
	__start__ --> node1;
	node1 -.-> __end__;
	node1 -.-> node2;
	node2 --> node1;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```
:::

:::js

<LanggraphGraphApiVisualizeMermaidJs />

```
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	node1(node1)
	node2(node2)
	__end__([<p>__end__</p>]):::last
	__start__ --> node1;
	node1 -.-> __end__;
	node1 -.-> node2;
	node2 --> node1;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```
:::

## PNG

:::python
Render the same graph as a `.png` with one of three approaches:

* Mermaid.ink API (default; no extra packages)
* Mermaid + Pyppeteer (`pip install pyppeteer`)
* Graphviz (`pip install pygraphviz`, plus the system [Graphviz](https://graphviz.org/download/) binary)

**Using Mermaid.ink**

By default, `draw_mermaid_png()` uses the Mermaid.ink API to generate the diagram.

```python
from IPython.display import Image, display

display(Image(app.get_graph().draw_mermaid_png()))
```

![Simple graph visualization](/oss/images/graph_api_image_10.png)

**Using Mermaid + Pyppeteer**

```python
import nest_asyncio
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

nest_asyncio.apply()  # Required for Jupyter Notebook to run async functions

display(
    Image(
        app.get_graph().draw_mermaid_png(
            curve_style=CurveStyle.LINEAR,
            node_colors=NodeStyles(first="#ffdfba", last="#baffc9", default="#fad7de"),
            wrap_label_n_words=9,
            output_file_path=None,
            draw_method=MermaidDrawMethod.PYPPETEER,
            background_color="white",
            padding=10,
        )
    )
)
```

**Using Graphviz**

<LanggraphGraphApiVisualizeGraphvizPy />

:::

:::js
Render the graph as a `.png`. This uses the Mermaid.ink API to generate the diagram.

```typescript
import * as fs from "node:fs/promises";

const drawableGraph = await app.getGraphAsync();
const image = await drawableGraph.drawMermaidPng();
const imageBuffer = new Uint8Array(await image.arrayBuffer());

await fs.writeFile("graph.png", imageBuffer);
```
:::

## See also

* [Graph API overview](/oss/langgraph/graph-api)
* [Use the Graph API](/oss/langgraph/use-graph-api)
* [LangSmith Studio](/langsmith/studio)
* [Run a local server](/oss/langgraph/local-server)
