from managed_deepagents import define_schedule

schedule = define_schedule(
    cron="0 9 * * 1,3,5",
    timezone="America/Los_Angeles",
    prompt=(
        "Run the OpenWiki docs release check. "
        "First call the release-research subagent for openwiki "
        "(get_release_diff, get_product_source_file, check_docs_coverage). "
        "Then ship only needs_docs features from that report with surgical "
        "get_docs_file edits, product=openwiki, and ship-docs-update. "
        "Never claim a ticket or PR without a tool-returned URL. "
        "Lead with the outcome. If research finds nothing, say so briefly and stop."
    ),
)
