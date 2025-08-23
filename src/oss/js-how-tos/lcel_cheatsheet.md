# LangChain Expression Language Cheatsheet

This is a quick reference for all the most important LCEL primitives. For more advanced usage see the [LCEL how-to guides](/oss/how-to/#langchain-expression-language-lcel) and the [full API reference](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html).

### Invoke a runnable
#### [runnable.invoke()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#invoke)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const runnable = RunnableLambda.from((x: number) => x.toString());

await runnable.invoke(5);
```



```output
"5"
```


### Batch a runnable
#### [runnable.batch()](hhttps://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#batch)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const runnable = RunnableLambda.from((x: number) => x.toString());

await runnable.batch([7, 8, 9]);
```



```output
[ "7", "8", "9" ]
```


### Stream a runnable
#### [runnable.stream()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#stream)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

async function* generatorFn(x: number[]) {
  for (const i of x) {
    yield i.toString();
  }
}

const runnable = RunnableLambda.from(generatorFn);

const stream = await runnable.stream([0, 1, 2, 3, 4]);

for await (const chunk of stream) {
  console.log(chunk);
  console.log("---")
}
```
```output
0
---
1
---
2
---
3
---
4
---
```
### Compose runnables
#### [runnable.pipe()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#pipe)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const runnable1 = RunnableLambda.from((x: any) => {
  return { foo: x };
});

const runnable2 = RunnableLambda.from((x: any) => [x].concat([x]));

const chain = runnable1.pipe(runnable2);

await chain.invoke(2);
```



```output
[ { foo: 2 }, { foo: 2 } ]
```


#### [RunnableSequence.from()](https://api.js.langchain.com/classes/langchain_core.runnables.RunnableSequence.html#from)


```typescript
import { RunnableLambda, RunnableSequence } from "@langchain/core/runnables";

const runnable1 = RunnableLambda.from((x: any) => {
  return { foo: x };
});

const runnable2 = RunnableLambda.from((x: any) => [x].concat([x]));

const chain = RunnableSequence.from([
  runnable1,
  runnable2,
]);

await chain.invoke(2);
```



```output
[ { foo: 2 }, { foo: 2 } ]
```


### Invoke runnables in parallel
#### [RunnableParallel](https://api.js.langchain.com/classes/langchain_core.runnables.RunnableParallel.html)


```typescript
import { RunnableLambda, RunnableParallel } from "@langchain/core/runnables";

const runnable1 = RunnableLambda.from((x: any) => {
  return { foo: x };
});

const runnable2 = RunnableLambda.from((x: any) => [x].concat([x]));

const chain = RunnableParallel.from({
  first: runnable1,
  second: runnable2,
});

await chain.invoke(2);
```



```output
{ first: { foo: 2 }, second: [ 2, 2 ] }
```


### Turn a function into a runnable
#### [RunnableLambda](https://api.js.langchain.com/classes/langchain_core.runnables.RunnableLambda.html)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const adder = (x: number) => {
  return x + 5;
};

const runnable = RunnableLambda.from(adder);

await runnable.invoke(5);
```



```output
10
```


### Merge input and output dicts
#### [RunnablePassthrough.assign()](https://api.js.langchain.com/classes/langchain_core.runnables.RunnablePassthrough.html#assign)


```typescript
import { RunnableLambda, RunnablePassthrough } from "@langchain/core/runnables";

const runnable = RunnableLambda.from((x: { foo: number }) => {
  return x.foo + 7;
});

const chain = RunnablePassthrough.assign({
  bar: runnable,
});

await chain.invoke({ foo: 10 });
```



```output
{ foo: 10, bar: 17 }
```


### Include input dict in output dict

#### [RunnablePassthrough](https://api.js.langchain.com/classes/langchain_core.runnables.RunnablePassthrough.html)


```typescript
import {
  RunnableLambda,
  RunnableParallel,
  RunnablePassthrough
} from "@langchain/core/runnables";

const runnable = RunnableLambda.from((x: { foo: number }) => {
  return x.foo + 7;
});

const chain = RunnableParallel.from({
  bar: runnable,
  baz: new RunnablePassthrough(),
});

await chain.invoke({ foo: 10 });
```



```output
{ baz: { foo: 10 }, bar: 17 }
```


### Add default invocation args

#### [runnable.bind()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#bind)


```typescript
import { type RunnableConfig, RunnableLambda } from "@langchain/core/runnables";

const branchedFn = (mainArg: Record<string, any>, config?: RunnableConfig) => {
  if (config?.configurable?.boundKey !== undefined) {
    return { ...mainArg, boundKey: config?.configurable?.boundKey };
  }
  return mainArg;
}

const runnable = RunnableLambda.from(branchedFn);
const boundRunnable = runnable.bind({ configurable: { boundKey: "goodbye!" } });

await boundRunnable.invoke({ bar: "hello" });
```



```output
{ bar: "hello", boundKey: "goodbye!" }
```


### Add fallbacks

#### [runnable.withFallbacks()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#withFallbacks)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const runnable = RunnableLambda.from((x: any) => {
  throw new Error("Error case")
});

const fallback = RunnableLambda.from((x: any) => x + x);

const chain = runnable.withFallbacks([fallback]);

await chain.invoke("foo");
```



