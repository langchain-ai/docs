# How to use LangChain tools

Tools are interfaces that an agent, chain, or LLM can use to interact with the world.
They combine a few things:

1. The name of the tool
2. A description of what the tool is
3. JSON schema of what the inputs to the tool are
4. The function to call 
5. Whether the result of a tool should be returned directly to the user

It is useful to have all this information because this information can be used to build action-taking systems! The name, description, and schema can be used to prompt the LLM so it knows how to specify what action to take, and then the function to call is equivalent to taking that action.

The simpler the input to a tool is, the easier it is for an LLM to be able to use it.
Many agents will only work with tools that have a single string input.

Importantly, the name, description, and schema (if used) are all used in the prompt. Therefore, it is vitally important that they are clear and describe exactly how the tool should be used.

## Default Tools

Let's take a look at how to work with tools. To do this, we'll work with a built in tool.


```typescript
import { WikipediaQueryRun } from "@langchain/community/tools/wikipedia_query_run";

const tool = new WikipediaQueryRun({
  topKResults: 1,
  maxDocContentLength: 100,
});
```

This is the default name:


```typescript
tool.name;
```



```output
"wikipedia-api"
```


This is the default description:


```typescript
tool.description;
```



```output
"A tool for interacting with and fetching data from the Wikipedia API."
```


This is the default schema of the inputs. This is a [Zod](https://zod.dev) schema on the tool class. We convert it to JSON schema for display purposes:


```typescript
import { zodToJsonSchema } from "zod-to-json-schema";

zodToJsonSchema(tool.schema);
```



```output
{
  type: "object",
  properties: { input: { type: "string" } },
  additionalProperties: false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```


We can see if the tool should return directly to the user


```typescript
tool.returnDirect;
```



```output
false
```


We can invoke this tool with an object input:


```typescript
await tool.invoke({ input: "langchain" })
```



```output
"Page: LangChain\n" +
  "Summary: LangChain is a framework designed to simplify the creation of applications "
```


We can also invoke this tool with a single string input. 
We can do this because this tool expects only a single input.
If it required multiple inputs, we would not be able to do that.


```typescript
await tool.invoke("langchain")
```



```output
"Page: LangChain\n" +
  "Summary: LangChain is a framework designed to simplify the creation of applications "
```


## How to use built-in toolkits

Toolkits are collections of tools that are designed to be used together for specific tasks. They have convenient loading methods.

For a complete list of available ready-made toolkits, visit [Integrations](/oss/integrations/toolkits/).

All Toolkits expose a `getTools()` method which returns a list of tools.

You're usually meant to use them this way:

```ts
// Initialize a toolkit
const toolkit = new ExampleTookit(...);

// Get list of tools
const tools = toolkit.getTools();
```

## More Topics

This was a quick introduction to tools in LangChain, but there is a lot more to learn

**[Built-In Tools](/oss/integrations/tools/)**: For a list of all built-in tools, see [this page](/oss/integrations/tools/)
    
**[Custom Tools](/oss/how-to/custom_tools)**: Although built-in tools are useful, it's highly likely that you'll have to define your own tools. See [this guide](/oss/how-to/custom_tools) for instructions on how to do so.
