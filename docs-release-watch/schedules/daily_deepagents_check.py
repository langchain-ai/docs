from managed_deepagents import define_schedule

schedule = define_schedule(
    cron="30 9 * * *",
    timezone="America/Los_Angeles",
    prompt=(
        "Run the Deep Agents Python docs release check. "
        "Load the deepagents skill. "
        "Find the newest deepagents== release from langchain-ai/deepagents "
        "published at least 7 days ago. "
        "Ignore deepagents-code and other packages on the same GitHub releases feed. "
        "Do not cover Deep Agents JS (deepagentsjs). "
        "Compare it to the Deep Agents library docs under src/oss/deepagents/, "
        "excluding src/oss/deepagents/code/, and prefer :::python sections. "
        "For each user-facing feature that needs documentation changes and is not "
        "already tracked in memory, create one Linear DOC ticket and one draft PR "
        "using the ship-docs-update skill. "
        "If nothing needs docs changes, say so briefly and stop."
    ),
)
