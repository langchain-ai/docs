---
title: INVALID_PROMPT_INPUT
---

{/* TODO: fix link when porting page */}
Occurs when a [prompt template](https://github.com/langchain-ai/langchain/blob/v0.3/docs/docs/concepts/prompt_templates.mdx) received missing or invalid input variables.

:::js
One unexpected way this can occur is if you add a JSON object directly into a prompt template:

```typescript
import { PromptTemplate } from "@langchain/core/prompts";
import { ChatOpenAI } from "@langchain/openai";

const prompt = PromptTemplate.fromTemplate(`You are a helpful assistant.

Here is an example of how you should respond:

{
  "firstName": "John",
  "lastName": "Doe",
  "age": 21
}

Now, answer the following question:

{question}`);
```

You might think that the above prompt template should require a single input key named question, but the JSON object will be interpreted as an additional variable because the curly braces (`{`) are not escaped, and should be preceded by a second brace instead, like this:

```typescript
import { PromptTemplate } from "@langchain/core/prompts";
import { ChatOpenAI } from "@langchain/openai";

const prompt = PromptTemplate.fromTemplate(`You are a helpful assistant.

Here is an example of how you should respond:

{{
  "firstName": "John",
  "lastName": "Doe",
  "age": 21
}}

Now, answer the following question:

{question}`);
```
:::


## Troubleshooting

To resolve this error, you can:

1. Review your prompt template for correctness. When using f-string formats, ensure proper escaping of curly braces:
   * Use `{{` for single braces in f-strings
   * Use `{{{{` for double braces in f-strings
2. When using `MessagesPlaceholder` components, confirm you're passing message arrays or message-like objects. If using shorthand tuples, wrap variable names in curly braces like `["placeholder", "{messages}"]`
3. Debug by examining actual inputs to your prompt template by using [LangSmith](/langsmith/home) or logging to verify they match expectations
4. If sourcing prompts from LangChain [Prompt Hub](https://smith.langchain.com/prompts), isolate and test the prompt with sample inputs to ensure it functions as intended
