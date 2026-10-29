// Evaluation quickstart, step 5: target plus the correctness evaluator.

// :snippet-start: evaluation-quickstart-eval-evaluator-js
// :codegroup-tab: TypeScript
// :codegroup-fence-mods: highlight={4,20-37}
import { evaluate } from "langsmith/evaluation";
import { wrapOpenAI } from "langsmith/wrappers/openai";
import OpenAI from "openai";
import { createLLMAsJudge, CORRECTNESS_PROMPT } from "openevals";

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

const judge = createLLMAsJudge({
  prompt: CORRECTNESS_PROMPT,
  // KEEP MODEL
  model: "openai:gpt-5.5",
  feedbackKey: "correctness",
});

async function correctnessEvaluator(run: {
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  referenceOutputs?: Record<string, any>;
}) {
  return judge({
    inputs: run.inputs,
    outputs: run.outputs,
    // OpenEvals expects snake_case here:
    reference_outputs: run.referenceOutputs,
  });
}
// :snippet-end:

// :remove-start:
// The full experiment runs in evaluation-quickstart-3-eval-run.ts.
if (
  typeof target !== "function" ||
  typeof correctnessEvaluator !== "function" ||
  typeof evaluate !== "function"
) {
  throw new Error("target, correctnessEvaluator, or evaluate is not a function");
}
console.log("✓ target and evaluator defined");
// :remove-end:
