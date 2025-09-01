---
title: Chroma
---


This guide will help you getting started with such a retriever backed by a [Chroma vector store](/oss/integrations/vectorstores/chroma). For detailed documentation of all features and configurations head to the [API reference](https://api.js.langchain.com/classes/langchain.retrievers_self_query.SelfQueryRetriever.html).

## Overview

A [self-query retriever](/oss/how-to/self_query/) retrieves documents by dynamically generating metadata filters based on some input query. This allows the retriever to account for underlying document metadata in addition to pure semantic similarity when fetching results.

It uses a module called a `Translator` that generates a filter based on information about metadata fields and the query language that a given vector store supports.

### Integration details

| Backing vector store | Self-host | Cloud offering | Package | [Py support](https://python.langchain.com/docs/integrations/retrievers/self_query/chroma_self_query/) |
| :--- | :--- | :---: | :---: | :---: |
[`Chroma`](https://api.js.langchain.com/classes/langchain_community_vectorstores_chroma.Chroma.html) | ✅ | ✅ | [`@langchain/community`](https://www.npmjs.com/package/@langchain/community) | ✅ |

## Setup

Set up a Chroma instance as documented [here](/oss/integrations/vectorstores/chroma).

If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

```typescript
// process.env.LANGSMITH_API_KEY = "<YOUR API KEY HERE>";
// process.env.LANGSMITH_TRACING = "true";
```

### Installation

The vector store lives in the `@langchain/community` package. You'll also need to install the `langchain` package to import the main `SelfQueryRetriever` class.

For this example, we'll also use OpenAI embeddings, so you'll need to install the `@langchain/openai` package and [obtain an API key](https://platform.openai.com):

```{=mdx}
import IntegrationInstallTooltip from "@mdx_components/integration_install_tooltip.mdx";
<IntegrationInstallTooltip></IntegrationInstallTooltip>

<Npm2Yarn>
  @langchain/community langchain @langchain/openai @langchain/core
</Npm2Yarn>
```
## Instantiation

First, initialize your Chroma vector store with some documents that contain metadata:


```typescript
import { OpenAIEmbeddings } from "@langchain/openai";
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { Document } from "@langchain/core/documents";
import type { AttributeInfo } from "langchain/chains/query_constructor";

/**
 * First, we create a bunch of documents. You can load your own documents here instead.
 * Each document has a pageContent and a metadata field. Make sure your metadata matches the AttributeInfo below.
 */
const docs = [
  new Document({
    pageContent:
      "A bunch of scientists bring back dinosaurs and mayhem breaks loose",
    metadata: { year: 1993, rating: 7.7, genre: "science fiction" },
  }),
  new Document({
    pageContent:
      "Leo DiCaprio gets lost in a dream within a dream within a dream within a ...",
    metadata: { year: 2010, director: "Christopher Nolan", rating: 8.2 },
  }),
  new Document({
    pageContent:
      "A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea",
    metadata: { year: 2006, director: "Satoshi Kon", rating: 8.6 },
  }),
  new Document({
    pageContent:
      "A bunch of normal-sized women are supremely wholesome and some men pine after them",
    metadata: { year: 2019, director: "Greta Gerwig", rating: 8.3 },
  }),
  new Document({
    pageContent: "Toys come alive and have a blast doing so",
    metadata: { year: 1995, genre: "animated" },
  }),
  new Document({
    pageContent: "Three men walk into the Zone, three men walk out of the Zone",
    metadata: {
      year: 1979,
      director: "Andrei Tarkovsky",
      genre: "science fiction",
      rating: 9.9,
    },
  }),
];

/**
 * Next, we define the attributes we want to be able to query on.
 * in this case, we want to be able to query on the genre, year, director, rating, and length of the movie.
 * We also provide a description of each attribute and the type of the attribute.
 * This is used to generate the query prompts.
 */
const attributeInfo: AttributeInfo[] = [
  {
    name: "genre",
    description: "The genre of the movie",
    type: "string or array of strings",
  },
  {
    name: "year",
    description: "The year the movie was released",
    type: "number",
  },
  {
    name: "director",
    description: "The director of the movie",
    type: "string",
  },
  {
    name: "rating",
    description: "The rating of the movie (1-10)",
    type: "number",
  },
  {
    name: "length",
    description: "The length of the movie in minutes",
    type: "number",
  },
];

/**
 * Next, we instantiate a vector store. This is where we store the embeddings of the documents.
 * We also need to provide an embeddings object. This is used to embed the documents.
 */
const embeddings = new OpenAIEmbeddings();
const vectorStore = await Chroma.fromDocuments(docs, embeddings, {
  collectionName: "movie-collection",
});
```
Now we can instantiate our retriever:

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
import { SelfQueryRetriever } from "langchain/retrievers/self_query";
import { ChromaTranslator } from "@langchain/community/structured_query/chroma";

const selfQueryRetriever = SelfQueryRetriever.fromLLM({
  llm,
  vectorStore,
  /** A short summary of what the document contents represent. */
  documentContents: "Brief summary of a movie",
  attributeInfo,
  /**
   * We need to create a basic translator that translates the queries into a
   * filter format that the vector store can understand. We provide a basic translator
   * translator here, but you can create your own translator by extending BaseTranslator
   * abstract class. Note that the vector store needs to support filtering on the metadata
   * attributes you want to query on.
   */
  structuredQueryTranslator: new ChromaTranslator(),
});
```

## Usage

Now, ask a question that requires some knowledge of the document's metadata to answer. You can see that the retriever will generate the correct result:


```typescript
await selfQueryRetriever.invoke(
  "Which movies are rated higher than 8.5?"
);
```
```output
[
  Document {
    pageContent: 'A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea',
    metadata: { director: 'Satoshi Kon', rating: 8.6, year: 2006 },
    id: undefined
  },
  Document {
    pageContent: 'Three men walk into the Zone, three men walk out of the Zone',
    metadata: {
      director: 'Andrei Tarkovsky',
      genre: 'science fiction',
      rating: 9.9,
      year: 1979
    },
    id: undefined
  }
]
```
## Use within a chain

Like other retrievers, Chroma self-query retrievers can be incorporated into LLM applications via [chains](/oss/how-to/sequence/).

Note that because their returned answers can heavily depend on document metadata, we format the retrieved documents differently to include that information.


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
  return docs.map((doc) => JSON.stringify(doc)).join("\n\n");
}

// See https://js.langchain.com/docs/tutorials/rag
const ragChain = RunnableSequence.from([
  {
    context: selfQueryRetriever.pipe(formatDocs),
    question: new RunnablePassthrough(),
  },
  prompt,
  llm,
  new StringOutputParser(),
]);
```


```typescript
await ragChain.invoke("Which movies are rated higher than 8.5?")
```
```output
The movies rated higher than 8.5 are:

1. The movie directed by Andrei Tarkovsky, which has a rating of 9.9. 
2. The movie directed by Satoshi Kon, which has a rating of 8.6.
```
## Default search params

You can also pass a `searchParams` field into the above method that provides default filters applied in addition to any generated query. The filter syntax is the same as the backing Chroma vector store:


```typescript
const selfQueryRetrieverWithDefaultParams = SelfQueryRetriever.fromLLM({
  llm,
  vectorStore,
  documentContents: "Brief summary of a movie",
  attributeInfo,
  structuredQueryTranslator: new ChromaTranslator(),
  searchParams: {
    filter: {
      rating: {
        $gt: 8.5,
      }
    },
    mergeFiltersOperator: "and",
  }
});
```

## API reference

For detailed documentation of all Chroma self-query retriever features and configurations head to the [API reference](https://api.js.langchain.com/classes/langchain.retrievers_self_query.SelfQueryRetriever.html).
