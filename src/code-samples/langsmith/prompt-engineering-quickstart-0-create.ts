// Runs before prompt-engineering-quickstart-1-test.ts and -2-iterate.ts:
// the runner executes .ts samples in lexical path order.

// :remove-start:
// CI and local reruns share the hub prompt "prompt-quickstart" with the
// Python sample. A second push of the same content returns 409
// "Nothing to commit"; treat that as success so the suite stays idempotent.
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
