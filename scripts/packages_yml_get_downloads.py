"""Update downloads count in packages.yml from pepy.tech badge numbers."""

import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import requests
from ruamel.yaml import YAML

yaml = YAML()
# Preserve quotes, comments, and formatting
yaml.preserve_quotes = True
yaml.width = 4096  # Prevent line wrapping

PACKAGE_YML = Path(__file__).parents[1] / "packages.yml"


def _parse_badge_count(raw: str) -> int:
    """Parse pepy badge text like '1.2k', '3.4M', or '12,345' into an int."""
    latest = raw.replace(",", "")
    if latest.endswith(("k", "K")):
        return int(float(latest[:-1]) * 1_000)
    if latest.endswith(("m", "M")):
        return int(float(latest[:-1]) * 1_000_000)
    return int(float(latest))


def _get_downloads(p: dict) -> int:
    """Get downloads count from pepy.tech badge SVG.

    Args:
        p: Package dict from packages.yml

    Returns:
        Downloads count as int. Returns 0 when pepy has not indexed the
        package yet (HTTP 404), which is common for newly published packages.

    Raises:
        requests.RequestException: If the HTTP request fails for a reason
            other than a missing package badge.
    """
    name = p["name"]
    url = f"https://pepy.tech/badge/{name}/month"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            print(
                f"warn: pepy badge not found for {name}; recording 0 downloads",
                file=sys.stderr,
            )
            return 0
        response.raise_for_status()
        svg = response.text
    except requests.RequestException as e:
        msg = f"Failed to fetch downloads for {name}: {e}"
        raise requests.RequestException(msg) from e

    texts = re.findall(r"<text[^>]*>([^<]+)</text>", svg)
    latest = texts[-1].strip() if texts else "0"
    return _parse_badge_count(latest)


current_datetime = datetime.now(UTC)
yesterday = current_datetime - timedelta(days=1)

with PACKAGE_YML.open() as f:
    data = yaml.load(f)

seen = set()
for p in data["packages"]:
    if p["name"] in seen:
        msg = f"Duplicate package: {p['name']}"
        raise ValueError(msg)
    seen.add(p["name"])
    downloads_updated_at_str = p.get("downloads_updated_at")
    downloads_updated_at = (
        datetime.fromisoformat(downloads_updated_at_str)
        if downloads_updated_at_str
        else None
    )

    if downloads_updated_at is not None and downloads_updated_at > yesterday:
        print(f"done: {p['name']}: {p['downloads']}")
        continue

    p["downloads"] = _get_downloads(p)
    p["downloads_updated_at"] = current_datetime.isoformat()
    with PACKAGE_YML.open("w") as f:
        yaml.dump(data, f)
    print(f"{p['name']}: {p['downloads']}")


with PACKAGE_YML.open("w") as f:
    yaml.dump(data, f)
