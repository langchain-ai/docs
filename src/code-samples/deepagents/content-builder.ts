// Content builder agent with brand memory, skills, subagents, and image generation.

// :snippet-start: content-builder-tools-js
import { tool } from "@langchain/core/tools";
import * as z from "zod";
import * as fs from "node:fs";
import * as path from "node:path";

const EXAMPLE_DIR = path.dirname(new URL(import.meta.url).pathname);

const webSearch = tool(
  async ({ query, maxResults = 5, topic = "general" }) => {
    const apiKey = process.env.TAVILY_API_KEY;
    if (!apiKey) return { error: "TAVILY_API_KEY not set" };
    try {
      const { TavilyClient } = await import("tavily");
      const client = new TavilyClient({ apiKey });
      return client.search(query, { maxResults, topic });
    } catch (e) {
      return { error: `Search failed: ${e}` };
    }
  },
  {
    name: "web_search",
    description: "Search the web for current information.",
    schema: z.object({
      query: z.string().describe("The search query (be specific and detailed)"),
      maxResults: z
        .number()
        .optional()
        .describe("Number of results to return (default: 5)"),
      topic: z
        .enum(["general", "news"])
        .optional()
        .describe('"general" for most queries, "news" for current events'),
    }),
  },
);

const generateCover = tool(
  async ({ prompt, slug }) => {
    try {
      const { GoogleGenerativeAI } = await import("@google/generative-ai");
      const genai = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY ?? "");
      const model = genai.getGenerativeModel({
        // KEEP MODEL
        model: "gemini-2.5-flash-image",
      });
      const result = await model.generateContent(prompt);
      const part = result.response.candidates?.[0]?.content?.parts?.find(
        (p) => p.inlineData,
      );
      if (!part?.inlineData) return "No image generated";
      const outputPath = path.join(EXAMPLE_DIR, "blogs", slug, "hero.png");
      fs.mkdirSync(path.dirname(outputPath), { recursive: true });
      fs.writeFileSync(outputPath, Buffer.from(part.inlineData.data, "base64"));
      return `Image saved to ${outputPath}`;
    } catch (e) {
      return `Error: ${e}`;
    }
  },
  {
    name: "generate_cover",
    description: "Generate a cover image for a blog post.",
    schema: z.object({
      prompt: z
        .string()
        .describe("Detailed description of the image to generate."),
      slug: z
        .string()
        .describe("Blog post slug. Image saves to blogs/<slug>/hero.png"),
    }),
  },
);

const generateSocialImage = tool(
  async ({ prompt, platform, slug }) => {
    try {
      const { GoogleGenerativeAI } = await import("@google/generative-ai");
      const genai = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY ?? "");
      const model = genai.getGenerativeModel({
        // KEEP MODEL
        model: "gemini-2.5-flash-image",
      });
      const result = await model.generateContent(prompt);
      const part = result.response.candidates?.[0]?.content?.parts?.find(
        (p) => p.inlineData,
      );
      if (!part?.inlineData) return "No image generated";
      const outputPath = path.join(EXAMPLE_DIR, platform, slug, "image.png");
      fs.mkdirSync(path.dirname(outputPath), { recursive: true });
      fs.writeFileSync(outputPath, Buffer.from(part.inlineData.data, "base64"));
      return `Image saved to ${outputPath}`;
    } catch (e) {
      return `Error: ${e}`;
    }
  },
  {
    name: "generate_social_image",
    description: "Generate an image for a social media post.",
    schema: z.object({
      prompt: z
        .string()
        .describe("Detailed description of the image to generate."),
      platform: z.string().describe('Either "linkedin" or "tweets"'),
      slug: z
        .string()
        .describe("Post slug. Image saves to <platform>/<slug>/image.png"),
    }),
  },
);
// :snippet-end:

// :snippet-start: content-builder-create-agent-js
import { createDeepAgent, FilesystemBackend } from "deepagents";

function createContentWriter() {
  const researcherSubagent = {
    name: "researcher",
    description:
      "Research subagent with web search capability. Delegate research tasks here.",
    systemPrompt:
      "You are a research assistant. Use the web_search tool to find current, accurate information and return well-organized findings.",
    tools: [webSearch],
  };

  return createDeepAgent({
    model: "anthropic:claude-sonnet-4-6",
    memory: ["./AGENTS.md"],
    skills: ["./skills/"],
    tools: [generateCover, generateSocialImage],
    subagents: [researcherSubagent],
    backend: new FilesystemBackend({ rootDir: EXAMPLE_DIR }),
  });
}
// :snippet-end:

// :snippet-start: content-builder-entry-point-js
const task =
  process.argv.slice(2).join(" ") ||
  "Write a blog post about how AI agents are transforming software development";

const agent = createContentWriter();
const result = await agent.invoke({
  messages: [{ role: "user", content: task }],
  config: { configurable: { threadId: "content-builder-demo" } },
});

const messages = result.messages ?? [];
for (const msg of messages) {
  if (msg.content) console.log(msg.content);
}
// :remove-start:
if (!result) throw new Error("Agent invocation failed");
// :remove-end:
// :snippet-end:

// :remove-start:
if (import.meta.url === `file://${process.argv[1]}`) {
  if (!webSearch || !generateCover || !generateSocialImage) {
    throw new Error("Tool creation failed");
  }
  console.log("✓ Content builder agent components defined correctly");
}
// :remove-end:
