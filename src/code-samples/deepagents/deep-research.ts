// :snippet-start: deep-research-tools-js
import { tool } from "langchain";
import { z } from "zod";

async function fetchWebpageContent(
  url: string,
  timeout = 10_000,
): Promise<string> {
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    const response = await fetch(url, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
      signal: controller.signal,
    });
    clearTimeout(id);
    if (!response.ok) {
      return `Error fetching ${url}: HTTP ${response.status}`;
    }
    return await response.text();
  } catch (e) {
    return `Error fetching ${url}: ${e}`;
  }
}

const tavilySearch = tool(
  async ({
    query,
    maxResults = 1,
    topic = "general",
  }: {
    query: string;
    maxResults?: number;
    topic?: "general" | "news" | "finance";
  }) => {
    const response = await fetch("https://api.tavily.com/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.TAVILY_API_KEY}`,
      },
      body: JSON.stringify({ query, max_results: maxResults, topic }),
    });
    const data = (await response.json()) as {
      results: Array<{ url: string; title: string }>;
    };
    const results = data.results ?? [];
    const resultTexts: string[] = [];
    for (const result of results) {
      const content = await fetchWebpageContent(result.url);
      resultTexts.push(
        `## ${result.title}\n**URL:** ${result.url}\n\n${content}\n---`,
      );
    }
    return (
      `Found ${resultTexts.length} result(s) for '${query}':\n\n` +
      resultTexts.join("\n")
    );
  },
  {
    name: "tavily_search",
    description:
      "Search the web for information on a given query. Uses Tavily to discover relevant URLs, then fetches and returns full webpage content.",
    schema: z.object({
      query: z.string().describe("Search query to execute"),
      maxResults: z
        .number()
        .optional()
        .default(1)
        .describe("Maximum number of results to return (default: 1)"),
      topic: z
        .enum(["general", "news", "finance"])
        .optional()
        .default("general")
        .describe(
          "Topic filter - 'general', 'news', or 'finance' (default: 'general')",
        ),
    }),
  },
);
// :snippet-end:

const RESEARCH_WORKFLOW_INSTRUCTIONS = `# Research Workflow

Follow this workflow for all research requests:

1. **Plan**: Create a todo list with write_todos to break down the research into focused tasks
2. **Save the request**: Use write_file() to save the user's research question to \`/research_request.md\`
3. **Research**: Delegate research tasks to sub-agents using the task() tool - ALWAYS use sub-agents for research, never conduct research yourself
4. **Synthesize**: Review all sub-agent findings and consolidate citations (each unique URL gets one number across all findings)
5. **Write Report**: Write a comprehensive final report to \`/final_report.md\` (see Report Writing Guidelines below)
6. **Verify**: Read \`/research_request.md\` and confirm you've addressed all aspects with proper citations and structure

## Research Planning Guidelines
- Batch similar research tasks into a single TODO to minimize overhead
- For simple fact-finding questions, use 1 sub-agent
- For comparisons or multi-faceted topics, delegate to multiple parallel sub-agents
- Each sub-agent should research one specific aspect and return findings

## Report Writing Guidelines

When writing the final report to \`/final_report.md\`, follow these structure patterns:

**For comparisons:**
1. Introduction
2. Overview of topic A
3. Overview of topic B
4. Detailed comparison
5. Conclusion

**For lists/rankings:**
Simply list items with details - no introduction needed:
1. Item 1 with explanation
2. Item 2 with explanation
3. Item 3 with explanation

**For summaries/overviews:**
1. Overview of topic
2. Key concept 1
3. Key concept 2
4. Key concept 3
5. Conclusion

**General guidelines:**
- Use clear section headings (## for sections, ### for subsections)
- Write in paragraph form by default - be text-heavy, not just bullet points
- Do NOT use self-referential language ("I found...", "I researched...")
- Write as a professional report without meta-commentary
- Each section should be comprehensive and detailed
- Use bullet points only when listing is more appropriate than prose

**Citation format:**
- Cite sources inline using [1], [2], [3] format
- Assign each unique URL a single citation number across ALL sub-agent findings
- End report with ### Sources section listing each numbered source
- Number sources sequentially without gaps (1,2,3,4...)
- Format: [1] Source Title: URL (each on separate line for proper list rendering)
- Example:

 Some important finding [1]. Another key insight [2].

 ### Sources
 [1] AI Research Paper: https://example.com/paper
 [2] Industry Analysis: https://example.com/analysis
`;

