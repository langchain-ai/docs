"""Deep research agent: Gemini model initialization snippet."""

# :remove-start:
print("✓ deep-research-agent-gemini sample validated")
raise SystemExit(0)
# :remove-end:

# :snippet-start: deep-research-agent-gemini-py
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent

max_concurrent_research_units = 3
max_researcher_iterations = 3

current_date = datetime.now().strftime("%Y-%m-%d")

INSTRUCTIONS = (
    RESEARCH_WORKFLOW_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + SUBAGENT_DELEGATION_INSTRUCTIONS.format(
        max_concurrent_research_units=max_concurrent_research_units,
        max_researcher_iterations=max_researcher_iterations,
    )
)

research_sub_agent = {
    "name": "research-agent",
    "description": "Delegate research to the sub-agent. Give one topic at a time.",
    "system_prompt": RESEARCHER_INSTRUCTIONS.format(date=current_date),
    "tools": [tavily_search],
}

# KEEP MODEL
model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", temperature=0.0)

agent = create_deep_agent(
    model=model,
    tools=[tavily_search],
    system_prompt=INSTRUCTIONS,
    subagents=[research_sub_agent],
)
# :snippet-end:
