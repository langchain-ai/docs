# How to add chat history


<Note>
**This tutorial previously built a chatbot using [RunnableWithMessageHistory](https://api.js.langchain.com/classes/_langchain_core.runnables.RunnableWithMessageHistory.html). You can access this version of the tutorial in the [v0.2 docs](https://js.langchain.com/v0.2/docs/how_to/qa_chat_history_how_to/).**


The LangGraph implementation offers a number of advantages over `RunnableWithMessageHistory`, including the ability to persist arbitrary components of an application's state (instead of only messages).

</Note>

In many Q&A applications we want to allow the user to have a back-and-forth conversation, meaning the application needs some sort of "memory" of past questions and answers, and some logic for incorporating those into its current thinking.

In this guide we focus on **adding logic for incorporating historical messages.**

This is largely a condensed version of the [Conversational RAG tutorial](/oss/tutorials/qa_chat_history).

We will cover two approaches:

1. [Chains](/oss/how-to/qa_chat_history_how_to#chains), in which we always execute a retrieval step;
2. [Agents](/oss/how-to/qa_chat_history_how_to#agents), in which we give an LLM discretion over whether and how to execute a retrieval step (or multiple steps).

For the external knowledge source, we will use the same [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) blog post by Lilian Weng from the [RAG tutorial](/oss/tutorials/rag).

## Setup
### Dependencies

We’ll use an OpenAI chat model and embeddings and a Memory vector store in this walkthrough, but everything shown here works with any [ChatModel](/oss/concepts/chat_models) or [LLM](/oss/concepts/text_llms), [Embeddings](/oss/concepts/embedding_models), and [VectorStore](/oss/concepts/vectorstores) or [Retriever](/oss/concepts/retrievers).

We’ll use the following packages:

```bash
npm install --save langchain @langchain/openai langchain cheerio uuid
```

We need to set environment variable `OPENAI_API_KEY`:

```bash
export OPENAI_API_KEY=YOUR_KEY
```

### LangSmith

Many of the applications you build with LangChain will contain multiple steps with multiple invocations of LLM calls. As these applications get more and more complex, it becomes crucial to be able to inspect what exactly is going on inside your chain or agent. The best way to do this is with [LangSmith](https://docs.smith.langchain.com).

Note that LangSmith is not needed, but it is helpful. If you do want to use LangSmith, after you sign up at the link above, make sure to set your environment variables to start logging traces:


```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=YOUR_KEY

# Reduce tracing latency if you are not in a serverless environment
# export LANGCHAIN_CALLBACKS_BACKGROUND=true
```

## Chains {#chains}

In a conversational RAG application, queries issued to the retriever should be informed by the context of the conversation. LangChain provides a [createHistoryAwareRetriever](https://api.js.langchain.com/functions/langchain.chains_history_aware_retriever.createHistoryAwareRetriever.html) constructor to simplify this. It constructs a chain that accepts keys `input` and `chat_history` as input, and has the same output schema as a retriever. `createHistoryAwareRetriever` requires as inputs:  

1. LLM;
2. Retriever;
3. Prompt.

First we obtain these objects:

### LLM

We can use any supported chat model:

```{=mdx}
import ChatModelTabs from "@theme/ChatModelTabs"

<ChatModelTabs customVarName="llm" />
```
```typescript
// @lc-docs-hide-cell
import { ChatOpenAI } from "@langchain/openai";

const llm = new ChatOpenAI({ model: "gpt-4o" });
```

### Initial setup


```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { MemoryVectorStore } from "langchain/vectorstores/memory"
import { OpenAIEmbeddings } from "@langchain/openai";

const loader = new CheerioWebBaseLoader(
  "https://lilianweng.github.io/posts/2023-06-23-agent/"
);

const docs = await loader.load();

const textSplitter = new RecursiveCharacterTextSplitter({ chunkSize: 1000, chunkOverlap: 200 });
const splits = await textSplitter.splitDocuments(docs);
const vectorStore = await MemoryVectorStore.fromDocuments(splits, new OpenAIEmbeddings());

// Retrieve and generate using the relevant snippets of the blog.
const retriever = vectorStore.asRetriever();
```

### Prompt

We'll use a prompt that includes a `MessagesPlaceholder` variable under the name "chat_history". This allows us to pass in a list of Messages to the prompt using the "chat_history" input key, and these messages will be inserted after the system message and before the human message containing the latest question.


```typescript
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";

const contextualizeQSystemPrompt = (
  "Given a chat history and the latest user question " +
  "which might reference context in the chat history, " +
  "formulate a standalone question which can be understood " +
  "without the chat history. Do NOT answer the question, " +
  "just reformulate it if needed and otherwise return it as is."
)

const contextualizeQPrompt = ChatPromptTemplate.fromMessages(
  [
    ["system", contextualizeQSystemPrompt],
    new MessagesPlaceholder("chat_history"),
    ["human", "{input}"],
  ]
)
```

### Assembling the chain

We can then instantiate the history-aware retriever:


```typescript
import { createHistoryAwareRetriever } from "langchain/chains/history_aware_retriever";

const historyAwareRetriever = await createHistoryAwareRetriever({
  llm,
  retriever,
  rephrasePrompt: contextualizeQPrompt
});

```

This chain prepends a rephrasing of the input query to our retriever, so that the retrieval incorporates the context of the conversation.

Now we can build our full QA chain.

As in the [RAG tutorial](/oss/tutorials/rag), we will use [createStuffDocumentsChain](https://api.js.langchain.com/functions/langchain.chains_combine_documents.createStuffDocumentsChain.html) to generate a `questionAnswerChain`, with input keys `context`, `chat_history`, and `input`-- it accepts the retrieved context alongside the conversation history and query to generate an answer.

We build our final `ragChain` with [createRetrievalChain](https://api.js.langchain.com/functions/langchain.chains_retrieval.createRetrievalChain.html). This chain applies the `historyAwareRetriever` and `questionAnswerChain` in sequence, retaining intermediate outputs such as the retrieved context for convenience. It has input keys `input` and `chat_history`, and includes `input`, `chat_history`, `context`, and `answer` in its output.


```typescript
import { createStuffDocumentsChain } from "langchain/chains/combine_documents";
import { createRetrievalChain } from "langchain/chains/retrieval";

const systemPrompt = 
  "You are an assistant for question-answering tasks. " +
  "Use the following pieces of retrieved context to answer " +
  "the question. If you don't know the answer, say that you " +
  "don't know. Use three sentences maximum and keep the " +
  "answer concise." +
  "\n\n" +
  "{context}";

const qaPrompt = ChatPromptTemplate.fromMessages([
  ["system", systemPrompt],
  new MessagesPlaceholder("chat_history"),
  ["human", "{input}"],
]);

const questionAnswerChain = await createStuffDocumentsChain({
  llm,
  prompt: qaPrompt,
});

const ragChain = await createRetrievalChain({
  retriever: historyAwareRetriever,
  combineDocsChain: questionAnswerChain,
});
```

### Stateful Management of chat history

We have added application logic for incorporating chat history, but we are still manually plumbing it through our application. In production, the Q&A application we usually persist the chat history into a database, and be able to read and update it appropriately.

[LangGraph](https://langchain-ai.github.io/langgraphjs/) implements a built-in [persistence layer](https://langchain-ai.github.io/langgraphjs/concepts/persistence/), making it ideal for chat applications that support multiple conversational turns.

Wrapping our chat model in a minimal LangGraph application allows us to automatically persist the message history, simplifying the development of multi-turn applications.

LangGraph comes with a simple [in-memory checkpointer](https://langchain-ai.github.io/langgraphjs/reference/classes/checkpoint.MemorySaver.html), which we use below. See its documentation for more detail, including how to use different persistence backends (e.g., SQLite or Postgres).

For a detailed walkthrough of how to manage message history, head to the How to add message history (memory) guide.


```typescript
import { AIMessage, BaseMessage, HumanMessage } from "@langchain/core/messages";
import { StateGraph, START, END, MemorySaver, messagesStateReducer, Annotation } from "@langchain/langgraph";

// Define the State interface
const GraphAnnotation = Annotation.Root({
  input: Annotation<string>(),
  chat_history: Annotation<BaseMessage[]>({
    reducer: messagesStateReducer,
    default: () => [],
  }),
  context: Annotation<string>(),
  answer: Annotation<string>(),
})

// Define the call_model function
async function callModel(state: typeof GraphAnnotation.State) {
  const response = await ragChain.invoke(state);
  return {
    chat_history: [
      new HumanMessage(state.input),
      new AIMessage(response.answer),
    ],
    context: response.context,
    answer: response.answer,
  };
}

// Create the workflow
const workflow = new StateGraph(GraphAnnotation)
  .addNode("model", callModel)
  .addEdge(START, "model")
  .addEdge("model", END);

// Compile the graph with a checkpointer object
const memory = new MemorySaver();
const app = workflow.compile({ checkpointer: memory });
```


```typescript
import { v4 as uuidv4 } from "uuid";

const threadId = uuidv4();
const config = { configurable: { thread_id: threadId } };

const result = await app.invoke(
  { input: "What is Task Decomposition?" },
  config,
)
console.log(result.answer);
```
```output
Task Decomposition is the process of breaking down a complicated task into smaller, simpler, and more manageable steps. Techniques like Chain of Thought (CoT) and Tree of Thoughts expand on this by enabling agents to think step by step or explore multiple reasoning possibilities at each step. This allows for a more structured and interpretable approach to handling complex tasks.
```

```typescript
const result2 = await app.invoke(
  { input: "What is one way of doing it?" },
  config,
)
console.log(result2.answer);
```
```output
One way of doing task decomposition is by using an LLM with simple prompting, such as asking "Steps for XYZ.\n1." or "What are the subgoals for achieving XYZ?" This method leverages direct prompts to guide the model in breaking down tasks.
```
The conversation history can be inspected via the state of the application:


```typescript
const chatHistory = (await app.getState(config)).values.chat_history;
for (const message of chatHistory) {
  console.log(message);
}
```
```output
HumanMessage {
  "content": "What is Task Decomposition?",
  "additional_kwargs": {},
  "response_metadata": {}
}
AIMessage {
  "content": "Task Decomposition is the process of breaking down a complicated task into smaller, simpler, and more manageable steps. Techniques like Chain of Thought (CoT) and Tree of Thoughts expand on this by enabling agents to think step by step or explore multiple reasoning possibilities at each step. This allows for a more structured and interpretable approach to handling complex tasks.",
  "additional_kwargs": {},
  "response_metadata": {},
  "tool_calls": [],
  "invalid_tool_calls": []
}
HumanMessage {
  "content": "What is one way of doing it?",
  "additional_kwargs": {},
  "response_metadata": {}
}
AIMessage {
  "content": "One way of doing task decomposition is by using an LLM with simple prompting, such as asking \"Steps for XYZ.\\n1.\" or \"What are the subgoals for achieving XYZ?\" This method leverages direct prompts to guide the model in breaking down tasks.",
  "additional_kwargs": {},
  "response_metadata": {},
  "tool_calls": [],
  "invalid_tool_calls": []
}
```
### Tying it together

![](../../static/img/conversational_retrieval_chain.png)

For convenience, we tie together all of the necessary steps in a single code cell:


```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { MemoryVectorStore } from "langchain/vectorstores/memory"
import { OpenAIEmbeddings, ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { createHistoryAwareRetriever } from "langchain/chains/history_aware_retriever";
import { createStuffDocumentsChain } from "langchain/chains/combine_documents";
import { createRetrievalChain } from "langchain/chains/retrieval";
import { AIMessage, BaseMessage, HumanMessage } from "@langchain/core/messages";
import { StateGraph, START, END, MemorySaver, messagesStateReducer, Annotation } from "@langchain/langgraph";
import { v4 as uuidv4 } from "uuid";

const llm2 = new ChatOpenAI({ model: "gpt-4o" });

const loader2 = new CheerioWebBaseLoader(
  "https://lilianweng.github.io/posts/2023-06-23-agent/"
);

const docs2 = await loader2.load();

const textSplitter2 = new RecursiveCharacterTextSplitter({ chunkSize: 1000, chunkOverlap: 200 });
const splits2 = await textSplitter2.splitDocuments(docs2);
const vectorStore2 = await MemoryVectorStore.fromDocuments(splits2, new OpenAIEmbeddings());

// Retrieve and generate using the relevant snippets of the blog.
const retriever2 = vectorStore2.asRetriever();

const contextualizeQSystemPrompt2 =
  "Given a chat history and the latest user question " +
  "which might reference context in the chat history, " +
  "formulate a standalone question which can be understood " +
  "without the chat history. Do NOT answer the question, " +
  "just reformulate it if needed and otherwise return it as is.";

const contextualizeQPrompt2 = ChatPromptTemplate.fromMessages(
  [
    ["system", contextualizeQSystemPrompt2],
    new MessagesPlaceholder("chat_history"),
    ["human", "{input}"],
  ]
)

const historyAwareRetriever2 = await createHistoryAwareRetriever({
  llm: llm2,
  retriever: retriever2,
  rephrasePrompt: contextualizeQPrompt2
});

const systemPrompt2 = 
  "You are an assistant for question-answering tasks. " +
  "Use the following pieces of retrieved context to answer " +
  "the question. If you don't know the answer, say that you " +
  "don't know. Use three sentences maximum and keep the " +
  "answer concise." +
  "\n\n" +
  "{context}";

const qaPrompt2 = ChatPromptTemplate.fromMessages([
  ["system", systemPrompt2],
  new MessagesPlaceholder("chat_history"),
  ["human", "{input}"],
]);

const questionAnswerChain2 = await createStuffDocumentsChain({
  llm: llm2,
  prompt: qaPrompt2,
});

const ragChain2 = await createRetrievalChain({
  retriever: historyAwareRetriever2,
  combineDocsChain: questionAnswerChain2,
});

// Define the State interface
const GraphAnnotation2 = Annotation.Root({
  input: Annotation<string>(),
  chat_history: Annotation<BaseMessage[]>({
    reducer: messagesStateReducer,
    default: () => [],
  }),
  context: Annotation<string>(),
  answer: Annotation<string>(),
})

// Define the call_model function
async function callModel2(state: typeof GraphAnnotation2.State) {
  const response = await ragChain2.invoke(state);
  return {
    chat_history: [
      new HumanMessage(state.input),
      new AIMessage(response.answer),
    ],
    context: response.context,
    answer: response.answer,
  };
}

// Create the workflow
const workflow2 = new StateGraph(GraphAnnotation2)
  .addNode("model", callModel2)
  .addEdge(START, "model")
  .addEdge("model", END);

// Compile the graph with a checkpointer object
const memory2 = new MemorySaver();
const app2 = workflow2.compile({ checkpointer: memory2 });

const threadId2 = uuidv4();
const config2 = { configurable: { thread_id: threadId2 } };

const result3 = await app2.invoke(
  { input: "What is Task Decomposition?" },
  config2,
)
console.log(result3.answer);

const result4 = await app2.invoke(
  { input: "What is one way of doing it?" },
  config2,
)
console.log(result4.answer);
```
```output
Task Decomposition is the process of breaking a complicated task into smaller, simpler steps to enhance model performance on complex tasks. Techniques like Chain of Thought (CoT) and Tree of Thoughts (ToT) are used for this, with CoT focusing on step-by-step thinking and ToT exploring multiple reasoning possibilities at each step. Decomposition can be carried out by the LLM itself, using task-specific instructions, or through human inputs.
One way of doing task decomposition is by prompting the LLM with simple instructions such as "Steps for XYZ.\n1." or "What are the subgoals for achieving XYZ?" This encourages the model to break down the task into smaller, manageable steps on its own.
```
## Agents {#agents}

Agents leverage the reasoning capabilities of LLMs to make decisions during execution. Using agents allow you to offload some discretion over the retrieval process. Although their behavior is less predictable than chains, they offer some advantages in this context:
- Agents generate the input to the retriever directly, without necessarily needing us to explicitly build in contextualization, as we did above;
- Agents can execute multiple retrieval steps in service of a query, or refrain from executing a retrieval step altogether (e.g., in response to a generic greeting from a user).

### Retrieval tool

Agents can access "tools" and manage their execution. In this case, we will convert our retriever into a LangChain tool to be wielded by the agent:


```typescript
import { createRetrieverTool } from "langchain/tools/retriever";

const tool =  createRetrieverTool(
    retriever,
    {
      name: "blog_post_retriever",
      description: "Searches and returns excerpts from the Autonomous Agents blog post.",
    }
)
const tools = [tool]
```

### Agent constructor

Now that we have defined the tools and the LLM, we can create the agent. We will be using [LangGraph](https://langchain-ai.github.io/langgraphjs) to construct the agent. 
Currently we are using a high level interface to construct the agent, but the nice thing about LangGraph is that this high-level interface is backed by a low-level, highly controllable API in case you want to modify the agent logic.


```typescript
import { createReactAgent } from "@langchain/langgraph/prebuilt";

const agentExecutor = createReactAgent({ llm, tools })
```

We can now try it out. Note that so far it is not stateful (we still need to add in memory)


```typescript
const query = "What is Task Decomposition?"

for await (const s of await agentExecutor.stream(
  { messages: [{ role: "user", content: query }] },
)){
  console.log(s)
  console.log("----")
}
```
```output
{
  agent: {
    messages: [
      AIMessage {
        "id": "chatcmpl-AB7xlcJBGSKSp1GvgDY9FP8KvXxwB",
        "content": "",
        "additional_kwargs": {
          "tool_calls": [
            {
              "id": "call_Ev0nA6nzGwOeMC5upJUUxTuw",
              "type": "function",
              "function": "[Object]"
            }
          ]
        },
        "response_metadata": {
          "tokenUsage": {
            "completionTokens": 19,
            "promptTokens": 66,
            "totalTokens": 85
          },
          "finish_reason": "tool_calls",
          "system_fingerprint": "fp_52a7f40b0b"
        },
        "tool_calls": [
          {
            "name": "blog_post_retriever",
            "args": {
              "query": "Task Decomposition"
            },
            "type": "tool_call",
            "id": "call_Ev0nA6nzGwOeMC5upJUUxTuw"
          }
        ],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 66,
          "output_tokens": 19,
          "total_tokens": 85
        }
      }
    ]
  }
}
----
{
  tools: {
    messages: [
      ToolMessage {
        "content": "Fig. 1. Overview of a LLM-powered autonomous agent system.\nComponent One: Planning#\nA complicated task usually involves many steps. An agent needs to know what they are and plan ahead.\nTask Decomposition#\nChain of thought (CoT; Wei et al. 2022) has become a standard prompting technique for enhancing model performance on complex tasks. The model is instructed to “think step by step” to utilize more test-time computation to decompose hard tasks into smaller and simpler steps. CoT transforms big tasks into multiple manageable tasks and shed lights into an interpretation of the model’s thinking process.\nTree of Thoughts (Yao et al. 2023) extends CoT by exploring multiple reasoning possibilities at each step. It first decomposes the problem into multiple thought steps and generates multiple thoughts per step, creating a tree structure. The search process can be BFS (breadth-first search) or DFS (depth-first search) with each state evaluated by a classifier (via a prompt) or majority vote.\n\nTask decomposition can be done (1) by LLM with simple prompting like \"Steps for XYZ.\\n1.\", \"What are the subgoals for achieving XYZ?\", (2) by using task-specific instructions; e.g. \"Write a story outline.\" for writing a novel, or (3) with human inputs.\nAnother quite distinct approach, LLM+P (Liu et al. 2023), involves relying on an external classical planner to do long-horizon planning. This approach utilizes the Planning Domain Definition Language (PDDL) as an intermediate interface to describe the planning problem. In this process, LLM (1) translates the problem into “Problem PDDL”, then (2) requests a classical planner to generate a PDDL plan based on an existing “Domain PDDL”, and finally (3) translates the PDDL plan back into natural language. Essentially, the planning step is outsourced to an external tool, assuming the availability of domain-specific PDDL and a suitable planner which is common in certain robotic setups but not in many other domains.\nSelf-Reflection#\n\nAgent System Overview\n                \n                    Component One: Planning\n                        \n                \n                    Task Decomposition\n                \n                    Self-Reflection\n                \n                \n                    Component Two: Memory\n                        \n                \n                    Types of Memory\n                \n                    Maximum Inner Product Search (MIPS)\n                \n                \n                    Component Three: Tool Use\n                \n                    Case Studies\n                        \n                \n                    Scientific Discovery Agent\n                \n                    Generative Agents Simulation\n                \n                    Proof-of-Concept Examples\n                \n                \n                    Challenges\n                \n                    Citation\n                \n                    References\n\n(3) Task execution: Expert models execute on the specific tasks and log results.\nInstruction:\n\nWith the input and the inference results, the AI assistant needs to describe the process and results. The previous stages can be formed as - User Input: {{ User Input }}, Task Planning: {{ Tasks }}, Model Selection: {{ Model Assignment }}, Task Execution: {{ Predictions }}. You must first answer the user's request in a straightforward manner. Then describe the task process and show your analysis and model inference results to the user in the first person. If inference results contain a file path, must tell the user the complete file path.",
        "name": "blog_post_retriever",
        "additional_kwargs": {},
        "response_metadata": {},
        "tool_call_id": "call_Ev0nA6nzGwOeMC5upJUUxTuw"
      }
    ]
  }
}
----
{
  agent: {
    messages: [
      AIMessage {
        "id": "chatcmpl-AB7xmiPNPbMX2KvZKHM2oPfcoFMnY",
        "content": "**Task Decomposition** involves breaking down a complicated or large task into smaller, more manageable subtasks. Here are some insights based on current techniques and research:\n\n1. **Chain of Thought (CoT)**:\n   - Introduced by Wei et al. (2022), this technique prompts the model to \"think step by step\".\n   - It helps decompose hard tasks into several simpler steps.\n   - Enhances the interpretability of the model's thought process.\n\n2. **Tree of Thoughts (ToT)**:\n   - An extension of CoT by Yao et al. (2023).\n   - Decomposes problems into multiple thought steps and generates several possibilities at each step.\n   - Utilizes tree structures through BFS (Breadth-First Search) or DFS (Depth-First Search) with evaluation by a classifier or majority vote.\n\n3. **Methods of Task Decomposition**:\n   - **Simple Prompting**: Asking the model directly, e.g., \"Steps for XYZ.\\n1.\" or \"What are the subgoals for achieving XYZ?\".\n   - **Task-Specific Instructions**: Tailoring instructions to the task, such as \"Write a story outline\" for writing a novel.\n   - **Human Inputs**: Receiving inputs from humans to refine the process.\n\n4. **LLM+P Approach**:\n   - Suggested by Liu et al. (2023), combines language models with an external classical planner.\n   - Uses Planning Domain Definition Language (PDDL) for long-horizon planning:\n     1. Translates the problem into a PDDL problem.\n     2. Requests an external planner to generate a PDDL plan.\n     3. Translates the PDDL plan back into natural language.\n   - This method offloads the planning complexity to a specialized tool, especially relevant for domains utilizing robotic setups.\n\nTask Decomposition is a fundamental component of planning in autonomous agent systems, aiding in the efficient accomplishment of complex tasks by breaking them into smaller, actionable steps.",
        "additional_kwargs": {},
        "response_metadata": {
          "tokenUsage": {
            "completionTokens": 411,
            "promptTokens": 732,
            "totalTokens": 1143
          },
          "finish_reason": "stop",
          "system_fingerprint": "fp_e375328146"
        },
        "tool_calls": [],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 732,
          "output_tokens": 411,
          "total_tokens": 1143
        }
      }
    ]
  }
}
----
```
LangGraph comes with built in persistence, so we don't need to use `ChatMessageHistory`! Rather, we can pass in a checkpointer to our LangGraph agent directly.

Distinct conversations are managed by specifying a key for a conversation thread in the config object, as shown below.


```typescript
import { MemorySaver } from "@langchain/langgraph";

const memory3 = new MemorySaver();

const agentExecutor2 = createReactAgent({ llm, tools, checkpointSaver: memory3 })
```

This is all we need to construct a conversational RAG agent.

Let's observe its behavior. Note that if we input a query that does not require a retrieval step, the agent does not execute one:


```typescript
const threadId3 = uuidv4();
const config3 = { configurable: { thread_id: threadId3 } };

for await (const s of await agentExecutor2.stream({ messages: [{ role: "user", content: "Hi! I'm bob" }] }, config3)) {
  console.log(s)
  console.log("----")
}
```
```output
{
  agent: {
    messages: [
      AIMessage {
        "id": "chatcmpl-AB7y8P8AGHkxOwKpwMc3qj6r0skYr",
        "content": "Hello, Bob! How can I assist you today?",
        "additional_kwargs": {},
        "response_metadata": {
          "tokenUsage": {
            "completionTokens": 12,
            "promptTokens": 64,
            "totalTokens": 76
          },
          "finish_reason": "stop",
          "system_fingerprint": "fp_e375328146"
        },
        "tool_calls": [],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 64,
          "output_tokens": 12,
          "total_tokens": 76
        }
      }
    ]
  }
}
----
```
Further, if we input a query that does require a retrieval step, the agent generates the input to the tool:


```typescript
const query2 = "What is Task Decomposition?"

for await (const s of await agentExecutor2.stream({ messages: [{ role: "user", content: query2 }] }, config3)) {
  console.log(s)
  console.log("----")
}
```
```output
{
  agent: {
    messages: [
      AIMessage {
        "id": "chatcmpl-AB7y8Do2IHJ2rnUvvMU3pTggmuZud",
        "content": "",
        "additional_kwargs": {
          "tool_calls": [
            {
              "id": "call_3tSaOZ3xdKY4miIJdvBMR80V",
              "type": "function",
              "function": "[Object]"
            }
          ]
        },
        "response_metadata": {
          "tokenUsage": {
            "completionTokens": 19,
            "promptTokens": 89,
            "totalTokens": 108
          },
          "finish_reason": "tool_calls",
          "system_fingerprint": "fp_e375328146"
        },
        "tool_calls": [
          {
            "name": "blog_post_retriever",
            "args": {
              "query": "Task Decomposition"
            },
            "type": "tool_call",
            "id": "call_3tSaOZ3xdKY4miIJdvBMR80V"
          }
        ],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 89,
          "output_tokens": 19,
          "total_tokens": 108
        }
      }
    ]
  }
}
----
{
  tools: {
    messages: [
      ToolMessage {
        "content": "Fig. 1. Overview of a LLM-powered autonomous agent system.\nComponent One: Planning#\nA complicated task usually involves many steps. An agent needs to know what they are and plan ahead.\nTask Decomposition#\nChain of thought (CoT; Wei et al. 2022) has become a standard prompting technique for enhancing model performance on complex tasks. The model is instructed to “think step by step” to utilize more test-time computation to decompose hard tasks into smaller and simpler steps. CoT transforms big tasks into multiple manageable tasks and shed lights into an interpretation of the model’s thinking process.\nTree of Thoughts (Yao et al. 2023) extends CoT by exploring multiple reasoning possibilities at each step. It first decomposes the problem into multiple thought steps and generates multiple thoughts per step, creating a tree structure. The search process can be BFS (breadth-first search) or DFS (depth-first search) with each state evaluated by a classifier (via a prompt) or majority vote.\n\nTask decomposition can be done (1) by LLM with simple prompting like \"Steps for XYZ.\\n1.\", \"What are the subgoals for achieving XYZ?\", (2) by using task-specific instructions; e.g. \"Write a story outline.\" for writing a novel, or (3) with human inputs.\nAnother quite distinct approach, LLM+P (Liu et al. 2023), involves relying on an external classical planner to do long-horizon planning. This approach utilizes the Planning Domain Definition Language (PDDL) as an intermediate interface to describe the planning problem. In this process, LLM (1) translates the problem into “Problem PDDL”, then (2) requests a classical planner to generate a PDDL plan based on an existing “Domain PDDL”, and finally (3) translates the PDDL plan back into natural language. Essentially, the planning step is outsourced to an external tool, assuming the availability of domain-specific PDDL and a suitable planner which is common in certain robotic setups but not in many other domains.\nSelf-Reflection#\n\nAgent System Overview\n                \n                    Component One: Planning\n                        \n                \n                    Task Decomposition\n                \n                    Self-Reflection\n                \n                \n                    Component Two: Memory\n                        \n                \n                    Types of Memory\n                \n                    Maximum Inner Product Search (MIPS)\n                \n                \n                    Component Three: Tool Use\n                \n                    Case Studies\n                        \n                \n                    Scientific Discovery Agent\n                \n                    Generative Agents Simulation\n                \n                    Proof-of-Concept Examples\n                \n                \n                    Challenges\n                \n                    Citation\n                \n                    References\n\n(3) Task execution: Expert models execute on the specific tasks and log results.\nInstruction:\n\nWith the input and the inference results, the AI assistant needs to describe the process and results. The previous stages can be formed as - User Input: {{ User Input }}, Task Planning: {{ Tasks }}, Model Selection: {{ Model Assignment }}, Task Execution: {{ Predictions }}. You must first answer the user's request in a straightforward manner. Then describe the task process and show your analysis and model inference results to the user in the first person. If inference results contain a file path, must tell the user the complete file path.",
        "name": "blog_post_retriever",
        "additional_kwargs": {},
        "response_metadata": {},
        "tool_call_id": "call_3tSaOZ3xdKY4miIJdvBMR80V"
      }
    ]
  }
}
----
{
  agent: {
    messages: [
      AIMessage {
        "id": "chatcmpl-AB7y9tpoTvM3lsrhoxCWkkerk9fb2",
        "content": "Task decomposition is a methodology used to break down complex tasks into smaller, more manageable steps. Here’s an overview of various approaches to task decomposition:\n\n1. **Chain of Thought (CoT)**: This technique prompts a model to \"think step by step,\" which aids in transforming big tasks into multiple smaller tasks. This method enhances the model’s performance on complex tasks by making the problem more manageable and interpretable.\n\n2. **Tree of Thoughts (ToT)**: An extension of Chain of Thought, this approach explores multiple reasoning possibilities at each step, effectively creating a tree structure. The search process can be carried out using Breadth-First Search (BFS) or Depth-First Search (DFS), with each state evaluated by either a classifier or a majority vote.\n\n3. **Simple Prompting**: Involves straightforward instructions to decompose a task, such as starting with \"Steps for XYZ. 1.\" or asking \"What are the subgoals for achieving XYZ?\". This can also include task-specific instructions like \"Write a story outline\" for writing a novel.\n\n4. **LLM+P**: Combines Large Language Models (LLMs) with an external classical planner. The problem is translated into a Planning Domain Definition Language (PDDL) format, an external planner generates a plan, and then the plan is translated back into natural language. This approach highlights a synergy between modern AI techniques and traditional planning strategies.\n\nThese approaches allow complex problems to be approached and solved more efficiently by focusing on manageable sub-tasks.",
        "additional_kwargs": {},
        "response_metadata": {
          "tokenUsage": {
            "completionTokens": 311,
            "promptTokens": 755,
            "totalTokens": 1066
          },
          "finish_reason": "stop",
          "system_fingerprint": "fp_52a7f40b0b"
        },
        "tool_calls": [],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 755,
          "output_tokens": 311,
          "total_tokens": 1066
        }
      }
    ]
  }
}
----
```
Above, instead of inserting our query verbatim into the tool, the agent stripped unnecessary words like "what" and "is".

This same principle allows the agent to use the context of the conversation when necessary:


```typescript
const query3 = "What according to the blog post are common ways of doing it? redo the search"

for await (const s of await agentExecutor2.stream({ messages: [{ role: "user", content: query3 }] }, config3)) {
  console.log(s)
  console.log("----")
}
```
```output
{
  agent: {
    messages: [
      AIMessage {
        "id": "chatcmpl-AB7yDE4rCOXTPZ3595GknUgVzASmt",
        "content": "",
        "additional_kwargs": {
          "tool_calls": [
            {
              "id": "call_cWnDZq2aloVtMB4KjZlTxHmZ",
              "type": "function",
              "function": "[Object]"
            }
          ]
        },
        "response_metadata": {
          "tokenUsage": {
            "completionTokens": 21,
            "promptTokens": 1089,
            "totalTokens": 1110
          },
          "finish_reason": "tool_calls",
          "system_fingerprint": "fp_52a7f40b0b"
        },
        "tool_calls": [
          {
            "name": "blog_post_retriever",
            "args": {
              "query": "common ways of task decomposition"
            },
            "type": "tool_call",
            "id": "call_cWnDZq2aloVtMB4KjZlTxHmZ"
          }
        ],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 1089,
          "output_tokens": 21,
          "total_tokens": 1110
        }
      }
    ]
  }
}
----
{
  tools: {
    messages: [
      ToolMessage {
        "content": "Fig. 1. Overview of a LLM-powered autonomous agent system.\nComponent One: Planning#\nA complicated task usually involves many steps. An agent needs to know what they are and plan ahead.\nTask Decomposition#\nChain of thought (CoT; Wei et al. 2022) has become a standard prompting technique for enhancing model performance on complex tasks. The model is instructed to “think step by step” to utilize more test-time computation to decompose hard tasks into smaller and simpler steps. CoT transforms big tasks into multiple manageable tasks and shed lights into an interpretation of the model’s thinking process.\nTree of Thoughts (Yao et al. 2023) extends CoT by exploring multiple reasoning possibilities at each step. It first decomposes the problem into multiple thought steps and generates multiple thoughts per step, creating a tree structure. The search process can be BFS (breadth-first search) or DFS (depth-first search) with each state evaluated by a classifier (via a prompt) or majority vote.\n\nTask decomposition can be done (1) by LLM with simple prompting like \"Steps for XYZ.\\n1.\", \"What are the subgoals for achieving XYZ?\", (2) by using task-specific instructions; e.g. \"Write a story outline.\" for writing a novel, or (3) with human inputs.\nAnother quite distinct approach, LLM+P (Liu et al. 2023), involves relying on an external classical planner to do long-horizon planning. This approach utilizes the Planning Domain Definition Language (PDDL) as an intermediate interface to describe the planning problem. In this process, LLM (1) translates the problem into “Problem PDDL”, then (2) requests a classical planner to generate a PDDL plan based on an existing “Domain PDDL”, and finally (3) translates the PDDL plan back into natural language. Essentially, the planning step is outsourced to an external tool, assuming the availability of domain-specific PDDL and a suitable planner which is common in certain robotic setups but not in many other domains.\nSelf-Reflection#\n\nAgent System Overview\n                \n                    Component One: Planning\n                        \n                \n                    Task Decomposition\n                \n                    Self-Reflection\n                \n                \n                    Component Two: Memory\n                        \n                \n                    Types of Memory\n                \n                    Maximum Inner Product Search (MIPS)\n                \n                \n                    Component Three: Tool Use\n                \n                    Case Studies\n                        \n                \n                    Scientific Discovery Agent\n                \n                    Generative Agents Simulation\n                \n                    Proof-of-Concept Examples\n                \n                \n                    Challenges\n                \n                    Citation\n                \n                    References\n\nResources:\n1. Internet access for searches and information gathering.\n2. Long Term memory management.\n3. GPT-3.5 powered Agents for delegation of simple tasks.\n4. File output.\n\nPerformance Evaluation:\n1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities.\n2. Constructively self-criticize your big-picture behavior constantly.\n3. Reflect on past decisions and strategies to refine your approach.\n4. Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps.",
        "name": "blog_post_retriever",
        "additional_kwargs": {},
        "response_metadata": {},
        "tool_call_id": "call_cWnDZq2aloVtMB4KjZlTxHmZ"
      }
    ]
  }
}
----
{
  agent: {
    messages: [
      AIMessage {
        "id": "chatcmpl-AB7yGASxz0Z0g2jiCxwx4gYHYJTi4",
        "content": "According to the blog post, there are several common methods of task decomposition:\n\n1. **Simple Prompting by LLMs**: This involves straightforward instructions to decompose a task. Examples include:\n   - \"Steps for XYZ. 1.\"\n   - \"What are the subgoals for achieving XYZ?\"\n   - Task-specific instructions like \"Write a story outline\" for writing a novel.\n\n2. **Human Inputs**: Decomposition can be guided by human insights and instructions.\n\n3. **Chain of Thought (CoT)**: This technique prompts a model to think step-by-step, enabling it to break down complex tasks into smaller, more manageable tasks. CoT has become a standard method to enhance model performance on intricate tasks.\n\n4. **Tree of Thoughts (ToT)**: An extension of CoT, this approach decomposes the problem into multiple thought steps and generates several thoughts per step, forming a tree structure. The search process can be performed using Breadth-First Search (BFS) or Depth-First Search (DFS), with each state evaluated by a classifier or through a majority vote.\n\n5. **LLM+P (Large Language Model plus Planner)**: This method integrates LLMs with an external classical planner. It involves:\n   - Translating the problem into “Problem PDDL” (Planning Domain Definition Language).\n   - Using an external planner to generate a PDDL plan based on an existing “Domain PDDL”.\n   - Translating the PDDL plan back into natural language.\n  \nBy utilizing these methods, tasks can be effectively decomposed into more manageable parts, allowing for more efficient problem-solving and planning.",
        "additional_kwargs": {},
        "response_metadata": {
          "tokenUsage": {
            "completionTokens": 334,
            "promptTokens": 1746,
            "totalTokens": 2080
          },
          "finish_reason": "stop",
          "system_fingerprint": "fp_52a7f40b0b"
        },
        "tool_calls": [],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 1746,
          "output_tokens": 334,
          "total_tokens": 2080
        }
      }
    ]
  }
}
----
```
Note that the agent was able to infer that "it" in our query refers to "task decomposition", and generated a reasonable search query as a result-- in this case, "common ways of task decomposition".

### Tying it together

For convenience, we tie together all of the necessary steps in a single code cell:


```typescript
import { createRetrieverTool } from "langchain/tools/retriever";
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { MemorySaver } from "@langchain/langgraph";
import { ChatOpenAI } from "@langchain/openai";
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { MemoryVectorStore } from "langchain/vectorstores/memory"
import { OpenAIEmbeddings } from "@langchain/openai";

const llm3 = new ChatOpenAI({ model: "gpt-4o" });

const loader3 = new CheerioWebBaseLoader(
  "https://lilianweng.github.io/posts/2023-06-23-agent/"
);

const docs3 = await loader3.load();

const textSplitter3 = new RecursiveCharacterTextSplitter({ chunkSize: 1000, chunkOverlap: 200 });
const splits3 = await textSplitter3.splitDocuments(docs3);
const vectorStore3 = await MemoryVectorStore.fromDocuments(splits3, new OpenAIEmbeddings());

// Retrieve and generate using the relevant snippets of the blog.
const retriever3 = vectorStore3.asRetriever();

const tool2 = createRetrieverTool(
    retriever3,
    {
      name: "blog_post_retriever",
      description: "Searches and returns excerpts from the Autonomous Agents blog post.",
    }
)
const tools2 = [tool2]
const memory4 = new MemorySaver();

const agentExecutor3 = createReactAgent({ llm: llm3, tools: tools2, checkpointSaver: memory4 })
```

## Next steps

We've covered the steps to build a basic conversational Q&A application:

- We used chains to build a predictable application that generates search queries for each user input;
- We used agents to build an application that "decides" when and how to generate search queries.

To explore different types of retrievers and retrieval strategies, visit the [retrievers](/docs/how_to#retrievers) section of the how-to guides.

For a detailed walkthrough of LangChain's conversation memory abstractions, visit the [How to add message history (memory)](/oss/how-to/message_history) LCEL page.
