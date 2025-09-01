---
title: AWSKendraRetriever
---

## Overview

[Amazon Kendra](https://aws.amazon.com/kendra/) is an intelligent search service provided by Amazon Web Services (AWS).
It utilizes advanced natural language processing (NLP) and machine learning algorithms to enable powerful search capabilities across various data sources within an organization.
Kendra is designed to help users find the information they need quickly and accurately, improving productivity and decision-making.

With Kendra, users can search across a wide range of content types, including documents, FAQs, knowledge bases, manuals, and websites.
It supports multiple languages and can understand complex queries, synonyms, and contextual meanings to provide highly relevant search results.

This will help you getting started with the Amazon Kendra [`retriever`](/oss/concepts/retrievers). For detailed documentation of all `AWSKendraRetriever` features and configurations head to the [API reference](https://api.js.langchain.com/classes/langchain_aws.AmazonKendraRetriever.html).

### Integration details

| Retriever | Source | Package |
| :--- | :--- | :---: |
[AWSKendraRetriever](https://api.js.langchain.com/classes/langchain_aws.AmazonKendraRetriever.html) | Various AWS resources | [`@langchain/aws`](https://www.npmjs.com/package/@langchain/aws) |

## Setup

You'll need an AWS account and an Amazon Kendra instance to get started. See this [tutorial](https://docs.aws.amazon.com/kendra/latest/dg/getting-started.html) from AWS for more information.

If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

```typescript
// process.env.LANGSMITH_API_KEY = "<YOUR API KEY HERE>";
// process.env.LANGSMITH_TRACING = "true";
```

### Installation

This retriever lives in the `@langchain/aws` package:

```{=mdx}
import IntegrationInstallTooltip from "@mdx_components/integration_install_tooltip.mdx";
<IntegrationInstallTooltip></IntegrationInstallTooltip>

<Npm2Yarn>
  @langchain/aws @langchain/core
</Npm2Yarn>
```
## Instantiation

Now we can instantiate our retriever:


```typescript
import { AmazonKendraRetriever } from "@langchain/aws";

const retriever = new AmazonKendraRetriever({
  topK: 10,
  indexId: "YOUR_INDEX_ID",
  region: "us-east-2", // Your region
  clientOptions: {
    credentials: {
      accessKeyId: "YOUR_ACCESS_KEY_ID",
      secretAccessKey: "YOUR_SECRET_ACCESS_KEY",
    },
  },
});
```
## Usage


```typescript
const query = "..."

await retriever.invoke(query);
```
## Use within a chain

Like other retrievers, the `AWSKendraRetriever` can be incorporated into LLM applications via [chains](/oss/how-to/sequence/).

We will need a LLM or chat model:

```{=mdx}
<ChatModelTabs customVarName="llm" />
```
```typescript
// @lc-docs-hide-cell

import { ChatOpenAI } from "@langchain/openai";

const llm = new ChatOpenAI({
  model: "gpt-4o-mini",
  temperature: 0,
});
```


```typescript
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { RunnablePassthrough, RunnableSequence } from "@langchain/core/runnables";
import { StringOutputParser } from "@langchain/core/output_parsers";

import type { Document } from "@langchain/core/documents";

const prompt = ChatPromptTemplate.fromTemplate(`
Answer the question based only on the context provided.

Context: {context}

Question: {question}`);

const formatDocs = (docs: Document[]) => {
  return docs.map((doc) => doc.pageContent).join("\n\n");
}

// See https://js.langchain.com/docs/tutorials/rag
const ragChain = RunnableSequence.from([
  {
    context: retriever.pipe(formatDocs),
    question: new RunnablePassthrough(),
  },
  prompt,
  llm,
  new StringOutputParser(),
]);
```


```typescript
await ragChain.invoke(query);
```

## API reference

For detailed documentation of all `AmazonKendraRetriever` features and configurations head to the [API reference](https://api.js.langchain.com/classes/langchain_aws.AmazonKendraRetriever.html).
