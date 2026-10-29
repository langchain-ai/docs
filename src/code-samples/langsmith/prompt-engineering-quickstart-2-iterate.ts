// Runs after prompt-engineering-quickstart-0-create.ts and -1-test.ts.

// :snippet-start: prompt-engineering-quickstart-iterate-js
// :codegroup-tab: TypeScript
import { Client } from "langsmith";
import { ChatPromptTemplate } from "@langchain/core/prompts";

const client = new Client();

const newPrompt = ChatPromptTemplate.fromMessages([
    ["system", "You are a helpful chatbot. Speak in Spanish."],
    ["user", "{question}"]
]);

await client.pushPrompt("prompt-quickstart", {
    object: newPrompt
});
// :snippet-end:

// :remove-start:
console.log("✓ pushed a second commit to prompt-quickstart");
// :remove-end:
