// Depends on prompt-engineering-quickstart-0-create.ts having pushed the prompt.

// :snippet-start: prompt-engineering-quickstart-test-js
// :codegroup-tab: TypeScript
import { OpenAI } from "openai";
import { pull } from "langchain/hub"
import { convertPromptToOpenAI } from "@langchain/openai";

const oaiClient = new OpenAI();

const prompt = await pull("prompt-quickstart");

// Format the prompt with the question
const formattedPrompt = await prompt.invoke({ question: "What is the color of the sky?" });

const response = await oaiClient.chat.completions.create({
    // KEEP MODEL
    model: "gpt-5.5",
    messages: convertPromptToOpenAI(formattedPrompt).messages,
});
// :snippet-end:

// :remove-start:
if (!response.choices[0]?.message?.content) {
    throw new Error("model returned no content");
}
console.log("✓ pulled prompt and called the model");
// :remove-end:
