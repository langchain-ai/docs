#!/usr/bin/env python3
"""Quick check for OPENAI_API_KEY_NEW against OpenAI API."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


API_URL = "https://api.openai.com/v1/models"


def main() -> int:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is not set.")
        print("Set it first, then rerun this script.")
        return 1

    req = urllib.request.Request(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            payload = json.loads(body)
            models = payload.get("data", [])
            print("OPENAI_API_KEY works (HTTP 200).")
            if models:
                model_ids = sorted(
                    m.get("id", "<unknown>") for m in models if isinstance(m, dict)
                )
                print(f"Accessible models ({len(model_ids)}):")
                for model_id in model_ids:
                    print(f"- {model_id}")
            else:
                print("Authenticated, but model list was empty.")
            return 0
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        print(f"OpenAI request failed with HTTP {err.code}.")
        if err.code in (401, 403):
            print("The key is invalid, revoked, or lacks required permissions.")
        print("Response body:")
        print(body)
        return 1
    except urllib.error.URLError as err:
        print("Network error while contacting OpenAI:")
        print(err.reason)
        return 1
    except json.JSONDecodeError:
        print("Received non-JSON response from OpenAI.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
