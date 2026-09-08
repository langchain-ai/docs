"""Write the current UTC date and time to a file (runs inside the sandbox)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S %Z")
    out = Path("/tmp/skill_timestamp.txt")
    out.write_text(stamp + "\n", encoding="utf-8")
    print(stamp)


if __name__ == "__main__":
    main()
