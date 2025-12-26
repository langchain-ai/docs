"""Update downloads count in packages.yml from pepy.tech badge numbers."""

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

import requests
from ruamel.yaml import YAML

yaml = YAML()
# Preserve quotes, comments, and formatting
yaml.preserve_quotes = True
yaml.width = 4096  # Prevent line wrapping

PACKAGE_YML = Path(__file__).parents[1] / "reference" / "packages.yml"


def _get_downloads(p: dict) -> int:
    """Get downloads count from pepy.tech badge SVG.

    Args:
        p: Package dict from packages.yml

    Returns:
        Downloads count as int.

    Raises:
        requests.RequestException: If HTTP request fails.
    """
    url = f"https://pepy.tech/badge/{p['name']}/month"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        svg = response.text
    except requests.RequestException as e:
        msg = f"Failed to fetch downloads for {p['name']}: {e}"
        raise requests.RequestException(msg) from e

    texts = re.findall(r"<text[^>]*>([^<]+)</text>", svg)
    latest = texts[-1].strip() if texts else "0"

    # Parse "1.2k", "3.4M", "12,345" -> int
    latest = latest.replace(",", "")
    if latest.endswith(("k", "K")):
        return int(float(latest[:-1]) * 1_000)
    if latest.endswith(("m", "M")):
        return int(float(latest[:-1]) * 1_000_000)
    return int(float(latest))


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
