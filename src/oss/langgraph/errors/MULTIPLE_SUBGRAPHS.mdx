---
title: MULTIPLE_SUBGRAPHS
---

This error occurs when you [call a subgraph inside a node](/oss/langgraph/use-subgraphs#call-a-subgraph-inside-a-node) multiple times, and the subgraph is compiled with `checkpointer=True` (continuations mode).

## Troubleshooting

Choose one of the following based on your requirements:

:::python
1. **Don't need interrupts?** Use `checkpointer=False` to opt out of checkpointing entirely:
   ```python
   subgraph = subgraph_builder.compile(checkpointer=False)
   ```

2. **Need interrupts but not cross-invocation persistence?** Use the default inherited mode by omitting `checkpointer`:
   ```python
   subgraph = subgraph_builder.compile()
   ```
   Each invocation gets a unique namespace, so parallel execution works. The subgraph starts fresh each time but can use `interrupt()`.

3. **Need cross-invocation persistence?** Use `checkpointer=True`. LangGraph assigns each invocation a position-based namespace suffix (`calling_node`, `calling_node|1`, etc.) to prevent conflicts. For stable, name-based namespaces, wrap each subgraph with a unique node name — see [parallel subgraphs](/oss/langgraph/use-subgraphs#subgraph-persistence).
:::

:::js
1. **Don't need interrupts?** Use `checkpointer: false` to opt out of checkpointing entirely:
   ```typescript
   const subgraph = subgraphBuilder.compile({ checkpointer: false });
   ```

2. **Need interrupts but not cross-invocation persistence?** Use the default inherited mode by omitting `checkpointer`:
   ```typescript
   const subgraph = subgraphBuilder.compile();
   ```
   Each invocation gets a unique namespace, so parallel execution works. The subgraph starts fresh each time but can use `interrupt()`.

3. **Need cross-invocation persistence?** Use `checkpointer: true`. LangGraph assigns each invocation a position-based namespace suffix (`calling_node`, `calling_node|1`, etc.) to prevent conflicts. For stable, name-based namespaces, wrap each subgraph with a unique node name — see [parallel subgraphs](/oss/langgraph/use-subgraphs#subgraph-persistence).
:::

## Related

- [Subgraph persistence](/oss/langgraph/use-subgraphs#subgraph-persistence) — full comparison of checkpointer modes
- [Persistence](/oss/langgraph/persistence) — how checkpointers work in LangGraph
