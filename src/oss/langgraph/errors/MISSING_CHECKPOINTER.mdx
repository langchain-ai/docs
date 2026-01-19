---
title: MISSING_CHECKPOINTER
---

You are attempting to use built-in LangGraph persistence without providing a checkpointer.

:::python
This happens when a `checkpointer` is missing in the `compile()` method of @[`StateGraph`][StateGraph] or @[`@entrypoint`].
:::

:::js
This happens when a `checkpointer` is missing in the `compile()` method of @[`StateGraph`][StateGraph] or @[`entrypoint`].
:::


## Troubleshooting

The following may help resolve this error:

:::python
-   Initialize and pass a checkpointer to the `compile()` method of @[`StateGraph`][StateGraph] or @[`@entrypoint`].
:::
:::js
-   Initialize and pass a checkpointer to the `compile()` method of @[`StateGraph`][StateGraph] or @[`entrypoint`].
:::

:::python

```python
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()

# Graph API
graph = StateGraph(...).compile(checkpointer=checkpointer)

# Functional API
@entrypoint(checkpointer=checkpointer)
def workflow(messages: list[str]) -> str:
    ...
```

:::

:::js

```typescript
import { InMemorySaver, StateGraph } from "@langchain/langgraph";
const checkpointer = new InMemorySaver();

// Graph API
import { StateGraph } from "@langchain/langgraph";
const graph = new StateGraph(...).compile({ checkpointer });

// Functional API
import { entrypoint } from "@langchain/langgraph";
const workflow = entrypoint(
    { checkpointer, name: "workflow" },
    async (messages: string[]) => {
        // ...
    }
);
```

:::

-   Use the LangGraph API so you don't need to implement or configure checkpointers manually. The API handles all persistence infrastructure for you.

## Related

- Read more about [persistence](/oss/langgraph/persistence).
