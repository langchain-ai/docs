"""Download a workflow artifact zip from the GitHub REST API (cross-host redirect–safe)."""

from __future__ import annotations

import sys


def download_artifact_bytes(archive_url: str, token: str) -> bytes:
    """
    `archive_url` is the `archive_download_url` for an artifacts API object.

    Use ``requests`` so redirects to signed S3 URLs are followed **without** sending
    ``Authorization`` to a non-``github.com`` host. ``urllib`` forwards that header and
    the download can fail (often with HTTP 403 on the storage host).
    """
    try:
        import requests
    except ImportError as e:  # pragma: no cover
        print(
            "This script needs the 'requests' package. Install with:\n"
            "  python3 -m pip install requests",
            file=sys.stderr,
        )
        raise SystemExit(2) from e
    r = requests.get(
        archive_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=300,
    )
    r.raise_for_status()
    return r.content
