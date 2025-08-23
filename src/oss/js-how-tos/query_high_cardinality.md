# How to deal with high cardinality categorical variables

<Info>
**Prerequisites**


This guide assumes familiarity with the following:

- [Query analysis](/oss/tutorials/rag#query-analysis)

</Info>

High cardinality data refers to columns in a dataset that contain a large number of unique values. This guide demonstrates some techniques for dealing with these inputs.

For example, you may want to do query analysis to create a filter on a categorical column. One of the difficulties here is that you usually need to specify the EXACT categorical value. The issue is you need to make sure the LLM generates that categorical value exactly. This can be done relatively easy with prompting when there are only a few values that are valid. When there are a high number of valid values then it becomes more difficult, as those values may not fit in the LLM context, or (if they do) there may be too many for the LLM to properly attend to.

In this notebook we take a look at how to approach this.

## Setup

### Install dependencies

```{=mdx}
import IntegrationInstallTooltip from "@mdx_components/integration_install_tooltip.mdx";
<IntegrationInstallTooltip></IntegrationInstallTooltip>

<Npm2Yarn>
  @langchain/community @langchain/core zod @faker-js/faker
</Npm2Yarn>
```
### Set environment variables

```
# Optional, use LangSmith for best-in-class observability
LANGSMITH_API_KEY=your-api-key
LANGSMITH_TRACING=true

# Reduce tracing latency if you are not in a serverless environment
# LANGCHAIN_CALLBACKS_BACKGROUND=true
```
#### Set up data

We will generate a bunch of fake names


```typescript
import { faker } from "@faker-js/faker";

const names = Array.from({ length: 10000 }, () => (faker as any).person.fullName());
```
Let's look at some of the names


```typescript
names[0]
```
```output
"Rolando Wilkinson"
```



```typescript
names[567]
```



```output
"Homer Harber"
```


## Query Analysis

We can now set up a baseline query analysis


```typescript
import { z } from "zod";

const searchSchema = z.object({
    query: z.string(),
    author: z.string(),
})
```

```{=mdx}
<ChatModelTabs customVarName="llm" />
```
```typescript
// @lc-docs-hide-cell
import { ChatOpenAI } from '@langchain/openai';

const llm = new ChatOpenAI({
  model: "gpt-3.5-turbo",
  temperature: 0,
})
```


```typescript
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { RunnablePassthrough, RunnableSequence } from "@langchain/core/runnables";

const system = `Generate a relevant search query for a library system`;
const prompt = ChatPromptTemplate.fromMessages(
    [
      ["system", system],
      ["human", "{question}"],
    ]
)
const llmWithTools = llm.withStructuredOutput(searchSchema, {
  name: "Search"
})
const queryAnalyzer = RunnableSequence.from([
  {
    question: new RunnablePassthrough(),
  },
  prompt,
  llmWithTools
]);
```

We can see that if we spell the name exactly correctly, it knows how to handle it


```typescript
await queryAnalyzer.invoke("what are books about aliens by Jesse Knight")
```



```output
{ query: "aliens", author: "Jesse Knight" }
```


The issue is that the values you want to filter on may NOT be spelled exactly correctly


```typescript
await queryAnalyzer.invoke("what are books about aliens by jess knight")
```



```output
{ query: "books about aliens", author: "jess knight" }
```


### Add in all values

One way around this is to add ALL possible values to the prompt. That will generally guide the query in the right direction


```typescript
const systemTemplate = `Generate a relevant search query for a library system using the 'search' tool.

The 'author' you return to the user MUST be one of the following authors:

{authors}

Do NOT hallucinate author name!`
const basePrompt = ChatPromptTemplate.fromMessages(
    [
      ["system", systemTemplate],
      ["human", "{question}"],
    ]
)
const promptWithAuthors = await basePrompt.partial({ authors: names.join(", ") })

const queryAnalyzerAll = RunnableSequence.from([
  {
    question: new RunnablePassthrough(),
  },
  promptWithAuthors,
  llmWithTools
])
```

However... if the list of categoricals is long enough, it may error!


```typescript
try {
    const res = await queryAnalyzerAll.invoke("what are books about aliens by jess knight")
} catch (e) {
    console.error(e)
}
```
```output
Error: 400 This model's maximum context length is 16385 tokens. However, your messages resulted in 50197 tokens (50167 in the messages, 30 in the functions). Please reduce the length of the messages or functions.
    at Function.generate (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/openai/4.47.1/error.mjs:41:20)
    at OpenAI.makeStatusError (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/openai/4.47.1/core.mjs:256:25)
    at OpenAI.makeRequest (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/openai/4.47.1/core.mjs:299:30)
    at eventLoopTick (ext:core/01_core.js:63:7)
    at async file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/@langchain/openai/0.0.31/dist/chat_models.js:756:29
    at async RetryOperation._fn (file:///Users/jacoblee/Library/Caches/deno/npm/registry.npmjs.org/p-retry/4.6.2/index.js:50:12) {
  status: 400,
  headers: {
    "alt-svc": 'h3=":443"; ma=86400',
    "cf-cache-status": "DYNAMIC",
    "cf-ray": "885f794b3df4fa52-SJC",
    "content-length": "340",
    "content-type": "application/json",
    date: "Sat, 18 May 2024 23:02:16 GMT",
    "openai-organization": "langchain",
    "openai-processing-ms": "230",
    "openai-version": "2020-10-01",
    server: "cloudflare",
    "set-cookie": "_cfuvid=F_c9lnRuQDUhKiUE2eR2PlsxHPldf1OAVMonLlHTjzM-1716073336256-0.0.1.1-604800000; path=/; domain="... 48 more characters,
    "strict-transport-security": "max-age=15724800; includeSubDomains",
    "x-ratelimit-limit-requests": "10000",
    "x-ratelimit-limit-tokens": "2000000",
    "x-ratelimit-remaining-requests": "9999",
    "x-ratelimit-remaining-tokens": "1958402",
    "x-ratelimit-reset-requests": "6ms",
    "x-ratelimit-reset-tokens": "1.247s",
    "x-request-id": "req_7b88677d6883fac1520e44543f68c839"
  },
  request_id: "req_7b88677d6883fac1520e44543f68c839",
  error: {
    message: "This model's maximum context length is 16385 tokens. However, your messages resulted in 50197 tokens"... 101 more characters,
    type: "invalid_request_error",
    param: "messages",
    code: "context_length_exceeded"
  },
  code: "context_length_exceeded",
  param: "messages",
  type: "invalid_request_error",
  attemptNumber: 1,
  retriesLeft: 6
}
```
We can try to use a longer context window... but with so much information in there, it is not guaranteed to pick it up reliably

```{=mdx}
<ChatModelTabs customVarName="llmLong" openaiParams={`{ model: "gpt-4o-mini" }`} />
```
```typescript
// @lc-docs-hide-cell
import { ChatOpenAI } from '@langchain/openai';

const llmLong = new ChatOpenAI({
  model: "gpt-4o",
  temperature: 0,
})
```


```typescript
const structuredLlmLong = llmLong.withStructuredOutput(searchSchema, {
  name: "Search"
});
const queryAnalyzerAllLong = RunnableSequence.from([
  {
    question: new RunnablePassthrough(),
  },
  prompt,
  structuredLlmLong
]);
```


```typescript
await queryAnalyzerAllLong.invoke("what are books about aliens by jess knight")
```



```output
{ query: "aliens", author: "jess knight" }
```


### Find and all relevant values

Instead, what we can do is create a [vector store index](/oss/concepts/vectorstores) over the relevant values and then query that for the N most relevant values,


```typescript
import { OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "langchain/vectorstores/memory";

const embeddings = new OpenAIEmbeddings({
  model: "text-embedding-3-small",
})
const vectorstore = await MemoryVectorStore.fromTexts(names, {}, embeddings);

const selectNames = async (question: string) => {
  const _docs = await vectorstore.similaritySearch(question, 10);
  const _names = _docs.map(d => d.pageContent);
  return _names.join(", ");
}

const createPrompt = RunnableSequence.from([
  {
      question: new RunnablePassthrough(),
      authors: selectNames,
  },
  basePrompt
])

await createPrompt.invoke("what are books by jess knight")
```



```output
ChatPromptValue {
  lc_serializable: true,
  lc_kwargs: {
    messages: [
      SystemMessage {
        lc_serializable: true,
        lc_kwargs: {
          content: "Generate a relevant search query for a library system using the 'search' tool.\n" +
            "\n" +
            "The 'author' you ret"... 243 more characters,
          additional_kwargs: {},
          response_metadata: {}
        },
        lc_namespace: [ "langchain_core", "messages" ],
        content: "Generate a relevant search query for a library system using the 'search' tool.\n" +
          "\n" +
          "The 'author' you ret"... 243 more characters,
        name: undefined,
        additional_kwargs: {},
        response_metadata: {}
      },
      HumanMessage {
        lc_serializable: true,
        lc_kwargs: {
          content: "what are books by jess knight",
          additional_kwargs: {},
          response_metadata: {}
        },
        lc_namespace: [ "langchain_core", "messages" ],
        content: "what are books by jess knight",
        name: undefined,
        additional_kwargs: {},
        response_metadata: {}
      }
    ]
  },
  lc_namespace: [ "langchain_core", "prompt_values" ],
  messages: [
    SystemMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "Generate a relevant search query for a library system using the 'search' tool.\n" +
          "\n" +
          "The 'author' you ret"... 243 more characters,
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "Generate a relevant search query for a library system using the 'search' tool.\n" +
        "\n" +
        "The 'author' you ret"... 243 more characters,
      name: undefined,
      additional_kwargs: {},
      response_metadata: {}
    },
    HumanMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "what are books by jess knight",
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "what are books by jess knight",
      name: undefined,
      additional_kwargs: {},
      response_metadata: {}
    }
  ]
}
```



```typescript
const queryAnalyzerSelect = createPrompt.pipe(llmWithTools);

await queryAnalyzerSelect.invoke("what are books about aliens by jess knight")
```



```output
{ query: "aliens", author: "Jess Knight" }
```


## Next steps

You've now learned how to deal with high cardinality data when constructing queries.

Next, check out some of the other query analysis guides in this section, like [how to use few-shotting to improve performance](/oss/how-to/query_no_queries).


```typescript

```
