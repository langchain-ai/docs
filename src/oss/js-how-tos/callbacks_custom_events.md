# How to dispatch custom callback events

<Info>
**Prerequisites**


This guide assumes familiarity with the following concepts:

- [Callbacks](/oss/concepts/callbacks)
- [Custom callback handlers](/oss/how-to/custom_callbacks)
- [Stream Events API](/oss/concepts/streaming#streamevents)

</Info>

In some situations, you may want to dipsatch a custom callback event from within a [Runnable](/oss/concepts/#runnable-interface) so it can be surfaced
in a custom callback handler or via the [Stream Events API](/oss/concepts/streaming#streamevents).

For example, if you have a long running tool with multiple steps, you can dispatch custom events between the steps and use these custom events to monitor progress.
You could also surface these custom events to an end user of your application to show them how the current task is progressing.

To dispatch a custom event you need to decide on two attributes for the event: the `name` and the `data`.

| Attribute | Type | Description                                                                                              |
|-----------|------|----------------------------------------------------------------------------------------------------------|
| name      | string  | A user defined name for the event.                                                                       |
| data      | any     | The data associated with the event. This can be anything, though we suggest making it JSON serializable. |


<Info>
**- Custom callback events can only be dispatched from within an existing `Runnable`.**

- If using `streamEvents`, you must use `version: "v2"` to consume custom events.
- Sending or rendering custom callback events in LangSmith is not yet supported.
</Info>

## Stream Events API

The most useful way to consume custom events is via the [`.streamEvents()`](/oss/concepts/streaming#streamevents) method.

We can use the `dispatchCustomEvent` API to emit custom events from this method. 

```{=mdx}
<Warning>
**Compatibility**

Dispatching custom callback events requires `@langchain/core>=0.2.16`. See [this guide](/oss/how-to/installation/#installing-integration-packages) for some considerations to take when upgrading `@langchain/core`.

The default entrypoint below triggers an import and initialization of [`async_hooks`](https://nodejs.org/api/async_hooks.html) to enable automatic `RunnableConfig` passing, which is not supported in all environments. If you see import issues, you must import from `@langchain/core/callbacks/dispatch/web` and propagate the `RunnableConfig` object manually (see example below).
</Warning>
```
```typescript
import { RunnableLambda } from "@langchain/core/runnables";
import { dispatchCustomEvent } from "@langchain/core/callbacks/dispatch";

const reflect = RunnableLambda.from(async (value: string) => {
  await dispatchCustomEvent("event1", { reversed: value.split("").reverse().join("") });
  await dispatchCustomEvent("event2", 5);
  return value;
});

const eventStream = await reflect.streamEvents("hello world", { version: "v2" });

for await (const event of eventStream) {
  if (event.event === "on_custom_event") {
    console.log(event);
  }
}
```
```output
{
  event: 'on_custom_event',
  run_id: '9eac217d-3a2d-4563-a91f-3bd49bee4b3d',
  name: 'event1',
  tags: [],
  metadata: {},
  data: { reversed: 'dlrow olleh' }
}
{
  event: 'on_custom_event',
  run_id: '9eac217d-3a2d-4563-a91f-3bd49bee4b3d',
  name: 'event2',
  tags: [],
  metadata: {},
  data: 5
}
```
If you are in a web environment that does not support `async_hooks`, you must import from the web entrypoint and propagate the config manually instead:


```typescript
import { RunnableConfig, RunnableLambda } from "@langchain/core/runnables";
import { dispatchCustomEvent as dispatchCustomEventWeb } from "@langchain/core/callbacks/dispatch/web";

const reflect = RunnableLambda.from(async (value: string, config?: RunnableConfig) => {
  await dispatchCustomEventWeb("event1", { reversed: value.split("").reverse().join("") }, config);
  await dispatchCustomEventWeb("event2", 5, config);
  return value;
});

const eventStream = await reflect.streamEvents("hello world", { version: "v2" });

for await (const event of eventStream) {
  if (event.event === "on_custom_event") {
    console.log(event);
  }
}
```
```output
{
  event: 'on_custom_event',
  run_id: 'dee1e4f0-c5ff-4118-9391-461a0dcc4cb2',
  name: 'event1',
  tags: [],
  metadata: {},
  data: { reversed: 'dlrow olleh' }
}
{
  event: 'on_custom_event',
  run_id: 'dee1e4f0-c5ff-4118-9391-461a0dcc4cb2',
  name: 'event2',
  tags: [],
  metadata: {},
  data: 5
}
```
## Callback Handler

Let's see how to emit custom events with `dispatchCustomEvent`.

Remember, you **must** call `dispatchCustomEvent` from within an existing `Runnable`.


```typescript
import { RunnableConfig, RunnableLambda } from "@langchain/core/runnables";
import { dispatchCustomEvent } from "@langchain/core/callbacks/dispatch";

const reflect = RunnableLambda.from(async (value: string) => {
  await dispatchCustomEvent("event1", { reversed: value.split("").reverse().join("") });
  await dispatchCustomEvent("event2", 5);
  return value;
});

await reflect.invoke("hello world", {
  callbacks: [{
    handleCustomEvent(eventName, data, runId) {
      console.log(eventName, data, runId);
    },
  }]
});
```
```output
event1 { reversed: 'dlrow olleh' } 9c3770ac-c83d-4626-9643-b5fd80eb5431
event2 5 9c3770ac-c83d-4626-9643-b5fd80eb5431
hello world
```
## Related

You've now seen how to emit custom events from within your chains.

You can check out the more in depth guide for [stream events](/oss/how-to/streaming/#using-stream-events) for more ways to parse and receive intermediate steps from your chains.
