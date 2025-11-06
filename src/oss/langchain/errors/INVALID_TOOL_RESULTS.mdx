---
title: INVALID_TOOL_RESULTS
---

<Note>
    Currently only used in `langchainjs` (JavaScript/TypeScript).
</Note>

This error occurs when passing mismatched, insufficient, or excessive @[`ToolMessage`] objects to a model during tool calling operations.

The error stems from a fundamental requirement: an assistant message with `tool_calls` must be followed by tool messages responding to each `tool_call_id`.

When a model returns an @[`AIMessage`] with tool calls, you must provide exactly one corresponding @[`ToolMessage`] for each tool call, with matching `tool_call_id` values.

## Common causes

* **Insufficient responses**: If a model requests two tool executions but you only provide one response message, the model rejects the incomplete message chain
* **Duplicate responses**: Providing multiple @[`ToolMessage`] objects for the same tool call ID results in rejection, as does having unmatched IDs
* **Orphaned tool messages**: Sending a @[`ToolMessage`] without a preceding @[`AIMessage`] containing tool calls violates protocol requirements

:::python
Here's an example of a problematic pattern:

```python
# Model requests two tool calls
response_message.tool_calls  # Returns 2 calls

# But only one ToolMessage provided
chat_history.append(ToolMessage(
    content=str(tool_response),
    tool_call_id=tool_call.get("id")
))

model_with_tools.invoke(chat_history)
```
:::

:::js
Here's an example of a problematic pattern:

```javascript
// Model requests two tool calls
responseMessage.tool_calls // Returns 2 calls

// But only one ToolMessage provided
chatHistory.push({
  role: "tool",
  content: toolResponse,
  tool_call_id: responseMessage.tool_calls[0].id
});

await modelWithTools.invoke(chatHistory); // Fails with INVALID_TOOL_RESULTS
```
:::

## Troubleshooting

To resolve this error:

* **Count matching pairs**: Ensure one @[`ToolMessage`] exists per tool call in the preceding @[`AIMessage`]
* **Verify IDs**: Confirm each `ToolMessage.tool_call_id` matches an actual tool call identifier
