"""Configuration: hooks handler example."""

# :remove-start:
import io
import sys
from contextlib import redirect_stderr


def handle_hook_payload(payload: dict) -> None:
    event = payload["event"]
    if event == "session.start":
        print(f"Session started: {payload['thread_id']}", file=sys.stderr)
    elif event == "permission.request":
        print(f"Approval needed for: {payload['tool_names']}", file=sys.stderr)


stderr = io.StringIO()
with redirect_stderr(stderr):
    handle_hook_payload({"event": "session.start", "thread_id": "abc123"})
assert "Session started: abc123" in stderr.getvalue()

stderr = io.StringIO()
with redirect_stderr(stderr):
    handle_hook_payload({"event": "permission.request", "tool_names": ["write_file"]})
assert "Approval needed for: ['write_file']" in stderr.getvalue()
print("✓ configuration-hooks-handler sample validated")
raise SystemExit(0)
# :remove-end:

# :snippet-start: configuration-hooks-handler-py
import json
import sys


def handle_hook_payload(payload: dict) -> None:
    event = payload["event"]
    if event == "session.start":
        print(f"Session started: {payload['thread_id']}", file=sys.stderr)
    elif event == "permission.request":
        print(f"Approval needed for: {payload['tool_names']}", file=sys.stderr)


if __name__ == "__main__":
    handle_hook_payload(json.load(sys.stdin))
# :snippet-end:
