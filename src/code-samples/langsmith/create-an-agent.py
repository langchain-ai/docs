# :remove-start:
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

# Exercise the real SDK against a local HTTP fixture, without creating live agents.
requests_seen = []
agent_response = {
    "id": "support-agent",
    "name": "Support agent",
    "source_type": "EXTERNAL",
    "agent_type": "CUSTOM",
    "created_at": "2026-10-22T00:00:00Z",
    "tag_key_id": "00000000-0000-4000-8000-000000000001",
    "tag_value_id": "00000000-0000-4000-8000-000000000002",
    "environments": [
        {
            "id": "00000000-0000-4000-8000-000000000003",
            "agent_id": "support-agent",
            "environment": "PRODUCTION",
            "tracer_session_id": "00000000-0000-4000-8000-000000000004",
            "tracer_session_name": "support-agent-production",
        }
    ],
}


class AgentFixture(BaseHTTPRequestHandler):
    def do_POST(self):
        """Capture the creation request sent by the SDK."""
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        requests_seen.append((self.command, self.path, body))
        self.respond()

    def do_GET(self):
        """Return SDK initialization metadata or the registered agent."""
        if self.path == "/info":
            payload = b"{}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        requests_seen.append((self.command, self.path, None))
        self.respond()

    def respond(self):
        """Return an agent response using the public API schema."""
        payload = json.dumps(agent_response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        """Keep the HTTP fixture quiet."""


server = ThreadingHTTPServer(("127.0.0.1", 0), AgentFixture)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
test_environment = patch.dict(
    os.environ,
    {
        "LANGSMITH_ENDPOINT": f"http://127.0.0.1:{server.server_port}",
        "LANGSMITH_API_KEY": "docs-test-placeholder",
        "LANGSMITH_WORKSPACE_ID": "00000000-0000-4000-8000-000000000005",
        "LANGSMITH_TRACING": "false",
        "LANGSMITH_DISABLE_RUN_COMPRESSION": "true",
    },
    clear=True,
)
test_environment.start()
# :remove-end:

# :snippet-start: create-agent-py
from langsmith import Client

client = Client()
agent = client.agents.create(
    id="support-agent",
    name="Support agent",
    source_type="EXTERNAL",
)
print(agent.id)  # Use as LANGSMITH_AGENT_ID
# :snippet-end:

# :snippet-start: agent-environment-project-py
from langsmith import Client

client = Client()
agent = client.agents.retrieve("support-agent")
production = next(env for env in agent.environments if env.environment == "PRODUCTION")
print(production.tracer_session_name)  # Use as LANGSMITH_PROJECT
print(production.tracer_session_id)  # Use with APIs that take a project ID
# :snippet-end:

# :remove-start:
assert requests_seen == [
    (
        "POST",
        "/api/v1/agents",
        {"id": "support-agent", "name": "Support agent", "source_type": "EXTERNAL"},
    ),
    ("GET", "/api/v1/agents/support-agent", None),
], requests_seen
assert production.tracer_session_name == "support-agent-production"
assert str(production.tracer_session_id) == "00000000-0000-4000-8000-000000000004"
server.shutdown()
server.server_close()
thread.join()
test_environment.stop()
print("Agent creation and environment lookup validated")
# :remove-end:
