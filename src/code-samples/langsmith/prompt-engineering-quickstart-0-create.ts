// Runs before prompt-engineering-quickstart-1-test.ts and -2-iterate.ts:
// the runner executes .ts samples in lexical path order.

// :snippet-start: prompt-engineering-quickstart-create-js
// :codegroup-tab: TypeScript
import { Client } from "langsmith";
import { ChatPromptTemplate } from "@langchain/core/prompts";

const client = new Client();

const prompt = ChatPromptTemplate.fromMessages([
["system", "You are a helpful chatbot."],
["user", "{question}"],
]);

await client.pushPrompt("prompt-quickstart", {
object: prompt,
});
// :snippet-end:

// :remove-start:
console.log("✓ pushed prompt-quickstart");
// :remove-end:
