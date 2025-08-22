---
title: RedisVectorStore
---

```{=mdx}
<Tip>
**Compatibility**

Only available on Node.js.
</Tip>
```
[Redis](https://redis.io/) is a fast open source, in-memory data store. As part of the [Redis Stack](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/), [RediSearch](https://redis.io/docs/latest/develop/interact/search-and-query/) is the module that enables vector similarity semantic search, as well as many other types of searching.

This guide provides a quick overview for getting started with Redis [vector stores](/oss/concepts/#vectorstores). For detailed documentation of all `RedisVectorStore` features and configurations head to the [API reference](https://api.js.langchain.com/classes/langchain_redis.RedisVectorStore.html).

## Overview

### Integration details

| Class | Package | [PY support](https://python.langchain.com/docs/integrations/vectorstores/redis/) |  Package latest |
| :--- | :--- | :---: | :---: |
| [`RedisVectorStore`](https://api.js.langchain.com/classes/langchain_redis.RedisVectorStore.html) | [`@langchain/redis`](https://npmjs.com/@langchain/redis/) | ✅ |  ![NPM - Version](https://img.shields.io/npm/v/@langchain/redis?style=flat-square&label=%20&) |

## Setup

To use Redis vector stores, you'll need to set up a Redis instance and install the `@langchain/redis` integration package. You can also install the [`node-redis`](https://github.com/redis/node-redis) package to initialize the vector store with a specific client instance.

This guide will also use [OpenAI embeddings](/oss/integrations/text_embedding/openai), which require you to install the `@langchain/openai` integration package. You can also use [other supported embeddings models](/oss/integrations/text_embedding) if you wish.

```{=mdx}
import IntegrationInstallTooltip from "@mdx_components/integration_install_tooltip.mdx";
<IntegrationInstallTooltip></IntegrationInstallTooltip>

<Npm2Yarn>
  @langchain/redis @langchain/core redis @langchain/openai
</Npm2Yarn>
```
You can set up a Redis instance locally with Docker by following [these instructions](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/#redisredis-stack).

### Credentials

Once you've set up an instance, set the `REDIS_URL` environment variable:

```typescript
process.env.REDIS_URL = "your-redis-url"
```
If you are using OpenAI embeddings for this guide, you'll need to set your OpenAI key as well:

```typescript
process.env.OPENAI_API_KEY = "YOUR_API_KEY";
```
If you want to get automated tracing of your model calls you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

```typescript
// process.env.LANGSMITH_TRACING="true"
// process.env.LANGSMITH_API_KEY="your-api-key"
```
## Instantiation


```typescript
import { RedisVectorStore } from "@langchain/redis";
import { OpenAIEmbeddings } from "@langchain/openai";

import { createClient } from "redis";

const embeddings = new OpenAIEmbeddings({
  model: "text-embedding-3-small",
});

const client = createClient({
  url: process.env.REDIS_URL ?? "redis://localhost:6379",
});
await client.connect();

const vectorStore = new RedisVectorStore(embeddings, {
  redisClient: client,
  indexName: "langchainjs-testing",
});
```
## Manage vector store

### Add items to vector store


```typescript
import type { Document } from "@langchain/core/documents";

const document1: Document = {
  pageContent: "The powerhouse of the cell is the mitochondria",
  metadata: { type: "example" }
};

const document2: Document = {
  pageContent: "Buildings are made out of brick",
  metadata: { type: "example" }
};

const document3: Document = {
  pageContent: "Mitochondria are made out of lipids",
  metadata: { type: "example" }
};

const document4: Document = {
  pageContent: "The 2024 Olympics are in Paris",
  metadata: { type: "example" }
}

const documents = [document1, document2, document3, document4];

await vectorStore.addDocuments(documents);
```
Top-level document ids and deletion are currently not supported.

## Query vector store

Once your vector store has been created and the relevant documents have been added you will most likely wish to query it during the running of your chain or agent. 

### Query directly

Performing a simple similarity search can be done as follows:


```typescript
const similaritySearchResults = await vectorStore.similaritySearch("biology", 2);

for (const doc of similaritySearchResults) {
  console.log(`* ${doc.pageContent} [${JSON.stringify(doc.metadata, null)}]`);
}
```
Filtering will currently look for any metadata key containing the provided string.

If you want to execute a similarity search and receive the corresponding scores you can run:


```typescript
const similaritySearchWithScoreResults = await vectorStore.similaritySearchWithScore("biology", 2)

for (const [doc, score] of similaritySearchWithScoreResults) {
  console.log(`* [SIM=${score.toFixed(3)}] ${doc.pageContent} [${JSON.stringify(doc.metadata)}]`);
}
```
```output
* [SIM=0.835] The powerhouse of the cell is the mitochondria [{"type":"example"}]
* [SIM=0.852] Mitochondria are made out of lipids [{"type":"example"}]
```
### Query by turning into retriever

You can also transform the vector store into a [retriever](/oss/concepts/retrievers) for easier usage in your chains. 


```typescript
const retriever = vectorStore.asRetriever({
  k: 2,
});
await retriever.invoke("biology");
```
```output
[
  Document {
    pageContent: 'The powerhouse of the cell is the mitochondria',
    metadata: { type: 'example' },
    id: undefined
  },
  Document {
    pageContent: 'Mitochondria are made out of lipids',
    metadata: { type: 'example' },
    id: undefined
  }
]
```
### Usage for retrieval-augmented generation

For guides on how to use this vector store for retrieval-augmented generation (RAG), see the following sections:

- [Tutorials: working with external knowledge](/oss/tutorials/#working-with-external-knowledge).
- [How-to: Question and answer with RAG](/oss/how-to/#qa-with-rag)
- [Retrieval conceptual docs](/oss/concepts/retrieval)

## Deleting an index

You can delete an entire index with the following command:


```typescript
await vectorStore.delete({ deleteAll: true });
```

## Closing connections

Make sure you close the client connection when you are finished to avoid excessive resource consumption:


```typescript
await client.disconnect();
```

## API reference

For detailed documentation of all `RedisVectorSearch` features and configurations head to the [API reference](https://api.js.langchain.com/classes/langchain_redis.RedisVectorStore.html).
