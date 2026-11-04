// Evaluation quickstart, step 4: the target function on its own.

// :snippet-start: evaluation-quickstart-eval-target-js
// :codegroup-tab: TypeScript
// eval.ts
import { evaluate } from "langsmith/evaluation";
import { wrapOpenAI } from "langsmith/wrappers/openai";
import OpenAI from "openai";

const openaiClient = wrapOpenAI(new OpenAI());

async function target(inputs: Record<string, any>): Promise<Record<string, any>> {
  const question = String(inputs.question ?? "");
  const resp = await openaiClient.chat.completions.create({
    // KEEP MODEL
    model: "gpt-6-luna",
    messages: [
      { role: "system", content: "Answer the following question accurately" },
      { role: "user", content: question },
    ],
  });
  return { answer: resp.choices[0].message.content?.trim() ?? "" };
}
// :snippet-end:

// :remove-start:
// The full experiment runs in evaluation-quickstart-3-eval-run.ts; here only
// check that the step's code constructs and typechecks.
if (typeof target !== "function" || typeof evaluate !== "function") {
  throw new Error("target or evaluate is not a function");
}
console.log("✓ target defined");
// :remove-end:
