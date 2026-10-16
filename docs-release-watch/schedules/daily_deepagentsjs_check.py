from managed_deepagents import define_schedule

schedule = define_schedule(
    cron="30 10 * * 1,3,5",
    timezone="America/Los_Angeles",
    prompt=(
        "Run the Deep Agents JS docs release check. "
        "Load the deepagentsjs skill. "
        "Find the newest deepagents@ release from langchain-ai/deepagentsjs "
        "published at least 7 days ago. "
        "Ignore deepagents-acp@ and other packages on the same GitHub releases feed. "
        "Compare it to the Deep Agents library docs under src/oss/deepagents/, "
        "excluding src/oss/deepagents/code/, and prefer :::js sections. "
        "For each user-facing feature that needs documentation changes and is not "
        "already tracked in memory, create one Linear DOC ticket and one draft PR "
        "using the ship-docs-update skill. "
        "If nothing needs docs changes, say so briefly and stop."
    ),
)
