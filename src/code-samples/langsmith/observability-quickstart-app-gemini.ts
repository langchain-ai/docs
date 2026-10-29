// :remove-start:
// CI holds the Gemini key as GOOGLE_API_KEY; the docs read GEMINI_API_KEY.
process.env.GEMINI_API_KEY ??= process.env.GOOGLE_API_KEY;
// :remove-end:

// :snippet-start: observability-quickstart-app-gemini-js
// :codegroup-tab: TypeScript
import { GoogleGenAI } from "@google/genai";
import { wrapGemini } from "langsmith/wrappers/gemini";
import { traceable } from "langsmith/traceable";

const client = wrapGemini(new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY })); // log every Gemini call automatically

const getContext = traceable(
    async function getContext(question: string): Promise<string> { // trace this as a tool span
        // In a real app, this would query a knowledge base or vector store
        return "LangSmith traces are stored for 14 days on the Developer plan.";
    },
    { run_type: "tool" }
);

const assistant = traceable(async function assistant(question: string) { // capture the full pipeline as a single trace
    const context = await getContext(question);
    const response = await client.models.generateContent({
        // KEEP MODEL
        model: "gemini-3.8-flash",
        contents: question,
        config: { systemInstruction: `Answer using the context below.\n\nContext: ${context}` },
    });
    return response.text ?? null;
});

(async () => {
    console.log(await assistant("How long are LangSmith traces stored?"));
})();
// :snippet-end:
