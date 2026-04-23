---
name: write-timestamp
description: Use when the user wants the current date and time written to a file via the bundled script inside the sandbox.
---

# Write timestamp

## Instructions

1. The script is available in the sandbox at `/skills/write-timestamp/write_timestamp.py` after sync.
2. Run it with the `execute` tool, for example: `python /skills/write-timestamp/write_timestamp.py`
3. Read `/tmp/skill_timestamp.txt` with `read_file` and summarize the result for the user.
