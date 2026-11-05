"""Local model proxy for the AI docs review agent.

Claude Code talks to this proxy on 127.0.0.1 with a placeholder key. The proxy
runs as a separate user that can read the real gateway key and headers, adds
them, and forwards the request to the LLM Gateway. The agent's environment and
files never contain a model credential.

    python3 scripts/ai_review_proxy.py --config /etc/ai-review/model.json --port 8787

The config file holds ``base_url``, ``api_key``, and ``custom_headers`` (the
newline-separated ``Name: value`` format Claude Code uses).
"""

from __future__ import annotations

import argparse
import http.client
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

MAX_REQUEST_BYTES = 8 * 1024 * 1024
# Headers the client may not set: auth is the proxy's job, and hop-by-hop
# headers belong to this connection only.
DROP_REQUEST = {
    "authorization",
    "x-api-key",
    "host",
    "connection",
    "proxy-authorization",
    "transfer-encoding",
    "content-length",
}
DROP_RESPONSE = {"connection", "transfer-encoding", "content-length", "keep-alive"}


def parse_headers(raw: str) -> dict[str, str]:
    """Parse Claude Code's newline-separated ``Name: value`` header format."""
    out = {}
    for line in raw.splitlines():
        name, sep, value = line.partition(":")
        if sep and name.strip():
            out[name.strip()] = value.strip()
    return out


def outbound_headers(incoming: dict[str, str], api_key: str, custom: dict[str, str]) -> dict[str, str]:
    """Headers to send upstream: the client's, minus auth, plus the real credentials."""
    headers = {k: v for k, v in incoming.items() if k.lower() not in DROP_REQUEST}
    headers.update(custom)
    headers["x-api-key"] = api_key
    return headers


def make_handler(base_url: str, api_key: str, custom: dict[str, str]) -> type[BaseHTTPRequestHandler]:
    """Build a request handler bound to one upstream."""
    upstream = urlsplit(base_url)
    if upstream.scheme != "https" or not upstream.hostname:
        msg = "base_url must be an https URL"
        raise ValueError(msg)
    prefix = upstream.path.rstrip("/")

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"  # one request per connection, body ends at close

        def log_message(self, fmt: str, *args: object) -> None:
            """Log the method and path only, never headers or bodies."""
            sys.stderr.write(f"proxy: {self.command} {self.path.split('?')[0]}\n")

        def _forward(self) -> None:
            if not self.path.startswith("/v1/"):
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_REQUEST_BYTES:
                self.send_error(413)
                return
            body = self.rfile.read(length) if length else None
            headers = outbound_headers(dict(self.headers.items()), api_key, custom)
            conn = http.client.HTTPSConnection(upstream.hostname, upstream.port or 443, timeout=600)
            try:
                conn.request(self.command, prefix + self.path, body=body, headers=headers)
                resp = conn.getresponse()
                self.send_response(resp.status)
                for name, value in resp.getheaders():
                    if name.lower() not in DROP_RESPONSE:
                        self.send_header(name, value)
                self.end_headers()
                while chunk := resp.read1(65536):
                    self.wfile.write(chunk)
                    self.wfile.flush()
            except OSError as err:
                sys.stderr.write(f"proxy: upstream error {type(err).__name__}\n")
                self.send_error(502)
            finally:
                conn.close()

        def do_POST(self) -> None:
            """Forward a POST."""
            self._forward()

        def do_GET(self) -> None:
            """Forward a GET."""
            self._forward()

    return Handler


def main(argv: list[str] | None = None) -> int:
    """Serve on 127.0.0.1 until stopped."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--config", required=True)
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args(argv)
    with open(args.config, encoding="utf-8") as fh:
        cfg = json.load(fh)
    handler = make_handler(cfg["base_url"], cfg["api_key"], parse_headers(cfg.get("custom_headers", "")))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    sys.stderr.write(f"proxy: listening on 127.0.0.1:{args.port}\n")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