// :snippet-start: researcher-instructions-js
const RESEARCHER_INSTRUCTIONS = `You are a research assistant conducting research on the user's input topic. For context, today's date is {date}.

Your job is to use tools to gather information about the user's input topic.
You can use the tavily_search tool to find resources that can help answer the research question.
You can call it in series or in parallel, your research is conducted in a tool-calling loop.

You have access to the tavily_search tool for conducting web searches.

Think like a human researcher with limited time. Follow these steps:

1. **Read the question carefully** - What specific information does the user need?
2. **Start with broader searches** - Use broad, comprehensive queries first
3. **After each search, pause and assess** - Do I have enough to answer? What's still missing?
4. **Execute narrower searches as you gather information** - Fill in the gaps
5. **Stop when you can answer confidently** - Don't keep searching for perfection

**Tool Call Budgets** (Prevent excessive searching):
- **Simple queries**: Use 2-3 search tool calls maximum
- **Complex queries**: Use up to 5 search tool calls maximum
- **Always stop**: After 5 search tool calls if you cannot find the right sources

**Stop Immediately When**:
- You can answer the user's question comprehensively
- You have 3+ relevant examples/sources for the question
- Your last 2 searches returned similar information

After each search, assess results before continuing: What key information did I find? What's missing? Do I have enough to answer? Should I search more or provide my answer?

When providing your findings back to the orchestrator:

1. **Structure your response**: Organize findings with clear headings and detailed explanations
2. **Cite sources inline**: Use [1], [2], [3] format when referencing information from your searches
3. **Include Sources section**: End with ### Sources listing each numbered source with title and URL

Example:
## Key Findings
Context engineering is a critical technique for AI agents [1]. Studies show that proper context management can improve performance by 40% [2].

### Sources
[1] Context Engineering Guide: https://example.com/context-guide
[2] AI Performance Study: https://example.com/study

The orchestrator will consolidate citations from all sub-agents into the final report.
`;
// :snippet-end:

const SUBAGENT_DELEGATION_INSTRUCTIONS = `# Sub-Agent Research Coordination

Your role is to coordinate research by delegating tasks from your TODO list to specialized research sub-agents.

## Delegation Strategy

**DEFAULT: Start with 1 sub-agent** for most queries:
- "What is quantum computing?" -> 1 sub-agent (general overview)
- "List the top 10 coffee shops in San Francisco" -> 1 sub-agent
- "Summarize the history of the internet" -> 1 sub-agent
- "Research context engineering for AI agents" -> 1 sub-agent (covers all aspects)

**ONLY parallelize when the query EXPLICITLY requires comparison or has clearly independent aspects:**

**Explicit comparisons** -> 1 sub-agent per element:
- "Compare OpenAI vs Anthropic vs DeepMind AI safety approaches" -> 3 parallel sub-agents
- "Compare Python vs JavaScript for web development" -> 2 parallel sub-agents

**Clearly separated aspects** -> 1 sub-agent per aspect (use sparingly):
- "Research renewable energy adoption in Europe, Asia, and North America" -> 3 parallel sub-agents (geographic separation)
- Only use this pattern when aspects cannot be covered efficiently by a single comprehensive search

## Key Principles
- **Bias towards single sub-agent**: One comprehensive research task is more token-efficient than multiple narrow ones
- **Avoid premature decomposition**: Don't break "research X" into "research X overview", "research X techniques", "research X applications" - just use 1 sub-agent for all of X
- **Parallelize only for clear comparisons**: Use multiple sub-agents when comparing distinct entities or geographically separated data

## Parallel Execution Limits
- Use at most {maxConcurrentResearchUnits} parallel sub-agents per iteration
- Make multiple task() calls in a single response to enable parallel execution
- Each sub-agent returns findings independently

## Research Limits
- Stop after {maxResearcherIterations} delegation rounds if you haven't found adequate sources
- Stop when you have sufficient information to answer comprehensively
- Bias towards focused research over exhaustive exploration`;

// :snippet-start: deep-research-agent-claude-js
import { createDeepAgent } from "deepagents";
import { ChatAnthropic } from "@langchain/anthropic";

const maxConcurrentResearchUnits = 3;
const maxResearcherIterations = 3;

const currentDate = new Date().toISOString().split("T")[0];

const INSTRUCTIONS =
  RESEARCH_WORKFLOW_INSTRUCTIONS +
  "\n\n" +
  "=".repeat(80) +
  "\n\n" +
  SUBAGENT_DELEGATION_INSTRUCTIONS.replace(
    "{maxConcurrentResearchUnits}",
    String(maxConcurrentResearchUnits),
  ).replace("{maxResearcherIterations}", String(maxResearcherIterations));

const researchSubAgent = {
  name: "research-agent",
  description: "Delegate research to the sub-agent. Give one topic at a time.",
  systemPrompt: RESEARCHER_INSTRUCTIONS.replace("{date}", currentDate),
  tools: [tavilySearch],
};

const model = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
  temperature: 0,
});

const agent = createDeepAgent({
  model,
  tools: [tavilySearch],
  systemPrompt: INSTRUCTIONS,
  subagents: [researchSubAgent],
});
// :snippet-end:

// :remove-start:
// These run blocks make real API calls. Wrap in a never-called function so
// tsx can parse and type-check them without executing them.
async function _runExamples() {
  // :remove-end:
  // :snippet-start: deep-research-run-sync-js
  {
    async function main() {
      const result = await agent.invoke({
        messages: [
          {
            role: "user",
            content:
              "What are the main differences between RAG and fine-tuning for LLM applications?",
          },
        ],
      });

      for (const msg of result.messages ?? []) {
        if (msg.content) {
          console.log(msg.content);
        }
      }
    }

    main().catch((err) => {
      console.error(err);
      process.exitCode = 1;
    });
  }
  // :snippet-end:

  // :snippet-start: deep-research-run-stream-js
  {
    async function main() {
      for await (const chunk of await agent.stream(
        {
          messages: [
            {
              role: "user",
              content: "Compare Python vs JavaScript for web development",
            },
          ],
        },
        { streamMode: "updates" },
      )) {
        for (const [, update] of Object.entries(chunk)) {
          const messages = (update as any)?.messages;
          if (!messages) continue;
          const msgList = Array.isArray(messages) ? messages : [messages];
          for (const msg of msgList) {
            if (msg.content) {
              console.log(msg.content);
            }
          }
        }
      }
    }

    main().catch((err) => {
      console.error(err);
      process.exitCode = 1;
    });
  }
  // :snippet-end:
  // :remove-start:
} // end _runExamples
// :remove-end:

// :remove-start:
// Test that components are defined correctly
if (!tavilySearch) throw new Error("tavilySearch not defined");
if (!RESEARCH_WORKFLOW_INSTRUCTIONS)
  throw new Error("RESEARCH_WORKFLOW_INSTRUCTIONS not defined");
if (!RESEARCHER_INSTRUCTIONS)
  throw new Error("RESEARCHER_INSTRUCTIONS not defined");
if (!SUBAGENT_DELEGATION_INSTRUCTIONS)
  throw new Error("SUBAGENT_DELEGATION_INSTRUCTIONS not defined");
if (!INSTRUCTIONS) throw new Error("INSTRUCTIONS not defined");
if (!researchSubAgent) throw new Error("researchSubAgent not defined");
if (!model) throw new Error("model not defined");
if (!agent) throw new Error("agent not defined");
if (!agent.invoke) throw new Error("agent.invoke not defined");
if (!agent.stream) throw new Error("agent.stream not defined");
console.log("✓ Deep research agent components defined correctly");
// :remove-end:
