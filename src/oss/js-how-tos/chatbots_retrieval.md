# How to do retrieval

<Info>
**Prerequisites**


This guide assumes familiarity with the following:

- [Chatbots](/oss/tutorials/chatbot)
- [Retrieval-augmented generation](/oss/tutorials/rag)

</Info>

Retrieval is a common technique chatbots use to augment their responses with data outside a chat model’s training data. This section will cover how to implement retrieval in the context of chatbots, but it’s worth noting that retrieval is a very subtle and deep topic.

## Setup

You’ll need to install a few packages, and set any LLM API keys:

```{=mdx}
<Npm2Yarn>
  @langchain/openai @langchain/core cheerio
</Npm2Yarn>
```
Let’s also set up a chat model that we’ll use for the below examples.

```{=mdx}
<ChatModelTabs customVarName="llm" />
```
```typescript
// @lc-docs-hide-cell

import { ChatOpenAI } from "@langchain/openai";

const llm = new ChatOpenAI({
  model: "gpt-4o",
  temperature: 0,
});
```

## Creating a retriever

We’ll use [the LangSmith documentation](https://docs.smith.langchain.com) as source material and store the content in a vectorstore for later retrieval. Note that this example will gloss over some of the specifics around parsing and storing a data source - you can see more [in-depth documentation on creating retrieval systems here](/oss/how-to/#qa-with-rag).

Let’s use a document loader to pull text from the docs:


```typescript
import "cheerio";
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

const loader = new CheerioWebBaseLoader(
  "https://docs.smith.langchain.com/user_guide"
);

const rawDocs = await loader.load();

rawDocs[0].pageContent.length;
```



```output
36687
```


Next, we split it into smaller chunks that the LLM’s context window can handle and store it in a vector database:


```typescript
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";

const textSplitter = new RecursiveCharacterTextSplitter({
  chunkSize: 500,
  chunkOverlap: 0,
});

const allSplits = await textSplitter.splitDocuments(rawDocs);
```

Then we embed and store those chunks in a vector database:


```typescript
import { OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "langchain/vectorstores/memory";

const vectorstore = await MemoryVectorStore.fromDocuments(
  allSplits,
  new OpenAIEmbeddings()
);
```

And finally, let’s create a retriever from our initialized vectorstore:


```typescript
const retriever = vectorstore.asRetriever(4);

const docs = await retriever.invoke("how can langsmith help with testing?");

console.log(docs);
```
```output
[
  Document {
    pageContent: "These test cases can be uploaded in bulk, created on the fly, or exported from application traces. L"... 294 more characters,
    metadata: {
      source: "https://docs.smith.langchain.com/user_guide",
      loc: { lines: { from: 7, to: 7 } }
    }
  },
  Document {
    pageContent: "We provide native rendering of chat messages, functions, and retrieve documents.Initial Test Set​Whi"... 347 more characters,
    metadata: {
      source: "https://docs.smith.langchain.com/user_guide",
      loc: { lines: { from: 6, to: 6 } }
    }
  },
  Document {
    pageContent: "will help in curation of test cases that can help track regressions/improvements and development of "... 393 more characters,
    metadata: {
      source: "https://docs.smith.langchain.com/user_guide",
      loc: { lines: { from: 11, to: 11 } }
    }
  },
  Document {
    pageContent: "that time period — this is especially handy for debugging production issues.LangSmith also allows fo"... 396 more characters,
    metadata: {
      source: "https://docs.smith.langchain.com/user_guide",
      loc: { lines: { from: 11, to: 11 } }
    }
  }
]
```
We can see that invoking the retriever above results in some parts of the LangSmith docs that contain information about testing that our chatbot can use as context when answering questions. And now we’ve got a retriever that can return related data from the LangSmith docs!

## Document chains

Now that we have a retriever that can return LangChain docs, let’s create a chain that can use them as context to answer questions. We’ll use a `createStuffDocumentsChain` helper function to "stuff" all of the input documents into the prompt. It will also handle formatting the docs as strings.

In addition to a chat model, the function also expects a prompt that has a `context` variable, as well as a placeholder for chat history messages named `messages`. We’ll create an appropriate prompt and pass it as shown below:


```typescript
import { createStuffDocumentsChain } from "langchain/chains/combine_documents";
import {
  ChatPromptTemplate,
  MessagesPlaceholder,
} from "@langchain/core/prompts";

const SYSTEM_TEMPLATE = `Answer the user's questions based on the below context. 
If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

<context>
{context}
</context>
`;

const questionAnsweringPrompt = ChatPromptTemplate.fromMessages([
  ["system", SYSTEM_TEMPLATE],
  new MessagesPlaceholder("messages"),
]);

const documentChain = await createStuffDocumentsChain({
  llm,
  prompt: questionAnsweringPrompt,
});
```

We can invoke this `documentChain` by itself to answer questions. Let’s use the docs we retrieved above and the same question, `how can langsmith help with testing?`:


```typescript
import { HumanMessage, AIMessage } from "@langchain/core/messages";

await documentChain.invoke({
  messages: [new HumanMessage("Can LangSmith help test my LLM applications?")],
  context: docs,
});
```



```output
"Yes, LangSmith can help test your LLM applications. It allows developers to create datasets, which a"... 229 more characters
```


Looks good! For comparison, we can try it with no context docs and compare the result:


```typescript
await documentChain.invoke({
  messages: [new HumanMessage("Can LangSmith help test my LLM applications?")],
  context: [],
});
```



```output
"I don't know."
```


We can see that the LLM does not return any results.

## Retrieval chains

Let’s combine this document chain with the retriever. Here’s one way this can look:


```typescript
import type { BaseMessage } from "@langchain/core/messages";
import {
  RunnablePassthrough,
  RunnableSequence,
} from "@langchain/core/runnables";

const parseRetrieverInput = (params: { messages: BaseMessage[] }) => {
  return params.messages[params.messages.length - 1].content;
};

const retrievalChain = RunnablePassthrough.assign({
  context: RunnableSequence.from([parseRetrieverInput, retriever]),
}).assign({
  answer: documentChain,
});
```

Given a list of input messages, we extract the content of the last message in the list and pass that to the retriever to fetch some documents. Then, we pass those documents as context to our document chain to generate a final response.

Invoking this chain combines both steps outlined above:


```typescript
await retrievalChain.invoke({
  messages: [new HumanMessage("Can LangSmith help test my LLM applications?")],
});
```



```output
{
  messages: [
    HumanMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "Can LangSmith help test my LLM applications?",
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "Can LangSmith help test my LLM applications?",
      name: undefined,
      additional_kwargs: {},
      response_metadata: {}
    }
  ],
  context: [
    Document {
      pageContent: "These test cases can be uploaded in bulk, created on the fly, or exported from application traces. L"... 294 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "this guide, we’ll highlight the breadth of workflows LangSmith supports and how they fit into each s"... 343 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "We provide native rendering of chat messages, functions, and retrieve documents.Initial Test Set​Whi"... 347 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "The ability to rapidly understand how the model is performing — and debug where it is failing — is i"... 138 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    }
  ],
  answer: "Yes, LangSmith can help test your LLM applications. It allows developers to create datasets, which a"... 297 more characters
}
```


Looks good!

## Query transformation

Our retrieval chain is capable of answering questions about LangSmith, but there’s a problem - chatbots interact with users conversationally, and therefore have to deal with followup questions.

The chain in its current form will struggle with this. Consider a followup question to our original question like `Tell me more!`. If we invoke our retriever with that query directly, we get documents irrelevant to LLM application testing:


```typescript
await retriever.invoke("Tell me more!");
```



```output
[
  Document {
    pageContent: "Oftentimes, changes in the prompt, retrieval strategy, or model choice can have huge implications in"... 40 more characters,
    metadata: {
      source: "https://docs.smith.langchain.com/user_guide",
      loc: { lines: { from: 8, to: 8 } }
    }
  },
  Document {
    pageContent: "This allows you to quickly test out different prompts and models. You can open the playground from a"... 37 more characters,
    metadata: {
      source: "https://docs.smith.langchain.com/user_guide",
      loc: { lines: { from: 10, to: 10 } }
    }
  },
  Document {
    pageContent: "We provide native rendering of chat messages, functions, and retrieve documents.Initial Test Set​Whi"... 347 more characters,
    metadata: {
      source: "https://docs.smith.langchain.com/user_guide",
      loc: { lines: { from: 6, to: 6 } }
    }
  },
  Document {
    pageContent: "together, making it easier to track the performance of and annotate your application across multiple"... 244 more characters,
    metadata: {
      source: "https://docs.smith.langchain.com/user_guide",
      loc: { lines: { from: 11, to: 11 } }
    }
  }
]
```


This is because the retriever has no innate concept of state, and will only pull documents most similar to the query given. To solve this, we can transform the query into a standalone query without any external references an LLM.

Here’s an example:


```typescript
const queryTransformPrompt = ChatPromptTemplate.fromMessages([
  new MessagesPlaceholder("messages"),
  [
    "user",
    "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
  ],
]);

const queryTransformationChain = queryTransformPrompt.pipe(llm);

await queryTransformationChain.invoke({
  messages: [
    new HumanMessage("Can LangSmith help test my LLM applications?"),
    new AIMessage(
      "Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examples and add them to datasets to expand the surface area of your evaluation sets or to fine-tune a model for improved quality or reduced costs. Additionally, LangSmith can be used to monitor your application, log all traces, visualize latency and token usage statistics, and troubleshoot specific issues as they arise."
    ),
    new HumanMessage("Tell me more!"),
  ],
});
```



```output
AIMessage {
  lc_serializable: true,
  lc_kwargs: {
    content: '"LangSmith LLM application testing and evaluation features"',
    tool_calls: [],
    invalid_tool_calls: [],
    additional_kwargs: { function_call: undefined, tool_calls: undefined },
    response_metadata: {}
  },
  lc_namespace: [ "langchain_core", "messages" ],
  content: '"LangSmith LLM application testing and evaluation features"',
  name: undefined,
  additional_kwargs: { function_call: undefined, tool_calls: undefined },
  response_metadata: {
    tokenUsage: { completionTokens: 11, promptTokens: 144, totalTokens: 155 },
    finish_reason: "stop"
  },
  tool_calls: [],
  invalid_tool_calls: []
}
```


Awesome! That transformed query would pull up context documents related to LLM application testing.

Let’s add this to our retrieval chain. We can wrap our retriever as follows:


```typescript
import { RunnableBranch } from "@langchain/core/runnables";
import { StringOutputParser } from "@langchain/core/output_parsers";

const queryTransformingRetrieverChain = RunnableBranch.from([
  [
    (params: { messages: BaseMessage[] }) => params.messages.length === 1,
    RunnableSequence.from([parseRetrieverInput, retriever]),
  ],
  queryTransformPrompt
    .pipe(llm)
    .pipe(new StringOutputParser())
    .pipe(retriever),
]).withConfig({ runName: "chat_retriever_chain" });
```

Then, we can use this query transformation chain to make our retrieval chain better able to handle such followup questions:



```typescript
const conversationalRetrievalChain = RunnablePassthrough.assign({
  context: queryTransformingRetrieverChain,
}).assign({
  answer: documentChain,
});
```

Awesome! Let’s invoke this new chain with the same inputs as earlier:



```typescript
await conversationalRetrievalChain.invoke({
  messages: [new HumanMessage("Can LangSmith help test my LLM applications?")],
});
```



```output
{
  messages: [
    HumanMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "Can LangSmith help test my LLM applications?",
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "Can LangSmith help test my LLM applications?",
      name: undefined,
      additional_kwargs: {},
      response_metadata: {}
    }
  ],
  context: [
    Document {
      pageContent: "These test cases can be uploaded in bulk, created on the fly, or exported from application traces. L"... 294 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "this guide, we’ll highlight the breadth of workflows LangSmith supports and how they fit into each s"... 343 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "We provide native rendering of chat messages, functions, and retrieve documents.Initial Test Set​Whi"... 347 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "The ability to rapidly understand how the model is performing — and debug where it is failing — is i"... 138 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    }
  ],
  answer: "Yes, LangSmith can help test your LLM applications. It allows developers to create datasets, which a"... 297 more characters
}
```



```typescript
await conversationalRetrievalChain.invoke({
  messages: [
    new HumanMessage("Can LangSmith help test my LLM applications?"),
    new AIMessage(
      "Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examples and add them to datasets to expand the surface area of your evaluation sets or to fine-tune a model for improved quality or reduced costs. Additionally, LangSmith can be used to monitor your application, log all traces, visualize latency and token usage statistics, and troubleshoot specific issues as they arise."
    ),
    new HumanMessage("Tell me more!"),
  ],
});
```



```output
{
  messages: [
    HumanMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "Can LangSmith help test my LLM applications?",
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "Can LangSmith help test my LLM applications?",
      name: undefined,
      additional_kwargs: {},
      response_metadata: {}
    },
    AIMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examp"... 317 more characters,
        tool_calls: [],
        invalid_tool_calls: [],
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examp"... 317 more characters,
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      tool_calls: [],
      invalid_tool_calls: []
    },
    HumanMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "Tell me more!",
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "Tell me more!",
      name: undefined,
      additional_kwargs: {},
      response_metadata: {}
    }
  ],
  context: [
    Document {
      pageContent: "These test cases can be uploaded in bulk, created on the fly, or exported from application traces. L"... 294 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "We provide native rendering of chat messages, functions, and retrieve documents.Initial Test Set​Whi"... 347 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "this guide, we’ll highlight the breadth of workflows LangSmith supports and how they fit into each s"... 343 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "will help in curation of test cases that can help track regressions/improvements and development of "... 393 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    }
  ],
  answer: "LangSmith supports a variety of workflows to aid in the development of your applications, from creat"... 607 more characters
}
```


You can check out [this LangSmith trace](https://smith.langchain.com/public/dc4d6bd4-fea5-45df-be94-06ad18882ae9/r) to see the internal query transformation step for yourself.

## Streaming

Because this chain is constructed with LCEL, you can use familiar methods like `.stream()` with it:


```typescript
const stream = await conversationalRetrievalChain.stream({
  messages: [
    new HumanMessage("Can LangSmith help test my LLM applications?"),
    new AIMessage(
      "Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examples and add them to datasets to expand the surface area of your evaluation sets or to fine-tune a model for improved quality or reduced costs. Additionally, LangSmith can be used to monitor your application, log all traces, visualize latency and token usage statistics, and troubleshoot specific issues as they arise."
    ),
    new HumanMessage("Tell me more!"),
  ],
});

for await (const chunk of stream) {
  console.log(chunk);
}
```
```output
{
  messages: [
    HumanMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "Can LangSmith help test my LLM applications?",
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "Can LangSmith help test my LLM applications?",
      name: undefined,
      additional_kwargs: {},
      response_metadata: {}
    },
    AIMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examp"... 317 more characters,
        tool_calls: [],
        invalid_tool_calls: [],
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examp"... 317 more characters,
      name: undefined,
      additional_kwargs: {},
      response_metadata: {},
      tool_calls: [],
      invalid_tool_calls: []
    },
    HumanMessage {
      lc_serializable: true,
      lc_kwargs: {
        content: "Tell me more!",
        additional_kwargs: {},
        response_metadata: {}
      },
      lc_namespace: [ "langchain_core", "messages" ],
      content: "Tell me more!",
      name: undefined,
      additional_kwargs: {},
      response_metadata: {}
    }
  ]
}
{
  context: [
    Document {
      pageContent: "These test cases can be uploaded in bulk, created on the fly, or exported from application traces. L"... 294 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "We provide native rendering of chat messages, functions, and retrieve documents.Initial Test Set​Whi"... 347 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "this guide, we’ll highlight the breadth of workflows LangSmith supports and how they fit into each s"... 343 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    },
    Document {
      pageContent: "will help in curation of test cases that can help track regressions/improvements and development of "... 393 more characters,
      metadata: {
        source: "https://docs.smith.langchain.com/user_guide",
        loc: { lines: [Object] }
      }
    }
  ]
}
{ answer: "" }
{ answer: "Lang" }
{ answer: "Smith" }
{ answer: " offers" }
{ answer: " a" }
{ answer: " comprehensive" }
{ answer: " suite" }
{ answer: " of" }
{ answer: " tools" }
{ answer: " and" }
{ answer: " workflows" }
{ answer: " to" }
{ answer: " support" }
{ answer: " the" }
{ answer: " development" }
{ answer: " and" }
{ answer: " testing" }
{ answer: " of" }
{ answer: " L" }
{ answer: "LM" }
{ answer: " applications" }
{ answer: "." }
{ answer: " Here" }
{ answer: " are" }
{ answer: " some" }
{ answer: " key" }
{ answer: " features" }
{ answer: " and" }
{ answer: " functionalities" }
{ answer: ":\n\n" }
{ answer: "1" }
{ answer: "." }
{ answer: " **" }
{ answer: "Test" }
{ answer: " Case" }
{ answer: " Management" }
{ answer: "**" }
{ answer: ":\n" }
{ answer: "  " }
{ answer: " -" }
{ answer: " **" }
{ answer: "Bulk" }
{ answer: " Upload" }
{ answer: " and" }
{ answer: " Creation" }
{ answer: "**" }
{ answer: ":" }
{ answer: " You" }
{ answer: " can" }
{ answer: " upload" }
{ answer: " test" }
{ answer: " cases" }
{ answer: " in" }
{ answer: " bulk" }
{ answer: "," }
{ answer: " create" }
{ answer: " them" }
{ answer: " on" }
{ answer: " the" }
{ answer: " fly" }
{ answer: "," }
{ answer: " or" }
{ answer: " export" }
{ answer: " them" }
{ answer: " from" }
{ answer: " application" }
{ answer: " traces" }
{ answer: ".\n" }
{ answer: "  " }
{ answer: " -" }
{ answer: " **" }
{ answer: "Datas" }
{ answer: "ets" }
{ answer: "**" }
{ answer: ":" }
{ answer: " Lang" }
{ answer: "Smith" }
{ answer: " allows" }
{ answer: " you" }
{ answer: " to" }
{ answer: " create" }
{ answer: " datasets" }
{ answer: "," }
{ answer: " which" }
{ answer: " are" }
{ answer: " collections" }
{ answer: " of" }
{ answer: " inputs" }
{ answer: " and" }
{ answer: " reference" }
{ answer: " outputs" }
{ answer: "." }
{ answer: " These" }
{ answer: " datasets" }
{ answer: " can" }
{ answer: " be" }
{ answer: " used" }
{ answer: " to" }
{ answer: " run" }
{ answer: " tests" }
{ answer: " on" }
{ answer: " your" }
{ answer: " L" }
{ answer: "LM" }
{ answer: " applications" }
{ answer: ".\n\n" }
{ answer: "2" }
{ answer: "." }
{ answer: " **" }
{ answer: "Custom" }
{ answer: " Evalu" }
{ answer: "ations" }
{ answer: "**" }
{ answer: ":\n" }
{ answer: "  " }
{ answer: " -" }
{ answer: " **" }
{ answer: "LL" }
{ answer: "M" }
{ answer: " and" }
{ answer: " He" }
{ answer: "uristic" }
{ answer: " Based" }
{ answer: "**" }
{ answer: ":" }
{ answer: " You" }
{ answer: " can" }
{ answer: " run" }
{ answer: " custom" }
{ answer: " evaluations" }
{ answer: " using" }
{ answer: " both" }
{ answer: " L" }
{ answer: "LM" }
{ answer: "-based" }
{ answer: " and" }
{ answer: " heuristic" }
{ answer: "-based" }
{ answer: " methods" }
{ answer: " to" }
{ answer: " score" }
{ answer: " test" }
{ answer: " results" }
{ answer: ".\n\n" }
{ answer: "3" }
{ answer: "." }
{ answer: " **" }
{ answer: "Comparison" }
{ answer: " View" }
{ answer: "**" }
{ answer: ":\n" }
{ answer: "  " }
{ answer: " -" }
{ answer: " **" }
{ answer: "Pro" }
{ answer: "tot" }
{ answer: "yp" }
{ answer: "ing" }
{ answer: " and" }
{ answer: " Regression" }
{ answer: " Tracking" }
{ answer: "**" }
{ answer: ":" }
{ answer: " When" }
{ answer: " prot" }
{ answer: "otyping" }
{ answer: " different" }
{ answer: " versions" }
{ answer: " of" }
{ answer: " your" }
{ answer: " applications" }
{ answer: "," }
{ answer: " Lang" }
{ answer: "Smith" }
{ answer: " provides" }
{ answer: " a" }
{ answer: " comparison" }
{ answer: " view" }
{ answer: " to" }
{ answer: " see" }
{ answer: " if" }
{ answer: " there" }
{ answer: " have" }
{ answer: " been" }
{ answer: " any" }
{ answer: " regress" }
{ answer: "ions" }
{ answer: " with" }
{ answer: " respect" }
{ answer: " to" }
{ answer: " your" }
{ answer: " initial" }
{ answer: " test" }
{ answer: " cases" }
{ answer: ".\n\n" }
{ answer: "4" }
{ answer: "." }
{ answer: " **" }
{ answer: "Native" }
{ answer: " Rendering" }
{ answer: "**" }
{ answer: ":\n" }
{ answer: "  " }
{ answer: " -" }
{ answer: " **" }
{ answer: "Chat" }
{ answer: " Messages" }
{ answer: "," }
{ answer: " Functions" }
{ answer: "," }
{ answer: " and" }
{ answer: " Documents" }
{ answer: "**" }
{ answer: ":" }
{ answer: " Lang" }
{ answer: "Smith" }
{ answer: " provides" }
{ answer: " native" }
{ answer: " rendering" }
{ answer: " of" }
{ answer: " chat" }
{ answer: " messages" }
{ answer: "," }
{ answer: " functions" }
{ answer: "," }
{ answer: " and" }
{ answer: " retrieved" }
{ answer: " documents" }
{ answer: "," }
{ answer: " making" }
{ answer: " it" }
{ answer: " easier" }
{ answer: " to" }
{ answer: " visualize" }
{ answer: " and" }
{ answer: " understand" }
{ answer: " the" }
{ answer: " outputs" }
{ answer: ".\n\n" }
{ answer: "5" }
{ answer: "." }
{ answer: " **" }
{ answer: "Pro" }
{ answer: "tot" }
{ answer: "yp" }
{ answer: "ing" }
{ answer: " Support" }
{ answer: "**" }
{ answer: ":\n" }
{ answer: "  " }
{ answer: " -" }
{ answer: " **" }
{ answer: "Quick" }
{ answer: " Experiment" }
{ answer: "ation" }
{ answer: "**" }
{ answer: ":" }
{ answer: " The" }
{ answer: " platform" }
{ answer: " supports" }
{ answer: " quick" }
{ answer: " experimentation" }
{ answer: " with" }
{ answer: " different" }
{ answer: " prompts" }
{ answer: "," }
{ answer: " model" }
{ answer: " types" }
{ answer: "," }
{ answer: " retrieval" }
{ answer: " strategies" }
{ answer: "," }
{ answer: " and" }
{ answer: " other" }
{ answer: " parameters" }
{ answer: ".\n\n" }
{ answer: "6" }
{ answer: "." }
{ answer: " **" }
{ answer: "Feedback" }
{ answer: " Capture" }
{ answer: "**" }
{ answer: ":\n" }
{ answer: "  " }
{ answer: " -" }
{ answer: " **" }
{ answer: "Human" }
{ answer: " Feedback" }
{ answer: "**" }
{ answer: ":" }
{ answer: " When" }
{ answer: " launching" }
{ answer: " your" }
{ answer: " application" }
{ answer: " to" }
{ answer: " an" }
{ answer: " initial" }
{ answer: " set" }
{ answer: " of" }
{ answer: " users" }
{ answer: "," }
{ answer: " Lang" }
{ answer: "Smith" }
{ answer: " allows" }
{ answer: " you" }
{ answer: " to" }
{ answer: " gather" }
{ answer: " human" }
{ answer: " feedback" }
{ answer: " on" }
{ answer: " the" }
{ answer: " responses" }
{ answer: "." }
{ answer: " This" }
{ answer: " helps" }
{ answer: " identify" }
{ answer: " interesting" }
{ answer: " runs" }
{ answer: " and" }
{ answer: " highlight" }
{ answer: " edge" }
{ answer: " cases" }
{ answer: " causing" }
{ answer: " problematic" }
{ answer: " responses" }
{ answer: ".\n" }
{ answer: "  " }
{ answer: " -" }
{ answer: " **" }
{ answer: "Feedback" }
{ answer: " Scores" }
{ answer: "**" }
{ answer: ":" }
{ answer: " You" }
{ answer: " can" }
{ answer: " attach" }
{ answer: " feedback" }
{ answer: " scores" }
{ answer: " to" }
{ answer: " logged" }
{ answer: " traces" }
{ answer: "," }
{ answer: " often" }
{ answer: " integrated" }
{ answer: " into" }
{ answer: " the" }
{ answer: " system" }
{ answer: ".\n\n" }
{ answer: "7" }
{ answer: "." }
{ answer: " **" }
{ answer: "Monitoring" }
{ answer: " and" }
{ answer: " Troubles" }
{ answer: "hooting" }
{ answer: "**" }
{ answer: ":\n" }
{ answer: "  " }
{ answer: " -" }
{ answer: " **" }
{ answer: "Logging" }
{ answer: " and" }
{ answer: " Visualization" }
{ answer: "**" }
{ answer: ":" }
{ answer: " Lang" }
{ answer: "Smith" }
{ answer: " logs" }
{ answer: " all" }
{ answer: " traces" }
{ answer: "," }
{ answer: " visual" }
{ answer: "izes" }
{ answer: " latency" }
{ answer: " and" }
{ answer: " token" }
{ answer: " usage" }
{ answer: " statistics" }
{ answer: "," }
{ answer: " and" }
{ answer: " helps" }
{ answer: " troubleshoot" }
{ answer: " specific" }
{ answer: " issues" }
{ answer: " as" }
{ answer: " they" }
{ answer: " arise" }
{ answer: ".\n\n" }
{ answer: "Overall" }
{ answer: "," }
{ answer: " Lang" }
{ answer: "Smith" }
{ answer: " is" }
{ answer: " designed" }
{ answer: " to" }
{ answer: " support" }
{ answer: " the" }
{ answer: " entire" }
{ answer: " lifecycle" }
{ answer: " of" }
{ answer: " L" }
{ answer: "LM" }
{ answer: " application" }
{ answer: " development" }
{ answer: "," }
{ answer: " from" }
{ answer: " initial" }
{ answer: " prot" }
{ answer: "otyping" }
{ answer: " to" }
{ answer: " deployment" }
{ answer: " and" }
{ answer: " ongoing" }
{ answer: " monitoring" }
{ answer: "," }
{ answer: " making" }
{ answer: " it" }
{ answer: " a" }
{ answer: " powerful" }
{ answer: " tool" }
{ answer: " for" }
{ answer: " developers" }
{ answer: " looking" }
{ answer: " to" }
{ answer: " build" }
{ answer: " and" }
{ answer: " maintain" }
{ answer: " high" }
{ answer: "-quality" }
{ answer: " L" }
{ answer: "LM" }
{ answer: " applications" }
{ answer: "." }
{ answer: "" }
```
## Next steps

You've now learned some techniques for adding personal data as context to your chatbots.

This guide only scratches the surface of retrieval techniques. For more on different ways of ingesting, preparing, and retrieving the most relevant data, check out our [how to guides on retrieval](/oss/how-to/#retrievers).
