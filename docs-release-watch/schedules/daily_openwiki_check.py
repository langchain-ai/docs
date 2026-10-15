from managed_deepagents import define_schedule

schedule = define_schedule(
    cron="0 9 * * 1,3,5",
    timezone="America/Los_Angeles",
    prompt=(
        "Run the OpenWiki docs release check. "
        "Load the openwiki skill. "
        "Find the newest OpenWiki release published at least 7 days ago. "
        "Compare it to the OpenWiki docs under src/oss/openwiki/. "
        "For each user-facing feature that needs documentation changes and is not "
        "already tracked in memory, create one Linear DOC ticket and one draft PR "
        "using the ship-docs-update skill. "
        "If nothing needs docs changes, say so briefly and stop."
    ),
)
