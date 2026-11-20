"""Tests for LangSmith OpenAPI documentation filtering."""

import pytest

from scripts.process_langsmith_openapi import process_spec


@pytest.mark.parametrize("tags", [[], ["runs"]])
def test_sql_query_is_hidden_without_hiding_neighboring_paths(tags: list[str]) -> None:
    """Hide only the SQL query path, regardless of its public tags."""
    spec = {
        "paths": {
            path: {"post": {"tags": tags, "summary": "Query", "responses": {}}}
            for path in ("/v2/sql/query", "/v2/sql/query/stats", "/v2/runs/query")
        },
    }

    result = process_spec(spec)

    assert result["paths"]["/v2/sql/query"]["post"]["x-hidden"] is True
    assert "x-hidden" not in result["paths"]["/v2/sql/query/stats"]["post"]
    assert "x-hidden" not in result["paths"]["/v2/runs/query"]["post"]
