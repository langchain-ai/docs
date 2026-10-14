from managed_deepagents import define_schedule

schedule = define_schedule(
    cron="0 10 * * *",
    timezone="America/Los_Angeles",
    prompt=(
        "Run the Deep Agents Code docs release check. "
        "Load the deepagents-code skill. "
        "Find the newest deepagents-code== release published at least 7 days ago. "
        "Ignore deepagents== and other packages on the same GitHub releases feed. "
        "Compare it to the Deep Agents Code docs under src/oss/deepagents/code/. "
        "For each user-facing feature that needs documentation changes and is not "
        "already tracked in memory, create one Linear DOC ticket and one draft PR "
        "using the ship-docs-update skill. "
        "If nothing needs docs changes, say so briefly and stop."
    ),
)
