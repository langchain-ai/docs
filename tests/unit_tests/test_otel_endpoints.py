"""Unit tests for OpenTelemetry endpoint configurations and docs accuracy."""

import os
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

DOCS_DIR = Path(__file__).resolve().parents[2] / "src"


def test_docs_no_generic_otlp_endpoint_with_signal_path() -> None:
    """Verify docs never set generic OTEL_EXPORTER_OTLP_ENDPOINT with a signal path."""
    bad_pattern = re.compile(
        r"OTEL_EXPORTER_OTLP_ENDPOINT\s*=\s*['\"]?https?://[^\s'\"]+/v1/(traces|metrics|logs)"
    )
    violations = []
    for mdx_path in DOCS_DIR.glob("**/*.mdx"):
        content = mdx_path.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), start=1):
            if bad_pattern.search(line):
                rel_path = mdx_path.relative_to(DOCS_DIR.parent)
                violations.append(f"{rel_path}:{i} - {line.strip()}")

    assert not violations, (
        "Found generic OTEL_EXPORTER_OTLP_ENDPOINT with signal suffix:\n"
        + "\n".join(violations)
    )


def test_docs_collector_configs_use_traces_endpoint() -> None:
    """Verify collector exporter YAML configs use traces_endpoint for /v1/traces."""
    bad_pattern = re.compile(r"\bendpoint:\s+https?://[^\s]+/v1/traces")
    violations = []
    for mdx_path in DOCS_DIR.glob("**/*.mdx"):
        content = mdx_path.read_text(encoding="utf-8")
        if "exporters:" not in content:
            continue
        for i, line in enumerate(content.splitlines(), start=1):
            if bad_pattern.search(line):
                rel_path = mdx_path.relative_to(DOCS_DIR.parent)
                violations.append(f"{rel_path}:{i} - {line.strip()}")

    assert not violations, (
        "Found collector exporter using 'endpoint:' with /v1/traces:\n"
        + "\n".join(violations)
    )


def test_otlp_traces_endpoint_mocked_export() -> None:
    """Ensure OTEL_EXPORTER_OTLP_TRACES_ENDPOINT resolves without duplicate suffix."""
    expected_url = "https://api.smith.langchain.com/otel/v1/traces"
    test_env = {
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT": expected_url,
    }

    with patch.dict(os.environ, test_env, clear=True):
        exporter = OTLPSpanExporter()
        assert exporter._endpoint == expected_url

        with patch.object(exporter._session, "post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, text="OK")

            provider = TracerProvider()
            provider.add_span_processor(SimpleSpanProcessor(exporter))
            tracer = provider.get_tracer("test")

            with tracer.start_as_current_span("test-span"):
                pass

            provider.force_flush()

            assert mock_post.called
            called_url = mock_post.call_args.kwargs["url"]
            assert called_url == expected_url
            assert not called_url.endswith("/v1/traces/v1/traces")


def test_otlp_base_endpoint_appends_single_suffix() -> None:
    """Ensure OTEL_EXPORTER_OTLP_ENDPOINT base URL appends /v1/traces exactly once."""
    base_url = "https://api.smith.langchain.com/otel"
    expected_url = "https://api.smith.langchain.com/otel/v1/traces"
    test_env = {
        "OTEL_EXPORTER_OTLP_ENDPOINT": base_url,
    }

    with patch.dict(os.environ, test_env, clear=True):
        exporter = OTLPSpanExporter()
        assert exporter._endpoint == expected_url

        with patch.object(exporter._session, "post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, text="OK")

            provider = TracerProvider()
            provider.add_span_processor(SimpleSpanProcessor(exporter))
            tracer = provider.get_tracer("test")

            with tracer.start_as_current_span("test-span"):
                pass

            provider.force_flush()

            assert mock_post.called
            called_url = mock_post.call_args.kwargs["url"]
            assert called_url == expected_url
            assert not called_url.endswith("/v1/traces/v1/traces")
