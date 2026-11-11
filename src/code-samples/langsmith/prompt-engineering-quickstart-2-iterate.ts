// Runs after prompt-engineering-quickstart-0-create.ts and -1-test.ts.

// :remove-start:
// Same shared-prompt 409 handling as prompt-engineering-quickstart-0-create.ts.
import { Client as _LangSmithClient } from "langsmith";

const _origPushPrompt = _LangSmithClient.prototype.pushPrompt;
_LangSmithClient.prototype.pushPrompt = async function (
  this: InstanceType<typeof _LangSmithClient>,
  ...args: any[]
) {
  try {
    return await _origPushPrompt.apply(this, args as never);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    if (!message.includes("Nothing to commit")) {
      throw err;
    }
    return undefined;
  }
};
// :remove-end:

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