```output
"foofoo"
```


### Add retries
#### [runnable.withRetry()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#withRetry)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

let counter = 0;

const retryFn = (_: any) => {
  counter++;
  console.log(`attempt with counter ${counter}`);
  throw new Error("Expected error");
};

const chain = RunnableLambda.from(retryFn).withRetry({
  stopAfterAttempt: 2,
});

await chain.invoke(2);
```
```output
attempt with counter 1
``````output
attempt with counter 2
```
```output
Stack trace:
``````output
Error: Expected error
``````output
    at RunnableLambda.retryFn [as func] (<anonymous>:6:9)
``````output
    at file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/@langchain/core/0.2.0/dist/runnables/base.js:1337:45
``````output
    at MockAsyncLocalStorage.run (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/@langchain/core/0.2.0/dist/singletons/index.js:7:16)
``````output
    at file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/@langchain/core/0.2.0/dist/runnables/base.js:1335:67
``````output
    at new Promise (<anonymous>)
``````output
    at RunnableLambda._invoke (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/@langchain/core/0.2.0/dist/runnables/base.js:1330:16)
``````output
    at RunnableLambda._callWithConfig (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/@langchain/core/0.2.0/dist/runnables/base.js:207:33)
``````output
    at eventLoopTick (ext:core/01_core.js:78:9)
``````output
    at async RetryOperation._fn (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/p-retry/4.6.2/index.js:50:12)
```

### Configure runnable execution

#### [RunnableConfig](https://api.js.langchain.com/interfaces/langchain_core.runnables.RunnableConfig.html)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const runnable1 = RunnableLambda.from(async (x: any) => {
  await new Promise((resolve) => setTimeout(resolve, 2000));
  return { foo: x };
});

// Takes 4 seconds
await runnable1.batch([1, 2, 3], { maxConcurrency: 2 });
```



```output
[ { foo: 1 }, { foo: 2 }, { foo: 3 } ]
```


### Add default config to runnable

#### [runnable.withConfig()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#withConfig)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const runnable1 = RunnableLambda.from(async (x: any) => {
  await new Promise((resolve) => setTimeout(resolve, 2000));
  return { foo: x };
}).withConfig({
  maxConcurrency: 2,
});

// Takes 4 seconds
await runnable1.batch([1, 2, 3]);
```



```output
[ { foo: 1 }, { foo: 2 }, { foo: 3 } ]
```


### Build a chain dynamically based on input


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const runnable1 = RunnableLambda.from((x: any) => {
  return { foo: x };
});

const runnable2 = RunnableLambda.from((x: any) => [x].concat([x]));

const chain = RunnableLambda.from((x: number): any => {
  if (x > 6) {
    return runnable1;
  }
  return runnable2;
});

await chain.invoke(7);
```



```output
{ foo: 7 }
```



```typescript
await chain.invoke(5);
```



```output
[ 5, 5 ]
```


### Generate a stream of internal events
#### [runnable.streamEvents()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#streamEvents)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const runnable1 = RunnableLambda.from((x: number) => {
  return {
    foo: x,
  };
}).withConfig({
  runName: "first",
});

async function* generatorFn(x: { foo: number }) {
  for (let i = 0; i < x.foo; i++) {
    yield i.toString();
  }
}

const runnable2 = RunnableLambda.from(generatorFn).withConfig({
  runName: "second",
});

const chain = runnable1.pipe(runnable2);

for await (const event of chain.streamEvents(2, { version: "v1" })) {
  console.log(`event=${event.event} | name=${event.name} | data=${JSON.stringify(event.data)}`);
}
```
```output
event=on_chain_start | name=RunnableSequence | data={"input":2}
event=on_chain_start | name=first | data={}
event=on_chain_stream | name=first | data={"chunk":{"foo":2}}
event=on_chain_start | name=second | data={}
event=on_chain_end | name=first | data={"input":2,"output":{"foo":2}}
event=on_chain_stream | name=second | data={"chunk":"0"}
event=on_chain_stream | name=RunnableSequence | data={"chunk":"0"}
event=on_chain_stream | name=second | data={"chunk":"1"}
event=on_chain_stream | name=RunnableSequence | data={"chunk":"1"}
event=on_chain_end | name=second | data={"output":"01"}
event=on_chain_end | name=RunnableSequence | data={"output":"01"}
```
### Return a subset of keys from output object

#### [runnable.pick()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#pick)


```typescript
import { RunnableLambda, RunnablePassthrough } from "@langchain/core/runnables";

const runnable = RunnableLambda.from((x: { baz: number }) => {
  return x.baz + 5;
});

const chain = RunnablePassthrough.assign({
  foo: runnable,
}).pick(["foo", "bar"]);

await chain.invoke({"bar": "hi", "baz": 2});
```



```output
{ foo: 7, bar: "hi" }
```


### Declaratively make a batched version of a runnable

#### [`runnable.map()`](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#map)


```typescript
import { RunnableLambda } from "@langchain/core/runnables";

const runnable1 = RunnableLambda.from((x: number) => [...Array(x).keys()]);
const runnable2 = RunnableLambda.from((x: number) => x + 5);

const chain = runnable1.pipe(runnable2.map());

await chain.invoke(3);
```



```output
[ 5, 6, 7 ]
```


### Get a graph representation of a runnable

#### [runnable.getGraph()](https://api.js.langchain.com/classes/langchain_core.runnables.Runnable.html#getGraph)


```typescript
import { RunnableLambda, RunnableSequence } from "@langchain/core/runnables";

const runnable1 = RunnableLambda.from((x: any) => {
  return { foo: x };
});

const runnable2 = RunnableLambda.from((x: any) => [x].concat([x]));

const runnable3 = RunnableLambda.from((x: any) => x.toString());

const chain = RunnableSequence.from([
  runnable1,
  {
    second: runnable2,
    third: runnable3,
  }
]);

await chain.getGraph();
```



```output
Graph {
  nodes: {
    "935c67df-7ae3-4853-9d26-579003c08407": {
      id: "935c67df-7ae3-4853-9d26-579003c08407",
      data: {
        name: "RunnableLambdaInput",
        schema: ZodAny {
          spa: [Function: bound safeParseAsync] AsyncFunction,
          _def: [Object],
          parse: [Function: bound parse],
          safeParse: [Function: bound safeParse],
          parseAsync: [Function: bound parseAsync] AsyncFunction,
          safeParseAsync: [Function: bound safeParseAsync] AsyncFunction,
          refine: [Function: bound refine],
          refinement: [Function: bound refinement],
          superRefine: [Function: bound superRefine],
          optional: [Function: bound optional],
          nullable: [Function: bound nullable],
          nullish: [Function: bound nullish],
          array: [Function: bound array],
          promise: [Function: bound promise],
          or: [Function: bound or],
          and: [Function: bound and],
          transform: [Function: bound transform],
          brand: [Function: bound brand],
          default: [Function: bound default],
          catch: [Function: bound catch],
          describe: [Function: bound describe],
          pipe: [Function: bound pipe],
          readonly: [Function: bound readonly],
          isNullable: [Function: bound isNullable],
          isOptional: [Function: bound isOptional],
          _any: true
        }
      }
    },
    "a73d7b3e-0ed7-46cf-b141-de64ea1e12de": {
      id: "a73d7b3e-0ed7-46cf-b141-de64ea1e12de",
      data: RunnableLambda {
        lc_serializable: false,
        lc_kwargs: { func: [Function (anonymous)] },
        lc_runnable: true,
        name: undefined,
        lc_namespace: [ "langchain_core", "runnables" ],
        func: [Function (anonymous)]
      }
    },
    "ff104b34-c13b-4677-8b82-af70d3548e12": {
      id: "ff104b34-c13b-4677-8b82-af70d3548e12",
      data: RunnableMap {
        lc_serializable: true,
        lc_kwargs: { steps: [Object] },
        lc_runnable: true,
        name: undefined,
        lc_namespace: [ "langchain_core", "runnables" ],
        steps: { second: [RunnableLambda], third: [RunnableLambda] }
      }
    },
    "2dc627dc-1c06-45b1-b14f-bb1f6e689f83": {
      id: "2dc627dc-1c06-45b1-b14f-bb1f6e689f83",
      data: {
        name: "RunnableMapOutput",
        schema: ZodAny {
          spa: [Function: bound safeParseAsync] AsyncFunction,
          _def: [Object],
          parse: [Function: bound parse],
          safeParse: [Function: bound safeParse],
          parseAsync: [Function: bound parseAsync] AsyncFunction,
          safeParseAsync: [Function: bound safeParseAsync] AsyncFunction,
          refine: [Function: bound refine],
          refinement: [Function: bound refinement],
          superRefine: [Function: bound superRefine],
          optional: [Function: bound optional],
          nullable: [Function: bound nullable],
          nullish: [Function: bound nullish],
          array: [Function: bound array],
          promise: [Function: bound promise],
          or: [Function: bound or],
          and: [Function: bound and],
          transform: [Function: bound transform],
          brand: [Function: bound brand],
          default: [Function: bound default],
          catch: [Function: bound catch],
          describe: [Function: bound describe],
          pipe: [Function: bound pipe],
          readonly: [Function: bound readonly],
          isNullable: [Function: bound isNullable],
          isOptional: [Function: bound isOptional],
          _any: true
        }
      }
    }
  },
  edges: [
    {
      source: "935c67df-7ae3-4853-9d26-579003c08407",
      target: "a73d7b3e-0ed7-46cf-b141-de64ea1e12de",
      data: undefined
    },
    {
      source: "ff104b34-c13b-4677-8b82-af70d3548e12",
      target: "2dc627dc-1c06-45b1-b14f-bb1f6e689f83",
      data: undefined
    },
    {
      source: "a73d7b3e-0ed7-46cf-b141-de64ea1e12de",
      target: "ff104b34-c13b-4677-8b82-af70d3548e12",
      data: undefined
    }
  ]
}
```



```typescript

```
